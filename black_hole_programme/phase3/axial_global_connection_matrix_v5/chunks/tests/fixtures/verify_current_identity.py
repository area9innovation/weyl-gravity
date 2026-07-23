#!/usr/bin/env python3
"""Independent replay fixture for the handoff-schema mutation tests."""
from __future__ import annotations

import json
from pathlib import Path


data = json.loads(Path(__file__).with_name("current_identity.json").read_text())
assert data["result_id"] == "SYNTHETIC_ACTION_CURRENT_IDENTITY_V1"
assert data["claim_flags"]["radial_current_conservation_certified"] is True
assert data["identity"] == "A^dagger J + J A + d_r J = 0"
print("PASS")
