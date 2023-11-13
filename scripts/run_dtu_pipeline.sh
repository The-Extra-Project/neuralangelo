export DTU_PATH="datasets/dtu"
bash projects/neuralangelo/scripts/preprocess_dtu.sh ${PATH_TO_DTU}

##TODO: temporaire installation of the tinycudann
echo "Generate json files"
python3 projects/neuralangelo/scripts/convert_dtu_to_json.py --dtu_path ${DTU_PATH}


python projects/neuralangelo/scripts/generate_config.py \
  --sequence_name="DTU" \
  --data_dir="datasets/dtu/${1}/" \
  --scene_type="object" 

GROUP=${1}
NAME=${2}

echo "running the training epoch session" 

torchrun --nproc_per_node=1 train.py \
    --logdir=logs/{GROUP}/{NAME} \
    --show_pbar \
    --config=projects/neuralangelo/configs/custom/${2}.yaml \
    --data.readjust.scale=0.5 \
    --max_iter=20000 \
    --validation_iter=99999999 \
    --model.object.sdf.encoding.coarse2fine.step=200 \
    --model.object.sdf.encoding.hashgrid.dict_size=19 \
    --optim.sched.warm_up_end=200 \
    --optim.sched.two_steps=[12000,16000]

echo "running the isometric extraction pipeline to recover the mesh"

torchrun --nproc_per_node=1 projects/neuralangelo/scripts/extract_mesh.py \
    --config=logs/{GROUP}/{NAME}/config.yaml \
    --checkpoint=logs/{GROUP}/{NAME}/*.pt \
    --output_file=${mesh_fname} \
    --resolution=300 --block_res=128 \
    --textured