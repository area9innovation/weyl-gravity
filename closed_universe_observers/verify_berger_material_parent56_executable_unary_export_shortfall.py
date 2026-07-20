#!/usr/bin/env python3
"""Independent verifier for the material-parent executable-unary shortfall."""

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "closed_universe_observers"
C = P / "certificates/BERGER_MATERIAL_PARENT56_EXECUTABLE_UNARY_EXPORT_SHORTFALL.json"
X = P / "certificates/BERGER_MATERIAL_PARENT56_EXECUTABLE_UNARY_EXPORT_SHORTFALL_PAYLOAD.json"
SCHEMA = P / "schema/berger-material-parent56-executable-unary-export-shortfall-v1.schema.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sparse(matrix: sp.Matrix, shift: int = 0):
    return [
        {"output": shift + row, "input": col, "coefficient": sp.sstr(sp.factor(matrix[row, col]))}
        for row in range(matrix.rows) for col in range(matrix.cols) if matrix[row, col] != 0
    ]


def main() -> int:
    cert, payload = json.loads(C.read_text()), json.loads(X.read_text())
    Draft202012Validator(json.loads(SCHEMA.read_text())).validate(cert)
    assert sha256(X) == cert["payload_ref"]["sha256"]
    for ref in cert["dependency_refs"].values():
        assert sha256(ROOT / ref["path"]) == ref["sha256"]
    parent = json.loads((ROOT / cert["dependency_refs"]["parent_payload"]["path"]).read_text())
    physical = parent["carrier"]["physical_even_rows"]
    cotangent = parent["carrier"]["odd_cotangent_rows"]
    assert len(physical) == 28 and cotangent == [name + "_plus" for name in physical]
    assert [row["row_id"] for row in payload["carrier"]["rows"]] == physical + cotangent

    pairing = sp.zeros(56)
    for item in payload["carrier"]["pairing_entries"]:
        pairing[item["left"], item["right"]] = sp.sympify(item["coefficient"])
    assert pairing.rank() == 56
    assert pairing + pairing.T == sp.zeros(56)

    # Rebuild the quadratic variation directly, organized by the three
    # action summands rather than by the producer's exported block list.
    s, omega = sp.symbols("s Omega_K")
    d = sp.Matrix([[s, -omega], [omega, s]])
    h = sp.zeros(28)
    action_pairs = []
    for detector in range(2):
        action_pairs.append((
            [f"rod_orientation_{detector}_{i}" for i in range(2)],
            [f"rod_momentum_{detector}_{i}" for i in range(2)],
        ))
        action_pairs.append((
            [f"polarization_{detector}_{i}" for i in range(2)],
            [f"polarization_momentum_{detector}_{i}" for i in range(2)],
        ))
    for emitter in range(2):
        action_pairs.append((
            [f"emitter_phase_{emitter}_{i}" for i in range(2)],
            [f"emitter_phase_momentum_{emitter}_{i}" for i in range(2)],
        ))
    for coordinates, momenta in action_pairs:
        x = [physical.index(name) for name in coordinates]
        y = [physical.index(name) for name in momenta]
        for a in range(2):
            for b in range(2):
                h[y[a], x[b]] = d[a, b]
                h[x[a], y[b]] = -d[a, b]
    for detector in range(2):
        m = physical.index(f"memory_{detector}")
        lam = physical.index(f"memory_multiplier_{detector}")
        h[lam, m], h[m, lam] = s, -s
    assert sparse(h, 28) == payload["derivable_internal_unary"]["sparse_entries"]
    assert sparse(h.subs(s, 0), 28) == payload["derivable_internal_unary"]["zero_mode_sparse_entries"]
    assert h.rank() == 28 and h.subs(s, 0).rank() == 24
    assert h.T.applyfunc(lambda value: sp.expand(value.subs(s, -s))) == h

    q1 = sp.zeros(56)
    q1[28:56, 0:28] = h
    assert q1 * q1 == sp.zeros(56)
    detector = sp.zeros(2, 56)
    detector[0, physical.index("memory_0")] = 1
    detector[1, physical.index("memory_1")] = 1
    assert detector.rank() == 2 and detector * q1 == sp.zeros(2, 56)

    # Method-distinct decisive route: differentiate the displayed mixed
    # background-readout term with independent symbolic variables.
    lam0, lam1, f00, f01, f10, f11 = sp.symbols("lam0 lam1 f00 f01 f10 f11")
    mixed = -lam0 * f00 - lam1 * f11
    derivatives = [
        sp.diff(mixed, lam0, f00),
        sp.diff(mixed, f00, lam0),
        sp.diff(mixed, lam1, f11),
        sp.diff(mixed, f11, lam1),
    ]
    assert derivatives == [-1, -1, -1, -1]
    assert all(name not in physical for name in ("F_0_0", "F_0_1", "F_1_0", "F_1_1"))
    missing = payload["first_missing_variational_object"]
    assert len(missing["nonzero_unplaceable_derivatives"]) == 4
    assert {item["coefficient"] for item in missing["nonzero_unplaceable_derivatives"]} == {"-1"}
    assert missing["status"] == "NO_CERTIFIED_MAP"
    assert payload["disposition"]["complete_action_derived_material_parent_unary"] == "NO_CERTIFIED_MAP"
    print("BERGER_MATERIAL_PARENT56_EXECUTABLE_UNARY_EXPORT_SHORTFALL independent verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
