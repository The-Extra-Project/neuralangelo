#!/bin/bash                                                                                                                                                                                                                                                                                                                    

export MAIN_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}")/" && pwd )"

print_fun() # Show a list of functions
{
    grep "^function" $0
}

COLMAP_IMG=colmap
NEUANGELO_IMG=neuralangelo

IMG_NAME=${NEUANGELO_IMG}

if [ $# -eq 0 ]
then
    echo "=> functions aviable are :"
    print_fun
    exit 1;
fi

function build_image
{
    DOCKER_BUILDKIT=0 docker build  -t neuralangelo -f ./docker/Dockerfile-neuralangelo .

}

function run_container
{     
    CMD="docker run -u 0 -d --privileged \
	   -v /tmp/.X11-unix:/tmp/.X11-unix \
	   -v ${PWD}:/app/docker/ \
	   --gpus all -p 3000:3000 \
	   -e DISPLAY=$DISPLAY \
	   --name  ${IMG_NAME}-cont \
	   --device /dev/nvidia0:/dev/nvidia0 \
	   --device /dev/nvidiactl:/dev/nvidiactl \
	   --device /dev/nvidia-uvm:/dev/nvidia-uvm \
	   --device /dev/nvidia-uvm-tools:/dev/nvidia-uvm-tools  \
	   --device /dev/nvidia-modeset:/dev/nvidia-modeset \
	   -ti \
	   ${IMG_NAME}"
    echo $CMD
    eval $CMD
    
}

function kill_container
{
    docker kill ${IMG_NAME}-cont  2>/dev/null
    docker rm -f ${IMG_NAME}-cont  2>/dev/null
}

function ssh_container
{
    docker exec -it ${IMG_NAME}-cont bash
}

function all
{
    kill_container
    run_container
    ssh_container
}

function before_docker
{
    xhost local:root
}


$@


