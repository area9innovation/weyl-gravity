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
    "full_surface_gap_audit": "foundations/results/FOUNDATIONAL_FULL_SURFACE_GAP_AUDIT_V1.json",
    "explorer_snapshot": "foundations/results/FOUNDATIONAL_MATRIX_EXPLORER_SITE_V2.json",
    "theory_assembly": "foundations/results/FOUNDATIONAL_THEORY_ASSEMBLY_ATLAS_V1.json",
    "gr_cassini_assembly": "foundations/results/FOUNDATIONAL_GR_CASSINI_MODEL_ASSEMBLY_V1.json",
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
        "result_id": data["result_id"],
        "lifecycle": data["lifecycle"],
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
    site = loaded["explorer_snapshot"]
    gr_cassini = loaded["gr_cassini_assembly"]
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
            "bt_euclidean_direct_capabilities": sum(item["evidence_role"] == "DIRECT_LOCAL" for item in bt_euclidean["capability_decisions"]),
            "bt_euclidean_reconstruction_status": next(item["new_status"] for item in bt_euclidean["capability_decisions"] if item["coordinate"]["obligation"] == "RECONSTRUCTION_LIMITS"),
            "bt_euclidean_numerical_status": bt_euclidean["numerical_reproducibility_records"][0]["status"],
            "bt_euclidean_carrier_relation": bt_euclidean["carrier_interface"]["relation"],
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
            "bt_euclidean_finite_capabilities_imported": True,
            "bt_euclidean_coarse_reproduction_separated": True,
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
            "a continuum, empirical, Born-rule, or Lorentzian promotion from the BT Euclidean finite lattice",
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
