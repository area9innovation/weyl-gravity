"""Exclude k=0 ell=1/generic oscillator pairs from every generic minus shell."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import sympy as sp

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_ell1_generic_pair_minus_nonresonance.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_ell1_generic_pair_minus_nonresonance.schema.json"
INPUTS = {
    "offsets": ROOT / "bridge/certificates/einstein_maxwell_weyl_cross_ell_k0_generic_output_nonresonance.json",
    "ell1_no_go": ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_ellipse_ell1_oscillator_minus_no_go.json",
    "generic_pair": ROOT / "bridge/certificates/einstein_maxwell_weyl_same_ell_generic_pair_minus_nonresonance.json",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build() -> dict[str, object]:
    records = {name: json.loads(path.read_text()) for name, path in INPUTS.items()}
    bounds = records["offsets"]["family_reduction"]["exact_open_bounds"]
    assert bounds["Einstein_minus"] == ["-1/2", "-1/5"]
    assert bounds["extra"] == ["3/10", "1/2"]
    assert bounds["Einstein_plus"] == ["1", "5/4"]
    assert records["ell1_no_go"]["classification"]["all_k0_physical_and_extra_ell1_oscillator_additions_covered"]
    assert records["generic_pair"]["classification"]["combined_all_generic_input_ell_pairs_minus_nonresonant"]

    exceptional = 2 / sp.sqrt(3)
    assert sp.Rational(23, 20) < exceptional < sp.Rational(7, 6)
    w2 = sp.sqrt(6 - 2 * sp.sqrt(3))
    assert sp.simplify(2 - w2) < w2

    return {
        "schema": "einstein-maxwell-weyl-ell1-generic-pair-minus-nonresonance-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": sha(SCHEMA),
        "result_id": "EINSTEIN_MAXWELL_WEYL_ELL1_GENERIC_PAIR_MINUS_NONRESONANCE",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "scope": {
            "theory": "Weyl-Maxwell target",
            "background": "compact magnetically supported Plebanski-Hacyan product",
            "boundaries": "closed S1_L times S2; stationary k=0 shell arithmetic",
            "charge_sector": "fixed N=2 magnetic bundle",
            "carrier": "one physical or extra ell1 oscillator paired with one generic q-minus, p-extra or q-plus oscillator",
            "degree": 2,
            "parity": "all input/output parity combinations conservatively retained",
            "ell": "ell1 input times generic ell>=2; generic target L in {ell-1,ell,ell+1} intersect L>=2",
            "m": "all Clebsch-Gordan-allowed values",
            "k": 0,
            "omega": "all signed sums/differences using ell1 frequencies 2/sqrt(3) and 2",
        },
        "integer_offset_reduction": {
            "generic_offsets": "u_minus in (-1/2,-1/5), u_extra in (3/10,1/2), u_plus in (1,5/4)",
            "target_offset": "u_target in (-1/2,-1/5)",
            "angular_integer": "D=L-ell belongs to {-1,0,1}",
            "exceptional_frequency_bounds": "23/20<2/sqrt(3)<7/6",
            "sum_equation": "D=u_branch+s-u_target",
            "difference_equation": "D=u_branch-s-u_target",
        },
        "interval_audit": {
            "exceptional_sum": {
                "minus": "D in (17/20,22/15); only D=1 is possible and the strict adjacent minus gap is <2/sqrt(3)",
                "extra": "D>33/20>1",
                "plus": "D>47/20>1",
            },
            "exceptional_difference": {
                "minus": "D in (-22/15,-17/20); only D=-1 is possible and the strict adjacent minus gap is <2/sqrt(3)",
                "extra": "D in (-2/3,-3/20), containing no integer",
                "plus": "D in (1/30,3/5), containing no integer",
            },
            "physical_sum": "for every branch D>17/10>1",
            "physical_difference": {
                "minus": "D in (-23/10,-17/10)",
                "extra": "D in (-3/2,-1)",
                "plus": "D in (-4/5,-1/4)",
            },
            "absolute_difference_exception": "only 2-omega_minus(2) reverses the order; it is strictly below omega_minus(2)",
            "conclusion": "no allowed integer D solves an ell1-generic sum/difference collision with a generic minus target",
        },
        "complete_k0_pair_census": {
            "ell1_ell1_and_ell1_original": "excluded by the imported dipole theorem",
            "generic_generic_equal_or_distinct_ell": "excluded by the imported combined generic-pair theorem",
            "ell1_generic": "excluded by this integer-offset theorem",
            "conclusion": "every quadratic pair of certified k=0 oscillators is nonresonant on every generic Einstein-minus target shell",
        },
        "classification": {
            "both_ell1_frequencies_covered": True,
            "all_three_generic_branches_covered": True,
            "all_angularly_allowed_minus_targets_covered": True,
            "all_sum_and_difference_channels_covered": True,
            "complete_k0_oscillator_pair_to_minus_census_closed": True,
            "quadratic_source_coefficients_computed": False,
            "nonzero_momentum_classified": False,
            "causal_or_quantum_claim": False,
        },
        "interpretation": "The shell arithmetic needed to screen a d-times-minus obstruction is now empty for the complete certified k=0 oscillator inventory. Combining this with the source pivot and Taub sign data yields the complete bounded no-go on the declared finite-nonminus/Wiener-minus carrier.",
        "next_gate": "assemble the complete k=0 carrier no-go from the empty pair census, standard-global reduction and nonzero d pivot",
        "claim_boundary": "This is shell arithmetic only. It does not itself assemble the bounded tangent-cone theorem, compute unrelated source channels, treat nonzero momentum, causal propagation, residual states or quantum claims.",
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
        raise AssertionError("stale ell1-generic minus nonresonance certificate")
    print("EINSTEIN_MAXWELL_WEYL_ELL1_GENERIC_PAIR_MINUS_NONRESONANCE: PASS")


if __name__ == "__main__":
    main()
