from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_PATH = BASE_DIR / "data" / "runtime" / "trades_runtime.csv"

df = pd.read_csv(DATA_PATH)

df = df.fillna("")

raw_cases = df.to_dict(orient="records")