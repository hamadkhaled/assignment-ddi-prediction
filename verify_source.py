"""Verify the embedded CSV's source against the original supplementary workbook.

This is optional: the notebook can run on its own. Install pandas, numpy, and
openpyxl to use this independent provenance check. No files are modified.
"""
from pathlib import Path
import hashlib
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
workbook = ROOT / "data" / "amiajnl-2013-002512-s2.xlsx"
csv = ROOT / "data" / "source_cv.csv"
assert hashlib.sha256(workbook.read_bytes()).hexdigest() == "9d60b830a0c2035e3e7dfd73106a5e7db214284e2e439a37e3869264ccf83cdf"
assert hashlib.sha256(csv.read_bytes()).hexdigest() == "b50d5679de3f8dfd213777e0f555867573e6810b322c9024bc5c5ad071412a58"
original = pd.read_excel(workbook, sheet_name="5-fold CV", engine="openpyxl")
extracted = pd.read_csv(csv, float_precision="round_trip")
assert original.columns.tolist() == extracted.columns.tolist()
assert original.shape == extracted.shape == (13952, 7)
for col in original.columns:
    if pd.api.types.is_numeric_dtype(original[col]):
        np.testing.assert_array_equal(original[col].to_numpy(), extracted[col].to_numpy())
    else:
        assert original[col].tolist() == extracted[col].tolist(), col
print("Verified original workbook hash, extracted CSV hash, schema, row order, labels, IDs, and every numeric value.")
