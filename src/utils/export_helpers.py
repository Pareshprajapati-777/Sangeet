"""
Export Utilities for Sangeet.
Formats catalog query results into downloadable CSV and JSON strings.
"""

from typing import List, Dict, Any
import json
import pandas as pd

def to_csv_bytes(records: List[Dict[str, Any]]) -> bytes:
    df = pd.DataFrame(records)
    return df.to_csv(index=False).encode("utf-8")

def to_json_bytes(records: List[Dict[str, Any]]) -> bytes:
    return json.dumps(records, indent=2, default=str).encode("utf-8")
