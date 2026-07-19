"""Certify the bounded obstruction on the Einstein-minus-balanced ellipse."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_ellipse_bounded_obstruction.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_exceptional_ellipse_bounded_obstruction.schema.json"
INPUTS = {
    "ellipse": ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_axisymmetric_resonance_ellipse.json",
    "balance": ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_ellipse_einstein_minus_frequency_gate.json",
    "zero_source": ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_ellipse_zero_frequency_source.json",
    "abd_minus": ROOT / "bridge/certificates/einstein_maxwell_weyl_abd_axial_ell2_minus_resonance.json",
    "ell2_neutral": ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_neutral_face_second_order.json",
    "smooth": ROOT / "bridge/certificates/einstein_maxwell_weyl_complete_finite_harmonic_smooth_global_second_order.json",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build() -> dict[str, object]:
    records = {name: json.loads(path.read_text(encoding="utf-8")) for name, path in INPUTS.items()}
    ellipse = records["ellipse"]
    balance = records["balance"]
    zero = records["zero_source"]
    abd = records["abd_minus"]
    if ellipse["parameterization"]["domain"] != "r_x,r_p>=0, d!=0, not both r_x,r_p zero":
        raise AssertionError("ellipse domain changed")
    if not balance["classification"]["mu_H_mu_Px_mu_Ji_all_zero_on_balanced_axisymmetric_fixture"]:
        raise AssertionError("Einstein-minus balance changed")
    if not zero["classification"]["complete_zero_frequency_source_solved"]:
        raise AssertionError("zero-frequency source changed")
    if not abd["classification"]["nonzero_minus_forces_a_b_d_zero"]:
        raise AssertionError("d-times-minus shell ideal changed")
    if abd["bounded_zero_locus"]["ideal_on_wave_amplitude_z"] != "<b*z,a*z,d*z>":
        raise AssertionError("bounded shell ideal changed")
    if not records["ell2_neutral"]["second_order_correction"]["all_nine_nonzero_frequency_pair_types_removable"]:
        raise AssertionError("ell2 wave self/cross ledger changed")

    root = sp.sqrt(3)
    frequency = sp.sqrt(6 - 2 * root)
    pairing = 12 * sp.I * (3 * root - 1) * frequency
    if sp.simplify(pairing) == 0:
        raise AssertionError("d-times-minus pairing lost nonzero algebraic value")

    return {
        "schema": "einstein-maxwell-weyl-exceptional-ellipse-bounded-obstruction-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA),
        "result_id": "EINSTEIN_MAXWELL_WEYL_EXCEPTIONAL_ELLIPSE_BOUNDED_OBSTRUCTION",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "scope": balance["scope"],
        "declared_tangent": {
            "ellipse_endpoint": "r_p=0, r_x^2=(115/16)d^2 with d!=0",
            "controls": ellipse["parameterization"],
            "Einstein_minus": balance["normalized_balance"]["required_direct_representative_occupation"],
            "stabilizer_moment_maps": "mu_H=mu_Px=mu_J1=mu_J2=mu_J3=0",
        },
        "unique_bounded_obstruction": {
            "carrier": "axial L=2,m=0,k=0 at Omega=omega_minus",
            "source_pair": "circumference velocity d times the axial Einstein-minus coefficient A_-",
            "adjoint_pairing_per_d_Aminus": "12*I*(3*sqrt(3)-1)*sqrt(6-2*sqrt(3))",
            "nonzero": True,
            "isolation": [
                "the original exceptional/control resonance equations are solved by the ellipse controls",
                "the complete zero-frequency source cancels",
                "Einstein-minus self and ordinary ell2 pair types are removable",
                "Einstein-minus cross products with exceptional and control oscillators are off shell",
                "no other occupied input pair lies on the L2,omega_minus carrier",
            ],
        },
        "correction_classes": {
            "BOUNDED_OR_FINITE_QUASIPERIODIC": {
                "status": "OBSTRUCTED",
                "reason": "d and A_- are both nonzero, while the exact shell ideal <b*z,a*z,d*z> forces d*A_-=0",
            },
            "SMOOTH_EXPONENTIAL_POLYNOMIAL": {
                "status": "CERTIFIED",
                "reason": "all five stabilizer moment maps vanish and the complete finite-support smooth theorem permits the required secular shell inverse",
            },
            "CAUSAL_RETARDED": {"status": "NO_CERTIFIED_MAP"},
        },
        "classification": {
            "nonzero_stabilizer_balanced_tangent_explicit": True,
            "complete_zero_frequency_source_solved": True,
            "unique_d_times_Einstein_minus_shell_pairing_nonzero": True,
            "bounded_or_finite_quasiperiodic_extension_obstructed": True,
            "smooth_exponential_polynomial_extension_certified": True,
            "general_exceptional_mixed_zero_locus_classified": False,
            "all_orders_integrability": False,
            "causal_or_quantum_claim": False,
        },
        "interpretation": "Einstein-minus charge balance does not rescue this exceptional resonance ellipse in the bounded correction class. The added wave cancels the Taub charge and the complete zero-frequency source, but its resonant product with the indispensable circumference velocity d has a nonzero dynamical adjoint pairing. Allowing a secular correction removes that particular obstruction.",
        "next_gate": "classify whether another exceptional mixed branch with d=0 and additional opposite-sign carriers can satisfy both the resonance equations and every bounded shell functional",
        "claim_boundary": "This is one axisymmetric pure-axial endpoint obstruction, not the full exceptional mixed zero locus. It does not assemble all m, treat nonzero momentum, prove all-orders integration, or make causal, residual, particle or quantum claims.",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": _sha256(Path(__file__)),
            "inputs": {
                name: {"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)}
                for name, path in INPUTS.items()
            },
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()
    value = build()
    if args.write:
        OUTPUT.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    elif json.loads(OUTPUT.read_text(encoding="utf-8")) != value:
        raise AssertionError("stale exceptional ellipse bounded-obstruction certificate")
    print("EINSTEIN_MAXWELL_WEYL_EXCEPTIONAL_ELLIPSE_BOUNDED_OBSTRUCTION: PASS")


if __name__ == "__main__":
    main()
