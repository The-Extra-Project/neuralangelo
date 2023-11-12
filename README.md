# Neuralangelo-decentralised 
This is the mofidied implementation of original **Neuralangelo** paper with significant changes.
    - Allows to run training the mesh regeneration on various real-life video / photo scans like [tanks-and-temples]().



## Credits:

[Zhaoshuo Li](https://mli0603.github.io/),
[Thomas Müller](https://tom94.net/),
[Alex Evans](https://research.nvidia.com/person/alex-evans),
[Russell H. Taylor](https://www.cs.jhu.edu/~rht/),
[Mathias Unberath](https://mathiasunberath.github.io/),
[Ming-Yu Liu](https://mingyuliu.net/),
[Chen-Hsuan Lin](https://chenhsuanlin.bitbucket.io/)  
IEEE Conference on Computer Vision and Pattern Recognition (CVPR), 2023

### [Project page](https://research.nvidia.com/labs/dir/neuralangelo/) | [Paper](https://arxiv.org/abs/2306.03092/) | [Colab notebook](https://colab.research.google.com/drive/13u8DX9BNzQwiyPPCB7_4DbSxiQ5-_nGF)

The code is built upon the Imaginaire library from the Deep Imagination Research Group at NVIDIA.  




This implementation is to be solely used for running the compute operations for non commercial demonstration purposes only,

 For business  deployment, please contact the authors and submit the [NVIDIA research licensing form](https://www.nvidia.com/en-us/research/inquiries/).

--------------------------------------

## Setup


1. Build both the docker images which runs the preprocessing commands.

```
> docker compose build up -d 
```

2. You need to download the 
- [trainingdata](https://drive.google.com/file/d/1jAr3IDvhVmmYeDWi0D_JfgiHcl70rzVE/view?resourcekey=)   into the dataset/tanks_and_dataset/ 
- and  videos in dataset/videos
- for downloading all te videos in once you can deploy the 

and as following structure:

```
./tanks_and_temples/
├── Barn
│   ├── Barn.json
│   ├── Barn.ply
│   ├── Barn_COLMAP.ply
│   ├── Barn_COLMAP_SfM.log
│   ├── Barn_mapping_reference.txt
│   ├── Barn_trans.txt
│   ├── database.db
│   ├── images_raw
│   ├── pinhole_dict.json
│   └── sparse
├── Caterpillar
│   ├── Caterpillar.json
│   ├── Caterpillar.ply
│   ├── Caterpillar_COLMAP.ply
│   ├── Caterpillar_COLMAP_SfM.log
│   ├── Caterpillar_mapping_reference.txt
│   └── Caterpillar_trans.txt
├── Church
│   ├── Church.json
│   ├── Church.ply
│   ├── Church_COLMAP.ply
│   ├── Church_COLMAP_SfM.log
│   ├── Church_COLMAP_SfM_ff.log
│   ├── Church_mapping_reference.txt
│   └── Church_trans.txt
├── Courthouse
│   ├── Courthouse.json
│   ├── Courthouse.ply
│   ├── Courthouse_COLMAP.ply
│   ├── Courthouse_COLMAP_SfM.log
│   ├── Courthouse_COLMAP_SfM_ff.log
│   ├── Courthouse_mapping_reference.txt
│   └── Courthouse_trans.txt
├── Ignatius
│   ├── Ignatius.json
│   ├── Ignatius.ply
│   ├── Ignatius_COLMAP.ply
│   ├── Ignatius_COLMAP_SfM.log
│   ├── Ignatius_mapping_reference.txt
│   └── Ignatius_trans.txt
├── Meetingroom
│   ├── Meetingroom.json
│   ├── Meetingroom.ply
│   ├── Meetingroom_COLMAP.ply
│   ├── Meetingroom_COLMAP_SfM.log
│   ├── Meetingroom_mapping_reference.txt
│   └── Meetingroom_trans.txt
├── Truck
│   ├── Truck.json
│   ├── Truck.ply
│   ├── Truck_COLMAP.ply
│   ├── Truck_COLMAP_SfM.log
│   ├── Truck_mapping_reference.txt
│   └── Truck_trans.txt
```
3. install the bacalau and streamlit locally

4. Then setup the streamlit application: 
    - streamlit run dashboard/app.py  
    - select the dataset and the downsampling on which you want to run the training (lower value thus better but still takes enormous time)


--------------------------------------

##  About Data preparation:
Please refer to [Data Preparation](DATA_PROCESSING.md) for understanding the various scripts and their actions .  for our concern we use tanks_and_temples dataset video. the generated json format as [Instant NGP](https://github.com/NVlabs/instant-ngp).

--------------------------------------

## Run Neuralangelo!
```bash
EXPERIMENT=toy_example
GROUP=example_group
NAME=example_name
CONFIG=projects/neuralangelo/configs/custom/${EXPERIMENT}.yaml
GPUS=1  # use >1 for multi-GPU training!
torchrun --nproc_per_node=${GPUS} train.py \
    --logdir=logs/${GROUP}/${NAME} \
    --config=${CONFIG} \
    --show_pbar
```
Some useful notes:
- This codebase supports logging with [Weights & Biases](https://wandb.ai/site). You should have a W&B account for this.
    - Add `--wandb` to the command line argument to enable W&B logging.
    - Add `--wandb_name` to specify the W&B project name.
    - More detailed control can be found in the `init_wandb()` function in `imaginaire/trainers/base.py`.
- Configs can be overridden through the command line (e.g. `--optim.params.lr=1e-2`).
- Set `--checkpoint={CHECKPOINT_PATH}` to initialize with a certain checkpoint; set `--resume` to resume training.
- If appearance embeddings are enabled, make sure `data.num_images` is set to the number of training images.

--------------------------------------

## Isosurface extraction
Use the following command to run isosurface mesh extraction:
```bash
CHECKPOINT=logs/${GROUP}/${NAME}/xxx.pt
OUTPUT_MESH=xxx.ply
CONFIG=logs/${GROUP}/${NAME}/config.yaml
RESOLUTION=2048
BLOCK_RES=128
GPUS=1  # use >1 for multi-GPU mesh extraction
torchrun --nproc_per_node=${GPUS} projects/neuralangelo/scripts/extract_mesh.py \
    --config=${CONFIG} \
    --checkpoint=${CHECKPOINT} \
    --output_file=${OUTPUT_MESH} \
    --resolution=${RESOLUTION} \
    --block_res=${BLOCK_RES}
```
Some useful notes:
- Add `--textured` to extract meshes with textures.
- Add `--keep_lcc` to remove noises. May also remove thin structures.
- Lower `BLOCK_RES` to reduce GPU memory usage.
- Lower `RESOLUTION` to reduce mesh size.

--------------------------------------

## Frequently asked questions (FAQ)
1. **Q:** CUDA out of memory. How do I decrease the memory footprint?  
    **A:** Neuralangelo requires at least 24GB GPU memory with our default configuration. If you run out of memory, consider adjusting the following hyperparameters under `model.object.sdf.encoding.hashgrid` (with suggested values):

    | GPU VRAM      | Hyperparameter          |
    | :-----------: | :---------------------: |
    | 8GB           | `dict_size=20`, `dim=4` |
    | 12GB          | `dict_size=21`, `dim=4` |
    | 16GB          | `dict_size=21`, `dim=8` |

    Please note that the above hyperparameter adjustment may sacrifice the reconstruction quality.

   If Neuralangelo runs fine during training but CUDA out of memory during evaluation, consider adjusting the evaluation parameters under `data.val`, including setting smaller `image_size` (e.g., maximum resolution 200x200), and setting `batch_size=1`, `subset=1`.

2. **Q:** The reconstruction of my custom dataset is bad. What can I do?  
    **A:** It is worth looking into the following:
    - The camera poses recovered by COLMAP may be off. We have implemented tools (using [Blender](https://github.com/mli0603/BlenderNeuralangelo) or [Jupyter notebook](projects/neuralangelo/scripts/visualize_colmap.ipynb)) to inspect the COLMAP results.
    - The computed bounding regions may be off and/or too small/large. Please refer to [data preprocessing](DATA_PROCESSING.md) on how to adjust the bounding regions manually.
    - The video capture sequence may contain significant motion blur or out-of-focus frames. Higher shutter speed (reducing motion blur) and smaller aperture (increasing focus range) are very helpful.

--------------------------------------

## Citation
If you find our code useful for your research, please cite
```
@inproceedings{li2023neuralangelo,
  title={Neuralangelo: High-Fidelity Neural Surface Reconstruction},
  author={Li, Zhaoshuo and M\"uller, Thomas and Evans, Alex and Taylor, Russell H and Unberath, Mathias and Liu, Ming-Yu and Lin, Chen-Hsuan},
  booktitle={IEEE Conference on Computer Vision and Pattern Recognition ({CVPR})},
  year={2023}
}
```
