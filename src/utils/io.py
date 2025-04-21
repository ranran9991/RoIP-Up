import os
import soundfile as sf


def save_audio(y, sr, original_filename, dest_dir):
    """Save the transformed audio to the destination directory as WAV."""
    filename_wo_ext = os.path.splitext(original_filename)[0]
    dest_path = os.path.join(dest_dir, f"{filename_wo_ext}.wav")
    sf.write(dest_path, y, sr)
    return dest_path
