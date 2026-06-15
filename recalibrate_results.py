import sqlite3
import json
import ast
import pandas as pd

from src.data.schema import LabeledTrade
from src.orchestration.review_pipeline import build_reasoning_output

DB_PATH = "compliance_audit.db"

def main():
    conn = sqlite3.connect(DB_PATH)

    df = pd.read_sql(
        "SELECT * FROM audited_trades",
        conn
    )

    print(f"Loaded {len(df)} records.")

    cursor = conn.cursor()

    for i, (_, row) in enumerate(df.iterrows(), start=1):

        trade_dict = row.to_dict()

        # -----------------------
        # Deserialize JSON fields
        # -----------------------

        if isinstance(
            trade_dict.get("relevant_policies"),
            str
        ):
            trade_dict["relevant_policies"] = (
                ast.literal_eval(
                    trade_dict["relevant_policies"]
                )
            )

        retrieved_policies = []

        if isinstance(
            trade_dict.get("retrieved_policies"),
            str
        ):
            retrieved_policies = json.loads(
                trade_dict["retrieved_policies"]
            )

        retrieved_chunks = []

        if isinstance(
            trade_dict.get("retrieved_chunks"),
            str
        ):
            retrieved_chunks = json.loads(
                trade_dict["retrieved_chunks"]
            )

        trade = LabeledTrade(**trade_dict)

        # -----------------------
        # REASONING ONLY
        # -----------------------

        audit_payload = build_reasoning_output(
            trade,
            retrieved_policies,
            retrieved_chunks
        )

        cursor.execute(
            """
            UPDATE audited_trades
            SET
                compliance_probability = ?,
                compliance_label = ?,
                risk_score = ?,
                confidence_score = ?,
                escalation_level = ?,
                priority_score = ?,
                flag_reasons = ?
            WHERE trade_id = ?
            """,
            (
                audit_payload["compliance_probability"],
                int(
                    audit_payload[
                        "compliance_label"
                    ]
                ),
                audit_payload["risk_score"],
                audit_payload["confidence_score"],
                audit_payload["escalation_level"],
                audit_payload["priority_score"],
                audit_payload["flag_reasons"],
                trade.trade_id
            )
        )

        if i % 50 == 0:
            conn.commit()
            print(
                f"Updated {i}/{len(df)} records."
            )

    conn.commit()
    conn.close()

    print("Recalibration complete.")


if __name__ == "__main__":
    main()
