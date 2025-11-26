# src/se_datagen/engine/entities.py

from __future__ import annotations
from dataclasses import dataclass
from typing import Literal

import pandas as pd
from faker import Faker
import numpy as np

from config import GenerationConfig

fake = Faker()
Faker.seed(42)
np.random.seed(42)

EntityType = Literal["customer", "company", "account"]


@dataclass
class EntityGenerator:
    config: GenerationConfig

    def generate_customers(self) -> pd.DataFrame:
        rows = []
        for i in range(self.config.n_customers):
            rows.append(
                {
                    "customer_id": f"CUST_{i+1:06d}",
                    "first_name": fake.first_name(),
                    "last_name": fake.last_name(),
                    "email": fake.email(),
                    "phone": fake.phone_number(),
                    "address": fake.address().replace("\n", ", "),
                    "country": fake.country(),
                    "date_of_birth": fake.date_of_birth(minimum_age=18, maximum_age=85),
                }
            )
        return pd.DataFrame(rows)

    def generate_companies(self) -> pd.DataFrame:
        rows = []
        for i in range(self.config.n_companies):
            rows.append(
                {
                    "company_id": f"COMP_{i+1:06d}",
                    "name": fake.company(),
                    "registration_number": fake.bothify(text="REG########"),
                    "country": fake.country(),
                    "address": fake.address().replace("\n", ", "),
                    "sector": "Banking" if self.config.industry == "banking" else "Generic",
                }
            )
        return pd.DataFrame(rows)

    def generate_accounts(
        self, customers: pd.DataFrame
    ) -> pd.DataFrame:
        min_acc, max_acc = self.config.n_accounts_per_customer
        rows = []
        account_idx = 1

        for _, cust in customers.iterrows():
            n_accounts = np.random.randint(min_acc, max_acc + 1)
            for _ in range(n_accounts):
                rows.append(
                    {
                        "account_id": f"ACC_{account_idx:09d}",
                        "customer_id": cust["customer_id"],
                        "iban": fake.iban(),
                        "currency": "GBP",
                        "opened_date": fake.date_between(start_date="-5y", end_date="today"),
                    }
                )
                account_idx += 1

        return pd.DataFrame(rows)
