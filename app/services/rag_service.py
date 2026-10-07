import json
import os
from typing import List
import chromadb
from chromadb.utils import embedding_functions


class RAGService:
    """Service class encapsulating ChromaDB vector storage and factual sports retrieval."""

    def __init__(self, db_path: str = "./chroma_db", collection_name: str = "sports_history"):
        self.db_path = db_path
        self.collection_name = collection_name
        self.client = chromadb.PersistentClient(path=self.db_path)
        self.embedding_function = embedding_functions.DefaultEmbeddingFunction()
        self.collection = self.get_or_create_collection()

    def get_or_create_collection(self):
        """Initializes or opens the sports history collection in ChromaDB."""
        return self.client.get_or_create_collection(
            name=self.collection_name,
            embedding_function=self.embedding_function
        )

    def populate_from_json(self, json_file_path: str = os.path.join("data", "sports_facts.json")) -> int:
        """Populates the vector collection from the seed JSON facts file if empty."""
        if self.collection.count() > 0:
            return self.collection.count()

        if not os.path.exists(json_file_path):
            raise FileNotFoundError(f"Could not find sports facts file at {json_file_path}")

        with open(json_file_path, "r", encoding="utf-8") as file:
            sports_facts = json.load(file)

        documents = []
        metadatas = []
        ids = []

        for item in sports_facts:
            documents.append(item["fact"])
            metadatas.append({
                "sport": item["sport"],
                "category": item.get("category", "General")
            })
            ids.append(str(item["id"]))

        self.collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        return len(documents)

    def retrieve_facts(self, sport: str, query: str, n_results: int = 2) -> List[str]:
        """Retrieves top matching historical facts filtered by sport."""
        results = self.collection.query(
            query_texts=[query],
            where={"sport": sport},
            n_results=n_results
        )

        if results and results.get("documents") and len(results["documents"]) > 0:
            return results["documents"][0]
        return []
