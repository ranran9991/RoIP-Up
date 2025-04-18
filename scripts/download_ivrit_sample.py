import argparse
import os
import requests
from tqdm import tqdm
from datasets import load_dataset
import soundfile as sf


def download_audio_files(num_samples: int, output_dir: str) -> None:
    dataset = load_dataset("ivrit-ai/crowd-transcribe-v5", split=f"train[:{num_samples}]")
    os.makedirs(output_dir, exist_ok=True)

    for _, sample in enumerate(tqdm(dataset.select(range(num_samples)), desc="Downloading audio files")):
        signal = sample["audio"]['array']
        fs = sample['audio']['sampling_rate']
        idx = sample['audio']['path']
        filename = os.path.join(output_dir, f"{idx}")
        sf.write(filename, signal, fs)


def main():
    parser = argparse.ArgumentParser(description="Download audio files from the ivrit-ai/crowd-transcribe-v5 dataset.")
    parser.add_argument(
        "-n", "--num_samples", type=int, default=10,
        help="Number of audio samples to download (default: 10)"
    )
    parser.add_argument(
        "-o", "--output_dir", type=str, default="../data/ivrit_audio",
        help="Directory to save downloaded audio files (default: ../data/ivrit_audio)"
    )

    args = parser.parse_args()
    download_audio_files(args.num_samples, args.output_dir)


if __name__ == "__main__":
    main()
