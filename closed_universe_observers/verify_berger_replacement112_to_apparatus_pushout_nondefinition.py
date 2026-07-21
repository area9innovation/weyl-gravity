#!/usr/bin/env python3
"""Independent verifier for the replacement112 pushout nondefinition."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import sympy as sp
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "closed_universe_observers"
C = P / "certificates/BERGER_REPLACEMENT112_TO_APPARATUS_PUSHOUT_NONDEFINITION.json"
X = P / "certificates/BERGER_REPLACEMENT112_TO_APPARATUS_PUSHOUT_NONDEFINITION_PAYLOAD.json"
SCHEMA = P / "schema/berger-replacement112-to-apparatus-pushout-nondefinition-v1.schema.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    certificate = json.loads(C.read_text())
    payload = json.loads(X.read_text())
    Draft202012Validator(json.loads(SCHEMA.read_text())).validate(certificate)
    assert sha(X) == certificate["payload_ref"]["sha256"]
    for reference in certificate["dependency_refs"].values():
        assert sha(ROOT / reference["path"]) == reference["sha256"]
    terminal_ref = certificate["dependency_refs"]["terminal_replacement112_payload"]
    terminal = json.loads((ROOT / terminal_ref["path"]).read_text())
    separator = payload["basis_independent_separator"]
    assert separator["defect_entry_count"] == terminal["mixed_nilpotency_obstruction"]["quotient_defect_count"] == 132
    assert separator["defect_position_count"] == 28
    assert separator["exact_specialization_rank_lower_bound"] == 1
    assert separator["zero_property_is_basis_invariant"] is True
    assert separator["witness"] == terminal["mixed_nilpotency_obstruction"]["first_exact_witness"]

    r10, r58, j = sp.symbols("r10 r58 j")
    value = sp.sympify(separator["witness_point_value"], locals={"r10": r10, "r58": r58, "j": j})
    ideal = sp.groebner([r10**2 - 10, r58**2 - 58, j**2 + 1], r10, r58, j, domain=sp.QQ)
    assert ideal.reduce(value)[1] != 0
    assert payload["category_of_complexes_gate"]["source_object_status"] == "OBSTRUCTED"
    assert payload["category_of_complexes_gate"]["pushout_status"] == "NONDEFINED"
    assert set(payload["consumer_activation"].values()) == {"NO_CERTIFIED_MAP"}
    print("BERGER_REPLACEMENT112_TO_APPARATUS_PUSHOUT_NONDEFINITION independent verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
