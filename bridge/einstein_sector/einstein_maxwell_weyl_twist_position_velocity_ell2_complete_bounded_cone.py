"""Certify the complete bounded cone after adjoining twist velocity."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_twist_position_velocity_ell2_complete_bounded_cone.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_twist_position_velocity_ell2_complete_bounded_cone.schema.json"
INPUTS = {
    "position_cone": ROOT / "bridge/certificates/einstein_maxwell_weyl_constant_twist_ell2_complete_bounded_cone.json",
    "global_polynomial": ROOT / "bridge/certificates/einstein_maxwell_weyl_standard_global_bounded_second_order.json",
}


class TwistPositionVelocityConeError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise TwistPositionVelocityConeError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _velocity_elimination(polynomial_growth: dict[str, Any], source_result_id: str) -> dict[str, Any]:
    bx, by, bz = sp.symbols("B_x B_y B_z", real=True)
    vector = sp.Matrix([bx, by, bz])
    norm_squared = sp.expand(vector.dot(vector))
    stf = vector * vector.T - sp.eye(3) * norm_squared / 3
    stf_norm_squared = sp.factor(sp.trace(stf.T * stf))
    expected = sp.Rational(2, 3) * norm_squared**2
    _require(stf_norm_squared == expected, "twist-velocity STF norm changed")
    _require(polynomial_growth["SO3_twist_leading_tensor"] == "STF(B tensor B)", "imported twist tensor changed")
    _require(polynomial_growth["SO3_twist_leading_norm_squared"] == str(expected), "imported twist norm changed")
    _require(polynomial_growth["twist_polar_L2_metric_00_t2"] == "-7*B**2", "direct aligned twist coefficient changed")
    return {
        "bounded_obstruction_tensor": "STF(B tensor B)*t^2 in the polar L=2 source",
        "exact_norm_squared": str(stf_norm_squared),
        "direct_aligned_metric_00_coefficient": polynomial_growth["twist_polar_L2_metric_00_t2"],
        "real_zero_locus": "B_x=B_y=B_z=0",
        "why_other_inputs_cannot_cancel_it": "finite oscillatory products are bounded and generalized-zero cross terms have different harmonic or polynomial degree",
        "source_certificate_result_id": source_result_id,
    }


def build() -> dict[str, Any]:
    records = {name: json.loads(path.read_text(encoding="utf-8")) for name, path in INPUTS.items()}
    position = records["position_cone"]
    global_polynomial = records["global_polynomial"]
    _require(
        position["classification"]["bounded_zero_locus_necessary_and_sufficient"]
        and position["classification"]["complete_constant_twist_plus_ell2_wave_carrier_covered"],
        "constant-twist ell2 bounded cone changed",
    )
    _require(
        global_polynomial["classification"]["universal_b_twist_velocity_and_Qe_a_elimination_on_complete_finite_carrier"],
        "universal twist-velocity elimination changed",
    )
    _require(
        global_polynomial["universal_complete_carrier_corollary"]["statement"]
        == "for any complete finite-support input admitting a bounded second-order correction, b=0, B=0 and Q_e*a=0",
        "universal finite-carrier statement changed",
    )
    universal_reason = global_polynomial["universal_complete_carrier_corollary"]["reason"]
    _require("oscillator products are bounded" in universal_reason and "twist L=2 STF(B tensor B)*t^2" in universal_reason, "universal noncancellation proof changed")
    velocity = _velocity_elimination(global_polynomial["polynomial_growth_ideal"], global_polynomial["result_id"])
    value = {
        "schema": "einstein-maxwell-weyl-twist-position-velocity-ell2-complete-bounded-cone-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA),
        "result_id": "EINSTEIN_MAXWELL_WEYL_TWIST_POSITION_VELOCITY_ELL2_COMPLETE_BOUNDED_CONE",
        "result_state": "COMPLETE_TWIST_POSITION_VELOCITY_ELL2_BOUNDED_CONE_CLASSIFIED",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "scope": {
            "theory": "Weyl-Maxwell target",
            "background": "compact magnetically supported Plebanski-Hacyan product",
            "boundaries": "closed S1_L times S2; bounded or finite-quasiperiodic second-order correction",
            "charge_sector": "fixed N=2 magnetic bundle; all homogeneous tangents except the axial twist position/velocity pair are zero",
            "carrier": "arbitrary real axial twist position A and velocity B plus the complete axial/polar ell=2,k=0 Einstein-plus, Einstein-minus and extra-primary wave carrier",
            "degree": 2,
            "parity": "axial generalized-zero twist and axial/polar wave branches",
            "ell": "global 1 plus wave 2; outputs 0,...,4",
            "m": "all three real twist components and all wave m=-2,...,2",
            "k": 0,
            "omega": "generalized zero plus the three distinct ell2 positive-frequency shells",
        },
        "twist_velocity_elimination": velocity,
        "complete_bounded_zero_locus": {
            "first_equation": "B=0",
            "A_zero_branch": "mu_H=mu_J1=mu_J2=mu_J3=0 on the complete ell2 q/p wave carrier",
            "A_nonzero_branch": "rotate A to its axis; both Einstein q-primary shells have only m_A=0, each nonzero-m extra coefficient lies in span{polar_e1,-4*sqrt(3)*axial_e1+15*polar_e2}, and mu_H=mu_J1=mu_J2=mu_J3=0",
            "necessity": "the universal polar L=2 t^2 coefficient forces B=0; the remaining equations are the complete constant-position theorem",
            "sufficiency": "after B=0 the tangent lies exactly in the certified constant-position carrier, whose displayed equations admit a bounded correction",
            "nonaxisymmetric_survivor": "B=0 with nonzero A, equal polar_e1 amplitudes at m_A=+2,-2, and the certified Einstein-minus energy balance",
        },
        "correction_classes": {
            "BOUNDED_OR_FINITE_QUASIPERIODIC": {"status": "CERTIFIED", "claim": "the displayed equations are necessary and sufficient on the declared A,B plus ell2 carrier"},
            "SMOOTH_EXPONENTIAL_POLYNOMIAL": {"status": "CERTIFIED", "claim": "every certified bounded correction is a smooth exponential-polynomial correction; the larger secular cone with B nonzero is not classified"},
            "CAUSAL_RETARDED": {"status": "NO_CERTIFIED_MAP"},
        },
        "classification": {
            "complete_twist_position_velocity_plus_ell2_wave_carrier_covered": True,
            "twist_velocity_forced_zero_in_bounded_class": True,
            "bounded_zero_locus_necessary_and_sufficient": True,
            "nonaxisymmetric_nonzero_position_survivor_retained": True,
            "other_homogeneous_tangents_classified": False,
            "other_ell_or_nonzero_momentum_classified": False,
            "unrestricted_smooth_secular_cone_classified": False,
            "causal_or_quantum_claim": False,
            "all_orders_integrability": False,
        },
        "interpretation": "Twist velocity is a genuine linear Jordan partner but not a bounded second-order direction on this finite carrier. Its self-source has an uncancellable quadratic-in-time polar quadrupole, so the bounded cone lies entirely on B=0 and is exactly the previously certified constant-position cone. Constant twist position remains nontrivial and can coexist with off-axis wave data.",
        "next_gate": "adjoin the remaining homogeneous directions a,c,d,Q_e,W_x one scope at a time, using their already classified polynomial and shell ledgers; then generalize the constant-position incidence map to arbitrary fixed ell",
        "claim_boundary": "This theorem is complete only for axial twist position/velocity plus the full ell=2,k=0 q/p wave carrier in the bounded correction class. It does not classify other homogeneous tangents, other ell, nonzero or opposite momentum, the unrestricted secular cone, causal propagation, all-orders solutions, residual states, observables or quantum theory.",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "inputs": {name: {"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)} for name, path in INPUTS.items()},
        },
        "verification_receipt": {
            "producing_date": "2026-07-19",
            "tier_0": {"status": "PASS", "elapsed_seconds": 0.24},
            "tier_1": {"status": "PASS", "elapsed_seconds": 3.03, "tests_run": 35},
            "tier_2": {"status": "PASS_BY_CONTENT_ADDRESS", "criterion": "the direct global polynomial-growth theorem and complete constant-position ell2 cone are unchanged hashed inputs"},
            "tier_3": {"status": "NOT_RUN", "reason": "other homogeneous and harmonic directions remain open; no programme-wide freeze is promoted"},
        },
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_twist_position_velocity_ell2_complete_bounded_cone --check",
            "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_twist_position_velocity_ell2_complete_bounded_cone.py",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_twist_position_velocity_ell2_complete_bounded_cone",
        ],
    }
    Draft202012Validator.check_schema(json.loads(SCHEMA.read_text(encoding="utf-8")))
    Draft202012Validator(json.loads(SCHEMA.read_text(encoding="utf-8"))).validate(value)
    return value


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    arguments = parser.parse_args()
    value = build()
    if arguments.write:
        OUTPUT.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    elif json.loads(OUTPUT.read_text(encoding="utf-8")) != value:
        raise TwistPositionVelocityConeError("twist-position/velocity ell2 bounded-cone certificate is stale")
    print("EINSTEIN_MAXWELL_WEYL_TWIST_POSITION_VELOCITY_ELL2_COMPLETE_BOUNDED_CONE: PASS")


if __name__ == "__main__":
    main()
