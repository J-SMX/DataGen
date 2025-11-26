# src/se_datagen/engine/export.py

from __future__ import annotations
from pathlib import Path
import pandas as pd


class Exporter:
    """
    Handles exporting tabular data to disk (CSV / JSON).

    You can extend this class later with Parquet, Excel, etc.
    """

    def __init__(self, output_dir: str | Path):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def to_csv(self, name: str, df: pd.DataFrame) -> Path:
        path = self.output_dir / f"{name}.csv"
        df.to_csv(path, index=False)
        return path

    def to_json(self, name: str, df: pd.DataFrame, orient: str = "records") -> Path:
        path = self.output_dir / f"{name}.json"
        df.to_json(path, orient=orient, date_format="iso")
        return path


def build_edge_list(
    customers: pd.DataFrame,
    companies: pd.DataFrame,
    accounts: pd.DataFrame,
    transactions: pd.DataFrame,
) -> pd.DataFrame:
    """
    Create an edge list suitable for graph ingestion:

    - CUSTOMER -> ACCOUNT        (owns_account)
    - CUSTOMER -> COMPANY        (employed_by)
    - ACCOUNT  -> ACCOUNT        (transaction)
    """
    edges: list[dict[str, str]] = []

    # CUSTOMER -> ACCOUNT
    for _, row in accounts.iterrows():
        edges.append(
            {
                "source_id": row["customer_id"],
                "target_id": row["account_id"],
                "relationship_type": "owns_account",
            }
        )

    # CUSTOMER -> COMPANY (employment)
    if "employer_company_id" in customers.columns:
        employed = customers.dropna(subset=["employer_company_id"])
        for _, row in employed.iterrows():
            edges.append(
                {
                    "source_id": row["customer_id"],
                    "target_id": row["employer_company_id"],
                    "relationship_type": "employed_by",
                }
            )

    # ACCOUNT -> ACCOUNT (transactions)
    for _, row in transactions.iterrows():
        edges.append(
            {
                "source_id": row["src_account_id"],
                "target_id": row["dst_account_id"],
                "relationship_type": "transaction",
            }
        )

    return pd.DataFrame(edges)
