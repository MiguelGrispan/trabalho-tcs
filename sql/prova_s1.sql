SELECT cd_cvm, nome, setor,
       MAX(CASE WHEN ano = 2025 THEN valor END) AS receita_2025
FROM contas
WHERE demonstracao = 'DRE' AND cd_conta = '3.01'
GROUP BY cd_cvm, nome, setor
ORDER BY nome;
