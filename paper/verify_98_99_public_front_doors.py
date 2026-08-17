#!/usr/bin/env python3
"""Independent hash and claim-boundary audit for public Papers 98 and 99."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "paper/98-99-public-front-door-receipt.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def main() -> None:
    receipt = json.loads(RECEIPT.read_text())
    require(
        receipt["schema_version"] == "public-front-door-editorial-receipt-v3",
        "unexpected receipt schema",
    )
    require(receipt["result_id"] == "PUBLIC_FRONT_DOOR_98_99_TIMELESS_SYNTHESIS_V3", "unexpected result id")
    require(receipt["lifecycle"] == "VERIFIED_NAVIGATION_ARTIFACT", "unexpected lifecycle")
    require(
        receipt["dependency_tags"]
        == [
            "LOCAL-ALGEBRAIC",
            "EUCLIDEAN-SPECTRAL",
            "REDUCED-MODE",
            "LORENTZIAN-CAUSAL",
        ],
        "dependency-tag boundary drifted",
    )

    require(len(receipt["artifacts"]) == 4, "artifact count drifted")
    for relative, digest in receipt["artifacts"].items():
        path = ROOT / relative
        require(path.is_file(), f"missing artifact: {relative}")
        require(sha256(path) == digest, f"artifact hash drifted: {relative}")

    require(len(receipt["authorities"]) == 9, "authority count drifted")
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
        require(
            payload["does_not_establish"] == row["does_not_establish"],
            f"authority boundary drifted: {name}",
        )
        authorities[name] = payload

    passports = authorities["theory_passports"]
    assemblies = authorities["theory_assemblies"]
    comparison = authorities["ngc3198_comparison"]
    gate = authorities["classical_gate_a"]
    green = authorities["typed_q2_q3_green"]
    hadamard = authorities["hadamard_pseudo_state"]
    bt = authorities["bt_green_tail"]
    require(len(passports["passports"]) == 8, "theory-passport count drifted")
    require(len(assemblies["assemblies"]) == 9, "programme-assembly count drifted")
    coverage = {row["id"]: row["coverage"]["direct"] for row in assemblies["assemblies"]}
    require(coverage["STANDARD_MIXED_REFERENCE"] == 16, "mainstream coverage drifted")
    require(coverage["KREIN_ALGEBRAIC_PROGRAMME"] == 15, "Mannheim coverage drifted")
    require(coverage["PURE_WEYL_BV_BFV_PROGRAMME"] == 15, "pure-Weyl coverage drifted")

    expected_models = {
        "NEWTONIAN_BARYONS_ONLY": (23.896205433040972, 128.72235125034302, False),
        "GR_NFW_DARK_HALO": (5.147987363846723, 0.9652634913239349, True),
        "MANNHEIM_CONFORMAL_GRAVITY": (4.694475967312153, 3.201777683080153, False),
    }
    models = {row["model_id"]: row for row in comparison["models"]}
    for model_id, (rms, reduced_chi2, passed) in expected_models.items():
        row = models[model_id]
        require(row["metrics"]["unweighted_rms_residual_km_s"] == rms, f"RMS drifted: {model_id}")
        require(row["metrics"]["reduced_chi_squared"] == reduced_chi2, f"chi-squared drifted: {model_id}")
        require(row["random_error_gate"]["passed"] is passed, f"empirical gate drifted: {model_id}")

    require(
        gate["result_state"] == "CLASSICAL_IMPORT_GATE_A_VERIFIED_ON_IMMUTABLE_STRICT_PURE_WEYL_SNAPSHOT",
        "Gate-A status drifted",
    )
    require(
        green["result_state"] == "NONLINEAR_GREEN_COMPATIBILITY_AND_SECOND_SOURCE_COCYCLE_CERTIFIED_HADAMARD_OPEN",
        "q2/q3 Green frontier drifted",
    )
    require(
        hadamard["result_state"] == "FULL_386_BRST_HADAMARD_TWO_POINT_CERTIFIED_POSITIVE_STATE_OPEN",
        "Hadamard pseudo-state frontier drifted",
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

    for relative, recorded in receipt["local_links"].items():
        source = ROOT / relative
        links = re.findall(r"\[[^]]+\]\(([^)]+)\)", source.read_text())
        local = [link.split("#", 1)[0] for link in links if "://" not in link and not link.startswith("#")]
        require(local == recorded, f"link ledger drifted: {relative}")
        require(all((source.parent / link).exists() for link in local), f"local link missing: {relative}")

    checks = receipt["public_summary_checks"]
    require(
        checks
        == {
            "atlas_coordinates": 576,
            "changelog_phrases_rejected": 12,
            "paper98_required_fragments": 8,
            "paper99_required_fragments": 6,
            "physlib_passports": 2,
            "programme_prototypes": 9,
            "theory_passports": 8,
        },
        "public-summary ledger drifted",
    )
    require(all(value is False for value in receipt["claim_flags"].values()), "a promotion flag is true")

    paper98 = (ROOT / "paper/98-physicist-executive-summary.md").read_text()
    paper99 = (ROOT / "paper/99-how-to-build-a-universe.md").read_text()
    normalized98 = " ".join(paper98.split())
    normalized99 = " ".join(paper99.split())
    require("The word **pseudo-state** is load-bearing." in normalized98, "Paper 98 pseudo-state boundary missing")
    require("coverage envelopes, not rankings" in normalized98, "Paper 98 coverage boundary missing")
    require("## The obligation ladder" in paper98, "Paper 98 obligation argument missing")
    require("## Consequences for theory construction" in paper98, "Paper 98 synthesis missing")
    require("A theory is a stack, not an equation" in normalized99, "Paper 99 stack explanation missing")
    require("“Not reached” is not “refuted.”" in normalized99, "Paper 99 status explanation missing")
    require("not a truth machine" in normalized99, "Paper 99 AI boundary missing")
    require("## What the examples establish" in paper99, "Paper 99 synthesis missing")
    forbidden_headings = [
        "## What is established—and what is not",
        "## Paper map",
        "## Highest-leverage next questions",
        "## Public scorecard",
    ]
    require(
        all(heading not in paper98 and heading not in paper99 for heading in forbidden_headings),
        "changelog-style heading survived",
    )
    print("Papers 98–99 independent public-front-door audit: PASS")


if __name__ == "__main__":
    main()
