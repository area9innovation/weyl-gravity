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

AUTHORITY_PATHS = {
    "intersection_cube": "foundations/results/FOUNDATIONAL_INTERSECTION_CUBE_V4.json",
    "explorer_snapshot": "foundations/results/FOUNDATIONAL_MATRIX_EXPLORER_SITE_V2.json",
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
    site = loaded["explorer_snapshot"]
    atlas_data = json.loads((ROOT / ATLAS_DATA).read_text())
    dimensions = cube["dimensions"]
    payload = {
        "schema_version": "paper-21-reverse-foundations-claim-map-v1",
        "result_id": "PAPER21_REVERSE_FOUNDATIONS_INTRODUCTION_V1",
        "result_kind": "PROGRAMME_SYNTHESIS_AND_TYPED_CASE_STUDY_MAP",
        "lifecycle": "WORKING_DRAFT",
        "created": "2026-08-12",
        "dependency_tags": [
            "LOCAL-ALGEBRAIC",
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
            "evidence_records": site["counts"]["evidence_records"],
            "axis_options": sum(len(axis["keys"]) for axis in atlas_data["axes"]),
            "implication_nodes": len(atlas_data["graph"]["nodes"]),
            "implication_edges": len(atlas_data["graph"]["edges"]),
            "strength_ladder_levels": len(atlas_data["ladder"]),
            "literature_complete": cube["claim_flags"]["literature_complete"],
            "all_cells_assessed": cube["claim_flags"]["all_576_cells_assessed"],
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
                "authorities": ["intersection_cube", "explorer_snapshot"],
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
        ],
        "claim_flags": {
            "programme_definition_supplied": True,
            "typed_relations_supplied": True,
            "case_study_authorities_pinned": True,
            "static_atlas_appendix_generated": True,
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
            "literature completeness or absence theorems for unmapped cells",
            "representation invariance of the RCA_0 coded-wave upper bound",
            "a complete Lorentzian off-shell BV propagator",
            "a BRST-compatible Hadamard state for the full metric BV complex",
            "renormalized Lorentzian time-ordered products or causal perturbative AQFT",
            "restoration of a Lorentzian quantum master equation",
            "promotion of any quantum lifecycle state",
        ],
        "authorities": authorities,
        "independent_checker": {
            "path": "paper/verify_21_reverse_foundations_claim_map.py",
            "checks": [
                "authority content hashes",
                "authority result identities and dependency tags",
                "atlas counts against source artifacts",
                "generated appendix hash and normalized atlas source",
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
