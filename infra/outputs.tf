# O que o terraform apply mostra no fim (e o terraform output mostra de novo).

output "tela" {
  description = "Abra no navegador."
  value       = "http://localhost:${var.porta_tela}"
}

output "banco" {
  description = "Endereço do PostgreSQL para o Python fora do contêiner (DATABASE_URL), com a sua senha."
  value       = "postgresql://postgres:<senha>@localhost:${var.porta_banco}/raiox"
}

output "ia" {
  description = "Se o Gemini está ligado e de onde vem a chave."
  value = var.ia_real ? (
    fileexists("${local.raiz}/.env") ? "ligada: a chave vem do .env" : "ligada, mas sem .env: o raio-x com IA vai dar erro"
  ) : "desligada: o texto é montado sem IA"
}

output "testes" {
  description = "Os testes dentro do contêiner, com o banco de testes."
  value       = "docker exec ${docker_container.tela.name} python -m pytest -q"
}
