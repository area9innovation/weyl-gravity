"""Exclude standard generalized-zero rescues of the exceptional ellipse plus minus sector."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_ellipse_standard_global_minus_no_go.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_exceptional_ellipse_standard_global_minus_no_go.schema.json"
INPUTS = {
    "wiener": ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_ellipse_wiener_minus_dressing_no_go.json",
    "global": ROOT / "bridge/certificates/einstein_maxwell_weyl_standard_global_bounded_second_order.json",
    "electric_wilson": ROOT / "bridge/certificates/einstein_maxwell_weyl_electric_wilson_complete_oscillator_transport.json",
    "circumference": ROOT / "bridge/certificates/einstein_maxwell_weyl_circumference_complete_oscillator_bounded_classification.json",
    "constant_twist": ROOT / "bridge/certificates/einstein_maxwell_weyl_fixed_ell_constant_twist_bounded_cone.json",
    "pivot": ROOT / "bridge/certificates/einstein_maxwell_weyl_abd_generic_lambda_pivot.json",
    "ellipse": ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_axisymmetric_resonance_ellipse.json",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build() -> dict[str, object]:
    records = {name: json.loads(path.read_text()) for name, path in INPUTS.items()}
    assert records["wiener"]["classification"]["smooth_wiener_bohr_minus_completion_classified"]
    assert records["global"]["classification"]["universal_b_twist_velocity_and_Qe_a_elimination_on_complete_finite_carrier"]
    assert records["electric_wilson"]["classification"]["Q_e_times_every_oscillator_bounded_removable"]
    assert records["electric_wilson"]["classification"]["W_x_times_every_oscillator_source_zero"]
    assert records["circumference"]["classification"]["k0_circumference_cross_bounded_removable"]
    assert records["constant_twist"]["classification"]["every_fixed_ell_constant_twist_bounded_product_cone_certified"]
    assert records["pivot"]["classification"]["all_fixed_ell_at_least_2_pivots_nonzero"]
    assert records["ellipse"]["parameterization"]["domain"] == "r_x,r_p>=0, d!=0, not both r_x,r_p zero"

    return {
        "schema": "einstein-maxwell-weyl-exceptional-ellipse-standard-global-minus-no-go-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": sha(SCHEMA),
        "result_id": "EINSTEIN_MAXWELL_WEYL_EXCEPTIONAL_ELLIPSE_STANDARD_GLOBAL_MINUS_NO_GO",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "scope": {
            "theory": "Weyl-Maxwell target",
            "background": "compact magnetically supported Plebanski-Hacyan product",
            "boundaries": "closed S1_L times S2; bounded smooth uniformly almost-periodic correction",
            "charge_sector": "fixed N=2 magnetic bundle with first-order electric tangent allowed",
            "carrier": "any axisymmetric exceptional resonance-ellipse point, arbitrary standard generalized-zero data, and a smooth Wiener-Bohr k=0 Einstein-minus sum",
            "degree": 2,
            "parity": "homogeneous plus both axial/polar dressing parities",
            "ell": "global ell=0,1; exceptional/control ell=1,2; every minus ell>=2 with countable support",
            "m": "all global components and minus m with convergent stabilizer moment maps",
            "k": 0,
            "omega": "generalized zero, exceptional/control frequencies, and occupied omega_minus(ell)",
        },
        "standard_global_reduction": {
            "coordinates": "homogeneous (a,b,c,d,Q_e,W_x) and twist (A,B), with d the total ellipse circumference-velocity coordinate",
            "universal_bounded_polynomial_ideal": "b=0, B=0, Q_e*a=0",
            "completion_extension": "products of bounded uniformly almost-periodic oscillators are bounded uniformly almost periodic and have no positive-degree time-polynomial coefficient, so the finite-support universal polynomial ideal remains necessary on the declared Wiener-Bohr completion",
            "remaining_global_mu_H": "-a^2-Q_e^2; c,d,W_x,A have zero diagonal Hamiltonian moment map",
            "balance_consequence": "the strictly negative ellipse plus the nonpositive surviving global contribution still requires at least one opposite-sign Einstein-minus coefficient",
            "spectators": {
                "W_x": "its mixed source with every oscillator vanishes",
                "Q_e": "duality supplies a bounded mixed primitive for every oscillator",
                "c": "the exact radius-family derivative supplies a bounded mixed primitive at k=0",
                "A": "the fixed-ell flat-connection theorem gives zero same-shell adjoint projection and bounded neighboring-channel inverses on every generic minus block",
            },
        },
        "triangular_resonant_reduction": {
            "projection_class": "continuous Bohr-frequency, spherical-harmonic and target-adjoint projections from the Wiener theorem",
            "first_step": "after b=0, the nonzero a-times-minus highest time-degree pivot forces a=0 on every occupied minus block",
            "second_step": "after a=b=0, the nonzero d-times-minus pivot forces every occupied minus coefficient to vanish because d!=0",
            "no_global_screening": "Q_e,c,W_x,A have zero resonant adjoint component by their exact transport theorems; B and b already vanish",
            "contradiction": "moment-map balance requires a nonzero minus coefficient, while bounded compatibility removes all of them",
        },
        "correction_classes": {
            "BOUNDED_SMOOTH_UNIFORMLY_ALMOST_PERIODIC": {"status": "OBSTRUCTED"},
            "SMOOTH_INFINITE_SECULAR": {"status": "OPEN", "reason": "no uniform inverse estimate is certified for the countable secular sum"},
            "CAUSAL_RETARDED": {"status": "NO_CERTIFIED_MAP"},
        },
        "classification": {
            "all_standard_generalized_zero_additions_covered": True,
            "smooth_wiener_bohr_minus_completion_covered": True,
            "bounded_extension_obstructed": True,
            "twist_velocity_and_cubic_jordan_velocity_eliminated": True,
            "electric_wilson_circumference_and_constant_twist_transport_accounted_for": True,
            "genuinely_oscillatory_nonminus_carriers_classified": False,
            "maximal_sobolev_or_finite_energy_completion_classified": False,
            "smooth_infinite_secular_extension_classified": False,
            "nonzero_momentum_classified": False,
            "causal_or_quantum_claim": False,
        },
        "interpretation": "No standard homogeneous, charge, Wilson or twist datum rescues the exceptional ellipse once the bounded polynomial and resonant ledgers are imposed. The only remaining possible k=0 rescue must use genuinely oscillatory nonminus carriers whose quadratic products can screen a minus shell.",
        "next_gate": "classify genuinely oscillatory Einstein-plus, extra-primary, physical-dipole or additional exceptional carriers on the d-times-minus resonant shells",
        "claim_boundary": "This theorem covers standard generalized-zero data plus the smooth Wiener-Bohr k=0 minus sector. Genuinely oscillatory nonminus carriers, maximal Sobolev domains, infinite secular inverses, nonzero momentum, causal, residual and quantum claims remain open.",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": sha(Path(__file__)),
            "inputs": {name: {"path": str(path.relative_to(ROOT)), "sha256": sha(path)} for name, path in INPUTS.items()},
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    value = build()
    if args.write:
        OUTPUT.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
    elif json.loads(OUTPUT.read_text()) != value:
        raise AssertionError("stale exceptional standard-global minus no-go certificate")
    print("EINSTEIN_MAXWELL_WEYL_EXCEPTIONAL_ELLIPSE_STANDARD_GLOBAL_MINUS_NO_GO: PASS")


if __name__ == "__main__":
    main()
