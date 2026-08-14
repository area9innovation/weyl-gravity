#!/usr/bin/env python3
"""Generate the auditable claim map for paper 21.

The generator imports existing certificates as authorities.  It does not
reproduce their scientific computations.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "paper/21-reverse-foundations-of-physics-claim-map.json"
PAPER = "paper/21-reverse-foundations-of-physics.tex"
APPENDIX = "paper/21-reverse-foundations-of-physics-appendices.tex"
APPENDIX_GENERATOR = "paper/generate_21_reverse_foundations_appendices.py"
ATLAS_DATA = "foundations/site/data.json"
ASSEMBLY_DATA = "foundations/site/assemblies.json"

AUTHORITY_PATHS = {
    "intersection_cube": "foundations/results/FOUNDATIONAL_INTERSECTION_CUBE_V10.json",
    "bt_euclidean_import": "foundations/results/FOUNDATIONAL_BT_EUCLIDEAN_LATTICE_IMPORT_V1.json",
    "bt_free_reconstruction_obstruction": "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_FREE_RECONSTRUCTION_OBSTRUCTION_V1.json",
    "bt_interacting_os_preflight": "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_OS_WITNESS_PREFLIGHT_V1.json",
    "bt_lambda04_os_kernel_obstruction": "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_LAMBDA04_OS_KERNEL_OBSTRUCTION_V1.json",
    "bt_uniform_convexity_obstruction": "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_UNIFORM_CONVEXITY_OBSTRUCTION_V1.json",
    "bt_schwinger_dyson_mode_obstruction": "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_SCHWINGER_DYSON_MODE_OBSTRUCTION_V1.json",
    "bt_bilaplacian_reference_bridge": "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_BILAPLACIAN_REFERENCE_BRIDGE_V1.json",
    "bt_low_mode_uv_schur_obstruction": "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_LOW_MODE_UV_SCHUR_OBSTRUCTION_V1.json",
    "bt_action_weight_virial_obstruction": "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_ACTION_WEIGHT_VIRIAL_OBSTRUCTION_V1.json",
    "bt_affine_virial_action_density": "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_AFFINE_VIRIAL_ACTION_DENSITY_V1.json",
    "bt_orthogonal_hessian_block_obstruction": "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_ORTHOGONAL_HESSIAN_BLOCK_OBSTRUCTION_V1.json",
    "bt_residual_spectrahedral_pushforward": "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_RESIDUAL_SPECTRAHEDRAL_PUSHFORWARD_V1.json",
    "bt_residual_boundary_curvature_obstruction": "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_RESIDUAL_BOUNDARY_CURVATURE_OBSTRUCTION_V1.json",
    "full_surface_gap_audit": "foundations/results/FOUNDATIONAL_FULL_SURFACE_GAP_AUDIT_V1.json",
    "explorer_snapshot": "foundations/results/FOUNDATIONAL_MATRIX_EXPLORER_SITE_V2.json",
    "theory_assembly": "foundations/results/FOUNDATIONAL_THEORY_ASSEMBLY_ATLAS_V1.json",
    "gr_cassini_assembly": "foundations/results/FOUNDATIONAL_GR_CASSINI_MODEL_ASSEMBLY_V1.json",
    "mannheim_ngc3198_assembly": "foundations/results/FOUNDATIONAL_MANNHEIM_NGC3198_MODEL_ASSEMBLY_V1.json",
    "ngc3198_common_fit_comparison": "foundations/results/FOUNDATIONAL_NGC3198_COMMON_FIT_COMPARISON_V1.json",
    "explicit_krein": "foundations/results/FOUNDATIONAL_KREIN_EXPLICIT_J_ZF_V1.json",
    "krein_state_selection": "foundations/results/FOUNDATIONAL_KREIN_STATE_SELECTION_ZF_V1.json",
    "separable_cstar_state_chain": "foundations/results/FOUNDATIONAL_BT_SEPARABLE_STATE_CHAIN_ZF_V1.json",
    "coded_wave": "foundations/results/FOUNDATIONAL_CODED_POLYGONAL_WAVE_RCA0_V1.json",
    "finite_graph_causality": "foundations/results/FOUNDATIONAL_FINITE_GRAPH_WAVE_CAUSALITY_V1.json",
    "finite_bv": "foundations/results/FOUNDATIONAL_FREE_BV_ENERGY2_PRA_SDR_V1.json",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_digest(payload: dict) -> str:
    body = dict(payload)
    body.pop("canonical_digest", None)
    encoded = json.dumps(body, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def load_authority(relative: str) -> tuple[dict, dict]:
    path = ROOT / relative
    data = json.loads(path.read_text())
    record = {
        "path": relative,
        "sha256": sha256(path),
        "result_id": data.get("result_id", data.get("certificate")),
        "lifecycle": data.get("lifecycle", data.get("lifecycle_state")),
        "dependency_tags": data.get("dependency_tags", []),
    }
    return data, record


def build() -> dict:
    loaded: dict[str, dict] = {}
    authorities: dict[str, dict] = {}
    for name, path in AUTHORITY_PATHS.items():
        loaded[name], authorities[name] = load_authority(path)

    cube = loaded["intersection_cube"]
    bt_euclidean = loaded["bt_euclidean_import"]
    bt_free_obstruction = loaded["bt_free_reconstruction_obstruction"]
    bt_interacting_os = loaded["bt_interacting_os_preflight"]
    bt_lambda04_os = loaded["bt_lambda04_os_kernel_obstruction"]
    bt_action_weight = loaded["bt_action_weight_virial_obstruction"]
    bt_affine_virial = loaded["bt_affine_virial_action_density"]
    bt_orthogonal_hessian = loaded["bt_orthogonal_hessian_block_obstruction"]
    bt_residual_pushforward = loaded["bt_residual_spectrahedral_pushforward"]
    bt_residual_curvature = loaded["bt_residual_boundary_curvature_obstruction"]
    site = loaded["explorer_snapshot"]
    gr_cassini = loaded["gr_cassini_assembly"]
    mannheim_ngc3198 = loaded["mannheim_ngc3198_assembly"]
    ngc3198_common_fit = loaded["ngc3198_common_fit_comparison"]
    atlas_data = json.loads((ROOT / ATLAS_DATA).read_text())
    assembly_data = json.loads((ROOT / ASSEMBLY_DATA).read_text())
    evidence = atlas_data["evidence"]
    literature = [entry for entry in evidence.values() if entry["kind"] == "LITERATURE"]
    local_results = [entry for entry in evidence.values() if entry["kind"] == "LOCAL_RESULT"]
    dimensions = cube["dimensions"]
    payload = {
        "schema_version": "paper-21-reverse-foundations-claim-map-v1",
        "result_id": "PAPER21_REVERSE_FOUNDATIONS_INTRODUCTION_V1",
        "result_kind": "PROGRAMME_SYNTHESIS_AND_TYPED_CASE_STUDY_MAP",
        "lifecycle": "WORKING_DRAFT",
        "created": "2026-08-14",
        "dependency_tags": [
            "LOCAL-ALGEBRAIC",
            "EUCLIDEAN-SPECTRAL",
            "REDUCED-MODE",
            "LORENTZIAN-CAUSAL",
        ],
        "paper": {
            "path": PAPER,
            "sha256": sha256(ROOT / PAPER),
            "appendix": {
                "path": APPENDIX,
                "sha256": sha256(ROOT / APPENDIX),
                "source_path": ATLAS_DATA,
                "source_sha256": sha256(ROOT / ATLAS_DATA),
                "source_canonical_digest": atlas_data["canonical_digest"],
                "assembly_source_path": ASSEMBLY_DATA,
                "assembly_source_sha256": sha256(ROOT / ASSEMBLY_DATA),
                "assembly_source_canonical_digest": assembly_data["canonical_digest"],
                "generator_path": APPENDIX_GENERATOR,
                "generator_sha256": sha256(ROOT / APPENDIX_GENERATOR),
            },
        },
        "formal_object": {
            "judgement": "L + S + M + Enc(P) |-[_R] O",
            "coordinates": {
                "L": "logic and inference rules",
                "S": "set, type, or existence theory",
                "M": "mathematical carrier and analytic machinery",
                "Enc(P)": "physical postulates under an explicit encoding",
                "R": "representation of inputs and outputs",
                "O": "one declared theorem-level physical obligation",
            },
            "relation_types": [
                "USED_BY_DISPLAYED_PROOF",
                "SUFFICIENT_OVER_BASE",
                "NECESSARY_OVER_BASE",
                "EQUIVALENT_OVER_BASE",
                "AVOIDED_BY_REFORMULATION",
                "INDEPENDENT_OVER_BASE",
                "UNKNOWN",
            ],
        },
        "atlas_snapshot": {
            "axis_sizes": dimensions["axis_sizes"],
            "cartesian_total": dimensions["cartesian_total"],
            "emitted_cells": dimensions["emitted_cells"],
            "coverage_classified_cells": dimensions["coverage_classified_cells"],
            "migration_pending_cells": dimensions["migration_pending_cells"],
            "emitted_status_counts": dimensions["status_counts"],
            "synthetic_complements": dimensions["cartesian_total"] - dimensions["emitted_cells"],
            "total_not_mapped_in_explorer": site["counts"]["not_mapped"],
            "reviewed_open_gaps": site["counts"]["reviewed_gap"],
            "evidence_records": site["counts"]["evidence_records"],
            "literature_records": len(literature),
            "local_result_records": len(local_results),
            "content_pinned_literature": sum(
                entry["artifact_status"] == "CONTENT_PINNED" for entry in literature
            ),
            "metadata_only_literature": sum(
                entry["artifact_status"] == "METADATA_ONLY" for entry in literature
            ),
            "evidence_records_used_by_matrix": len({
                evidence_id
                for cell in atlas_data["cells"]
                for evidence_id in cell.get("evidence", [])
            }),
            "axis_options": sum(len(axis["keys"]) for axis in atlas_data["axes"]),
            "implication_nodes": len(atlas_data["graph"]["nodes"]),
            "implication_edges": len(atlas_data["graph"]["edges"]),
            "strength_ladder_levels": len(atlas_data["ladder"]),
            "literature_complete": cube["claim_flags"]["literature_complete"],
            "all_cells_assessed": cube["claim_flags"]["all_576_coordinates_assessed"],
            "prototype_assemblies": len(assembly_data["assemblies"]),
            "research_programme_lenses": sum(
                bool(item.get("camp_summary") and item.get("scope_note"))
                for item in assembly_data["assemblies"]
            ),
            "model_scoped_assemblies": len(assembly_data["model_scoped_assemblies"]),
            "gr_cassini_stages": len(gr_cassini["stages"]),
            "gr_cassini_interfaces": len(gr_cassini["interfaces"]),
            "gr_cassini_required_obligations": gr_cassini["applicability_summary"]["required"],
            "gr_cassini_required_obligations_satisfied": gr_cassini["applicability_summary"]["required_satisfied"],
            "gr_cassini_bounded_complete": gr_cassini["assembly_disposition"]["complete_within_declared_scope"],
            "gr_cassini_prediction_inside_reported_band": gr_cassini["empirical_comparison_rail"]["prediction_inside_reported_band"],
            "mannheim_ngc3198_stages": len(mannheim_ngc3198["stages"]),
            "mannheim_ngc3198_interfaces": len(mannheim_ngc3198["interfaces"]),
            "mannheim_ngc3198_endpoint_coarse_gate_passed": mannheim_ngc3198["numerical_reproduction_rail"]["gate_passed"],
            "mannheim_ngc3198_sparc_rms_km_s": mannheim_ngc3198["empirical_comparison_rail"]["unweighted_rms_residual_km_s"],
            "mannheim_ngc3198_sparc_reduced_chi2": mannheim_ngc3198["empirical_comparison_rail"]["reduced_chi_squared_no_refit"],
            "mannheim_ngc3198_sparc_coarse_gate_passed": mannheim_ngc3198["empirical_comparison_rail"]["coarse_rms_gate_passed"],
            "mannheim_ngc3198_sparc_random_error_gate_passed": mannheim_ngc3198["empirical_comparison_rail"]["random_error_reduced_chi2_gate_passed"],
            "mannheim_ngc3198_empirically_supported": mannheim_ngc3198["assembly_disposition"]["empirically_supported_within_declared_scope"],
            "ngc3198_common_fit_models": len(ngc3198_common_fit["models"]),
            "ngc3198_common_fit_ranking_AICc": ngc3198_common_fit["ranking_by_AICc"],
            "ngc3198_common_fit_random_error_passes": [item["model_id"] for item in ngc3198_common_fit["models"] if item["random_error_gate"]["passed"]],
            "ngc3198_common_fit_complete_theory_selected": ngc3198_common_fit["claim_flags"]["complete_theory_selected"],
            "bt_euclidean_direct_capabilities": sum(item["evidence_role"] == "DIRECT_LOCAL" for item in bt_euclidean["capability_decisions"]),
            "bt_euclidean_reconstruction_status": next(item["new_status"] for item in bt_euclidean["capability_decisions"] if item["coordinate"]["obligation"] == "RECONSTRUCTION_LIMITS"),
            "bt_euclidean_numerical_status": bt_euclidean["numerical_reproducibility_records"][0]["status"],
            "bt_euclidean_carrier_relation": bt_euclidean["carrier_interface"]["relation"],
            "bt_free_os_reflected_norm": bt_free_obstruction["finite_volume_os_obstruction"]["four_dimensional_slice_average_reflected_norm"],
            "bt_free_os_near_zero_status": bt_free_obstruction["disposition"]["ordinary_os_reflection_positivity_near_lambda_zero"],
            "bt_free_os_lambda_0p4_status": bt_free_obstruction["disposition"]["ordinary_os_reflection_positivity_at_lambda_0p4"],
            "bt_free_h_minus_one_bound": bt_free_obstruction["free_volume_uniform_estimate"]["uniform_result"]["bound"],
            "bt_free_l2_status": bt_free_obstruction["disposition"]["free_uniform_l2_estimate"],
            "bt_interacting_os_numerical_status": bt_interacting_os["disposition"]["lambda_0p4_reflected_witness"],
            "bt_interacting_os_local_z": bt_interacting_os["algorithm_summaries"]["local_metropolis"]["z_from_zero"],
            "bt_interacting_os_hmc_z": bt_interacting_os["algorithm_summaries"]["hmc"]["z_from_zero"],
            "bt_interacting_os_cross_sampler_z": bt_interacting_os["cross_sampler_mean_z"],
            "bt_lambda_0p4_exact_os_status": bt_lambda04_os["disposition"]["ordinary_os_reflection_positivity_at_lambda_0p4"],
            "bt_interacting_uniform_h_minus_one_status": bt_action_weight["method_disposition"]["actual_interacting_h_minus_one_second_moment_bound"],
            "bt_pointwise_action_weight_necessary_exponent": "AT_LEAST_ONE_HALF",
            "bt_pointwise_virial_constant_two_status": bt_action_weight["radial_virial_obstruction"]["status"],
            "bt_affine_virial_status": bt_affine_virial["method_disposition"]["affine_pointwise_virial_bound"],
            "bt_actual_action_density_status": bt_affine_virial["method_disposition"]["actual_uniform_action_density_moment"],
            "bt_actual_half_action_factor_status": bt_affine_virial["method_disposition"]["actual_annealed_half_action_density_factor"],
            "bt_lambda_0p4_action_density_bound": bt_affine_virial["actual_gibbs_action_density"]["lambda_point_four_uniform_action_density_bound"],
            "bt_global_orthogonal_hessian_block_status": bt_orthogonal_hessian["method_disposition"]["global_orthogonal_hessian_block_positivity"],
            "bt_pointwise_half_action_curvature_route_status": bt_orthogonal_hessian["method_disposition"]["pointwise_half_action_curvature_route"],
            "bt_orthogonal_hessian_cell_value": bt_orthogonal_hessian["cell_calculation"]["directional_hessian"],
            "bt_residual_boundary_coordinate_status": bt_residual_pushforward["method_disposition"]["residual_spectrahedral_boundary_coordinates"],
            "bt_residual_tree_jacobian_status": bt_residual_pushforward["method_disposition"]["ground_state_tree_jacobian"],
            "bt_residual_entropy_jacobian_minimum_status": bt_residual_pushforward["method_disposition"]["vertex_transitive_entropy_jacobian_minimum"],
            "bt_residual_cycle_jacobian": bt_residual_pushforward["exact_cycle_fixture"]["restricted_jacobian"],
            "bt_normalized_lowest_mode_marginal_status": bt_residual_pushforward["method_disposition"]["normalized_lowest_mode_marginal_bound"],
            "bt_residual_pointwise_strict_convexity_status": bt_residual_curvature["method_disposition"]["pointwise_strict_convexity"],
            "bt_residual_uniform_curvature_status": bt_residual_curvature["method_disposition"]["uniform_positive_principal_curvature"],
            "bt_residual_weighted_mean_curvature_status": bt_residual_curvature["method_disposition"]["global_positive_gaussian_weighted_mean_curvature"],
            "bt_residual_trial_curvature_q2": bt_residual_curvature["lambda_point_four_fixture"]["trial_normal_curvature"],
            "bt_residual_weighted_mean_curvature_q2": bt_residual_curvature["lambda_point_four_fixture"]["gaussian_weighted_mean_curvature"],
            "standard_reference_direct_obligations": next(item for item in assembly_data["assemblies"] if item["id"] == "STANDARD_MIXED_REFERENCE")["coverage"]["direct"],
            "external_calibration_records": len(assembly_data["calibration_controls"][0]["records"]),
            "external_calibration_benchmark_families": sum(item["status"] == "SUPPORTED_CONTROL" for item in assembly_data["calibration_controls"][0]["benchmark_coverage"]),
        },
        "claims": [
            {
                "claim_id": "RF-01-TYPED-JUDGEMENT",
                "statement": "Physical, mathematical, foundational, and representational assumptions must be typed before implication strength is assigned.",
                "status": "PROGRAMME_DEFINITION",
                "authorities": [],
                "dependency_tags": ["LOCAL-ALGEBRAIC"],
            },
            {
                "claim_id": "RF-02-NAVIGATIONAL-ATLAS",
                "statement": "The current 6 x 6 x 16 atlas is a navigational projection with 576 coordinates, not an ontology or an independence theorem.",
                "status": "CORPUS_SYNTHESIS",
                "authorities": ["intersection_cube", "full_surface_gap_audit", "explorer_snapshot"],
                "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE", "LORENTZIAN-CAUSAL"],
            },
            {
                "claim_id": "RF-03-EXPLICIT-KREIN-ZF",
                "statement": "The displayed named reduced-mode Krein carrier and Fock lift are constructible in ZF without a Countable Choice operation; finite cutoffs are PRA-checkable.",
                "status": "SUFFICIENT_OVER_BASE",
                "authorities": ["explicit_krein"],
                "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
            },
            {
                "claim_id": "RF-04-STATE-SELECTION-SPLIT",
                "statement": "Explicit normalized states exist in the displayed ZF carrier, but the fundamental symmetry does not select a unique physical state; the normal permutation-invariant density-state obstruction is scoped to its stated symmetry class.",
                "status": "SUFFICIENCY_AND_SCOPED_OBSTRUCTION",
                "authorities": ["krein_state_selection", "separable_cstar_state_chain"],
                "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
            },
            {
                "claim_id": "RF-05-CODED-WAVE-RCA0",
                "statement": "RCA_0 suffices for the represented coded-circle wave evolution, uniqueness, group law, and energy conservation with supplied fast Cauchy rates.",
                "status": "SUFFICIENT_OVER_BASE",
                "authorities": ["coded_wave"],
                "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
            },
            {
                "claim_id": "RF-06-EVOLUTION-CAUSALITY-SPLIT",
                "statement": "The coded evolution result does not construct advanced or retarded Green maps or prove continuum causal support.",
                "status": "DOES_NOT_ESTABLISH",
                "authorities": ["coded_wave"],
                "dependency_tags": ["REDUCED-MODE", "LORENTZIAN-CAUSAL"],
            },
            {
                "claim_id": "RF-07-FINITE-CONTINUUM-SPLIT",
                "statement": "Exact graph-step causal support is certified for a finite rational recurrence and is not a continuum Lorentzian causal theorem.",
                "status": "LOCAL_RESULT_WITH_BOUNDARY",
                "authorities": ["finite_graph_causality"],
                "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE", "LORENTZIAN-CAUSAL"],
            },
            {
                "claim_id": "RF-08-FINITE-BV-BOUNDARY",
                "statement": "One explicitly presented finite energy-two BV contraction is PRA-checkable; this does not establish an infinite classical freeze or a quantum promotion.",
                "status": "SUFFICIENT_OVER_BASE",
                "authorities": ["finite_bv"],
                "dependency_tags": ["LOCAL-ALGEBRAIC"],
            },
            {
                "claim_id": "RF-09-GR-CASSINI-ASSEMBLY",
                "statement": "For the declared standard-GR solar-vacuum model, the exact field-equation-to-null-delay chain gives gamma=1 and the resulting prediction lies inside the publisher's displayed Cassini band; the operational and empirical joins remain literature-scoped.",
                "status": "MODEL_SCOPED_EMPIRICAL_COMPARISON",
                "authorities": ["gr_cassini_assembly"],
                "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
            },
            {
                "claim_id": "RF-10-BT-EUCLIDEAN-LATTICE",
                "statement": "The positive finite BT Euclidean lattice supplies five direct finite-volume capabilities and a coarse independent-sampler reproduction record; reconstruction remains open, and its full nonperturbative carrier is not identical to the all-real BT/Krein carrier.",
                "status": "LOCAL_RESULT_WITH_NUMERICAL_AND_CARRIER_BOUNDARIES",
                "authorities": ["bt_euclidean_import"],
                "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
            },
            {
                "claim_id": "RF-11-BT-FREE-RECONSTRUCTION-OBSTRUCTION",
                "statement": "On the zero-mode-fixed 6^4 free BT lattice, a shift-invariant positive-time slice observable has exact reflected norm -1/1296; fixed-volume continuity extends the ordinary-OS obstruction to some open coupling interval around zero, while lambda=0.4 remains open. The free L^4 family has a uniform H^-1 second-moment bound 15/32 and a logarithmically divergent L2 second moment.",
                "status": "SCOPED_OS_OBSTRUCTION_AND_FREE_UNIFORM_ESTIMATE",
                "authorities": ["bt_free_reconstruction_obstruction"],
                "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
            },
            {
                "claim_id": "RF-12-BT-INTERACTING-OS-PREFLIGHT",
                "statement": "At lambda=0.4 on 6^4, all eight independent HMC and local-Metropolis chain means for the reflected witness are negative; equal-replica scores are -6.25 and -2.53 standard errors and the algorithm means differ by 0.64 combined standard errors. This numerical result is supporting only; the separate exact kernel certificate decides ordinary OS positivity.",
                "status": "NUMERICAL_FINITE_VOLUME_SUPPORTING_EXACT_OBSTRUCTION",
                "authorities": ["bt_interacting_os_preflight"],
                "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
            },
            {
                "claim_id": "RF-13-BT-INTERACTING-RECONSTRUCTION-FRONTIER",
                "statement": "At lambda=0.4 on the 6^4 lattice, an exact two-point reflected density-kernel minor obstructs ordinary OS positivity. The affine virial theorem proves a volume-uniform actual Gibbs action-density bound and annealed half-action factor. Exact period-four data obstruct the global Schur route. The residual map identifies positive fields modulo scale with a Schrödinger spectrahedral boundary and gives the exact normalized Gaussian-surface/tree-Jacobian pushforward. That boundary is pointwise strictly convex, but an exact C4 family has trial curvature tending to zero and negative Gaussian weighted mean curvature at lambda=0.4, obstructing the standard uniform positive-curvature spectral-gap route. The lowest log-ground-state marginal and actual interacting H^-1 moment remain open.",
                "status": "EXACT_FINITE_OS_HESSIAN_AND_BOUNDARY_CURVATURE_ROUTE_OBSTRUCTIONS_WITH_ACTION_DENSITY_AND_NORMALIZED_RESIDUAL_REFORMULATION",
                "authorities": [
                    "bt_lambda04_os_kernel_obstruction",
                    "bt_uniform_convexity_obstruction",
                    "bt_schwinger_dyson_mode_obstruction",
                    "bt_bilaplacian_reference_bridge",
                    "bt_low_mode_uv_schur_obstruction",
                    "bt_action_weight_virial_obstruction",
                    "bt_affine_virial_action_density",
                    "bt_orthogonal_hessian_block_obstruction",
                    "bt_residual_spectrahedral_pushforward",
                    "bt_residual_boundary_curvature_obstruction",
                ],
                "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
            },
            {
                "claim_id": "RF-14-MANNHEIM-NGC3198-ASSEMBLY",
                "statement": "For the declared Mannheim--Kazanas NGC 3198 thin-disk model, independent evaluation coarsely reproduces the paper's endpoint and passes a no-refit SPARC RMS gate, but fails the declared reduced-chi-squared gate from SPARC random errors alone; the mixed comparison does not establish empirical support.",
                "status": "NUMERICAL_REPRODUCTION_WITH_MIXED_CROSS_DATASET_COMPARISON",
                "authorities": ["mannheim_ngc3198_assembly"],
                "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
            },
            {
                "claim_id": "RF-15-NGC3198-COMMON-FIT-CONTROL",
                "statement": "Under one bounded NGC 3198 protocol with common velocities and analytic baryonic geometry, GR plus NFW has the lowest AICc and is the only tested family passing the declared random-error gate; this does not select a complete theory or generalize beyond one galaxy.",
                "status": "BOUNDED_SINGLE_GALAXY_COMMON_PROTOCOL_MODEL_COMPARISON",
                "authorities": ["ngc3198_common_fit_comparison"],
                "dependency_tags": ["LOCAL-ALGEBRAIC"],
            },
        ],
        "literature_scope": [
            {"source_id": "simpson-2009", "url": "https://doi.org/10.1017/CBO9780511581007", "role": "reverse mathematics and subsystem calibration"},
            {"source_id": "carcassi-aidala-2022", "url": "https://doi.org/10.1007/s10701-022-00555-z", "role": "reverse physics"},
            {"source_id": "hardy-2001", "url": "https://arxiv.org/abs/quant-ph/0101012", "role": "operational reconstruction and continuity"},
            {"source_id": "chiribella-dariano-perinotti-2011", "url": "https://doi.org/10.1103/PhysRevA.84.012311", "role": "informational reconstruction and purification"},
            {"source_id": "blackadar-farah-karagila-2023", "url": "https://arxiv.org/abs/2304.09602", "role": "Hilbert spaces in ZF without Countable Choice"},
            {"source_id": "blackadar-farah-2026", "url": "https://arxiv.org/abs/2602.15812", "role": "separable C*-algebras in ZF"},
            {"source_id": "coquand-spitters-2009", "url": "https://doi.org/10.1017/S0305004109002515", "role": "constructive Gelfand duality"},
            {"source_id": "heunen-landsman-spitters-2009", "url": "https://arxiv.org/abs/0709.4364", "role": "topos algebraic quantum theory"},
            {"source_id": "gibbons-hoffman-wootters-2004", "url": "https://arxiv.org/abs/quant-ph/0401155", "role": "finite-field phase-space construction"},
            {"source_id": "baer-2015", "url": "https://arxiv.org/abs/1310.0738", "role": "classical Green-hyperbolic theory"},
            {"source_id": "weihrauch-zhong-2006", "url": "https://doi.org/10.1137/S0097539704446360", "role": "computable fundamental solutions"},
            {"source_id": "pischke-2025", "url": "https://arxiv.org/abs/2304.01723", "role": "proof mining for nonlinear semigroups"},
            {"source_id": "bertotti-iess-tortora-2003", "url": "https://doi.org/10.1038/nature01997", "role": "standard-GR solar-system positive control"},
            {"source_id": "kramer-et-al-2021", "url": "https://doi.org/10.1103/PhysRevX.11.041050", "role": "standard-GR compact-binary positive control"},
            {"source_id": "lvk-gwtc3-2021", "url": "https://arxiv.org/abs/2112.06861", "role": "standard-GR gravitational-wave positive control"},
            {"source_id": "abbott-et-al-gw170817-2017", "url": "https://arxiv.org/abs/1710.05834", "role": "standard-GR multimessenger propagation positive control"},
            {"source_id": "mannheim-obrien-2012", "url": "https://arxiv.org/abs/1011.3495", "role": "published conformal-gravity rotation-curve equations and NGC 3198 parameter row"},
            {"source_id": "lelli-mcgaugh-schombert-2016", "url": "https://astroweb.case.edu/SPARC/", "role": "official later SPARC NGC 3198 cross-dataset rotation curve"},
        ],
        "claim_flags": {
            "programme_definition_supplied": True,
            "typed_relations_supplied": True,
            "case_study_authorities_pinned": True,
            "static_atlas_appendix_generated": True,
            "complete_evidence_register_generated": True,
            "complete_literature_register_generated": True,
            "evidence_usage_crosswalk_generated": True,
            "model_scoped_end_to_end_assembly_generated": True,
            "bounded_empirical_comparison_registered": True,
            "mannheim_ngc3198_mixed_assembly_registered": True,
            "ngc3198_common_fit_comparison_registered": True,
            "bt_euclidean_finite_capabilities_imported": True,
            "bt_euclidean_coarse_reproduction_separated": True,
            "bt_free_os_obstruction_certified": True,
            "bt_free_h_minus_one_estimate_certified": True,
            "bt_lambda_0p4_os_status_decided": True,
            "bt_lambda_0p4_two_sampler_sign_support": True,
            "bt_interacting_uniform_h_minus_one_established": False,
            "bt_half_action_density_candidate_established": False,
            "bt_actual_interacting_action_density_established": True,
            "bt_actual_annealed_half_action_factor_established": True,
            "bt_global_orthogonal_hessian_block_obstructed": True,
            "bt_pointwise_half_action_curvature_route_obstructed": True,
            "bt_residual_spectrahedral_pushforward_established": True,
            "bt_vertex_transitive_entropy_jacobian_minimum_established": True,
            "bt_normalized_lowest_mode_marginal_established": False,
            "bt_residual_pointwise_strict_convexity_established": True,
            "bt_residual_uniform_positive_curvature_established": False,
            "bt_residual_positive_weighted_mean_curvature_established": False,
            "bt_standard_boundary_curvature_spectral_gap_route_obstructed": True,
            "research_programme_lenses_explained": True,
            "weakest_foundation_proved": False,
            "global_physics_implies_choice_theorem": False,
            "axes_independent_proved": False,
            "atlas_exhaustive": False,
            "literature_complete": False,
            "new_lorentzian_claim": False,
            "quantum_lifecycle_promoted": False,
        },
        "does_not_establish": [
            "a universal weakest foundation for physics or Weyl gravity",
            "that physical evidence implies the Axiom of Choice or its negation",
            "that the atlas axes are independent or every coordinate is coherent",
            "literature completeness or absence theorems for reviewed open gaps",
            "representation invariance of the RCA_0 coded-wave upper bound",
            "a complete Lorentzian off-shell BV propagator",
            "a BRST-compatible Hadamard state for the full metric BV complex",
            "renormalized Lorentzian time-ordered products or causal perturbative AQFT",
            "restoration of a Lorentzian quantum master equation",
            "promotion of any quantum lifecycle state",
            "reproduction of the Cassini raw-data reduction, likelihood, covariance analysis, or systematic-error budget",
            "a complete standard-GR theory or empirical support for a Weyl-gravity model",
            "a population-level model ranking or complete-theory selection from the NGC 3198 common-fit control",
            "a continuum, empirical, Born-rule, or Lorentzian promotion from the BT Euclidean finite lattice",
            "reflection-positivity failure at every nonzero coupling or in a continuum limit",
        ],
        "authorities": authorities,
        "independent_checker": {
            "path": "paper/verify_21_reverse_foundations_claim_map.py",
            "checks": [
                "authority content hashes",
                "authority result identities and dependency tags",
                "atlas counts against source artifacts",
                "generated appendix hash and normalized atlas source",
                "complete literature citations, URLs, artifact statuses, roles, and boundaries",
                "complete local-certificate locators, positive flags, dependency tags, and boundaries",
                "all-record matrix, graph, and strength-ladder usage crosswalk",
                "claim-to-authority dependency boundaries",
                "required paper language and bibliography keys",
                "canonical claim-map digest",
            ],
        },
    }
    payload["canonical_digest"] = canonical_digest(payload)
    return payload


def render(payload: dict) -> str:
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    expected = render(build())
    if args.check:
        if not OUTPUT.exists() or OUTPUT.read_text() != expected:
            raise SystemExit(f"stale generated artifact: {OUTPUT.relative_to(ROOT)}")
        print(f"PASS {OUTPUT.relative_to(ROOT)} is current")
        return 0
    OUTPUT.write_text(expected)
    print(f"wrote {OUTPUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
