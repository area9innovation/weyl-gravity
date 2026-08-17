#!/usr/bin/env python3
"""Generate the content-addressed editorial receipt for Papers 98 and 99."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "paper/98-99-public-front-door-receipt.json"
ARTIFACTS = [
    "paper/98-physicist-executive-summary.md",
    "paper/98-physicist-executive-summary.pdf",
    "paper/99-how-to-build-a-universe.md",
    "paper/99-how-to-build-a-universe.pdf",
]
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
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def local_links(relative: str) -> list[str]:
    path = ROOT / relative
    links = re.findall(r"\[[^]]+\]\(([^)]+)\)", path.read_text())
    local = [link.split("#", 1)[0] for link in links if "://" not in link and not link.startswith("#")]
    missing = [link for link in local if not (path.parent / link).exists()]
    if missing:
        raise ValueError(f"missing local links in {relative}: {missing}")
    return local


def load_authorities() -> dict[str, dict]:
    result = {}
    for name, relative in AUTHORITIES.items():
        path = ROOT / relative
        payload = json.loads(path.read_text())
        result[name] = {
            "path": relative,
            "sha256": sha256(path),
            "result_id": payload.get("result_id", payload.get("certificate")),
            "dependency_tags": payload["dependency_tags"],
            "does_not_establish": payload["does_not_establish"],
        }
    return result


def validate_scientific_summary() -> None:
    passports = json.loads((ROOT / AUTHORITIES["theory_passports"]).read_text())
    assemblies = json.loads((ROOT / AUTHORITIES["theory_assemblies"]).read_text())
    comparison = json.loads((ROOT / AUTHORITIES["ngc3198_comparison"]).read_text())
    gate = json.loads((ROOT / AUTHORITIES["classical_gate_a"]).read_text())
    green = json.loads((ROOT / AUTHORITIES["typed_q2_q3_green"]).read_text())
    hadamard = json.loads((ROOT / AUTHORITIES["hadamard_pseudo_state"]).read_text())
    bt = json.loads((ROOT / AUTHORITIES["bt_green_tail"]).read_text())

    if len(passports["passports"]) != 8:
        raise ValueError("theory-passport count drifted")
    if len(assemblies["assemblies"]) != 9:
        raise ValueError("programme-assembly count drifted")
    coverage = {row["id"]: row["coverage"]["direct"] for row in assemblies["assemblies"]}
    if coverage["STANDARD_MIXED_REFERENCE"] != 16:
        raise ValueError("mainstream reference coverage drifted")
    if coverage["KREIN_ALGEBRAIC_PROGRAMME"] != 15 or coverage["PURE_WEYL_BV_BFV_PROGRAMME"] != 15:
        raise ValueError("programme coverage summary drifted")

    models = {row["model_id"]: row for row in comparison["models"]}
    expected = {
        "NEWTONIAN_BARYONS_ONLY": (23.896205433040972, 128.72235125034302, False),
        "GR_NFW_DARK_HALO": (5.147987363846723, 0.9652634913239349, True),
        "MANNHEIM_CONFORMAL_GRAVITY": (4.694475967312153, 3.201777683080153, False),
    }
    for model_id, (rms, reduced_chi2, passed) in expected.items():
        row = models[model_id]
        if row["metrics"]["unweighted_rms_residual_km_s"] != rms:
            raise ValueError(f"RMS drifted for {model_id}")
        if row["metrics"]["reduced_chi_squared"] != reduced_chi2:
            raise ValueError(f"reduced chi-squared drifted for {model_id}")
        if row["random_error_gate"]["passed"] is not passed:
            raise ValueError(f"empirical gate drifted for {model_id}")

    if gate["result_state"] != "CLASSICAL_IMPORT_GATE_A_VERIFIED_ON_IMMUTABLE_STRICT_PURE_WEYL_SNAPSHOT":
        raise ValueError("Gate-A status drifted")
    if green["result_state"] != "NONLINEAR_GREEN_COMPATIBILITY_AND_SECOND_SOURCE_COCYCLE_CERTIFIED_HADAMARD_OPEN":
        raise ValueError("q2/q3 Green frontier drifted")
    if hadamard["result_state"] != "FULL_386_BRST_HADAMARD_TWO_POINT_CERTIFIED_POSITIVE_STATE_OPEN":
        raise ValueError("Hadamard pseudo-state frontier drifted")
    if "a positive quasifree Hadamard state or positive physical graviton Hilbert space" not in hadamard["does_not_establish"]:
        raise ValueError("Hadamard positivity boundary drifted")
    if bt["research_disposition"]["all_field_torus_scaled_PL"] != "REFUTED":
        raise ValueError("BT all-field disposition drifted")
    if bt["research_disposition"]["lorentzian_transfer"] != "NOT_ESTABLISHED":
        raise ValueError("BT Lorentzian boundary drifted")


def build() -> dict:
    validate_scientific_summary()
    paper98 = (ROOT / ARTIFACTS[0]).read_text()
    paper99 = (ROOT / ARTIFACTS[2]).read_text()
    normalized98 = " ".join(paper98.split())
    normalized99 = " ".join(paper99.split())
    required98 = [
        "576 navigational coordinates",
        "BRST–Hadamard two-point **pseudo-state pair**",
        "Mannheim therefore has the smallest unweighted RMS",
        "Paper 22 answers **no**",
        "Eight theory passports",
        "two Lean/Physlib proof passports",
    ]
    required99 = [
        "A theory is a stack, not an equation",
        "They are not 576 rival universes. They are 576 questions.",
        "one plausible universal stability shortcut is false",
        "It is not a positive physical state",
        "Some finite identities are exposed as Lean 4.32/Physlib proof passports.",
    ]
    for fragment in required98:
        if fragment not in normalized98:
            raise ValueError(f"Paper 98 public claim missing: {fragment}")
    for fragment in required99:
        if fragment not in normalized99:
            raise ValueError(f"Paper 99 public claim missing: {fragment}")
    forbidden = [
        "does not currently contain:\n\n- a BRST-compatible Hadamard state",
        "**Public pre-release — 27 July 2026**",
        "# Are Weyl Gravity’s Ghosts Real?",
    ]
    for phrase in forbidden:
        if phrase in paper98 or phrase in paper99:
            raise ValueError(f"stale public-front-door language survived: {phrase}")

    links = {
        ARTIFACTS[0]: local_links(ARTIFACTS[0]),
        ARTIFACTS[2]: local_links(ARTIFACTS[2]),
    }
    return {
        "schema_version": "public-front-door-editorial-receipt-v2",
        "result_id": "PUBLIC_FRONT_DOOR_98_99_REFRESH_V2",
        "result_kind": "CONTENT_ADDRESSED_PUBLIC_NAVIGATION_AND_CLAIM_BOUNDARY_RECEIPT",
        "lifecycle": "VERIFIED_NAVIGATION_ARTIFACT",
        "created": "2026-08-17",
        "dependency_tags": [
            "LOCAL-ALGEBRAIC",
            "EUCLIDEAN-SPECTRAL",
            "REDUCED-MODE",
            "LORENTZIAN-CAUSAL",
        ],
        "artifacts": {relative: sha256(ROOT / relative) for relative in ARTIFACTS},
        "local_links": links,
        "authorities": load_authorities(),
        "public_summary_checks": {
            "paper98_required_fragments": len(required98),
            "paper99_required_fragments": len(required99),
            "stale_phrases_rejected": len(forbidden),
            "theory_passports": 8,
            "programme_prototypes": 9,
            "atlas_coordinates": 576,
            "physlib_passports": 2,
        },
        "claim_flags": {
            "NEW_SCIENTIFIC_THEOREM": False,
            "MATRIX_GRADE_PROMOTED": False,
            "POSITIVE_HADAMARD_STATE_ESTABLISHED": False,
            "COMPLETE_THEORY_SELECTED": False,
            "POPULATION_LEVEL_EMPIRICAL_VERDICT": False,
            "LORENTZIAN_QME_ESTABLISHED": False,
        },
        "does_not_establish": [
            "a new scientific theorem or lifecycle promotion",
            "that programme coverage composes into a complete physical theory",
            "a positive Hadamard state, Lorentzian QME, scattering or unitarity",
            "population-level or held-out empirical performance",
            "a continuum Bateman–Turok reconstruction or Lorentzian transfer",
            "that Lean or Physlib formalization supplies a missing physical premise",
            "peer review or independent reproduction of the whole programme",
        ],
        "verification_commands": [
            "python3 paper/generate_98_99_public_front_door_receipt.py --check",
            "python3 paper/verify_98_99_public_front_doors.py",
            "pandoc paper/98-physicist-executive-summary.md --from=gfm --pdf-engine=xelatex -V geometry:margin=0.9in -V fontsize=10pt -V colorlinks=true -V title-meta='Reverse Physics and Pure-Weyl Gravity: Executive Summary for Physicists' -V author-meta='GPT-5.6.sol; Asger Alstrup Palm' -o paper/98-physicist-executive-summary.pdf",
            "pandoc paper/99-how-to-build-a-universe.md --from=gfm --pdf-engine=xelatex -V geometry:margin=0.75in -V fontsize=10pt -V colorlinks=true -V title-meta='How to Build a Universe: Physics, Mathematics, Logic—and Research in the Age of AI' -V author-meta='GPT-5.6.sol; Asger Alstrup Palm' -o paper/99-how-to-build-a-universe.pdf",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rendered = json.dumps(build(), indent=2, sort_keys=True) + "\n"
    if args.check:
        if not OUTPUT.exists() or OUTPUT.read_text() != rendered:
            raise SystemExit("Papers 98–99 public-front-door receipt is stale")
        print("Papers 98–99 public-front-door receipt: PASS")
    else:
        OUTPUT.write_text(rendered)
        print(f"wrote {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
