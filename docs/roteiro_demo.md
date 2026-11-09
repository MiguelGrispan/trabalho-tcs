# Roteiro da demo

Demo ao vivo: 6 minutos, das 06:00 às 12:00 da apresentação (`guia_projeto_final.pdf` §3: "aplicação rodando em tempo
real"). Versão da banca: tag `v1.0.1`. Dono: Miguel (MG6).

## Antes de apresentar

No computador da demo, na raiz do repositório, **antes de a banca começar** (e sempre depois de reiniciar o computador ou o Docker):

1. `docker compose up -d`: sobe a tela e o banco.
   Se o código mudou desde o último build (ex.: depois do `git pull` que trouxe a `v1.0.1`), use `docker compose up -d --build`:
   sem o `--build`, o compose reaproveita a imagem velha da tela.
2. `docker compose ps`: os 2 (`banco` e `tela`) precisam aparecer como `healthy`.
3. Abra http://localhost:8501: a tela precisa abrir e a busca precisa achar uma empresa da demo (ex.: WEG).
   Se aparecer o aviso de banco vazio, carregue a CVM no banco do contêiner (README, seção "Como rodar com Docker").

**Por quê:** depois de reiniciar, só o banco volta sozinho. O `restart: unless-stopped` está só no banco
(`docker-compose.yml:40`); a tela fica `Exited`, e a página não abre. O código está congelado (`v1.0.1`), então o conserto é
esta lista, não uma mudança no compose.

**Se o Terraform estiver de pé** (`docker ps` mostra `raiox-tela` e `raiox-banco`): o compose e o Terraform usam as mesmas
portas, um de cada vez. Rode `terraform destroy` dentro de `infra/` antes do passo 1 (README, "Como rodar com Terraform").
No Terraform a tela também não volta sozinha (`infra/main.tf:68`: o `restart` está só no banco).

## Roteiro dos 6 minutos

A escrever (MG6), com o vídeo de reserva gravado na `v1.0.1` e guardado em 2 lugares (`guia_projeto_final.pdf` §3, dica).
