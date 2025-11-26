# src/se_datagen/ui/cli.py

from __future__ import annotations
import argparse
from pathlib import Path

from se_datagen.config import GenerationConfig
from se_datagen.engine.entities import EntityGenerator
from se_datagen.engine.relationships import RelationshipBuilder
from se_datagen.engine.scenarios import ScenarioInjector
from se_datagen.engine.export import Exporter, build_edge_list


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Synthetic SE data generator")
    parser.add_argument("--industry", default="banking", help="Industry template (banking, insurance, telco, ...)")
    parser.add_argument("--n-customers", type=int, default=500)
    parser.add_argument("--n-companies", type=int, default=100)
    parser.add_argument("--n-transactions", type=int, default=10_000)
    parser.add_argument("--no-fraud", action="store_true", help="Disable fraud/anomaly injection")
    parser.add_argument("--output-dir", default="./output")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = GenerationConfig(
        industry=args.industry,
        n_customers=args.n_customers,
        n_companies=args.n_companies,
        n_transactions=args.n_transactions,
        include_fraud=not args.no_fraud,
    )

    print(f"[+] Generating synthetic data for industry={config.industry}")

    # 1. Entities
    ent_gen = EntityGenerator(config)
    customers = ent_gen.generate_customers()
    companies = ent_gen.generate_companies()
    accounts = ent_gen.generate_accounts(customers)

    # 2. Relationships
    rel_builder = RelationshipBuilder(config)
    customers = rel_builder.assign_companies_to_customers(customers, companies)
    transactions = rel_builder.generate_transactions(accounts)

    # 3. Scenarios (fraud, anomalies)
    scenario_injector = ScenarioInjector()
    if config.include_fraud:
        customers = scenario_injector.add_duplicate_customers(customers, ratio=0.02)
        transactions = scenario_injector.add_structured_fraud_transactions(
            transactions, accounts, n_rings=3, ring_size=5
        )

    # 4. Edge list for graph / Quantexa-style ingestion
    edge_list = build_edge_list(customers, companies, accounts, transactions)

    # 5. Export
    exporter = Exporter(args.output_dir)
    output_dir = Path(args.output_dir)

    print(f"[+] Writing CSV/JSON files to {output_dir.resolve()}")
    exporter.to_csv("customers", customers)
    exporter.to_csv("companies", companies)
    exporter.to_csv("accounts", accounts)
    exporter.to_csv("transactions", transactions)
    exporter.to_csv("edges", edge_list)

    # Optional JSON for API demos
    exporter.to_json("customers", customers)
    exporter.to_json("transactions", transactions)

    print("[✓] Done.")


if __name__ == "__main__":
    main()
