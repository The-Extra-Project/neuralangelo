#!/bin/sh
## ${1} is the name of the dataset (which is named also in the docker container)
## ${2}  scene type based on the dataset , for the training data defined for barn, it will be outside
## ${3} name of the output file that you want to receive


SEQUENCE=${1}
PATH_TO_VIDEO=./datasets/videos/${1}.mp4
DOWNSAMPLE_RATE=2
SCENE_TYPE=${2}

echo "running the initial run_ffmpeg to sequence the photos from videos"

bash ./projects/neuralangelo/scripts/run_ffmpeg.sh ${SEQUENCE} ${PATH_TO_VIDEO} ${DOWNSAMPLE_RATE}



DATA_PATH=./datasets/${SEQUENCE}_ds${DOWNSAMPLE_RATE}

mv ${DATA_PATH}/*.jpg  ./datasets/tanks_and_temples/

echo "copying the raw aligned images from the video to the raw images dataset"



bash projects/neuralangelo/scripts/run_colmap.sh ${DATA_PATH}

## generate the JSON files and training parameters

PATH_TO_TNT=datasets/tanks_and_temples  # Modify this to be the Tanks and Temples root directory.

bash projects/neuralangelo/scripts/preprocess_tnt.sh ${PATH_TO_TNT}


echo "running the training phase"
EXPERIMENT=${1}
GROUP=${1}_example
NAME=example_name
CONFIG=projects/neuralangelo/configs/custom/${EXPERIMENT}.yaml
GPUS=1  # use >1 for multi-GPU training!
torchrun --nproc_per_node=${GPUS} train.py \
    --logdir=logs/${GROUP}/${NAME} \
    --config=${CONFIG} \
    --show_pbar

echo "generating the ply file dataset from the model"

CHECKPOINT=logs/${GROUP}/${NAME}/*.pt
OUTPUT_MESH=${3}
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


