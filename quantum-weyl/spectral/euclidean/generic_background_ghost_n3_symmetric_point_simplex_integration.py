#!/usr/bin/env python3
"""Integrate the exact ghost n=3 carrier projection at x1=x2=x3=1."""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import itertools
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import mpmath as mp
import sympy as sp


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUTPUT = HERE / "certificates/GENERIC_BACKGROUND_GHOST_N3_SYMMETRIC_POINT_SIMPLEX_INTEGRATION.json"
SCHEMA = HERE / "schema/generic-background-ghost-n3-symmetric-point-simplex-integration-v1.schema.json"
PROJECTION = HERE / "certificates/GENERIC_BACKGROUND_GHOST_N3_FIVE_CARRIER_PROJECTION.json"

A, B, C = sp.symbols("alpha1 alpha2 alpha0")
E2, E3 = sp.symbols("e2 e3")
U, V = sp.symbols("u v")


def _q(value: Fraction | int | sp.Rational) -> dict[str, int]:
    rational = sp.Rational(value)
    return {"numerator": int(rational.p), "denominator": int(rational.q)}


def _from_q(value: dict[str, int]) -> sp.Rational:
    return sp.Rational(value["numerator"], value["denominator"])


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _reference(path: Path) -> dict[str, str]:
    value = json.loads(path.read_text())
    return {
        "path": str(path.relative_to(ROOT)),
        "result_id": value["result_id"],
        "sha256": _sha256(path),
    }


def _poly_terms(expression: sp.Expr, variables: tuple[sp.Symbol, ...]) -> list[dict[str, Any]]:
    polynomial = sp.Poly(sp.expand(expression), *variables, domain=sp.QQ)
    return [
        {"exponents": list(exponents), "coefficient": _q(coefficient)}
        for exponents, coefficient in polynomial.terms()
        if coefficient
    ]


def _poly_from_terms(
    terms: list[dict[str, Any]], variables: tuple[sp.Symbol, ...]
) -> sp.Expr:
    return sp.expand(
        sum(
            _from_q(term["coefficient"])
            * sp.prod(variable ** exponent for variable, exponent in zip(variables, term["exponents"]))
            for term in terms
        )
    )


def _row_numerator(row: dict[str, Any]) -> sp.Expr:
    return sp.expand(
        sum(
            _from_q(term["coefficient"])
            * A ** term["alpha_exponents"][0]
            * B ** term["alpha_exponents"][1]
            for term in row["terms"]
        )
    )


def _symmetric_numerator(row: dict[str, Any]) -> sp.Expr:
    base = _row_numerator(row)
    averaged = sp.expand(
        sum(
            base.xreplace({A: permutation[0], B: permutation[1]})
            for permutation in itertools.permutations((A, B, C), 3)
        )
        / 6
    )
    symmetric, remainder, mapping = sp.symmetrize(
        averaged, [A, B, C], formal=True
    )
    if remainder != 0:
        raise ValueError("symmetric-point numerator failed invariant reduction")
    substitution = {
        mapping[0][0]: 1,
        mapping[1][0]: E2,
        mapping[2][0]: E3,
    }
    return sp.factor(symmetric.subs(substitution))


