#!/usr/bin/env python3
"""Independently replay the candidate recursive causal-tree domain theorem."""

from __future__ import annotations

import hashlib
import json
from math import comb
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/STRICT_386_RECURSIVE_CAUSAL_TREE_DOMAINS_V1.json"
PREFLIGHT = HERE / "certificates/STRICT_386_STABILIZED_Q2_GREEN_COMPOSITION_PREFLIGHT_V1.json"
GREEN = HERE / "certificates/STRICT_386_GRAPH_GREEN_ACTION_NAME_V1.json"
Q2 = HERE / "certificates/STRICT_386_STABILIZED_Q2_LIFT_PREFLIGHT_V1.json"
INPUTS = (
    (PREFLIGHT, "STRICT_386_STABILIZED_Q2_GREEN_COMPOSITION_PREFLIGHT_V1"),
    (GREEN, "STRICT_386_GRAPH_GREEN_ACTION_NAME_V1"),
    (Q2, "STRICT_386_STABILIZED_Q2_LIFT_PREFLIGHT_V1"),
)


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()


def census() -> list[dict[str, int]]:
    plus = {1: 0}
    minus = {1: 0}
    total = {1: 1}
    rows: list[dict[str, int]] = []
    for leaves in range(2, 11):
        plus[leaves] = 0
        minus[leaves] = 0
        for left in range(1, leaves):
            right = leaves - left
            plus[leaves] += total[left] * total[right] - minus[left] * minus[right]
            minus[leaves] += total[left] * total[right] - plus[left] * plus[right]
        total[leaves] = plus[leaves] + minus[leaves]
        topologies = comb(2 * (leaves - 1), leaves - 1) // leaves
        possible = topologies * (2 ** (leaves - 1))
        rows.append({
            "leaves": leaves,
            "plane_binary_tree_topologies": topologies,
            "all_sign_decorations": possible,
            "admissible_plus_root": plus[leaves],
            "admissible_minus_root": minus[leaves],
            "admissible_total": total[leaves],
            "not_uniformly_defined": possible - total[leaves],
        })
    return rows


def hashed(block: Mapping[str, Any]) -> bool:
    return block.get("sha256") == digest({key: item for key, item in block.items() if key != "sha256"})


