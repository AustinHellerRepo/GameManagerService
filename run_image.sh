# test
docker run --name game_manager_service --network game_manager_network -p 35125:35125 -e "DOCKER_IP=$(ip -4 addr show docker0 | grep -Po 'inet \K[\d.]+')" --rm game_manager_service

# production
#docker run --name game_manager_service --network game_manager_network -e "DOCKER_IP=$(ip -4 addr show docker0 | grep -Po 'inet \K[\d.]+')" --rm game_manager_service
