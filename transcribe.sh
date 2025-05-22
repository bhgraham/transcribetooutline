#!/bin/bash
# Simple OpenAI Whisper Docker transcription (no temp files)

set -euo pipefail

usage() {
    echo "Usage:"
    echo "  $0 <input_audio.(wav|mp4)> <output_text.txt>"
    exit 1
}
# ...existing code...

if [ "$1" = "-b" ]; then
    if [ $# -ne 2 ]; then
        echo "Usage: $0 -b <directory>"
        exit 1
    fi
    BATCH_DIR="$2"
    if [ ! -d "$BATCH_DIR" ]; then
        echo "Directory '$BATCH_DIR' not found." >&2
        exit 1
    fi
    for f in "$BATCH_DIR"/*.{wav,mp4}; do
        [ -e "$f" ] || continue
        echo "Processing: $f"
        "$0" "$f"
    done
    exit 0
fi

# ...existing code...
if [ $# -lt 1 ] || [ $# -gt 2 ]; then
    usage
fi

INPUT_FILE="$1"
EXT="${INPUT_FILE##*.}"

if [ ! -f "$INPUT_FILE" ]; then
    echo "Audio file '$INPUT_FILE' not found." >&2
    exit 1
fi

if ! command -v docker &> /dev/null; then
    echo "Docker not found!" >&2
    exit 1
fi

# If mp4, convert to wav (same basename)
if [[ "$EXT" == "mp4" ]]; then
    if ! command -v ffmpeg &> /dev/null; then
        echo "ffmpeg not found! Please install ffmpeg to process mp4 files." >&2
        exit 1
    fi
    BASENAME="${INPUT_FILE%.*}"
    WAV_FILE="${BASENAME}.wav"
    ffmpeg -y -i "$INPUT_FILE" -vn -acodec pcm_s16le -ar 16000 -ac 1 "$WAV_FILE"
    INPUT_FILE="$WAV_FILE"
elif [[ "$EXT" != "wav" ]]; then
    echo "Unsupported input file type: .$EXT" >&2
    exit 1
fi

# Output file logic
if [ $# -eq 2 ]; then
    OUTPUT_FILE="$2"
else
    BASENAME="$(basename "${INPUT_FILE%.*}")"
    INPUT_DIR="$(cd "$(dirname "$INPUT_FILE")"; pwd)"
    OUTPUT_FILE="${INPUT_DIR}/${BASENAME}.txt"
fi


# Get Windows path for Docker
if command -v pwd -W &>/dev/null; then
    WIN_INPUT_DIR="$(cd "$(dirname "$INPUT_FILE")"; pwd -W)"
else
    WIN_INPUT_DIR="$INPUT_DIR"
fi

INPUT_FILENAME="$(basename "$INPUT_FILE")"
OUTPUT_FILENAME="$(basename "$OUTPUT_FILE")"
EXPECTED_TXT="${WIN_INPUT_DIR}\\${INPUT_FILENAME%.*}.txt"

GPU_FLAG=""
IMAGE_TAG="latest"
if docker info | grep -qi 'nvidia'; then
    GPU_FLAG="--gpus all"
    IMAGE_TAG="latest-gpu"
fi

DOCKER_IMAGE="onerahmet/openai-whisper-asr-webservice:${IMAGE_TAG}"

docker image inspect "$DOCKER_IMAGE" &>/dev/null || docker pull "$DOCKER_IMAGE"

echo "WIN_INPUT_DIR: $WIN_INPUT_DIR"
echo "INPUT_FILENAME: $INPUT_FILENAME"
echo "Docker run will mount: -v \"${WIN_INPUT_DIR}:/data\""

ls -l "$INPUT_DIR"

MSYS_NO_PATHCONV=1 docker run --rm $GPU_FLAG \
    -v "${WIN_INPUT_DIR}:/data" \
    -w /data \
    "$DOCKER_IMAGE" whisper "$INPUT_FILENAME" --output_format txt --output_dir /data

# Check/move output using Unix path
EXPECTED_TXT="${INPUT_DIR}/${INPUT_FILENAME%.*}.txt"
if [ -f "$EXPECTED_TXT" ]; then
    if [ "$EXPECTED_TXT" != "$OUTPUT_FILE" ]; then
        mv -f "$EXPECTED_TXT" "$OUTPUT_FILE"
    fi
    echo "Transcription complete. Output: $OUTPUT_FILE"
else
    echo "Transcription failed or no output found." >&2
    exit 1
fi