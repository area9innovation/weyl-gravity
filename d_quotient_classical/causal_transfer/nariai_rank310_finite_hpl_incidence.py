#!/usr/bin/env python3
"""Finite polynomial HPL theorem for the transverse rank-310 incidence."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

import d_quotient_classical.causal_transfer.nariai_parent_detour_mapping_cone_repair as repair
from d_quotient_classical.causal_transfer.nariai_transverse_rank310_dual_sdr import (
    abstract_fixture,
    matrix_adjoint,
    matrix_defects,
)


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "d_quotient_classical/causal_transfer"
OUTPUT = ROOT / "d_quotient_classical/certificates/NARIAI_RANK310_FINITE_HPL_INCIDENCE_THEOREM_V1.json"
REPORT = ROOT / "d_quotient_classical/reports/nariai-rank310-finite-hpl-incidence.md"
SCHEMA = ROOT / "d_quotient_classical/schema/nariai-rank310-finite-hpl-incidence-v1.schema.json"
VERIFIER = HERE / "verify_nariai_rank310_finite_hpl_incidence.py"
TESTS = HERE / "tests/test_nariai_rank310_finite_hpl_incidence.py"
CORE = HERE / "nariai_transverse_rank310_dual_sdr.py"

DEPENDENCIES = {
    "base_rank310_sdr": ROOT / "d_quotient_classical/certificates/NARIAI_PARENT_DETOUR_MAPPING_CONE_REPAIR_V1.json",
    "global_formal_variation": ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_GLOBAL_HPL_RANK310_CAUSAL_VARIATION_V1.json",
    "global_einstein_branch_obstruction": ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_KANTOWSKI_SACHS_GLOBAL_OBSTRUCTION_V1.json",
}

Matrix = repair.Matrix
Polynomial = dict[int, Matrix]


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise ValueError(f"dependency is not an object: {path}")
    return value


def _ref(path: Path, value: dict[str, Any]) -> dict[str, str]:
    return {
        "artifact_id": str(value["result_id"]),
        "path": str(path.relative_to(ROOT)),
        "sha256": _sha(path),
    }


def _poly_add(left: Polynomial, right: Polynomial) -> Polynomial:
    output: Polynomial = {}
    for degree in sorted(set(left) | set(right)):
        if degree in left and degree in right:
            output[degree] = repair._add(left[degree], right[degree])
        elif degree in left:
            output[degree] = left[degree]
        else:
            output[degree] = right[degree]
    return output


def _poly_scale(value: Polynomial, coefficient: int) -> Polynomial:
    return {degree: repair._scale(matrix, coefficient) for degree, matrix in value.items()}


def _poly_multiply(left: Polynomial, right: Polynomial) -> Polynomial:
    output: Polynomial = {}
    for left_degree, left_matrix in left.items():
        for right_degree, right_matrix in right.items():
            degree = left_degree + right_degree
            term = repair._multiply(left_matrix, right_matrix)
            output[degree] = term if degree not in output else repair._add(output[degree], term)
    return output


def _poly_adjoint(value: Polynomial) -> Polynomial:
    return {degree: matrix_adjoint(matrix) for degree, matrix in value.items()}


def _defects(value: Polynomial) -> dict[str, list[dict[str, Any]]]:
    return {
        str(degree): matrix_defects(matrix)
        for degree, matrix in sorted(value.items())
        if matrix_defects(matrix)
    }


def exact_fixture() -> dict[str, Any]:
    value = abstract_fixture()
    base = value["base"]
    delta = value["dotted"]["q_dot"]
    multiply, add, scale = repair._multiply, repair._add, repair._scale
    homotopy = base["homotopy"]

    incidence = {
        "Delta": matrix_defects(delta),
        "H_Delta": matrix_defects(multiply(homotopy, delta)),
        "Delta_H": matrix_defects(multiply(delta, homotopy)),
        "H_Delta_H": matrix_defects(multiply(multiply(homotopy, delta), homotopy)),
    }
    vanishings = {
        "Q_Delta_plus_Delta_Q": len(matrix_defects(add(multiply(base["q"], delta), multiply(delta, base["q"])))),
        "Delta_squared": len(matrix_defects(multiply(delta, delta))),
        "H_Delta_squared": len(matrix_defects(multiply(multiply(homotopy, delta), multiply(homotopy, delta)))),
        "Delta_H_squared": len(matrix_defects(multiply(multiply(delta, homotopy), multiply(delta, homotopy)))),
        "p_Delta_H_Delta_I": len(matrix_defects(multiply(multiply(multiply(multiply(base["projection"], delta), homotopy), delta), base["inclusion"]))),
    }
    if any(vanishings.values()):
        raise AssertionError(f"finite HPL incidence did not terminate: {vanishings}")

    q_full: Polynomial = {0: base["q"], 1: delta}
    inclusion: Polynomial = {
        0: base["inclusion"],
        1: scale(multiply(multiply(homotopy, delta), base["inclusion"]), -1),
    }
    projection: Polynomial = {
        0: base["projection"],
        1: scale(multiply(multiply(base["projection"], delta), homotopy), -1),
    }
    h_new: Polynomial = {
        0: homotopy,
        1: scale(multiply(multiply(homotopy, delta), homotopy), -1),
    }
    q_metric = _poly_multiply(_poly_multiply(projection, q_full), inclusion)
    expected_metric: Polynomial = {
        0: base["metric_q"],
        1: multiply(multiply(base["projection"], delta), base["inclusion"]),
    }
    metric_comparison = _defects(_poly_add(q_metric, _poly_scale(expected_metric, -1)))
    if metric_comparison:
        raise AssertionError(f"transferred metric differential gained higher terms: {metric_comparison}")

    full_identity: Polynomial = {0: repair._identity(len(base["q"]))}
    metric_identity: Polynomial = {0: repair._identity(len(base["metric_q"]))}
    full_pairing: Polynomial = {0: base["pairing"]}
    metric_pairing: Polynomial = {0: base["metric_pairing"]}
    degree_sign: Polynomial = {0: repair._degree_sign(repair.BLOCK_DEGREES)}

    identities = {
        "projection_inclusion": _poly_add(_poly_multiply(projection, inclusion), _poly_scale(metric_identity, -1)),
        "inclusion_chain": _poly_add(_poly_multiply(q_full, inclusion), _poly_scale(_poly_multiply(inclusion, expected_metric), -1)),
        "projection_chain": _poly_add(_poly_multiply(projection, q_full), _poly_scale(_poly_multiply(expected_metric, projection), -1)),
        "retract": _poly_add(
            _poly_add(full_identity, _poly_scale(_poly_multiply(inclusion, projection), -1)),
            _poly_scale(_poly_add(_poly_multiply(q_full, h_new), _poly_multiply(h_new, q_full)), -1),
        ),
        "homotopy_squared": _poly_multiply(h_new, h_new),
        "homotopy_inclusion": _poly_multiply(h_new, inclusion),
        "projection_homotopy": _poly_multiply(projection, h_new),
        "homotopy_odd_cyclic": _poly_add(
            _poly_multiply(_poly_adjoint(h_new), full_pairing),
            _poly_scale(_poly_multiply(_poly_multiply(degree_sign, full_pairing), h_new), -1),
        ),
        "metric_pairing_pullback": _poly_add(
            _poly_multiply(_poly_multiply(_poly_adjoint(inclusion), full_pairing), inclusion),
            _poly_scale(metric_pairing, -1),
        ),
        "projection_is_inclusion_adjoint": _poly_add(
            _poly_scale(_poly_multiply(_poly_multiply(metric_pairing, _poly_adjoint(inclusion)), full_pairing), -1),
            _poly_scale(projection, -1),
        ),
    }
    identity_defects = {name: _defects(polynomial) for name, polynomial in identities.items()}
    failed = {name: defects for name, defects in identity_defects.items() if defects}
    if failed:
        raise AssertionError(f"finite polynomial HPL identity failed: {failed}")

    inverse_left = add(repair._identity(len(base["q"])), multiply(homotopy, delta))
    inverse_right = add(repair._identity(len(base["q"])), scale(multiply(homotopy, delta), -1))
    inverse_defect = add(multiply(inverse_left, inverse_right), scale(repair._identity(len(base["q"])), -1))
    dual_inverse_left = add(repair._identity(len(base["q"])), multiply(delta, homotopy))
    dual_inverse_right = add(repair._identity(len(base["q"])), scale(multiply(delta, homotopy), -1))
    dual_inverse_defect = add(multiply(dual_inverse_left, dual_inverse_right), scale(repair._identity(len(base["q"])), -1))
    if matrix_defects(inverse_defect) or matrix_defects(dual_inverse_defect):
        raise AssertionError("finite HPL inverse identity failed")

    return {
        "coefficient_ring": "Q[epsilon] with noncommutative PBW operator atoms",
        "block_count": len(base["q"]),
        "delta_nonzero_blocks": incidence["Delta"],
        "H_delta_nonzero_blocks": incidence["H_Delta"],
        "delta_H_nonzero_blocks": incidence["Delta_H"],
        "H_delta_H_nonzero_blocks": incidence["H_Delta_H"],
        "nilpotence_defect_counts": vanishings,
        "identity_defect_counts": {name: 0 for name in identities},
        "metric_higher_order_defects": 0,
        "inverse_series_length": 2,
        "polynomial_degrees": {
            "Q_epsilon": 1,
            "I_epsilon": 1,
            "p_epsilon": 1,
            "H_epsilon": 1,
            "q_metric_epsilon": 1,
        },
    }


def build() -> dict[str, Any]:
    records = {name: _load(path) for name, path in DEPENDENCIES.items()}
    if not records["base_rank310_sdr"]["flags"]["SUPPORT_LOCAL_AUTOMORPHISM_SDR"]:
        raise ValueError("base rank-310 SDR drifted")
    if not records["global_formal_variation"]["flags"]["TRANSVERSE_FORMAL_RANK310_CAUSAL_VARIATION"]:
        raise ValueError("formal rank-310 variation drifted")
    if not records["global_einstein_branch_obstruction"]["flags"]["TRANSVERSE_KS_GLOBAL_FAMILY_OBSTRUCTED"]:
        raise ValueError("global Einstein-branch disposition drifted")
    fixture = exact_fixture()
    sources = {
        str(path.relative_to(ROOT)): _sha(path)
        for path in (Path(__file__).resolve(), VERIFIER, TESTS, SCHEMA, CORE)
    }
    return {
        "schema": "pure-weyl-nariai-rank310-finite-hpl-incidence-v1",
        "result_id": "NARIAI_RANK310_FINITE_HPL_INCIDENCE_THEOREM_V1",
        "result_state": "RANK310_TRANSVERSE_HPL_DENOMINATOR_TERMINATES_SUPPORT_LOCALLY",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "dependency_refs": {name: _ref(DEPENDENCIES[name], records[name]) for name in DEPENDENCIES},
        "theorem": {
            "statement": "For a finite rank-310 differential Q_epsilon=Q0+epsilon Delta with the certified transverse four-block incidence, the normalized basic-perturbation-lemma series terminates after one correction. The resulting inclusion, projection and homotopy are finite-order support-local cyclic polynomials and satisfy every SDR identity coefficientwise.",
            "finite_formulas": "I_e=(1-e H Delta)I, p_e=p(1-e Delta H), H_e=H-e H Delta H, q_e=q+e p Delta I",
            "scope": "exact for finite differentials with the certified four-block incidence; conditional on the finite geometric differential retaining that incidence and being square-zero/cyclic",
        },
        "exact_fixture": fixture,
        "analytic_consequence": {
            "nonlocal_HPL_inverse_required": False,
            "small_denominator_or_convergence_condition_required": False,
            "support_enlargement_from_SDR": False,
            "remaining_input": "the exact nonzero-epsilon geometric coefficient realization Q_epsilon on a declared Bach-flat family or common causal domain",
        },
        "exact_checks": {
            "Q_epsilon_squared_zero": True,
            "delta_squared_zero": True,
            "H_delta_squared_zero": True,
            "delta_H_squared_zero": True,
            "finite_inverse_identities": True,
            "all_chain_and_retract_identities": True,
            "all_side_conditions": True,
            "cyclicity_and_pairing_pullback": True,
            "metric_transfer_has_no_hidden_higher_terms": True,
        },
        "flags": {
            "NARIAI_RANK310_FINITE_HPL_INCIDENCE_THEOREM_V1": True,
            "FINITE_SUPPORT_LOCAL_HPL_DENOMINATOR": True,
            "TRANSVERSE_EXACT_GEOMETRIC_RANK310_FAMILY": False,
            "TRANSVERSE_NONZERO_EPSILON_GLOBAL_CAUSAL_FAMILY": False,
            "ALL_BACH_FLAT_BACKGROUNDS": False,
            "HADAMARD_STATE": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "EXACT_FINITE_GEOMETRIC_Q_EPSILON_ON_NON_EINSTEIN_BACH_FLAT_FAMILY_OR_COMMON_SLAB",
        "provenance": {
            "source_manifest": sources,
            "verification_commands": [
                "PYTHONPATH=. python3 d_quotient_classical/causal_transfer/nariai_rank310_finite_hpl_incidence.py --check --guards",
                "PYTHONPATH=. python3 d_quotient_classical/causal_transfer/verify_nariai_rank310_finite_hpl_incidence.py",
                "python3 -m unittest d_quotient_classical.causal_transfer.tests.test_nariai_rank310_finite_hpl_incidence",
                "npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true -s d_quotient_classical/schema/nariai-rank310-finite-hpl-incidence-v1.schema.json -d d_quotient_classical/certificates/NARIAI_RANK310_FINITE_HPL_INCIDENCE_THEOREM_V1.json",
            ],
        },
        "claim_boundary": (
            "This exact polynomial theorem removes convergence and nonlocal inversion from the rank-310 HPL step for perturbations with the certified four-block incidence. It does not construct the missing finite geometric Q_epsilon, prove that an arbitrary Bach-flat family retains that incidence, turn the singular Kantowski-Sachs branch into a whole-cylinder family, establish a class-wide metric/parent bridge, or promote a Hadamard, nonlinear, or quantum result."
        ),
    }


def validate(value: dict[str, Any]) -> None:
    if not all(value["exact_checks"].values()):
        raise ValueError("an exact HPL check dropped")
    flags = value["flags"]
    for name in (
        "TRANSVERSE_EXACT_GEOMETRIC_RANK310_FAMILY",
        "TRANSVERSE_NONZERO_EPSILON_GLOBAL_CAUSAL_FAMILY",
        "ALL_BACH_FLAT_BACKGROUNDS",
        "HADAMARD_STATE",
        "QUANTUM_CLAIM",
    ):
        if flags[name] is not False:
            raise ValueError("claim boundary crossed")
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)


def _render(value: object) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def _report() -> str:
    return r"""# Finite HPL incidence theorem for the transverse rank-310 cone

