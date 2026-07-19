"""Certify the complete coefficientwise candidate-13 mixed tangent cone."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_candidate13_complete_mixed_cone.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_ell2_two_abs_momentum_candidate13_complete_mixed_cone.schema.json"
INPUTS = {
    "candidate13_incidence": ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_candidate13_L4_incidence_reduction.json",
    "same_fibre_census": ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_candidate13_same_fibre_resonance_census.json",
    "finite_generic_cone": ROOT / "bridge/certificates/einstein_maxwell_weyl_finite_generic_smooth_global_second_order.json",
    "isolated_cross_fibre_candidates": ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_isolated_candidates.json",
    "pure_extra_taub_join": ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_candidate13_pure_extra_taub_join.json",
    "mixed_bounded_witness": ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_candidate13_mixed_bounded_extension.json",
    "pressure_obstruction": ROOT / "bridge/certificates/einstein_maxwell_weyl_candidate13_mixed_pressure_obstruction.json",
    "bounded_zero_block": ROOT / "bridge/certificates/einstein_maxwell_weyl_finite_generic_bounded_zero_block.json",
    "candidate13_zero_block": ROOT / "bridge/certificates/einstein_maxwell_weyl_candidate13_bounded_zero_frequency_decomposition.json",
    "scalar_separation": ROOT / "bridge/certificates/einstein_maxwell_weyl_candidate13_scalar_separation_no_go.json",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(value: bool, message: str) -> None:
    if not value:
        raise AssertionError(message)


def build() -> dict[str, object]:
    records = {name: json.loads(path.read_text(encoding="utf-8")) for name, path in INPUTS.items()}
    incidence = records["candidate13_incidence"]
    same = records["same_fibre_census"]
    generic = records["finite_generic_cone"]
    isolated = records["isolated_cross_fibre_candidates"]
    pure = records["pure_extra_taub_join"]
    witness = records["mixed_bounded_witness"]
    pressure = records["pressure_obstruction"]
    zero_block = records["bounded_zero_block"]
    candidate13_zero = records["candidate13_zero_block"]
    separation = records["scalar_separation"]

    require(incidence["classification"]["candidate_13_ideal_prime"], "candidate-13 cross-fibre ideal changed")
    require(incidence["prime_zero_variety_theorem"]["equation_count"] == 18, "candidate-13 equation count changed")
    require(same["classification"]["candidate_13_all_nonzero_same_fibre_channels_off_shell"], "same-fibre census changed")
    require(not same["classification"]["same_fibre_nonzero_frequency_source_matrices_required_for_bounded_gate"], "same-fibre gate reopened")
    require(generic["classification"]["complete_reduced_adjoint_cokernel_decomposition_certified"], "generic cokernel theorem changed")
    require(not generic["classification"]["bounded_resonance_zero_locus_solved"], "generic bounded gate unexpectedly closed")
    require(isolated["classification"]["twenty_one_distinct_admissible_candidates"], "cross-fibre isolation changed")
    require(pure["classification"]["candidate_13_resonance_Taub_common_zero_is_origin"], "pure-extra face changed")
    require(witness["classification"]["candidate_13_mixed_witness_bounded_second_order_obstructed"], "mixed bounded obstruction changed")
    require(witness["classification"]["candidate_13_mixed_witness_smooth_second_order_extendible"], "mixed smooth point changed")
    require(pressure["classification"]["candidate13_bounded_pressure_functional_nonzero"], "bounded pressure functional changed")
    require(zero_block["classification"]["five_stabilizers_plus_circle_pressure_complete_on_finite_generic_zero_block"], "bounded zero-block theorem changed")
    require(zero_block["classification"]["bounded_zero_frequency_necessity_and_sufficiency_certified"], "bounded zero-block sufficiency changed")
    require(candidate13_zero["classification"]["complete_candidate13_bounded_zero_frequency_receiver_certified"], "candidate-13 bounded zero-block specialization changed")
    require(candidate13_zero["classification"]["five_stabilizers_plus_circle_pressure_necessary_and_sufficient"], "candidate-13 zero-block sufficiency changed")
    require(separation["classification"]["candidate13_complete_bounded_cone_is_origin"], "candidate-13 scalar separation changed")
    require(not separation["classification"]["candidate13_nonzero_bounded_point_exists"], "candidate-13 bounded point unexpectedly appeared")

    normal_equations = incidence["pencil_reduction"]["normal_form_equations"]
    return {
        "schema": "einstein-maxwell-weyl-ell2-two-abs-momentum-candidate13-complete-mixed-cone-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": sha(SCHEMA),
        "result_id": "EINSTEIN_MAXWELL_WEYL_ELL2_TWO_ABS_MOMENTUM_CANDIDATE13_COMPLETE_MIXED_CONE",
        "result_state": "CANDIDATE13_BOUNDED_CONE_IS_ORIGIN_AND_SMOOTH_CONE_IS_FIVE_MOMENT_MAP_ZERO_SET",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "generality_level": "G4_COMPLETE_FINITE_CANDIDATE13_GENERIC_TWO_FIBRE_CARRIER",
        "scope": {
            "theory": "Weyl-Maxwell target",
            "background": "candidate-13 tuned compact magnetically supported Plebanski-Hacyan product",
            "boundaries": "closed S1_L times S2 before final residual quotient",
            "charge_sector": "fixed magnetic U(1) bundle P_N with N=2",
            "carrier": "all generic ell=2 q-minus, p-extra and q-plus positive-frequency coefficients on the signed candidate-13 n=1 and n=-2 collision fibres, both parities and every m, with reality conjugates",
            "degree": 2,
            "parity": "both axial and polar inputs and all selected output parities",
            "ell": "input ell=2; every quadratic output L=0,1,2,3,4",
            "m": "all m=-2,...,2 and every Clebsch-Gordan-allowed output M",
            "k": "signed n=1 and n=-2 candidate-13 fibres and their reality conjugates",
            "omega": "all q-minus, p-extra and q-plus positive-frequency shells and all quadratic signed sums",
        },
        "second_order_equation": "L_WM v=-(1/2)D^2E_WM[u,u]",
        "coefficientwise_functionals": {
            "stabilizer": ["mu_H", "mu_Px", "mu_J1", "mu_J2", "mu_J3"],
            "bounded_circle_pressure": {
                "name": "R_c",
                "formula": pressure["primary_action_identity"]["pressure_functional"],
                "description": "independent bounded zero-frequency circle-pressure functional; it is secularly removable but not in the bounded class",
            },
            "candidate13_cross_fibre": {
                "count_over_C": 18,
                "normal_form": normal_equations,
                "description": "the 18 Sym^8(C^2) coefficients of the two displayed binary-octic equations on the p-primary amplitudes; q-primary amplitudes are spectators for this resonance ideal",
                "reality": "the opposite signed-momentum block is the complex conjugate and supplies no independent real equation",
            },
            "same_fibre_nonzero_frequency": "none: all 18 temporal channels are off shell by 144 exact target-shell defects",
            "zero_frequency": "the complete bounded zero-block source map is the five stabilizer moments plus R_c; the formal Wilson-acceleration mean covector has identically zero quadratic source",
        },
        "tangent_cones": {
            "BOUNDED_OR_FINITE_QUASIPERIODIC": {
                "status": "CERTIFIED",
                "formula": "Z2_bounded={u:mu_H=mu_Px=mu_J1=mu_J2=mu_J3=R_c=0 and R_13,1=...=R_13,18=0}",
                "necessity": "the five stabilizer pairings, independent bounded circle pressure, and every candidate-13 shell coefficient must vanish",
                "sufficiency": "the bounded zero-block theorem leaves only the five stabilizers and R_c on generic oscillatory sources; the same-fibre census and isolated-candidate theorem leave only the eighteen cross-fibre coefficients at nonzero frequency",
            },
            "SMOOTH_EXPONENTIAL_POLYNOMIAL": {
                "status": "CERTIFIED",
                "formula": "Z2_smooth={u:mu_H=mu_Px=mu_J1=mu_J2=mu_J3=0}",
                "reason": "the 18 finite-frequency candidate-13 resonances admit certified secular inverses in the smooth exponential-polynomial correction class",
            },
            "CAUSAL_RETARDED": {
                "status": "NO_CERTIFIED_MAP",
                "formula": "NO_CERTIFIED_MAP",
            },
        },
        "geometry": {
            "pure_extra_face": "the bounded and smooth cones meet the declared pure-extra carrier only at the origin because mu_H is negative definite there",
            "bounded_real_zero_locus": "{0}; the exact scalar separator D is strictly positive on every nonzero declared coefficient vector",
            "mixed_nonzero_point": "the axial m=0 three-occupation witness lies in Z2_smooth but not Z2_bounded because R_c<0",
            "cross_fibre_resonance_variety": "the 18 candidate-13 equations alone define one prime complex dimension-22 cone in the 40-dimensional p-primary ambient space",
            "real_moment_map_intersection_decomposed": True,
        },
        "classification": {
            "complete_candidate13_bounded_tangent_cone_formula_certified": True,
            "candidate13_known_bounded_functional_ledger_certified": True,
            "complete_candidate13_bounded_functional_ledger_certified": True,
            "complete_candidate13_smooth_tangent_cone_formula_certified": True,
            "five_stabilizer_pressure_and_eighteen_resonance_functionals_necessary_bounded": True,
            "five_stabilizer_pressure_and_eighteen_resonance_functionals_sufficient_bounded": True,
            "five_stabilizer_functionals_necessary_and_sufficient_smooth": True,
            "same_fibre_nonzero_frequency_source_functionals_absent_after_shell_reduction": True,
            "pure_extra_face_is_origin": True,
            "candidate13_complete_bounded_cone_is_origin": True,
            "nonzero_mixed_bounded_point_exists": False,
            "nonzero_mixed_bounded_point_nonexistence_certified": True,
            "nonzero_mixed_smooth_point_certified": True,
            "real_algebraic_component_decomposition_classified": True,
            "all_orders_integrability": False,
            "causal_residual_observational_or_quantum_claim": False,
        },
        "interpretation": "At candidate 13 the bounded cone collapses to the origin: an exact rational combination of H, P_x and circle pressure is positive definite on the full generic two-fibre carrier. The smooth cone remains the nontrivial five-moment-map zero set because pressure and finite-frequency resonances admit secular inverses.",
        "next_gate": "test whether analogous scalar separators exist at the other collision circumferences and keep exceptional or generalized-zero carriers separate",
        "claim_boundary": "This is a complete bounded-origin and smooth cone theorem on the declared finite generic candidate-13 carrier. It does not include exceptional/global inputs, prove all-orders integration, causal correction, residual or observational descent, or make quantum claims.",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": sha(Path(__file__)),
            "inputs": {name: {"path": str(path.relative_to(ROOT)), "sha256": sha(path)} for name, path in INPUTS.items()},
        },
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_ell2_two_abs_momentum_candidate13_complete_mixed_cone --check",
            "python3 -m bridge.einstein_sector.verify_einstein_maxwell_weyl_ell2_two_abs_momentum_candidate13_complete_mixed_cone",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_ell2_two_abs_momentum_candidate13_complete_mixed_cone",
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
        raise AssertionError("candidate-13 complete mixed-cone certificate is stale")
    print("EINSTEIN_MAXWELL_WEYL_ELL2_TWO_ABS_MOMENTUM_CANDIDATE13_COMPLETE_MIXED_CONE: PASS")


if __name__ == "__main__":
    main()
