import subprocess

import numpy as np
from pydub import AudioSegment
from pydub.utils import which
from scipy.signal import butter, lfilter, resample


def bandpass_filter(data, lowcut, highcut, fs, order=6):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    return lfilter(b, a, data)


def add_static(audio_np, intensity=0.01):
    noise = np.random.normal(0, intensity, audio_np.shape)
    return np.clip(audio_np + noise, -1.0, 1.0)


def compress_audio(audio_np, orig_rate, compressed_rate=4000, bit_depth=4):
    """ Simple Compression by resampling -> quantization -> upsampling."""
    # Downsample
    compressed = resample(audio_np, int(len(audio_np) * compressed_rate / orig_rate))

    # Quantize (bit depth reduction)
    max_val = 2 ** (bit_depth - 1) - 1
    compressed = np.round(compressed * max_val) / max_val

    # Upsample back
    restored = resample(compressed, len(audio_np))
    return np.clip(restored, -1.0, 1.0)


def ffmpeg_transcode_with_codec(input_path):
    """ GSM codec artifacts. """
    AudioSegment.converter = which("/usr/local/bin/ffmpeg")
    # Load the WAV file
    audio = AudioSegment.from_mp3(input_path)

    encoded_path = 'temp_codec_file.gsm'
    # Export to GSM format
    audio.export(encoded_path, format="gsm", parameters=["-ar", "8000", "-ac", "1", "-c:a", "libgsm"])

    # Load GSM file
    audio_gsm = AudioSegment.from_file(encoded_path, format="gsm")

    decoded_path = 'temp_decoded.wav'

    # Export back to WAV
    audio_gsm.export(decoded_path, format="wav")

    return decoded_path


def add_squelch(segment: AudioSegment, level=-50):
    """Add low-volume static noise to a silent segment to simulate squelch hiss."""
    duration_ms = len(segment)
    noise = np.random.normal(0, 1, int(8000 * duration_ms / 1000))
    noise = (noise * 32767).astype(np.int16)
    noise_segment = AudioSegment(
        noise.tobytes(), frame_rate=8000, sample_width=2, channels=1
    )
    return noise_segment - abs(level)


def apply_ptt_effect(audio_np, fs):
    chop_duration = int(0.03 * fs)
    audio_np[:chop_duration] *= np.linspace(0, 1, chop_duration)
    audio_np[-chop_duration:] *= np.linspace(1, 0, chop_duration)
    return audio_np