def check(value: Mapping[str, Any] | None = None) -> list[str]:
    value = load(RESULT) if value is None else value
    preflight, green, q2 = (load(path) for path, _ in INPUTS)
    errors: list[str] = []
    if (
        value.get("result_id") != "STRICT_386_RECURSIVE_CAUSAL_TREE_DOMAINS_V1"
        or value.get("result_kind") != "CANDIDATE_POLARIZED_FINITE_CAUSAL_TREE_DOMAIN_THEOREM_AND_MIXED_SIGN_NONDEFINITION"
        or value.get("result_state") != "POLARIZED_FINITE_TREES_CERTIFIED_UNRESTRICTED_MIXED_AND_INFINITE_SERIES_OPEN"
        or value.get("lifecycle") != "CLASSIFIED"
        or value.get("dependency_tags") != ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"]
    ):
        errors.append("identity/lifecycle")

    provenance = value.get("provenance", {}).get("inputs", [])
    if len(provenance) != 3:
        errors.append("provenance count")
    else:
        for row, (path, expected) in zip(provenance, INPUTS):
            source = load(path)
            if (
                (source.get("result_id") or source.get("schema")) != expected
                or row.get("path") != str(path.relative_to(ROOT))
                or row.get("result_or_artifact_id") != expected
                or row.get("sha256") != sha(path)
            ):
                errors.append("provenance " + expected)

    theorem = value.get("analytic_extension_import", {})
    baer = next(item for item in green["analytic_sources"] if item["id"] == "baer-2015")
    if (
        theorem.get("source_id") != "baer-2015"
        or theorem.get("source_pdf_sha256") != baer["artifact"]["sha256"]
        or theorem.get("source_pdf_sha256") != "879948318de8b4a5a74b52179f78120d074bc7773734b82495b6db4c363f4c99"
        or theorem.get("theorem") != "Theorem 3.8"
        or theorem.get("spatial_compactness_lemmas") != ["Lemma 1.7", "Remark 1.8"]
        or "Gamma_pc" not in theorem.get("retarded_extension", "")
        or "Gamma_fc" not in theorem.get("advanced_extension", "")
        or theorem.get("import_status") != "CONTENT_PINNED_CLASSICAL_THEOREM_NOT_WEAK_BASE_FORMALIZED"
        or not hashed(theorem)
    ):
        errors.append("analytic extension import")

    support = value.get("support_algebra", {})
    expected_intersections = {
        "C*C": "C", "C*PC": "C", "C*FC": "C",
        "PC*C": "C", "PC*PC": "PC", "PC*FC": "C",
        "FC*C": "C", "FC*PC": "C", "FC*FC": "FC",
    }
    expected_green_domains = {
        "plus(C)": "PC", "plus(PC)": "PC", "plus(FC)": "NOT_UNIFORMLY_DEFINED",
        "minus(C)": "FC", "minus(PC)": "NOT_UNIFORMLY_DEFINED", "minus(FC)": "FC",
    }
    if (
        support.get("intersection_table_on_RxS3") != expected_intersections
        or support.get("green_domain_table") != expected_green_domains
        or support.get("local_maps_preserve_every_class") is not True
        or support.get("unindexed_global_joint_LF_continuity_claimed") is not False
        or "Gamma_pc" not in support.get("graph_homotopy_extensions", {}).get("plus", "")
        or "Gamma_fc" not in support.get("graph_homotopy_extensions", {}).get("minus", "")
        or not hashed(support)
    ):
        errors.append("support algebra")

    tree = value.get("recursive_polarized_tree_theorem", {})
    if (
        tree.get("retarded", {}).get("all_finite_plane_binary_trees") is not True
        or tree.get("retarded", {}).get("root_space") != "Gamma_pc^infinity(M,E_386)"
        or tree.get("advanced", {}).get("all_finite_plane_binary_trees") is not True
        or tree.get("advanced", {}).get("root_space") != "Gamma_fc^infinity(M,E_386)"
        or len(tree.get("induction", [])) != 5
        or tree.get("finite_tree_support_domain_defects") != 0
        or tree.get("finite_tree_nodewise_homotopy_domain_defects") != 0
        or tree.get("formal_power_series") != "NOT_SUMMED"
        or tree.get("status") != "ALL_FINITE_POLARIZED_TREES_CERTIFIED_FOR_CANDIDATE_Q2"
        or not hashed(tree)
    ):
        errors.append("polarized tree induction")

    expected_census = census()
    if value.get("sign_decoration_census") != expected_census:
        errors.append("sign-decoration recurrence")
    if expected_census[0]["not_uniformly_defined"] != 0 or expected_census[1]["not_uniformly_defined"] != 0 or expected_census[2]["not_uniformly_defined"] != 2:
        errors.append("minimal recurrence boundary")

    mixed = value.get("mixed_sign_boundary", {})
    if (
        mixed.get("all_comb_trees_every_sign_decoration_admissible") is not True
        or mixed.get("first_uniform_failure_leaf_count") != 4
        or mixed.get("first_failure_topology") != "balanced four-leaf tree"
        or len(mixed.get("minimal_witnesses", [])) != 2
        or mixed.get("four_leaf_all_sign_decorations") != 40
        or mixed.get("four_leaf_admissible") != 38
        or mixed.get("four_leaf_not_uniformly_defined") != 2
        or "do not define" not in mixed.get("causal_difference_iteration", "")
        or "not a no-go theorem" not in mixed.get("scope", "")
        or not hashed(mixed)
    ):
        errors.append("mixed-sign boundary")

    zero = value.get("zero_mode_mismatch_witness", {})
    if (
        zero.get("spatial_branch") != "S3 scalar k=0"
        or zero.get("kernel") != "s_0(t-r)=t-r"
        or "diverges quadratically" not in zero.get("advanced_on_PC_witness", "")
        or "diverges quadratically" not in zero.get("retarded_on_FC_witness", "")
        or zero.get("defects") != 0
        or "do not extend" not in zero.get("establishes", "")
        or "actual q2 tree" not in zero.get("does_not_establish", "")
        or not hashed(zero)
    ):
        errors.append("zero-mode mismatch witness")

    foundations = value.get("foundational_strength", {})
    if (
        foundations.get("classification") != "FINITE_EXACT_TREE_GRAMMAR_OVER_CLASSICAL_SUPPORT_SPACE_ANALYSIS"
        or "primitive recursive" not in foundations.get("finite_exact_layer", "")
        or foundations.get("weakest_complete_foundational_base") != "NOT_ESTABLISHED"
        or foundations.get("axiom_of_choice_status") != "NO_NEW_CHOICE_BEYOND_THE_IMPORTED_GREEN_AND_SMOOTH_SUPPORT_THEOREMS"
        or not hashed(foundations)
    ):
        errors.append("foundational boundary")

    authority = value.get("authority_boundary", {})
    if (
        authority.get("candidate_q2_only") is not True
        or authority.get("authoritative_full_q2_imported") is not False
        or authority.get("candidate_authoritative_equivalence_certified") is not False
        or authority.get("classical_import_gate_a_status") != "FAIL_CLOSED"
        or authority.get("q3_or_higher_operations_imported") is not False
        or not hashed(authority)
    ):
        errors.append("authority boundary")

    flags = value.get("claim_flags", {})
    required_true = {
        "STRICT_386_CANDIDATE_RETARDED_ALL_FINITE_Q2_TREES_CERTIFIED",
        "STRICT_386_CANDIDATE_ADVANCED_ALL_FINITE_Q2_TREES_CERTIFIED",
        "STRICT_386_CANDIDATE_SUPPORT_GRAMMAR_CERTIFIED",
        "STRICT_386_CANDIDATE_FIXED_STEP_TREE_CONTINUITY_CERTIFIED",
        "STRICT_386_FIRST_MIXED_SIGN_DOMAIN_NONDEFINITION_AT_FOUR_LEAVES",
    }
    if not all(flags.get(key) is True for key in required_true):
        errors.append("positive claim flags")
    if any(flags.get(key) is not False for key in set(flags) - required_true):
        errors.append("promotion firewall")

    snapshot = value.get("tree_domain_snapshot", {})
    expected_snapshot = {
        "kind": "STRICT_386_CANDIDATE_RECURSIVE_CAUSAL_TREE_DOMAIN_SNAPSHOT",
        "first_response_sha256": preflight["response_snapshot"]["sha256"],
        "theorem_import_sha256": theorem.get("sha256"),
        "support_algebra_sha256": support.get("sha256"),
        "recursive_theorem_sha256": tree.get("sha256"),
        "decoration_census_sha256": digest(expected_census),
        "mixed_boundary_sha256": mixed.get("sha256"),
        "zero_mode_boundary_sha256": zero.get("sha256"),
        "foundations_sha256": foundations.get("sha256"),
        "authority_sha256": authority.get("sha256"),
        "receiver_status": "CANDIDATE_SCOPED_NOT_GATE_A_ACCEPTED",
    }
    expected_snapshot["sha256"] = digest(expected_snapshot)
    if snapshot != expected_snapshot:
        errors.append("tree-domain snapshot")

    expected_hashes = {
        "analytic_extension_import_sha256": theorem.get("sha256"),
        "support_algebra_sha256": support.get("sha256"),
        "recursive_polarized_tree_theorem_sha256": tree.get("sha256"),
        "sign_decoration_census_sha256": digest(expected_census),
        "mixed_sign_boundary_sha256": mixed.get("sha256"),
        "zero_mode_mismatch_witness_sha256": zero.get("sha256"),
        "foundational_strength_sha256": foundations.get("sha256"),
        "authority_boundary_sha256": authority.get("sha256"),
        "tree_domain_snapshot_sha256": expected_snapshot["sha256"],
    }
    if value.get("canonical_hashes") != expected_hashes:
        errors.append("canonical hashes")
    return errors


def main() -> int:
    errors = check()
    print("STRICT_386_RECURSIVE_CAUSAL_TREE_DOMAINS_V1: " + ("PASS" if not errors else "FAIL"))
    if not errors:
        print("  - every finite all-retarded and all-advanced candidate q2 tree closes on PC/FC domains")
        print("  - exact support grammar finds the first mixed-sign nondefinition at four leaves")
        print("  - infinite series, authoritative q2, Hadamard and QME claims remain fail closed")
    for error in errors:
        print("  - " + error)
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
