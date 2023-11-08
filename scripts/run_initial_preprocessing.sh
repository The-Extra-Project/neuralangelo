#!/bin/bash
SEQUENCE=${1}
DOWNSAMPLE_RATE=$2
SCENE_TYPE=${3}
PATH_TO_VIDEO=/app/neuralangelo/datasets/videos/${SEQUENCE}.mp4
TNT_PATH=/app/neuralangelo/datasets/tanks_and_temples/${SEQUENCE}/
bash ./app/neuralangelo/projects/neuralangelo/scripts/run_ffmpeg.sh ${SEQUENCE} ${PATH_TO_VIDEO} ${DOWNSAMPLE_RATE}
DATA_PATH=/app/neuralangelo/datasets/${SEQUENCE}_ds${DOWNSAMPLE_RATE}
#bash projects/neuralangelo/scripts/run_colmap.sh ${DATA_PATH}
## NOTE: in case for running more comprehensive evaluation, its preferable

echo "now running the tnt evaluation dataset"
bash ./app/neuralangelo/projects/neuralangelo/scripts/preprocess_tnt.sh ${TNT_PATH}