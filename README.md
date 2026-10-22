# Automação de relatórios

Transforma uma planilha de vendas em um relatório executivo em Excel,
sem copiar e colar.

## O problema
Montar o relatório de vendas toda semana à mão leva horas e gera erro.
Este projeto lê o arquivo, limpa os dados, calcula os indicadores e gera
o relatório pronto.

## O que faz
- Remove linhas duplicadas e padroniza nomes
- Corrige campos vazios
- Calcula faturamento, vendas, ticket médio e clientes únicos
- Gera gráficos de linha, rosca e barras em Excel

## Como rodar
    pip install -r requirements.txt
    python gerar_dados.py
    python main.py

O relatório sai em `saida/relatorio.xlsx`.

## Testes
    python -m pytest

## Tecnologias
Python, pandas, XlsxWriter, pytest

![Relatório](docs/relatorio.png)

