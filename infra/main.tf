# Sobe o Raio-X inteiro com Terraform: a tela (Streamlit) e o banco (PostgreSQL), cada um no seu contêiner.
# Faz o mesmo que o docker-compose.yml, escrito como infraestrutura automatizada (requisitos_projeto.MD, Aplicação).
#
# Comandos (dentro da pasta infra/):
#   terraform init       uma vez só: baixa o provider do Docker
#   terraform plan       mostra o que vai criar, mudar ou apagar, sem fazer nada
#   terraform apply      constrói a imagem e sobe os 2 (a 1ª vez demora uns 5 min) → http://localhost:8501
#   terraform destroy    apaga os 2 contêineres e a rede; o banco (volume raiox-banco-dados) e a data/ continuam
#
# O docker compose e o Terraform usam as mesmas portas (8501 e 5432): rode um de cada vez (docker compose down antes
# do terraform apply), ou mude as portas: terraform apply -var porta_tela=8502 -var porta_banco=5433
#
# Testes dentro do contêiner, com o banco de testes (raiox_teste):
#   docker exec raiox-tela python -m pytest -q
# Carregar a CVM no banco do contêiner (no Linux, o --user deixa o contêiner gravar na sua data/; no Mac não precisa):
#   docker exec --user "$(id -u):$(id -g)" raiox-tela python scripts/carregar_dfp.py
#   docker exec --user "$(id -u):$(id -g)" raiox-tela python scripts/indicadores.py
# Apagar o banco de vez (depois do destroy): docker volume rm raiox-banco-dados

locals {
  raiz = abspath("${path.module}/..") # a raiz do repositório

  # O que, se mudar, pede uma imagem nova da tela. O resto do repositório (docs, guias) não muda o que a tela roda.
  padroes_da_imagem = [
    "Dockerfile", "requirements.txt", "pytest.ini",
    "app/**", "raiox/**", "scripts/**", "falsos/**", "avaliacao/**", "tests/**", "aprender/**",
  ]
  # Os caches do Python mudam a cada execução e não entram na imagem (.dockerignore): fora da conta.
  arquivos_da_imagem = sort([
    for f in flatten([for p in local.padroes_da_imagem : tolist(fileset(local.raiz, p))]) : f
    if !strcontains(f, "__pycache__") && !strcontains(f, ".pytest_cache") && !strcontains(f, ".ipynb_checkpoints")
  ])
}

# ---------- imagens ----------

resource "docker_image" "tela" {
  name         = "raiox-tela:terraform" # outro nome que o do compose (raiox-tela): um não troca a imagem do outro
  keep_locally = true                   # o destroy não apaga a imagem: o próximo apply fica rápido

  build {
    context = local.raiz # o Dockerfile e o .dockerignore da raiz: a data/ e o .env não entram na imagem
  }

  # Nome e conteúdo de cada arquivo: mudou algum, o apply refaz a imagem e troca a tela; nada mudou, "No changes".
  triggers = {
    codigo = sha1(join(",", [for f in local.arquivos_da_imagem : "${f}:${filesha1("${local.raiz}/${f}")}"]))
  }
}

resource "docker_image" "banco" {
  name         = "postgres:17" # a mesma versão do CI e do docker-compose.yml
  keep_locally = true
}

# ---------- rede ----------

# Na rede raiox, a tela acha o banco pelo nome "banco", como no compose.
resource "docker_network" "raiox" {
  name = "raiox"
}

# ---------- banco ----------

resource "docker_container" "banco" {
  name    = "raiox-banco"
  image   = docker_image.banco.image_id
  restart = "unless-stopped"
  env     = ["POSTGRES_PASSWORD=${var.senha_banco}", "POSTGRES_DB=raiox"]

  # O banco fica num volume com nome que o Terraform não cria nem apaga (o Docker cria sozinho na 1ª vez):
  # por isso o terraform destroy não apaga o banco.
  volumes {
    volume_name    = "raiox-banco-dados"
    container_path = "/var/lib/postgresql/data"
  }
  # Na 1ª vez (volume vazio), o PostgreSQL roda o infra/banco/01_banco_de_testes.sql, que cria o raiox_teste.
  volumes {
    host_path      = "${local.raiz}/infra/banco"
    container_path = "/docker-entrypoint-initdb.d"
    read_only      = true
  }

  ports {
    internal = 5432
    external = var.porta_banco
    ip       = "127.0.0.1" # só o seu computador enxerga o banco
  }

  networks_advanced {
    name    = docker_network.raiox.name
    aliases = ["banco"]
  }

  healthcheck {
    test     = ["CMD-SHELL", "pg_isready -U postgres -d raiox"]
    interval = "5s"
    timeout  = "5s"
    retries  = 10
  }
  wait         = true # o apply só segue quando o banco aceita conexões
  wait_timeout = 120
}

# ---------- tela ----------

resource "docker_container" "tela" {
  name  = "raiox-tela"
  image = docker_image.tela.image_id

  env = [
    "DATABASE_URL=postgresql://postgres:${var.senha_banco}@banco:5432/raiox",
    "TEST_DATABASE_URL=postgresql://postgres:${var.senha_banco}@banco:5432/raiox_teste",
    "RAIOX_IA_REAL=${var.ia_real ? "1" : ""}",
    "RAIOX_DADOS=${var.dados}",
  ]

  # A data/ não vai para o Git nem para a imagem: entra como pasta montada, e o destroy não mexe nela.
  volumes {
    host_path      = "${local.raiz}/data"
    container_path = "/app/data"
  }
  # A chave do Gemini: o seu .env, só leitura, se ele existir (o código chama load_dotenv()).
  # Assim a chave não passa pelo Terraform e não fica no terraform.tfstate.
  dynamic "volumes" {
    for_each = fileexists("${local.raiz}/.env") ? [1] : []
    content {
      host_path      = "${local.raiz}/.env"
      container_path = "/app/.env"
      read_only      = true
    }
  }

  ports {
    internal = 8501
    external = var.porta_tela
    ip       = "127.0.0.1" # só o seu computador abre a tela (com a IA ligada, cada raio-x gasta crédito)
  }

  networks_advanced {
    name = docker_network.raiox.name
  }

  depends_on   = [docker_container.banco] # a tela só sobe com o banco de pé
  wait         = true                     # o apply só termina quando a tela responde (HEALTHCHECK do Dockerfile)
  wait_timeout = 120
}
