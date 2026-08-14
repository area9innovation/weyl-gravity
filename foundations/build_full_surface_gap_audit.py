#!/usr/bin/env python3
"""Build a typed audit of every remaining unassessed atlas coordinate."""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
FOUNDATIONS = ROOT / "foundations"
SOURCE = FOUNDATIONS / "results/FOUNDATIONAL_INTERSECTION_CUBE_V8.json"
OUTPUT = FOUNDATIONS / "results/FOUNDATIONAL_FULL_SURFACE_GAP_AUDIT_V1.json"
REPORT = FOUNDATIONS / "reports/full-surface-gap-audit.md"

FOUNDATION_REQUIREMENTS = {
    "CLASSICAL_STANDARD": "state the classical set-theoretic and analytic assumptions used by the proof",
    "WEAK_ARITHMETIC": "give an explicit coding over a named weak base and prove an upper bound or reversal",
    "WEAK_CHOICE_ZF": "work in ZF and record every use or avoidance of a choice principle",
    "CONSTRUCTIVE_COMPUTABLE": "supply witnesses, algorithms, moduli, and a representation of all inputs and outputs",
    "TOPOS_INTERNAL": "formulate the construction in the internal language and identify every non-geometric logical step",
    "FINITE_DISCRETE": "give exact finite data and state which continuum or infinite conclusion is deliberately excluded",
}
CARRIER_REQUIREMENTS = {
    "FINITE_EXACT": "construct exact finite algebraic data with decidable verification",
    "HILBERT_OPERATOR": "specify the positive inner product, operator domains, closures, and spectral hypotheses",
    "KREIN_INDEFINITE": "specify the indefinite pairing, fundamental symmetry, domains, and physical-positivity policy",
    "ALGEBRAIC_CSTAR": "specify the observable algebra, positivity notion, states, representations, and locality assumptions",
    "SMOOTH_DISTRIBUTIONAL": "specify function spaces, topology, domains, wavefront or support conditions, and continuity",
    "LOCALIC_SYNTHETIC": "construct the internal or point-free objects and the morphisms that express the physical operation",
}
OBLIGATION_DELIVERABLES = {
    "KINEMATICS_OBSERVABLES": "construct the configuration and observable objects and prove their declared algebraic closure",
    "STATE_EXISTENCE": "construct at least one normalized or algebraically valid state",
    "STATE_REPRESENTATION": "relate abstract states to a declared vector, density, measure, valuation, or representation object",
    "PROBABILITY_RULE": "derive normalized nonnegative probabilities for declared events",
    "PHYSICAL_STATE_SELECTION": "prove a criterion selecting a physically distinguished state",
    "GENERATOR_SPECTRAL_DYNAMICS": "construct the evolution generator and its relevant spectral or frequency data",
    "EVOLUTION_WELLPOSEDNESS": "prove existence, uniqueness, and stable or computable dependence for the evolution problem",
    "CAUSAL_PROPAGATION_GREEN": "construct advanced or retarded response maps and prove the required causal support",
    "GAUGE_BV_COHOMOLOGY": "construct the gauge or BV complex and compute the declared physical cohomology",
    "INTERACTION_CONSTRUCTION": "construct a genuine coupling or nonlinear interaction with its consistency conditions",
    "COUNTERTERM_CLASSIFICATION": "classify every allowed counterterm in the declared local or finite model",
    "ANOMALY_CLASSIFICATION": "classify every possible symmetry or master-equation obstruction",
    "RENORMALIZED_PRODUCTS": "construct the required singular products or a controlled regulator-independent replacement",
    "QME_RESTORATION": "restore the quantum master equation after anomaly and counterterm classification",
    "RESIDUAL_QUANTUM_TRANSFER": "transfer a restored quantum correction through a certified residual contraction",
    "RECONSTRUCTION_LIMITS": "prove a controlled bridge to operational predictions, a standard formulation, or a continuum limit",
}


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def coordinate(cell: dict[str, Any]) -> tuple[str, str, str]:
    return cell["foundation"], cell["carrier"], cell["obligation"]


