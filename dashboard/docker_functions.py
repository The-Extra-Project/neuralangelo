import os
from subprocess import check_call

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

def colmap_execution_tnt(ds_name: str, downsample_rate: int,scene_type: str):
    """
    generates the downsampled images from video (defined from other datasets or users own video).
    
    """
    try:
        stream_output(["bash ../scripts/run_dataset_pipeline.sh " + "run_tnt_pipeline " + ds_name  + " " + downsample_rate +  " " + scene_type])
        
        ## now copy the outputs        
    except Exception as e:
        st.error("inside colmap execution" + str(e))

def colmap_execution_dtu(dataset_name,learning_rate ):
    """
    generates the downsampled images from video (defined from other datasets or users own video).
    
    """
    try:
        stream_output(["bash ../scripts/run_dataset_pipeline.sh " + "run_DTU_pipeline " + dataset_name  + " " +  learning_rate ])
        
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
    
