#!/usr/bin/env python3
"""Generate the content-addressed receipt for the timeless Paper 00 synthesis."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = "paper/00-ghosts-geometry-reality.tex"
PDF = "paper/00-ghosts-geometry-reality.pdf"
OUTPUT = ROOT / "paper/00-ghosts-geometry-reality-receipt.json"
AUTHORITIES = {
    "theory_passports": "foundations/results/FOUNDATIONAL_END_TO_END_THEORY_PASSPORT_ATLAS_V1.json",
    "theory_assemblies": "foundations/results/FOUNDATIONAL_THEORY_ASSEMBLY_ATLAS_V1.json",
    "ngc3198_comparison": "foundations/results/FOUNDATIONAL_NGC3198_COMMON_FIT_COMPARISON_V1.json",
    "classical_gate_a": "quantum-weyl/classical_import/certificates/CLASSICAL_IMPORT_GATE_V30_RECONCILIATION.json",
    "typed_q2_q3_green": "quantum-weyl/classical_import/certificates/STRICT_M2_Q2_Q3_TYPED_GREEN_COMPATIBILITY_V1.json",
    "hadamard_pseudo_state": "quantum-weyl/lorentzian/certificates/STRICT_386_BRST_HADAMARD_TWO_POINT_V1.json",
    "bt_green_tail": "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_TORUS_GREEN_TAIL_COUNTERFAMILY_V1.json",
    "physlib_source_bridge": "foundations/site/sources/physlib-demo/certificates/PHYSLIB_STRICT_WEYL_SECOND_SOURCE_BRIDGE_V1.json",
    "physlib_finite_replay": "foundations/site/sources/physlib-demo/certificates/PHYSLIB_MINIMAL_ARITY_THREE_FINITE_REPLAY_V1.json",
    "paper12_anomaly_claim_map": "paper/12-pure-weyl-one-loop-bv-anomaly-claim-map.json",
    "paper17_resonance_claim_map": "paper/17-pure-weyl-schwarzschild-extension-structure-claim-map.json",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def load_authorities() -> tuple[dict[str, dict], dict[str, dict]]:
    ledger = {}
    payloads = {}
    for name, relative in AUTHORITIES.items():
        path = ROOT / relative
        payload = json.loads(path.read_text())
        payloads[name] = payload
        ledger[name] = {
            "path": relative,
            "sha256": sha256(path),
            "result_id": payload.get("result_id", payload.get("certificate")),
            "dependency_tags": payload["dependency_tags"],
        }
        boundary = payload.get("does_not_establish")
        if boundary is None:
            boundary = payload.get("explicit_nonclaims", payload.get("headline"))
        ledger[name]["claim_boundary"] = boundary
    return ledger, payloads


def validate_authorities(payloads: dict[str, dict]) -> None:
    passports = payloads["theory_passports"]
    assemblies = payloads["theory_assemblies"]
    comparison = payloads["ngc3198_comparison"]
    gate = payloads["classical_gate_a"]
    green = payloads["typed_q2_q3_green"]
    hadamard = payloads["hadamard_pseudo_state"]
    bt = payloads["bt_green_tail"]
    paper12 = payloads["paper12_anomaly_claim_map"]
    paper17 = payloads["paper17_resonance_claim_map"]

    require(len(passports["passports"]) == 8, "theory-passport count drifted")
    require(len(assemblies["assemblies"]) == 9, "programme-assembly count drifted")

    models = {row["model_id"]: row for row in comparison["models"]}
    expected = {
        "NEWTONIAN_BARYONS_ONLY": (23.896205433040972, 128.72235125034302, False),
        "GR_NFW_DARK_HALO": (5.147987363846723, 0.9652634913239349, True),
        "MANNHEIM_CONFORMAL_GRAVITY": (4.694475967312153, 3.201777683080153, False),
    }
    for model_id, (rms, reduced_chi2, passed) in expected.items():
        row = models[model_id]
        require(row["metrics"]["unweighted_rms_residual_km_s"] == rms, f"RMS drifted: {model_id}")
        require(row["metrics"]["reduced_chi_squared"] == reduced_chi2, f"chi-squared drifted: {model_id}")
        require(row["random_error_gate"]["passed"] is passed, f"empirical gate drifted: {model_id}")

    require(
        gate["result_state"] == "CLASSICAL_IMPORT_GATE_A_VERIFIED_ON_IMMUTABLE_STRICT_PURE_WEYL_SNAPSHOT",
        "Gate-A state drifted",
    )
    require(
        green["result_state"] == "NONLINEAR_GREEN_COMPATIBILITY_AND_SECOND_SOURCE_COCYCLE_CERTIFIED_HADAMARD_OPEN",
        "typed Green frontier drifted",
    )
    require(
        hadamard["result_state"] == "FULL_386_BRST_HADAMARD_TWO_POINT_CERTIFIED_POSITIVE_STATE_OPEN",
        "Hadamard frontier drifted",
    )
    require(
        "a positive quasifree Hadamard state or positive physical graviton Hilbert space"
        in hadamard["does_not_establish"],
        "Hadamard positivity boundary drifted",
    )
    require(bt["research_disposition"]["all_field_torus_scaled_PL"] == "REFUTED", "BT disposition drifted")
    require(
        bt["research_disposition"]["lorentzian_transfer"] == "NOT_ESTABLISHED",
        "BT Lorentzian boundary drifted",
    )
    require(
        paper12["certified_claims"]["strict_one_loop_local_Euclidean_QME_obstructed"] is True,
        "strict anomaly claim drifted",
    )
    require(
        paper12["certified_claims"]["extended_one_loop_local_Euclidean_QME_restored"] is True,
        "changed-theory restoration claim drifted",
    )
    for flag in (
        "certified_qnm_smith_type_0_0_2",
        "exterior_cutoff_green_double_pole",
        "global_ecs_green_double_pole",
        "mode_reduced_retarded_green_operator",
    ):
        require(paper17["claim_flags"][flag] is True, f"Paper 17 claim drifted: {flag}")
    for flag in ("complete_retarded_qnm_expansion", "global_causal_resolvent", "detector_sensitivity"):
        require(paper17["claim_flags"][flag] is False, f"Paper 17 nonclaim drifted: {flag}")


def local_links_and_citations(source: str) -> tuple[list[str], list[str]]:
    links = [target for target in re.findall(r"\\href\{([^}]+)\}", source) if "://" not in target]
    missing = [target for target in links if not (ROOT / "paper" / target).resolve().exists()]
    require(not missing, f"missing local links: {missing}")
    cited = set()
    for group in re.findall(r"\\cite\{([^}]+)\}", source):
        cited.update(key.strip() for key in group.split(","))
    defined = set(re.findall(r"\\bibitem\{([^}]+)\}", source))
    require(not (cited - defined), f"undefined bibliography keys: {sorted(cited - defined)}")
    return links, sorted(cited)


def build() -> dict:
    source = (ROOT / SOURCE).read_text()
    normalized = " ".join(source.split())
    authority_ledger, payloads = load_authorities()
    validate_authorities(payloads)

    required = [
        "An equation is not yet a theory",
        "The ghost question is four questions",
        "full 386-row off-shell carrier admits a BRST--Hadamard two-point pseudo-state pair",
        "Mannheim has the smallest unweighted residual",
        "This refutes one deterministic all-field scaled-PL architecture",
        "The Cartesian product contains \\(6\\times6\\times16=576\\) coordinates",
        "A sign is not a state.",
        "These routes are thematic references, not a sequence of release notes.",
    ]
    forbidden = [
        "Public pre-release, July 2026",
        "The newest results concern Schwarzschild black holes",
        "Authorship, accountability, and status",
        "What the first six papers establish",
        "\\section{Paper map}",
        "\\section{What remains open}",
        "\\textbf{Current verdict.}",
        "The most important next steps are now narrower",
        "eighteen-paper programme",
        "Papers~16 and~17 contain the current black-hole",
    ]
    for fragment in required:
        require(fragment in normalized, f"required synthesis fragment missing: {fragment}")
    for fragment in forbidden:
        require(fragment not in source, f"changelog fragment survived: {fragment}")

    links, citations = local_links_and_citations(source)
    return {
        "schema_version": "paper-00-timeless-introduction-receipt-v1",
        "result_id": "PAPER_00_TIMELESS_GHOSTS_REVERSE_FOUNDATIONS_SYNTHESIS_V1",
        "result_kind": "CONTENT_ADDRESSED_PUBLIC_SYNTHESIS_AND_CLAIM_BOUNDARY_RECEIPT",
        "lifecycle": "VERIFIED_NAVIGATION_ARTIFACT",
        "created": "2026-08-17",
        "dependency_tags": [
            "LOCAL-ALGEBRAIC",
            "EUCLIDEAN-SPECTRAL",
            "REDUCED-MODE",
            "LORENTZIAN-CAUSAL",
        ],
        "artifacts": {SOURCE: sha256(ROOT / SOURCE), PDF: sha256(ROOT / PDF)},
        "authorities": authority_ledger,
        "local_links": links,
        "bibliography_keys": citations,
        "editorial_checks": {
            "required_synthesis_fragments": len(required),
            "changelog_fragments_rejected": len(forbidden),
            "local_links_resolved": len(links),
            "bibliography_keys_resolved": len(citations),
            "atlas_coordinates": 576,
            "theory_passports": 8,
            "programme_prototypes": 9,
        },
        "claim_flags": {
            "NEW_SCIENTIFIC_THEOREM": False,
            "MATRIX_GRADE_PROMOTED": False,
            "COMPLETE_THEORY_SELECTED": False,
            "POSITIVE_HADAMARD_STATE_ESTABLISHED": False,
            "LORENTZIAN_QME_ESTABLISHED": False,
            "POPULATION_LEVEL_EMPIRICAL_VERDICT": False,
            "GLOBAL_BLACK_HOLE_WAVEFORM_ESTABLISHED": False,
        },
        "does_not_establish": [
            "a new scientific theorem or quantum lifecycle promotion",
            "a positive full-BV quantum state, Lorentzian QME, scattering, or unitarity",
            "a complete metric/BV retarded propagator or global black-hole waveform",
            "population-level or systematics-complete galactic model selection",
            "a continuum or Lorentzian Bateman--Turok reconstruction",
            "that atlas coverage composes into a complete physical theory",
            "that a finite or formal proof supplies a missing physical premise",
            "peer review or independent reproduction of the whole programme",
        ],
        "verification_commands": [
            "cd paper && pdflatex -interaction=nonstopmode -halt-on-error 00-ghosts-geometry-reality.tex && pdflatex -interaction=nonstopmode -halt-on-error 00-ghosts-geometry-reality.tex",
            "python3 paper/generate_00_timeless_introduction_receipt.py --check",
            "python3 paper/verify_00_timeless_introduction.py",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rendered = json.dumps(build(), indent=2, sort_keys=True) + "\n"
    if args.check:
        require(OUTPUT.exists() and OUTPUT.read_text() == rendered, "Paper 00 receipt is stale")
        print("Paper 00 timeless-introduction receipt: PASS")
    else:
        OUTPUT.write_text(rendered)
        print(f"wrote {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
