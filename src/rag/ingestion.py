"""
src/rag/ingestion.py
Description: Vector database ingestion pipeline. Loads structural chunks,
             generates vector embeddings using sentence-transformers, and
             populates a persistent local ChromaDB collection.
"""

import os
import sys
from pathlib import Path

# Ensure the root src folder is on the system path for clean relative imports
sys.path.append(str(Path(__file__).resolve().parents[2]))

import chromadb
from chromadb.utils import embedding_functions
from src.rag.chunking import create_chunks

# Storage configurations
POLICIES_DIR = "data/policies"
CHROMA_DB_DIR = "data/chroma"
COLLECTION_NAME = "regulatory_policies"

def run_ingestion_pipeline():
    """
    Executes the end-to-end ingestion pipeline:
    1. Extracts markdown files and builds contextual text chunks.
    2. Initializes a local, persistent ChromaDB database.
    3. Downloads/loads a local text embedding model via sentence-transformers.
    4. Commits vector data and structural metadata to disk.
    """
    print("=== Starting Compliance RAG Ingestion Pipeline ===")
    
    # Step 1: Generate your custom chunks
    print(f"[*] Scanning '{POLICIES_DIR}' for policy manuals...")
    try:
        chunks = create_chunks(POLICIES_DIR)
        if not chunks:
            print("[X] Ingestion aborted: No valid markdown chunks were generated. Add files to data/policies.")
            return
        print(f"[✓] Successfully generated {len(chunks)} structural policy chunks.")
    except Exception as e:
        print(f"[X] Chunking stage failed: {e}")
        return

    # Step 2: Set up persistent Chroma Client
    print(f"[*] Initializing persistent database cluster at '{CHROMA_DB_DIR}'...")
    os.makedirs(CHROMA_DB_DIR, exist_ok=True)
    chroma_client = chromadb.PersistentClient(path=CHROMA_DB_DIR)

    # Step 3: Configure sentence-transformers embedding function
    # 'all-MiniLM-L6-v2' is a lightweight, fast, industry-standard model for local embedding runs.
    print("[*] Loading local embedding model ('all-MiniLM-L6-v2')...")
    embedding_func = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )

    # Step 4: Create or reset the collection
    try:
        # If the collection already exists, delete it to ensure we don't duplicate keys on re-runs
        try:
            chroma_client.delete_collection(name=COLLECTION_NAME)
            print(f"[*] Flushed preexisting vector collection '{COLLECTION_NAME}' for clean rebuilt.")
        except Exception:
            pass # Collection didn't exist yet, safe to proceed
        
        collection = chroma_client.create_collection(
            name=COLLECTION_NAME,
            embedding_function=embedding_func,
            metadata={"hnsw:space": "cosine"} # Use cosine similarity for semantic distance mapping
        )
    except Exception as e:
        print(f"[X] Database collection initialization failed: {e}")
        return

    # Step 5: Unpack payloads and execute batch database insert
    print(f"[*] Vectorizing and uploading {len(chunks)} elements to ChromaDB...")
    
    ids = [c["chunk_id"] for c in chunks]
    documents = [c["text"] for c in chunks]
    metadatas = [c["metadata"] for c in chunks]

    try:
        collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas
        )
        print("=" * 60)
        print(f"[✓] SUCCESS: Compliance database populated!")
        print(f"[✓] Total Vectors Stored: {collection.count()}")
        print("=" * 60)
    except Exception as e:
        print(f"[X] Failed to write vectors to database: {e}")

if __name__ == "__main__":
    run_ingestion_pipeline()