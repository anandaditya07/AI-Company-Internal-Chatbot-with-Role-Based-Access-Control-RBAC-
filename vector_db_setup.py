import os
from chromadb.config import Settings
from chromadb import PersistentClient
from chromadb.utils import embedding_functions
import json

# Initialize ChromaDB client
client = PersistentClient(path="vector_store")

# Load metadata
metadata_file = "vector_store/metadata.json"
with open(metadata_file, "r", encoding="utf-8") as f:
    metadata = json.load(f)

# Create collection
collection_name = "company_documents"
if collection_name not in client.list_collections():
    collection = client.create_collection(
        name=collection_name,
        embedding_function=embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
    )
else:
    collection = client.get_collection(collection_name)

# Add documents to collection
for chunk in metadata:
    collection.add(
        documents=[chunk["content"]],
        metadatas=[{
            "role": chunk["role"],
            "file_name": chunk["file_name"],
            "chunk_id": chunk["chunk_id"]
        }],
        ids=[f"{chunk['file_name']}_{chunk['chunk_id']}"],
        embeddings=[chunk["embedding"]]
    )

print("Vector database initialized and populated.")