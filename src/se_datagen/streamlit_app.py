import streamlit as st
import os
import sys

src_path = os.path.abspath(__file__)
src_path = str(src_path[:-17])
sys.path.append(src_path)
print(src_path)

from config import GenerationConfig
from engine.entities import EntityGenerator
from engine.relationships import RelationshipBuilder
from engine.scenarios import ScenarioInjector
from engine.export import Exporter, build_edge_list




def main():
    st.title("SE Synthetic Data Generator")

    st.sidebar.header("Configuration")

    industry = st.sidebar.selectbox("Industry", ["banking", "insurance", "telco"])
    n_customers = st.sidebar.slider("Customers", 100, 10_000, 500, step=100)
    n_companies = st.sidebar.slider("Companies", 10, 1_000, 100, step=10)
    n_txn = st.sidebar.slider("Transactions", 1_000, 100_000, 10_000, step=1_000)
    include_fraud = st.sidebar.checkbox("Include fraud scenarios", value=True)
    output_dir = st.sidebar.text_input("Output directory", "./output")

    if st.button("Generate Data"):
        config = GenerationConfig(
            industry=industry,
            n_customers=n_customers,
            n_companies=n_companies,
            n_transactions=n_txn,
            include_fraud=include_fraud,
        )

        st.write("Generating data…")

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
        if include_fraud:
            customers = scenario_injector.add_duplicate_customers(customers, ratio=0.02)
            transactions = scenario_injector.add_structured_fraud_transactions(
                transactions, accounts, n_rings=3, ring_size=5
            )

        # 4. Edge list
        edges = build_edge_list(customers, companies, accounts, transactions)

        # 5. Export
        exporter = Exporter(output_dir)
        exporter.to_csv("customers", customers)
        exporter.to_csv("companies", companies)
        exporter.to_csv("accounts", accounts)
        exporter.to_csv("transactions", transactions)
        exporter.to_csv("edges", edges)

        st.success("Data generated!")
        st.write("Sample customers", customers.head())
        st.write("Sample transactions", transactions.head())
        st.write("Sample edges", edges.head())


if __name__ == "__main__":
    main()
