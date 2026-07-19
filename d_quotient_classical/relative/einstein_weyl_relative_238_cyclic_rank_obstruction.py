#!/usr/bin/env python3
"""Certify the odd-pairing rank obstruction on the proposed 238-row carrier."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
RESULT_ID = "EINSTEIN_WEYL_RELATIVE_238_ROW_CYCLIC_RANK_OBSTRUCTION_V1"
OUTPUT = ROOT / f"d_quotient_classical/certificates/{RESULT_ID}.json"
REPORT = ROOT / "d_quotient_classical/reports/einstein-weyl-relative-238-row-cyclic-rank-obstruction.md"
SCHEMA = ROOT / "d_quotient_classical/schema/relative-238-row-cyclic-rank-obstruction-v1.schema.json"
VERIFIER = ROOT / "d_quotient_classical/relative/verify_einstein_weyl_relative_238_cyclic_rank_obstruction.py"
TESTS = ROOT / "d_quotient_classical/relative/tests/test_einstein_weyl_relative_238_cyclic_rank_obstruction.py"

DEPENDENCIES = {
    "linear_triangle_components": ROOT / "bridge/einstein_sector/generated/einstein_weyl_relative_linear_triangle_v1/components.json",
    "de_rham_carrier": ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_FIVE_CURRENT_DE_RHAM_CARRIER_V1.json",
    "de_rham_q2": ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_FIVE_CURRENT_DE_RHAM_Q2_V1.json",
}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise TypeError(f"expected object: {path}")
    return value


def _artifact(path: Path, value: dict[str, Any]) -> dict[str, str]:
    return {
        "artifact_id": str(value.get("result_id", value.get("schema"))),
        "path": str(path.relative_to(ROOT)),
        "sha256": _sha(path),
    }


def exact_rank_audit() -> dict[str, Any]:
    triangle = _load(DEPENDENCIES["linear_triangle_components"])
    carrier = _load(DEPENDENCIES["de_rham_carrier"])
    cofiber = triangle["mapping_cofiber"]["degree_dimensions"]
    current = carrier["carrier"]["degree_ranks_minus2_to3"]
    if cofiber != [5, 20, 28, 19, 6] or current != [5, 25, 50, 50, 25, 5]:
        raise AssertionError("imported degree ranks changed")
    padded_cofiber = [*cofiber, 0]
    combined = [left + right for left, right in zip(padded_cofiber, current)]
    degrees = list(range(-2, 4))
    by_degree = dict(zip(degrees, combined))
    pairs = []
    minimum = 0
    for degree in (-2, -1, 0):
        dual = 1 - degree
        left, right = by_degree[degree], by_degree[dual]
        deficit = abs(left - right)
        minimum += deficit
        pairs.append({
            "degree": degree,
            "dual_degree": dual,
            "rank": left,
            "dual_rank": right,
            "rank_deficit": deficit,
            "required_addition_side": f"degree_{dual}" if left > right else f"degree_{degree}",
        })
    if combined != [10, 45, 78, 69, 31, 5] or minimum != 28:
        raise AssertionError("combined odd-pairing rank audit changed")
    return {
        "degree_range": degrees,
        "mapping_cofiber_ranks_padded": padded_cofiber,
        "de_rham_carrier_ranks": current,
        "combined_ranks": combined,
        "odd_pairing_degree": 1,
        "dual_degree_rule": "d_dual=1-d",
        "dual_pair_audit": pairs,
        "minimum_additional_rows_if_only_rows_are_added": minimum,
        "one_rank_minimal_degree_completion": {"degree_1": 9, "degree_2": 14, "degree_3": 5},
    }


def build() -> dict[str, Any]:
    dependencies = {name: _load(path) for name, path in DEPENDENCIES.items()}
    if not dependencies["linear_triangle_components"]["classification"]["support_local_mapping_cofiber"]:
        raise AssertionError("relative mapping cofiber is unavailable")
    if not dependencies["de_rham_carrier"]["classification"]["unary_cyclicity_exact"]:
        raise AssertionError("de Rham carrier cyclicity is unavailable")
    if not dependencies["de_rham_q2"]["classification"]["current_interface_cyclic_completion_exact"]:
        raise AssertionError("de Rham q2 interface is unavailable")
    audit = exact_rank_audit()
    return {
        "schema": "pure-weyl-relative-238-row-cyclic-rank-obstruction-v1",
        "result_id": RESULT_ID,
        "result_state": "FIXED_238_ROW_CARRIER_HAS_NO_NONDEGENERATE_DEGREE_ONE_ODD_PAIRING",
        "lifecycle_status": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "scope": {
            "theory": "Einstein-Maxwell source relative to Weyl-Maxwell target",
            "background": "compact magnetic Plebanski-Hacyan product",
            "boundaries": "support-local off-shell bundle complex before harmonic or causal reduction",
            "charge_sector": "five connected stabilizers H,P_x,J_1,J_2,J_3",
            "carrier": "78-row relative mapping cofiber direct-summed with the 160-row five-current de Rham/cotangent carrier",
            "degree": "-2 through 3",
            "parity": "candidate nondegenerate BV odd pairing of cohomological degree one",
            "ell": "not harmonic-reduced", "m": "not harmonic-reduced", "k": "not harmonic-reduced", "omega": "not harmonic-reduced"
        },
        "dependencies": {name: _artifact(path, dependencies[name]) for name, path in DEPENDENCIES.items()},
        "rank_audit": audit,
        "obstruction": {
            "necessary_condition": "a nondegenerate degree-one pairing requires rank(C^d)=rank(C^(1-d)) for every d",
            "failed_pairs": [[-2, 3], [-1, 2], [0, 1]],
            "conclusion": "no coefficient choice, differential cross-incidence, or q2 correction on the fixed 238 rows can make the carrier a nondegenerate cyclic BV complex",
            "minimum_enlargement_statement": "if rows are only added and degrees are unchanged, at least 28 new rows are necessary; the rank-minimal degree counts are 9 in degree 1, 14 in degree 2, and 5 in degree 3",
            "sufficiency_warning": "the rank-minimal 28-row completion is only necessary; bundle covariance, q1-square-zero, cyclic adjunction, q1q2 and support locality must still be solved",
        },
        "classification": {
            "combined_238_row_rank_census_exact": True,
            "nondegenerate_degree_one_odd_pairing_exists_on_fixed_carrier": False,
            "fixed_238_row_cyclic_bv_complex_possible": False,
            "minimum_additional_row_lower_bound": 28,
            "rank_minimal_degree_profile_identified": True,
            "noncyclic_238_row_q1q2_complex_obstructed": False,
            "larger_cyclic_mixed_bundle_carrier_obstructed": False,
            "altered_grading_or_quotient_obstructed": False,
            "causal_or_quantum_claim": False,
        },
        "next_gate": "CLASSIFY_THE_BUNDLE_TYPES_AND_INCIDENCE_OF_AT_LEAST_28_CYCLIC_COMPLETION_ROWS_BEFORE_ANY_FULL_Q2_SOLVE",
        "provenance": {
            "source_manifest": {
                str(path.relative_to(ROOT)): _sha(path)
                for path in (Path(__file__).resolve(), VERIFIER, TESTS, SCHEMA)
            },
            "verification_commands": [
                "PYTHONPATH=. python3 -m d_quotient_classical.relative.einstein_weyl_relative_238_cyclic_rank_obstruction --check --guards",
                "PYTHONPATH=. python3 -m d_quotient_classical.relative.verify_einstein_weyl_relative_238_cyclic_rank_obstruction",
                "python3 -m unittest d_quotient_classical.relative.tests.test_einstein_weyl_relative_238_cyclic_rank_obstruction",
                "npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true -s d_quotient_classical/schema/relative-238-row-cyclic-rank-obstruction-v1.schema.json -d d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_238_ROW_CYCLIC_RANK_OBSTRUCTION_V1.json",
            ],
        },
        "claim_boundary": (
            "This exact LOCAL-ALGEBRAIC theorem is a rank obstruction to a nondegenerate degree-one odd pairing on the fixed 238-row direct-sum carrier. It is independent of coefficient choices and therefore rules out a cyclic BV q1/q2 completion on those rows. It does not obstruct a noncyclic or presymplectic 238-row complex, a quotient or regrading, or a larger mixed-bundle carrier. The 28-row lower bound is necessary but not sufficient and does not itself construct the required cyclic incidence, causal Green data, arity three, observables, particles or quantum transfer."
        ),
    }


def validate(value: dict[str, Any]) -> None:
    schema = _load(SCHEMA)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)


def _render(value: object) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def _report() -> str:
    return r"""# Rank obstruction for the fixed 238-row cyclic carrier

