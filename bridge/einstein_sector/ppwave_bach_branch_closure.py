#!/usr/bin/env python3
"""Exact support-local Einstein/extra-Weyl closure on Brinkmann pp-waves."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
from itertools import product
import json
from pathlib import Path
from typing import Any

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/ppwave_bach_branch_closure.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/ppwave_bach_branch_closure.schema.json"
REPORT = ROOT / "reports/ppwave-bach-branch-closure.md"
INDEPENDENT_VERIFIER = ROOT / "bridge/einstein_sector/verify_ppwave_bach_branch_closure.py"
TEST_PATH = ROOT / "bridge/einstein_sector/tests/test_ppwave_bach_branch_closure.py"
DIMENSION = 4


class PPWaveClosureError(RuntimeError):
    """Raised when an exact pp-wave closure identity fails."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise PPWaveClosureError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _nonzero_matrix(matrix: sp.MatrixBase) -> dict[str, str]:
    return {
        f"{row}{column}": str(sp.factor(matrix[row, column]))
        for row, column in product(range(matrix.rows), range(matrix.cols))
        if sp.factor(matrix[row, column]) != 0
    }


def _geometry() -> dict[str, Any]:
    u, v, x, y = sp.symbols("u v x y", real=True)
    coordinates = (u, v, x, y)
    profile = sp.Function("H")(u, x, y)
    metric = sp.Matrix(
        [
            [profile, 1, 0, 0],
            [1, 0, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1],
        ]
    )
    inverse = sp.simplify(metric.inv())
    connection = [
        [[sp.S.Zero for _ in range(DIMENSION)] for _ in range(DIMENSION)]
        for _ in range(DIMENSION)
    ]
    for target, first, second in product(range(DIMENSION), repeat=3):
        connection[target][first][second] = sp.simplify(
            sum(
                inverse[target, index]
                * (
                    sp.diff(metric[index, second], coordinates[first])
                    + sp.diff(metric[index, first], coordinates[second])
                    - sp.diff(metric[first, second], coordinates[index])
                )
                for index in range(DIMENSION)
            )
            / 2
        )

    riemann = [
        [
            [[sp.S.Zero for _ in range(DIMENSION)] for _ in range(DIMENSION)]
            for _ in range(DIMENSION)
        ]
        for _ in range(DIMENSION)
    ]
    for target, source, first, second in product(range(DIMENSION), repeat=4):
        riemann[target][source][first][second] = sp.simplify(
            sp.diff(connection[target][source][second], coordinates[first])
            - sp.diff(connection[target][source][first], coordinates[second])
            + sum(
                connection[target][middle][first]
                * connection[middle][source][second]
                - connection[target][middle][second]
                * connection[middle][source][first]
                for middle in range(DIMENSION)
            )
        )
    ricci = sp.Matrix(
        DIMENSION,
        DIMENSION,
        lambda first, second: sp.simplify(
            sum(
                riemann[index][first][index][second]
                for index in range(DIMENSION)
            )
        ),
    )
    scalar = sp.simplify(
        sum(
            inverse[first, second] * ricci[first, second]
            for first, second in product(range(DIMENSION), repeat=2)
        )
    )
    schouten = sp.simplify((ricci - metric * scalar / 6) / 2)

    lowered_riemann = [
        [
            [[sp.S.Zero for _ in range(DIMENSION)] for _ in range(DIMENSION)]
            for _ in range(DIMENSION)
        ]
        for _ in range(DIMENSION)
    ]
    weyl = [
        [
            [[sp.S.Zero for _ in range(DIMENSION)] for _ in range(DIMENSION)]
            for _ in range(DIMENSION)
        ]
        for _ in range(DIMENSION)
    ]
    for first, second, third, fourth in product(range(DIMENSION), repeat=4):
        lowered_riemann[first][second][third][fourth] = sp.simplify(
            sum(
                metric[first, target] * riemann[target][second][third][fourth]
                for target in range(DIMENSION)
            )
        )
        weyl[first][second][third][fourth] = sp.simplify(
            lowered_riemann[first][second][third][fourth]
            - (
                metric[first, third] * schouten[fourth, second]
                - metric[first, fourth] * schouten[third, second]
                - metric[second, third] * schouten[fourth, first]
                + metric[second, fourth] * schouten[third, first]
            )
        )

    derivative_schouten = [
        [[sp.S.Zero for _ in range(DIMENSION)] for _ in range(DIMENSION)]
        for _ in range(DIMENSION)
    ]
    for derivative, first, second in product(range(DIMENSION), repeat=3):
        derivative_schouten[derivative][first][second] = sp.simplify(
            sp.diff(schouten[first, second], coordinates[derivative])
            - sum(
                connection[index][derivative][first] * schouten[index, second]
                + connection[index][derivative][second] * schouten[first, index]
                for index in range(DIMENSION)
            )
        )
    second_schouten = [
        [
            [[sp.S.Zero for _ in range(DIMENSION)] for _ in range(DIMENSION)]
            for _ in range(DIMENSION)
        ]
        for _ in range(DIMENSION)
    ]
    for outer, inner, first, second in product(range(DIMENSION), repeat=4):
        second_schouten[outer][inner][first][second] = sp.simplify(
            sp.diff(derivative_schouten[inner][first][second], coordinates[outer])
            - sum(
                connection[index][outer][inner]
                * derivative_schouten[index][first][second]
                + connection[index][outer][first]
                * derivative_schouten[inner][index][second]
                + connection[index][outer][second]
                * derivative_schouten[inner][first][index]
                for index in range(DIMENSION)
            )
        )
    schouten_up = sp.simplify(inverse * schouten * inverse)
    bach = sp.zeros(DIMENSION)
    for first, second in product(range(DIMENSION), repeat=2):
        laplacian = sum(
            inverse[outer, inner]
            * second_schouten[outer][inner][first][second]
            for outer, inner in product(range(DIMENSION), repeat=2)
        )
        mixed = sum(
            inverse[outer, inner]
            * second_schouten[outer][first][second][inner]
            for outer, inner in product(range(DIMENSION), repeat=2)
        )
        curvature = sum(
            schouten_up[inner, outer] * weyl[first][inner][second][outer]
            for inner, outer in product(range(DIMENSION), repeat=2)
        )
        bach[first, second] = sp.simplify(laplacian - mixed + curvature)
    return {
        "coordinates": coordinates,
        "profile": profile,
        "metric": metric,
        "inverse": inverse,
        "ricci": ricci,
        "scalar": scalar,
        "bach": bach,
    }


