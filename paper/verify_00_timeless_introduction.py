#!/usr/bin/env python3
"""Independent audit of Paper 00's guide coverage, authorities, and boundaries."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "paper/00-ghosts-geometry-reality-receipt.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def main() -> None:
    receipt = json.loads(RECEIPT.read_text())
    require(
        receipt["schema_version"] == "paper-00-programme-guide-receipt-v2",
        "unexpected receipt schema",
    )
    require(
        receipt["result_id"] == "PAPER_00_THEMATIC_PROGRAMME_GUIDE_V2",
        "unexpected result id",
    )
    require(receipt["lifecycle"] == "VERIFIED_NAVIGATION_ARTIFACT", "unexpected lifecycle")
    require(
        receipt["dependency_tags"]
        == ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL", "REDUCED-MODE", "LORENTZIAN-CAUSAL"],
        "dependency tags drifted",
    )
    require(len(receipt["artifacts"]) == 2, "artifact count drifted")
    for relative, digest in receipt["artifacts"].items():
        path = ROOT / relative
        require(path.is_file(), f"missing artifact: {relative}")
        require(sha256(path) == digest, f"artifact hash drifted: {relative}")

    require(len(receipt["authorities"]) == 11, "authority count drifted")
    authorities = {}
    for name, row in receipt["authorities"].items():
        path = ROOT / row["path"]
        payload = json.loads(path.read_text())
        require(sha256(path) == row["sha256"], f"authority hash drifted: {name}")
        require(
            payload.get("result_id", payload.get("certificate")) == row["result_id"],
            f"authority identity drifted: {name}",
        )
        require(payload["dependency_tags"] == row["dependency_tags"], f"authority tags drifted: {name}")
        boundary = payload.get("does_not_establish")
        if boundary is None:
            boundary = payload.get("explicit_nonclaims", payload.get("headline"))
        require(boundary == row["claim_boundary"], f"authority boundary drifted: {name}")
        authorities[name] = payload

    require(len(authorities["theory_passports"]["passports"]) == 8, "passport count drifted")
    require(len(authorities["theory_assemblies"]["assemblies"]) == 9, "assembly count drifted")
    require(
        authorities["classical_gate_a"]["result_state"]
        == "CLASSICAL_IMPORT_GATE_A_VERIFIED_ON_IMMUTABLE_STRICT_PURE_WEYL_SNAPSHOT",
        "Gate-A state drifted",
    )
    require(
        authorities["typed_q2_q3_green"]["result_state"]
        == "NONLINEAR_GREEN_COMPATIBILITY_AND_SECOND_SOURCE_COCYCLE_CERTIFIED_HADAMARD_OPEN",
        "typed Green frontier drifted",
    )
    hadamard = authorities["hadamard_pseudo_state"]
    require(
        hadamard["result_state"] == "FULL_386_BRST_HADAMARD_TWO_POINT_CERTIFIED_POSITIVE_STATE_OPEN",
        "Hadamard frontier drifted",
    )
    require(
        "a positive quasifree Hadamard state or positive physical graviton Hilbert space"
        in hadamard["does_not_establish"],
        "Hadamard positivity boundary drifted",
    )
    bt = authorities["bt_green_tail"]
    require(bt["research_disposition"]["all_field_torus_scaled_PL"] == "REFUTED", "BT disposition drifted")
    require(bt["research_disposition"]["lorentzian_transfer"] == "NOT_ESTABLISHED", "BT boundary drifted")

    models = {row["model_id"]: row for row in authorities["ngc3198_comparison"]["models"]}
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

    paper12 = authorities["paper12_anomaly_claim_map"]
    require(paper12["certified_claims"]["strict_one_loop_local_Euclidean_QME_obstructed"] is True, "anomaly drifted")
    require(
        paper12["certified_claims"]["extended_one_loop_local_Euclidean_QME_restored"] is True,
        "changed-theory QME restoration drifted",
    )
    paper17 = authorities["paper17_resonance_claim_map"]
    for flag in (
        "certified_qnm_smith_type_0_0_2",
        "exterior_cutoff_green_double_pole",
        "global_ecs_green_double_pole",
        "mode_reduced_retarded_green_operator",
    ):
        require(paper17["claim_flags"][flag] is True, f"Paper 17 claim drifted: {flag}")
    for flag in ("complete_retarded_qnm_expansion", "global_causal_resolvent", "detector_sensitivity"):
        require(paper17["claim_flags"][flag] is False, f"Paper 17 nonclaim drifted: {flag}")

    source_path = ROOT / "paper/00-ghosts-geometry-reality.tex"
    source = source_path.read_text()
    direct = [
        target
        for target in re.findall(r"\\href\{([^}]+)\}", source)
        if "://" not in target and target != "#1"
    ]
    paper_links = re.findall(r"\\paperlink\{([^}]+)\}", source)
    links = sorted(set(direct + paper_links))
    require(links == receipt["local_links"], "local-link ledger drifted")
    require(all((source_path.parent / target).resolve().exists() for target in links), "a local link is missing")
    cited = set()
    for group in re.findall(r"\\cite\{([^}]+)\}", source):
        cited.update(key.strip() for key in group.split(","))
    defined = set(re.findall(r"\\bibitem\{([^}]+)\}", source))
    require(not (cited - defined), "an undefined bibliography key survived")
    require(sorted(cited) == receipt["bibliography_keys"], "bibliography ledger drifted")

    require(
        receipt["editorial_checks"]
        == {
            "archive_documents_covered": 1,
            "atlas_coordinates": 576,
            "bibliography_keys_resolved": 0,
            "bridge_notes_covered": 3,
            "changelog_fragments_rejected": 14,
            "computational_supplements_covered": 4,
            "headline_papers_covered": 22,
            "local_links_resolved": 33,
            "programme_prototypes": 9,
            "public_entrances_covered": 2,
            "required_guide_fragments": 7,
            "theory_passports": 8,
        },
        "editorial-check ledger drifted",
    )
    require(all(value is False for value in receipt["claim_flags"].values()), "a promotion flag is true")
    required_sections = [
        "\\section{Choose an entrance}",
        "\\section{How claims move through the series}",
        "\\section{Thread I: completion and interaction---Papers 01--06}",
        "\\section{Thread II: causal and compact pure-Weyl theory---Papers 07--13}",
        "\\section{Thread III: black holes and the four-level classification---Papers 14--18}",
        "\\section{Thread IV: assumptions and reverse foundations---Papers 19--22}",
        "\\section{Reading routes by research question}",
        "\\section{How to inspect a claim}",
    ]
    require(all(section in source for section in required_sections), "a guide section is missing")
    basenames = {Path(link).name for link in links}
    for paper_number in range(1, 23):
        prefix = f"{paper_number:02d}-"
        require(any(name.startswith(prefix) for name in basenames), f"Paper {paper_number:02d} is not linked")
    for paper_number in (90, 91, 92, 98, 99):
        prefix = f"{paper_number:02d}-"
        require(any(name.startswith(prefix) for name in basenames), f"Paper {paper_number:02d} is not linked")
    forbidden = [
        "\\section{Paper map}",
        "\\section{What remains open}",
        "\\textbf{Current verdict.}",
        "Public pre-release, July 2026",
    ]
    require(all(fragment not in source for fragment in forbidden), "changelog structure survived")
    print("Paper 00 independent programme-guide audit: PASS")


if __name__ == "__main__":
    main()
