from flytekit import workflow, task, kwtypes
from flytekitplugins.bacalhau import BacalhauTask
neuralangelo_task = BacalhauTask(
    name="devextralabs/neuralangelo",
    inputs=kwtypes(
        spec=dict,
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
        spec=dict(
            engine="Docker",
            verifier="Noop",
            PublisherSpec={"type": "IPFS"},
            docker={
                "image": "nvcr.io/nvidia/cuda:11.8.0-devel-ubuntu20.04",
                "entrypoint":[],                
            },
            language={"job_context": None},
            wasm=None,
            resources=None,
            timeout=1800,
            outputs=[
                {
                    "storage_source": "IPFS",
                    "name": "outputs",
                    "path": "/outputs",
                }                
            ],
            inputs=[
                {
                    "cid": "s3://tanks-and-temples/tanks-and-temples",
                    "name": "pc_file_output",
                    "path":"/tanks-and-temples/" + str(sequence_str) + "/",
                    "storageSrouce":"S3"    
                }
            ],
            deal={"concurrency": 1}
        ),
    )
    return data_transfer_task