def build_certificate() -> dict[str, Any]:
    data = _geometry()
    u, _v, x, y = data["coordinates"]
    profile = data["profile"]
    ricci = data["ricci"]
    bach = data["bach"]
    transverse_laplacian = sp.diff(profile, x, 2) + sp.diff(profile, y, 2)
    transverse_bilaplacian = (
        sp.diff(profile, x, 4)
        + 2 * sp.diff(profile, x, 2, y, 2)
        + sp.diff(profile, y, 4)
    )
    expected_ricci = sp.zeros(DIMENSION)
    expected_ricci[0, 0] = -transverse_laplacian / 2
    expected_bach = sp.zeros(DIMENSION)
    expected_bach[0, 0] = -transverse_bilaplacian / 4
    _require(ricci == expected_ricci, "pp-wave Ricci tensor drifted")
    _require(data["scalar"] == 0, "pp-wave scalar curvature is not zero")
    _require(bach == expected_bach, "pp-wave Bach tensor is not the transverse bilaplacian")

    einstein_amplitude = sp.Function("f")(u)
    extra_amplitude = sp.Function("g")(u)
    einstein_profile = einstein_amplitude * (x**2 - y**2)
    extra_profile = extra_amplitude * x**3
    coefficient_e, coefficient_x = sp.symbols("a b")
    combined_profile = coefficient_e * einstein_profile + coefficient_x * extra_profile

    def delta(expression: sp.Expr) -> sp.Expr:
        return sp.factor(sp.diff(expression, x, 2) + sp.diff(expression, y, 2))

    einstein_delta = delta(einstein_profile)
    extra_delta = delta(extra_profile)
    combined_bach = sp.factor(-delta(delta(combined_profile)) / 4)
    combined_ricci = sp.factor(-delta(combined_profile) / 2)
    _require(einstein_delta == 0, "declared Einstein profile is not harmonic")
    _require(extra_delta == 6 * x * extra_amplitude, "declared extra-Weyl profile drifted")
    _require(delta(extra_delta) == 0, "declared extra-Weyl profile is not biharmonic")
    _require(combined_bach == 0, "Einstein plus extra-Weyl pp-wave does not close")
    _require(combined_ricci != 0, "extra-Weyl branch unexpectedly became Einstein")

    q2_coefficients = {
        "Einstein_Einstein": sp.diff(combined_bach, coefficient_e, 2),
        "Einstein_extraWeyl": sp.diff(combined_bach, coefficient_e, coefficient_x),
        "extraWeyl_extraWeyl": sp.diff(combined_bach, coefficient_x, 2),
    }
    _require(all(value == 0 for value in q2_coefficients.values()), "restricted q2 is nonzero")

    payload = {
        "schema": "ppwave-bach-branch-closure-v1",
        "result_id": "PPWAVE_BACH_BRANCH_CLOSURE",
        "result_state": "RESTRICTED_SUPPORT_LOCAL_EINSTEIN_EXTRA_WEYL_Q2_ZERO",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "schema_path": str(SCHEMA.relative_to(ROOT)),
            "schema_sha256": _sha256(SCHEMA),
            "independent_verifier_path": str(INDEPENDENT_VERIFIER.relative_to(ROOT)),
            "independent_verifier_sha256": _sha256(INDEPENDENT_VERIFIER),
            "test_path": str(TEST_PATH.relative_to(ROOT)),
            "test_sha256": _sha256(TEST_PATH),
            "report_path": str(REPORT.relative_to(ROOT)),
            "report_sha256": _sha256(REPORT),
        },
        "geometry": {
            "coordinates": ["u", "v", "x", "y"],
            "metric": "ds^2=2 du dv+dx^2+dy^2+H(u,x,y)du^2",
            "profile_dependence": "arbitrary smooth H(u,x,y), independent of v",
            "support_scope": "restricted support-local Brinkmann/Kerr-Schild field sector; no mode truncation",
            "inverse_metric": [[str(value) for value in row] for row in data["inverse"].tolist()],
        },
        "exact_field_equations": {
            "ricci_nonzero_components": _nonzero_matrix(ricci),
            "scalar_curvature": "0",
            "bach_nonzero_components": _nonzero_matrix(bach),
            "einstein_equation": "Delta_perp H=0",
            "bach_equation": "Delta_perp^2 H=0",
            "bach_is_exactly_linear_in_H": True,
        },
        "branch_representatives": {
            "Einstein": {
                "profile": "f(u)*(x^2-y^2)",
                "Delta_perp_H": "0",
                "Ricci_flat": True,
                "Bach_flat": True,
            },
            "extra_Weyl": {
                "profile": "g(u)*x^3",
                "Delta_perp_H": "6*x*g(u)",
                "Ricci_flat": False,
                "Bach_flat": True,
            },
            "sum_is_exact_Bach_solution": True,
        },
        "restricted_nonlinear_tensor": {
            "Taylor_convention": "q2(F,G)=d_a d_b B[Hbar+aF+bG]|a=b=0",
            "q1": "q1(H)=-Delta_perp^2 H/4 in the uu equation row",
            "q2_entries": {name: str(value) for name, value in q2_coefficients.items()},
            "q2_identically_zero_for_arbitrary_ppwave_profiles": True,
            "all_higher_Taylor_coefficients_zero": True,
            "cyclicity_on_declared_sector": "AUTOMATIC_ZERO_TENSOR",
        },
        "branch_mixing_verdict": {
            "Einstein_Einstein_to_extraWeyl": "ZERO",
            "Einstein_extraWeyl_to_Einstein": "ZERO",
            "Einstein_extraWeyl_to_extraWeyl": "ZERO",
            "extraWeyl_extraWeyl_to_Einstein": "ZERO",
            "extraWeyl_extraWeyl_to_extraWeyl": "ZERO",
            "restricted_branches_close_together": True,
        },
        "transfer_disposition": {
            "restricted_ell2": "pi_cl q2(iota_cl tensor iota_cl)=0",
            "homotopy_choice_affects_result": False,
            "reason": "q2 vanishes before projection on the declared support-local branch sector",
            "higher_brackets_on_sector": "ZERO_FROM_EXACT_LINEARITY_OF_BACH_ON_THE_SLICE",
        },
        "physical_interpretation": {
            "negative_direction_reintroduced_by_ell2": False,
            "pairing_sign_of_extra_Weyl_branch_classified": False,
            "topological_Weyl_square_direction_tested": False,
            "one_particle_statement": "NOT_ADDRESSED",
        },
        "exact_checks": {
            "metric_inverse_exact": True,
            "ricci_tensor_exact": True,
            "scalar_zero": True,
            "bach_tensor_exact": True,
            "bach_linearity_exact": True,
            "Einstein_representative_exact": True,
            "extra_Weyl_representative_exact": True,
            "mixed_exact_solution": True,
            "restricted_q2_zero": True,
            "restricted_ell2_zero": True,
        },
        "flags": {
            "RESTRICTED_SUPPORT_LOCAL_Q2_BLOCK": True,
            "ACTUAL_EINSTEIN_EXTRA_WEYL_BRANCH_LABELS": True,
            "RESTRICTED_TRANSFERRED_ELL2_COMPUTED": True,
            "FULL_SUPPORT_LOCAL_BV_Q2": False,
            "COMPLETE_54_ROW_TRANSFER": False,
            "WEYL_SQUARE_DEFORMATION_CENTRALITY_TESTED": False,
            "LORENTZIAN_CAUSAL_CERTIFIED": False,
            "QME_RESTORED": False,
        },
        "next_gate": "NONALIGNED_SUPPORT_LOCAL_BRANCH_BLOCK_OR_COMPLETE_54_ROW_Q2",
        "claim_boundary": "This exact LOCAL-ALGEBRAIC theorem proves that the Bach tensor is linear on the arbitrary-profile Brinkmann pp-wave slice, so the restricted support-local q2 and every transferred branch-mixing ell2 entry vanish for the declared Einstein and non-Einstein biharmonic representatives. It is not the complete support-local BV q2, does not classify nonaligned interactions or the Weyl-square deformation classes, and supplies no causal, scattering, pairing-positivity, or quantum theorem.",
    }
    verify_payload(payload)
    return payload


