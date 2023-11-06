import streamlit as st
from dataset.tanks_temples_dataset import id_download_dict, intermediate_list
from dotenv import load_dotenv, set_key
from subprocess import check_call
import time
import os
def main():
    st.title("neuralangelo demo")
    dataset_list = []
    for key in intermediate_list:
        dataset_list.append(key)
    form = st.form("neuralangelo_params")
    scene_type = form.selectbox("scene type", options=["outdoor","indoor","object"])
    value = form.selectbox("dataset category", options=["intermediate","advanced","both","training","all"])
    dataset = form.selectbox("training dataset",options=dataset_list)
    submitted = form.form_submit_button("train model")
    if submitted:
        st.write("DOWNLOADING DATASET")
        while st.spinner(text="colmap processing In progress"):
            time.sleep(200)
            
        st.success('preprocesing done')
        st.write("training stage")
        dataset_parse(value)   
        setting_env_variables(sequence_path="barn", video_path="./dataset/", scene_type=scene_type)

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
        check_call(["docker compose run", "neuralangelo-complete-pipeline" ])


    except Exception as e:
        print("error:{}".format(e)) 

def setting_env_variables(sequence_path, video_path, scene_type):
    """
    Setup the initial training variable for the training stage (based on the dataset selected by the neuralangelo)
    """
    env_path = "../.env"
    set_key(env_path, "SEQUENCE", sequence_path)
    set_key(env_path, "PATH_TO_VIDEO", video_path)
    set_key(env_path, "SCENE_PATH", scene_type)




if __name__ == "__main__":
    main()