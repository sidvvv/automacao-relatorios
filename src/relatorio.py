from pathlib import Path

import xlsxwriter

from src import indicadores as ind


def gerar_relatorio(df, resumo, caminho="saida/relatorio.xlsx"):
    caminho = str(caminho)
    Path(caminho).parent.mkdir(parents=True, exist_ok=True)

    mensal = ind.vendas_por_mes(df)
    por_produto = ind.vendas_por_produto(df)
    n_m = len(mensal)
    n_p = len(por_produto)
    n_top = min(5, n_p)

    wb = xlsxwriter.Workbook(caminho)
    ws = wb.add_worksheet("Relatório")
    dados = wb.add_worksheet("Dados")

    titulo = wb.add_format({
        "bold": True, "font_size": 18, "font_color": "#FFFFFF",
        "bg_color": "#1F2A44", "valign": "vcenter", "indent": 1,
    })
    periodo = wb.add_format({"font_size": 10, "font_color": "#5F6B7A", "indent": 1})
    rotulo = wb.add_format({
        "font_size": 10, "font_color": "#5F6B7A", "bg_color": "#F1F4F9",
        "align": "center", "valign": "vcenter",
        "left": 2, "right": 2, "left_color": "#FFFFFF", "right_color": "#FFFFFF",
    })
    moeda = wb.add_format({
        "bold": True, "font_size": 20, "font_color": "#1F2A44", "bg_color": "#F1F4F9",
        "align": "center", "valign": "vcenter", "num_format": "R$ #,##0.00",
        "left": 2, "right": 2, "left_color": "#FFFFFF", "right_color": "#FFFFFF",
    })
    inteiro = wb.add_format({
        "bold": True, "font_size": 20, "font_color": "#1F2A44", "bg_color": "#F1F4F9",
        "align": "center", "valign": "vcenter", "num_format": "#,##0",
        "left": 2, "right": 2, "left_color": "#FFFFFF", "right_color": "#FFFFFF",
    })
    negrito = wb.add_format({"bold": True})
    numero = wb.add_format({"num_format": "#,##0"})

    ws.hide_gridlines(2)
    ws.set_column(0, 11, 13)
    ws.set_row(0, 36)
    ws.set_row(3, 40)

    ws.merge_range(0, 0, 0, 11, "Relatório executivo de vendas", titulo)
    inicio = df["data"].min().strftime("%d/%m/%Y")
    fim = df["data"].max().strftime("%d/%m/%Y")
    ws.merge_range(1, 0, 1, 11, f"Período: {inicio} a {fim}", periodo)

    cartoes = [
        ("Faturamento", ind.faturamento_total(df), moeda),
        ("Vendas", ind.numero_vendas(df), inteiro),
        ("Ticket médio", ind.ticket_medio(df), moeda),
        ("Clientes únicos", ind.clientes_unicos(df), inteiro),
    ]
    for i, (nome, valor, formato) in enumerate(cartoes):
        c = i * 3
        ws.merge_range(2, c, 2, c + 2, nome, rotulo)
        ws.merge_range(3, c, 3, c + 2, valor, formato)

    dados.set_column(0, 4, 16)
    dados.write_row(0, 0, ["Mês", "Faturamento"])
    for i, (mes, valor) in enumerate(mensal.items(), start=1):
        dados.write(i, 0, mes)
        dados.write(i, 1, valor)
    dados.write_row(0, 3, ["Produto", "Faturamento"])
    for i, (produto, valor) in enumerate(por_produto.items(), start=1):
        dados.write(i, 3, produto)
        dados.write(i, 4, valor)

    linha = wb.add_chart({"type": "line"})
    linha.add_series({
        "name": "Faturamento",
        "categories": ["Dados", 1, 0, n_m, 0],
        "values": ["Dados", 1, 1, n_m, 1],
        "line": {"color": "#2E6FD8", "width": 2.25},
        "marker": {"type": "circle", "size": 5},
    })
    linha.set_title({"name": "Vendas por mês (último mês parcial)", "name_font": {"size": 12}})
    linha.set_legend({"none": True})
    linha.set_y_axis({"num_format": "R$ #,##0"})
    linha.set_size({"width": 570, "height": 300})
    ws.insert_chart("A7", linha)

    rosca = wb.add_chart({"type": "doughnut"})
    rosca.add_series({
        "categories": ["Dados", 1, 3, n_p, 3],
        "values": ["Dados", 1, 4, n_p, 4],
        "data_labels": {"percentage": True},
    })
    rosca.set_title({"name": "Participação por produto", "name_font": {"size": 12}})
    rosca.set_legend({"position": "right"})
    rosca.set_size({"width": 570, "height": 300})
    ws.insert_chart("G7", rosca)

    barras = wb.add_chart({"type": "bar"})
    barras.add_series({
        "categories": ["Dados", 1, 3, n_top, 3],
        "values": ["Dados", 1, 4, n_top, 4],
        "fill": {"color": "#2E8B57"},
        "data_labels": {"value": True, "num_format": "R$ #,##0"},
    })
    barras.set_title({"name": "Top produtos", "name_font": {"size": 12}})
    barras.set_legend({"none": True})
    barras.set_y_axis({"reverse": True})
    barras.set_x_axis({"visible": False, "major_gridlines": {"visible": False}})
    barras.set_size({"width": 570, "height": 300})
    ws.insert_chart("A23", barras)

    ws.write("G24", "Resumo da limpeza", negrito)
    itens = [
        ("Linhas lidas", resumo["linhas_lidas"]),
        ("Duplicadas removidas", resumo["duplicadas_removidas"]),
        ("Campos corrigidos", resumo["campos_corrigidos"]),
    ]
    for i, (nome, valor) in enumerate(itens, start=24):
        ws.write(i, 6, nome)
        ws.write(i, 9, valor, numero)

    wb.close()
    return caminho