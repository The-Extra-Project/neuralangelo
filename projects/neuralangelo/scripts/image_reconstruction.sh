#!/bin/sh
SEQUENCE=lego
PATH_TO_VIDEO=lego.mp4
DOWNSAMPLE_RATE=2
SCENE_TYPE=object
PATH_TO_VIDEO=./datas/lego.mp4

bash ./projects/neuralangelo/scripts/run_ffmpeg.sh ${SEQUENCE} ${PATH_TO_VIDEO} ${DOWNSAMPLE_RATE}
DATA_PATH=./datasets/${SEQUENCE}_ds${DOWNSAMPLE_RATE}
bash projects/neuralangelo/scripts/run_colmap.sh ${DATA_PATH}


