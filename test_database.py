from src.database import setup_and_populate_db, query_historic_facts


def main():
    print("=" * 50)
    print("Setting up ChromaDB...")
    print("=" * 50)

    setup_and_populate_db()

    print("\nRetrieving Cricket facts...\n")

    results = query_historic_facts(
        sport="Cricket",
        query_text="History of Cricket",
        n_results=2
    )

    for i, fact in enumerate(results, start=1):
        print(f"{i}. {fact}")


if __name__ == "__main__":
    main()