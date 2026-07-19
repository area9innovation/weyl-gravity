"""Exclude every single-mode Einstein-minus dressing of the resonance ellipse."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_ellipse_single_minus_dressing_no_go.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_exceptional_ellipse_single_minus_dressing_no_go.schema.json"
INPUTS = {
    "ellipse": ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_axisymmetric_resonance_ellipse.json",
    "generic_pivot": ROOT / "bridge/certificates/einstein_maxwell_weyl_abd_generic_lambda_pivot.json",
    "radiative_current": ROOT / "bridge/certificates/einstein_maxwell_weyl_radiative_symplectic_restriction.json",
    "smooth": ROOT / "bridge/certificates/einstein_maxwell_weyl_complete_finite_harmonic_smooth_global_second_order.json",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build() -> dict[str, object]:
    records = {name: json.loads(path.read_text(encoding="utf-8")) for name, path in INPUTS.items()}
    ellipse = records["ellipse"]
    pivot = records["generic_pivot"]
    current = records["radiative_current"]
    if not ellipse["classification"]["Einstein_minus_balance_required"]:
        raise AssertionError("ellipse charge sign changed")
    if ellipse["parameterization"]["domain"] != "r_x,r_p>=0, d!=0, not both r_x,r_p zero":
        raise AssertionError("ellipse domain changed")
    if not (
        pivot["classification"]["generic_lambda_functional_form_proved_without_interpolation"]
        and pivot["classification"]["all_fixed_ell_at_least_2_pivots_nonzero"]
        and pivot["classification"]["both_parities_classified"]
        and pivot["classification"]["all_m_promoted"]
    ):
        raise AssertionError("generic d-times-minus pivot changed")
    rad = current["theorem"]["all_ell_ge_2_classification"]
    if rad["minus_weight_sign"] != "negative" or not rad["restricted_target_form_nondegenerate"]:
        raise AssertionError("Einstein-minus current sign changed")
    if not records["smooth"]["classification"]["complete_finite_harmonic_smooth_tangent_cone_classified"]:
        raise AssertionError("complete smooth theorem changed")

    return {
        "schema": "einstein-maxwell-weyl-exceptional-ellipse-single-minus-dressing-no-go-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA),
        "result_id": "EINSTEIN_MAXWELL_WEYL_EXCEPTIONAL_ELLIPSE_SINGLE_MINUS_DRESSING_NO_GO",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "scope": {
            "theory": "Weyl-Maxwell target",
            "background": "compact magnetically supported Plebanski-Hacyan product",
            "boundaries": "closed S1_L times S2; bounded/finite-quasiperiodic correction",
            "charge_sector": "fixed N=2 magnetic bundle",
            "carrier": "any point of the axisymmetric exceptional resonance ellipse plus one axisymmetric Einstein-minus q-primary",
            "degree": 2,
            "parity": "the dressing may be axial or polar; output parities remain separate",
            "ell": "exceptional/control inputs 1,2 and one dressing ell_d>=2",
            "m": "m=0 dressing; generic pivot itself is certified for all m",
            "k": 0,
            "omega": "omega_minus^2=ell_d*(ell_d+1)-sqrt(2*ell_d*(ell_d+1))",
        },
        "charge_balance": {
            "ellipse_H_sign": "strictly negative away from the origin",
            "Einstein_minus_H_sign": "strictly positive in the Taub convention because the relative current weight is negative",
            "amplitude_choice": "the unique positive squared amplitude cancels mu_H",
            "other_stabilizers": "m=0 and k=0 give mu_Px=mu_J1=mu_J2=mu_J3=0",
        },
        "generic_obstruction": {
            "ellipse_fact": "d!=0 at every declared ellipse point",
            "pivot_domain": "lambda=ell_d*(ell_d+1)>=6",
            "axial_pivot": pivot["generic_lambda_derivation"]["axial_b_t2"],
            "polar_pivot": pivot["generic_lambda_derivation"]["polar_b_t3"],
            "triangular_consequence": pivot["nonvanishing"]["consequence"],
            "SO3": pivot["SO3_promotion"],
            "contradiction": "the nonzero dressing amplitude forces d=0 for bounded correction, but every ellipse point has d!=0",
        },
        "correction_classes": {
            "BOUNDED_OR_FINITE_QUASIPERIODIC": {"status": "OBSTRUCTED"},
            "SMOOTH_EXPONENTIAL_POLYNOMIAL": {"status": "CERTIFIED"},
            "CAUSAL_RETARDED": {"status": "NO_CERTIFIED_MAP"},
        },
        "classification": {
            "entire_axisymmetric_resonance_ellipse_covered": True,
            "every_single_m0_Einstein_minus_dressing_ell_ge_2_covered": True,
            "both_dressing_parities_covered": True,
            "stabilizer_balance_possible_but_bounded_extension_obstructed": True,
            "smooth_secular_extension_certified": True,
            "multiple_minus_modes_or_other_carriers_classified": False,
            "all_orders_integrability": False,
            "causal_or_quantum_claim": False,
        },
        "interpretation": "The endpoint obstruction is not an accident of ell=2 or axial parity. Every point of the exceptional resonance ellipse needs d!=0, whereas any single Einstein-minus mode capable of cancelling its Hamiltonian charge has a nonzero d-cross pivot in every physical ell and either parity. Thus no single-mode Einstein-minus dressing produces a bounded second-order tangent, although each stabilizer-balanced dressing has a smooth secular correction.",
        "next_gate": "test multi-minus and additional-carrier dressings, where distinct quadratic pairs could in principle share and cancel a d-times-minus shell functional",
        "claim_boundary": "This theorem covers one Einstein-minus dressing mode at a time. It does not exclude cancellations among multiple minus modes or additional carriers, classify nonzero momentum, prove all-orders integration, or make causal, residual, particle or quantum claims.",
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
        raise AssertionError("stale exceptional single-minus no-go certificate")
    print("EINSTEIN_MAXWELL_WEYL_EXCEPTIONAL_ELLIPSE_SINGLE_MINUS_DRESSING_NO_GO: PASS")


if __name__ == "__main__":
    main()
