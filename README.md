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



### Filtros do dashboard (Etapa 4.7)

O endpoint `POST /api/relatorios/processar` recebe `data_inicio`,
`data_fim` e `produto` como parâmetros opcionais. As datas são inclusivas.

- `periodo_selecionado`: intervalo solicitado; limites omitidos usam as
  datas disponíveis na planilha limpa, antes do filtro de produto.
- `periodo`: primeira e última venda do resultado, ou `null` sem vendas.
- `sem_resultados`: indica filtros válidos sem correspondências.
  Nesse caso a resposta é HTTP 200, os quatro indicadores são zero e os
  arrays de faturamento mensal e ranking de produtos ficam vazios.
- Opções de filtros, diagnóstico de qualidade e resumo da limpeza continuam
  representando a planilha completa. Datas inválidas ou invertidas e
  planilhas sem vendas válidas continuam retornando HTTP 422.

O dashboard exibe os dois períodos separadamente. A última venda do mês
não comprova que os dados do mês são parciais, por isso não gera esse aviso.
Sem meses há um estado vazio; com um mês há um cartão de faturamento;
com dois ou mais há um gráfico de linha com mês e ano.
Limpar filtros limpa os três campos e consulta novamente a planilha sem
parâmetros de filtro. O arquivo é reenviado pela aplicação a cada consulta.

Para verificar, instale `requirements-dev.txt` e execute `python -m pytest -q`.
No diretório `frontend`, execute `npm ci` e `npm run build`.
