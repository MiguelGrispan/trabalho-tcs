-- O PostgreSQL do docker-compose.yml roda este arquivo só na 1ª vez, quando o volume do banco ainda está vazio.
-- Cria o banco dos testes, o mesmo que o CI (.github/workflows/testes.yml) e o tests/banco_teste.py usam.
CREATE DATABASE raiox_teste;