The 78-row relative mapping cofiber has degree ranks

\[
(5,20,28,19,6)_{-2,\ldots,2},
\]

while the self-dual 160-row five-current de Rham carrier has ranks

\[
(5,25,50,50,25,5)_{-2,\ldots,3}.
\]

Their fixed direct sum therefore has ranks

\[
(10,45,78,69,31,5)_{-2,\ldots,3}.
\]

A nondegenerate BV odd pairing of degree one pairs degree (d) with degree
(1-d).  The three paired rank comparisons are

\[
10\neq5,\qquad45\neq31,\qquad78\neq69.
\]

Thus no choice of coefficients, differential cross-incidence, or arity-two
operation can make the fixed 238-row carrier a nondegenerate cyclic BV
complex.  If the repair only adds rows without changing degrees, it needs at
least (5+14+9=28) new directions: five in degree three, fourteen in degree
two, and nine in degree one.

This is only a necessary rank completion.  It does not identify the covariant
bundle types or prove that a 28-row completion can satisfy square-zero,
cyclicity, arity-two, locality, or causal identities.  Noncyclic and
presymplectic 238-row constructions are not ruled out.
"""


def _guards(value: dict[str, Any]) -> None:
    for key in (
        "nondegenerate_degree_one_odd_pairing_exists_on_fixed_carrier",
        "fixed_238_row_cyclic_bv_complex_possible",
        "noncyclic_238_row_q1q2_complex_obstructed",
        "larger_cyclic_mixed_bundle_carrier_obstructed",
        "altered_grading_or_quotient_obstructed",
        "causal_or_quantum_claim",
    ):
        mutant = deepcopy(value)
        mutant["classification"][key] = True
        try:
            validate(mutant)
        except Exception:
            continue
        raise AssertionError(f"mutation guard accepted classification.{key}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()
    value = build()
    validate(value)
    if args.write:
        OUTPUT.write_text(_render(value))
        REPORT.write_text(_report())
    if args.check and (OUTPUT.read_text() != _render(value) or REPORT.read_text() != _report()):
        raise AssertionError("238-row cyclic-rank outputs drifted")
    if args.guards:
        _guards(value)
    print(f"{RESULT_ID}: PASS")


if __name__ == "__main__":
    main()
