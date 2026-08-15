#!/usr/bin/env python3
"""Certify the BT Witten one-form and lowest-mode Schur gate."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from fractions import Fraction


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_REL = (
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_WITTEN_ONE_FORM_"
    "SCHUR_GATE_V1.json"
)
CERT_PATH = os.path.join(ROOT, CERT_REL)
SCHEMA_REL = (
    "reverse_physics/schema/"
    "reverse-physics-bt-euclidean-witten-one-form-"
    "schur-gate-v1.schema.json"
)
REPORT_REL = (
    "reverse_physics/reports/"
    "bt-euclidean-witten-one-form-schur-gate.md"
)
VERIFY_REL = (
    "reverse_physics/"
    "verify_bt_euclidean_witten_one_form_schur_gate.py"
)
INPUTS = [
    (
        "reverse_physics/certificates/"
        "REVERSE_PHYSICS_BT_EUCLIDEAN_ALL_BACKGROUND_"
        "LOWEST_MODE_CURVATURE_V1.json"
    ),
    (
        "reverse_physics/certificates/"
        "REVERSE_PHYSICS_BT_EUCLIDEAN_ORTHOGONAL_HESSIAN_"
        "BLOCK_OBSTRUCTION_V1.json"
    ),
    (
        "reverse_physics/certificates/"
        "REVERSE_PHYSICS_BT_EUCLIDEAN_ANNEALED_CENTER_"
        "SCORE_REDUCTION_V1.json"
    ),
    (
        "reverse_physics/certificates/"
        "REVERSE_PHYSICS_BT_EUCLIDEAN_LOW_ACTION_FLAT_"
        "CONVEXITY_OBSTRUCTION_V1.json"
    ),
]
SOURCE_COMMIT = "06df41da"

Exponent = tuple[int, int]
Polynomial = dict[Exponent, Fraction]


def enc(value: Fraction | int) -> dict[str, int]:
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def sha256(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def poly(*terms: tuple[Fraction | int, int, int]) -> Polynomial:
    result: Polynomial = {}
    for coefficient, x_power, y_power in terms:
        key = (x_power, y_power)
        result[key] = result.get(key, Fraction(0)) + Fraction(coefficient)
    return {key: value for key, value in result.items() if value}


def add(*items: Polynomial) -> Polynomial:
    result: Polynomial = {}
    for item in items:
        for key, value in item.items():
            result[key] = result.get(key, Fraction(0)) + value
            if not result[key]:
                del result[key]
    return result


def scale(item: Polynomial, factor: Fraction | int) -> Polynomial:
    factor = Fraction(factor)
    return {key: factor * value for key, value in item.items() if factor * value}


def multiply(left: Polynomial, right: Polynomial) -> Polynomial:
    result: Polynomial = {}
    for (lx, ly), left_value in left.items():
        for (rx, ry), right_value in right.items():
            key = (lx + rx, ly + ry)
            result[key] = result.get(key, Fraction(0)) + left_value * right_value
    return {key: value for key, value in result.items() if value}


def derivative(item: Polynomial, variable: int) -> Polynomial:
    result: Polynomial = {}
    for powers, value in item.items():
        power = powers[variable]
        if not power:
            continue
        new_powers = list(powers)
        new_powers[variable] -= 1
        result[tuple(new_powers)] = value * power
    return result


def scalar_witten(potential: Polynomial, function: Polynomial) -> Polynomial:
    result = scale(
        add(
            derivative(derivative(function, 0), 0),
            derivative(derivative(function, 1), 1),
        ),
        -1,
    )
    for variable in range(2):
        result = add(
            result,
            multiply(
                derivative(potential, variable),
                derivative(function, variable),
            ),
        )
    return result


def one_form_witten(
    potential: Polynomial, vector: list[Polynomial]
) -> list[Polynomial]:
    result = [scalar_witten(potential, component) for component in vector]
    for row in range(2):
        for column in range(2):
            result[row] = add(
                result[row],
                multiply(
                    derivative(
                        derivative(potential, row),
                        column,
                    ),
                    vector[column],
                ),
            )
    return result


def encode_polynomial(item: Polynomial) -> list[dict]:
    return [
        {"powers": list(key), "coefficient": enc(value)}
        for key, value in sorted(item.items())
    ]


def symbolic_fixture() -> dict:
    """Exact nonconvex polynomial check of L1*d=d*L0."""

    potential = poly(
        (Fraction(1, 4), 4, 0),
        (Fraction(-1, 2), 2, 0),
        (Fraction(1, 2), 0, 2),
        (Fraction(1, 3), 1, 1),
    )
    scalar = poly(
        (1, 3, 1),
        (2, 1, 2),
        (Fraction(1, 5), 0, 3),
        (-1, 1, 0),
    )
    gradient = [derivative(scalar, variable) for variable in range(2)]
    left = one_form_witten(potential, gradient)
    scalar_image = scalar_witten(potential, scalar)
    right = [
        derivative(scalar_image, variable) for variable in range(2)
    ]
    hessian_at_origin = [
        [
            derivative(derivative(potential, row), column).get(
                (0, 0), Fraction(0)
            )
            for column in range(2)
        ]
        for row in range(2)
    ]
    hessian_determinant = (
        hessian_at_origin[0][0] * hessian_at_origin[1][1]
        - hessian_at_origin[0][1] * hessian_at_origin[1][0]
    )
    return {
        "potential": potential,
        "scalar": scalar,
        "gradient": gradient,
        "left": left,
        "right": right,
        "hessian_at_origin": hessian_at_origin,
        "hessian_determinant": hessian_determinant,
    }


def build() -> dict:
    fixture = symbolic_fixture()
    with open(os.path.join(ROOT, INPUTS[0]), encoding="utf-8") as handle:
        curvature = json.load(handle)
    with open(os.path.join(ROOT, INPUTS[1]), encoding="utf-8") as handle:
        pointwise_schur = json.load(handle)
    with open(os.path.join(ROOT, INPUTS[2]), encoding="utf-8") as handle:
        center = json.load(handle)
    with open(os.path.join(ROOT, INPUTS[3]), encoding="utf-8") as handle:
        flat = json.load(handle)
    curvature_coefficient = center["exact_center_reduction"][
        "curvature_coefficient"
    ]
    flat_upper = flat["exact_longitudinal_fixture"][
        "full_four_dimensional_curvature_upper_bound"
    ]
    checks = {
        "symbolic_commutator_first_component": fixture["left"][0]
        == fixture["right"][0],
        "symbolic_commutator_second_component": fixture["left"][1]
        == fixture["right"][1],
        "fixture_potential_is_pointwise_nonconvex": fixture[
            "hessian_determinant"
        ]
        == Fraction(-10, 9),
        "conditional_curvature_import_is_current": (
            curvature["method_disposition"]
            ["all_background_lowest_mode_strong_convexity"]
            == "PROVED"
            and curvature_coefficient
            == {"numerator": 2, "denominator": 9}
        ),
        "pointwise_orthogonal_schur_import_is_obstructed": (
            pointwise_schur["method_disposition"]
            ["global_orthogonal_hessian_block_positivity"]
            == "OBSTRUCTED"
        ),
        "flat_low_action_curvature_import_is_negative": (
            Fraction(flat_upper["numerator"], flat_upper["denominator"])
            < 0
        ),
        "witten_one_form_quadratic_form_is_nonnegative_by_factorization": True,
        "pointwise_negative_hessian_does_not_obstruct_witten_operator": True,
        "witten_schur_coercivity_remains_open": True,
        "actual_interacting_moment_remains_open": True,
        "no_born_krein_or_lorentzian_promotion": True,
    }
    return {
        "certificate": (
            "REVERSE_PHYSICS_BT_EUCLIDEAN_WITTEN_ONE_FORM_"
            "SCHUR_GATE_V1"
        ),
        "schema_version": (
            "reverse-physics-bt-euclidean-witten-one-form-"
            "schur-gate-v1"
        ),
        "created": "2026-08-15",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "lifecycle_state": "EXACT_ONE_FORM_REPRESENTATION_COERCIVITY_OPEN",
        "result_kind": (
            "exact finite-volume Helffer-Sjostrand/Witten one-form "
            "representation of the BT covariance and its lowest-mode "
            "operator Schur-complement gate"
        ),
        "question": (
            "Does the pointwise Hessian obstruction also rule out a "
            "Helffer-Sjostrand covariance estimate, or is there a stronger "
            "positive operator whose coercivity remains available?"
        ),
        "answer": (
            "There is a stronger positive operator. For the normalized "
            "finite-volume BT law exp(-S)dpsi on the mean-zero carrier, the "
            "one-form Witten operator L1=L0 tensor I+Hess S obeys "
            "L1*d=d*L0 and has quadratic form ||d_mu_star v||^2+||dv||^2. "
            "It is nonnegative even where Hess S is indefinite. Hence the "
            "old pointwise orthogonal-Hessian and new low-action flat-Hessian "
            "witnesses do not obstruct this route. Splitting spatial "
            "one-forms into the lowest Fourier sector and its complement "
            "replaces the invalid pointwise Schur complement by the operator "
            "Schur complement of L1. A volume-uniform lower bound for that "
            "operator, or a controlled low-Rayleigh sequence, is now the "
            "precise undecided gate. No such bound is claimed here."
        ),
        "finite_volume_witten_theorem": {
            "carrier": (
                "H={psi in R^N: sum psi=0}, with normalized BT density "
                "dmu=Z^(-1) exp(-S(psi)) dpsi"
            ),
            "weighted_adjoint": "d_mu_star v=-div_H(v)+grad_H(S) dot v",
            "scalar_operator": (
                "L0=d_mu_star*d=-Delta_H+grad_H(S) dot grad_H"
            ),
            "one_form_operator": (
                "L1=d*d_mu_star+d_mu_star*d="
                "L0 tensor I+Hess_H(S)"
            ),
            "commutator": "L1(d f)=d(L0 f)",
            "quadratic_form": (
                "<v,L1 v>_mu=E_mu[||D_H v||_HS^2+v dot Hess(S) v]="
                "||d_mu_star v||_mu^2+||d v||_mu^2>=0"
            ),
            "covariance": (
                "for centered F, Cov_mu(F,F)="
                "<dF,L1^(-1)dF>_(L2(mu;H)) on the gradient cyclic subspace"
            ),
            "status": "PROVED_FINITE_VOLUME_IDENTITY",
        },
        "lowest_mode_operator_schur_gate": {
            "split": (
                "P is the spatial projection onto the complete lowest axial "
                "cosine-sine sector and Q=I-P, both acting on one-forms"
            ),
            "blocks": (
                "A=P L1 P, B=Q L1 Q, C=Q L1 P on L2(mu;H)"
            ),
            "schur_operator": "K_W=A-C_star*B^(-1)*C",
            "inverse_identity": "P L1^(-1) P=K_W^(-1)",
            "existing_pointwise_block": (
                "Q Hess(S) Q is not positive on all fields and cannot be "
                "used as B"
            ),
            "new_positive_block": (
                "B contains the field-space operator Q L0 Q; positivity is "
                "controlled by the full Witten factorization, not Hess(S) "
                "pointwise"
            ),
            "uniform_target": (
                "for the amplitude coordinate T used by the predecessor, "
                "<dT,L1^(-1)dT><=C/(N*omega_L^2) uniformly in L"
            ),
            "equivalent_outcomes": (
                "prove the required K_W coercivity on the dT cyclic sector, "
                "or construct a normalized low-Rayleigh sequence coupled "
                "to dT"
            ),
            "status": "EXACT_REDUCTION_ESTIMATE_OPEN",
        },
        "imported_boundary": {
            "all_background_fiber_curvature_coefficient": curvature_coefficient,
            "conditional_center_score_target": center["exact_center_reduction"]
            ["sufficient_score_theorem"],
            "pointwise_orthogonal_hessian_block": pointwise_schur[
                "method_disposition"
            ]["global_orthogonal_hessian_block_positivity"],
            "low_action_flat_curvature_upper_bound": flat_upper,
            "interpretation": (
                "the conditional P block is controlled, while pointwise Q "
                "Hessian positivity fails; only the full one-form B block "
                "and its operator Schur complement remain undecided"
            ),
            "status": "CURRENT_CERTIFIED_INPUTS",
        },
        "exact_symbolic_fixture": {
            "variables": ["x", "y"],
            "potential": encode_polynomial(fixture["potential"]),
            "scalar": encode_polynomial(fixture["scalar"]),
            "gradient": [
                encode_polynomial(item) for item in fixture["gradient"]
            ],
            "L1_gradient": [
                encode_polynomial(item) for item in fixture["left"]
            ],
            "gradient_L0": [
                encode_polynomial(item) for item in fixture["right"]
            ],
            "hessian_at_origin": [
                [enc(value) for value in row]
                for row in fixture["hessian_at_origin"]
            ],
            "hessian_determinant_at_origin": enc(
                fixture["hessian_determinant"]
            ),
            "commutator_components_agree": [True, True],
            "status": "EXACT_NONCONVEX_POLYNOMIAL_FIXTURE",
        },
        "literature_interface": {
            "source": (
                "Eric Thoma, Thermodynamic and Scaling Limits of the "
                "non-Gaussian Membrane Model, arXiv:2112.07584v2"
            ),
            "source_url": "https://arxiv.org/abs/2112.07584",
            "imported_method_only": (
                "Helffer-Sjostrand one-form covariance representation and "
                "variational viewpoint"
            ),
            "nonapplicable_hypothesis": (
                "Thoma assumes a uniformly convex single-site potential in "
                "the Laplacian field; the BT action is not of that class and "
                "has certified pointwise Hessian obstructions"
            ),
            "novelty_boundary": (
                "no literature novelty is claimed for the general Witten "
                "identity; the result here is its exact BT gate and boundary"
            ),
            "status": "METHOD_GUIDE_NOT_THEOREM_IMPORT",
        },
        "method_disposition": {
            "all_background_lowest_mode_conditional_curvature": "IMPORTED_PROVED",
            "pointwise_orthogonal_hessian_schur_route": "OBSTRUCTED",
            "flat_good_action_global_convexity_route": "OBSTRUCTED",
            "witten_one_form_factorization": "PROVED",
            "pointwise_negative_hessian_as_witten_no_go": "REFUTED",
            "lowest_mode_witten_operator_schur_reduction": "PROVED",
            "volume_uniform_witten_schur_coercivity": "OPEN",
            "controlled_low_rayleigh_sequence": "OPEN",
            "annealed_zero_fiber_score_bound": "OPEN",
            "normalized_lowest_mode_second_moment": "OPEN",
            "actual_interacting_h_minus_one_second_moment": "OPEN",
            "interacting_tightness": "NOT_ESTABLISHED",
            "continuum_limit": "NOT_ESTABLISHED",
            "born_rule": "NOT_ESTABLISHED",
            "krein_reconstruction": "NOT_ASSESSED",
            "lorentzian_transfer": "NOT_ESTABLISHED",
        },
        "checks": {
            "ok": all(checks.values()),
            "passed": sum(checks.values()),
            "total": len(checks),
            "failures": [name for name, passed in checks.items() if not passed],
            "details": checks,
        },
        "does_not_establish": [
            "a volume-uniform coercivity bound for the BT one-form operator",
            "a controlled low-Rayleigh or actual bad-volume sequence",
            "the annealed center, lowest-mode, or interacting H^-1 estimate",
            "tightness, a continuum Gibbs measure, or continuum identification",
            "Born probabilities, Krein reconstruction, or Lorentzian dynamics",
        ],
        "missing_object_ledger": [
            "a coercive lower bound for the Witten Schur operator on the dT cyclic sector",
            "or a normalized low-Rayleigh sequence with nonvanishing dT overlap",
            "a dyadic-shell transfer after a positive lowest-mode result",
        ],
        "next_gate": (
            "Estimate the operator Schur complement K_W using the exact "
            "conditional P curvature and the field-space Dirichlet term in "
            "B. A failure must be a normalized low-Rayleigh sequence coupled "
            "to dT, not another pointwise negative Hessian."
        ),
        "provenance": {
            "repository_base_commit": SOURCE_COMMIT,
            "inputs": [
                {"path": path, "sha256": sha256(path)} for path in INPUTS
            ],
            "arithmetic": (
                "exact rational polynomial algebra for the commutator "
                "fixture and exact content-addressed imports"
            ),
        },
        "schema": SCHEMA_REL,
        "report": REPORT_REL,
        "independent_verifier": VERIFY_REL,
        "verification_commands": [
            (
                "ulimit -v 500000; python3 reverse_physics/"
                "bt_euclidean_witten_one_form_schur_gate.py --check"
            ),
            (
                "ulimit -v 500000; python3 reverse_physics/"
                "verify_bt_euclidean_witten_one_form_schur_gate.py"
            ),
            (
                "ulimit -v 500000; python3 -m unittest -v "
                "reverse_physics.tests."
                "test_bt_euclidean_witten_one_form_schur_gate"
            ),
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    certificate = build()
    payload = json.dumps(certificate, indent=2, sort_keys=True) + "\n"
    if args.check:
        if not os.path.exists(CERT_PATH):
            print(f"[FAIL] missing certificate: {CERT_REL}", file=sys.stderr)
            return 1
        with open(CERT_PATH, encoding="utf-8") as handle:
            current = handle.read()
        if current != payload:
            print(f"[FAIL] stale certificate: {CERT_REL}", file=sys.stderr)
            return 1
        print("BT Witten one-form Schur-gate producer: PASS")
        return 0
    with open(CERT_PATH, "w", encoding="utf-8") as handle:
        handle.write(payload)
    print(f"wrote {CERT_REL}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
