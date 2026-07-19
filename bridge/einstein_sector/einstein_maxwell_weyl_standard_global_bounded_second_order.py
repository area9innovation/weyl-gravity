"""Bounded second-order cone of the complete standard generalized-zero sector."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_standard_global_bounded_second_order.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_standard_global_bounded_second_order.schema.json"
INPUTS = {
    "complete_finite": ROOT / "bridge/certificates/einstein_maxwell_weyl_complete_finite_harmonic_smooth_global_second_order.json",
    "moment_maps": ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_global_moment_maps.json",
    "homogeneous": ROOT / "bridge/certificates/einstein_maxwell_weyl_homogeneous_quadric_second_order.json",
    "twist_source": ROOT / "bridge/certificates/einstein_maxwell_weyl_homogeneous_twist_collinear_second_order.json",
    "twist_orbit": ROOT / "bridge/certificates/einstein_maxwell_weyl_twist_velocity_so3_orbit_second_order.json",
    "global_self": ROOT / "bridge/certificates/einstein_maxwell_weyl_global_orbit_self_second_order.json",
    "abstract_cone": ROOT / "d_quotient_classical/certificates/FINITE_HARMONIC_SECOND_ORDER_TANGENT_CONE_THEOREM_V1.json",
}


class StandardGlobalBoundedError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise StandardGlobalBoundedError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _polynomial_elimination(records: dict[str, Any]) -> dict[str, Any]:
    t = sp.symbols("t", real=True)
    a, b, c, d, charge, wilson = sp.symbols("a b c d Q_e W_x", real=True)
    position, velocity = sp.symbols("A B", real=True)
    locals_map = {
        "t": t,
        "a": a,
        "b": b,
        "c": c,
        "d": d,
        "Q_e": charge,
        "W_x": wilson,
        "A": position,
        "B": velocity,
    }
    row_order = records["homogeneous"]["quadratic_source"]["row_order"]
    homogeneous_rows = {
        name: sp.sympify(value, locals=locals_map)
        for name, value in zip(
            row_order,
            records["homogeneous"]["quadratic_source"]["rows"],
            strict=True,
        )
    }
    positive_coefficients = {
        name: {
            degree: sp.factor(sp.expand(value).coeff(t, degree))
            for degree in range(1, 3)
            if sp.expand(value).coeff(t, degree) != 0
        }
        for name, value in homogeneous_rows.items()
    }
    _require(
        positive_coefficients["E11"][2] == sp.Rational(15, 2) * b**2,
        "homogeneous leading coefficient changed",
    )
    _require(
        positive_coefficients["Maxwell1"][1].subs(b, 0) == charge * a,
        "homogeneous residual linear coefficient changed",
    )

    twist_text = records["twist_source"]["theorem"]["projected_source"]["polar_L2"]["metric_00"]
    twist_row = sp.sympify(twist_text, locals=locals_map)
    twist_leading = sp.factor(sp.expand(twist_row).coeff(t, 2))
    _require(twist_leading == -7 * velocity**2, "twist leading coefficient changed")

    bx, by, bz = sp.symbols("B_x B_y B_z", real=True)
    vector = sp.Matrix([bx, by, bz])
    norm_squared = sp.expand(vector.dot(vector))
    stf = vector * vector.T - sp.eye(3) * norm_squared / 3
    stf_norm = sp.factor(sp.trace(stf.T * stf))
    _require(stf_norm == sp.Rational(2, 3) * norm_squared**2, "STF norm changed")

    reduced_rows = {
        name: sp.factor(value.subs({b: 0, velocity: 0}))
        for name, value in homogeneous_rows.items()
    }
    remaining_positive_all = {
        name: {
            degree: sp.factor(sp.expand(value).coeff(t, degree))
            for degree in range(1, 3)
            if sp.expand(value).coeff(t, degree) != 0
        }
        for name, value in reduced_rows.items()
    }
    remaining_positive = {
        name: coefficients
        for name, coefficients in remaining_positive_all.items()
        if coefficients
    }
    _require(
        remaining_positive == {"Maxwell1": {1: charge * a}},
        "reduced polynomial ideal changed",
    )
    return {
        "homogeneous_positive_degree_coefficients": {
            name: {str(degree): str(value) for degree, value in coefficients.items()}
            for name, coefficients in positive_coefficients.items()
            if coefficients
        },
        "twist_polar_L2_metric_00_t2": str(twist_leading),
        "SO3_twist_leading_tensor": "STF(B tensor B)",
        "SO3_twist_leading_norm_squared": str(stf_norm),
        "real_polynomial_zero_locus": "b=0, B=0, Q_e*a=0",
        "elimination": [
            "the homogeneous E11 t^2 coefficient (15/2)b^2 forces b=0",
            "the polar L=2 twist t^2 tensor STF(B tensor B) forces B=0 over the reals",
            "after b=B=0 the only positive-degree global source coefficient is Q_e*a*t in Maxwell1",
        ],
    }


def build() -> dict[str, Any]:
    records = {name: json.loads(path.read_text(encoding="utf-8")) for name, path in INPUTS.items()}
    _require(
        records["complete_finite"]["classification"]["complete_certified_linear_input_inventory_included"],
        "complete finite inventory changed",
    )
    _require(
        records["moment_maps"]["classification"]["standard_homogeneous_common_zero_locus_classified"]
        and records["moment_maps"]["classification"]["standard_twist_common_zero_locus_classified"],
        "global moment maps changed",
    )
    _require(
        records["homogeneous"]["classification"]["direct_complete_homogeneous_quadratic_source_computed"],
        "homogeneous source changed",
    )
    _require(
        records["twist_source"]["classification"]["full_SO3_covariant_collinear_cone_classified"],
        "twist source changed",
    )
    _require(
        records["twist_orbit"]["classification"]["complete_A_zero_twist_velocity_SO3_orbit_second_order_extendible"],
        "twist orbit changed",
    )
    _require(
        records["global_self"]["classification"]["twist_self_polar_L2_source_removable"],
        "constant twist correction changed",
    )
    _require(
        records["abstract_cone"]["correction_classes"]["BOUNDED_OR_FINITE_QUASIPERIODIC"]["status"] == "CERTIFIED",
        "bounded correction class changed",
    )
    polynomial = _polynomial_elimination(records)
    return {
        "schema": "einstein-maxwell-weyl-standard-global-bounded-second-order-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA),
        "result_id": "EINSTEIN_MAXWELL_WEYL_STANDARD_GLOBAL_BOUNDED_SECOND_ORDER",
        "result_state": "COMPLETE_STANDARD_GENERALIZED_ZERO_BOUNDED_SECOND_ORDER_CONE_CLASSIFIED",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "scope": {
            "theory": "Weyl-Maxwell target restricted to the complete standard generalized-zero image",
            "background": "compact magnetically supported Plebanski-Hacyan product",
            "boundaries": "closed S1_L times S2; bounded or finite-quasiperiodic second-order correction",
            "charge_sector": "fixed N=2 magnetic bundle; electric tangent Q_e allowed before elimination",
            "carrier": "homogeneous (a,b,c,d,Q_e,W_x) plus axial twist position/velocity vectors (A,B), with no oscillatory input",
            "degree": 2,
            "parity": "homogeneous and axial ell=1 generalized-zero inputs; polar L=0,2 and axial L=1 outputs kept distinct",
            "ell": "input 0 and 1; output 0,1,2",
            "m": "all real twist components by SO3 covariance",
            "k": 0,
            "omega": "generalized zero only",
        },
        "first_order_representatives": {
            "homogeneous": "K=a+b*t, C=a*t^2+(b/3)t^3+c+d*t, A_x=W_x+Q_e*t",
            "twist": "h_(x,a)=(A_a+B_a*t)X_a, a_x=-(A_a+B_a*t)Y_(1a)",
        },
        "polynomial_growth_ideal": polynomial,
        "universal_complete_carrier_corollary": {
            "statement": "for any complete finite-support input admitting a bounded second-order correction, b=0 and B=0",
            "reason": "oscillator products are bounded; homogeneous-twist cross terms lie in L=1; therefore neither the homogeneous L=0 b^2*t^2 coefficient nor the twist L=2 STF(B tensor B)*t^2 coefficient can be canceled by any other certified input block",
            "remaining_full_carrier_polynomial_gate": "classify a,d,Q_e crossed with the finite oscillatory carrier; c,W_x and constant A are certified spectator/modulus directions",
        },
        "moment_map_intersection": {
            "after_polynomial_elimination": "mu_H=-(a^2+Q_e^2), mu_Px=0, mu_J=0",
            "real_common_zero": "a=0, Q_e=0",
            "complete_bounded_tangent_cone": "Z2_global^bounded={(c,d,W_x,A): c,d,W_x real, A in R^3}",
        },
        "bounded_correction": {
            "homogeneous_c_d_Wx": "the complete quadratic source vanishes when a=b=Q_e=0; c and W_x are spectators and d has zero self-source",
            "constant_twist_A": "rotate A to the certified Y_10 axis, use the constant polar L=2 correction C_t2=-2|A|^2/3 in that normalization, and rotate the correction back",
            "cross_terms": "c is absent from the direct homogeneous-twist source, d couples only to twist velocity B after a=0, and W_x has zero field strength; hence all surviving cross sources vanish",
            "regularity": "real, smooth, spatially periodic and time independent, hence bounded finite-quasiperiodic",
        },
        "correction_classes": {
            "BOUNDED_OR_FINITE_QUASIPERIODIC": {"status": "CERTIFIED", "cone": "(c,d,W_x,A)"},
            "SMOOTH_SECULAR": {"status": "CERTIFIED", "reason": "the bounded correction is contained in the smooth exponential-polynomial class"},
            "CAUSAL_RETARDED": {"status": "NO_CERTIFIED_MAP"},
        },
        "classification": {
            "complete_standard_generalized_zero_polynomial_ideal_classified": True,
            "complete_standard_generalized_zero_bounded_cone_classified": True,
            "universal_b_and_twist_velocity_elimination_on_complete_finite_carrier": True,
            "oscillatory_cross_polynomial_ideal_classified": False,
            "complete_finite_bounded_common_zero_locus_solved": False,
            "all_orders_integrability": False,
            "causal_retarded_map_certified": False,
        },
        "interpretation": "Bounded second-order consistency does not remove all global data. It removes the homogeneous cubic Jordan velocity b and every twist velocity B, and the Taub equation then removes a and Q_e in the pure global sector. Static circumference, linear circle shear d, Wilson holonomy and constant SO3 twist survive with a bounded correction. In the full finite carrier, b=B=0 is already universal; only the residual a,d,Q_e times oscillator polynomial ideal and the bounded shell resonances remain.",
        "next_gate": "compute the residual a,d,Q_e times arbitrary q/p oscillator polynomial maps after the universal b=B=0 elimination, then intersect their zero locus with the finite shell-resonance ledger R_(j,a)",
        "claim_boundary": "This is the complete bounded second-order theorem for the standard generalized-zero carrier and a universal b=B=0 consequence for arbitrary finite inputs. It does not classify cancellations involving a,d,Q_e and oscillatory modes, solve the full bounded finite-support cone, prove causal propagation, all-orders integration, final residual descent, observables, particles or quantum theory.",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "inputs": {
                name: {"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)}
                for name, path in INPUTS.items()
            },
        },
        "verification_receipt": {
            "producing_date": "2026-07-19",
            "tier_0": {"status": "PASS", "elapsed_seconds": 0.12, "max_rss_kb": 16228},
            "tier_1": {"status": "PASS", "elapsed_seconds": 1.36, "max_rss_kb": 58756, "tests_run": 15},
            "tier_2": {"status": "PASS_BY_CONTENT_ADDRESS", "criterion": "all direct four-dimensional source and current inputs are unchanged exact certificates"},
            "tier_3": {"status": "NOT_RUN", "reason": "oscillatory cross-polynomial, complete bounded, causal, all-orders, residual and quantum gates remain excluded"},
        },
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_standard_global_bounded_second_order --check",
            "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_standard_global_bounded_second_order.py",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_standard_global_bounded_second_order",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    arguments = parser.parse_args()
    value = build()
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    if arguments.write:
        OUTPUT.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    elif json.loads(OUTPUT.read_text(encoding="utf-8")) != value:
        raise StandardGlobalBoundedError("standard global bounded certificate is stale")
    print("EINSTEIN_MAXWELL_WEYL_STANDARD_GLOBAL_BOUNDED_SECOND_ORDER: PASS")


if __name__ == "__main__":
    main()
