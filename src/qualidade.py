
import pandas as pd


def diagnosticar(df: pd.DataFrame) -> dict:
    """Analisa a qualidade dos dados sem modificar a planilha."""

    return {
        "registros_recebidos": int(len(df)),

        "colunas": df.columns.tolist(),

        "duplicatas_exatas": int(df.duplicated().sum()),

        "valores_ausentes": {
            coluna: int(total)
            for coluna, total in df.isna().sum().items()
        },
    }
