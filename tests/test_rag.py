from types import SimpleNamespace

import pytest

from src.rag import rag
from src.rag.rag import ComplianceRetriever


def test_retriever_init_requires_chroma_directory(monkeypatch):
    monkeypatch.setattr(rag.os.path, "exists", lambda path: False)

    with pytest.raises(FileNotFoundError, match="Vector database directory"):
        ComplianceRetriever()


def test_retriever_init_connects_collection(monkeypatch):
    calls = {}

    class FakeClient:
        def __init__(self, path):
            calls["path"] = path

        def get_collection(self, **kwargs):
            calls["collection"] = kwargs
            return "collection"

    monkeypatch.setattr(rag.os.path, "exists", lambda path: True)
    monkeypatch.setattr(rag.chromadb, "PersistentClient", FakeClient)
    monkeypatch.setattr(
        rag.embedding_functions,
        "SentenceTransformerEmbeddingFunction",
        lambda model_name: f"embedding:{model_name}",
    )

    retriever = ComplianceRetriever()

    assert calls["path"] == rag.CHROMA_DB_DIR
    assert calls["collection"]["name"] == rag.COLLECTION_NAME
    assert retriever.collection == "collection"


def test_retrieve_policy_evidence_handles_empty_query():
    retriever = object.__new__(ComplianceRetriever)

    assert retriever.retrieve_policy_evidence("   ") == []


def test_retrieve_policy_evidence_unpacks_chroma_results():
    retriever = object.__new__(ComplianceRetriever)
    retriever.collection = SimpleNamespace(
        query=lambda **kwargs: {
            "ids": [["chunk-1", "chunk-2"]],
            "documents": [["Text 1", "Text 2"]],
            "metadatas": [
                [
                    {"source_policy": "POL-001", "section_scope": "Scope 1"},
                    {},
                ]
            ],
            "distances": [[0.123456, 0.9]],
        }
    )

    result = retriever.retrieve_policy_evidence("client profile", top_k=2)

    assert result == [
        {
            "chunk_id": "chunk-1",
            "policy_id": "POL-001",
            "section_scope": "Scope 1",
            "text": "Text 1",
            "similarity_distance": 0.1235,
        },
        {
            "chunk_id": "chunk-2",
            "policy_id": "UNKNOWN",
            "section_scope": "General",
            "text": "Text 2",
            "similarity_distance": 0.9,
        },
    ]


def test_retrieve_policy_evidence_handles_empty_results():
    retriever = object.__new__(ComplianceRetriever)
    retriever.collection = SimpleNamespace(query=lambda **kwargs: {"ids": [[]]})

    assert retriever.retrieve_policy_evidence("client profile") == []


def test_retrieve_policy_evidence_defaults_missing_distances():
    retriever = object.__new__(ComplianceRetriever)
    retriever.collection = SimpleNamespace(
        query=lambda **kwargs: {
            "ids": [["chunk-1"]],
            "documents": [["Text 1"]],
            "metadatas": [[{"source_policy": "POL-001"}]],
        }
    )

    assert retriever.retrieve_policy_evidence("client profile") == [
        {
            "chunk_id": "chunk-1",
            "policy_id": "POL-001",
            "section_scope": "General",
            "text": "Text 1",
            "similarity_distance": 0.0,
        }
    ]


def test_retrieve_best_chunk_for_policy_handles_empty_inputs():
    retriever = object.__new__(ComplianceRetriever)

    assert retriever.retrieve_best_chunk_for_policy("", "POL-001") is None
    assert retriever.retrieve_best_chunk_for_policy("query", "   ") is None


def test_retrieve_best_chunk_for_policy_unpacks_single_result():
    captured = {}

    def fake_query(**kwargs):
        captured.update(kwargs)
        return {
            "ids": [["chunk-1"]],
            "documents": [["Best text"]],
            "metadatas": [[{"source_policy": "POL-001", "section_scope": "Scope"}]],
            "distances": [[0.3333333]],
        }

    retriever = object.__new__(ComplianceRetriever)
    retriever.collection = SimpleNamespace(query=fake_query)

    result = retriever.retrieve_best_chunk_for_policy("query", "POL-001")

    assert captured["where"] == {"source_policy": "POL-001"}
    assert result == {
        "chunk_id": "chunk-1",
        "policy_id": "POL-001",
        "section_scope": "Scope",
        "text": "Best text",
        "similarity_distance": 0.333333,
    }


def test_retrieve_best_chunk_for_policy_defaults_distance_and_metadata():
    retriever = object.__new__(ComplianceRetriever)
    retriever.collection = SimpleNamespace(
        query=lambda **kwargs: {
            "ids": [["chunk-1"]],
            "documents": [["Best text"]],
            "metadatas": [[{}]],
            "distances": [[]],
        }
    )

    assert retriever.retrieve_best_chunk_for_policy("query", "POL-999") == {
        "chunk_id": "chunk-1",
        "policy_id": "POL-999",
        "section_scope": "General",
        "text": "Best text",
        "similarity_distance": 0.0,
    }


def test_retrieve_best_chunk_for_policy_handles_no_result():
    retriever = object.__new__(ComplianceRetriever)
    retriever.collection = SimpleNamespace(query=lambda **kwargs: {"ids": [[]]})

    assert retriever.retrieve_best_chunk_for_policy("query", "POL-001") is None
