latest_image_id=$(docker images -q | tail -1)
docker rmi -f $latest_image_id
docker compose build colmap
docker run --rm -it neuralangelo-colmap  Barn outdoor 2