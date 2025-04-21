import os
import argparse
import librosa
import soundfile as sf
from pydub import AudioSegment, silence

import io
import random
import numpy as np
from src.utils.io import save_audio
from src.utils.transforms import add_static, compress_audio, bandpass_filter, ffmpeg_transcode_with_codec, \
    apply_ptt_effect, add_squelch


def extract_mp3_files(src_dir):
    """Extract all MP3 file paths from the source directory."""
    return [os.path.join(src_dir, f) for f in os.listdir(src_dir) if f.endswith(".wav")]


def transform_audio(audio_path, output_path, add_squelch_noise=True):
    # Parameters
    fs = 8000
    silence_thresh = -40
    min_silence_len = 300
    keep_silence = 100

    transcoded_path = ffmpeg_transcode_with_codec(audio_path)
    audio = AudioSegment.from_file(transcoded_path).set_channels(1).set_frame_rate(fs)
    # Extract raw samples and normalize
    samples = np.array(audio.get_array_of_samples()).astype(np.float32)
    samples /= np.iinfo(audio.array_type).max

    # Split based on silence
    non_silent_ranges = silence.detect_nonsilent(audio, min_silence_len=min_silence_len, silence_thresh=silence_thresh)

    processed_audio = AudioSegment.silent(duration=0, frame_rate=fs)

    # Keep track of cursor for inserting silence gaps
    cursor = 0
    for start, end in non_silent_ranges:
        # Add silence before this chunk if needed
        if start > cursor:
            silent_chunk = audio[cursor:start]
            if add_squelch_noise:
                silent_chunk = add_squelch(silent_chunk, level=-50)
            processed_audio += silent_chunk

        # Process non-silent chunk
        chunk = audio[start:end]
        samples = np.array(chunk.get_array_of_samples()).astype(np.float32)
        samples /= np.iinfo(chunk.array_type).max

        filtered = bandpass_filter(samples, 300, 3000, fs)
        with_static = add_static(filtered)
        with_ptt = apply_ptt_effect(with_static, fs)

        # Add squelch tail
        tail = np.random.normal(0, 0.05, int(0.02 * fs))
        full_burst = np.concatenate([with_ptt, tail])

        int16 = (full_burst * 32767).astype(np.int16)

        seg = AudioSegment(
            int16.tobytes(),
            frame_rate=fs,
            sample_width=2,
            channels=1
        )

        processed_audio += seg
        cursor = end

        # Add any remaining silence at the end
    if cursor < len(audio):
        end_silence = audio[cursor:]
        if add_squelch_noise:
            end_silence = add_squelch(end_silence, level=-50)
        processed_audio += end_silence

    processed_audio.export(output_path, format="wav")
    print(f"ROIP-style audio saved to {output_path}")

    # Clean up
    for file in os.listdir():
        if file.startswith("temp_codec_file") or file == "temp_decoded.wav":
            os.remove(file)


def run_etl(src_dir, dest_dir):
    os.makedirs(dest_dir, exist_ok=True)
    mp3_files = extract_mp3_files(src_dir)

    for file_path in mp3_files:
        print(f"Processing {file_path}...")
        filename = os.path.splitext(os.path.basename(file_path))[0] + '.wav'
        try:
            transform_audio(file_path, os.path.join(dest_dir, filename))
        except Exception as _:
            print(f'FAILED PROCESSING {filename}')


def main():
    parser = argparse.ArgumentParser(description="ETL pipeline for wav audio using librosa.")
    parser.add_argument('-i', '--input-dir', type=str,
                        help='Path to input directory containing MP3 files.',
                        default='../data/ivrit_audio')
    parser.add_argument('-o', '--output-dir', type=str,
                        help='Path to output directory for transformed files.',
                        default='../data/ivrit_transformed')

    args = parser.parse_args()
    run_etl(args.input_dir, args.output_dir)


if __name__ == "__main__":
    main()
