#!/usr/bin/env python3
"""Independent verifier for the retained-36 projector obstruction."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
DEFAULT = ROOT / "d_quotient_classical/certificates/BERGER_RETAINED_36_RESIDUAL_BRANCH_LOCAL_PROJECTOR_OBSTRUCTION_V1.json"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify(path: Path) -> None:
    data = json.loads(path.read_text())
    for dependency in data["dependency_refs"].values():
        dependency_path = ROOT / dependency["path"]
        if _sha(dependency_path) != dependency["sha256"]:
            raise AssertionError(f"dependency digest drifted: {dependency_path}")
    for source in data["provenance"]["source_manifest"]:
        source_path = ROOT / source["path"]
        if _sha(source_path) != source["sha256"]:
            raise AssertionError(f"source digest drifted: {source_path}")

    remainder_path = ROOT / data["dependency_refs"]["lower_by_two_remainder"]["path"]
    remainder = json.loads(remainder_path.read_text())
    terms = None
    for row, column, candidate in remainder["entries"]:
        if (row, column) == (0, 0):
            terms = candidate
            break
    if terms is None:
        raise AssertionError("entry (0,0) missing")

    p = sp.symbols("p0:4")
    u = 3 * sp.sqrt(10) / 20
    v = 2 * sp.sqrt(10) / 3
    symbol = 0
    for powers, raw in terms:
        if sum(powers) == 2:
            coefficient = sp.sympify(raw, locals={"u": u, "v": v})
            symbol += coefficient * sp.prod(p[index] ** powers[index] for index in range(4))
    expected = (71 * p[1] ** 2 + 71 * p[2] ** 2 + 9 * p[3] ** 2) / 80
    if sp.expand(symbol - expected) != 0:
        raise AssertionError("independent coefficient evaluation failed")
    wave = -p[0] ** 2 + p[1] ** 2 + p[2] ** 2 + p[3] ** 2
    if sp.rem(symbol, wave, p[0]) == 0:
        raise AssertionError("witness is wave-divisible")
    if sp.expand(symbol).coeff(p[1], 2) * sp.Rational(80, 71) != 1:
        raise AssertionError("witness normalization failed")

    lower = json.loads((ROOT / data["dependency_refs"]["metric_lower_by_two_biwave"]["path"]).read_text())
    obstruction = lower["canonical_factor_obstruction"]
    if obstruction["nonzero_degree_two_entries"] != 92 or obstruction["nondivisible_degree_two_entries"] != 92:
        raise AssertionError("full nondivisibility ledger failed")
    if data["flags"]["BERGER_RETAINED_36_RESIDUAL_BRANCH_BASIS_V2"] is not False:
        raise AssertionError("basis V2 was promoted")
    if data["flags"]["ELL3_BRANCH_PROJECTION_AUTHORIZED"] is not False:
        raise AssertionError("branch projection was authorized")
    if data["category_guards"]["topological_odd_direction_is_particle_branch"] is not False:
        raise AssertionError("topological direction misclassified")
    if data["principal_filtered_module_audit"]["solutions_a_b"] != [["0", "0"], ["1", "0"]]:
        raise AssertionError("dual-number audit failed")
    print("BERGER_RETAINED_36_RESIDUAL_BRANCH_LOCAL_PROJECTOR_OBSTRUCTION_V1 independent verification: PASS")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", nargs="?", type=Path, default=DEFAULT)
    args = parser.parse_args()
    verify(args.path)


if __name__ == "__main__":
    main()