# Each row gives an exact divergence identity on the open simplex.  With
# c=1-a-b, e2=ab+bc+ca and e3=abc, define
#   X=(a*c*P(a,b)/e2^k, b*c*P(b,a)/e2^k).
# Then div X is the listed target.  The stored vertex orders make the flux of
# the punctured-corner arcs vanish; the explicit a*c and b*c factors kill the
# three open-edge normal fluxes.
MASTER_DIVERGENCES: dict[str, dict[str, Any]] = {
    "M11": {
        "powers": [1, 1],
        "denominator_power": 2,
        "P": -2
        * (
            9 * A**3 * B
            - 6 * A**3
            + 9 * A**2 * B**2
            - 14 * A**2 * B
            + 8 * A**2
            + 9 * A * B**3
            - 14 * A * B**2
            + 7 * A * B
            - 2 * A
            - 5 * B**3
            + 5 * B**2
            - 2 * B
        ),
        "target": 54 * V / U + 4 / U - 22,
        "value": (sp.Rational(11, 54), sp.Rational(-2, 27)),
        "vertex_orders": [1, 1, 0],
    },
    "M12": {
        "powers": [1, 2],
        "denominator_power": 2,
        "P": (
            -3 * A**3
            - A**2 * B
            + 4 * A**2
            - A * B**2
            + 2 * A * B
            - A
            - B**3
            + B**2
            - B
        ),
        "target": 3 * V / U**2 - 1 / U + 4,
        "value": (sp.Rational(-2, 3), sp.Rational(1, 3)),
        "vertex_orders": [1, 1, 0],
    },
    "M23": {
        "powers": [2, 3],
        "denominator_power": 3,
        "P": -B
        * (
            23 * A**4
            - 203 * A**3 * B
            + 64 * A**3
            - 249 * A**2 * B**2
            + 396 * A**2 * B
            - 137 * A**2
            - 92 * A * B**3
            + 285 * A * B**2
            - 203 * A * B
            + 50 * A
            - 46 * B**4
            + 92 * B**3
            - 56 * B**2
            + 10 * B
        ),
        "target": 54 * V**2 / U**3 - 10 / U + 46,
        "value": (sp.Rational(-23, 54), sp.Rational(5, 27)),
        "vertex_orders": [2, 2, 1],
    },
    "M34": {
        "powers": [3, 4],
        "denominator_power": 4,
        "P": B
        * (
            324 * A**5 * B**2
            - 2883 * A**5 * B
            + 648 * A**4 * B**3
            - 5507 * A**4 * B**2
            + 8754 * A**4 * B
            - 620 * A**4
            + 324 * A**3 * B**4
            - 6775 * A**3 * B**3
            + 18895 * A**3 * B**2
            - 12331 * A**3 * B
            + 1240 * A**3
            - 5021 * A**2 * B**4
            + 13973 * A**2 * B**3
            - 17582 * A**2 * B**2
            + 7204 * A**2 * B
            - 620 * A**2
            - 1740 * A * B**5
            + 5800 * A * B**4
            - 7310 * A * B**3
            + 3994 * A * B**2
            - 744 * A * B
            - 580 * B**6
            + 1740 * B**5
            - 1864 * B**4
            + 828 * B**3
            - 124 * B**2
        )
        / 2,
        "target": 486 * V**3 / U**4 - 62 / U + 290,
        "value": (sp.Rational(-145, 486), sp.Rational(31, 243)),
        "vertex_orders": [3, 3, 2],
    },
}


MOMENT_VALUES: dict[tuple[int, int], tuple[sp.Rational, sp.Rational]] = {
    (0, 0): (sp.Rational(1, 2), sp.S.Zero),
    (0, 1): (sp.S.Zero, sp.S.One),
    **{
        tuple(value["powers"]): value["value"]
        for value in MASTER_DIVERGENCES.values()
    },
}


def _linear_value(expression: sp.Expr) -> tuple[sp.Rational, sp.Rational, list[dict[str, Any]]]:
    polynomial = sp.Poly(sp.expand(expression), E2, E3, domain=sp.QQ)
    rational = sp.S.Zero
    master = sp.S.Zero
    contributions: list[dict[str, Any]] = []
    for (e2_power, e3_power), coefficient in polynomial.terms():
        if coefficient == 0:
            continue
        moment_key = (e3_power, 4 - e2_power)
        if moment_key not in MOMENT_VALUES:
            raise ValueError(f"missing symmetric-point master moment: {moment_key}")
        moment_rational, moment_master = MOMENT_VALUES[moment_key]
        rational += coefficient * moment_rational
        master += coefficient * moment_master
        contributions.append(
            {
                "moment_powers": list(moment_key),
                "coefficient": _q(coefficient),
            }
        )
    return sp.Rational(rational), sp.Rational(master), contributions


def _decimal_value(rational: sp.Rational, master_coefficient: sp.Rational) -> str:
    mp.mp.dps = 80
    clausen = mp.im(mp.polylog(2, mp.e ** (mp.j * mp.pi / 3)))
    scalar_master = 4 * clausen / mp.sqrt(3)
    value = mp.mpf(int(rational.p)) / int(rational.q)
    value += mp.mpf(int(master_coefficient.p)) / int(master_coefficient.q) * scalar_master
    return mp.nstr(value, 60)


def _master_rows() -> list[dict[str, Any]]:
    rows = []
    for moment_id, value in MASTER_DIVERGENCES.items():
        rational, master = value["value"]
        rows.append(
            {
                "moment_id": moment_id,
                "powers": value["powers"],
                "value": {
                    "rational": _q(rational),
                    "scalar_triangle_master_coefficient": _q(master),
                },
                "divergence_certificate": {
                    "denominator_power": value["denominator_power"],
                    "P_terms": _poly_terms(value["P"], (A, B)),
                    "target": sp.sstr(value["target"]),
                    "vertex_order_points": [[0, 0], [1, 0], [0, 1]],
                    "vertex_vanishing_orders": value["vertex_orders"],
                    "open_edge_normal_flux": "ZERO",
                    "punctured_corner_flux": "ZERO_BY_STORED_VANISHING_ORDERS",
                },
            }
        )
    return rows


