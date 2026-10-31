# Conecta ao Docker do seu computador. Não cria nada na nuvem.
# No Mac, se o terraform apply disser que não acha o Docker, rode antes:
#   export DOCKER_HOST=unix://$HOME/.docker/run/docker.sock
provider "docker" {}