def verify_payload(payload: dict[str, Any]) -> None:
    if any(value is not True for value in payload["exact_checks"].values()):
        raise PPWaveClosureError("pp-wave exact check dropped")
    _require(
        payload["branch_representatives"]["sum_is_exact_Bach_solution"] is True,
        "pp-wave mixed branch closure dropped",
    )
    _require(
        all(
            value == "0"
            for value in payload["restricted_nonlinear_tensor"]["q2_entries"].values()
        ),
        "pp-wave restricted q2 drifted",
    )
    _require(
        payload["transfer_disposition"]["restricted_ell2"]
        == "pi_cl q2(iota_cl tensor iota_cl)=0",
        "pp-wave restricted ell2 drifted",
    )
    flags = payload["flags"]
    for name in (
        "RESTRICTED_SUPPORT_LOCAL_Q2_BLOCK",
        "ACTUAL_EINSTEIN_EXTRA_WEYL_BRANCH_LABELS",
        "RESTRICTED_TRANSFERRED_ELL2_COMPUTED",
    ):
        _require(flags[name] is True, f"pp-wave positive flag dropped: {name}")
    for name in (
        "FULL_SUPPORT_LOCAL_BV_Q2",
        "COMPLETE_54_ROW_TRANSFER",
        "WEYL_SQUARE_DEFORMATION_CENTRALITY_TESTED",
        "LORENTZIAN_CAUSAL_CERTIFIED",
        "QME_RESTORED",
    ):
        _require(flags[name] is False, f"pp-wave boundary crossed: {name}")