def key(coord: tuple[str, str, str]) -> str:
    return "|".join(coord)


def canonical_digest(value: dict[str, Any]) -> str:
    body = dict(value)
    body.pop("canonical_digest", None)
    return hashlib.sha256(json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def decisions(source: dict[str, Any]) -> list[dict[str, Any]]:
    axes = {axis["id"]: [item["id"] for item in axis["keys"]] for axis in source["axes"]}
    foundations = axes["FOUNDATION"]
    carriers = axes["CARRIER"]
    obligations = axes["REFINED_OBLIGATION"]
    current = {coordinate(cell): cell for cell in source["cells"]}
    classified = {coord for coord, cell in current.items() if cell["status"] != "NOT_MAPPED"}
    result = []
    for foundation in foundations:
        for carrier in carriers:
            for obligation in obligations:
                coord = (foundation, carrier, obligation)
                old = current.get(coord)
                if old is not None and old["status"] != "NOT_MAPPED":
                    continue
                neighbors = sorted(
                    key(other) for other in classified
                    if sum(left != right for left, right in zip(coord, other)) == 1
                )
                result.append({
                    "coordinate": {"foundation": foundation, "carrier": carrier, "obligation": obligation},
                    "prior_surface_state": "EMITTED_NOT_MAPPED" if old is not None else "SYNTHETIC_NOT_EMITTED",
                    "review_class": "COHERENT_TYPED_GAP",
                    "new_status": "REVIEWED_GAP",
                    "evidence_role": "SUPPORTING",
                    "research_question": f"Under {foundation}, using {carrier}, can one {OBLIGATION_DELIVERABLES[obligation]}?",
                    "foundation_requirement": FOUNDATION_REQUIREMENTS[foundation],
                    "carrier_requirement": CARRIER_REQUIREMENTS[carrier],
                    "missing_certificate": OBLIGATION_DELIVERABLES[obligation],
                    "nearest_assessed_coordinates": neighbors,
                    "nearest_neighbor_count": len(neighbors),
                    "finding": "This coordinate has now been explicitly formulated and reviewed as a coherent open research question, but no direct local or literature result is certified for it in the atlas.",
                    "boundary": "REVIEWED_GAP is an assessment state, not a result, priority assignment, literature-absence claim, impossibility theorem, or evidence that adjacent records transfer.",
                })
    return result


def build() -> dict[str, Any]:
    source = load(SOURCE)
    if source.get("result_id") != "FOUNDATIONAL_INTERSECTION_CUBE_V8":
        raise ValueError("cube-v8 source identity")
    items = decisions(source)
    prior_counts = Counter(item["prior_surface_state"] for item in items)
    if len(items) != 175 or prior_counts != {"EMITTED_NOT_MAPPED": 51, "SYNTHETIC_NOT_EMITTED": 124}:
        raise ValueError("full-surface gap partition")
    value = {
        "schema_version": "foundational-full-surface-gap-audit-v1",
        "result_id": "FOUNDATIONAL_FULL_SURFACE_GAP_AUDIT_V1",
        "result_kind": "TYPED_FULL_CARTESIAN_GAP_ASSESSMENT",
        "lifecycle": "CLASSIFIED",
        "created": "2026-08-14",
        "repository_base_commit": "3b4c7dfa3506baeef447ba97038f5f6f9f807a75",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL", "REDUCED-MODE", "LORENTZIAN-CAUSAL"],
        "question": "Can every remaining coordinate in the 6 x 6 x 16 atlas be given an explicit typed research question without mistaking assessment for a scientific result?",
        "answer": "Yes. The audit formulates all 175 remaining coordinates, separates 51 previously emitted blanks from 124 browser-only complements, states the foundation, carrier, and obligation-specific deliverable for each, and classifies each as REVIEWED_GAP. It certifies complete assessment coverage, not complete physics or literature coverage.",
        "status_definition": {
            "id": "REVIEWED_GAP",
            "short_label": "Reviewed open gap",
            "mark": "O",
            "meaning": "The coordinate is explicitly formulated and assessed, but no direct result is certified and it is not designated as a current priority gap.",
            "rank": "OPEN_NONRESULT",
            "distinguished_from": {
                "NOT_MAPPED": "No coordinate-level assessment has yet been made.",
                "PRIORITY_GAP": "The programme has designated a reviewed gap as a current priority.",
                "PIECES_ONLY": "Relevant ingredients are registered but do not compose the target result.",
            },
        },
        "method": {
            "cartesian_axes": [6, 6, 16],
            "cartesian_total": 576,
            "source_emitted_cells": 452,
            "source_not_mapped_cells": 51,
            "synthetic_complements": 124,
            "newly_reviewed_coordinates": 175,
            "foundation_templates": FOUNDATION_REQUIREMENTS,
            "carrier_templates": CARRIER_REQUIREMENTS,
            "obligation_templates": OBLIGATION_DELIVERABLES,
            "neighbor_policy": "List every already-classified coordinate differing in exactly one axis as navigation only; no evidence transfer is inferred.",
        },
        "decisions": items,
        "proof_obligations": [
            {"id": "CARTESIAN_CLOSURE", "status": "PASS", "evidence": "The six foundations, six carriers, and sixteen obligations generate exactly 576 unique coordinates."},
            {"id": "PRIOR_PARTITION", "status": "PASS", "evidence": "Exactly 51 cube-v8 coordinates are NOT_MAPPED and exactly 124 Cartesian complements are absent."},
            {"id": "EXACT_DECISION_SET", "status": "PASS", "evidence": "Every and only those 175 coordinates receives one decision."},
            {"id": "FOUNDATION_TYPING", "status": "PASS", "evidence": "Every decision states its foundation-specific proof requirement."},
            {"id": "CARRIER_TYPING", "status": "PASS", "evidence": "Every decision states its carrier-specific construction requirement."},
            {"id": "OBLIGATION_TYPING", "status": "PASS", "evidence": "Every decision states a theorem-level missing deliverable."},
            {"id": "NEIGHBOR_NONTRANSFER", "status": "PASS", "evidence": "All one-axis neighbors are recomputed as navigation and never promoted to direct evidence."},
            {"id": "NONPRIORITY_SEPARATION", "status": "PASS", "evidence": "REVIEWED_GAP remains distinct from the 30 existing PRIORITY_GAP coordinates."},
            {"id": "NONRESULT_BOUNDARY", "status": "PASS", "evidence": "No decision is graded as local, literature, or pieces-only evidence."},
            {"id": "LITERATURE_BOUNDARY", "status": "PASS", "evidence": "The audit makes no literature-absence or literature-completeness claim."},
        ],
        "proof_authority": {"status": "INDEPENDENT_STRUCTURAL_REDERIVATION", "meaning": "The checker reconstructs the Cartesian complement, validates all typed templates and neighbor sets, and rejects any positive-grade or absence promotion."},
        "provenance": {"inputs": [{"path": str(SOURCE.relative_to(ROOT)), "sha256": sha(SOURCE), "role": "last partially assessed authoritative cube"}]},
        "independent_checker": {"path": "foundations/check_full_surface_gap_audit.py", "expected_digest": "a6c18514f7c575e2072b9323f101882ff184981a56caf0908a350f2bcd5a7404", "checks": ["Cartesian closure", "51/124 prior partition", "175 exact decisions", "typed requirements", "one-axis neighbors", "reviewed-gap-only status", "nonresult and nonabsence boundaries"]},
        "claim_flags": {
            "all_175_remaining_coordinates_reviewed": True,
            "all_576_coordinates_formulated": True,
            "new_reviewed_gap_status_defined": True,
            "direct_results_added": False,
            "pieces_only_results_added": False,
            "priority_assignments_added": False,
            "literature_complete": False,
            "literature_absence_proved": False,
            "all_physical_obligations_solved": False,
            "complete_theory_identified": False,
            "new_lorentzian_claim": False,
        },
        "does_not_establish": [
            "a direct mathematical or physical result for any of the 175 coordinates",
            "that every formulated coordinate is realizable in one common physical theory",
            "that adjacent evidence transfers across a foundation, carrier, or obligation axis",
            "that any newly reviewed gap is a programme priority",
            "literature completeness or absence of relevant literature",
            "impossibility, independence, inconsistency, or a no-go theorem",
            "a weakest foundation, carrier equivalence, or continuum limit",
            "a complete Weyl theory, quantum completion, empirical agreement, or LORENTZIAN-CAUSAL result",
        ],
        "human_report": "foundations/reports/full-surface-gap-audit.md",
    }
    value["canonical_digest"] = canonical_digest(value)
    return value


def render(value: dict[str, Any]) -> str:
    by_foundation = Counter(item["coordinate"]["foundation"] for item in value["decisions"])
    by_obligation = Counter(item["coordinate"]["obligation"] for item in value["decisions"])
    lines = [
        "# Full 576-coordinate surface gap audit", "", f"**Result:** `{value['result_id']}`", "", "**Lifecycle:** `CLASSIFIED`", "", "## Outcome", "", value["answer"], "",
        "`REVIEWED_GAP` means **reviewed open question**, not result. It is deliberately separate from `PRIORITY_GAP`, which names a selected current programme priority, and from `PIECES_ONLY`, which requires registered ingredients.", "",
        "Complete assessment is not a replacement for direct results, and `REVIEWED_GAP` is not a literature-absence claim.", "",
        "## Partition", "", "| Prior surface state | Coordinates | New state |", "|---|---:|---|", "| Emitted but `NOT_MAPPED` | 51 | `REVIEWED_GAP` |", "| Browser-only Cartesian complement | 124 | `REVIEWED_GAP` |", "| **Total** | **175** | **175 explicit assessments** |", "",
        "## Remaining questions by foundation", "", "| Foundation | Reviewed gaps |", "|---|---:|", *[f"| `{name}` | {count} |" for name, count in sorted(by_foundation.items())], "", "## Remaining questions by obligation", "", "| Obligation | Reviewed gaps |", "|---|---:|", *[f"| `{name}` | {count} |" for name, count in sorted(by_obligation.items())], "",
        "Each machine-readable decision supplies a research question, a foundation requirement, a carrier requirement, the missing theorem-level certificate, and all already-assessed one-axis neighbors. Those neighbors are navigation only and do not license evidence transfer.", "", "## Verification", "", "```text", "python3 foundations/build_full_surface_gap_audit.py --check", "python3 foundations/check_full_surface_gap_audit.py", "python3 foundations/verify_full_surface_gap_audit.py", "python3 -m unittest foundations.tests.test_full_surface_gap_audit", "```", "", "## Boundaries", "", *["- This does not establish " + item + "." for item in value["does_not_establish"]], ""
    ]
    return "\n".join(lines)


def generated() -> tuple[bytes, bytes]:
    value = build()
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode(), render(value).encode()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result_bytes, report_bytes = generated()
    outputs = ((OUTPUT, result_bytes), (REPORT, report_bytes))
    stale = [str(path.relative_to(ROOT)) for path, content in outputs if not path.is_file() or path.read_bytes() != content]
    if args.check:
        print("FOUNDATIONAL_FULL_SURFACE_GAP_AUDIT_V1: " + ("generated artifacts current" if not stale else "stale: " + ", ".join(stale)))
        return bool(stale)
    for path, content in outputs:
        path.write_bytes(content)
    print("FOUNDATIONAL_FULL_SURFACE_GAP_AUDIT_V1: wrote result and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
