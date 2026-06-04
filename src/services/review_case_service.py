"""
src/services/review_case_service.py
Description: Instantly serves the pre-audited analytical records from the local SQLite DB.
             Enables immediate server filtering and sorting across all 1,000 cases with $0.00 token cost.
"""

import sqlite3
import json

DB_PATH = "compliance_audit.db"

def dict_factory(cursor, row):
    """Converts raw database SQL rows into matching python dictionaries."""
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def _serialize_case(case_dict: dict) -> dict:
    """
    Sanitizes, serializes, and formats database rows to fulfill the frontend's
    expected TradeCase interface contract while preventing data leaks.
    """
    if not case_dict:
        return case_dict

    # 1. EXCLUDE PRIVILEGED COLUMNS FROM PAYLOAD
    case_dict.pop("true_compliance", None)
    case_dict.pop("case_type", None)
    case_dict.pop("relevant_policies", None)

    # 2. ENFORCE BOOLEAN TYPING FOR COMPLIANCE LABEL
    # SQLite saves booleans as integers (1 or 0). Standardize to JSON booleans.
    case_dict["compliance_label"] = case_dict.get("compliance_label") in (1, True)

    # 3. Safely inflate retrieved_policies and chunks back into true structural JSON lists
    for array_key in ["retrieved_policies", "retrieved_chunks"]:
        raw_val = case_dict.get(array_key)
        if isinstance(raw_val, str) and raw_val.strip().startswith("["):
            try:
                case_dict[array_key] = json.loads(raw_val)
            except Exception:
                case_dict[array_key] = []
        elif not raw_val:
            case_dict[array_key] = []

    # 4. LOWERCASE ESCALATION ROUTING STRINGS FOR THE LAYOUT FILTER MATCHES
    if case_dict.get("escalation_level"):
        case_dict["escalation_level"] = case_dict["escalation_level"].lower()

    return case_dict

def get_all_enriched_cases(escalation_filter: str | None = None) -> list[dict]:
    """
    Fetches all 1,000 fully evaluated cases instantly.
    Allows total, immediate sorting via frontend prioritization panels.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = dict_factory
    cursor = conn.cursor()
    
    if escalation_filter in ["urgent", "priority", "queue", "none"]:
        cursor.execute("SELECT * FROM audited_trades WHERE escalation_level = ?", (escalation_filter,))
    else:
        cursor.execute("SELECT * FROM audited_trades ORDER BY priority_score DESC")
        
    results = cursor.fetchall()
    conn.close()
    
    # Run serialization pipeline across the response array
    return [_serialize_case(dict(row)) for row in results]

def get_single_case_from_db(trade_id: str) -> dict | None:
    """
    Retrieves the complete audit ledger for a clicked row instantly.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = dict_factory
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM audited_trades WHERE trade_id = ?", (trade_id,))
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return _serialize_case(dict(result))
    return None