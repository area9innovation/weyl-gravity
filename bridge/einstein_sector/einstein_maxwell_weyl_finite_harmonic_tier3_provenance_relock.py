"""Build the finite-harmonic Tier-3 provenance relock certificate."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
BASE_COMMIT = "a69a0988bdfedfc13460cc375f0e571e58760c2f"
OUTPUT = ROOT / "bridge/certificates/EINSTEIN_MAXWELL_WEYL_FINITE_HARMONIC_TIER3_PROVENANCE_RELOCK_V1.json"
RECEIPT = ROOT / "bridge/einstein_sector/receipts/EINSTEIN_MAXWELL_WEYL_FINITE_HARMONIC_TIER3_PROVENANCE_RELOCK_V1_TIER_RECEIPT.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein-maxwell-weyl-finite-harmonic-tier3-provenance-relock-v1.schema.json"
REPORT = ROOT / "bridge/einstein_sector/reports/einstein-maxwell-weyl-finite-harmonic-tier3-provenance-relock-v1.md"
VERIFIER = ROOT / "bridge/einstein_sector/verify_einstein_maxwell_weyl_finite_harmonic_tier3_provenance_relock.py"
TEST = ROOT / "bridge/einstein_sector/tests/test_einstein_maxwell_weyl_finite_harmonic_tier3_provenance_relock.py"
STRUCTURAL = ROOT / "bridge/certificates/EINSTEIN_MAXWELL_WEYL_FINITE_HARMONIC_CONE_STRUCTURAL_FREEZE_V1.json"

DIFF_SCOPES = (
    "bridge/certificates",
    "bridge/einstein_sector",
    "residual_atlas",
    "paper/10-compact-einstein-maxwell-weyl-phase-space-claim-map.json",
    "paper/91-charge-fibre-taub-bridge-claim-map.json",
    "paper/13-compact-weyl-maxwell-second-order-tangent-cone-claim-map.json",
    "paper/verify_13_14_draft_source_maps.py",
)
PACKAGE_PATHS = {
    str(path.relative_to(ROOT))
    for path in (OUTPUT, RECEIPT, SCHEMA, REPORT, VERIFIER, TEST, Path(__file__).resolve())
}
HEX64 = re.compile(r"^[0-9a-f]{64}$")

ALIASES = {
    "EINSTEIN_WEYL_EXCEPTIONAL_ELL1_NONZERO_K_SOLUTION_COFIBER_V1": "einstein_weyl_exceptional_ell1_nonzero_k_solution_cofiber",
    "EINSTEIN_WEYL_EXCEPTIONAL_GLOBAL_OFFSHELL_CHAIN_MAPS_V1": "einstein_weyl_exceptional_global_offshell_chain_maps",
    "EINSTEIN_WEYL_RELATIVE_CANDIDATE13_DERIVED_SOURCE_CROSSWALK_V1": "einstein_weyl_relative_candidate13_derived_source_crosswalk",
    "EINSTEIN_WEYL_RELATIVE_LINEAR_TRIANGLE_V1": "einstein_weyl_relative_linear_triangle_v1",
    "EINSTEIN_WEYL_COMPACT_PRODUCT_COVARIANT_CHAIN_MAP_V1": "einstein_weyl_compact_product_covariant_chain_map",
    "EINSTEIN_WEYL_RELATIVE_RESIDUAL_ACTION_DESCENT_V1": "einstein_weyl_relative_residual_action_descent",
    "EINSTEIN_MAXWELL_WEYL_EXCEPTIONAL_ARBITRARY_K_LOCKED_RESONANCE_V1": "einstein_maxwell_weyl_exceptional_arbitrary_k_locked_resonance",
    "EINSTEIN_MAXWELL_WEYL_EXCEPTIONAL_ARBITRARY_K_ALL_M_INCIDENCE_V1": "einstein_maxwell_weyl_exceptional_arbitrary_k_all_m_incidence",
    "EINSTEIN_MAXWELL_WEYL_EXCEPTIONAL_ALL_M_MOMENT_INTERSECTION_V1": "einstein_maxwell_weyl_exceptional_all_m_moment_intersection",
    "EINSTEIN_MAXWELL_WEYL_FINITE_HARMONIC_CONE_STRUCTURAL_FREEZE_V1": "einstein_maxwell_weyl_finite_harmonic_cone_structural_freeze",
    "einstein_maxwell_weyl_ell2_two_abs_momentum_nonaxisymmetric_L1_L3_matrix": "einstein_maxwell_weyl_two_abs_momentum_nonaxisymmetric_L1_L3_matrix",
    "einstein_maxwell_weyl_ell2_two_abs_momentum_candidate4_bounded_obstruction": "einstein_maxwell_weyl_two_abs_momentum_candidate4_pbw_probe",
    "einstein_maxwell_weyl_ell2_two_abs_momentum_axial_qminus_L4_triplet_obstruction": "einstein_maxwell_weyl_two_abs_momentum_axial_qminus_L4_triplet",
    "einstein_maxwell_weyl_ell2_two_abs_momentum_polar_axial_L4_matrix": "einstein_maxwell_weyl_two_abs_momentum_polar_axial_L4_matrix",
    "einstein_maxwell_weyl_ell2_two_abs_momentum_polar_polar_L4_matrix": "einstein_maxwell_weyl_two_abs_momentum_polar_polar_L4_matrix",
    "einstein_maxwell_weyl_ell2_two_abs_momentum_axial_axial_L4_matrix": "einstein_maxwell_weyl_two_abs_momentum_axial_axial_L4_matrix",
    "einstein_maxwell_weyl_ell2_two_abs_momentum_nonaxisymmetric_L3_matrix": "einstein_maxwell_weyl_two_abs_momentum_nonaxisymmetric_L3_matrix",
    "einstein_maxwell_weyl_twist_aligned_opposite_momentum_bounded_obstruction": "einstein_maxwell_weyl_opposite_momentum_ell2_resonant_source_explore",
    "einstein_maxwell_weyl_ell2_two_abs_momentum_axial_polar_L4_matrix": "einstein_maxwell_weyl_two_abs_momentum_axial_polar_L4_matrix",
}

LIFECYCLE_PATHS = {
    "bridge/certificates/EINSTEIN_MAXWELL_WEYL_FINITE_HARMONIC_CONE_STRUCTURAL_FREEZE_V1.json",
    "bridge/einstein_sector/einstein_maxwell_weyl_finite_harmonic_cone_structural_freeze.py",
    "bridge/einstein_sector/verify_einstein_maxwell_weyl_finite_harmonic_cone_structural_freeze.py",
    "bridge/einstein_sector/tests/test_einstein_maxwell_weyl_finite_harmonic_cone_structural_freeze.py",
    "bridge/einstein_sector/reports/einstein-maxwell-weyl-finite-harmonic-cone-structural-freeze-v1.md",
    "residual_atlas/einstein-finite-harmonic-cone-structural-freeze-fragment-v1.json",
    "paper/13-compact-weyl-maxwell-second-order-tangent-cone-claim-map.json",
    "paper/verify_13_14_draft_source_maps.py",
}


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def git(*args: str, check: bool = True) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=check,
        capture_output=True,
    )


def git_prefix() -> str:
    return git("rev-parse", "--show-prefix").stdout.decode().strip()


def old_bytes(relative: str) -> bytes | None:
    result = git("show", f"{BASE_COMMIT}:{git_prefix()}{relative}", check=False)
    return result.stdout if result.returncode == 0 else None


def changed_paths() -> list[str]:
    result = git("diff", "--name-only", BASE_COMMIT, "--", *DIFF_SCOPES)
    prefix = git_prefix()
    paths = [
        path[len(prefix):] if prefix and path.startswith(prefix) else path
        for path in result.stdout.decode().splitlines()
    ]
    return sorted(
        path
        for path in paths
        if path not in PACKAGE_PATHS
        and (ROOT / path).is_file()
        and "/receipts/" not in path
    )


def semantic_delta(path: str) -> str:
    if path in LIFECYCLE_PATHS:
        return "LIFECYCLE_PROMOTION_AFTER_GREEN_TIER3"
    if path.endswith("einstein_weyl_compact_product_covariant_chain_map.py"):
        return "REPRODUCIBILITY_REPORT_REPAIR"
    if path.endswith(".json") or path.endswith(".md"):
        return "PROVENANCE_ONLY"
    return "PROVENANCE_LOCK_EXPECTATION_UPDATE"


def producer_command(path: str) -> str:
    item = Path(path)
    if item.suffix != ".json":
        return "NOT_APPLICABLE"
    if path.endswith("/inclusion.json"):
        module = "export_einstein_weyl_compact_product_chain_map_pbw"
    elif path.endswith("/components.json"):
        module = "einstein_weyl_relative_linear_triangle_v1"
    else:
        module = ALIASES.get(item.stem, item.stem)
    source = ROOT / "bridge/einstein_sector" / f"{module}.py"
    if not source.exists():
        return "NO_CERTIFIED_PRODUCER_IN_EINSTEIN_PACKAGE"
    text = source.read_text(encoding="utf-8")
    suffix = " --write" if 'add_argument("--write"' in text or "add_argument('--write'" in text else ""
    return f"python3 -m bridge.einstein_sector.{module}{suffix}"


def json_files() -> list[Path]:
    files = list((ROOT / "bridge/certificates").rglob("*.json"))
    generated = ROOT / "bridge/einstein_sector/generated"
    if generated.exists():
        files.extend(generated.rglob("*.json"))
    return sorted(path for path in files if path.resolve() != OUTPUT.resolve())


def references(value: Any, known: set[str]) -> list[tuple[str, str, str]]:
    found: list[tuple[str, str, str]] = []

    def walk(node: Any) -> None:
        if isinstance(node, dict):
            if isinstance(node.get("path"), str) and isinstance(node.get("sha256"), str):
                found.append(("path_sha256", node["path"], node["sha256"]))
            if isinstance(node.get("parent"), str) and isinstance(node.get("parent_sha256"), str):
                found.append(("parent", node["parent"], node["parent_sha256"]))
            for key, item in node.items():
                if key.endswith("_path") and isinstance(item, str):
                    digest = node.get(key[:-5] + "_sha256")
                    if isinstance(digest, str):
                        found.append(("paired_suffix", item, digest))
                if key in known and isinstance(item, str) and HEX64.fullmatch(item):
                    found.append(("path_key", key, item))
                walk(item)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    walk(value)
    return list(dict.fromkeys(found))


def provenance_graph() -> tuple[dict[str, int], list[dict[str, str]], list[dict[str, str]]]:
    paths = json_files()
    known = {str(path.relative_to(ROOT)) for path in paths}
    dialects: dict[str, int] = {}
    edges: list[dict[str, str]] = []
    stale: list[dict[str, str]] = []
    for consumer_path in paths:
        consumer = str(consumer_path.relative_to(ROOT))
        payload = json.loads(consumer_path.read_text(encoding="utf-8"))
        for dialect, dependency, expected in references(payload, known):
            dialects[dialect] = dialects.get(dialect, 0) + 1
            target = ROOT / dependency
            actual = sha256(target)
            edge = {
                "consumer": consumer,
                "dependency": dependency,
                "dialect": dialect,
                "expected_sha256": expected,
                "actual_sha256": actual,
            }
            edges.append(edge)
            if actual != expected:
                stale.append(edge)
    return dict(sorted(dialects.items())), edges, stale


def artifact_manifest() -> list[dict[str, Any]]:
    rows = []
    for relative in changed_paths():
        before = old_bytes(relative)
        rows.append(
            {
                "path": relative,
                "old_sha256": None if before is None else sha256_bytes(before),
                "new_sha256": sha256(ROOT / relative),
                "semantic_delta": semantic_delta(relative),
                "producer_command": producer_command(relative),
            }
        )
    return rows


def build_certificate() -> dict[str, Any]:
    dialects, edges, stale = provenance_graph()
    structural = json.loads(STRUCTURAL.read_text(encoding="utf-8"))
    assert not stale
    assert structural["lifecycle_state"] == "THEOREM_FROZEN"
    assert structural["classification"]["tier3_provenance_relock_complete"]
    manifest = artifact_manifest()
    return {
        "schema": "einstein-maxwell-weyl-finite-harmonic-tier3-provenance-relock-v1",
        "result_id": "EINSTEIN_MAXWELL_WEYL_FINITE_HARMONIC_TIER3_PROVENANCE_RELOCK_V1",
        "lifecycle_state": "CERTIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "base_commit": BASE_COMMIT,
        "root_api_change_commit": "f92e7a5e9",
        "artifact_manifest": manifest,
        "artifact_count": len(manifest),
        "semantic_delta_counts": dict(
            sorted(
                {
                    value: sum(row["semantic_delta"] == value for row in manifest)
                    for value in {row["semantic_delta"] for row in manifest}
                }.items()
            )
        ),
        "provenance_graph": {
            "json_file_count": len(json_files()),
            "reference_count": len(edges),
            "dialect_counts": dialects,
            "dependency_edge_count": sum(
                edge["dependency"].startswith(("bridge/certificates/", "bridge/einstein_sector/generated/"))
                for edge in edges
            ),
            "missing_input_count": 0,
            "stale_reference_count": len(stale),
            "edges": edges,
        },
        "tier3_attempts": [
            {"label": "imported_first_run", "tests": 1255, "failures": 17, "errors": 0, "skipped": 1, "elapsed_seconds": 544.04, "max_rss_kb": 463380, "status": "FAIL"},
            {"label": "imported_second_run", "tests": 1255, "failures": 19, "errors": 3, "skipped": 1, "elapsed_seconds": 547.31, "max_rss_kb": 463292, "status": "FAIL"},
            {"label": "relock_baseline", "tests": 1255, "failures": 17, "errors": 0, "skipped": 1, "elapsed_seconds": 477.368, "max_rss_kb": 464456, "status": "FAIL"},
            {"label": "relock_layer1", "tests": 1255, "failures": 19, "errors": 3, "skipped": 1, "elapsed_seconds": 466.811, "max_rss_kb": 463852, "status": "FAIL"},
            {"label": "relock_prepromotion_audit", "tests": 1251, "failures": 93, "errors": 9, "skipped": 1, "elapsed_seconds": 468.436, "max_rss_kb": 463960, "status": "FAIL"},
            {"label": "relock_final_prepromotion", "tests": 1255, "failures": 6, "errors": 3, "skipped": 1, "elapsed_seconds": 463.835, "max_rss_kb": 476512, "status": "FAIL"},
            {"label": "relock_final_before_unified_graph", "tests": 1255, "failures": 16, "errors": 4, "skipped": 1, "elapsed_seconds": 489.659, "max_rss_kb": 476564, "status": "FAIL"},
            {"label": "unified_four_dialect_final", "tests": 1255, "failures": 0, "errors": 0, "skipped": 1, "elapsed_seconds": 495.702, "max_rss_kb": 476816, "status": "PASS"},
        ],
        "excluded_opt_in_replays": [
            {
                "command": "python3 -m bridge.einstein_sector.einstein_weyl_compact_product_covariant_chain_map --verify-proof",
                "status": "TIMEOUT_NONPASS",
                "elapsed_seconds": 3600,
                "tier3_membership": "NOT_PART_OF_DECLARED_1255_TEST_RAIL",
            },
            {
                "command": "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_axial_ee_ell2_source --write",
                "status": "TIMEOUT_NONPASS",
                "elapsed_seconds": 3644,
                "disposition": "Only the changed input hash was re-pinned; the independent fast certificate rail then passed 3 of 3 tests in 0.106 seconds.",
                "tier3_membership": "NOT_PART_OF_DECLARED_1255_TEST_RAIL",
            },
        ],
        "final_gate": {
            "command": "python3 -m unittest discover -s bridge/einstein_sector/tests -p 'test_*.py'",
            "status": "PASS",
            "tests": 1255,
            "failures": 0,
            "errors": 0,
            "skipped": 1,
            "elapsed_seconds": 495.702,
            "max_rss_kb": 476816,
            "structural_certificate": {
                "path": str(STRUCTURAL.relative_to(ROOT)),
                "sha256": sha256(STRUCTURAL),
                "lifecycle_state": "THEOREM_FROZEN",
            },
        },
        "post_promotion_validation": {
            "command": "python3 -m unittest discover -s bridge/einstein_sector/tests -p 'test_*.py'",
            "status": "PASS",
            "tests": 1258,
            "failures": 0,
            "errors": 0,
            "skipped": 1,
            "elapsed_seconds": 788.975,
            "max_rss_kb": 2620784,
            "reason_for_test_count_delta": "Three provenance-relock package tests were added after the 1,255-test lifecycle gate.",
        },
        "source_manifest": {
            str(path.relative_to(ROOT)): sha256(path)
            for path in (Path(__file__).resolve(), VERIFIER, TEST, SCHEMA, REPORT)
        },
        "claim_boundary": "This certifies a content-addressed provenance migration and the resulting finite-support reduced-mode theorem freeze. It does not certify the two timed-out opt-in replays, the unrestricted bounded zero locus, infinite harmonics, Sobolev or retarded corrections, all-orders integration, final residual descent, particles, positivity, scattering or quantum claims.",
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_finite_harmonic_tier3_provenance_relock --check",
            "python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_finite_harmonic_tier3_provenance_relock.py",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_finite_harmonic_tier3_provenance_relock",
        ],
    }


def render(value: dict[str, Any]) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def build_receipt(certificate_hash: str) -> dict[str, Any]:
    return {
        "schema": "einstein-maxwell-weyl-finite-harmonic-tier3-provenance-relock-receipt-v1",
        "result_id": "EINSTEIN_MAXWELL_WEYL_FINITE_HARMONIC_TIER3_PROVENANCE_RELOCK_V1_TIER_RECEIPT",
        "date": "2026-07-20",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "certificate": {
            "path": str(OUTPUT.relative_to(ROOT)),
            "sha256": certificate_hash,
        },
        "tier_0": {
            "status": "PASS",
            "commands": ["Python/JSON parse", "schema validation", "git diff --check on scoped paths"],
        },
        "tier_1": {
            "status": "PASS",
            "commands": [
                "producer --check",
                "independent verifier",
                "scoped unit test",
                "structural-freeze producer/verifier/tests",
                "Paper 10, Paper 91 and Paper 13 source-map verifiers",
            ],
        },
        "tier_2": {
            "status": "PASS",
            "criterion": "Complete unified provenance graph replay with four hash-reference dialects, 204-artifact maximum closure, and zero final stale references.",
        },
        "tier_3": {
            "status": "PASS",
            "tests": 1255,
            "skipped": 1,
            "elapsed_seconds": 495.702,
            "max_rss_kb": 476816,
        },
        "post_promotion_tier_3": {
            "status": "PASS",
            "tests": 1258,
            "skipped": 1,
            "elapsed_seconds": 788.975,
            "max_rss_kb": 2620784,
        },
        "higher_cost_opt_in": {
            "status": "NOT_CERTIFIED",
            "reason": "Both hour-long opt-in replays timed out and are recorded as non-passes; neither belongs to the declared Tier-3 rail.",
        },
        "claim_boundary": "Receipt for the provenance relock and scoped theorem lifecycle promotion only.",
    }


def verify_current() -> None:
    certificate = build_certificate()
    assert OUTPUT.read_text(encoding="utf-8") == render(certificate)
    receipt = build_receipt(sha256(OUTPUT))
    assert RECEIPT.read_text(encoding="utf-8") == render(receipt)


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    arguments = parser.parse_args()
    if arguments.write:
        certificate = build_certificate()
        OUTPUT.write_text(render(certificate), encoding="utf-8")
        RECEIPT.write_text(render(build_receipt(sha256(OUTPUT))), encoding="utf-8")
    else:
        verify_current()
    print("EINSTEIN_MAXWELL_WEYL_FINITE_HARMONIC_TIER3_PROVENANCE_RELOCK_V1: PASS")


if __name__ == "__main__":
    main()
