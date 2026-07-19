"""Join the candidate-13 prime resonance cone to the pure-extra Taub theorem."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_candidate13_pure_extra_taub_join.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_ell2_two_abs_momentum_candidate13_pure_extra_taub_join.schema.json"
INCIDENCE = ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_candidate13_L4_incidence_reduction.json"
TAUB = ROOT / "bridge/certificates/einstein_maxwell_weyl_moment_map_taub_bridge.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build() -> dict[str, object]:
    incidence = json.loads(INCIDENCE.read_text())
    taub = json.loads(TAUB.read_text())
    incidence_flags = incidence["classification"]
    taub_flags = taub["classification"]
    if not (
        incidence["candidate_index"] == 13
        and incidence["pencil_reduction"]["ambient_dimension_over_C"] == 40
        and incidence_flags["full_candidate_13_zero_variety_classified"]
        and incidence_flags["candidate_13_ideal_prime"]
        and incidence["scope"]["ell"] == "2 times 2 -> L=4"
    ):
        raise AssertionError("candidate-13 prime incidence input changed")
    if not (
        taub_flags["generic_covariant_moment_map_Taub_equality_certified"]
        and taub_flags["generic_extra_H_Taub_negative_definite"]
        and taub_flags["all_nonzero_generic_pure_extra_fixed_bundle_tangents_second_order_obstructed"]
    ):
        raise AssertionError("pure-extra Taub input changed")
    carrier = incidence["scope"]["carrier"]
    if "two multiplicity-two p_extra source branches" not in carrier:
        raise AssertionError("candidate-13 carrier ceased to be pure extra")
    return {
        "schema": "einstein-maxwell-weyl-ell2-two-abs-momentum-candidate13-pure-extra-taub-join-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": sha(SCHEMA),
        "result_id": "EINSTEIN_MAXWELL_WEYL_ELL2_TWO_ABS_MOMENTUM_CANDIDATE13_PURE_EXTRA_TAUB_JOIN",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle_state": "CLASSIFIED",
        "generality_level": "G2",
        "scope": incidence["scope"],
        "real_tangent_domain": {
            "positive_frequency_coordinates": "four p-primary internal amplitudes for each m=-2,...,2 on each of the signed momentum fibres n=1 and n=-2, with axial and polar parities retained",
            "reality": "negative-frequency coefficients are the complex conjugates; the declared coefficient space represents real finite harmonic tangents",
            "excluded": "all q-primary Einstein amplitudes, exceptional/global modes, charge-varying families and other momentum fibres",
        },
        "taub_restriction": {
            "formula": "mu_H(u)=-(L/4) sum_{j in {1,-2}} omega_j^2 c_j^dagger (G_X tensor W_2) c_j",
            "frequency_squared": "omega_j^2=k_j^2+16/3>0",
            "axial_extra_Gram_inertia": [2, 0],
            "polar_extra_Gram_inertia": [2, 0],
            "angular_form": "W_2 is positive definite",
            "cross_fibre_terms": "zero because H and the Lee-Wald current are diagonal in compact momentum and frequency shell",
            "verdict": "mu_H(u)<0 for every nonzero real tangent in the complete declared candidate-13 ambient p-primary carrier",
        },
        "common_zero_theorem": {
            "resonance_variety": "the prime complex dimension-22 candidate-13 cross-fibre cone",
            "equation": "Z_res(candidate13) intersect {mu_H=0}={0}",
            "all_five_moment_maps": "the common zero of (mu_H,mu_Px,mu_J1,mu_J2,mu_J3) on the resonance cone is {0} because its projection to mu_H=0 is already {0}",
            "same_fibre_sources_needed_for_no_go": False,
        },
        "second_order_verdict": {
            "bounded_or_finite_quasiperiodic": "OBSTRUCTED for every nonzero real tangent in the declared candidate-13 pure-extra carrier",
            "smooth_secular": "OBSTRUCTED for every nonzero real tangent because the stabilizer adjoint-cokernel pairing is independent of allowing secular propagation corrections",
            "causal_retarded": "NO_CERTIFIED_MAP",
            "zero_tangent": "trivially extendible and not counted as a nonzero mode",
        },
        "classification": {
            "candidate_13_prime_resonance_cone_imported": True,
            "candidate_13_pure_extra_H_Taub_negative_definite": True,
            "candidate_13_resonance_Taub_common_zero_is_origin": True,
            "candidate_13_nonzero_pure_extra_bounded_extension_obstructed": True,
            "candidate_13_nonzero_pure_extra_smooth_secular_extension_obstructed": True,
            "candidate_13_same_fibre_source_matrices_classified": False,
            "mixed_Einstein_extra_two_fibre_cone_classified": False,
            "causal_residual_observational_or_quantum_claim": False,
        },
        "provenance": {
            "inputs": {
                str(INCIDENCE.relative_to(ROOT)): sha(INCIDENCE),
                str(TAUB.relative_to(ROOT)): sha(TAUB),
            }
        },
        "next_gate": "adjoin q-primary Einstein amplitudes on the same tuned circumference, then restrict the same-fibre source ledger and all five moment maps to the resulting mixed carrier",
        "claim_boundary": "This theorem obstructs every nonzero real tangent in the declared candidate-13 pure-extra two-momentum carrier. It does not classify the larger mixed Einstein-extra carrier, same-fibre source matrices, charge-varying families, causal corrections, final residual observables or quantum states.",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rendered = json.dumps(build(), indent=2, sort_keys=True) + "\n"
    if args.write:
        OUTPUT.write_text(rendered)
    elif not OUTPUT.exists() or OUTPUT.read_text() != rendered:
        raise AssertionError("candidate-13 pure-extra Taub join certificate is stale")
    print("EINSTEIN_MAXWELL_WEYL_ELL2_TWO_ABS_MOMENTUM_CANDIDATE13_PURE_EXTRA_TAUB_JOIN: PASS")


if __name__ == "__main__":
    main()
