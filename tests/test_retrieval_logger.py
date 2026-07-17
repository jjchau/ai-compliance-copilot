import json
from pathlib import Path

import pytest

from src.logging.retrieval_logger import (
    _json_safe,
    build_retrieval_log_record,
    log_retrieval_context,
)


def make_chunk(**overrides):
    chunk = {
        "rank": 1,
        "chunk_id": "POL-002-KYC::1",
        "policy_id": "POL-002-KYC",
        "source_policy": "POL-002-KYC",
        "section_scope": "KYC completeness",
        "similarity_distance": 0.1234,
        "text": "Know-your-client information must be complete.",
        "source_path": Path("data/policies/POL-002-KYC.md"),
    }
    chunk.update(overrides)
    return chunk


def test_build_retrieval_log_record_preserves_raw_and_selected_context():
    raw_chunks = [
        make_chunk(),
        make_chunk(
            rank=2,
            chunk_id="POL-001-SUITABILITY::1",
            policy_id="POL-001-SUITABILITY",
            source_policy="POL-001-SUITABILITY",
            text="Recommendations must match the client profile.",
        ),
    ]
    selected_chunks = [raw_chunks[0]]

    record = build_retrieval_log_record(
        trade_id="TRADE-123",
        query_context="Client risk profile text",
        raw_chunks=raw_chunks,
        selected_chunks=selected_chunks,
        logged_retrieved_policies=["POL-002-KYC"],
        retrieval_configuration={"semantic_top_k": 10},
        run_id="RUN-1",
        pipeline_version="test",
    )

    assert record["trade_id"] == "TRADE-123"
    assert record["raw_chunk_count"] == 2
    assert record["selected_chunk_count"] == 1
    assert record["raw_policy_ids_in_rank_order"] == [
        "POL-002-KYC",
        "POL-001-SUITABILITY",
    ]
    assert record["selected_chunk_ids_in_order"] == ["POL-002-KYC::1"]
    assert record["selected_policy_ids_in_order"] == ["POL-002-KYC"]
    assert record["logged_retrieved_policies"] == ["POL-002-KYC"]
    assert record["llm_context"] == [
        "Know-your-client information must be complete."
    ]
    assert record["selected_chunks"][0]["selected_position"] == 1
    assert record["selected_chunks"][0]["text_sha256"]
    assert record["raw_chunks"][0]["metadata"]["source_path"] == str(
        Path("data/policies/POL-002-KYC.md")
    )


def test_build_retrieval_log_record_rejects_mismatched_policy_audit_list():
    with pytest.raises(ValueError, match="does not match"):
        build_retrieval_log_record(
            trade_id="TRADE-123",
            query_context="query",
            raw_chunks=[make_chunk()],
            selected_chunks=[make_chunk()],
            logged_retrieved_policies=["POL-001-SUITABILITY"],
        )


def test_build_retrieval_log_record_rejects_duplicate_selected_policy_ids():
    with pytest.raises(ValueError, match="duplicate policy IDs"):
        build_retrieval_log_record(
            trade_id="TRADE-123",
            query_context="query",
            raw_chunks=[
                make_chunk(),
                make_chunk(rank=2, chunk_id="POL-002-KYC::2"),
            ],
            selected_chunks=[
                make_chunk(),
                make_chunk(rank=2, chunk_id="POL-002-KYC::2"),
            ],
            logged_retrieved_policies=["POL-002-KYC", "POL-002-KYC"],
        )


def test_build_retrieval_log_record_rejects_missing_selected_fields():
    with pytest.raises(ValueError, match="missing policy_id"):
        build_retrieval_log_record(
            trade_id="TRADE-123",
            query_context="query",
            raw_chunks=[make_chunk()],
            selected_chunks=[make_chunk(policy_id="")],
            logged_retrieved_policies=[""],
        )

    with pytest.raises(ValueError, match="missing chunk_id"):
        build_retrieval_log_record(
            trade_id="TRADE-123",
            query_context="query",
            raw_chunks=[make_chunk()],
            selected_chunks=[make_chunk(chunk_id="")],
            logged_retrieved_policies=["POL-002-KYC"],
        )

    with pytest.raises(ValueError, match="empty policy text"):
        build_retrieval_log_record(
            trade_id="TRADE-123",
            query_context="query",
            raw_chunks=[make_chunk()],
            selected_chunks=[make_chunk(text="")],
            logged_retrieved_policies=["POL-002-KYC"],
        )


def test_log_retrieval_context_appends_jsonl_record(tmp_path):
    log_path = tmp_path / "retrieval_contexts.jsonl"

    record = log_retrieval_context(
        trade_id="TRADE-123",
        query_context="query",
        raw_chunks=[make_chunk()],
        selected_chunks=[make_chunk()],
        logged_retrieved_policies=["POL-002-KYC"],
        retrieval_configuration={"max_distance": 0.55},
        log_path=log_path,
    )

    lines = log_path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1
    assert json.loads(lines[0]) == record


def test_json_safe_handles_nested_non_native_values():
    class Dumpable:
        def model_dump(self, mode):
            return {"mode": mode, "value": {1, 2}}

    class Valued:
        value = "enum-value"

    assert _json_safe(None) is None
    assert _json_safe(
        {
            "tuple": (Path("a"), Valued()),
            "set": {"x"},
            "model": Dumpable(),
            "object": object(),
        }
    )["tuple"] == [str(Path("a")), "enum-value"]
    assert sorted(_json_safe({"set": {"x"}})["set"]) == ["x"]
    assert _json_safe({"model": Dumpable()})["model"] == {
        "mode": "json",
        "value": [1, 2],
    }
