"""
src/rag/rag.py
Description: Retrieval core engine. Takes operational query contexts,
             embeds them locally, and fetches matching policy evidence blocks
             from the persistent local ChromaDB storage layer.
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Any, cast

# Ensure the root src folder is on the system path for relative imports
sys.path.append(str(Path(__file__).resolve().parents[2]))

import chromadb
from chromadb.utils import embedding_functions

CHROMA_DB_DIR = "data/chroma"
COLLECTION_NAME = "regulatory_policies"

class ComplianceRetriever:
    def __init__(self):
        """
        Initializes the connection to the persistent local ChromaDB vector store
        and attaches the exact same local embedding model used during ingestion.
        """
        if not os.path.exists(CHROMA_DB_DIR):
            raise FileNotFoundError(
                f"Vector database directory not found at '{CHROMA_DB_DIR}'. "
                f"Please execute 'python src/rag/ingestion.py' first."
            )
            
        # Connect to local database instance
        self.chroma_client = chromadb.PersistentClient(path=CHROMA_DB_DIR)
        
        # Load local text embedding model via sentence-transformers
        self.embedding_func = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        
        # Retrieve reference to the existing policy collection
        self.collection = self.chroma_client.get_collection(
            name=COLLECTION_NAME,
            embedding_function=cast(Any, self.embedding_func)
        )

    def retrieve_policy_evidence(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Queries the vector database using semantic similarity search.
        
        Args:
            query: The case context text or string to match against rules.
            top_k: The max number of relevant policy chunks to return.
            
        Returns:
            A clean list of structured dictionary evidence payloads.
        """
        if not query.strip():
            return []

        # Execute semantic similarity vector lookup
        results = self.collection.query(
            query_texts=[query],
            n_results=top_k
        )

        # Unpack ChromaDB's highly nested array structures safely
        evidence_list = []
        
        # If no entries are returned, break out early
        if not results or not results['ids'] or len(results['ids'][0]) == 0:
            return []

        # Chroma query returns batches. Since we pass one query string, look at index 0.
        ids = results['ids'][0]
        documents = results['documents'][0]
        metadatas = results['metadatas'][0]
        distances = results['distances'][0] if 'distances' in results and results['distances'] else [0.0] * len(ids)

        for i in range(len(ids)):
            evidence_list.append({
                "chunk_id": ids[i],
                "policy_id": metadatas[i].get("source_policy", "UNKNOWN"),
                "section_scope": metadatas[i].get("section_scope", "General"),
                "text": documents[i],
                "similarity_distance": round(float(distances[i]), 4)
            })

        return evidence_list

# --- Local Verification Test Harness ---
if __name__ == "__main__":
    print("=== Launching Retrieval Engine Diagnostics ===")
    try:
        retriever = ComplianceRetriever()
        
        # Test scenario: Simulate a query matching one of our common synthetic test cases
        test_query = "Elderly client over age 70 purchasing highly volatile leveraged and inverse ETFs"
        print(f"[*] Running mock case query: '{test_query}'...\n")
        
        matches = retriever.retrieve_policy_evidence(test_query, top_k=2)
        
        print(f"[✓] Retrieved {len(matches)} matching compliance policy sections:\n")
        for idx, match in enumerate(matches):
            print(f"--- Match #{idx + 1} (Score/Distance: {match['similarity_distance']}) ---")
            print(f"Chunk Key:     {match['chunk_id']}")
            print(f"Regulatory Reference: {match['policy_id']} -> {match['section_scope']}")
            print(f"Extracted Evidence Body:\n{match['text']}")
            print("-" * 60)
            
    except Exception as e:
        print(f"[X] Retrieval engine failure: {str(e)}")