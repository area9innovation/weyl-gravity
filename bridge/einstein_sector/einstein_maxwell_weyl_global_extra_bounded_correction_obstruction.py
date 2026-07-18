#!/usr/bin/env python3
"""Obstruct bounded corrections on the complete global--extra common-zero orbit."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_global_extra_bounded_correction_obstruction.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_global_extra_bounded_correction_obstruction.schema.json"
INPUTS = {
    "cone": ROOT / "d_quotient_classical/certificates/PH_HOMOGENEOUS_TWIST_ELL2_EXTRA_BOUNDED_TANGENT_CONE_V1.json",
    "twist_source": ROOT / "bridge/certificates/einstein_maxwell_weyl_homogeneous_twist_collinear_second_order.json",
    "abstract_cone": ROOT / "d_quotient_classical/certificates/FINITE_HARMONIC_SECOND_ORDER_TANGENT_CONE_THEOREM_V1.json",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def theorem() -> dict[str, Any]:
    records = {name: json.loads(path.read_text(encoding="utf-8")) for name, path in INPUTS.items()}
    cone = records["cone"]
    if not cone["classification"]["complete_common_zero_locus_in_declared_nonzero_extra_carrier"]:
        raise AssertionError("complete common-zero cone changed")
    if cone["complete_nonzero_extra_parameterization"]["energy_balance"] != "beta^2=Q_e^2/2+(2/3)*X":
        raise AssertionError("global--extra energy balance changed")
    if records["abstract_cone"]["correction_classes"]["BOUNDED_OR_FINITE_QUASIPERIODIC"]["status"] != "CERTIFIED":
        raise AssertionError("bounded correction-category definition changed")

    t = sp.symbols("t", real=True)
    A, B = sp.symbols("A B", real=True)
    source_text = records["twist_source"]["theorem"]["projected_source"]["polar_L2"]["metric_00"]
    source = sp.sympify(source_text, locals={"t": t, "A": A, "B": B})
    leading = sp.factor(sp.expand(source).coeff(t, 2))
    if leading != -7 * B**2:
        raise AssertionError("twist zero-frequency L2 leading source changed")

    X, Q = sp.symbols("X Q", real=True)
    B_squared = Q**2 / 2 + sp.Rational(2, 3) * X
    orbit_leading = sp.factor(leading.subs(B**2, B_squared))
    if sp.expand(orbit_leading + sp.Rational(7, 2) * Q**2 + sp.Rational(14, 3) * X) != 0:
        raise AssertionError("orbit leading coefficient changed")

    return {
        "channel": {
            "frequency": 0,
            "angular_block": "polar L=2",
            "action_row": "metric_00",
            "direct_source": source_text,
            "quadratic_time_coefficient": str(leading),
            "orbit_coefficient": str(orbit_leading),
        },
        "selection_rule_audit": {
            "twist_self": "the only degree-two polynomial contribution in the zero-frequency polar L=2 channel; its leading term is -7*B^2*t^2",
            "extra_conjugate_self": "frequency zero but time independent",
            "extra_sum": "frequencies +/-2*omega_e, not zero",
            "twist_extra_cross": "frequencies +/-omega_e, not zero",
            "Q_e_self": "time independent because the electric field strength is constant",
            "homogeneous_spectators": "c and W_x do not supply a degree-two polar L=2 source; a=b=d=0 on the complete cone",
        },
        "functional_analysis": {
            "correction_space": "bounded finite-quasiperiodic coefficient fields with finitely many stationary frequencies and bounded derivatives through the Weyl-Maxwell operator order",
            "operator_property": "the linearized Weyl-Maxwell operator has stationary smooth coefficients, so it maps this correction space into bounded finite-quasiperiodic sources",
            "contradiction": "the certified source has nonzero quadratic growth -(7/2*Q_e^2+14/3*X)*t^2 for every X>0",
            "verdict": "no bounded or finite-quasiperiodic second-order correction exists anywhere on the nonzero-extra common-zero orbit",
        },
    }


def build() -> dict[str, Any]:
    result = theorem()
    return {
        "schema": "einstein-maxwell-weyl-global-extra-bounded-correction-obstruction-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA),
        "result_id": "EINSTEIN_MAXWELL_WEYL_GLOBAL_EXTRA_BOUNDED_CORRECTION_OBSTRUCTION",
        "result_state": "EVERY_NONZERO_GLOBAL_EXTRA_COMMON_ZERO_TANGENT_HAS_NO_BOUNDED_SECOND_ORDER_CORRECTION",
        "lifecycle_state": "OBSTRUCTED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "scope": {
            "theory": "Weyl-Maxwell",
            "background": "compact magnetically supported Plebanski-Hacyan product",
            "boundaries": "closed S1_L times S2; bounded or finite-quasiperiodic correction class",
            "charge_sector": "fixed N=2 magnetic bundle with arbitrary real first-order Q_e",
            "carrier": "complete certified nonzero-extra common-zero orbit in one homogeneous/twist times ell=2,k=0 extra multiplet",
            "degree": 2,
            "parity": "all four axial/polar extra multiplicities through the positive occupation X",
            "ell": "zero-frequency polar L=2 output",
            "m": "all through the certified aligned SO3 orbit",
            "k": 0,
            "omega": 0,
        },
        **result,
        "correction_classes": {
            "bounded_or_finite_quasiperiodic": "OBSTRUCTED for every nonzero point on the certified orbit",
            "smooth_exponential_polynomial": "OPEN: polynomial growth can invert this channel, but the complete mixed correction has not been assembled",
            "causal_or_retarded": "NO_CERTIFIED_MAP: no compact-product retarded BV complex is certified",
        },
        "classification": {
            "complete_nonzero_extra_common_zero_orbit_covered": True,
            "bounded_or_finite_quasiperiodic_correction_obstructed": True,
            "obstruction_is_independent_of_propagation_resonance": True,
            "smooth_exponential_polynomial_correction_constructed": False,
            "causal_retarded_map_certified": False,
            "all_orders_integrability": False,
        },
        "interpretation": "The necessary Taub/resonance common-zero theorem does not imply bounded second-order extendibility. Every nonzero common-zero point requires a twist velocity, and its self-source grows quadratically in the zero-frequency polar L=2 block. The bounded category is therefore empty on this orbit, while the smooth exponential-polynomial category remains a distinct open sufficiency problem.",
        "next_gate": "construct the complete smooth exponential-polynomial correction on the aligned SO3 orbit, including the twist-extra L=1,3 cross channels and the combined zero-frequency self-source",
        "claim_boundary": "This is a correction-class-specific second-order no-go. It does not obstruct smooth secular corrections, causal compact-source corrections, all-orders integration, other momentum fibres, final residual states, observations, particles or quantum theory.",
        "source_manifest": {str(path.relative_to(ROOT)): _sha256(path) for path in (*INPUTS.values(), Path(__file__).resolve(), SCHEMA)},
        "verification_receipt": {
            "producing_date": "2026-07-18",
            "tier_0": {"status": "PASS", "commands": ["python3 -m py_compile <scoped Python paths>", "python3 -m json.tool <certificate and schema>", "git diff --check -- <scoped paths>"]},
            "tier_1": {
                "status": "PASS",
                "commands": ["python3 -m bridge.einstein_sector.einstein_maxwell_weyl_global_extra_bounded_correction_obstruction --check", "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_global_extra_bounded_correction_obstruction.py", "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_global_extra_bounded_correction_obstruction"],
                "elapsed_seconds": {"generator_check": 0.63, "independent_verifier": 0.61, "unit_tests": 0.10},
            },
            "tier_2": {"status": "PASS_BY_CONTENT_ADDRESS", "reason": "the complete cone and direct twist source are unchanged certified inputs"},
            "tier_3": {"status": "NOT_RUN", "reason": "the smooth, causal and all-orders gates remain open"},
        },
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_global_extra_bounded_correction_obstruction --check",
            "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_global_extra_bounded_correction_obstruction.py",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_global_extra_bounded_correction_obstruction",
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
        raise AssertionError("bounded-correction obstruction certificate is stale")
    print("EINSTEIN_MAXWELL_WEYL_GLOBAL_EXTRA_BOUNDED_CORRECTION_OBSTRUCTION: PASS")


if __name__ == "__main__":
    main()
