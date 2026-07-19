"""Independent verifier for the exceptional ell=1 a,d pivot certificate."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_weyl_ad_exceptional_ell1_resonance_pivots.json"


def _parse(value: str) -> sp.Expr:
    return sp.sympify(value, locals={"I": sp.I, "sqrt": sp.sqrt, "t": sp.symbols("t", real=True)})


def verify() -> None:
    record = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    assert record["result_id"] == "EINSTEIN_MAXWELL_WEYL_AD_EXCEPTIONAL_ELL1_RESONANCE_PIVOTS"
    assert set(record["dependency_tags"]) == {"LOCAL-ALGEBRAIC", "REDUCED-MODE"}
    provenance = record["provenance"]
    for item in [provenance["direct_source_helper"], *provenance["inputs"].values()]:
        path = ROOT / item["path"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == item["sha256"]
    schema_path = ROOT / record["schema_path"]
    assert hashlib.sha256(schema_path.read_bytes()).hexdigest() == record["schema_sha256"]

    expected = {
        "axial": {
            "a": ["0", "2*I*(sqrt(3)*t - 21*I)/3", "0", "2*I*(sqrt(3)*t + I)"],
            "d": ["0", "sqrt(3)*I/3", "0", "sqrt(3)*I"],
            "witness": ["0", "-1/3", "0", "1"],
            "projected": {"a": "4*I*(4*sqrt(3)*t + 15*I)/9", "d": "8*sqrt(3)*I/9"},
        },
        "polar": {
            "a": ["0", "-I*(2*sqrt(3)*t - 3*I)", "0", "0"],
            "d": ["0", "-sqrt(3)*I", "0", "0"],
            "witness": ["0", "1", "0", "0"],
            "projected": {"a": "-I*(2*sqrt(3)*t - 3*I)", "d": "-sqrt(3)*I"},
        },
    }
    for parity, values in expected.items():
        witness = sp.Matrix([_parse(value) for value in record["adjoint_witnesses"][parity]])
        assert all(sp.simplify(witness[index] - _parse(value)) == 0 for index, value in enumerate(values["witness"]))
        for global_case in ("a", "d"):
            source = sp.Matrix([_parse(value) for value in record["direct_source_rows"][parity][global_case]])
            wanted_source = sp.Matrix([_parse(value) for value in values[global_case]])
            assert (source - wanted_source).applyfunc(sp.simplify) == sp.zeros(4, 1)
            projected = sp.factor((witness.T * source)[0])
            stored = _parse(record["projected_adjoint_polynomials"][parity][global_case])
            wanted = _parse(values["projected"][global_case])
            assert sp.simplify(projected - stored) == 0
            assert sp.simplify(projected - wanted) == 0

    classification = record["classification"]
    assert classification["a_times_exceptional_leading_pivot_nonzero_both_parities"] is True
    assert classification["d_times_exceptional_constant_pivot_nonzero_both_parities"] is True
    assert classification["exceptional_times_ell2_extra_difference_collision_open"] is True
    assert classification["complete_exceptional_mixed_bounded_zero_locus_solved"] is False
    assert classification["causal_or_quantum_claim"] is False
    assert "LIVE" in record["collision_ledger"]["exceptional_times_ell2_extra_difference"]
    print("EINSTEIN_MAXWELL_WEYL_AD_EXCEPTIONAL_ELL1_RESONANCE_PIVOTS independent verification: PASS")


if __name__ == "__main__":
    verify()