def build() -> dict[str, Any]:
    projection = json.loads(PROJECTION.read_text())
    if not projection["claim_flags"][
        "GENERIC_GHOST_N3_REPOSITORY_FIVE_CARRIER_PROJECTION_COMPUTED"
    ]:
        raise ValueError("parametric five-carrier dependency is not certified")

    channel_rows = []
    for row in projection["projection_rows"]:
        symmetric = _symmetric_numerator(row)
        rational, master, contributions = _linear_value(symmetric)
        channel_rows.append(
            {
                "channel_id": row["channel_id"],
                "symmetric_numerator_terms": _poly_terms(symmetric, (E2, E3)),
                "moment_reduction": contributions,
                "integrated_value": {
                    "rational": _q(rational),
                    "scalar_triangle_master_coefficient": _q(master),
                    "decimal_60": _decimal_value(rational, master),
                },
            }
        )

    formula_payload = {
        "masters": _master_rows(),
        "channels": channel_rows,
    }
    formula_digest = hashlib.sha256(
        json.dumps(formula_payload, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    result = {
        "schema": "quantum-weyl-generic-background-ghost-n3-symmetric-point-simplex-integration-v1",
        "result_id": "GENERIC_BACKGROUND_GHOST_N3_SYMMETRIC_POINT_SIMPLEX_INTEGRATION",
        "result_state": "COEFFICIENT_COMPUTED",
        "lifecycle_state": "N3_GHOST_SYMMETRIC_POINT_INTEGRATED_FULL_FUNCTIONS_AND_PHYSICAL_HESSIAN_OPEN",
        "dependency_tags": ["EUCLIDEAN-SPECTRAL"],
        "classical_commit": projection["classical_commit"],
        "scope": {
            "dimension": 4,
            "signature": "Euclidean",
            "curvature_order": 3,
            "kinematic_point": {"x1": 1, "x2": 1, "x3": 1},
            "input_block": "three W=-2 Ric insertions in the flat Endo alpha=-1/2 ghost kernel",
            "output": "eleven exact integrated scalar-flat quotient coordinates at the normalized symmetric nonexceptional point",
        },
        "convention": {
            "simplex": "alpha_i>=0 and alpha0+alpha1+alpha2=1",
            "e2": "alpha0*alpha1+alpha1*alpha2+alpha2*alpha0",
            "e3": "alpha0*alpha1*alpha2",
            "denominator": "Delta=e2 at x1=x2=x3=1",
            "overall_loop_prefactor": "(4*pi)^-2 excluded",
            "W_and_Tr_log_multiplier": "-8/3 already included upstream",
        },
        "scalar_triangle_master": {
            "symbol": "J_triangle",
            "simplex_integral": "integral_simplex 1/e2",
            "closed_form": "4*Cl2(pi/3)/sqrt(3)",
            "sector_map": "multiply by 3 and set (alpha1,alpha2,alpha0)=(x,y,1)/(1+x+y) on [0,1]^2",
            "one_dimensional_integrand": "3*log(((1+x)*(1+2*x))/(x*(x+2)))/(x^2+x+1)",
            "angle_substitution": "x=(sqrt(3)*tan(phi)-1)/2, phi in [pi/6,pi/3]",
            "clausen_convention": "Cl2(theta)=sum_{n>=1} sin(n*theta)/n^2",
            "exact_reduction_certificate": {
                "sector_count": 3,
                "sector_coordinates": "(alpha1,alpha2,alpha0)=(x,y,1)/(1+x+y), x,y in [0,1]",
                "sector_jacobian": "1/(1+x+y)^3",
                "sector_integrand": "1/((1+x+y)*(x+y+x*y))",
                "y_antiderivative": "log((x+(1+x)*y)/(1+x+y))/(x^2+x+1)",
                "angle_measure_identity": "dx/(x^2+x+1)=2*dphi/sqrt(3)",
                "angle_log_ratio": "log(sin(phi+pi/6)*sin(phi)/(sin(phi-pi/6)*sin(phi+pi/3)))",
                "log_sine_intervals": [
                    {"sign": 1, "lower_pi_units": _q(sp.Rational(1, 3)), "upper_pi_units": _q(sp.Rational(1, 2))},
                    {"sign": 1, "lower_pi_units": _q(sp.Rational(1, 6)), "upper_pi_units": _q(sp.Rational(1, 3))},
                    {"sign": -1, "lower_pi_units": _q(0), "upper_pi_units": _q(sp.Rational(1, 6))},
                    {"sign": -1, "lower_pi_units": _q(sp.Rational(1, 2)), "upper_pi_units": _q(sp.Rational(2, 3))},
                ],
                "log_sine_primitive": "integral log(sin u) du=-u*log(2)-Cl2(2u)/2",
                "clausen_distribution_identities": [
                    "Cl2(2*pi/3)=2*Cl2(pi/3)/3",
                    "Cl2(4*pi/3)=-2*Cl2(pi/3)/3",
                ],
                "angle_integral": "2*Cl2(pi/3)/3",
                "final_value": "4*Cl2(pi/3)/sqrt(3)",
            },
            "decimal_60": _decimal_value(sp.S.Zero, sp.S.One),
        },
        "master_moments": formula_payload["masters"],
        "channel_rows": formula_payload["channels"],
        "orientation_identities": {
            "I24": ["I24_123=I24_213=I24_312"],
            "I25": ["I25_123=I25_213=I25_312"],
            "I28": ["I28_123=I28_132=I28_231=0"],
        },
        "formula_digest": formula_digest,
        "coefficient_disposition": {
            "ghost_n3_symmetric_point_coordinates": "COMPUTED",
            "ghost_n3_full_kinematic_functions": "NOT_COMPUTED",
            "complete_ghost_third_curvature_functions": "NOT_COMPUTED",
            "physical_fourth_order_Hessian_functions": "NOT_COMPUTED",
            "complete_repository_third_curvature_functions": "NOT_COMPUTED",
        },
        "claim_flags": {
            "GENERIC_GHOST_N3_SYMMETRIC_POINT_SIMPLEX_INTEGRATED": True,
            "GENERIC_GHOST_N3_FULL_KINEMATIC_FUNCTIONS_COMPUTED": False,
            "COMPLETE_GENERIC_GHOST_DETERMINANT_COMPUTED": False,
            "REPOSITORY_CUBIC_FORM_FACTOR_FUNCTIONS_COMPUTED": False,
            "COMPLETE_RENORMALIZED_GAMMA1_SUPPLIED": False,
            "COMPLETE_RENORMALIZED_Q1_SUPPLIED": False,
            "RESIDUAL_TRANSFER_AUTHORIZED": False,
            "LORENTZIAN_CERTIFIED": False,
        },
        "dependencies": {"five_carrier_projection": _reference(PROJECTION)},
        "next_gate": "EXTEND_EXACT_SIMPLEX_REDUCTION_TO_GENERIC_X1_X2_X3_OR_SUPPLY_GENERIC_PHYSICAL_FOURTH_ORDER_HESSIAN_KERNEL",
        "claim_boundary": (
            "This EUCLIDEAN-SPECTRAL certificate exactly integrates the already certified n=3 Endo ghost five-carrier projection only at the normalized symmetric nonexceptional point x1=x2=x3=1. Permutation averaging, four exact divergence identities with vanishing boundary flux, and the scalar triangle master give all eleven values analytically. The three I24 orientations coincide, the three I25 orientations coincide, and all symmetric-section I28 coordinates integrate to zero. The upstream W=-2 Ric and -8/3 trace-log multiplier are included; (4*pi)^-2 is excluded. This is one coefficient-bearing kinematic fixture for the n=3 ghost block, not the full five form-factor functions, the full generic ghost determinant, the physical fourth-order Hessian, complete Gamma1/Q1, a QME result, residual transfer, or a Lorentzian, Hadamard, particle, positivity, scattering, or unitarity theorem."
        ),
    }
    validate(result)
    return result


def validate(value: dict[str, Any]) -> None:
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    payload = {
        "masters": value["master_moments"],
        "channels": value["channel_rows"],
    }
    digest = hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    if digest != value["formula_digest"]:
        raise ValueError("symmetric-point simplex formula digest drifted")
    if sum(
        _from_q(row["integrated_value"]["rational"])
        for row in value["channel_rows"][7:10]
    ) != 0 or sum(
        _from_q(row["integrated_value"]["scalar_triangle_master_coefficient"])
        for row in value["channel_rows"][7:10]
    ) != 0:
        raise ValueError("integrated I28 section drifted")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rendered = json.dumps(build(), indent=2, sort_keys=True) + "\n"
    if args.emit:
        OUTPUT.write_text(rendered)
    if args.check and (not OUTPUT.exists() or OUTPUT.read_text() != rendered):
        raise SystemExit(f"stale symmetric-point simplex integration: {OUTPUT}")
    print("GENERIC GHOST N3 SYMMETRIC POINT: ELEVEN EXACT SIMPLEX INTEGRALS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
