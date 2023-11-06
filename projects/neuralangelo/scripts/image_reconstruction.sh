#!/bin/sh
SEQUENCE=${1}
PATH_TO_VIDEO=./dataset/${1}/images_raw
DOWNSAMPLE_RATE=2
SCENE_TYPE=object
bash ./projects/neuralangelo/scripts/run_ffmpeg.sh ${SEQUENCE} ${PATH_TO_VIDEO} ${DOWNSAMPLE_RATE}
DATA_PATH=./datasets/${SEQUENCE}_ds${DOWNSAMPLE_RATE}
bash projects/neuralangelo/scripts/run_colmap.sh ${DATA_PATH}


EXPERIMENT=$SEQUENCE
GROUP=example_group
NAME=$SEQUENCE
CONFIG=projects/neuralangelo/configs/custom/${EXPERIMENT}.yaml
GPUS=1  

## running the training on the mesh algorithm
torchrun --nproc_per_node=${GPUS} train.py \
         --logdir=logs/${GROUP}/${NAME} \
	 --config=${CONFIG} \
         --show_pbar


## running the isometric reconstruction



CHECKPOINT=logs/${GROUP}/${NAME}/xxx.pt
OUTPUT_MESH=xxx.ply
CONFIG=logs/${GROUP}/${NAME}/config.yaml
RESOLUTION=2048
BLOCK_RES=128
GPUS=1  # use >1 for multi-GPU mesh extraction
torchrun --nproc_per_node=${GPUS} projects/neuralangelo/scripts/extract_mesh.py \
    --config=${CONFIG} \
    --checkpoint=${CHECKPOINT} \
    --output_file=${OUTPUT_MESH} \
    --resolution=${RESOLUTION} \
    --block_res=${BLOCK_RES}

