import os
import csv
from pathlib import Path
from typing import List, Dict
from sentence_transformers import SentenceTransformer

# Initialize embedding model
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

# Define roles and their document mappings
ROLE_DOCUMENT_MAPPING = {
    "Finance": ["financial_summary.md", "quarterly_financial_report.md"],
    "Marketing": [
        "market_report_q4_2024.md",
        "marketing_report_2024.md",
        "marketing_report_q1_2024.md",
        "marketing_report_q2_2024.md",
        "marketing_report_q3_2024.md",
    ],
    "HR": ["hr_data.csv"],
    "Engineering": ["engineering_master_doc.md"],
    "C-Level": [],
    "Employees": ["employee_handbook.md"],
}

# Preprocess documents
def preprocess_documents(base_path: str) -> List[Dict]:
    document_chunks = []

    for role, files in ROLE_DOCUMENT_MAPPING.items():
        for file_name in files:
            # Check if file exists in base_path or subfolders
            file_path = Path(base_path) / file_name
            if not file_path.exists():
                # Search in subfolders
                for subfolder in Path(base_path).iterdir():
                    if subfolder.is_dir():
                        potential_path = subfolder / file_name
                        if potential_path.exists():
                            file_path = potential_path
                            break

            if not file_path.exists():
                print(f"Warning: {file_name} not found in {base_path} or subfolders")
                continue

            if file_path.suffix == ".md":
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    chunks = chunk_text(content)

                    for idx, chunk in enumerate(chunks):
                        document_chunks.append({
                            "role": role,
                            "file_name": file_name,
                            "chunk_id": idx,
                            "content": chunk,
                        })

            elif file_path.suffix == ".csv":
                with open(file_path, "r", encoding="utf-8") as f:
                    reader = csv.reader(f)
                    content = "\n".join([", ".join(row) for row in reader])
                    chunks = chunk_text(content)

                    for idx, chunk in enumerate(chunks):
                        document_chunks.append({
                            "role": role,
                            "file_name": file_name,
                            "chunk_id": idx,
                            "content": chunk,
                        })

    return document_chunks

# Chunk text into smaller segments
def chunk_text(text: str, max_tokens: int = 300) -> List[str]:
    words = text.split()
    chunks = []

    for i in range(0, len(words), max_tokens):
        chunks.append(" ".join(words[i:i + max_tokens]))

    return chunks

# Generate embeddings and save metadata
def generate_embeddings_and_metadata(document_chunks: List[Dict], output_path: str):
    metadata = []

    for chunk in document_chunks:
        embedding = embedding_model.encode(chunk["content"]).tolist()
        chunk["embedding"] = embedding
        metadata.append(chunk)

    # Save metadata
    metadata_file = Path(output_path) / "metadata.json"
    with open(metadata_file, "w", encoding="utf-8") as f:
        import json
        json.dump(metadata, f, indent=4)

if __name__ == "__main__":
    base_path = "."
    output_path = "vector_store"

    os.makedirs(output_path, exist_ok=True)

    document_chunks = preprocess_documents(base_path)
    generate_embeddings_and_metadata(document_chunks, output_path)

    print("Preprocessing and embedding generation complete.")