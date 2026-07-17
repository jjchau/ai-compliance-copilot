from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

from src.config.paths import LOG_DIR


DEFAULT_RETRIEVAL_LOG_PATH = (
    LOG_DIR / "retrieval_contexts.jsonl"
)


def _json_safe(value: Any) -> Any:
    """
    Recursively convert common non-JSON-native values into
    JSON-serializable representations.
    """
    if value is None:
        return None

    if isinstance(
        value,
        (str, int, float, bool),
    ):
        return value

    if isinstance(value, Path):
        return str(value)

    if isinstance(value, Mapping):
        return {
            str(key): _json_safe(item)
            for key, item in value.items()
        }

    if isinstance(
        value,
        (list, tuple, set),
    ):
        return [
            _json_safe(item)
            for item in value
        ]

    if hasattr(value, "model_dump"):
        return _json_safe(
            value.model_dump(mode="json")
        )

    if hasattr(value, "value"):
        return _json_safe(value.value)

    return str(value)


def _sha256_text(value: str) -> str:
    return hashlib.sha256(
        value.encode("utf-8")
    ).hexdigest()


def _sha256_json(value: Any) -> str:
    serialized = json.dumps(
        value,
        ensure_ascii=False,
        separators=(",", ":"),
    )

    return hashlib.sha256(
        serialized.encode("utf-8")
    ).hexdigest()


def _normalize_chunk(
    chunk: Mapping[str, Any],
    *,
    fallback_rank: int,
    selected_position: int | None = None,
) -> dict[str, Any]:
    """
    Normalize one retrieved chunk without discarding its
    original semantic-retrieval rank.

    `rank` represents the original position in the raw
    semantic result.

    `selected_position`, when populated, represents the
    chunk's position in the final context sent to Gemini.
    """
    text = str(
        chunk.get("text") or ""
    )

    raw_rank = (
        chunk.get("rank")
        or chunk.get("original_rank")
        or fallback_rank
    )

    normalized = {
        "rank": int(raw_rank),
        "chunk_id": chunk.get(
            "chunk_id"
        ),
        "policy_id": chunk.get(
            "policy_id"
        ),
        "source_policy": chunk.get(
            "source_policy"
        ),
        "section_scope": chunk.get(
            "section_scope"
        ),
        "similarity_distance": chunk.get(
            "similarity_distance"
        ),
        "text": text,
        "text_sha256": _sha256_text(
            text
        ),
        "metadata": _json_safe(
            {
                key: value
                for key, value
                in chunk.items()
                if key
                not in {
                    "rank",
                    "original_rank",
                    "text",
                    "chunk_id",
                    "policy_id",
                    "source_policy",
                    "section_scope",
                    "similarity_distance",
                }
            }
        ),
    }

    if selected_position is not None:
        normalized[
            "selected_position"
        ] = selected_position

    return normalized


def _validate_selected_context(
    *,
    selected_chunks: Sequence[
        Mapping[str, Any]
    ],
    logged_retrieved_policies: Sequence[
        str
    ],
) -> None:
    """
    Enforce consistency between the selected chunks,
    policy audit list, and eventual Gemini context.
    """
    selected_policy_ids = [
        str(
            chunk.get("policy_id")
            or ""
        ).strip()
        for chunk in selected_chunks
    ]

    selected_chunk_ids = [
        str(
            chunk.get("chunk_id")
            or ""
        ).strip()
        for chunk in selected_chunks
    ]

    selected_texts = [
        str(
            chunk.get("text")
            or ""
        ).strip()
        for chunk in selected_chunks
    ]

    if any(
        not policy_id
        for policy_id
        in selected_policy_ids
    ):
        raise ValueError(
            "A selected retrieval chunk is "
            "missing policy_id."
        )

    if any(
        not chunk_id
        for chunk_id
        in selected_chunk_ids
    ):
        raise ValueError(
            "A selected retrieval chunk is "
            "missing chunk_id."
        )

    if any(
        not text
        for text in selected_texts
    ):
        raise ValueError(
            "A selected retrieval chunk has "
            "empty policy text."
        )

    if len(
        selected_policy_ids
    ) != len(
        set(selected_policy_ids)
    ):
        raise ValueError(
            "The selected Gemini context "
            "contains duplicate policy IDs."
        )

    normalized_logged_policies = [
        str(policy_id)
        for policy_id
        in logged_retrieved_policies
    ]

    if (
        normalized_logged_policies
        != selected_policy_ids
    ):
        raise ValueError(
            "logged_retrieved_policies "
            "does not match the ordered "
            "policy IDs in selected_chunks."
        )


