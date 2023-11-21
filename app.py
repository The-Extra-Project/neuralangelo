import streamlit as st
from dashboard.tanks_temples_dataset import intermediate_list, advanced_list, training_list, id_download_dict
#from workflow.workflow_bacalau import colmap_image_analysis_tnt_dataset
from imaginaire.trainers.base import BaseTrainer
from subprocess import check_call
from pathlib import Path
import os
from subprocess import Popen, PIPE, run
from collections import deque
import asyncio
import open3d as o3d
import logging
from typing import List
import time
import open3d
import wandb

project_name="neuralangelo"


def call_subprocess_command(command):
    """
    function to output the result after execution as a block.
    command: its the command that you want to run via the container script (the corresponding package should be installed in the native container / VM). 
    """
    try:
        command = Popen(command, stdout=PIPE, shell=True)      
        output, error = command.communicate() 
        if output:
            st.success(output.decode('utf-8'))
        elif error:
            st.error(error.decode('utf-8'))
        st.success(f"output command: {output.decode('utf-8')}")
    except Exception as ex:        
        st.error(f"exception occured at {error.decode('utf-8')}")
    

def stream_output(command: str, area: st.empty) -> None:
    """
    Streams the output of docker commands linewise for an  runtime command in realtime.
    Args:
        command: The  command  for which to stream the output of.
        area: its the container where you display the output.
    """
    try:
        with Popen(command,stdout=PIPE,stderr=PIPE,shell=True) as process:
            while True:
                output = ""
                line = process.stdout.readline()
                if not line:
                    break
                line = line.decode("utf-8")
                output += line
                with area:
                    container = st.container()
                    container.markdown(f"```\n{output}\n```")
            process.wait()

        # If there are any errors, raise them
        if process.returncode != 0:
            raise Exception(f"Command failed at: {command}")
    except Exception as ex:
        print(f"Exception occurred while streaming output: {ex}")




def wandb_training_metrics_DTU(dataset_name: str, container ):
    """
    shows the output of the training results on wandb for the DTU datasets.
    """
    #trainer_obj = BaseTrainer(cfg="projects/neuralangelo/configs/custom/DTU.yaml")
    container = st.empty()
    ##TODO: setup the parameters like learning rate, hashgrid_size and sdf encoding coarse2file grading step
    
    stream_output(['torchrun --nproc_per_node=1 train.py \
        --logdir=logs/' + dataset_name + ' \
        --show_pbar \
        --config=projects/neuralangelo/configs/custom/' + dataset_name + '.yaml \
        --data.readjust.scale=0.5 \
        --max_iter=20000 \
        --validation_iter=99999999 \
        --model.object.sdf.encoding.coarse2fine.step=200 \
        --model.object.sdf.encoding.hashgrid.dict_size=19 \
        --optim.sched.warm_up_end=200 \
        --optim.sched.two_steps=[12000,16000] \
        --optim.params.lr=1e-2 \
        --wandb \
        --wandb_name=neuralangelo \
        '], area=container)

        
#def state_management(state: str, value: str ):

def listing_tnt_dataset() -> List:
    list_params = []
    gdrive_ids_mapping = {}
    for key,value in id_download_dict.items():
        if key.split(".")[1] == "mp4":
            gdrive_ids_mapping[key.split(".")[0]] = value
    for key in  intermediate_list + advanced_list + training_list:
        list_params.append(key)
    
    return list_params

def listing_dtu_dataset():
    folder_names = []
    for entry in os.listdir("datasets/dtu"):
        folder_names.append(entry)
    return folder_names             

def run_tanks_dataset_local():
    """
    runs the dataset pipeline steps on localhost. 
    """
    pass


def local_tanks_temples(video, downsampling_dataset: int, scene_type, output):
    stream_output(["docker run -d -t neuralangelo-colmap  &&  container_id=$(docker ps -al | grep 'neuralangelo-neuralangelo' | awk '{print $1}')"])
    stream_output(["bash projects/neuralangelo/scripts/preprocess.sh " + video +  " " + " datasets/videos/" + video + ".mp4" +  " " + downsampling_dataset + " " +  scene_type  + " "  + "datasets/tanks_and_temples/"], area=output)




