from flytekit import workflow, task, kwtypes, dynamic 
from flytekitplugins.bacalhau import BacalhauTask
from bacalhau_apiclient.models.spec import Spec
from bacalhau_apiclient.models.deal import Deal
#from dotenv import load_dotenv
import os
from bacalhau_apiclient.models.job_spec_docker import JobSpecDocker
from bacalhau_apiclient.models.publisher_spec import PublisherSpec
from bacalhau_apiclient.models.storage_spec import StorageSpec


neuralangelo_task = BacalhauTask(
    name="devextralabs/neuralangelo",
    inputs=kwtypes(
        spec=Spec,
        api_version=str
    )
)

colmap_task= BacalhauTask(
        name="devextralabs/colmap_preprocessing",
    inputs=kwtypes(
        spec=dict,
        api_version=str
    )
)
@workflow
def colmap_image_analysis_tnt_dataset(sequence_str: str, downsample_rate: int, scene_type: str):
    
    data_transfer_task = colmap_task(
        api_version="v0.1",
        spec=Spec(
            engine="Docker",
            verifier="Noop",
            publisher_spec= PublisherSpec(
                type="IPFS",
                params={
                    "bucket": "",
                    "key": "",
                },
            
                ),
            docker=JobSpecDocker(
                image="nvcr.io/nvidia/cuda:11.8.0-devel-ubuntu20.04",
                entrypoint=[],                
            ),
            language={"job_context": None},
            resources=None,
            timeout="1800",
            outputs= [
                StorageSpec(
                    storage_source= "IPFS",
                    name= "outputs",
                    path="/outputs")
                    ],
            inputs=[
                StorageSpec(
                    s3="true",
                    name= "pc_file_output",
                    path="/tanks-and-temples/" + str(sequence_str) + "/",
                    storage_source=  "s3://tanks-and-temples/tanks-and-temples"  
                )
            ],
            deal={"concurrency": 1,  "TargetingMode": False}
        ),
    )
    
    
    return data_transfer_task


def  neuralangelo_reconstruction_stage(): 
    pass


