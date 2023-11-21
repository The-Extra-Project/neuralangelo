#!/bin/bash

function run_DTU_pipeline() {

##$1 is the directory for storing the dtu datasets (which is full dir like datasets like dtu_scan24)
##$2 define the learning rate for the optimum parameters ( in form xe-y) 
docker run  -d -t neuralangelo-neuralangelo

container_id=$(docker ps -al | grep "neuralangelo-neuralangelo" | awk '{print $1}')

#docker exec -it ${container_id} mkdir ./datasets/dtu
docker cp datasets/dtu/${1}  ${container_id}:workspaces/app/neuralangelo/datasets/

echo "now running the data preprocessing pipeline and recalibration"
## /workspaces/app/neuralangelo

docker exec -it ${container_id} bash projects/neuralangelo/scripts/preprocess_dtu.sh ./datasets/

docker exec -it ${container_id} ls -l ./datasets/

echo "generating the configuration for training steps"

docker exec -it ${container_id} python projects/neuralangelo/scripts/generate_config.py \
  --sequence_name=${1} \
  --data_dir=./datasets/dtu_scan69  \
  --scene_type=object\


echo "starting the training model w/ the given config file"

docker exec -it ${container_id} torchrun --nproc_per_node=1 train.py \
    --logdir=logs/${1} \
    --show_pbar \
    --config=projects/neuralangelo/configs/custom/${1}.yaml \
    --data.readjust.scale=0.5 \
    --max_iter=20000 \
    --validation_iter=99999999 \
    --model.object.sdf.encoding.coarse2fine.step=200 \
    --model.object.sdf.encoding.hashgrid.dict_size=19 \
    --optim.sched.warm_up_end=200 \
    --optim.sched.two_steps=[12000,16000] \
    --optim.params.lr=${2} \

echo "Training complete, storing the checkpoint file and running the torch output"

mesh_fname=f"logs/${1}/mesh.ply"

checkpoint_file= ls /root/neuralangelo/logs/${1} | grep ".pt"

docker exec -it ${container_id} torchrun --nproc_per_node=1 projects/neuralangelo/scripts/extract_mesh.py \
    --config=logs/${1}/config.yaml \
    --checkpoint=/root/neuralangelo/logs/Teddy_BEAR/Teddy/*.pt \
    --output_file={mesh_fname} \
    --resolution=300 --block_res=128 \
    --textured

docker cp ${container_id}:/workspace/app/neuralangelo/datasets .

}

function run_tnt_pipeline() {
##$1 is the name of the tnt dataset that we want to train 
##$2 is the downsampling rate that you want to define 
##$3 is the parameter for nature of the mapping (indoor,outdoor, object)
PATH_TO_VIDEO=$pwd/../datasets/videos/${1}.mp4
docker run  -d -t neuralangelo-colmap

container_id=$(docker ps -al | grep "neuralangelo-colmap" | awk '{print $1}')

docker cp ../datasets/tanks_and_temples/${1}  ${container_id}:/app/neuralangelo/datasets/

docker cp ${PATH_TO_VIDEO} ${container_id}:/app/neuralangelo/datasets/videos/


docker exec -it ${container_id} 
## NOTE: in case for running more comprehensive evaluation, its preferable
echo "now running the tnt preprocessing dataset  + \n" 

docker exec -it ${container_id} bash  ./projects/neuralangelo/scripts/preprocess_tnt.sh  ${DATA_PATH}

echo "fetching the result to the localhost in order to then run remaining operations on neuralangelo-docker"

docker cp ${2}:/workspace/app/neuralangelo/datasets .

docker exec -it ${container_id} bash  python3 projects/neuralangelo/scripts/generate_config.py --sequence_name ${1} --data_dir ${DATA_PATH} --scene_type ${SCENE_TYPE}

}

eval "$@"