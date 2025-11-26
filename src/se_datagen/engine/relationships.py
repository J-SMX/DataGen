# src/se_datagen/engine/relationships.py

from __future__ import annotations
import numpy as np
import pandas as pd
from faker import Faker

from config import GenerationConfig

fake = Faker()


class RelationshipBuilder:
    def __init__(self, config: GenerationConfig):
        self.config = config

    def assign_companies_to_customers(
        self, customers: pd.DataFrame, companies: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Simple employer relationship: each customer randomly assigned a company (or None).
        """
        company_ids = companies["company_id"].tolist()
        company_ids_or_none = company_ids + [None]  # some unemployed / self-employed
        employers = np.random.choice(company_ids_or_none, size=len(customers))
        customers = customers.copy()
        customers["employer_company_id"] = employers
        return customers

    def generate_transactions(
        self, accounts: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Very simplistic transaction generator.
        """
        n = self.config.n_transactions
        account_ids = accounts["account_id"].tolist()
        rows = []

        for i in range(n):
            src = np.random.choice(account_ids)
            dst = np.random.choice(account_ids)
            # avoid self-transfer
            if dst == src and len(account_ids) > 1:
                dst = np.random.choice([a for a in account_ids if a != src])

            rows.append(
                {
                    "txn_id": f"TXN_{i+1:09d}",
                    "src_account_id": src,
                    "dst_account_id": dst,
                    "amount": round(float(np.random.lognormal(mean=3.5, sigma=1.0)), 2),
                    "currency": "GBP",
                    "timestamp": fake.date_time_between(start_date="-2y", end_date="now"),
                    "description": fake.sentence(nb_words=4),
                }
            )

        return pd.DataFrame(rows)
