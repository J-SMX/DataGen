from __future__ import annotations
import pandas as pd
import numpy as np


class ScenarioInjector:
    """
    Adds anomalies and fraud patterns to otherwise 'normal' data.
    """

    def add_duplicate_customers(self, customers: pd.DataFrame, ratio: float = 0.02) -> pd.DataFrame:
        """
        Introduce near-duplicate customers (same name/address, slight variations).
        """
        customers = customers.copy()
        n_duplicates = int(len(customers) * ratio)
        if n_duplicates == 0:
            return customers

        dup_indices = np.random.choice(customers.index, size=n_duplicates, replace=False)
        new_rows = []

        max_id = customers["customer_id"].str.extract(r"(\d+)$").astype(int).max()[0]
        next_id = max_id + 1

        for idx in dup_indices:
            row = customers.loc[idx].to_dict()
            row["customer_id"] = f"CUST_{next_id:06d}"

            # Slight variation (e.g., typo in last name)
            row["last_name"] = row["last_name"] + np.random.choice(["", "-", " Jr", " Sr"])
            new_rows.append(row)
            next_id += 1

        dup_df = pd.DataFrame(new_rows)
        return pd.concat([customers, dup_df], ignore_index=True)

    def add_structured_fraud_transactions(
        self,
        transactions: pd.DataFrame,
        accounts: pd.DataFrame,
        n_rings: int = 3,
        ring_size: int = 5,
    ) -> pd.DataFrame:
        """
        Very rough 'layering/smurfing' pattern: rings of accounts with circular flows.
        """
        transactions = transactions.copy()
        extra_rows = []
        account_ids = accounts["account_id"].tolist()

        for ring_idx in range(n_rings):
            if len(account_ids) < ring_size:
                break
            ring_accounts = list(np.random.choice(account_ids, size=ring_size, replace=False))
            for i in range(len(ring_accounts)):
                src = ring_accounts[i]
                dst = ring_accounts[(i + 1) % len(ring_accounts)]
                extra_rows.append(
                    {
                        "txn_id": f"FRD_RING_{ring_idx}_{i}",
                        "src_account_id": src,
                        "dst_account_id": dst,
                        "amount": 9_999.99,  # classic structuring threshold
                        "currency": "GBP",
                        "timestamp": transactions["timestamp"].max(),
                        "description": "Layering pattern",
                    }
                )

        if extra_rows:
            fraud_df = pd.DataFrame(extra_rows)
            transactions = pd.concat([transactions, fraud_df], ignore_index=True)

        return transactions
