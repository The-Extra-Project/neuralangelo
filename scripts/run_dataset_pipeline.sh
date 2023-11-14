#!/bin/bash

SEQUENCE=$1
DOWNSAMPLE_RATE=$2
SCENE_TYPE=$3
DATA_TYPE=$4

fn run_DTU_pipeline() {
##$1 is the directory for storing the dtu datasets (which is full dir like datasets/dtu/dtu_scan24)

docker run  -d -t neuralangelo-neuralangelo ## NOTE: this requires the users to run the setup() function before.
container_id=$(docker ps -al | grep "neuralangelo-colmap" | awk '{print $1}')

docker cp ./datasets/${1}  ${container_id}:/app/neuralangelo/datasets/
echo "now running the data preprocessing pipeline and recalibration"
docker exec -it ${container_id} bash ./project/neuralangelo/scripts/run_preprocessing_dtu.sh ./datasets/${dir_dtu} 

echo "generating the configuration for training steps"

docker exec -it ${container_id} python projects/neuralangelo/scripts/generate_config.py \
  --sequence_name={SEQUENCE} \
  --data_dir="datasets/dtu/${SEQUENCE}/"  \
  --scene_type=${DATA_TYPE} \


echo "starting the training model w/ the given config file"

docker exec -it ${container_id} torchrun --nproc_per_node=1 train.py \
    --logdir=logs/{GROUP}/{NAME} \
    --show_pbar \
    --config=projects/neuralangelo/configs/custom/DTU.yaml \
    --data.readjust.scale=0.5 \
    --max_iter=20000 \
    --validation_iter=99999999 \
    --model.object.sdf.encoding.coarse2fine.step=200 \
    --model.object.sdf.encoding.hashgrid.dict_size=19 \
    --optim.sched.warm_up_end=200 \
    --optim.sched.two_steps=[12000,16000]

echo "Training complete, storing the checkpoint file "

mesh_fname=f"logs/${1}/mesh.ply"

checkpoint_file= ls /root/neuralangelo/logs/${1} | grep ".pt"

docker exec -it ${container_id} torchrun --nproc_per_node=1 projects/neuralangelo/scripts/extract_mesh.py \
    --config=logs/${1}/config.yaml \
    --checkpoint=/root/neuralangelo/logs/Teddy_BEAR/Teddy/*.pt \
    --output_file={mesh_fname} \
    --resolution=300 --block_res=128 \
    --textured

docker cp ${container_id}:/workspace/app/neuralangelo/datasets .

echo "run the mesh on the dataset "
}

fn run_tnt_pipeline() {
##$1 is the name of the tnt dataset that we want to train 
##$2 is the downsampling rate that you want to define 
##$3 is the parameter for nature of the mapping (indoor,outdoor, object)

PATH_TO_VIDEO=./datasets/videos/${1}.mp4

docker run  -d -t neuralangelo-colmap

container_id=$(docker ps -al | grep "neuralangelo-colmap" | awk '{print $1}')


docker cp ./datasets/tanks_and_temples/${1}  ${2}:/workspace/neuralangelo/datasets/
docker cp ${PATH_TO_VIDEO} ${2}:/app/neuralangelo/videos/${1}.mp4


docker exec -it ${2} bash ./projects/neuralangelo/scripts/preprocess_tnt.sh ${1} ${PATH_TO_VIDEO} ${2}

DATA_PATH=/app/neuralangelo/datasets/${1}/${1}_ds${2}

## NOTE: in case for running more comprehensive evaluation, its preferable
echo "now running the tnt preprocessing dataset  + \n" 

docker exec -it ${container_id} bash  ./projects/neuralangelo/scripts/preprocess_tnt.sh  ${DATA_PATH}

echo "fetching the result to the localhost in order to then run remaining operations on neuralangelo-docker"

docker cp ${2}:/workspace/app/neuralangelo/datasets .

docker exec -it ${container_id} bash  python3 projects/neuralangelo/scripts/generate_config.py --sequence_name ${1} --data_dir ${DATA_PATH} --scene_type ${SCENE_TYPE}
}

eval "$@"