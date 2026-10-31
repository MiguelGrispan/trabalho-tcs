# As escolhas de quem roda o terraform apply. Todas têm um padrão: o apply funciona sem mudar nada.
# Para mudar: terraform apply -var porta_tela=8502, ou copie o terraform.tfvars.example para terraform.tfvars.
#
# A chave do Gemini NÃO é variável daqui: a tela lê o seu .env, que o main.tf monta no contêiner.
# Assim a chave não fica no terraform.tfstate (o Terraform guarda as variáveis em texto puro nesse arquivo).

variable "porta_tela" {
  description = "Porta do seu computador para abrir a tela (http://localhost:<porta>)."
  type        = number
  default     = 8501

  validation {
    condition     = var.porta_tela >= 1024 && var.porta_tela <= 65535 && floor(var.porta_tela) == var.porta_tela
    error_message = "Escolha uma porta inteira entre 1024 e 65535."
  }
}

variable "porta_banco" {
  description = "Porta do seu computador para o PostgreSQL (5432 é o endereço padrão do raiox/banco.py)."
  type        = number
  default     = 5432

  validation {
    condition     = var.porta_banco >= 1024 && var.porta_banco <= 65535 && floor(var.porta_banco) == var.porta_banco
    error_message = "Escolha uma porta inteira entre 1024 e 65535."
  }
}

variable "senha_banco" {
  description = "Senha do PostgreSQL do contêiner (padrão: postgres, a mesma do código e do CI)."
  type        = string
  default     = "postgres"
  sensitive   = true
}

variable "ia_real" {
  description = "true liga o Gemini (gasta crédito; a chave vem do .env). false monta o texto sem IA (plano B da demo)."
  type        = bool
  default     = false
}

variable "dados" {
  description = "\"falsos\" força as empresas inventadas; vazio usa a data/ real, se ela existir (igual ao RAIOX_DADOS)."
  type        = string
  default     = ""

  validation {
    condition     = contains(["", "falsos"], var.dados)
    error_message = "Use \"\" (dados reais) ou \"falsos\"."
  }
}
