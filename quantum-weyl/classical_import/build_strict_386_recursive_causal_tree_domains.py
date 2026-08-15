#!/usr/bin/env python3
"""Build the candidate recursive causal-tree support-domain certificate."""

from __future__ import annotations

import argparse
import hashlib
import json
from math import comb
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/STRICT_386_RECURSIVE_CAUSAL_TREE_DOMAINS_V1.json"
REPORT = HERE / "REPORT_STRICT_386_RECURSIVE_CAUSAL_TREE_DOMAINS_V1.md"

PREFLIGHT = HERE / "certificates/STRICT_386_STABILIZED_Q2_GREEN_COMPOSITION_PREFLIGHT_V1.json"
GREEN = HERE / "certificates/STRICT_386_GRAPH_GREEN_ACTION_NAME_V1.json"
Q2 = HERE / "certificates/STRICT_386_STABILIZED_Q2_LIFT_PREFLIGHT_V1.json"
INPUTS = (
    (PREFLIGHT, "STRICT_386_STABILIZED_Q2_GREEN_COMPOSITION_PREFLIGHT_V1", "first candidate q2/Green response"),
    (GREEN, "STRICT_386_GRAPH_GREEN_ACTION_NAME_V1", "represented graph Green names and pinned Bär theorem"),
    (Q2, "STRICT_386_STABILIZED_Q2_LIFT_PREFLIGHT_V1", "finite-order support-local candidate q2"),
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()


def source_id(value: Mapping[str, Any]) -> str | None:
    return value.get("result_id") or value.get("schema")


def catalan(index: int) -> int:
    return comb(2 * index, index) // (index + 1)


def decoration_census(max_leaves: int = 10) -> list[dict[str, int]]:
    """Count uniformly support-admissible sign-decorated plane binary trees."""
    plus = {1: 0}
    minus = {1: 0}
    total = {1: 1}  # a compact leaf has no outgoing Green sign
    rows: list[dict[str, int]] = []
    for leaves in range(2, max_leaves + 1):
        plus[leaves] = sum(
            total[left] * total[leaves - left]
            - minus[left] * minus[leaves - left]
            for left in range(1, leaves)
        )
        minus[leaves] = sum(
            total[left] * total[leaves - left]
            - plus[left] * plus[leaves - left]
            for left in range(1, leaves)
        )
        total[leaves] = plus[leaves] + minus[leaves]
        topologies = catalan(leaves - 1)
        possible = topologies * 2 ** (leaves - 1)
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


def build() -> dict[str, Any]:
    values = {path: json.loads(path.read_text()) for path, _, _ in INPUTS}
    for path, expected, _ in INPUTS:
        if source_id(values[path]) != expected:
            raise ValueError(f"dependency identity drift: {path}")
    preflight, green, q2 = (values[path] for path, _, _ in INPUTS)
    if not preflight["claim_flags"].get("STRICT_386_CANDIDATE_Q2_GREEN_RESPONSE_IDENTITY_VERIFIED"):
        raise ValueError("first-response preflight unavailable")
    if not green["analytic_and_exact_replay"].get("full_graph_homotopy_identity_exact"):
        raise ValueError("graph homotopy unavailable")
    if not q2["claim_flags"].get("STRICT_386_STABILIZED_Q2_CANDIDATE_CONSTRUCTED"):
        raise ValueError("candidate q2 unavailable")
    baer = next(item for item in green["analytic_sources"] if item["id"] == "baer-2015")
    if baer["artifact"]["sha256"] != "879948318de8b4a5a74b52179f78120d074bc7773734b82495b6db4c363f4c99":
        raise ValueError("pinned Bär source drift")

    theorem_import = {
        "source_id": "baer-2015",
        "source_pdf_sha256": baer["artifact"]["sha256"],
        "source_locator": baer["artifact"]["locator"],
        "theorem": "Theorem 3.8",
        "spatial_compactness_lemmas": ["Lemma 1.7", "Remark 1.8"],
        "retarded_extension": "G_plus: Gamma_pc^infinity(M,F) -> Gamma_pc^infinity(M,F)",
        "advanced_extension": "G_minus: Gamma_fc^infinity(M,F) -> Gamma_fc^infinity(M,F)",
        "inverse_and_support": "P G_sign=G_sign P=identity on the matching support class and supp G_sign f subset J_sign(supp f)",
        "continuity": "continuous in the support-space locally convex topologies used by the pinned theorem",
        "cylinder_specialization": "On R x S3, past compact equals strictly past compact, future compact equals strictly future compact, and closed temporally compact support is compact.",
        "import_status": "CONTENT_PINNED_CLASSICAL_THEOREM_NOT_WEAK_BASE_FORMALIZED",
    }
    theorem_import["sha256"] = digest(theorem_import)

    support_algebra = {
        "classes": {
            "C": "compact support",
            "PC": "past-compact support; on R x S3 bounded below in cylinder time",
            "FC": "future-compact support; on R x S3 bounded above in cylinder time",
        },
        "q2_support_rule": "supp q2_candidate(u,v) subset supp(u) intersection supp(v)",
        "intersection_table_on_RxS3": {
            "C*C": "C", "C*PC": "C", "C*FC": "C",
            "PC*C": "C", "PC*PC": "PC", "PC*FC": "C",
            "FC*C": "C", "FC*PC": "C", "FC*FC": "FC",
        },
        "green_domain_table": {
            "plus(C)": "PC", "plus(PC)": "PC", "plus(FC)": "NOT_UNIFORMLY_DEFINED",
            "minus(C)": "FC", "minus(PC)": "NOT_UNIFORMLY_DEFINED", "minus(FC)": "FC",
        },
        "fixed_support_steps": {
            "PC_a": "smooth sections supported in [a,infinity) x S3",
            "FC_b": "smooth sections supported in (-infinity,b] x S3",
            "C_ab": "smooth sections supported in [a,b] x S3",
            "q2_PC_steps": "q2: PC_a x PC_b -> PC_max(a,b)",
            "q2_FC_steps": "q2: FC_a x FC_b -> FC_min(a,b)",
            "q2_mixed_steps": "q2: PC_a x FC_b -> C_ab (zero if a>b)",
        },
        "local_maps_preserve_every_class": True,
        "graph_homotopy_extensions": {
            "plus": "Lambda_graph,plus: Gamma_pc^infinity(M,E_386) -> Gamma_pc^infinity(M,E_386)",
            "minus": "Lambda_graph,minus: Gamma_fc^infinity(M,E_386) -> Gamma_fc^infinity(M,E_386)",
            "reason": "The parent Green extension is surrounded only by the certified finite-order support-local BGG, shear, endpoint, inclusion/projection and H_alg maps.",
        },
        "stepwise_continuity": "Every q2 step is continuous bilinear and every graph Green step is continuous linear on each displayed fixed-support Frechet step; finite tree compositions are continuous multilinear on fixed leaf-support steps.",
        "unindexed_global_joint_LF_continuity_claimed": False,
    }
    support_algebra["sha256"] = digest(support_algebra)

    recursive_theorem = {
        "tree_grammar": "T_sign ::= Lambda_graph,sign(q2_candidate(T_left,T_right)); leaves are compact smooth homogeneous inputs",
        "retarded": {
            "sign": "plus",
            "all_finite_plane_binary_trees": True,
            "root_space": "Gamma_pc^infinity(M,E_386)",
            "time_bound": "if leaf i is supported in [a_i,b_i] x S3 then root support is bounded below by max_i a_i",
        },
        "advanced": {
            "sign": "minus",
            "all_finite_plane_binary_trees": True,
            "root_space": "Gamma_fc^infinity(M,E_386)",
            "time_bound": "if leaf i is supported in [a_i,b_i] x S3 then root support is bounded above by min_i b_i",
        },
        "induction": [
            "compact leaves belong to both matching Green domains",
            "the intersection of two PC supports is PC and local q2 preserves it",
            "Lambda_graph,plus maps PC to PC; iterate for every finite retarded tree",
            "reverse future and past for every finite advanced tree",
            "q1 and every local transport map preserve the support class, so the nodewise homotopy identity remains valid",
        ],
        "finite_tree_support_domain_defects": 0,
        "finite_tree_nodewise_homotopy_domain_defects": 0,
        "continuity_scope": "continuous multilinear on every fixed finite collection of leaf-support Frechet steps",
        "formal_power_series": "NOT_SUMMED",
        "status": "ALL_FINITE_POLARIZED_TREES_CERTIFIED_FOR_CANDIDATE_Q2",
    }
    recursive_theorem["sha256"] = digest(recursive_theorem)

    census = decoration_census()
    mixed_boundary = {
        "admissibility_rule": "At an internal node, plus is uniformly admissible unless both noncompact children are FC; minus is uniformly admissible unless both noncompact children are PC. A compact child makes either sign admissible.",
        "all_comb_trees_every_sign_decoration_admissible": True,
        "first_uniform_failure_leaf_count": 4,
        "first_failure_topology": "balanced four-leaf tree",
        "minimal_witnesses": [
            "plus(minus(leaf1,leaf2),minus(leaf3,leaf4)) requires plus on an FC source",
            "minus(plus(leaf1,leaf2),plus(leaf3,leaf4)) requires minus on a PC source",
        ],
        "four_leaf_all_sign_decorations": census[2]["all_sign_decorations"],
        "four_leaf_admissible": census[2]["admissible_total"],
        "four_leaf_not_uniformly_defined": census[2]["not_uniformly_defined"],
        "causal_difference_iteration": "Expanding an arbitrary balanced iteration of B_causal=B_plus-B_minus contains both minimal nondefined decorations; therefore the current domains do not define unrestricted causal-difference trees.",
        "scope": "This is a support-domain nondefinition for the current Green architecture, not a no-go theorem against candidate-specific cancellations or an enlarged weighted/decaying domain.",
    }
    mixed_boundary["sha256"] = digest(mixed_boundary)

    zero_mode_boundary = {
        "spatial_branch": "S3 scalar k=0",
        "kernel": "s_0(t-r)=t-r",
        "advanced_on_PC_witness": "For a smooth chi_plus with chi_plus=0 at t<=0 and chi_plus=1 at t>=1, -integral_t^infinity (t-r) chi_plus(r) dr diverges quadratically.",
        "retarded_on_FC_witness": "For chi_minus(t)=chi_plus(-t), integral_-infinity^t (t-r) chi_minus(r) dr diverges quadratically.",
        "establishes": "The displayed zero-mode Duhamel names do not extend to every opposite-polarity support class merely by reusing the same improper integral.",
        "does_not_establish": "that an actual q2 tree realizes either scalar witness, or that no smaller decaying/weighted mixed domain can be constructed",
        "defects": 0,
    }
    zero_mode_boundary["sha256"] = digest(zero_mode_boundary)

    foundations = {
        "classification": "FINITE_EXACT_TREE_GRAMMAR_OVER_CLASSICAL_SUPPORT_SPACE_ANALYSIS",
        "finite_exact_layer": "The support-class algebra, Catalan recurrence, admissibility checker and induction over finite trees are primitive recursive and add no choice operation.",
        "analytic_layer": "The PC/FC Green extensions, their continuity, smooth cutoffs and Cauchy-support equivalences are imported from classical globally-hyperbolic analysis.",
        "infinite_layer": "No infinite tree sum, convergence radius, resummation, fixed point or selected solution is asserted.",
        "axiom_of_choice_status": "NO_NEW_CHOICE_BEYOND_THE_IMPORTED_GREEN_AND_SMOOTH_SUPPORT_THEOREMS",
        "constructive_status": "FINITE ADMISSIBILITY IS DECIDABLE; ANALYTIC EXTENSIONS HAVE NO TTE MODULUS OR BISHOP-CONSTRUCTIVE PROOF HERE",
        "weakest_complete_foundational_base": "NOT_ESTABLISHED",
    }
    foundations["sha256"] = digest(foundations)

    authority = {
        "candidate_q2_only": True,
        "authoritative_full_q2_imported": False,
        "candidate_authoritative_equivalence_certified": False,
        "classical_import_gate_a_status": "FAIL_CLOSED",
        "q3_or_higher_operations_imported": False,
        "why": "A recursive domain theorem for a receiver-constructed binary operation does not identify it with the source classical theory or supply omitted higher brackets.",
    }
    authority["sha256"] = digest(authority)

    flags = {
        "STRICT_386_CANDIDATE_RETARDED_ALL_FINITE_Q2_TREES_CERTIFIED": True,
        "STRICT_386_CANDIDATE_ADVANCED_ALL_FINITE_Q2_TREES_CERTIFIED": True,
        "STRICT_386_CANDIDATE_SUPPORT_GRAMMAR_CERTIFIED": True,
        "STRICT_386_CANDIDATE_FIXED_STEP_TREE_CONTINUITY_CERTIFIED": True,
        "STRICT_386_FIRST_MIXED_SIGN_DOMAIN_NONDEFINITION_AT_FOUR_LEAVES": True,
        "STRICT_386_UNRESTRICTED_MIXED_SIGN_TREES_CERTIFIED": False,
        "STRICT_386_ARBITRARY_CAUSAL_DIFFERENCE_TREES_CERTIFIED": False,
        "STRICT_386_INFINITE_TREE_SERIES_CONVERGENCE_CERTIFIED": False,
        "STRICT_386_AUTHORITATIVE_Q2_RECURSIVE_TREES_CERTIFIED": False,
        "STRICT_386_Q3_OR_HIGHER_CAUSAL_TREES_CERTIFIED": False,
        "CLASSICAL_IMPORT_GATE_PASSED": False,
        "HADAMARD_STATE_CONSTRUCTED": False,
        "RENORMALIZED_LORENTZIAN_PRODUCTS": False,
        "QME_RESTORED": False,
        "RESIDUAL_TRANSFERRED": False,
        "LORENTZIAN_QUANTUM_THEORY": False,
    }

    snapshot = {
        "kind": "STRICT_386_CANDIDATE_RECURSIVE_CAUSAL_TREE_DOMAIN_SNAPSHOT",
        "first_response_sha256": preflight["response_snapshot"]["sha256"],
        "theorem_import_sha256": theorem_import["sha256"],
        "support_algebra_sha256": support_algebra["sha256"],
        "recursive_theorem_sha256": recursive_theorem["sha256"],
        "decoration_census_sha256": digest(census),
        "mixed_boundary_sha256": mixed_boundary["sha256"],
        "zero_mode_boundary_sha256": zero_mode_boundary["sha256"],
        "foundations_sha256": foundations["sha256"],
        "authority_sha256": authority["sha256"],
        "receiver_status": "CANDIDATE_SCOPED_NOT_GATE_A_ACCEPTED",
    }
    snapshot["sha256"] = digest(snapshot)

    value = {
        "$schema": "../schema/strict-386-recursive-causal-tree-domains-v1.schema.json",
        "schema": "strict-386-recursive-causal-tree-domains-v1",
        "schema_path": "quantum-weyl/classical_import/schema/strict-386-recursive-causal-tree-domains-v1.schema.json",
        "result_id": "STRICT_386_RECURSIVE_CAUSAL_TREE_DOMAINS_V1",
        "result_kind": "CANDIDATE_POLARIZED_FINITE_CAUSAL_TREE_DOMAIN_THEOREM_AND_MIXED_SIGN_NONDEFINITION",
        "result_state": "POLARIZED_FINITE_TREES_CERTIFIED_UNRESTRICTED_MIXED_AND_INFINITE_SERIES_OPEN",
        "lifecycle": "CLASSIFIED",
        "created": "2026-08-15",
        "repository_base_commit": "a10212695438b66626f72a468928320f7f3f2def",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "question": "Can the candidate first causal response be iterated on honest support spaces, and exactly which sign-decorated finite trees are uniformly defined?",
        "answer": "Yes for every finite all-retarded tree and every finite all-advanced tree. Bär's content-pinned Green theorem extends the represented parent Green maps to past-compact and future-compact smooth sources; the certified local transports and q2 preserve those classes. This closes the candidate's polarized finite-tree domain problem by structural induction. It does not define every mixed-sign tree: the first uniform failure occurs at the balanced four-leaf tree, where a retarded parent can receive two future-compact advanced children, or conversely. The S3 zero mode shows why the opposite-polarity improper Duhamel integral cannot be extended to the whole mismatched class. The result is candidate-scoped, finite-order, and neither an infinite perturbation series nor an authoritative interacting Weyl theory.",
        "scope": {
            "theory": "strict pure-Weyl stabilized q2 candidate",
            "background": "unit ultrastatic vacuum conformal cylinder R x S3",
            "carrier": "fixed 386-row graph BV carrier",
            "leaves": "compactly supported smooth homogeneous sections",
            "trees": "finite plane full binary q2/Green trees",
        },
        "analytic_extension_import": theorem_import,
        "support_algebra": support_algebra,
        "recursive_polarized_tree_theorem": recursive_theorem,
        "sign_decoration_census": census,
        "mixed_sign_boundary": mixed_boundary,
        "zero_mode_mismatch_witness": zero_mode_boundary,
        "foundational_strength": foundations,
        "authority_boundary": authority,
        "tree_domain_snapshot": snapshot,
        "claim_flags": flags,
        "does_not_establish": [
            "that the stabilized q2 candidate is the authoritative nonlinear classical Weyl BV operation",
            "an accepted q2 or recursive-tree hash in classical import Gate A",
            "uniform definition of every mixed advanced/retarded sign decoration",
            "unrestricted recursive iteration of B_causal=B_plus-B_minus on arbitrary binary topologies",
            "candidate-specific noncancellation of either four-leaf support witness",
            "q3 or higher L-infinity operations or their causal compatibility",
            "convergence, summability, a fixed point or a solution selected from the finite formal tree family",
            "effective seminorm constants, a spectral tail modulus or numerical Green solver",
            "a weakest reverse-mathematical, choice-free or Bishop-constructive proof of the analytic support theorem",
            "a BRST-compatible Hadamard state, positivity, renormalized Lorentzian products, QME restoration, residual transfer, unitarity or a Lorentzian quantum theory",
        ],
        "next_gate": "Keep authoritative q2 identity first. For the candidate analytic route, either introduce a weighted/decaying mixed support space that removes the zero-mode mismatch or use polarized retarded/advanced Møller trees; then establish tree-series estimates and import any q3/higher brackets before making an interacting or Hadamard claim.",
        "canonical_hashes": {
            "analytic_extension_import_sha256": theorem_import["sha256"],
            "support_algebra_sha256": support_algebra["sha256"],
            "recursive_polarized_tree_theorem_sha256": recursive_theorem["sha256"],
            "sign_decoration_census_sha256": digest(census),
            "mixed_sign_boundary_sha256": mixed_boundary["sha256"],
            "zero_mode_mismatch_witness_sha256": zero_mode_boundary["sha256"],
            "foundational_strength_sha256": foundations["sha256"],
            "authority_boundary_sha256": authority["sha256"],
            "tree_domain_snapshot_sha256": snapshot["sha256"],
        },
        "provenance": {
            "inputs": [
                {"path": str(path.relative_to(ROOT)), "result_or_artifact_id": expected, "sha256": sha(path), "role": role}
                for path, expected, role in INPUTS
            ]
        },
        "independent_checker": {
            "path": "quantum-weyl/classical_import/check_strict_386_recursive_causal_tree_domains.py",
            "checks": [
                "all source identities and content hashes",
                "Bär Theorem 3.8 and spatially compact cylinder import contract",
                "PC/FC/compact intersection and Green-domain algebra",
                "all-finite polarized structural induction",
                "independent Catalan/sign recurrence through ten leaves",
                "minimal balanced four-leaf mixed-sign nondefinition",
                "opposite-polarity scalar zero-mode Duhamel divergence",
                "foundation, authority and quantum lifecycle firewalls",
            ],
        },
        "human_report": "quantum-weyl/classical_import/REPORT_STRICT_386_RECURSIVE_CAUSAL_TREE_DOMAINS_V1.md",
    }
    return value


def render(value: Mapping[str, Any]) -> str:
    theorem = value["analytic_extension_import"]
    tree = value["recursive_polarized_tree_theorem"]
    mixed = value["mixed_sign_boundary"]
    lines = [
        "# Strict 386-row recursive causal-tree domains v1", "", "## Outcome", "",
        value["answer"], "", "## The support-space repair", "",
        f"The content-pinned `{theorem['source_id']}` `{theorem['theorem']}` supplies `{theorem['retarded_extension']}` and `{theorem['advanced_extension']}`. {theorem['cylinder_specialization']}", "",
        "The graph homotopies inherit these domains because every surrounding BGG, shear, endpoint, SDR and q2 map is finite-order and support-local. On fixed time-support steps the maps are continuous; no unindexed global joint-LF claim is needed.", "",
        "## What now closes", "",
        f"- All finite retarded plane binary trees: **{tree['retarded']['all_finite_plane_binary_trees']}**.",
        f"- All finite advanced plane binary trees: **{tree['advanced']['all_finite_plane_binary_trees']}**.",
        f"- Support-domain defects: **{tree['finite_tree_support_domain_defects']}**.",
        f"- Infinite tree series: **{tree['formal_power_series']}**.", "",
        "## Mixed-sign census", "",
        "| Leaves | Tree topologies | All signings | Admissible | Not uniformly defined |", "|---:|---:|---:|---:|---:|",
    ]
    for row in value["sign_decoration_census"]:
        lines.append(f"| {row['leaves']} | {row['plane_binary_tree_topologies']} | {row['all_sign_decorations']} | {row['admissible_total']} | {row['not_uniformly_defined']} |")
    lines += [
        "", "The first failure is the balanced four-leaf topology:", "",
        "```text", *mixed["minimal_witnesses"], "```", "",
        "This means polarized retarded/advanced Møller trees close, while a naive arbitrary iteration of `B_causal` does not. The scalar S3 zero mode supplies an opposite-polarity improper-integral divergence witness; it is not asserted to lie in the image of the actual candidate q2. This support-domain nondefinition is not a no-go theorem against smaller weighted or decaying mixed domains.", "",
        "## Foundational split", "", value["foundational_strength"]["finite_exact_layer"], "", value["foundational_strength"]["analytic_layer"], "", value["foundational_strength"]["infinite_layer"], "",
        "## Reproduction", "", "```text",
        "python3 quantum-weyl/classical_import/build_strict_386_recursive_causal_tree_domains.py --check",
        "python3 quantum-weyl/classical_import/check_strict_386_recursive_causal_tree_domains.py",
        "python3 quantum-weyl/classical_import/verify_strict_386_recursive_causal_tree_domains.py",
        "python3 -m unittest quantum-weyl/classical_import/tests/test_strict_386_recursive_causal_tree_domains.py",
        "```", "", "## Boundaries", "",
    ]
    lines.extend(f"- This does not establish {item}." for item in value["does_not_establish"])
    lines += ["", "## Next gate", "", value["next_gate"], ""]
    return "\n".join(lines)


def generated() -> tuple[bytes, bytes]:
    value = build()
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode(), render(value).encode()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result, report = generated()
    stale = [
        str(path.relative_to(ROOT))
        for path, content in ((RESULT, result), (REPORT, report))
        if not path.is_file() or path.read_bytes() != content
    ]
    if args.check:
        print("STRICT_386_RECURSIVE_CAUSAL_TREE_DOMAINS_V1: " + ("generated artifacts current" if not stale else "stale: " + ", ".join(stale)))
        return bool(stale)
    RESULT.write_bytes(result)
    REPORT.write_bytes(report)
    print("STRICT_386_RECURSIVE_CAUSAL_TREE_DOMAINS_V1: wrote result and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
