import sqlite3

import pandas as pd

import enrich_dataset


def make_labeled_row(**overrides):
    row = {
        "trade_id": "TRADE-1",
        "client_age": 40,
        "client_income": 100000,
        "risk_tolerance": "Medium",
        "investment_experience": "Intermediate",
        "investment_objective": "Growth",
        "investment_time_horizon": "Medium",
        "investment_type": "ETFs",
        "investment_amount": 10000.0,
        "advisor_id": "ADV-001",
        "advisor_experience": "Mid",
        "advisor_history_risk": "Low",
        "advisor_rationale": "Suitable long-term ETF allocation.",
        "advisor_notes": "Reviewed objectives.",
        "kyc_completeness": "Complete",
        "true_compliance": True,
        "case_type": "Aligned Recommendation",
        "scenario_name": "Aligned Recommendation",
        "difficulty": "Easy",
        "severity_tier": "Low",
        "expected_workflow_bucket": "Auto_pass",
        "relevant_policies": "[]",
        "primary_policy": "",
    }
    row.update(overrides)
    return row


def test_database_helpers_and_safe_float(tmp_path):
    conn = sqlite3.connect(tmp_path / "audit.db")
    enrich_dataset.init_database(conn)
    cursor = conn.cursor()

    assert enrich_dataset.is_already_processed(cursor, "TRADE-1") is False
    assert enrich_dataset.safe_float("1.25") == 1.25
    assert enrich_dataset.safe_float(None, default=9.0) == 9.0
    assert enrich_dataset.safe_float("bad", default=2.5) == 2.5

    conn.close()


def test_main_processes_row_retries_429_and_writes_audit_payload(
    monkeypatch,
    tmp_path,
):
    db_path = tmp_path / "audit.db"
    rows = pd.DataFrame([make_labeled_row(relevant_policies=None, primary_policy=None)])
    calls = {"build": 0, "sleep": []}

    def fake_build_review_case(trade):
        calls["build"] += 1
        if calls["build"] == 1:
            raise RuntimeError("429 RESOURCE_EXHAUSTED")
        return {
            "compliance_probability": "0.93",
            "compliance_label": True,
            "risk_score": "7",
            "confidence_score": None,
            "escalation_level": "NONE",
            "priority_score": None,
            "flag_reasons": "Looks aligned.",
            "retrieved_policies": ["POL-001-SUITABILITY"],
            "retrieved_chunks": [{"chunk_id": "c1"}],
        }

    monkeypatch.setattr(enrich_dataset.pd, "read_csv", lambda path: rows)
    monkeypatch.setattr(enrich_dataset, "DB_OUTPUT_PATH", str(db_path))
    monkeypatch.setattr(enrich_dataset, "CSV_INPUT_PATH", "input.csv")
    monkeypatch.setattr(enrich_dataset, "assign_primary_policy", lambda trade: "POL-001-SUITABILITY")
    monkeypatch.setattr(enrich_dataset, "build_review_case", fake_build_review_case)
    monkeypatch.setattr(enrich_dataset.time, "sleep", lambda seconds: calls["sleep"].append(seconds))

    enrich_dataset.main()

    conn = sqlite3.connect(db_path)
    stored = conn.execute(
        "SELECT trade_id, compliance_label, confidence_score, escalation_level, "
        "retrieved_policies, retrieved_chunks, primary_policy "
        "FROM audited_trades"
    ).fetchone()
    conn.close()

    assert calls["build"] == 2
    assert calls["sleep"] == [enrich_dataset.RATE_LIMIT_DELAY, enrich_dataset.SAFE_SLEEP_DELAY]
    assert stored == (
        "TRADE-1",
        1,
        1.0,
        "none",
        '["POL-001-SUITABILITY"]',
        '[{"chunk_id": "c1"}]',
        "POL-001-SUITABILITY",
    )


def test_main_skips_already_processed_rows(monkeypatch, tmp_path):
    db_path = tmp_path / "audit.db"
    rows = pd.DataFrame([make_labeled_row()])

    conn = sqlite3.connect(db_path)
    enrich_dataset.init_database(conn)
    conn.execute(
        "INSERT INTO audited_trades (trade_id, compliance_label) VALUES (?, ?)",
        ("TRADE-1", 1),
    )
    conn.commit()
    conn.close()

    monkeypatch.setattr(enrich_dataset.pd, "read_csv", lambda path: rows)
    monkeypatch.setattr(enrich_dataset, "DB_OUTPUT_PATH", str(db_path))
    monkeypatch.setattr(
        enrich_dataset,
        "build_review_case",
        lambda trade: (_ for _ in ()).throw(AssertionError("should skip")),
    )

    enrich_dataset.main()


def test_main_handles_csv_load_failure(monkeypatch, capsys):
    monkeypatch.setattr(
        enrich_dataset.pd,
        "read_csv",
        lambda path: (_ for _ in ()).throw(OSError("missing file")),
    )

    enrich_dataset.main()

    assert "Critical Error reading source CSV" in capsys.readouterr().out
