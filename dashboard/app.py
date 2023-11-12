import streamlit as st
from dataset.tanks_temples_dataset import intermediate_list , advanced_list, training_list, id_download_dict
from subprocess import check_call
from pathlib import Path
import os
from subprocess import Popen, PIPE, run
from collections import deque
import asyncio
import open3d as o3d
def call_subprocess_command(command):
    """
    command: its the command that you want to run via the container scrip. 
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
    
    return command

def stream_output(command: str) -> None:
    """
    Streams the output of docker commands linewise.

    Args:
        command: The docker command to stream the output of.
    """
    output = deque(maxlen=20)
    
    try:
        with Popen(command,stdout=PIPE,stderr=PIPE,shell=True) as process:
            while True:
                line = process.stdout.readline()
                if not line:
                    break
                line = line.decode("utf-8")
                
                st.write(line)
                
        # Wait for the process to finish
        process.wait()

        # If there are any errors, raise them
        if process.returncode != 0:
            raise Exception(f"Command failed: {command}")
    except Exception as ex:
        print(f"Exception occurred while streaming output: {ex}")

    

def main():
    #subprocess.run(['docker', 'run', '-d','-t' , 'neuralangelo-colmap'])
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
    downsampling = form.text_input(label="number of frames that you want to resample", value=2)
    
    mesh_name = 'output_' + value
    
    submitted = form.form_submit_button("colmap calibration/analysis")
    allignment_images = form.form_submit_button("colmap image allignment")
    training_model = form.form_submit_button("neuralangelo training")
    mesh_generation = form.form_submit_button("mesh generation")    
    final_3D = form.form_submit_button("output vizualization")
    
    
    current_dir =  Path(__file__).parent
    parent_dir =  (current_dir / '../' ).resolve()
    datasets_dir = ( parent_dir / 'datasets/').resolve()
    videos_dir = (datasets_dir/ 'videos/').resolve()

    if submitted:
        st.text("preprocessing the given dataset")
        colmap_execution(value, downsampling, scene_type)
        st.text("the images along with json data and yaml files are preprocessed")
    
    if training_model:
        #subprocess.run(['docker', 'run', '-d','-t' , 'neuralangelo-colmap'])
        
        st.write("training stage and output")
        run_training_job(value,ds_rate=downsampling, experiment_name=value, group_name= value + "_group")
        st.write("finished with the trained weight and checkpoints stored")
        

    if mesh_generation:
        st.write("and the pointcloud generation phase")
        run_mesh_extraction(group_name=value,output_name= "output" + value,mesh= value + "ply" )
      
    if final_3D:
            st.write("result of neuralangelo model extraction")
            run_visualization('../datasets/tanks_and_temples/Barn/Barn.ply')
        

def dataset_parse(selected_group):
    """
    fetches the dataset selected by the user and fetches the video/ images and returns its relative path
    TODO: only used if you want to download all the videos (around 40GB's) in your localhost.
    """
    try:
        os.mkdir( os.getcwd() + "/datasets/")
        check_call(["python", __file__ + "dashboard/dataset/tanks_temples_dataset.py", "--modality" , "video" , "--group" , selected_group , "--pathname", "./datasets/videos/" ])
    except Exception as e:
        print("error:{}".format(e)) 

## these functions are for running the pipeline in sequential version:


def colmap_execution(ds_name: str, downsample_rate: int,scene_type: str):
    """
    generates the downsampled images from video ds and runs the calibration.
  
    """
    try:
        video_path = './datasets/videos/' + ds_name + '.mp4'
        stream_output([" bash ../scripts/run_initial_preprocessing.sh " + ds_name  + " " + downsample_rate +  " " + scene_type], )
        
        ## now copy the outputs 
        
        
        
    except Exception as e:
        st.error("inside colmap execution" + str(e))


def  run_training_job(sequence: str, ds_rate:int, experiment_name: str, group_name: str):

    stream_output(['docker', 'run', '-d', '-t' 'neuralangelo-neuralangelo'])

    ## copying the output results and the config files from the preprocessing  stage to the neuralangelo container.
    #stream_output([ 'docker' + 'cp' + './datasets/' + '' ])../datasets/t

    
    try:
        ## copying the previous results from colmap dataset.
        command_copy = Popen('docker cp neuralangelo-colmap:/app/neuralangelo/'+ ' neuralangelo:/app/neuralangelo',stdout=PIPE, shell=True)
        output_copy , error_copy = command_copy.communicate()
        if output_copy:
            st.success(output_copy.decode('utf-8'))
        elif error_copy:
            st.error(error_copy.decode('utf-8'))
        command = Popen('docker run -d neuralangelo-neuralangelo', stdout=PIPE, shell=True)        
        output, error = command.communicate() 
        if output:
            st.success(output.decode('utf-8'))
        elif error:
            st.error(error.decode('utf-8'))
        st.success(f"output command: {output.decode('utf-8')}")
    except Exception as ex:        
        st.error(f"exception occured at {command.stderr} or {command_copy.stderr}")


def run_mesh_extraction(group_name, output_name, mesh):
    try:
        command_extraction = Popen('docker run -d neuralangelo-neuralangelo' + group_name + '' + output_name + '' + mesh ,stdout=PIPE, shell=True)
        output , error = command_extraction.communicate()
        if output:
            st.success(output.decode('utf-8'))
        else: 
            st.error(error.decode('utf-8'))
        
        command_mesh = Popen('docker cp neuralangelo-neuralangelo:/app/neuralangelo/' + mesh  +' ../', stdout=PIPE, shell=True)
        mesh_result, error_mesh = command_mesh.communicate()
        if mesh_result:
            st.success(mesh_result.decode('utf-8'))
        else:
            st.error(error_mesh.decode('utf-8'))
    
    except Exception as ex:
        st.error(f"exception {error}")
    
def run_visualization(mesh_name: str):
    """
    mesh_name: its the output ply file generated after generation by the model image.
    """



    o3d.visualization.webrtc_server.enable_webrtc()
    
    ply_point_cloud = o3d.io.read_point_cloud(mesh_name)    
    print(ply_point_cloud)
    
    st.write(o3d.visualization.draw_geometries([ply_point_cloud],
                      zoom=0.3412,
                                  front=[0.4257, -0.2125, -0.8795],
                                  lookat=[2.6172, 2.0475, 1.532],
                                  up=[-0.0694, -0.9768, 0.2024]))
    
    
    
    
    

if __name__ == "__main__":
    main()