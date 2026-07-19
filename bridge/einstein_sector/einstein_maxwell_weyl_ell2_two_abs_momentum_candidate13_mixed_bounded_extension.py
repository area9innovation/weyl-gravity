"""Certify a bounded second-order extension of the candidate-13 mixed witness."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_candidate13_mixed_bounded_extension.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_ell2_two_abs_momentum_candidate13_mixed_bounded_extension.schema.json"
INPUTS = {
    "mixed_witness": ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_candidate13_mixed_moment_resonance_null_witness.json",
    "same_fibre_census": ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_candidate13_same_fibre_resonance_census.json",
    "finite_generic_cone": ROOT / "bridge/certificates/einstein_maxwell_weyl_finite_generic_smooth_global_second_order.json",
    "isolated_cross_fibre_candidates": ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_isolated_candidates.json",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(value: bool, message: str) -> None:
    if not value:
        raise AssertionError(message)


def build() -> dict[str, object]:
    records = {name: json.loads(path.read_text(encoding="utf-8")) for name, path in INPUTS.items()}
    witness = records["mixed_witness"]
    same = records["same_fibre_census"]
    generic = records["finite_generic_cone"]
    isolated = records["isolated_cross_fibre_candidates"]

    witness_flags = witness["classification"]
    require(witness_flags["nonzero_real_mixed_witness_certified"], "candidate-13 mixed witness disappeared")
    require(witness_flags["all_five_stabilizer_moment_maps_zero"], "candidate-13 moment-map cancellation changed")
    require(witness_flags["candidate_13_cross_fibre_resonance_functionals_zero"], "candidate-13 cross-fibre cancellation changed")
    same_flags = same["classification"]
    require(same["channel_count"] == 18 and same["nonzero_defect_count"] == 144, "same-fibre census changed")
    require(same_flags["candidate_13_all_nonzero_same_fibre_channels_off_shell"], "same-fibre shell exclusion changed")
    require(not same_flags["same_fibre_nonzero_frequency_source_matrices_required_for_bounded_gate"], "same-fibre source gate reopened")
    generic_flags = generic["classification"]
    require(generic_flags["complete_reduced_adjoint_cokernel_decomposition_certified"], "zero-block cokernel theorem changed")
    require("exists exactly" in generic["bounded_resonance_functionals"]["necessity_and_sufficiency"], "bounded sufficiency theorem changed")
    require(isolated["classification"]["twenty_one_distinct_admissible_candidates"], "cross-fibre isolation changed")

    return {
        "schema": "einstein-maxwell-weyl-ell2-two-abs-momentum-candidate13-mixed-bounded-extension-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": sha(SCHEMA),
        "result_id": "EINSTEIN_MAXWELL_WEYL_ELL2_TWO_ABS_MOMENTUM_CANDIDATE13_MIXED_BOUNDED_EXTENSION",
        "result_state": "ONE_CANDIDATE13_MIXED_EINSTEIN_EXTRA_TANGENT_EXTENDS_TO_SECOND_ORDER_IN_THE_BOUNDED_CLASS",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "generality_level": "G1_ONE_EXACT_MIXED_THREE_OCCUPATION_WITNESS",
        "scope": witness["scope"],
        "declared_tangent": {
            "p_primary_n1_occupation": witness["occupation_witness"]["p_primary_n1"],
            "p_primary_n_minus2_occupation": witness["occupation_witness"]["p_primary_n_minus2"],
            "q_minus_n1_occupation": witness["occupation_witness"]["q_minus_n1"],
            "q_minus_n_minus2_occupation": witness["occupation_witness"]["q_minus_n_minus2"],
            "relative_phases": "choose the positive real square roots of the displayed occupations; adjoin their negative-frequency complex conjugates",
            "reality": "the resulting first-order tangent and its blockwise correction are real",
        },
        "second_order_equation": "L_WM v=-(1/2)D^2E_WM[u,u]",
        "complete_blockwise_proof": {
            "abstract_criterion": generic["bounded_resonance_functionals"]["necessity_and_sufficiency"],
            "zero_frequency_cokernel": generic["complete_adjoint_cokernel_decomposition"]["zero_block"]["decomposition"],
            "zero_frequency_pairings": {
                "mu_H": "0",
                "mu_Px": "0",
                "mu_J1": "0",
                "mu_J2": "0",
                "mu_J3": "0",
            },
            "zero_frequency_consequence": "every constant source block lies in the image; L=0 and L=1 use the five vanishing stabilizer pairings, while every static L>=2 block is invertible after local gauge reduction",
            "same_fibre_nonzero_frequency": "all 18 channels are off shell by 144 exact defects; the two L=0 Fourier types use their separately certified empty quotients",
            "cross_fibre_nonzero_frequency": "the only candidate-13 shell functional is zero because p_primary_n_minus2=0; all other isolated cross-fibre collision fibres have distinct circumference",
            "correction_construction": "solve each finite off-shell block by its certified algebraic inverse, solve each zero-frequency compatible block by the certified reduced right inverse, and adjoin complex-conjugate blocks",
            "temporal_class": "finite quasiperiodic with no secular term",
            "spatial_class": "smooth and S1_L-periodic",
        },
        "correction_classes": {
            "BOUNDED_OR_FINITE_QUASIPERIODIC": {"status": "CERTIFIED"},
            "SMOOTH_EXPONENTIAL_POLYNOMIAL": {"status": "CERTIFIED", "reason": "the bounded correction lies in this larger class"},
            "CAUSAL_RETARDED": {"status": "NO_CERTIFIED_MAP"},
        },
        "classification": {
            "candidate_13_mixed_witness_bounded_second_order_extendible": True,
            "all_five_zero_frequency_adjoint_pairings_vanish": True,
            "all_same_fibre_nonzero_frequency_blocks_off_shell": True,
            "all_cross_fibre_bounded_resonance_functionals_vanish": True,
            "complete_finite_block_bounded_source_in_image": True,
            "explicit_blockwise_correction_recipe_certified": True,
            "full_candidate_13_mixed_tangent_cone_classified": False,
            "all_orders_integrability": False,
            "causal_residual_observational_or_quantum_claim": False,
        },
        "interpretation": "The candidate-13 mixed witness is not merely Taub-null. Its zero-frequency source has no adjoint-cokernel component, every nonzero same-fibre block is off shell, and its only possible cross-fibre shell coefficient vanishes. Hence the pure-extra obstruction is genuinely evaded by an Einstein-minus admixture at second order in the bounded class.",
        "next_gate": "classify the full mixed candidate-13 coefficient cone rather than extrapolating from this one extendible ray; causal/retarded extension remains a separate background-specific problem",
        "claim_boundary": "This certifies one exact axial m=0 mixed three-occupation tangent and a bounded second-order correction before the final residual quotient. It does not classify the full mixed cone, arbitrary phases or polar amplitudes, prove all-orders integration, construct a causal correction, or make residual, observational or quantum claims.",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": sha(Path(__file__)),
            "inputs": {name: {"path": str(path.relative_to(ROOT)), "sha256": sha(path)} for name, path in INPUTS.items()},
        },
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_ell2_two_abs_momentum_candidate13_mixed_bounded_extension --check",
            "python3 -m bridge.einstein_sector.verify_einstein_maxwell_weyl_ell2_two_abs_momentum_candidate13_mixed_bounded_extension",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_ell2_two_abs_momentum_candidate13_mixed_bounded_extension",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = build()
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(payload)
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.write:
        OUTPUT.write_text(rendered, encoding="utf-8")
    elif not OUTPUT.exists() or OUTPUT.read_text(encoding="utf-8") != rendered:
        raise AssertionError("candidate-13 mixed bounded-extension certificate is stale")
    print("EINSTEIN_MAXWELL_WEYL_ELL2_TWO_ABS_MOMENTUM_CANDIDATE13_MIXED_BOUNDED_EXTENSION: PASS")


if __name__ == "__main__":
    main()