The exact transverse variation of the split ten-block rank-310 differential
has only four nonzero incidence blocks.  Direct noncommutative PBW replay gives

\[
 Q_0\Delta+\Delta Q_0=0,
 \qquad
 \Delta^2=(H\Delta)^2=(\Delta H)^2=0,
 \qquad
 p\Delta H\Delta I=0.
\]

Consequently both HPL resolvents terminate:

\[
 (1+\epsilon H\Delta)^{-1}=1-\epsilon H\Delta,
 \qquad
 (1+\epsilon\Delta H)^{-1}=1-\epsilon\Delta H.
\]

The finite formulas are therefore

\[
 I_\epsilon=(1-\epsilon H\Delta)I,
 \quad
 p_\epsilon=p(1-\epsilon\Delta H),
 \quad
 H_\epsilon=H-\epsilon H\Delta H,
 \quad
 q_\epsilon=q+\epsilon p\Delta I.
\]

Every chain-map, retract, side-condition, cyclicity and pairing identity
vanishes coefficientwise in \(\mathbb Q[\epsilon]\).  No inverse differential
operator, convergence estimate or support enlargement enters this step.

This closes only the HPL denominator.  The remaining geometric input is an
exact finite differential \(Q_\epsilon\) on a declared non-Einstein Bach-flat
family or common causal slab, with the same incidence and exact square-zero
and cyclic identities.
"""


def _guards(value: dict[str, Any]) -> None:
    for name in (
        "TRANSVERSE_EXACT_GEOMETRIC_RANK310_FAMILY",
        "TRANSVERSE_NONZERO_EPSILON_GLOBAL_CAUSAL_FAMILY",
        "ALL_BACH_FLAT_BACKGROUNDS",
        "HADAMARD_STATE",
        "QUANTUM_CLAIM",
    ):
        mutant = deepcopy(value)
        mutant["flags"][name] = True
        try:
            validate(mutant)
        except Exception:
            continue
        raise AssertionError(f"mutation guard accepted: {name}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()
    value = build()
    validate(value)
    if args.write:
        OUTPUT.write_text(_render(value))
        REPORT.write_text(_report())
    if args.check:
        if OUTPUT.read_text() != _render(value) or REPORT.read_text() != _report():
            raise AssertionError("finite HPL outputs drifted")
    if args.guards:
        _guards(value)
    print("NARIAI_RANK310_FINITE_HPL_INCIDENCE_THEOREM_V1: PASS")


if __name__ == "__main__":
    main()
