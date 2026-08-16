#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from foundations.build_matrix_site_v2 import generated
from foundations.check_matrix_site_v2 import check

RESULT = ROOT / "foundations/results/FOUNDATIONAL_MATRIX_EXPLORER_SITE_V2.json"
SCHEMA = ROOT / "foundations/schema/foundational-matrix-explorer-site-v2.schema.json"
REPORT = ROOT / "foundations/reports/matrix-explorer-site-v2.md"
MANIFEST = ROOT / "foundations/site/manifest.json"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def verify(*, result=None, report=None) -> tuple[list[str], list[str]]:
    value = load(RESULT) if result is None else result
    text = REPORT.read_text() if report is None else report
    errors: list[str] = []
    checks: list[str] = []
    errors.extend("schema " + error.message for error in Draft202012Validator(load(SCHEMA), format_checker=FormatChecker()).iter_errors(value))
    checks.append("Draft 2020-12 result schema")
    checker_errors, summary = check()
    errors.extend("checker " + error for error in checker_errors)
    expected_summary = {
        "digest": value.get("provenance", {}).get("canonical_data_digest"),
        "cells": 576,
        "emitted": 576,
        "synthetic_not_mapped": 0,
        "total_not_mapped": 0,
        "coverage_classified": 576,
        "migration_reviewed": 576,
        "migration_pending": 0,
        "reviewed_no_transfer": 88,
        "evidence_records": 83,
        "graph_edges": 10,
        "ladder_levels": 6,
        "completion_branches": 7,
        "completion_stages": 11,
        "completion_cells": 77,
        "completion_routes": 7,
        "completion_decisions": 11,
        "theory_profiles": 36,
        "carrier_envelopes": 6,
        "pareto_profiles": 4,
        "prototype_assemblies": 9,
        "assembly_interfaces": 63,
        "empirical_comparisons": 0,
        "calibration_comparisons": 4,
        "calibration_benchmark_families": 3,
        "model_scoped_assemblies": 2,
        "model_scoped_stages": 13,
        "model_scoped_interfaces": 11,
        "bounded_complete_assemblies": 1,
        "certified_cross_cell_interfaces": 2,
        "certified_carrier_interfaces": 1,
        "numerical_reproduction_records": 1,
        "certified_assembly_interface_instances": 5,
        "dual_direct_cells": 8,
        "mark_counts": {"G": 28, "Gl": 2, "L": 112, "LR": 8, "Lr": 7, "Ol": 169, "P": 19, "Pl": 78, "Plr": 12, "Pr": 51, "R": 87, "Rl": 3},
    }
    if summary != expected_summary:
        errors.append("expected independent summary")
    checks.append("independent full-surface, migration, and evidence audit")
    for path, content in generated().items():
        if not path.is_file() or path.read_bytes() != content:
            errors.append("deterministic drift " + str(path.relative_to(ROOT)))
    checks.append("deterministic static build")
    if hashlib.sha256(MANIFEST.read_bytes()).hexdigest() != value.get("provenance", {}).get("manifest_sha256"):
        errors.append("manifest pin")
    checks.append("content-addressed manifest")
    flags = value.get("claim_flags", {})
    for key in ("static_site_generated", "all_cartesian_coordinates_visible", "all_cartesian_coordinates_assessed", "zero_not_mapped", "reviewed_gaps_distinguished_from_results", "all_emitted_migrations_reviewed", "coverage_and_migration_separated", "all_used_evidence_resolved", "theory_profiles_generated", "theory_assembly_atlas_generated", "bounded_observable_reconstruction_exposed", "localized_coefficient_weak_wave_exposed", "named_h2_test_completion_exposed", "smooth_to_h2_translator_exposed", "support_indexed_test_comparison_exposed", "scalar_green_choice_audit_exposed", "strict_candidate_q2_green_first_response_exposed", "strict_candidate_q2_green_foundations_exposed", "strict_candidate_polarized_finite_trees_exposed", "strict_first_mixed_sign_domain_nondefinition_exposed", "at_least_one_cross_cell_interface_certified", "composition_and_observation_rails_separated", "new_lorentzian_claim"):
        if flags.get(key) is not True:
            errors.append("positive flag " + key)
    if flags.get("completion_atlas_exposed") is not True:
        errors.append("positive flag completion_atlas_exposed")
    for key in ("proof_passports_exposed", "minimal_arity_three_finite_replay_exposed"):
        if flags.get(key) is not True:
            errors.append("positive flag " + key)
    for key in (
        "strict_authoritative_q2_green_compatibility_exposed",
        "strict_recursive_nonlinear_green_trees_exposed",
        "strict_386_full_brst_hadamard_two_point_exposed",
        "strict_386_full_brst_ward_exposed",
    ):
        if flags.get(key) is not True:
            errors.append("positive flag " + key)
    for key in ("strict_386_known_required_cubic_families_enumerated", "strict_386_vv_bv_cotangent_lift_canonical", "strict_386_hh_hv_bv_cotangent_lift_component_complete", "strict_386_full_bv_cotangent_lift_serialized", "strict_386_full_quadratic_bv_cotangent_lift_serialized", "strict_386_diff_bv_representation_component_complete", "strict_386_exhaustive_full_nonlinear_bv_family_census", "strict_nonlinear_weyl_boost_ghost_manifest_complete", "strict_386_full_source_q2_assembled", "strict_386_diff_cstar_v2_repair_exposed", "strict_386_source_q2_common_hash_accepted", "strict_386_full_q1_q2_identity_exposed", "strict_386_full_q2_cyclicity_exposed", "strict_386_full_D_q2_derivation_exposed", "strict_386_full_source_q2_pullback_replayed", "strict_authoritative_q3_imported", "strict_386_authoritative_full_q3_imported", "strict_386_full_arity_three_identity_exposed", "strict_386_full_q3_cyclicity_exposed", "strict_386_full_D_q3_derivation_exposed", "strict_386_full_source_q3_pullback_replayed", "strict_M1A2_local_semantic_extension_exposed", "strict_local_386_fully_typed_exposed"):
        if flags.get(key) is not True:
            errors.append("positive flag " + key)
    for key in ("strict_field_equation_green_component_exposed", "strict_field_equation_quotient_inverse_exposed", "strict_ungauge_fixed_full_inverse_obstruction_exposed"):
        if flags.get(key) is not True:
            errors.append("positive flag " + key)
    for key in ("strict_residual_zero_mode_payload_exposed", "strict_centered_cohomology_payload_exposed", "strict_residual_sdr_type_audit_exposed", "strict_graph_endpoint_sdr_support_local_exposed", "strict_m3_typed_split_exposed", "strict_m3l_common_endpoint_sdr_binding_exposed", "strict_m3r_typed_residual_comparison_exposed", "strict_M3R_represented_dfinite_comparison_exposed", "strict_current_470_induced_odd_pairing_rank_zero_exposed", "strict_finite_940_cotangent_preflight_exposed"):
        if flags.get(key) is not True:
            errors.append("positive flag " + key)
    for key in ("strict_q2_only_lambda2_source_obstruction_exposed", "strict_authoritative_q3_cancellation_target_exposed", "strict_pure_weyl_q3_witness_cancellation_exposed", "strict_lambda2_witness_full_source_closure_exposed", "strict_authoritative_minimal_q3_imported", "strict_minimal_arity_three_identity_exposed", "strict_minimal_q3_cyclicity_exposed", "strict_386_candidate_q3_stabilized", "strict_386_candidate_arity_three_identity_exposed", "strict_386_candidate_q3_cyclicity_exposed", "strict_386_candidate_D_q3_derivation_exposed", "strict_386_literal_trivial_stabilization_identity_refuted", "strict_386_linear_shear_theory_identity_refuted", "strict_386_candidate_internal_identities_preserved", "strict_386_nonlinear_equivalence_may_exist", "strict_M3RC_dual_comparison_maps_exposed", "strict_M4R_residual_cyclicity_exposed", "strict_M1_preflight_exposed", "strict_M1_typed_diagram_exposed", "strict_M1A3_represented_crosswalk_exposed", "strict_M1A4_ledger_freeze_exposed", "strict_M1A_full_typed_carrier_ledger_exposed", "strict_residual_zero_mode_common_freeze_exposed", "strict_centered_representative_common_freeze_exposed", "strict_M1_common_strict_snapshot_exposed", "strict_M1B_action_dual_lift_exposed", "strict_M1B_typed_cyclic_replay_exposed", "strict_M1B_represented_composite_contraction_exposed", "strict_M1C_common_manifest_replay_exposed", "strict_classical_gate_a_passed"):
        if flags.get(key) is not True:
            errors.append("positive flag " + key)
    for key in ("scientific_claims_duplicated_by_hand", "literature_complete", "unmapped_means_absent", "reviewed_gap_means_absent", "reviewed_no_transfer_means_absent", "priority_score_is_theorem", "complete_observationally_valid_theory_identified", "strict_dfinite_residual_projector_support_local_exposed", "strict_unrestricted_mixed_sign_trees_exposed", "strict_arbitrary_causal_difference_trees_exposed", "strict_infinite_tree_series_convergence_exposed", "strict_typed_field_equation_green_inverse_exposed", "strict_all_order_source_closure_exposed", "strict_386_q3_stabilized", "strict_386_authoritative_nonminimal_equivalence_exposed", "strict_386_candidate_causal_lambda2_source_closure_exposed", "strict_386_nonlinear_equivalence_constructed", "strict_386_nonlinear_equivalence_obstructed", "strict_full_weyl_lambda2_source_closure_exposed", "strict_Berger_q3_direct_import_compatible", "strict_386_positive_hadamard_state_exposed", "strict_386_physical_cohomology_positivity_exposed"):
        if flags.get(key) is not False:
            errors.append("boundary flag " + key)
    for key in ("proof_passports_change_evidence_grades", "minimal_arity_three_natural_operator_proof_formalized"):
        if flags.get(key) is not False:
            errors.append("boundary flag " + key)
    checks.append("fail-closed claim flags")
    for token in ("576", "169 `REVIEWED_GAP`", "0\n`NOT_MAPPED`", "not a result", "selected priority", "literature-absence claim", "all 401 prior", "51 emitted blanks", "124", "without transferring evidence", "exactly twenty additional empty cells", "seventeen", "three pieces-only", "classification before QME restoration", "none of those toy-model statements is a Weyl-BV promotion", "two certified", "CONDITIONAL_BRIDGE", "unique normal", "coarse numerical reproduction", "not empirical validation", "conditional bridges remain open", "N(k)=k+ell(K)+1", "not the full field", "rank-10", "coefficient by coefficient", "not a theorem for\nevery smooth test function", "named H2 completion", "nonmetrizable LF test topology", "representation-to-causality", "retarded and\nadvanced Green maps", "scalar benchmark", "Atlas V47", "arbitrary-input", "386-row", "nine ranked", "eleven-step", "72", "1,392", "3,907", "22", "16", "pairing slices", "212", "S4", "-75760/9", "not an authoritative", "Omega(f_hat,q2(v,v))=-1", "first nonlinear", "full source\npullback", "primary-source", "actual source q2", "accepted common q2 snapshot", "336 exact q1/q2 defects", "Gate V29", "M1B primal", "4,080", "support-expanding", "M1A2", "M1A3", "M1A4", "M1B", "M1C", "17,779", "205 test", "2,560-component", "M3L", "M3R", "M3RC-A", "M3RC-B", "M4L", "M4R", "rank zero", "940-coordinate", "8,980-coordinate", "H1=0", "support-local", "fifteen primal", "120", "ordered C3, C4 and C5", "85,091", "auxiliary quartic mass", "5,952 paired q3 coefficients", "separate coverage and migration", "Earlier cubes remain unchanged", "does not establish"):
        token = {"Atlas V47": "Atlas V49", "nine ranked": "seven ranked", "Gate V29": "Gate V30"}.get(token, token)
        if token not in text:
            errors.append("report token " + token)
    for token in ("Lean/Physlib proof passports", "changing evidence grades"):
        if token not in text:
            errors.append("report proof-passport token " + token)
    checks.append("human-readable migration and deployment report")
    return errors, checks


def main() -> int:
    errors, checks = verify()
    print("FOUNDATIONAL_MATRIX_EXPLORER_SITE_V2: " + ("PASS" if not errors else "FAIL"))
    for item in checks if not errors else errors:
        print("  - " + item)
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
