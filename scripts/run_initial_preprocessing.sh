#!/bin/bash

SEQUENCE=$1
DOWNSAMPLE_RATE=$2
SCENE_TYPE=$3
PATH_TO_VIDEO=../datasets/videos/${SEQUENCE}.mp4
TNT_PATH=../datasets/${SEQUENCE}/


echo "run the compute job "

docker compose run colmap

echo "copying all the required files"

docker cp ../datasets/  neuralangelo-colmap:/app/neuralangelo/datasets/

echo "running the initial commands on the docker container"
docker exec -it  neuralangelo-colmap bash ./projects/neuralangelo/scripts/run_ffmpeg.sh ${SEQUENCE} ${PATH_TO_VIDEO} ${DOWNSAMPLE_RATE}

echo "now transfering the frames into the alignement training data in order to run preprocessing pipelines"

docker exec -it  86540f06e9b2  mkdir ./datasets/${SEQUENCE}/images_raw

docker cp  86540f06e9b2:/datasets/${SEQUENCE}_ds${DOWNSAMPLE_RATE}/ 



DATA_PATH=/app/neuralangelo/datasets/${SEQUENCE}/${SEQUENCE}_ds${DOWNSAMPLE_RATE}
## NOTE: in case for running more comprehensive evaluation, its preferable
echo "now running the tnt preprocessing dataset"


docker exec -it  neuralangelo-colmap bash ./app/neuralangelo/projects/neuralangelo/scripts/preprocess_tnt.sh ${TNT_PATH}

echo "and finally the command in order to run the training config"

docker exec -it  neuralangelo-colmap python3 projects/neuralangelo/scripts/generate_config.py --sequence_name ${SEQUENCE} --data_dir ${DATA_PATH} --scene_type ${SCENE_TYPE}
