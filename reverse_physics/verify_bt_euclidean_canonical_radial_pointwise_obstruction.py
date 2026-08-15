#!/usr/bin/env python3
"""Independent verifier for the BT canonical-radial pointwise obstruction."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from fractions import Fraction

from jsonschema import Draft202012Validator


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_CERT = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_CANONICAL_RADIAL_POINTWISE_OBSTRUCTION_V1.json",
)
SCHEMA_PATH = os.path.join(
    ROOT,
    "reverse_physics/schema/"
    "reverse-physics-bt-euclidean-canonical-radial-pointwise-obstruction-v1.schema.json",
)
EXPECTED_INPUT = (
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_CANONICAL_PHASE_SCORE_CONNECTION_V1.json"
)


def frac(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def frac_vector(values: list[dict[str, int]]) -> tuple[Fraction, ...]:
    return tuple(frac(value) for value in values)


def frac_matrix(values: list[list[dict[str, int]]]) -> tuple[tuple[Fraction, ...], ...]:
    return tuple(frac_vector(row) for row in values)


def file_hash(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def independent_additive() -> dict:
    """Rebuild the C6 dot product from direct axial sums in Q(sqrt(3))."""
    n = (2, -2, 2, 0, -1, 0)
    weights = (1, 16, 1, 4, 8, 4)
    p = tuple(Fraction(weight, sum(weights)) for weight in weights)
    cosine = (
        Fraction(1), Fraction(1, 2), Fraction(-1, 2),
        Fraction(-1), Fraction(-1, 2), Fraction(1, 2),
    )
    sine = (
        Fraction(), Fraction(1, 2), Fraction(1, 2),
        Fraction(), Fraction(-1, 2), Fraction(-1, 2),
    )
    multiplicity = 216
    f = tuple(
        multiplicity * sum((Fraction(n[x]) * h[x] for x in range(6)), Fraction())
        for h in (cosine, sine)
    )
    z = tuple(
        sum((p[x] * h[x] for x in range(6)), Fraction())
        for h in (cosine, sine)
    )
    return {
        "p": p,
        "cosine": cosine,
        "sine": sine,
        "f": f,
        "z": z,
        "dot": f[0] * z[0] + 3 * f[1] * z[1],
    }


def independent_canonical() -> dict:
    """Rebuild the C4 residual, score, and connection site by site."""
    omega = (Fraction(1, 2), Fraction(1), Fraction(1, 2), Fraction(2))
    p = tuple(Fraction(value, 11) for value in (4, 2, 4, 1))
    h = (
        (Fraction(1), Fraction()),
        (Fraction(), Fraction(1)),
        (Fraction(-1), Fraction()),
        (Fraction(), Fraction(-1)),
    )
    residual = tuple(
        (omega[(x - 1) % 4] + omega[(x + 1) % 4] - 2 * omega[x]) / omega[x]
        for x in range(4)
    )
    gram = tuple(
        tuple(
            sum((p[x] * h[x][i] * h[x][j] for x in range(4)), Fraction())
            for j in range(2)
        )
        for i in range(2)
    )
    determinant = gram[0][0] * gram[1][1] - gram[0][1] * gram[1][0]
    inverse = (
        (gram[1][1] / determinant, -gram[0][1] / determinant),
        (-gram[1][0] / determinant, gram[0][0] / determinant),
    )
    y = []
    for i in range(2):
        nonlinear = sum(
            (p[x] * h[x][i] * (residual[x] ** 2 + 2 * residual[x]) for x in range(4)),
            Fraction(),
        )
        divergence = sum(
            (p[x] * (1 - p[x] / 64) * h[x][i] for x in range(4)),
            Fraction(),
        )
        y.append(-Fraction(25, 4) * nonlinear + divergence)
    connection = [Fraction(), Fraction()]
    for x in range(4):
        inv_h = tuple(
            sum((inverse[i][j] * h[x][j] for j in range(2)), Fraction())
            for i in range(2)
        )
        leverage = sum((h[x][i] * inv_h[i] for i in range(2)), Fraction())
        coefficient = p[x] ** 2 * (leverage - 1) / 64
        for i in range(2):
            connection[i] += coefficient * inv_h[i]
    score = tuple(
        sum((inverse[i][j] * y[j] for j in range(2)), Fraction()) - connection[i]
        for i in range(2)
    )
    f = (Fraction(), Fraction(-64))
    return {
        "p": p,
        "residual": residual,
        "gram": gram,
        "inverse": inverse,
        "y": tuple(y),
        "connection": tuple(connection),
        "score": score,
        "f": f,
        "dot": sum((f[i] * score[i] for i in range(2)), Fraction()),
    }


def verify(path: str) -> bool:
    checks: dict[str, bool] = {}
    try:
        with open(path, encoding="utf-8") as handle:
            cert = json.load(handle)
        with open(SCHEMA_PATH, encoding="utf-8") as handle:
            schema = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"[FAIL] load: {exc}")
        return False

    checks["strict_schema"] = not list(Draft202012Validator(schema).iter_errors(cert))
    inputs = cert["provenance"]["inputs"]
    checks["provenance_hash_current"] = (
        len(inputs) == 1
        and inputs[0]["path"] == EXPECTED_INPUT
        and inputs[0]["sha256"] == file_hash(EXPECTED_INPUT)
    )

    additive = independent_additive()
    public_additive = cert["additive_contraction_fixture"]
    checks["independent_additive_probability"] = (
        frac_vector(public_additive["reciprocal_marginal"]) == additive["p"]
        and sum(additive["p"]) == 1
        and frac_vector(public_additive["phase_cosine"]) == additive["cosine"]
        and frac_vector(public_additive["phase_sine_sqrt3_coefficients"])
        == additive["sine"]
    )
    checks["independent_additive_phase_derivative"] = (
        frac_vector(public_additive["field_phase_over_log2"])
        == additive["f"] == (Fraction(108), Fraction(108))
        and frac_vector(public_additive["constant_frame_phase_derivative"])
        == additive["z"] == (Fraction(5, 68), Fraction(5, 68))
    )
    checks["independent_additive_outward_sign"] = (
        frac(public_additive["field_dot_derivative_over_log2"])
        == additive["dot"] == Fraction(540, 17)
        and public_additive["sign"] == "F dot (X_1 F)=(540/17)*log(2)>0"
        and public_additive["disposition"]
        == "POINTWISE_PHASE_NORM_CONTRACTION_FALSE"
    )

    canonical = independent_canonical()
    public_canonical = cert["canonical_score_fixture"]
    checks["independent_canonical_residual_and_gram"] = (
        frac_vector(public_canonical["reciprocal_marginal"]) == canonical["p"]
        and frac_vector(public_canonical["residual"])
        == canonical["residual"] == (Fraction(4), Fraction(-1), Fraction(4), Fraction(-3, 2))
        and frac_matrix(public_canonical["gram"])
        == canonical["gram"]
        == ((Fraction(8, 11), Fraction()), (Fraction(), Fraction(3, 11)))
        and frac_matrix(public_canonical["gram_inverse"])
        == canonical["inverse"]
        == ((Fraction(11, 8), Fraction()), (Fraction(), Fraction(11, 3)))
    )
    checks["independent_canonical_score_components"] = (
        frac_vector(public_canonical["ward_score"])
        == canonical["y"] == (Fraction(), Fraction(6201, 7744))
        and frac_vector(public_canonical["connection"])
        == canonical["connection"] == (Fraction(), Fraction(1, 264))
        and frac_vector(public_canonical["canonical_score"])
        == canonical["score"] == (Fraction(), Fraction(563, 192))
    )
    checks["independent_canonical_negative_sign"] = (
        frac_vector(public_canonical["field_phase_over_log2"])
        == canonical["f"] == (Fraction(), Fraction(-64))
        and frac(public_canonical["field_dot_score_over_log2"])
        == canonical["dot"] == Fraction(-563, 3)
        and public_canonical["sign"] == "F dot S=-(563/3)*log(2)<0"
        and public_canonical["disposition"]
        == "POINTWISE_FIELD_SCORE_RADIAL_MONOTONICITY_FALSE"
    )

    definitions = cert["definitions"]
    boundary = cert["annealed_boundary"]
    checks["annealed_boundary_exact"] = (
        definitions["marginal_score"] == "bar_S(F)=E[S|F]=-grad_F log rho_F"
        and definitions["radial_normalization"] == "E[F dot bar_S(F)]=2"
        and boundary["surviving_object"] == "bar_S(F)=E[S|F]"
        and boundary["surviving_identity"] == "E[F dot bar_S(F)]=2"
        and boundary["status"] == "ANNEALED_COERCIVITY_OPEN"
    )
    disposition = cert["method_disposition"]
    checks["claim_boundary"] = (
        disposition["additive_pointwise_lowest_phase_contraction"] == "OBSTRUCTED"
        and disposition["field_level_pointwise_radial_score_sign"] == "OBSTRUCTED"
        and disposition["conditional_marginal_score_coercivity"] == "OPEN"
        and disposition["full_witten_form_coercivity"] == "OPEN"
        and disposition["normalized_lowest_mode_second_moment"] == "OPEN"
        and disposition["actual_interacting_h_minus_one_second_moment"] == "OPEN"
        and disposition["continuum_limit"] == "NOT_ESTABLISHED"
        and disposition["lorentzian_transfer"] == "NOT_ESTABLISHED"
    )
    checks["dependency_boundary"] = cert["dependency_tags"] == [
        "LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL", "REDUCED-MODE"
    ]
    checks["required_nonclaims"] = {
        "failure of canonical marginal-score or Witten coercivity",
        "a low-Rayleigh sequence for the full BT Witten operator",
        "boundedness or divergence of the normalized lowest-mode or interacting H^-1 moment",
    }.issubset(set(cert["does_not_establish"]))
    checks["certificate_checks_closed"] = (
        cert["checks"]["ok"]
        and cert["checks"]["passed"] == cert["checks"]["total"]
        and not cert["checks"]["failures"]
        and all(cert["checks"]["details"].values())
    )

    for name, passed in checks.items():
        print(f"[{'PASS' if passed else 'FAIL'}] {name}")
    print(f"RESULT: {'PASS' if all(checks.values()) else 'FAIL'} ({sum(checks.values())}/{len(checks)})")
    return all(checks.values())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("certificate", nargs="?", default=DEFAULT_CERT)
    args = parser.parse_args(argv)
    return 0 if verify(args.certificate) else 1


if __name__ == "__main__":
    sys.exit(main())
