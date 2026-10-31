# Versões do Terraform e do provider (o "plugin" que fala com o Docker).
# O .terraform.lock.hcl, ao lado, trava a versão exata do provider para todos, como o requirements.txt faz com o Python.
terraform {
  required_version = ">= 1.5.0, < 2.0.0" # o strcontains() do main.tf precisa do 1.5

  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 4.6"
    }
  }
}
