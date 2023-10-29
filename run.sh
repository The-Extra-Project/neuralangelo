SEQUENCE=lego
PATH_TO_VIDEO=lego.mp4
DOWNSAMPLE_RATE=2
SCENE_TYPE=object
PATH_TO_VIDEO=./datas/lego.mp4

## INSIDE COLMAP CONTAINER
bash ./projects/neuralangelo/scripts/run_ffmpeg.sh ${SEQUENCE} ${PATH_TO_VIDEO} ${DOWNSAMPLE_RATE}
DATA_PATH=./datasets/${SEQUENCE}_ds${DOWNSAMPLE_RATE}
bash projects/neuralangelo/scripts/run_colmap.sh ${DATA_PATH}

## INSIDE NEURALANGELO CONTAINER
EXPERIMENT=$SEQUENCE
GROUP=example_group
NAME=$SEQUENCE
CONFIG=projects/neuralangelo/configs/custom/${EXPERIMENT}.yaml
GPUS=1  
torchrun --nproc_per_node=${GPUS} train.py \
         --logdir=logs/${GROUP}/${NAME} \
	 --config=${CONFIG} \
         --show_pbar

