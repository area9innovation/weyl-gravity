#!/usr/bin/env python3
"""Independent replay of the combined-q1 linear-K obstruction."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import sympy as sp
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "closed_universe_observers"
C = (
    P
    / "certificates/"
    "BERGER_DYNAMICAL_APPARATUS_COMBINED_Q1_CROSSWALK_OBSTRUCTION.json"
)
X = (
    P
    / "certificates/"
    "BERGER_DYNAMICAL_APPARATUS_COMBINED_Q1_K_OBSTRUCTION_PAYLOAD.json"
)
SCHEMA = (
    P
    / "schema/"
    "berger-dynamical-apparatus-combined-q1-crosswalk-obstruction-v1.schema.json"
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    cert, payload = json.loads(C.read_text()), json.loads(X.read_text())
    Draft202012Validator(json.loads(SCHEMA.read_text())).validate(cert)
    assert sha(X) == cert["payload_ref"]["sha256"]
    for ref in cert["dependency_refs"].values():
        assert sha(ROOT / ref["path"]) == ref["sha256"]

    # Independent coefficient comparison for s*A*B=C*s^2.
    A = sp.diag(sp.Matrix([[0, -1], [1, 0]]), sp.Matrix([[0, -1], [1, 0]]))
    B = sp.symbols("b0:12")
    Cvars = sp.symbols("c0:12")
    bmat, cmat = sp.Matrix(4, 3, B), sp.Matrix(4, 3, Cvars)
    equations = list(A * bmat) + list(cmat)
    coefficient_matrix, _rhs = sp.linear_eq_to_matrix(equations, (*B, *Cvars))
    assert coefficient_matrix.rank() == 24
    assert len((*B, *Cvars)) - coefficient_matrix.rank() == 0
    recorded = payload["first_incompatibility"][
        "parent_material_rows_cannot_supply_missing_directions"
    ]
    assert recorded["coefficient_constraint_rank"] == 24
    assert recorded["constant_mixing_nullity"] == 0

    gate = json.loads(
        (
            P / "certificates/BERGER_84_ROW_APPARATUS_Q2_Q3_K_GATE.json"
        ).read_text()
    )["K_Berger_gate"]
    closure = gate["existing_rod_linear_symmetry_completion"]
    assert closure["current_real_rod_span_rank"] == 6
    assert closure["time_translation_closure_rank"] == 8
    assert closure["minimal_additional_real_rod_directions"] == 2
    assert not closure["constant_internal_6_by_6_completion_exists"]
    assert all(
        row["nonzero"] for row in gate["background_components"]["rod_witnesses"]
    )

    candidate = payload["candidate_pushout"]
    assert candidate["candidate_row_count"] == 156
    assert len(candidate["shared_row_relations"]) == 8
    assert candidate["parent_only_row_count"] == 48
    assert payload["minimal_repair"]["repaired_base_row_count"] == 112
    assert payload["minimal_repair"][
        "prospective_identified_union_row_count"
    ] == 160
    assert cert["interface_disposition"]["K_Berger_matrix"] == "OBSTRUCTED"
    assert all(
        status == "NO_CERTIFIED_MAP"
        for status in cert["downstream_disposition"].values()
    )
    print(
        "BERGER_DYNAMICAL_APPARATUS_COMBINED_Q1_CROSSWALK_OBSTRUCTION "
        "independent verification: PASS"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
