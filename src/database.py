import json
import os

import chromadb
from chromadb.utils import embedding_functions

def get_chroma_client():
    """
    Creates or opens the local ChromaDB database.
    """

    client = chromadb.PersistentClient(
        path="./chroma_db"
    )

    return client



def setup_and_populate_db():
    """
    Creates the sports collection and stores all facts
    from sports_facts.json into ChromaDB.
    """

    client = get_chroma_client()

    embedding_function = embedding_functions.DefaultEmbeddingFunction()

    collection = client.get_or_create_collection(
        name="sports_history",
        embedding_function=embedding_function
    )
    if collection.count() > 0:
        print("Database already populated.")
    
        return collection
    
    json_file_path = os.path.join("data", "sports_facts.json")

    if not os.path.exists(json_file_path):
        raise FileNotFoundError(
            f"Could not find {json_file_path}"
        )

    with open(json_file_path, "r", encoding="utf-8") as file:
        sports_facts = json.load(file)
    
    documents = []
    metadatas = []
    ids = []
        
    for item in sports_facts:
        documents.append(item["fact"])
            
        metadatas.append({
            "sport": item["sport"],
            "category": item["category"]
        })
        ids.append(str(item["id"]))
    
    collection.add(
        documents=documents,
        metadatas=metadatas,
        ids=ids
    )

    print(f"Successfully inserted {len(documents)} sports facts into ChromaDB.")

    return collection

def query_historic_facts(sport, query_text, n_results=2):
    """
    Retrieves the most relevant historic facts for a given sport.
    """

    client = get_chroma_client()

    embedding_function = embedding_functions.DefaultEmbeddingFunction()

    collection = client.get_collection(
        name="sports_history",
        embedding_function=embedding_function
    )

    results = collection.query(
        query_texts=[query_text],
        where={"sport": sport},
        n_results=n_results
    )

    return results["documents"][0]