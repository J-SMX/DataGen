from dataclasses import dataclass

@dataclass
class GenerationConfig:
    industry: str = "banking"
    n_customers: int = 500
    n_companies: int = 100
    n_accounts_per_customer: tuple[int, int] = (1, 3)  # min, max
    n_transactions: int = 10_000
    include_fraud: bool = True
    random_seed: int | None = 42
