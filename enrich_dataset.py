"""
enrich_dataset.py
Description: Dedicated batch enrichment engine with infinite fault tolerance for rate limits.
             Uses an active SQLite look-ahead check to seamlessly skip previously 
             processed records, enabling safe resumes if interrupted.
             
             Includes an infinite loop structure to survive Gemini 429 "RESOURCE_EXHAUSTED" 
             rate limits by executing recurring 65-second sleep cooldown cycles until 
             successful, while safely skipping to the next record on persistent non-429 failures.
"""

import sqlite3
import json
import time
import typing
import ast
import pandas as pd
from src.data.schema import Trade, LabeledTrade
from src.orchestration.review_pipeline import build_review_case
from src.decisioning.labeling import assign_primary_policy

# Configuration parameters
CSV_INPUT_PATH = "./data/runtime/trades_runtime_780holdout.csv"
#CSV_INPUT_PATH = "./data/runtime/trades_eval_stratified_v1.csv"
DB_OUTPUT_PATH = "compliance_audit.db"
SAFE_SLEEP_DELAY = 12.1    # Baseline pacing to honor 5 Requests-Per-Minute Free Tier constraints
RATE_LIMIT_DELAY = 65.0    # Cool-down wait time when hitting a 429 Resource Exhausted exception

def init_database(conn: sqlite3.Connection):
    """
    Initializes the audited_trades schema, ensuring both the string array column 
    and raw context chunks text blocks exist to satisfy the frontend contracts.
    """
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS audited_trades (
            trade_id TEXT PRIMARY KEY,
            trade_timestamp TEXT,
            client_age INTEGER,
            client_income REAL,
            risk_tolerance TEXT,
            investment_experience TEXT,
            investment_objective TEXT,
            investment_time_horizon TEXT,
            investment_type TEXT,
            investment_amount REAL,
            advisor_id TEXT,
            advisor_experience TEXT,
            advisor_history_risk TEXT,
            advisor_rationale TEXT,
            advisor_notes TEXT,
            kyc_completeness TEXT,
            true_compliance INTEGER,
            case_type TEXT,
            scenario_name TEXT,
            difficulty TEXT,
            severity_tier TEXT,
            expected_workflow_bucket TEXT,
            relevant_policies TEXT,
            primary_policy TEXT,
            compliance_probability REAL,
            compliance_label INTEGER,
            risk_score REAL,
            confidence_score REAL,
            escalation_level TEXT,
            priority_score REAL,
            flag_reasons TEXT,
            retrieved_policies TEXT,
            retrieved_chunks TEXT
        );
    """)
    conn.commit()

def is_already_processed(cursor: sqlite3.Cursor, trade_id: str) -> bool:
    """
    Checks if a valid audit entry already exists in the database.
    Allows the batch processor to resume on an existing database file without re-charging tokens.
    """
    cursor.execute("SELECT 1 FROM audited_trades WHERE trade_id = ? LIMIT 1;", (trade_id,))
    return cursor.fetchone() is not None

def safe_float(value, default=0.0) -> float:
    """Safely converts incoming parameters to floats, handling NoneType or malformed structures."""
    if value is None:
        return default
    try:
        return float(value)
    except (ValueError, TypeError):
        return default
    
def main():
    print("=== STARTING UNLIMITED-RETRY COMPLIANCE BATCH ENRICHMENT RUN ===")
    print(f"Reading source raw files from: {CSV_INPUT_PATH}")
    print(f"Targeting SQLite compliance ledger at: {DB_OUTPUT_PATH}")

    try:
        df = pd.read_csv(CSV_INPUT_PATH)
        print(f"[✓] Successfully loaded {len(df)} trade cases from CSV source file.")
    except Exception as e:
        print(f"[X] Critical Error reading source CSV mapping file: {e}")
        return

    # Establish database transaction connection
    conn = sqlite3.connect(DB_OUTPUT_PATH)
    init_database(conn)
    cursor = conn.cursor()

    # Process batch records sequentially using strict typing counter
    for current_count, (index, row) in enumerate(df.iterrows(), start=1):
        # Dictionary comprehension forces keys to 'str' type, clearing static type warnings
        trade_dict = {str(k): v for k, v in row.to_dict().items()}
        trade_dict = {k: None if pd.isna(v) else v for k, v in trade_dict.items()}
        trade_id = str(trade_dict.get("trade_id"))

        # 1. STATE INSPECTION PROGRESS CHECK (Automatic Skip Check)
        if is_already_processed(cursor, trade_id):
            print(f"[{current_count}/{len(df)}] Skipping Trade ID: {trade_id} (Already fully processed in ledger).")
            continue

        print(f"\n[{current_count}/{len(df)}] Processing Case Trade ID: {trade_id}...")

        success = False
        attempt_number = 0

        # Deserialize list fields loaded from CSV
        relevant_policies = trade_dict.get("relevant_policies")

        if relevant_policies is None:
            trade_dict["relevant_policies"] = []
        elif isinstance(relevant_policies, str):
            trade_dict["relevant_policies"] = ast.literal_eval(relevant_policies)
                
        # Convert pandas NaN to None
        if trade_dict.get("primary_policy") is None:
            trade_dict["primary_policy"] = assign_primary_policy(Trade(**trade_dict))

        # 2. INFINITE RETRY ENGINE LOOP FOR RATE LIMIT OVERLOADS
        while not success:
            try:
                attempt_number += 1
                
                # Instantiate Pydantic data schema validator
                trade = LabeledTrade(**trade_dict)

                # Extract Ground Truth Rules from internal module for local metrics verification
                #true_policies_list = get_relevant_policies(trade)
                #severity_tier = assign_severity_tier(trade)
                #expected_workflow_bucket = assign_expected_workflow_bucket(trade)
                #primary_policy = assign_primary_policy(trade)
                #true_compliance_val = 1 if trade_dict.get("true_compliance") in (1, True, "Compliant") else 0
                #case_type_val = str(trade_dict.get("case_type", "Standard Retail"))
                #scenario_name_val = str(trade_dict.get("scenario_name", "Default Scenario"))
                #difficulty_val = str(trade_dict.get("difficulty", "Medium"))

                # Execute unified RAG + Gemini AI orchestration pipeline
                audit_payload = build_review_case(trade)

                # Serialize arrays into clean JSON blocks for standard text columns
                relevant_policies_json = json.dumps(trade.relevant_policies)
                retrieved_policies_json = json.dumps(audit_payload.get("retrieved_policies", []))
                retrieved_chunks_json = json.dumps(audit_payload.get("retrieved_chunks", []))
                flag_reasons = audit_payload.get("flag_reasons", "No explanation generated.")

                # Commit payload cleanly to SQLite ledger rows using the safe_float helper
                cursor.execute("""
                    INSERT INTO audited_trades (
                        trade_id, trade_timestamp, client_age, client_income, risk_tolerance,
                        investment_experience, investment_objective, investment_time_horizon,
                        investment_type, investment_amount, advisor_id, advisor_experience,
                        advisor_history_risk, advisor_rationale, advisor_notes, kyc_completeness,
                        true_compliance, case_type, scenario_name, difficulty, severity_tier,
                        expected_workflow_bucket, relevant_policies, primary_policy,
                        compliance_probability, compliance_label, risk_score, confidence_score,
                        escalation_level, priority_score, flag_reasons, 
                        retrieved_policies, retrieved_chunks
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(trade_id) DO UPDATE SET
                        compliance_probability = excluded.compliance_probability,
                        compliance_label = excluded.compliance_label,
                        risk_score = excluded.risk_score,
                        confidence_score = excluded.confidence_score,
                        escalation_level = excluded.escalation_level,
                        priority_score = excluded.priority_score,
                        flag_reasons = excluded.flag_reasons,
                        relevant_policies = excluded.relevant_policies,
                        retrieved_policies = excluded.retrieved_policies,
                        retrieved_chunks = excluded.retrieved_chunks;
                """, (
                    trade.trade_id, trade.trade_timestamp, trade.client_age, trade.client_income,
                    trade.risk_tolerance, trade.investment_experience, trade.investment_objective,
                    trade.investment_time_horizon, trade.investment_type, trade.investment_amount,
                    trade.advisor_id, trade.advisor_experience, trade.advisor_history_risk,
                    trade.advisor_rationale, trade.advisor_notes, trade.kyc_completeness,
                    trade.true_compliance, trade.case_type, trade.scenario_name, trade.difficulty,
                    trade.severity_tier, trade.expected_workflow_bucket, relevant_policies_json,
                    trade.primary_policy,
                    # Wrap floats with safe_float defaults to capture NoneType outputs cleanly
                    safe_float(audit_payload.get("compliance_probability"), 0.0),
                    1 if audit_payload.get("compliance_label") else 0,
                    safe_float(audit_payload.get("risk_score"), 0.0),
                    safe_float(audit_payload.get("confidence_score"), 1.0),
                    str(audit_payload.get("escalation_level", "none")).lower(),
                    safe_float(audit_payload.get("priority_score"), 0.0),
                    str(flag_reasons),
                    retrieved_policies_json,
                    retrieved_chunks_json
                ))
                
                conn.commit()
                print(f"   [✓] Success on attempt {attempt_number}. Action Routing Category: {str(audit_payload.get('escalation_level')).upper()}")
                success = True

            except Exception as err:
                err_message = str(err)
                
                # 3. EXCEPTION 429 / RESOURCE EXHAUSTED HANDLER (PERSISTENT LOOPING)
                if "429" in err_message or "RESOURCE_EXHAUSTED" in err_message:
                    print(f"   [!] Rate limit encountered (429 Resource Exhausted) on attempt {attempt_number}.")
                    print(f"       Entering backoff cooldown. Sleeping for {RATE_LIMIT_DELAY} seconds before trying again...")
                    time.sleep(RATE_LIMIT_DELAY)
                
                # 4. SAFE-SKIPPING ON NON-429 TRANSIENT RUNTIME EXTREMITIES
                else:
                    print(f"   [!] Non-429 Operational Exception on case row {trade_id}: {err}")
                    print("       Safe-skipping this record to maintain structural pipeline progress.")
                    conn.rollback()
                    break # Breaks runtime loop to advance smoothly to the next row

        # Normal loop pacing wait interval to guarantee we remain comfortably within usage constraints
        if success:
            time.sleep(SAFE_SLEEP_DELAY)

    conn.close()
    print("\n[✓] Batch enrichment run completed successfully! The compliance ledger is perfectly aligned.")

if __name__ == "__main__":
    main()