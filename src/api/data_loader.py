from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_PATH = BASE_DIR / "data" / "runtime" / "trades_runtime.csv"

"""def load_trade_data() -> pd.DataFrame:
    try:
        df = pd.read_csv(DATA_PATH)
        return df
    except Exception as e:
        print(f"Error loading trade data: {e}")
        return pd.DataFrame()"""

df = pd.read_csv(DATA_PATH)

df = df.fillna("")

cases = df.to_dict(orient='records')

case_lookup = {case['trade_id']: case for case in cases}