def build_retrieval_log_record(
    *,
    trade_id: str,
    query_context: str,
    raw_chunks: Sequence[
        Mapping[str, Any]
    ],
    selected_chunks: Sequence[
        Mapping[str, Any]
    ],
    logged_retrieved_policies: Sequence[
        str
    ],
    retrieval_configuration: Mapping[
        str, Any
    ] | None = None,
    run_id: str | None = None,
    pipeline_version: str | None = None,
) -> dict[str, Any]:
    """
    Construct one complete retrieval audit record.

    `raw_chunks` is the full ordered semantic candidate
    set returned by the retriever.

    `selected_chunks` is the exact filtered,
    policy-deduplicated, ordered context sent to Gemini.
    """
    _validate_selected_context(
        selected_chunks=selected_chunks,
        logged_retrieved_policies=(
            logged_retrieved_policies
        ),
    )

    normalized_raw_chunks = [
        _normalize_chunk(
            chunk,
            fallback_rank=rank,
        )
        for rank, chunk in enumerate(
            raw_chunks,
            start=1,
        )
    ]

    normalized_selected_chunks = [
        _normalize_chunk(
            chunk,
            fallback_rank=position,
            selected_position=position,
        )
        for position, chunk in enumerate(
            selected_chunks,
            start=1,
        )
    ]

    exact_llm_context = [
        chunk["text"]
        for chunk
        in normalized_selected_chunks
    ]

    selected_chunk_ids = [
        chunk["chunk_id"]
        for chunk
        in normalized_selected_chunks
    ]

    selected_policy_ids = [
        chunk["policy_id"]
        for chunk
        in normalized_selected_chunks
    ]

    return {
        "timestamp": datetime.now(
            timezone.utc
        ).isoformat(),
        "run_id": run_id,
        "pipeline_version": (
            pipeline_version
        ),
        "trade_id": trade_id,
        "query_context": (
            query_context
        ),
        "query_sha256": _sha256_text(
            query_context
        ),
        "retrieval_configuration": (
            _json_safe(
                retrieval_configuration
                or {}
            )
        ),

        # Full ranked semantic candidate set.
        "raw_chunk_count": len(
            normalized_raw_chunks
        ),
        "raw_chunks": (
            normalized_raw_chunks
        ),
        "raw_policy_ids_in_rank_order": [
            chunk["policy_id"]
            for chunk
            in normalized_raw_chunks
        ],

        # Exact filtered and deduplicated
        # context sent to Gemini.
        "selected_chunk_count": len(
            normalized_selected_chunks
        ),
        "selected_chunks": (
            normalized_selected_chunks
        ),
        "selected_chunk_ids_in_order": (
            selected_chunk_ids
        ),
        "selected_policy_ids_in_order": (
            selected_policy_ids
        ),

        # Keep aligned with the AI-decision
        # audit record.
        "logged_retrieved_policies": list(
            logged_retrieved_policies
        ),

        # Exact ordered policy-text array
        # passed to Gemini.
        "llm_context": (
            exact_llm_context
        ),
        "llm_context_sha256": (
            _sha256_json(
                exact_llm_context
            )
        ),
    }


def log_retrieval_context(
    *,
    trade_id: str,
    query_context: str,
    raw_chunks: Sequence[
        Mapping[str, Any]
    ],
    selected_chunks: Sequence[
        Mapping[str, Any]
    ],
    logged_retrieved_policies: Sequence[
        str
    ],
    retrieval_configuration: Mapping[
        str, Any
    ] | None = None,
    run_id: str | None = None,
    pipeline_version: str | None = None,
    log_path: str | Path | None = None,
) -> dict[str, Any]:
    """
    Append one retrieval audit record to JSONL.

    The record preserves both:

    1. the complete ranked semantic candidate set; and
    2. the exact filtered, deduplicated context sent
       to Gemini.

    Returns the record so callers and tests can
    inspect it.
    """
    destination = Path(
        log_path
        or DEFAULT_RETRIEVAL_LOG_PATH
    )

    destination.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    record = build_retrieval_log_record(
        trade_id=trade_id,
        query_context=query_context,
        raw_chunks=raw_chunks,
        selected_chunks=(
            selected_chunks
        ),
        logged_retrieved_policies=(
            logged_retrieved_policies
        ),
        retrieval_configuration=(
            retrieval_configuration
        ),
        run_id=run_id,
        pipeline_version=(
            pipeline_version
        ),
    )

    with destination.open(
        "a",
        encoding="utf-8",
    ) as file:
        file.write(
            json.dumps(
                record,
                ensure_ascii=False,
            )
        )
        file.write("\n")

    return record