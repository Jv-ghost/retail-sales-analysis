from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"


def load_data(data_dir=DATA_DIR):
    """
    Carrega as bases de vendas e clientes.
    """
    data_dir = Path(data_dir)

    vendas = pd.read_excel(data_dir / "varejo.xlsx")

    clientes = pd.read_excel(data_dir / "cliente_varejo.xlsx")

    return vendas, clientes


def clean_sales_data(vendas):
    """
    Trata valores ausentes e inconsistências
    identificadas na base de vendas.
    """
    vendas_clean = vendas.copy()

    vendas_clean = vendas_clean.dropna(subset=["Preço", "estado"])

    vendas_clean = vendas_clean[
        vendas_clean["Preço"] <= vendas_clean["Preço_com_frete"]
    ].copy()

    vendas_clean["Frete"] = vendas_clean["Preço_com_frete"] - vendas_clean["Preço"]

    return vendas_clean


def consolidate_customers(clientes):
    """
    Consolida múltiplos registros de cliente
    utilizando a mediana de idade e renda.
    """
    clientes_clean = clientes.groupby("cliente_Log", as_index=False).agg(
        idade=("idade", "median"), renda=("renda", "median")
    )

    return clientes_clean


def merge_sales_customers(vendas_clean, clientes_clean):
    """
    Integra vendas e clientes utilizando
    uma relação many-to-one.
    """
    vendas_clientes = vendas_clean.merge(
        clientes_clean, how="left", on="cliente_Log", validate="many_to_one"
    )

    return vendas_clientes


def prepare_data(data_dir=DATA_DIR):
    """
    Executa o pipeline completo de preparação.
    """
    vendas, clientes = load_data(data_dir)

    vendas_clean = clean_sales_data(vendas)

    clientes_clean = consolidate_customers(clientes)

    vendas_clientes = merge_sales_customers(vendas_clean, clientes_clean)

    return (vendas_clean, clientes_clean, vendas_clientes)


if __name__ == "__main__":
    vendas_clean, clientes_clean, vendas_clientes = prepare_data()

    print("Base de vendas tratada:", vendas_clean.shape)

    print("Base de clientes consolidada:", clientes_clean.shape)

    print("Base integrada:", vendas_clientes.shape)
