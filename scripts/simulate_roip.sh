#!/bin/bash

# Usage: ./simulate_roip.sh input_audio.wav

if [ -z "$1" ]; then
  echo "Usage: $0 input_audio.wav"
  exit 1
fi

INPUT="$1"
BASENAME=$(basename "$INPUT" | cut -d. -f1)

TMP1="downsample.wav"
TMP2="bandpass.wav"
TMP3="compressed1.opus"
TMP4="decompressed1.wav"
TMP5="compressed2.opus"
TMP6="decompressed2.wav"
TMP7="distorted.wav"
TMP8="noise.wav"
TMP9="gated.wav"
TMP10="filtered_noise.wav"
OUTPUT="${BASENAME}_roip_sim.wav"

echo "🎙️  Simulating crunchy ROIP audio for: $INPUT"

# 1. Downsample to 8kHz mono
ffmpeg -y -i "$INPUT" -ar 8000 -ac 1 "$TMP1"

# 2. Bandpass filter
ffmpeg -y -i "$TMP1" -af "highpass=f=250, lowpass=f=3500" "$TMP2"

# 3. First round of Opus compression (low bitrate)
ffmpeg -y -i "$TMP2" -c:a libopus -b:a 8k -vbr off "$TMP3"
ffmpeg -y -i "$TMP3" "$TMP4"

# 4. Second round of Opus compression
ffmpeg -y -i "$TMP4" -c:a libopus -b:a 8k -vbr off "$TMP5"
ffmpeg -y -i "$TMP5" "$TMP6"

# 5. Distortion and moderate companding
ffmpeg -y -i "$TMP6" -af "acompressor, dynaudnorm, volume=4, compand=attacks=0:points=-90/-900|-60/-20|0/-10|20/-10" "$TMP7"

# 6. Generate white noise (higher amplitude)
DURATION=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$TMP7")
ffmpeg -y -f lavfi -i "anoisesrc=color=white:amplitude=0.01:duration=$DURATION" "$TMP8"

# 7. Bandpass-filter the noise (300Hz–3.4kHz)
ffmpeg -y -i "$TMP8" -af "highpass=f=300, lowpass=f=3400" "$TMP10"

# 8. Gate the voice to simulate squelch
ffmpeg -y -i "$TMP7" -af "compand=attacks=0:points=-90/-90|-50/-50|0/-10" "$TMP9"

# 9. Mix: boost the noise before combining
ffmpeg -y -i "$TMP10" -filter:a "volume=2.0" "boosted_noise.wav"

# 10. Final mix with heavier noise
ffmpeg -y -i "$TMP9" -i "boosted_noise.wav" -filter_complex "[0][1]amix=inputs=2:duration=first:dropout_transition=2" "$OUTPUT"

# Cleanup
rm "$TMP1" "$TMP2" "$TMP3" "$TMP4" "$TMP5" "$TMP6" "$TMP7" "$TMP8" "$TMP9" "$TMP10" "boosted_noise.wav"

echo "✅ Done! ROIP-style audio saved to: $OUTPUT"
