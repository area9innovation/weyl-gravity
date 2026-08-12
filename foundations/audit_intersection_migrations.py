#!/usr/bin/env python3
"""Generate the explicit v1-to-v2 migration decision ledger.

This is a review rail, not a literature producer.  It consumes the 112 v1
MIGRATION_UNRESOLVED cells and requires every one to match either a reviewed
evidence batch or an explicit empty-parent child-gap rule.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
FOUNDATIONS = ROOT / "foundations"
V0 = FOUNDATIONS / "results/FOUNDATIONAL_INTERSECTION_CUBE_V0.json"
V1 = FOUNDATIONS / "results/FOUNDATIONAL_INTERSECTION_CUBE_V1.json"
OUTPUT = FOUNDATIONS / "results/FOUNDATIONAL_INTERSECTION_CUBE_MIGRATION_AUDIT_V2.json"
REPORT = FOUNDATIONS / "reports/intersection-cube-migration-audit-v2.md"
LEDGERS = [
    FOUNDATIONS / "literature-ledger.json",
    FOUNDATIONS / "literature-supplement-known-attempts-v1.json",
    FOUNDATIONS / "literature-expansion-v2.json",
]
LOCAL_INPUTS = [
    FOUNDATIONS / "results/FOUNDATIONAL_EXPLICIT_ENERGY_SPECTRAL_FRAGMENT_ZF_V1.json",
    FOUNDATIONS / "results/FOUNDATIONAL_KREIN_EXPLICIT_J_ZF_V1.json",
]

EVIDENCE_BATCHES: dict[tuple[str, ...], tuple[str, str]] = {
    ("heunen-landsman-spitters-2009", "doring-2008", "brenna-flori-2012", "harding-heunen-2019"): ("TOPOS_CONTEXT_STATE_DYNAMICS", "Internal spectra, state measures, and one-parameter dynamics are reviewed; the records explicitly exclude causal propagation and interacting/renormalized field theory."),
    ("gibbons-hoffman-wootters-2004", "abramsky-coecke-2004", "constantin-doring-2020"): ("FINITE_QUANTUM_RECONSTRUCTION", "Finite phase-space, categorical protocol, and state-reconstruction results do not establish evolution well-posedness, causal propagation, or quantum field consistency obligations."),
    ("coquand-spitters-2009", "heunen-landsman-spitters-2009", "brenna-flori-2012"): ("CONSTRUCTIVE_TOPOS_DYNAMICS", "Constructive duality and internal one-parameter dynamics do not transfer to causal Green theory or interacting/renormalized field theory."),
    ("harding-heunen-2019", "constantin-doring-2020", "abramsky-coecke-2004"): ("FINITE_CONTEXTUAL_TOPOS", "Finite contextual and categorical structures do not establish causal propagation or the six quantum-consistency children."),
    ("FOUNDATIONAL_KREIN_EXPLICIT_J_ZF_V1", "mostafazadeh-2001", "gottschalk-2004"): ("ZF_KREIN_SPECTRAL_QFT", "The explicit Krein carrier, pseudo-Hermitian structure, and axiomatic indefinite-metric QFT do not construct the unresolved interaction or quantum-consistency children."),
    ("bender-boettcher-1998", "mostafazadeh-2001", "gottschalk-2004"): ("PT_KREIN_QFT", "Real-spectrum and indefinite-metric QFT results do not establish the unresolved interaction or quantum-consistency children."),
    ("blackadar-farah-karagila-2026", "blackadar-farah-2026", "neumann-pape-streicher-2018"): ("ZF_OPERATOR_FOUNDATIONS", "ZF operator theory and effective spectral representation do not establish interacting QFT, renormalized products, anomalies, QME restoration, or residual transfer."),
    ("neumann-pape-streicher-2018", "abramsky-coecke-2004"): ("EFFECTIVE_CATEGORICAL_QUANTUM", "Effective spectral representation and categorical protocols do not establish the unresolved field-interaction and quantum-consistency children."),
    ("neumann-pape-streicher-2018", "pour-el-richards-1981", "bridges-svozil-2000", "richman-bridges-1999"): ("CONSTRUCTIVE_HILBERT_FOUNDATIONS", "Constructive probability, Hilbert logic, effective spectra, and a representation-sensitive wave counterexample do not establish interacting or renormalized QFT children."),
    ("grinkevich-1996", "barnich-brandt-henneaux-2000"): ("SYNTHETIC_GEOMETRY_LOCAL_BRST", "Synthetic classical geometry and local BRST classification do not construct or represent states, probabilities, or a physical state-selection rule."),
    ("kogut-susskind-1975", "zohar-burrello-2014", "bahr-dittrich-2009", "dittrich-2012"): ("LATTICE_DISCRETE_DYNAMICS", "Lattice constraints and continuum-comparison programmes do not by themselves construct the four unresolved state/probability children."),
    ("bender-boettcher-1998", "mostafazadeh-2001"): ("PT_PSEUDOHERMITIAN_SPECTRAL", "PT-symmetric and pseudo-Hermitian spectral structure does not supply state representation, normalized probabilities, or causal Green propagation."),
    ("brown-simpson-1986", "humphreys-simpson-1999", "humphreys-simpson-1996", "brattka-2008"): ("REVERSE_FUNCTIONAL_ANALYSIS", "Logical-strength results for separation and Hahn-Banach principles do not construct a generator, well-posed evolution, or a causal Green operator."),
    ("grinkevich-1996",): ("SYNTHETIC_GENERAL_RELATIVITY", "The reviewed synthetic Einstein-equation formulation does not construct spectral generators, prove evolution well-posedness, or provide causal Green maps."),
    ("FOUNDATIONAL_EXPLICIT_ENERGY_SPECTRAL_FRAGMENT_ZF_V1",): ("ENERGY_SPECTRAL_FRAGMENT", "The exact energy spectrum is a reduced-mode spectral result and explicitly does not establish causal support or a Green operator."),
    ("barnich-brandt-henneaux-2000", "brunetti-fredenhagen-verch-2001", "fredenhagen-rejzner-2011", "brunetti-fredenhagen-rejzner-2013"): ("AQFT_BV_ARCHITECTURE", "AQFT state-space and BV-renormalization architecture does not derive a normalized probability rule for the Weyl metric theory."),
    ("coquand-spitters-2009", "henry-2014", "neumann-pape-streicher-2018"): ("LOCALIC_EFFECTIVE_SPECTRAL", "Localic duality and effective spectral representation do not construct localized causal Green propagation."),
    ("doring-2008", "brenna-flori-2012", "harding-heunen-2019"): ("TOPOS_STATE_INTERNAL_DYNAMICS", "State measures and internal one-parameter groups do not establish spacetime support or causal Green propagation."),
}

CHILD_NO_TRANSFER = {
    "STATE_EXISTENCE": "No reviewed record in the batch constructs a state in this refined coordinate.",
    "STATE_REPRESENTATION": "No reviewed record in the batch supplies the required state representation in this refined coordinate.",
    "PROBABILITY_RULE": "No reviewed record in the batch derives the required normalized event-probability rule.",
    "PHYSICAL_STATE_SELECTION": "No reviewed record in the batch selects a vacuum, thermal, Hadamard, or other physical state.",
    "GENERATOR_SPECTRAL_DYNAMICS": "No reviewed record in the batch constructs the required generator or spectral dynamics in this refined coordinate.",
    "EVOLUTION_WELLPOSEDNESS": "No reviewed record in the batch proves existence, uniqueness, stability, or computability of the required evolution.",
    "CAUSAL_PROPAGATION_GREEN": "No reviewed record in the batch constructs advanced/retarded maps with causal support.",
    "INTERACTION_CONSTRUCTION": "No reviewed record in the batch constructs the required interaction in this refined coordinate.",
    "COUNTERTERM_CLASSIFICATION": "No reviewed record in the batch classifies counterterms in this refined coordinate.",
    "ANOMALY_CLASSIFICATION": "No reviewed record in the batch classifies anomalies in this refined coordinate.",
    "RENORMALIZED_PRODUCTS": "No reviewed record in the batch constructs renormalized products in this refined coordinate.",
    "QME_RESTORATION": "No reviewed record in the batch restores the quantum master equation in this refined coordinate.",
    "RESIDUAL_QUANTUM_TRANSFER": "No reviewed record in the batch transfers a restored quantum correction to the residual complex.",
}

GAP_NAMES = {
    "GENERATOR_SPECTRAL_DYNAMICS": "a constructive smooth-wave generator with declared domains and representation",
    "INTERACTION_CONSTRUCTION": "an interaction construction in the declared foundational regime and smooth carrier",
    "COUNTERTERM_CLASSIFICATION": "a child-specific local counterterm classification",
    "ANOMALY_CLASSIFICATION": "a child-specific anomaly classification",
    "RENORMALIZED_PRODUCTS": "renormalized products in the declared foundational regime and carrier",
    "QME_RESTORATION": "restoration of the local quantum master equation",
    "RESIDUAL_QUANTUM_TRANSFER": "a quantum correction transferred to the residual complex after QME restoration",
}


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def coordinate(cell: dict[str, Any]) -> str:
    return "|".join(cell[key] for key in ("foundation", "carrier", "obligation"))


def canonical_digest(decisions: list[dict[str, Any]]) -> str:
    payload = [(x["coordinate"], x["v0_parent_status"], x["review_batch"], x["decision"], x["resulting_coverage_status"], x["parent_evidence"]) for x in decisions]
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def build() -> dict[str, Any]:
    v0, v1 = load(V0), load(V1)
    parents = {(x["foundation"], x["carrier"], x["obligation"]): x for x in v0["cells"]}
    pending = [x for x in v1["cells"] if x["status"] == "MIGRATION_UNRESOLVED"]
    observed_batches = {tuple(x["evidence"]) for x in pending if x["evidence"]}
    if observed_batches != set(EVIDENCE_BATCHES):
        missing = observed_batches - set(EVIDENCE_BATCHES)
        stale = set(EVIDENCE_BATCHES) - observed_batches
        raise ValueError(f"evidence batch closure failed; missing={missing}, stale={stale}")
    decisions = []
    for cell in pending:
        parent = parents[(cell["foundation"], cell["carrier"], cell["parent_obligation"])]
        if cell["evidence"]:
            batch_id, batch_basis = EVIDENCE_BATCHES[tuple(cell["evidence"])]
            decision = {
                "coordinate": coordinate(cell),
                "foundation": cell["foundation"], "carrier": cell["carrier"], "obligation": cell["obligation"],
                "parent_obligation": cell["parent_obligation"], "v0_parent_status": parent["status"],
                "parent_evidence": cell["evidence"], "review_batch": batch_id,
                "review_priority": "RESULT_DESCENDANT_FIRST" if parent["status"] in {"LOCAL_RESULT", "LITERATURE_RESULT"} else "PIECES_DESCENDANT_BATCH",
                "decision": "REVIEWED_NO_TRANSFER", "resulting_coverage_status": "NOT_MAPPED",
                "rationale": batch_basis + " " + CHILD_NO_TRANSFER[cell["obligation"]],
                "boundary": "This reviews only transfer of the named parent evidence. NOT_MAPPED is not a literature-absence claim and does not show that the coordinate is incoherent.",
            }
        else:
            if cell["obligation"] not in GAP_NAMES or parent["status"] != "PRIORITY_GAP":
                raise ValueError("unhandled empty-evidence migration " + coordinate(cell))
            decision = {
                "coordinate": coordinate(cell),
                "foundation": cell["foundation"], "carrier": cell["carrier"], "obligation": cell["obligation"],
                "parent_obligation": cell["parent_obligation"], "v0_parent_status": parent["status"],
                "parent_evidence": [], "review_batch": "EMPTY_PARENT_GAP_DECOMPOSITION",
                "review_priority": "EMPTY_PARENT_GAP_DECOMPOSITION",
                "decision": "REVIEWED_CHILD_GAP", "resulting_coverage_status": "PRIORITY_GAP",
                "rationale": "The broad v0 priority gap is coherent at this child: the current corpus lacks " + GAP_NAMES[cell["obligation"]] + ".",
                "boundary": "This is a reviewed programme gap in the current corpus, not proof of literature absence, impossibility, necessity, or a no-go theorem.",
            }
        decisions.append(decision)
    decisions.sort(key=lambda x: x["coordinate"])
    counts = Counter(x["decision"] for x in decisions)
    priorities = Counter(x["review_priority"] for x in decisions)
    batch_counts = Counter(x["review_batch"] for x in decisions)
    pins = [V0, V1, *LEDGERS, *LOCAL_INPUTS]
    return {
        "schema_version": "foundational-intersection-cube-migration-audit-v2",
        "result_id": "FOUNDATIONAL_INTERSECTION_CUBE_MIGRATION_AUDIT_V2",
        "result_kind": "EXPLICIT_MIGRATION_DECISION_LEDGER",
        "lifecycle": "SEPARATED",
        "created": "2026-08-12",
        "repository_base_commit": "24e988693bd9ee6874bedf9de476202c949a2e7e",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE", "LORENTZIAN-CAUSAL"],
        "purpose": "Clear every v1 migration uncertainty without promoting parent evidence across refined child boundaries.",
        "method": {
            "coverage_and_migration_are_separate": True,
            "evidence_batch_count": len(EVIDENCE_BATCHES),
            "review_rule": "A parent evidence set transfers only when its recorded supported statements and boundaries treat the child. Otherwise migration is reviewed-no-transfer and coverage remains NOT_MAPPED.",
            "empty_gap_rule": "An evidence-free v0 priority gap becomes a child priority gap only after the child missing object is stated explicitly.",
        },
        "summary": {
            "v1_pending": len(pending), "decisions": len(decisions),
            "decision_counts": dict(sorted(counts.items())),
            "priority_counts": dict(sorted(priorities.items())),
            "evidence_batch_counts": dict(sorted(batch_counts.items())),
            "pending_after_audit": 0,
        },
        "evidence_batches": [
            {"id": batch_id, "evidence": list(evidence), "reviewed_scope": basis, "cell_count": batch_counts[batch_id], "decision": "NO_TRANSFER_TO_LISTED_UNRESOLVED_CHILDREN"}
            for evidence, (batch_id, basis) in EVIDENCE_BATCHES.items()
        ],
        "decisions": decisions,
        "provenance": {"inputs": [{"path": str(path.relative_to(ROOT)), "sha256": sha(path)} for path in pins]},
        "independent_checker": {"path": "foundations/check_intersection_migration_audit.py", "checks": ["112-coordinate closure", "v1 pending partition", "v0 parent reconstruction", "18 evidence batches", "12 result-descendant priority cases", "76 pieces batches", "24 child-gap decompositions", "decision/status boundary", "canonical digest"], "expected_digest": canonical_digest(decisions)},
        "claim_flags": {"all_v1_pending_reviewed": True, "coverage_separated_from_migration": True, "parent_results_blindly_inherited": False, "reviewed_no_transfer_means_literature_absent": False, "child_gap_means_impossible": False, "new_lorentzian_claim": False},
        "does_not_establish": ["literature completeness", "that a reviewed-no-transfer coordinate has no supporting literature", "that every Cartesian coordinate is coherent", "a weakest mathematical base", "a new physical result", "a new Lorentzian-causal result"],
        "human_report": "foundations/reports/intersection-cube-migration-audit-v2.md",
    }


def render(result: dict[str, Any]) -> str:
    s = result["summary"]
    lines = [
        "# Refined-cube migration audit v2", "", f"**Result:** `{result['result_id']}`", "",
        "## Outcome", "",
        f"All **{s['v1_pending']}** v1 migration-pending cells have explicit decisions. The audit records **{s['decision_counts']['REVIEWED_NO_TRANSFER']} reviewed no-transfer** decisions and **{s['decision_counts']['REVIEWED_CHILD_GAP']} reviewed child gaps**. Pending after audit: **0**.", "",
        "Coverage and migration are now different fields. A reviewed parent source that does not treat a child clears the migration question but leaves coverage `NOT_MAPPED`. This is not a literature-absence claim, and it does not create a gap.", "",
        "## Workload decomposition", "",
        "| Review class | Cells | Outcome |", "|---|---:|---|",
        f"| Descendants of v0 direct results | {s['priority_counts']['RESULT_DESCENDANT_FIRST']} | Reviewed first; all are no-transfer under their recorded boundaries. |",
        f"| Descendants of v0 pieces-only cells | {s['priority_counts']['PIECES_DESCENDANT_BATCH']} | Reviewed in {result['method']['evidence_batch_count']} repeated evidence batches; all are no-transfer to the listed unresolved children. |",
        f"| Evidence-free v0 parent gaps | {s['priority_counts']['EMPTY_PARENT_GAP_DECOMPOSITION']} | Decomposed into explicit child priority gaps. |", "",
        "## Evidence batches", "", "| Batch | Cells | Evidence |", "|---|---:|---|",
    ]
    for batch in sorted(result["evidence_batches"], key=lambda x: (-x["cell_count"], x["id"])):
        lines.append(f"| `{batch['id']}` | {batch['cell_count']} | {', '.join(batch['evidence'])} |")
    lines += ["", "## Result-descendant reviews", "", "| Coordinate | Parent status | Decision | Rationale |", "|---|---|---|---|"]
    for item in result["decisions"]:
        if item["review_priority"] == "RESULT_DESCENDANT_FIRST":
            lines.append(f"| `{item['coordinate']}` | `{item['v0_parent_status']}` | `{item['decision']}` | {item['rationale']} |")
    lines += ["", "## Reproduction", "", "```text", "python3 foundations/audit_intersection_migrations.py --check", "python3 foundations/check_intersection_migration_audit.py", "python3 foundations/verify_intersection_migration_audit.py", "```", "", "## Boundaries", ""]
    lines.extend(f"- This does not establish {item}." for item in result["does_not_establish"])
    return "\n".join(lines) + "\n"


def generated() -> tuple[bytes, bytes]:
    result = build()
    return (json.dumps(result, indent=2, ensure_ascii=False) + "\n").encode(), render(result).encode()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result, report = generated()
    expected = [(OUTPUT, result), (REPORT, report)]
    stale = [str(path.relative_to(ROOT)) for path, content in expected if not path.is_file() or path.read_bytes() != content]
    if args.check:
        if stale:
            print("FOUNDATIONAL_INTERSECTION_CUBE_MIGRATION_AUDIT_V2: stale: " + ", ".join(stale))
            return 1
        print("FOUNDATIONAL_INTERSECTION_CUBE_MIGRATION_AUDIT_V2: generated artifacts current")
        return 0
    for path, content in expected:
        path.write_bytes(content)
    print("FOUNDATIONAL_INTERSECTION_CUBE_MIGRATION_AUDIT_V2: wrote result and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
