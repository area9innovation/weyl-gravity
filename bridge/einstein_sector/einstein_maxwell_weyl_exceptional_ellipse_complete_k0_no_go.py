"""Assemble the complete k=0 bounded no-go around the exceptional ellipse."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_ellipse_complete_k0_no_go.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_exceptional_ellipse_complete_k0_no_go.schema.json"
INPUTS = {
    "pair_census": ROOT / "bridge/certificates/einstein_maxwell_weyl_ell1_generic_pair_minus_nonresonance.json",
    "global_minus": ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_ellipse_standard_global_minus_no_go.json",
    "ell1": ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_ellipse_ell1_oscillator_minus_no_go.json",
    "wiener": ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_ellipse_wiener_minus_dressing_no_go.json",
    "moments": ROOT / "bridge/certificates/einstein_maxwell_weyl_mixed_moment_map_zero_locus.json",
    "pivot": ROOT / "bridge/certificates/einstein_maxwell_weyl_abd_generic_lambda_pivot.json",
    "ellipse": ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_axisymmetric_resonance_ellipse.json",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build() -> dict[str, object]:
    records = {name: json.loads(path.read_text()) for name, path in INPUTS.items()}
    assert records["pair_census"]["classification"]["complete_k0_oscillator_pair_to_minus_census_closed"]
    assert records["global_minus"]["classification"]["all_standard_generalized_zero_additions_covered"]
    assert records["ell1"]["classification"]["all_k0_physical_and_extra_ell1_oscillator_additions_covered"]
    assert records["wiener"]["classification"]["smooth_wiener_bohr_minus_completion_classified"]
    assert records["moments"]["same_nonzero_k_travelling_block"]["frequencies"]["strict_order_for_lambda_at_least_6"] == "0<omega_minus<omega_extra<omega_plus"
    assert records["pivot"]["classification"]["all_fixed_ell_at_least_2_pivots_nonzero"]
    assert records["ellipse"]["moment_map_audit"]["H"].startswith("strictly negative")

    return {
        "schema": "einstein-maxwell-weyl-exceptional-ellipse-complete-k0-no-go-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": sha(SCHEMA),
        "result_id": "EINSTEIN_MAXWELL_WEYL_EXCEPTIONAL_ELLIPSE_COMPLETE_K0_NO_GO",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "scope": {
            "theory": "Weyl-Maxwell target",
            "background": "compact magnetically supported Plebanski-Hacyan product",
            "boundaries": "closed S1_L times S2; bounded smooth uniformly almost-periodic correction",
            "charge_sector": "fixed N=2 magnetic bundle with first-order electric tangent allowed",
            "carrier": "any axisymmetric exceptional resonance-ellipse point, arbitrary standard generalized-zero data, arbitrary finite k=0 nonminus oscillators, and a smooth Wiener-Bohr k=0 Einstein-minus sum",
            "degree": 2,
            "parity": "all certified homogeneous, axial and polar parities",
            "ell": "global 0,1; all finite physical/extra ell1 and generic nonminus ell>=2; countable minus ell>=2",
            "m": "all retained m subject to convergent five stabilizer moment maps",
            "k": 0,
            "omega": "generalized zero and the complete certified k=0 q/p oscillator inventory",
        },
        "complete_carrier_inventory": {
            "generalized_zero": "all standard homogeneous, electric, Wilson and twist coordinates",
            "dipoles": "all physical standard and fourth-order extra ell1 oscillators",
            "generic_nonminus": "arbitrary finite Einstein-plus and both extra-primary multiplicities in every ell>=2",
            "generic_minus": "smooth Wiener-Bohr Einstein-minus completion in every ell>=2",
            "excluded": "nonzero compact momentum and non-Wiener maximal energy completions",
        },
        "taub_reduction": {
            "bounded_global_ideal": "b=B=0 and Q_e*a=0",
            "negative_blocks": "the exceptional ellipse, surviving a/Q_e globals, physical/extra ell1, generic Einstein-plus and generic extra-primary occupations all contribute with the nonpositive side of mu_H",
            "positive_block": "only Einstein-minus occupation supplies the opposite sign on the declared k=0 carrier",
            "necessity": "every common zero over a nonzero ellipse point contains at least one nonzero Einstein-minus coefficient",
        },
        "complete_minus_shell_isolation": {
            "oscillator_pairs": "the complete equal/distinct-ell generic and ell1/generic census proves that no quadratic oscillator pair reaches a generic minus shell",
            "global_columns": "b and B vanish; Q_e,c,W_x,A have zero relevant adjoint component; the a pivot is a distinct higher time degree",
            "wiener_projection": "absolute convergence makes every minus Bohr-harmonic adjoint coefficient a continuous projection",
            "remaining_source": "after the triangular a step, each occupied shell contains only d*C_parity(lambda)*c_(ell,m,parity)",
        },
        "contradiction": {
            "ellipse_fact": "d!=0 at every point of the nonzero resonance ellipse",
            "pivot_fact": "C_parity(lambda)!=0 in both parities for every lambda=ell(ell+1)>=6",
            "bounded_compatibility": "every Einstein-minus coefficient must vanish",
            "Taub_compatibility": "at least one Einstein-minus coefficient must be nonzero",
            "verdict": "the bounded second-order tangent cone has empty intersection with the complete declared carrier over the nonzero ellipse",
        },
        "correction_classes": {
            "BOUNDED_SMOOTH_UNIFORMLY_ALMOST_PERIODIC": {"status": "OBSTRUCTED"},
            "SMOOTH_INFINITE_SECULAR": {"status": "OPEN", "reason": "finite exponential-polynomial sufficiency has no certified uniform countable inverse estimate"},
            "CAUSAL_RETARDED": {"status": "NO_CERTIFIED_MAP"},
        },
        "classification": {
            "complete_declared_k0_carrier_covered": True,
            "all_standard_globals_covered": True,
            "all_finite_k0_nonminus_oscillators_covered": True,
            "smooth_wiener_bohr_minus_completion_covered": True,
            "bounded_tangent_cone_intersection_empty_over_nonzero_ellipse": True,
            "maximal_sobolev_or_finite_energy_completion_classified": False,
            "smooth_infinite_secular_extension_classified": False,
            "nonzero_momentum_classified": False,
            "all_orders_integrability": False,
            "causal_or_quantum_claim": False,
        },
        "interpretation": "At k=0 the exceptional resonance ellipse cannot be promoted to a bounded second-order tangent by any certified standard global datum or any finite collection of physical, extra or Einstein-plus oscillators, even with a smooth infinite Einstein-minus dressing. The obstruction is a genuine complete-carrier tangent-cone exclusion in the declared topology.",
        "next_gate": "treat nonzero compact momentum or weaken the Wiener topology with explicit Sobolev estimates; keep infinite secular, causal and all-orders questions separate",
        "claim_boundary": "Complete only for k=0, finite nonminus support and the declared smooth Wiener-Bohr minus completion. Maximal energy/Sobolev domains, infinite secular inverses, nonzero momentum, causal, residual, all-orders and quantum claims remain fail-closed.",
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
        raise AssertionError("stale complete k0 exceptional-ellipse no-go certificate")
    print("EINSTEIN_MAXWELL_WEYL_EXCEPTIONAL_ELLIPSE_COMPLETE_K0_NO_GO: PASS")


if __name__ == "__main__":
    main()
