"""
src/rag/chunking.py
Description: Optimized, context-aware markdown chunking pipeline. 
             Combines explicit structural header-splitting with parent context 
             injection for financial compliance RAG retrieval architectures.
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Any

# Operational parameters optimized for sentence-transformers + layout extraction
MAX_CHARS = 800
MIN_CHARS = 150

def load_markdown_documents(policy_dir: str) -> List[Dict[str, str]]:
    """
    Scans the data directory and loads raw markdown documentation.
    Returns a list of tracking objects containing file identifiers and bodies.
    """
    documents = []
    policy_path = Path(policy_dir)
    
    if not policy_path.exists():
        raise FileNotFoundError(f"Configured policy directory does not exist: {policy_dir}")

    for path in policy_path.glob("*.md"):
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
        documents.append({
            "policy_id": path.stem, # Captures 'POL-001-SUITABILITY' from filename
            "text": text
        })
    return documents

def split_by_structural_headers(text: str) -> List[Dict[str, str]]:
    """
    Tokenizes raw markdown into explicit section arrays based on headings (H1-H4).
    Tracks and pairs headers with their subsequent content blocks.
    """
    # Lookahead capture split on markdown headers at the start of lines
    pattern = r"(^#{1,4}\s+.*$)"
    parts = re.split(pattern, text, flags=re.MULTILINE)
    
    sections = []
    current_header = "General Overview"
    
    # Process text before the very first markdown header if it exists
    first_block = parts[0].strip()
    if first_block:
        sections.append({"header": current_header, "text": first_block})
        
    # Iterate across captured heading/body content sequences
    for i in range(1, len(parts), 2):
        current_header = parts[i].strip().lstrip("#").strip()
        section_text = parts[i+1].strip() if (i + 1) < len(parts) else ""
        if section_text:
            sections.append({"header": current_header, "text": section_text})
            
    return sections

def chunk_section_paragraphs(section_text: str, policy_id: str, header_context: str) -> List[str]:
    """
    Evaluates section text lengths and partitions oversized regulatory blocks into 
    paragraph-bound strings, explicitly embedding structural parent metadata.
    """
    # Context injection layout header applied to the tip of EVERY block
    context_prefix = f"[{policy_id} > {header_context}]\n"
    
    # If the block fits into a single token pool comfortably, commit immediately
    if len(context_prefix + section_text) <= MAX_CHARS:
        return [context_prefix + section_text]

    paragraphs = section_text.split("\n\n")
    chunks = []
    current_chunk = ""

    for paragraph in paragraphs:
        paragraph = paragraph.strip()
        if not paragraph:
            continue

        # Formulate proposal text with contextual anchors
        if not current_chunk:
            proposed = context_prefix + paragraph
        else:
            proposed = current_chunk + "\n\n" + paragraph

        # Check chunk boundary compliance
        if len(proposed) <= MAX_CHARS:
            current_chunk = proposed
        else:
            # Flush existing chunk before opening next accumulation window
            if current_chunk.strip():
                chunks.append(current_chunk.strip())
            current_chunk = context_prefix + paragraph

    # Ensure tail blocks are caught and flushed
    if current_chunk.strip():
        chunks.append(current_chunk.strip())

    return chunks

def create_chunks(policy_dir: str) -> List[Dict[str, Any]]:
    """
    Main ingestion execution endpoint. Handles file streaming, context parsing, 
    and dictionary creation for downstream vector injection.
    """
    documents = load_markdown_documents(policy_dir)
    all_chunks = []

    for doc in documents:
        policy_id = doc["policy_id"]
        sections = split_by_structural_headers(doc["text"])
        chunk_counter = 0

        for sec in sections:
            # Generate paragraph chunks while carrying down the parent scope
            section_chunks = chunk_section_paragraphs(sec["text"], policy_id, sec["header"])

            for chunk_text in section_chunks:
                # Disregard single lines, table remnants, or layout artifacts
                if len(chunk_text.strip()) < MIN_CHARS:
                    continue

                all_chunks.append({
                    "chunk_id": f"{policy_id}_CH_{chunk_counter:03d}",
                    "policy_id": policy_id,
                    "text": chunk_text.strip(),
                    "metadata": {
                        "source_policy": policy_id,
                        "section_scope": sec["header"],
                        "char_count": len(chunk_text.strip())
                    }
                })
                chunk_counter += 1

    return all_chunks

# --- Local Verification and Test Framework ---
if __name__ == "__main__":
    # Ensure standard policy path directory exists out of the box
    os.makedirs("data/policies", exist_ok=True)
    
    print("=== Launching Combined Chunking Engine Diagnostic Review ===")
    try:
        processed_chunks = create_chunks("data/policies")
        print(f"[✓] Execution successful. Parsed total of {len(processed_chunks)} vector chunks.\n")
        
        # Display sample schema for integration verification
        if processed_chunks:
            print("--- Sample Structural Payload Contract (Chunk 0) ---")
            sample = processed_chunks[0]
            print(f"Database Key:  {sample['chunk_id']}")
            print(f"Foreign Key:   {sample['policy_id']}")
            print(f"Meta Contract: {sample['metadata']}")
            print(f"Embedded Text Body:\n{sample['text']}")
            print("=" * 60)
        else:
            print("[!] Setup Notification: Place your markdown policy documents (.md) inside data/policies to verify output parsing.")
            
    except Exception as e:
        print(f"[X] Engine fault encountered: {str(e)}")