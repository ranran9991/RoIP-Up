from datasets import load_dataset
import os
import requests
from tqdm import tqdm

NUM_SAMPLES = 10

dataset = load_dataset("ivrit-ai/crowd-transcribe-v5", split="train[:10]")

output_dir = "../data/ivrit_audio"
os.makedirs(output_dir, exist_ok=True)

# Download audio files
for idx, sample in enumerate(tqdm(dataset.select(range(NUM_SAMPLES)), desc="Downloading audio files")):
    audio = sample["audio"]
    audio_url = audio["path"]
    filename = os.path.join(output_dir, f"{idx}.mp3")
    try:
        response = requests.get(audio_url)
        response.raise_for_status()
        with open(filename, "wb") as f:
            f.write(response.content)
    except Exception as e:
        print(f"Failed to download {audio_url}: {e}")
