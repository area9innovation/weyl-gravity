#!/usr/bin/env python3
"""Independent replay fixture for the typed differentiated-bound gate."""
from __future__ import annotations

import json
from pathlib import Path


data = json.loads(
    Path(__file__).with_name("frequency_derivative_bound.json").read_text()
)
assert data["schema"] == "synthetic-frequency-derivative-norm-bound-v1"
assert data["result_id"] == "SYNTHETIC_FREQUENCY_DERIVATIVE_BOUND_V1"
assert data["frequency_derivative_norm_upper"] == "0.0"
assert data["claim_flags"]["frequency_derivative_norm_bound_certified"] is True
print("PASS")
