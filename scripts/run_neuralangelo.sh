#!/bin/bash




echo "starting the training of the model on the raw images"
EXPERIMENT=$1
GROUP=$2
NAME=$SEQUENCE
CONFIG=projects/neuralangelo/configs/custom/${EXPERIMENT}.yaml
GPUS=1  
torchrun --nproc_per_node=${GPUS} train.py \
         --logdir=logs/${GROUP}/${NAME} \
	 --config=${CONFIG} \
         --show_pbar

## and then mesh generation 