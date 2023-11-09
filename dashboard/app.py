import streamlit as st
from dataset.tanks_temples_dataset import intermediate_list , advanced_list, training_list, id_download_dict
from subprocess import check_call
from pathlib import Path
import os
from subprocess import Popen, PIPE
import open3d as o3d
import asyncio

async def call_subprocess_command(command):
    try:
        command = await asyncio.run(asyncio.create_subprocess_shell(command, stdout=PIPE, shell=True))        
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
    runs the combined docker container on bacalau
    sequence_name: its the actual name of the video that you want to develop.
    
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
    downsampling = form.text_input(label="number of frames that you want to resample", value=2)
    
    mesh_name = 'output_' + value
    
    submitted = form.form_submit_button("colmap calibration/analysis")
    training_model = form.form_submit_button("neuralangelo training")
    mesh_generation = form.form_submit_button("mesh generation")    
    
    current_dir =  Path(__file__).parent
    parent_dir =  (current_dir / '../' ).resolve()
    datasets_dir = ( parent_dir / 'datasets/').resolve()
    videos_dir = (datasets_dir/ 'videos/').resolve()
    
    
    
    ##TODO: currently drive API's are rate limited so we've transferred already the trainingdata / videos for barn/family in the datasets/ folder 
    while submitted:
        ## downloading the necessary datasets
        st.header("downloading the training dataset and transferring to the requisite portal")
        #call_subprocess_command('python tanks_temples_dataset.py' + ' --modality video ' + ' --group both')
        ## insure before that the container is running in detached mode.
        #call_subprocess_command('docker exec -it neuralangelo-colmap mkdir ./datasets ')        
        if (os.path.exists(os.path.join(__file__ , 'training.zip'))):
            asyncio.run(call_subprocess_command('gdown 1jAr3IDvhVmmYeDWi0D_JfgiHcl70rzVE && 7z x trainingdata.zip -o tanks_and_temples'))
        #call_subprocess_command('docker cp ./tanks_and_temples neuralangelo-colmap:/datasets/tanks_and_temples/')
        #call_subprocess_command('')
        
        
        os.chdir(parent_dir)
        # if st.spinner(text="colmap processing In progress"):
        #     colmap_execution(ds_name=value, downsample_rate=5, scene_type=scene_type)
        #     for i in os.listdir((datasets_dir + '/tanks_and_temples/' + value + '/' ).resolve()):
        #         st.write('fetching the file details:  ' + str(i))
        # st.success('calibrated raw_images generated in ' +  videos_dir + value)
    if training_model:
        st.write("training stage and output")
        run_training_job(value,ds_rate=downsampling, experiment_name=value, group_name= value + "_group")
        st.write("finished with the trained weight and checkpoints stored")

    if mesh_generation:
        st.write("and the pointcloud generation phase")
        run_mesh_extraction(group_name=value,output_name= "output" + value,mesh= value + "ply" )
        
        

def dataset_parse(selected_group):
    """
    fetches the dataset selected by the user and fetches the video/ images and returns its relative path
    """
    try:
        os.mkdir( os.getcwd() + "/datasets/")
        check_call(["python", __file__ + "dashboard/dataset/tanks_temples_dataset.py", "--modality" , "video" , "--group" , selected_group , "--pathname", "./datasets/videos/" ])
    except Exception as e:
        print("error:{}".format(e)) 

## these functions are to provide the sequential version:


def colmap_execution(ds_name: str, downsample_rate: int, scene_type: str):
    """
    generates the downsampled images and does the preprocessing step for the given dataset.
    """
    try:
        check_call(["docker run -d colmap " + ds_name + " " + str(downsample_rate) + " " + scene_type])
    except Exception as e:
         print("inside colmap execution" + str(e))
    

def  run_training_job(sequence: str, ds_rate:int, experiment_name: str, group_name: str):
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
    ply_point_cloud = o3d.io.read_point_cloud(mesh_name)
    o3d.visualization([ply_point_cloud],
                      zoom=0.3412,
                                  front=[0.4257, -0.2125, -0.8795],
                                  lookat=[2.6172, 2.0475, 1.532],
                                  up=[-0.0694, -0.9768, 0.2024])
        
    
    

if __name__ == "__main__":
    main()