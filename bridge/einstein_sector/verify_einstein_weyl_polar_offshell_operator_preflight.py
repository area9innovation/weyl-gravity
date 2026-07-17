"""Independent structural verifier for the polar off-shell preflight."""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/einstein_weyl_polar_offshell_operator_preflight.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_weyl_polar_offshell_operator_preflight.schema.json"


def verify_certificate() -> None:
    payload = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator(json.loads(SCHEMA.read_text(encoding="utf-8"))).validate(payload)
    contraction = sp.Matrix(payload["target_Weyl_gauge_contraction"]["target_field_map"])
    kernel = sp.Matrix([int(value) for value in payload["target_Weyl_gauge_contraction"]["target_field_map_kernel"]])
    assert contraction.rank() == 4
    assert contraction * kernel == sp.zeros(4, 1)
    assert payload["target_Weyl_gauge_contraction"]["source_operator_on_kernel"][6] == "-1"
    assert payload["available_exact_inputs"]["Weyl_Maxwell_full_Euler_operator"] is None
    assert payload["classification"]["polar_offshell_chain_map_constructed"] is False
    assert payload["classification"]["paper_A_freeze_affected"] is False


if __name__ == "__main__":
    verify_certificate()