def main():
    st.title("neuralangelo demo")
    with st.form("neuralangelo dataset params"):
            st.title("tanks_temple dataset")
            scene_type = st.selectbox("scene type", options=["outdoor","indoor","object"])
            downsampling_dataset = st.text_input(label="number of frames that you want to resample", value=2)
            dataset_list = listing_tnt_dataset()
            upload_video = st.file_uploader("upload the video to be analyzed")
            if upload_video:
                st.video(data=upload_video, format="video/mp4")
            value = st.selectbox("dataset params the select", options= dataset_list)   
            submitted = st.form_submit_button("colmap image calibration")
            training = st.form_submit_button("training session")
            mesh_generation = st.form_submit_button("mesh generation")
            if submitted:
                output = st.empty()
                st.write("image calibration stage ")
                stream_output(["bash projects/neuralangelo/scripts/preprocess.sh " + value +  " " + " datasets/videos/" + value + ".mp4" +  " " + downsampling_dataset + " " +  scene_type  + " "  + "datasets/tanks_and_temples/"], area=output)
                st.write("generating the configuration")
                stream_output(['python projects/neuralangelo/scripts/generate_config.py \
                --sequence_name=' + value + ' \
                --data_dir=datasets/tanks_and_temples/' + value + '   \
                --scene_type=' +  scene_type + '\
                '], area=output)
            if training:
                stream_output(['torchrun --nproc_per_node=1 train.py \
                    --logdir=logs/' + value +  ' \
                    --show_pbar \
                    --config=projects/neuralangelo/configs/custom/' + value + '.yaml \
                    --data.readjust.scale=0.5 \
                    --max_iter=20000 \
                    --validation_iter=99999999 \
                    --model.object.sdf.encoding.coarse2fine.step=200 \
                    --model.object.sdf.encoding.hashgrid.dict_size=19 \
                    --optim.sched.warm_up_end=200 \
                    --optim.sched.two_steps=[12000,16000] \
                    --optim.params.lr=1e-2 \
                    '], area=output)
                

            if mesh_generation:
                st.success("generating the output with the defined parameters")
                stream_output(['torchrun --nproc_per_node=1 projects/neuralangelo/scripts/extract_mesh.py \
            --config=projects/neuralangelo/configs/custom/' + value + '.yaml \
            --checkpoint=logs/tnt/' + value + ' \
            --output_file=datasets/output_mesh/' + value + '.ply' + ' \
            --resolution=2048 \
            --block_res=128 \ '],area=output)
        
        
    with st.form('DTU'):
        st.title("DTU dataset")
        dataset_list = listing_dtu_dataset()
        value = st.selectbox("dataset selection", options= dataset_list)
        output = st.empty()
        calibrate = st.form_submit_button("doing the image recalibration")
        training = st.form_submit_button("generating config and output dataset")
        mesh_output = st.form_submit_button("mesh generation")
        resolution = st.text_input("resolution of the extracted image")
        input_text = st.text_input("resolution of the details")        
        if calibrate:
            stream_output(["bash ./projects/neuralangelo/scripts/preprocess_dtu.sh datasets/dtu"], area=output)
        if training:
            st.write("generating config along w/ training step")
            stream_output(['python projects/neuralangelo/scripts/generate_config.py \
                --sequence_name=' + value + ' \
                --data_dir=datasets/dtu/' + value + ' \
                --scene_type=object\
            '],area=output)
            stream_output(['torchrun --nproc_per_node=1 train.py \
            --logdir=logs/' + value + ' \
            --show_pbar \
            --config=projects/neuralangelo/configs/custom/' + value + '.yaml \
            --data.readjust.scale=0.5 \
            --max_iter=20000 \
            --validation_iter=99999999 \
            --model.object.sdf.encoding.coarse2fine.step=200 \
            --model.object.sdf.encoding.hashgrid.dict_size=19 \
            --optim.sched.warm_up_end=200 \
            --optim.sched.two_steps=[12000,16000] \
            --optim.params.lr=1e-2 \
            '], area=output)
            
            st.write("finished with the trained weight/checkpoints stored and now mesh generation")
        if mesh_output:
            
            stream_output(['torchrun --nproc_per_node=1 projects/neuralangelo/scripts/extract_mesh.py \
            --config=projects/neuralangelo/configs/custom/' + value + '.yaml \
            --checkpoint=logs/tnt/' + value + ' \
            --output_file=datasets/output_mesh/' + value + '.ply' + ' \
            --resolution=1024 \
            --block_res=2048 '], area=output)
        
        training_stage = st.form_submit_button("running the pipeline for various training stages")
        output_container = st.empty()
        if training_stage:
            wandb_training_metrics_DTU(value,output_container)


if __name__ == "__main__":
    main()