def _render(payload: dict[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def _guards(payload: dict[str, Any]) -> None:
    mutations = (
        ("promote full q2", ("flags", "FULL_SUPPORT_LOCAL_BV_Q2"), True),
        ("promote centrality", ("flags", "WEYL_SQUARE_DEFORMATION_CENTRALITY_TESTED"), True),
        ("erase mixed closure", ("branch_representatives", "sum_is_exact_Bach_solution"), False),
    )
    for name, path, value in mutations:
        mutant = deepcopy(payload)
        mutant[path[0]][path[1]] = value
        try:
            verify_payload(mutant)
        except PPWaveClosureError:
            continue
        raise PPWaveClosureError(f"mutation guard accepted: {name}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()
    payload = build_certificate()
    if args.write:
        OUTPUT.write_text(_render(payload), encoding="utf-8")
    if args.check and (not OUTPUT.exists() or OUTPUT.read_text(encoding="utf-8") != _render(payload)):
        raise PPWaveClosureError(f"pp-wave certificate is stale: {OUTPUT}")
    if args.guards:
        _guards(payload)
    if not args.write and not args.check and not args.guards:
        print(_render(payload), end="")
    else:
        print("PPWAVE_BACH_BRANCH_CLOSURE: RESTRICTED SUPPORT-LOCAL ELL2 ZERO")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
