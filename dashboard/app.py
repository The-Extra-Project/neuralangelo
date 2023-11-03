import streamlit as st
from dataset.tanks_temples_dataset import id_download_dict, intermediate_list
from dotenv import load_dotenv, set_key
from subprocess import check_call
import os
def main():
    st.title("neuralangelo demo")
    dataset_list = []
    for key in intermediate_list:
        dataset_list.append(key)
    form = st.form("neuralangelo_params")
    scene_type = form.selectbox("scene type", options=["outdoor","indoor","object"])
    value = form.selectbox("dataset category", options=["intermediate","advanced","both","training","all"])
    form.selectbox("training dataset",options=dataset_list)
    submitted = form.form_submit_button("train model")
    if submitted:
        st.write("DOWNLOADING DATASET")
        dataset_parse(value)
        setting_env_variables(sequence_path="tanks", video_path="./datas", scene_type=scene_type)

def dataset_parse(selected_group):
    """
    fetches the dataset selected by the user and fetches the video/ images and returns its relative path
    """
    try:
        os.mkdir( os.getcwd() + "/data")
        check_call(["python", os.getcwd() + "dashboard/dataset/tanks_temples_dataset.py", "--modality" , "video" , "--group" , selected_group , "--pathname", "./datas/" ])
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



def training_alignment():
    """
    runs the preprocess_tnt.sh dataset for preprocessing the given dataset.
    
    """





if __name__ == "__main__":
    main()