#!/usr/bin/env python3
"""Evaluate the three new physical triangle masters in the frozen Mellin scheme."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUTPUT = HERE / "certificates/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_TRIANGLE_RENORMALIZED_MASTER_VALUES.json"
SCHEMA = HERE / "schema/generic-background-physical-hessian-triangle-renormalized-master-values-v1.schema.json"
COMPLETENESS = HERE / "certificates/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_TRIANGLE_MASTER_COMPLETENESS.json"
VOLTERRA = HERE / "certificates/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_COVARIANT_VOLTERRA_CARRIER.json"
INCIDENCE = HERE / "certificates/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_FULL_BOUNDARY_INCIDENCE.json"

T = sp.symbols("t")
X1, X2, X3 = sp.symbols("x1 x2 x3", positive=True)
Z = sp.symbols("z", positive=True)
BOXES = (X1, X2, X3)
FIELD = sp.QQ.frac_field(*BOXES)
HALVES = (
    ("left", 1 / (2 - T), sp.S.Zero, sp.Rational(1, 2)),
    ("right", 1 / (1 + T), sp.Rational(1, 2), sp.S.One),
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _reference(path: Path) -> dict[str, str]:
    value = json.loads(path.read_text())
    return {
        "path": str(path.relative_to(ROOT)),
        "result_id": value["result_id"],
        "sha256": _sha256(path),
    }


def _canonical_digest(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _definite_rational(
    expression: sp.Expr, lower: sp.Expr, upper: sp.Expr
) -> tuple[sp.Expr, list[tuple[sp.Expr, sp.Expr]]]:
    """Integrate a factored rational function without generic-field Risch GCDs."""
    rational = sp.S.Zero
    logs: list[tuple[sp.Expr, sp.Expr]] = []
    partial = sp.apart(sp.factor(expression), T)
    for term in sp.Add.make_args(partial):
        numerator, denominator = term.as_numer_denom()
        polynomial = sp.Poly(denominator, T, domain=FIELD)
        coefficient, factors = sp.factor_list(polynomial)
        if not factors:
            primitive = sp.integrate(term, T)
            rational += primitive.subs(T, upper) - primitive.subs(T, lower)
            continue
        if len(factors) != 1 or factors[0][0].degree() != 1:
            raise ValueError("angular partial fraction did not split linearly")
        linear, power = factors[0]
        slope = linear.coeff_monomial(T)
        intercept = linear.coeff_monomial(1)
        scalar = sp.cancel(numerator / coefficient.as_expr())
        if sp.degree(scalar, T) != 0:
            raise ValueError("angular partial-fraction numerator retained t")
        at_lower = sp.cancel(slope * lower + intercept)
        at_upper = sp.cancel(slope * upper + intercept)
        if power == 1:
            logs.append(
                (sp.cancel(scalar / slope), sp.cancel(at_upper / at_lower))
            )
        else:
            rational += sp.cancel(
                scalar
                / (slope * (1 - power))
                * (at_upper ** (1 - power) - at_lower ** (1 - power))
            )
    return sp.cancel(rational), logs


def _radial_rows(
    linear: sp.Expr, correction: sp.Expr, radius: sp.Expr
) -> tuple[sp.Expr, sp.Expr, sp.Expr, sp.Expr]:
    endpoint = sp.factor(linear + correction * radius)
    log_argument = sp.factor(linear * radius * Z / endpoint)
    finite_zero = -sp.cancel(
        correction
        * radius
        * (
            11 * correction**2 * radius**2
            + 27 * correction * linear * radius
            + 18 * linear**2
        )
        / (6 * linear**4 * endpoint**3)
    )
    first = sp.cancel(
        radius
        * (
            correction**2 * radius**2
            + 3 * correction * linear * radius
            + 3 * linear**2
        )
        / (3 * linear**3 * endpoint**3)
    )
    second = sp.cancel(
        radius**2
        * (correction * radius + 3 * linear)
        / (6 * linear**2 * endpoint**3)
    )
    return log_argument, finite_zero, first, second


def _kernel(
    radius: sp.Expr,
    lower: sp.Expr,
    upper: sp.Expr,
    *,
    h0: sp.Expr,
    h1: sp.Expr,
) -> dict[str, Any]:
    linear = T * X1 + (1 - T) * X2
    correction = T * (1 - T) * X3 - linear
    log_argument, finite_zero, first, second = _radial_rows(
        linear, correction, radius
    )
    rational_density = sp.factor(
        T
        * (1 - T)
        * (h0 * finite_zero + (h1 - h0) * first - h1 * second)
    )
    rational, logs = _definite_rational(rational_density, lower, upper)

    logarithmic_density = sp.factor(T * (1 - T) * h0 / linear**4)
    if logarithmic_density:
        primitive = sp.integrate(sp.apart(logarithmic_density, T), T, risch=False)
        if primitive.has(sp.log):
            raise ValueError("Mellin logarithmic-density primitive is not rational")
        remainder = sp.factor(
            primitive * sp.diff(log_argument, T) / log_argument
        )
        rem_rational, rem_logs = _definite_rational(remainder, lower, upper)
        rational = sp.cancel(rational - rem_rational)
        logs.extend((-coefficient, argument) for coefficient, argument in rem_logs)
        logs.extend(
            (
                (sp.cancel(primitive.subs(T, upper)), sp.cancel(log_argument.subs(T, upper))),
                (-sp.cancel(primitive.subs(T, lower)), sp.cancel(log_argument.subs(T, lower))),
            )
        )

    logs = [
        (sp.cancel(coefficient), sp.factor(argument))
        for coefficient, argument in logs
        if coefficient != 0 and argument != 1
    ]
    value = rational + sum(
        coefficient * sp.log(argument) for coefficient, argument in logs
    )
    return {
        "rational": rational,
        "logs": logs,
        "value": value,
        "radial_identity": {
            "log_argument": log_argument,
            "finite_zero": finite_zero,
            "first": first,
            "second": second,
        },
    }


def _substitute_kernel(kernel: dict[str, Any], substitution: dict[sp.Symbol, sp.Symbol]) -> sp.Expr:
    return kernel["value"].subs(substitution, simultaneous=True)


def _serialize_expression(expression: sp.Expr) -> str:
    return sp.sstr(expression)


def _serialize_kernel(kernel: dict[str, Any]) -> dict[str, Any]:
    return {
        "rational_part": _serialize_expression(kernel["rational"]),
        "log_terms": [
            {
                "coefficient": _serialize_expression(coefficient),
                "argument": _serialize_expression(argument),
            }
            for coefficient, argument in kernel["logs"]
        ],
        "value": _serialize_expression(kernel["value"]),
    }


def _formula_payload() -> dict[str, Any]:
    templates: dict[str, dict[str, dict[str, Any]]] = {}
    for half_id, radius, lower, upper in HALVES:
        templates[half_id] = {
            "K0": _kernel(radius, lower, upper, h0=1, h1=0),
            "Kp": _kernel(radius, lower, upper, h0=0, h1=1),
            "Kq": _kernel(radius, lower, upper, h0=0, h1=T),
        }

    sector_substitutions = {
        "alpha1_dominant": {X1: X1, X2: X2, X3: X3},
        "alpha2_dominant": {X1: X2, X2: X3, X3: X1},
        "alpha0_dominant": {X1: X3, X2: X1, X3: X2},
    }
    # For a linear numerator h, h=h0+r*(p+q*t).  These coefficient triples
    # are fixed by the declared cyclic charts:
    # A dominant: (A,C,B), B dominant: (B,A,C), C dominant: (C,B,A).
    combinations = {
        "M14_singlet": {
            "alpha1_dominant": (1, 0, 0),
            "alpha2_dominant": (1, 0, 0),
            "alpha0_dominant": (1, 0, 0),
        },
        "M15_standard_u": {
            "alpha1_dominant": (1, -2, 1),
            "alpha2_dominant": (-1, 1, 1),
            "alpha0_dominant": (0, 1, -2),
        },
        "M16_standard_v": {
            "alpha1_dominant": (0, 1, -2),
            "alpha2_dominant": (1, -2, 1),
            "alpha0_dominant": (-1, 1, 1),
        },
    }

    r = sp.symbols("r")
    alpha0, alpha1, alpha2 = sp.symbols("alpha0 alpha1 alpha2")
    chart_rows = {
        "alpha1_dominant": {alpha1: 1 - r, alpha0: r * T, alpha2: r * (1 - T)},
        "alpha2_dominant": {alpha2: 1 - r, alpha1: r * T, alpha0: r * (1 - T)},
        "alpha0_dominant": {alpha0: 1 - r, alpha2: r * T, alpha1: r * (1 - T)},
    }
    master_polynomials = {
        "M14_singlet": sp.S.One,
        "M15_standard_u": alpha1 - alpha2,
        "M16_standard_v": alpha2 - alpha0,
    }
    for master_id, sector_coefficients in combinations.items():
        for sector_id, (h0, p, q) in sector_coefficients.items():
            reconstructed = h0 + r * (p + q * T)
            expected = master_polynomials[master_id].subs(chart_rows[sector_id])
            if sp.expand(reconstructed - expected) != 0:
                raise ValueError(
                    f"master chart reconstruction drifted: {master_id} {sector_id}"
                )

    master_rows = []
    master_values: dict[str, sp.Expr] = {}
    for master_id, sector_coefficients in combinations.items():
        sector_rows = []
        total = sp.S.Zero
        for sector_id, coefficients in sector_coefficients.items():
            substitution = sector_substitutions[sector_id]
            half_rows = []
            sector_total = sp.S.Zero
            for half_id in ("left", "right"):
                kernel_rows = templates[half_id]
                value = sum(
                    coefficient
                    * _substitute_kernel(kernel_rows[kernel_id], substitution)
                    for coefficient, kernel_id in zip(coefficients, ("K0", "Kp", "Kq"))
                )
                sector_total += value
                half_rows.append(
                    {"half_id": half_id, "value": _serialize_expression(value)}
                )
            total += sector_total
            sector_rows.append(
                {
                    "sector_id": sector_id,
                    "template_coefficients": list(coefficients),
                    "half_rows": half_rows,
                }
            )
        master_values[master_id] = total
        scale_derivative = sp.expand(Z * sp.diff(total, Z))
        master_rows.append(
            {
                "master_id": master_id,
                "sector_rows": sector_rows,
                "renormalized_value": _serialize_expression(total),
                "scale_derivative": _serialize_expression(scale_derivative),
            }
        )

    template_rows = {
        half_id: {
            kernel_id: _serialize_kernel(kernel)
            for kernel_id, kernel in rows.items()
        }
        for half_id, rows in templates.items()
    }
    return {
        "template_rows": template_rows,
        "sector_substitutions": {
            key: [sp.sstr(value[X1]), sp.sstr(value[X2]), sp.sstr(value[X3])]
            for key, value in sector_substitutions.items()
        },
        "master_rows": master_rows,
        "identity_ledger": {
            "template_count": 6,
            "dominant_sector_count": 3,
            "master_count": 3,
            "master_chart_reconstruction_count": 9,
            "master_chart_reconstruction_status": "ALL_EXACT",
            "standard_pair_S3_status": "INHERITED_FROM_EXACT_CHART_CROSSWALK_AND_CERTIFIED_MASTER_CARRIERS",
            "renormalization_scheme": "COMMON_DOMINANT_SECTOR_MELLIN_MINIMAL_SUBTRACTION",
        },
    }


def build() -> dict[str, Any]:
    completeness = json.loads(COMPLETENESS.read_text())
    volterra = json.loads(VOLTERRA.read_text())
    incidence = json.loads(INCIDENCE.read_text())
    if (
        completeness["claim_flags"]["ALL_ELEVEN_PHYSICAL_ROWS_IN_SIX_MASTER_SPAN"]
        is not True
        or volterra["claim_flags"]["COMMON_MELLIN_BOUNDARY_EXTENSION_DEFINED"]
        is not True
        or incidence["claim_flags"]["GENERIC_PHYSICAL_M14_DISPOSED"] is not True
    ):
        raise ValueError("renormalized-master dependency gate is not closed")
    payload = _formula_payload()
    result = {
        "schema": "quantum-weyl-generic-background-physical-hessian-triangle-renormalized-master-values-v1",
        "result_id": "GENERIC_BACKGROUND_PHYSICAL_HESSIAN_TRIANGLE_RENORMALIZED_MASTER_VALUES",
        "result_state": "THREE_NEW_PHYSICAL_TRIANGLE_MASTER_VALUES_EVALUATED_IN_COMMON_MELLIN_SCHEME",
        "lifecycle_state": "COEFFICIENT_COMPUTED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "classical_commit": completeness["classical_commit"],
        "scope": {
            "dimension": 4,
            "signature": "Euclidean",
            "kinematics": "positive nonexceptional x1,x2,x3",
            "scale_ratio": "z=mu^2/Q^2",
            "masters": [
                "integral_MS e3/Delta^4",
                "integral_MS e3*(alpha1-alpha2)/Delta^4",
                "integral_MS e3*(alpha2-alpha0)/Delta^4",
            ],
        },
        "subtraction_convention": {
            "sector_partition": "alpha_i is dominant",
            "chart": "alpha_i=1-r, alpha_j=r*t, alpha_k=r*(1-t)",
            "left_radius": "1/(2-t) for 0<=t<=1/2",
            "right_radius": "1/(1+t) for 1/2<=t<=1",
            "regulated_radial_measure": "z^s*r^(s-1)",
            "minimal_subtraction": "remove the coefficient of 1/s and retain the finite part at s=0",
        },
        **payload,
        "formula_digest": _canonical_digest(payload),
        "dependencies": {
            "master_completeness": _reference(COMPLETENESS),
            "Volterra_carrier": _reference(VOLTERRA),
            "boundary_incidence": _reference(INCIDENCE),
        },
        "claim_flags": {
            "RENORMALIZED_M14_SINGLET_VALUE_COMPUTED": True,
            "RENORMALIZED_STANDARD_S3_PAIR_VALUES_COMPUTED": True,
            "RENORMALIZED_SIX_MASTER_VALUES_COMPUTED": True,
            "PHYSICAL_N3_TRIANGLE_MASTER_COORDINATES_COMPUTED": False,
            "PHYSICAL_N3_TRIANGLE_INTEGRATED": False,
            "REPOSITORY_CUBIC_FORM_FACTOR_FUNCTIONS_COMPUTED": False,
            "COMPLETE_RENORMALIZED_GAMMA1_SUPPLIED": False,
            "COMPLETE_RENORMALIZED_Q1_SUPPLIED": False,
            "QME_RESTORED": False,
            "RESIDUAL_TRANSFER_AUTHORIZED": False,
            "LORENTZIAN_CERTIFIED": False,
        },
        "next_gate": "COMPUTE_PHYSICAL_MASTER_COORDINATE_FUNCTIONS_AND_ASSEMBLE_FIVE_THIRD_CURVATURE_FORM_FACTORS",
        "claim_boundary": (
            "This exact LOCAL-ALGEBRAIC and EUCLIDEAN-SPECTRAL certificate evaluates the Mellin-renormalized M14 singlet and the standard-S3 master pair as explicit sector-decomposed rational and logarithmic functions in the already frozen common Volterra subtraction scheme. It does not yet compute the six-master coordinate functions of the eleven physical channels, integrate the complete physical triangle, assemble the five repository third-curvature form factors, supply Gamma1 or Q1, restore a QME, authorize residual transfer, or establish a Lorentzian, Hadamard, particle, positivity, scattering or unitarity theorem."
        ),
    }
    validate(result)
    return result


def validate(value: dict[str, Any]) -> None:
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    payload = {
        key: value[key]
        for key in (
            "template_rows",
            "sector_substitutions",
            "master_rows",
            "identity_ledger",
        )
    }
    if _canonical_digest(payload) != value["formula_digest"]:
        raise ValueError("renormalized triangle-master formula digest drifted")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    value = build()
    rendered = json.dumps(value, indent=2, sort_keys=True) + "\n"
    if args.emit:
        OUTPUT.write_text(rendered)
    if args.check and (not OUTPUT.exists() or OUTPUT.read_text() != rendered):
        raise SystemExit(f"stale renormalized triangle-master certificate: {OUTPUT}")
    print("GENERIC PHYSICAL TRIANGLE RENORMALIZED MASTER VALUES: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
