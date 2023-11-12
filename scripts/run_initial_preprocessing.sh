#!/bin/bash

SEQUENCE=$1
DOWNSAMPLE_RATE=$2
SCENE_TYPE=$3
PATH_TO_VIDEO=./datasets/videos/${SEQUENCE}.mp4
TNT_PATH=./datasets/${SEQUENCE}/


echo "run the container" 

docker run  -d -t neuralangelo-colmap
container_id=$(docker ps -al | grep "neuralangelo-colmap" | awk '{print $1}')


echo "copying all the dataset files from local folder to the container" + '\n'


docker cp ../datasets/  ${container_id}:/app/neuralangelo/datasets/ 

echo "checking the videos availble"

docker exec -it ${container_id} ls ./datasets/videos

echo "running the initial commands on the docker container" + \n

docker exec -it ${container_id} bash ./projects/neuralangelo/scripts/run_ffmpeg.sh ${SEQUENCE} ${PATH_TO_VIDEO} ${DOWNSAMPLE_RATE}

DATA_PATH=/app/neuralangelo/datasets/${SEQUENCE}/${SEQUENCE}_ds${DOWNSAMPLE_RATE}

## NOTE: in case for running more comprehensive evaluation, its preferable
echo "now running the tnt preprocessing dataset" + \n

docker exec -it ${container_id} bash  ./app/neuralangelo/projects/neuralangelo/scripts/run_colmap.sh  ${DATA_PATH}

echo "and finally the command in order to run the training config" docker ps -al | awk '{print $3}' | head -1

docker exec -it ${container_id} bash  python3 projects/neuralangelo/scripts/generate_config.py --sequence_name ${SEQUENCE} --data_dir ${DATA_PATH} --scene_type ${SCENE_TYPE}
