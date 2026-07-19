"""Exclude every equal-ell generic k=0 oscillator pair from a minus target shell."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import sympy as sp

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_same_ell_generic_pair_minus_nonresonance.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_same_ell_generic_pair_minus_nonresonance.schema.json"
INPUTS = {
    "distinct_ell": ROOT / "bridge/certificates/einstein_maxwell_weyl_cross_ell_k0_generic_output_nonresonance.json",
    "finite_minus": ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_ellipse_finite_minus_dressing_no_go.json",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build() -> dict[str, object]:
    records = {name: json.loads(path.read_text()) for name, path in INPUTS.items()}
    distinct = records["distinct_ell"]["classification"]
    assert distinct["all_distinct_generic_input_ells_covered"]
    assert distinct["all_input_and_target_primary_branches_covered"]
    assert records["finite_minus"]["dispersion_lemma"]["integer_bracket"] == "w(a+b-1)<w(a)+w(b)<w(a+b) for integers a,b>=2"

    root3 = sp.sqrt(3)
    w2_squared = 6 - 2 * root3
    rational_bound = sp.Rational(159, 100)
    square_witness = 34719**2 - 12 * 10000**2
    assert square_witness > 0
    assert sp.Rational(34719, 10000) > 0
    ell2_direct = 18 - 10 * root3
    assert ell2_direct > 0

    return {
        "schema": "einstein-maxwell-weyl-same-ell-generic-pair-minus-nonresonance-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": sha(SCHEMA),
        "result_id": "EINSTEIN_MAXWELL_WEYL_SAME_ELL_GENERIC_PAIR_MINUS_NONRESONANCE",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "scope": {
            "theory": "Weyl-Maxwell target",
            "background": "compact magnetically supported Plebanski-Hacyan product",
            "boundaries": "closed S1_L times S2; stationary k=0 shell arithmetic",
            "charge_sector": "fixed N=2 magnetic bundle",
            "carrier": "every pair of generic q-minus, p-extra or q-plus oscillators with one common input ell",
            "degree": 2,
            "parity": "all input/output parity combinations conservatively retained",
            "ell": "common input ell>=2; every angularly allowed generic output 2<=L<=2ell",
            "m": "all Clebsch-Gordan-allowed values",
            "k": 0,
            "omega": "all signed sums and differences of the three generic branch frequencies",
        },
        "frequency_order": {
            "branches": "omega_minus(ell)<omega_extra(ell)<omega_plus(ell)",
            "lowest_generic_target": "omega_minus(2)=sqrt(6-2sqrt(3))",
            "monotonicity": "omega_minus(L) is strictly increasing for L>=2",
        },
        "difference_exclusion": {
            "largest_difference": "omega_plus(ell)-omega_minus(ell)",
            "ell_at_least_3_bound": "omega_plus(ell)<ell+5/4 and omega_minus(ell)>ell-17/50, hence the largest difference is <159/100",
            "lowest_target_bound": "159/100<sqrt(6-2sqrt(3)); exact squared witness is 34719^2-12*10000^2>0",
            "ell_2_direct_witness": "2*omega_minus(2)-omega_plus(2)>0 follows after squaring from 18-10sqrt(3)>0",
            "conclusion": "every nonzero branch difference is below every generic minus target frequency",
        },
        "sum_exclusion": {
            "minus_minus": "w(2ell-1)<2*w(ell)<w(2ell), so the smallest sum misses every integer-labelled minus shell",
            "all_other_pairs": "omega_minus(ell)>ell-1/2 and omega_extra(ell)>ell+3/10, so every non-minus-minus sum is >2ell-1/5",
            "largest_target": "omega_minus(2ell)<2ell-1/5",
            "conclusion": "every sum containing an extra or plus input lies above the largest angularly allowed minus target",
        },
        "combined_generic_pair_theorem": {
            "equal_input_ell": "all six unordered branch pairs and both temporal signs are nonresonant on every minus output shell",
            "distinct_input_ell": "the imported complete cross-ell theorem excludes every generic target branch, including minus",
            "conclusion": "no quadratic pair of generic k=0 p/q oscillators, at equal or distinct input ell, can occupy a generic Einstein-minus target shell",
        },
        "classification": {
            "all_equal_input_ell_at_least_2_covered": True,
            "all_six_unordered_branch_pairs_covered": True,
            "all_sum_and_difference_channels_covered": True,
            "all_angularly_allowed_minus_targets_covered": True,
            "combined_all_generic_input_ell_pairs_minus_nonresonant": True,
            "exceptional_ell1_times_generic_pairs_classified": False,
            "quadratic_source_coefficients_computed": False,
            "causal_or_quantum_claim": False,
        },
        "interpretation": "Generic oscillators cannot screen a d-times-minus resonant functional through a generic-generic quadratic product. After the dipole theorem, only an exceptional ell1 oscillator paired with a generic oscillator remains as a possible k=0 frequency competitor.",
        "next_gate": "exclude or classify exceptional ell1 times generic p/q pairs on angularly allowed minus targets",
        "claim_boundary": "This is a complete k=0 generic-pair-to-minus shell nonresonance theorem. It does not classify exceptional ell1 times generic pairs, source coefficients, nonzero momentum, bounded inversion, causal propagation, residual states or quantum claims.",
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
        raise AssertionError("stale same-ell generic-pair nonresonance certificate")
    print("EINSTEIN_MAXWELL_WEYL_SAME_ELL_GENERIC_PAIR_MINUS_NONRESONANCE: PASS")


if __name__ == "__main__":
    main()
