import streamlit as st
from dataset.tanks_temples_dataset import intermediate_list , advanced_list, training_list, id_download_dict
from dotenv import  set_key
from subprocess import check_call
from pathlib import Path
import time
import os
from subprocess import Popen, PIPE

def call_subprocess_command(command):
    try:
        command = Popen(command, stdout=PIPE, shell=True)        
        output, error = command.communicate() 
        if output:
            st.success(output.decode('utf-8'))
        elif error:
            st.error(error.decode('utf-8'))
        st.success(f"output command: {output.decode('utf-8')}")
    except Exception as ex:        
        st.error(f"exception occured at {command.stderr}")


def run_bacalhau_job(sequence_name, downsample_rate, raw_images_id):
    """
    runs the deployed containers.
    """
    try:
        command = Popen("bacalau docker run devextralabs/neuralangelo:0.1 " + sequence_name  + " " + downsample_rate + " " + raw_images_id , stdout=PIPE, shell=True)        
        output, error = command.communicate() 
        if output:
            st.success(output.decode('utf-8'))
        elif error:
            st.error(error.decode('utf-8'))
    except Exception as e:
        print(e)
    
def main():
    st.title("neuralangelo demo")
    dataset_list = []
    gdrive_ids_mapping = {}
    for key,value in id_download_dict.items():
        if key.split(".")[1] == "mp4":
            gdrive_ids_mapping[key.split(".")[0]] = value
    for key in  intermediate_list + advanced_list + training_list:
        dataset_list.append(key)
        
    form = st.form("neuralangelo dataset params")
    scene_type = form.selectbox("scene type", options=["outdoor","indoor","object"])
    value = form.selectbox("dataset category", options= dataset_list)
    submitted = form.form_submit_button("train model")
    
    
    current_dir =  Path(__file__).parent
    parent_dir =  (current_dir / '../' ).resolve()
    datasets_dir = ( parent_dir / './datasets').resolve()
    videos_dir = (datasets_dir/ './videos').resolve()

    if submitted:
        st.write("DOWNLOADING DATASET")
        os.chdir(parent_dir)
        while st.spinner(text="colmap processing In progress"):
            if not os.path.exists(videos_dir):
                os.mkdir(videos_dir)
            os.chdir(videos_dir)    
            call_subprocess_command("gdown " + str(gdrive_ids_mapping.get(value)))
        st.success('download completed on ' +  videos_dir + value)
        st.write("training stage and output")
        dataset_parse(value)   
        call_subprocess_command("docker run  devextralabs/neuralangelo" + value + "" + scene_type + "" + "output_mesh")

def dataset_parse(selected_group):
    """
    fetches the dataset selected by the user and fetches the video/ images and returns its relative path
    """
    try:
        os.mkdir( os.getcwd() + "/datasets/")
        check_call(["python", os.getcwd() + "dashboard/dataset/tanks_temples_dataset.py", "--modality" , "video" , "--group" , selected_group , "--pathname", "./datasets/videos/" ])
    except Exception as e:
        print("error:{}".format(e)) 
            

def run_preprocessing_job(docker_register):
    """
    runs the docker pipeline in order to generate the resligned images with their dataset.
    """    
    try:
        call_subprocess_command("docker run neuralangelo-complete-pipeline" )
    except Exception as e:
        print("error:{}".format(e)) 


if __name__ == "__main__":
    main()