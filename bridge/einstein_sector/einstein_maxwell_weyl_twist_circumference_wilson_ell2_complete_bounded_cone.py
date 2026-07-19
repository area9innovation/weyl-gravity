"""Adjoin the k=0 circumference and Wilson spectators to the twist-wave cone."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_twist_circumference_wilson_ell2_complete_bounded_cone.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_twist_circumference_wilson_ell2_complete_bounded_cone.schema.json"
INPUTS = {
    "twist_wave": ROOT / "bridge/certificates/einstein_maxwell_weyl_twist_position_velocity_ell2_complete_bounded_cone.json",
    "circumference": ROOT / "bridge/certificates/einstein_maxwell_weyl_circumference_complete_oscillator_bounded_classification.json",
    "electric_wilson": ROOT / "bridge/certificates/einstein_maxwell_weyl_electric_wilson_complete_oscillator_transport.json",
    "global": ROOT / "bridge/certificates/einstein_maxwell_weyl_standard_global_bounded_second_order.json",
}


class TwistCircumferenceWilsonConeError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise TwistCircumferenceWilsonConeError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build() -> dict[str, Any]:
    records = {name: json.loads(path.read_text(encoding="utf-8")) for name, path in INPUTS.items()}
    _require(records["twist_wave"]["classification"]["bounded_zero_locus_necessary_and_sufficient"], "twist-wave cone changed")
    _require(records["circumference"]["classification"]["k0_circumference_cross_bounded_removable"], "k0 circumference transport changed")
    _require(records["electric_wilson"]["classification"]["W_x_times_every_oscillator_source_zero"], "Wilson transport changed")
    cross_terms = records["global"]["bounded_correction"]["cross_terms"]
    _require("c is absent" in cross_terms and "W_x has zero field strength" in cross_terms, "global spectator cross terms changed")
    value = {
        "schema": "einstein-maxwell-weyl-twist-circumference-wilson-ell2-complete-bounded-cone-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA),
        "result_id": "EINSTEIN_MAXWELL_WEYL_TWIST_CIRCUMFERENCE_WILSON_ELL2_COMPLETE_BOUNDED_CONE",
        "result_state": "COMPLETE_C_WX_A_B_ELL2_BOUNDED_CONE_CLASSIFIED",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "scope": {
            "theory": "Weyl-Maxwell target",
            "background": "compact magnetically supported Plebanski-Hacyan product",
            "boundaries": "closed S1_L times S2; bounded or finite-quasiperiodic second-order correction",
            "charge_sector": "fixed N=2 magnetic bundle; electric, radion and circumference-velocity tangents set to zero",
            "carrier": "constant circumference c, flat Wilson W_x, arbitrary axial twist position A and velocity B, plus the complete axial/polar ell=2,k=0 q/p wave carrier",
            "degree": 2,
            "parity": "homogeneous spectators, axial generalized-zero twist and axial/polar waves",
            "ell": "global 0,1 plus wave 2; outputs 0,...,4",
            "m": "all twist components and all wave m=-2,...,2",
            "k": 0,
            "omega": "generalized zero plus all three ell2 shells",
        },
        "spectator_proof": {
            "circumference_wave": "the exact circle-radius family transports every k=0 oscillator and supplies a bounded mixed correction",
            "circumference_twist": "the direct generalized-zero source contains no c-times-twist term",
            "Wilson_wave": "D^2E[W_x,u_wave]=0 because delta F(W_x dx)=0",
            "Wilson_twist": "the Euler operators depend on the U1 connection only through F=dA",
            "self_and_mutual": "c and W_x have zero self and mutual quadratic sources on the declared global face",
        },
        "complete_bounded_zero_locus": {
            "free_spectators": "c and W_x are arbitrary real tangent coordinates",
            "twist_velocity": "B=0",
            "remaining_equations": "exactly the constant-position ell2 q/p shell restrictions and mu_H=mu_J1=mu_J2=mu_J3=0",
            "product_structure": "Z2_bounded(c,W_x,A,B,wave)=R_c x R_Wx x Z2_bounded(A,B,wave)",
            "necessity_and_sufficiency": "the spectator columns introduce no new cokernel equation, and their bounded corrections superpose with the complete twist-wave correction",
        },
        "correction_classes": {
            "BOUNDED_OR_FINITE_QUASIPERIODIC": {"status": "CERTIFIED"},
            "SMOOTH_EXPONENTIAL_POLYNOMIAL": {"status": "CERTIFIED", "claim": "the bounded correction is a smooth subclass; the unrestricted secular cone is not reclassified"},
            "CAUSAL_RETARDED": {"status": "NO_CERTIFIED_MAP"},
        },
        "classification": {
            "complete_c_Wx_A_B_plus_ell2_wave_carrier_covered": True,
            "circumference_and_Wilson_are_exact_bounded_spectators": True,
            "bounded_zero_locus_necessary_and_sufficient": True,
            "radion_circumference_velocity_or_electric_tangents_classified": False,
            "other_ell_or_nonzero_momentum_classified": False,
            "unrestricted_smooth_secular_cone_classified": False,
            "causal_or_quantum_claim": False,
            "all_orders_integrability": False,
        },
        "interpretation": "The compact global data stratify into dynamical and spectator directions. At k=0, circumference position and Wilson holonomy form a flat product factor over the nonlinear twist-wave cone, whereas twist velocity is removed. The next enlargements a, d and Q_e cannot be treated as spectators.",
        "next_gate": "adjoin the radion position a, circumference velocity d and electric tangent Q_e as separate dynamical incidence problems",
        "claim_boundary": "This is complete only for c,W_x,A,B plus the ell=2,k=0 q/p wave carrier in the bounded class. It excludes a,b,d,Q_e, other ell and momentum, unrestricted secular corrections, causal propagation, all-orders integration, residual observables and quantum theory.",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "inputs": {name: {"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)} for name, path in INPUTS.items()},
        },
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_twist_circumference_wilson_ell2_complete_bounded_cone --check",
            "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_twist_circumference_wilson_ell2_complete_bounded_cone.py",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_twist_circumference_wilson_ell2_complete_bounded_cone",
        ],
    }
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
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
        raise TwistCircumferenceWilsonConeError("twist/circumference/Wilson ell2 certificate is stale")
    print("EINSTEIN_MAXWELL_WEYL_TWIST_CIRCUMFERENCE_WILSON_ELL2_COMPLETE_BOUNDED_CONE: PASS")


if __name__ == "__main__":
    main()
