#!/usr/bin/env python3
"""Independent consumer for the coefficient-jet PBW requirements gate."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


CERT = ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_COEFFICIENT_JET_PBW_REQUIREMENTS_V1.json"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _compose(outer, inner, x):
    output = {}
    for i, a in outer.items():
        for j, b in inner.items():
            for r in range(i + 1):
                order = i - r + j
                output[order] = sp.expand(
                    output.get(order, 0)
                    + sp.binomial(i, r) * a * sp.diff(b, x, r)
                )
    return {order: value for order, value in output.items() if value != 0}


def verify() -> None:
    payload = json.loads(CERT.read_text())
    if payload["result_id"] != "NARIAI_TRANSVERSE_COEFFICIENT_JET_PBW_REQUIREMENTS_V1":
        raise AssertionError("wrong result id")
    for reference in payload["dependency_refs"].values():
        path = ROOT / reference["path"]
        dependency = json.loads(path.read_text())
        if dependency["result_id"] != reference["result_id"] or _sha(path) != reference["sha256"]:
            raise AssertionError(f"dependency mismatch: {path}")

    # Independent ordinary-differential-operator associativity replay.  This
    # does not call the certificate producer or its coefficient-jet algebra.
    x, epsilon = sp.symbols("x epsilon")
    a = {2: sp.Integer(1), 0: sp.Integer(2)}
    b = {1: sp.Integer(3), 0: 5 + epsilon * 7 * sp.exp(x)}
    c = {1: sp.Integer(11), 0: 13 + epsilon * 17 * sp.exp(x)}
    left = _compose(_compose(a, b, x), c, x)
    right = _compose(a, _compose(b, c, x), x)
    if left != right:
        raise AssertionError("direct polynomial fixture is nonassociative")
    expected_counts = []
    for jet_order in range(4):
        count = 0
        for coefficient in left.values():
            value = sp.diff(
                sp.diff(coefficient, epsilon).subs(epsilon, 0), x, jet_order
            ).subs(x, 0)
            count += int(value != 0)
        expected_counts.append(count)
    rows = payload["exact_data"]["backend_theorem"]["checked_output_coefficient_jet_orders"]
    if [row["nonzero_coefficients"] for row in rows] != expected_counts:
        raise AssertionError("backend/direct coefficient counts differ")

    requirements = payload["exact_data"]["nariai_replay_requirements"]
    l0 = requirements["corrected_L0_positive_coefficient_jet_words_required_for_first_square"]
    l1 = requirements["corrected_L1_positive_coefficient_jet_words_required_for_associativity"]
    if l0 != [[0], [1], [2], [3]]:
        raise AssertionError(f"L0 jet ledger drifted: {l0}")
    expected_l1 = [[0], [1], [2], [3]] + [
        [a, b] for a in range(4) for b in range(a, 4)
    ]
    if l1 != expected_l1:
        raise AssertionError(f"L1 jet ledger drifted: {l1}")
    if requirements["positive_order_corrected_splitting_jets_available"] is not False:
        raise AssertionError("missing splitting jets were promoted")
    if payload["flags"]["NARIAI_TRANSVERSE_ASSOCIATIVE_PBW_REPLAY"] is not False:
        raise AssertionError("Nariai replay was overpromoted")
    if payload["flags"]["TRANSVERSE_COMPLETE_RANK_310_SDR_FIRST_VARIATION"] is not False:
        raise AssertionError("rank-310 SDR was overpromoted")
    for name, digest in payload["source_manifest"].items():
        path = ROOT / name
        if not path.is_file() or _sha(path) != digest:
            raise AssertionError(f"source manifest mismatch: {name}")


if __name__ == "__main__":
    verify()
    print("NARIAI_TRANSVERSE_COEFFICIENT_JET_PBW_REQUIREMENTS_V1 independent verification: PASS")
