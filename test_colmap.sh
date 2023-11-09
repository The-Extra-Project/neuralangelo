
docker rmi -f $(docker images -q | tail -1)

echo "image deleted " +  $(docker images -q | tail -1) ;

docker build - < docker/Dockerfile-colmap --t colmap-processing:latest -v 

echo "copying the datasets to " + $(docker images -q | tail -1) ;


docker cp ./datasets  colmap-processing:/ 
docker run --rm -it neuralangelo-colmap  Barn outdoor 2