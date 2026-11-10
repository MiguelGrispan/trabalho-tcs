# Roteiro da demo

Demo ao vivo: **5 minutos** (alvo de `docs/tempo_apresentacao.md`; o guia §3 dava 6, das 06:00 às 12:00 de uma apresentação de 20 min: "aplicação rodando em tempo
real"). Versão do código: a mais nova que passar na conferência das fontes (provavelmente a `v1.1`, ainda não decidido em 10/11); a tag `v1.0.1` continua como plano B. Dono: Miguel (MG6).

## Antes de apresentar

No computador da demo, na raiz do repositório, **antes de a banca começar** (e sempre depois de reiniciar o computador ou o Docker):

1. `docker compose up -d`: sobe a tela e o banco.
   Se o código mudou desde o último build (ex.: depois do `git pull` que trouxe os PRs das fontes), use `docker compose up -d --build`:
   sem o `--build`, o compose reaproveita a imagem velha da tela.
2. `docker compose ps`: os 2 (`banco` e `tela`) precisam aparecer como `healthy`.
3. Abra http://localhost:8501: a tela precisa abrir e a busca precisa achar uma empresa da demo (ex.: WEG).
   Se aparecer o aviso de banco vazio, carregue a CVM no banco do contêiner (README, seção "Como rodar com Docker").

**Por quê:** depois de reiniciar, só o banco volta sozinho. O `restart: unless-stopped` está só no banco
(`docker-compose.yml:40`); a tela fica `Exited`, e a página não abre. O conserto é esta lista, não uma mudança no compose.

**Se o Terraform estiver de pé** (`docker ps` mostra `raiox-tela` e `raiox-banco`): o compose e o Terraform usam as mesmas
portas, um de cada vez. Rode `terraform destroy` dentro de `infra/` antes do passo 1 (README, "Como rodar com Terraform").
No Terraform a tela também não volta sozinha (`infra/main.tf:68`: o `restart` está só no banco).

## Roteiro dos 5 minutos

Depois de abrir a tela, gere um raio-x da WEG. No expander **De onde vem cada número**, mostre uma aba de
**Margem EBIT**: a tabela traz as contas 3.05 e 3.01 com descrição, ano e valor bruto. Em seguida mostre
**Baixar DFP (CVM)** e explique que o botão baixa o `.zip` oficial para uma conferência detalhada. Se o link
não aparecer, a carga de links não foi feita; rode `scripts/carregar_links.py` antes da demo.

A escrever (MG6). O vídeo de reserva **ainda não foi gravado** (10/11): grava-se na mesma versão da demo, já com o botão das fontes, e guarda-se em 2 lugares (`guia_projeto_final.pdf` §3, dica).
