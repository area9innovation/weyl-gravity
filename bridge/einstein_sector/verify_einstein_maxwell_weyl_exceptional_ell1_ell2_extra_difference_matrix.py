"""Independent verifier for the exceptional/ell2-extra difference matrix."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_ell1_ell2_extra_difference_matrix.json"


def verify() -> None:
    record = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    assert record["result_id"] == "EINSTEIN_MAXWELL_WEYL_EXCEPTIONAL_ELL1_ELL2_EXTRA_DIFFERENCE_MATRIX"
    for item in [record["provenance"]["direct_source_helper"], *record["provenance"]["inputs"].values()]:
        assert hashlib.sha256((ROOT / item["path"]).read_bytes()).hexdigest() == item["sha256"]
    assert hashlib.sha256((ROOT / record["schema_path"]).read_bytes()).hexdigest() == record["schema_sha256"]
    parse = lambda value: sp.sympify(value, locals={"I": sp.I, "sqrt": sp.sqrt})
    witnesses = {"axial": sp.Matrix([0, -sp.Rational(1, 3), 0, 1]), "polar": sp.Matrix([0, 1, 0, 0])}
    projections = {}
    for key, values in record["direct_source_rows"].items():
        exceptional, extra, _ = key.split("/")
        output = "polar" if exceptional == extra else "axial"
        vector = sp.Matrix([parse(value) for value in values])
        projections[key] = sp.factor((witnesses[output].T * vector)[0])
        assert sp.simplify(projections[key] - parse(record["adjoint_projections"][key])) == 0
    nonzero = {key: value for key, value in projections.items() if value != 0}
    assert nonzero == {
        "axial/polar/e2": -sp.Rational(768, 5),
        "polar/polar/e2": -sp.Rational(864, 5),
    }
    classification = record["classification"]
    assert classification["six_adjoint_columns_zero"] is True
    assert classification["two_adjoint_columns_nonzero"] is True
    assert classification["unique_ell2_polar_e2_control_amplitude"] is True
    assert classification["SO3_all_m_tensor_assembled"] is False
    assert classification["complete_exceptional_mixed_bounded_zero_locus_solved"] is False
    assert classification["causal_or_quantum_claim"] is False
    print("EINSTEIN_MAXWELL_WEYL_EXCEPTIONAL_ELL1_ELL2_EXTRA_DIFFERENCE_MATRIX independent verification: PASS")


if __name__ == "__main__":
    verify()
