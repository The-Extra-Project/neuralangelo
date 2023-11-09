#!/bin/bash


SEQUENCE=$1
DOWNSAMPLE_RATE=$2
SCENE_TYPE=$3
PATH_TO_VIDEO=../datasets/videos/${SEQUENCE}.mp4
TNT_PATH=../datasets/tanks_and_temples/${SEQUENCE}/
bash ../projects/neuralangelo/scripts/run_ffmpeg.sh ${SEQUENCE} ${PATH_TO_VIDEO} ${DOWNSAMPLE_RATE}
DATA_PATH=/app/neuralangelo/datasets/tanks_and_temples/${SEQUENCE}/${SEQUENCE}_ds${DOWNSAMPLE_RATE}
bash projects/neuralangelo/scripts/run_colmap.sh ${DATA_PATH}
## NOTE: in case for running more comprehensive evaluation, its preferable

echo "now running the tnt evaluation dataset"
bash ./app/neuralangelo/projects/neuralangelo/scripts/preprocess_tnt.sh ${TNT_PATH}

echo "and finally the command in order to run the training config"

python3 projects/neuralangelo/scripts/generate_config.py --sequence_name ${SEQUENCE} --data_dir ${DATA_PATH} --scene_type ${SCENE_TYPE}
