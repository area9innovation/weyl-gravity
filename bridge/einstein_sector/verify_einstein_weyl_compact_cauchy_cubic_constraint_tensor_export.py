"""Independent representation and normalization audit for the cubic export."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import jsonschema
import sympy as sp

ROOT = Path(__file__).resolve().parents[2]
CERT = ROOT / "bridge/certificates/EINSTEIN_WEYL_COMPACT_CAUCHY_CUBIC_CONSTRAINT_TENSOR_EXPORT_OBSTRUCTION_V1.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein-weyl-compact-cauchy-cubic-constraint-tensor-export-obstruction-v1.schema.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_payload(payload: dict, files: bool = True) -> None:
    jsonschema.Draft202012Validator(json.loads(SCHEMA.read_text())).validate(payload)
    if files:
        assert payload["schema_sha256"] == sha(SCHEMA)
        assert payload["provenance"]["generator_sha256"] == sha(ROOT / payload["provenance"]["generator_path"])
        for item in payload["provenance"]["inputs"].values():
            path = ROOT / item["path"]
            assert sha(path) == item["sha256"]
            assert json.loads(path.read_text())["result_id"] == item["result_id"]

    inputs = payload["provenance"]["inputs"]
    action = json.loads((ROOT / inputs["selected_action"]["path"]).read_text())
    ledger = json.loads((ROOT / inputs["canonical_constraint_ledger"]["path"]).read_text())
    correction = json.loads((ROOT / inputs["balanced_correction"]["path"]).read_text())
    polar = json.loads((ROOT / inputs["polar_field_crosswalk"]["path"]).read_text())
    assert action["rational_fixture"]["parameters"]["alpha_B"] == "3"
    assert "(alpha_B/8)" in action["conventions"]["weyl_maxwell_action"]
    assert correction["classification"]["complete_second_order_extension_constructed"] is True
    assert polar["target_operator"]["coordinates"] == ["A_t=A+K", "B", "C_t=C-K", "U"]

    boundary = ledger["action_derived_constraint_ledger"]["normalization_boundary"]
    background = ledger["douglis_nirenberg_symbol"]["background_momentum_normalization"]
    assert "nonzero canonical rescaling" in boundary
    assert "suppressed nonzero action normalization" in background
    serialized = json.dumps(ledger, sort_keys=True)
    assert "ostrogradsky_crosswalk" not in serialized
    assert "boundary_term_convention" not in serialized

    # Reconstruct the exact scale ambiguity without producer helpers.
    e, s = sp.symbols("e s")
    isolated = -s**2 * (1 + e) ** 2 * sp.series((1 + e) ** sp.Rational(-1, 2), e, 0, 4).removeO() / 2
    cubic = sp.expand(isolated).coeff(e, 3)
    assert sp.simplify(cubic - s**2 / 32) == 0
    witness = payload["normalization_witness"]
    assert sp.simplify(sp.sympify(witness["epsilon_cubed_coefficient"], locals={"scale": s}) - cubic) == 0
    assert witness["scale_1"] == "1/32"
    assert witness["scale_2"] == "1/8"

    assert payload["first_absent_export"]["row"] == "H_perp"
    assert payload["classification"]["exact_action_to_canonical_normalization_present"] is False
    assert payload["classification"]["covariant_to_canonical_correction_crosswalk_present"] is False
    assert payload["classification"]["complete_cubic_tensor_exported"] is False


def main() -> None:
    verify_payload(json.loads(CERT.read_text()))


if __name__ == "__main__":
    main()
