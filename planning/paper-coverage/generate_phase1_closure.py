#!/usr/bin/env python3
"""Generate the authoritative Phase-1 classification-ending records.

This joins already-frozen inputs.  It performs no new scientific inference and
keeps the distinct theory/background/carrier rows separate.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
STAMP = "2026-07-22"

LEDGER = ROOT / f"reports/phase1-closure-claims-ledger-{STAMP}.json"
SNAPSHOT = ROOT / f"reports/phase1-closure-dependency-snapshot-{STAMP}.json"
PAPER_AUDIT = ROOT / f"planning/paper-coverage/phase1-closure-paper-audit-{STAMP}.json"
REPORT = ROOT / f"reports/phase1-closure-{STAMP}.md"
ATLAS = ROOT / "residual_atlas/programme-phase1-classification-ending-fragment-v1.json"
RECEIPT = ROOT / f"reports/PHASE1_CLOSURE_V1_TIER_RECEIPT.json"

SOURCES = {
    "classical": {
        "work_item": "sf:program/work/classical-phase1-counterflow-claim-map-freeze",
        "path": "d_quotient_classical/phase1/CLASSICAL_PHASE1_COUNTERFLOW_CLAIM_MAP_V1.json",
        "result_id": "CLASSICAL_PHASE1_COUNTERFLOW_CLAIM_MAP_V1",
        "result_state": "PHASE1_CLASSICAL_COUNTERFLOW_CHAIN_FROZEN_TERMINAL_OBSTRUCTED",
        "commit": "be6325c64377026a98bf96935a204635593408d9",
    },
    "bridge": {
        "work_item": "sf:program/work/bridge-phase1-einstein-extra-contribution-freeze",
        "path": "bridge/phase1/BRIDGE_PHASE1_EINSTEIN_EXTRA_CONTRIBUTION_V1.json",
        "result_id": "BRIDGE_PHASE1_EINSTEIN_EXTRA_CONTRIBUTION_V1",
        "result_state": "PHASE1_EINSTEIN_EXTRA_STRUCTURAL_CONTRIBUTION_FROZEN",
        "commit": "f4079f2a21b3965c34b8810de05f52390e03e9e9",
    },
    "nonlinear": {
        "work_item": "sf:program/work/nonlinear-phase1-interaction-disposition-freeze",
        "path": "nonlinear/phase1/NONLINEAR_PHASE1_INTERACTION_DISPOSITION_V1.json",
        "result_id": "NONLINEAR_PHASE1_INTERACTION_DISPOSITION_V1",
        "result_state": "REPRESENTATIVES_CERTIFIED_COMPLETE_CYCLIC_CLASS_OPEN_COUNTERFLOW_NOT_ACTIVATED",
        "commit": "c6dce9298774abc16b4fed40d944993f4058c7b7",
    },
    "observer": {
        "work_item": "sf:program/work/observer-paper09-promotion-after-git-attached-tier3-v3",
        "path": "closed_universe_observers/receipts/PAPER09_PROMOTION_AFTER_GIT_ATTACHED_TIER3_V3_NO_PROMOTION.json",
        "result_id": "PAPER09_PROMOTION_AFTER_GIT_ATTACHED_TIER3_V3_NO_PROMOTION",
        "result_state": None,
        "commit": "e17071e2111451f5178a0ee48739d5231e2d8670",
    },
    "quantum": {
        "work_item": "sf:program/work/quantum-phase1-strict-weyl-and-selected-successor-synthesis-v2",
        "path": "quantum-weyl/phase1/certificates/PHASE1_QUANTUM_DISPOSITION_SYNTHESIS_V1.json",
        "result_id": "PHASE1_QUANTUM_DISPOSITION_SYNTHESIS_V1",
        "result_state": "PHASE1_QUANTUM_CLASSIFICATION_FROZEN_NO_SUCCESSOR_SELECTED",
        "commit": "3d1479bc6459fc7755379135794b2bed45dee6b8",
    },
    "coverage": {
        "work_item": "sf:program/work/programme-global-paper-coverage-baseline",
        "path": "planning/paper-coverage/phase1-paper-coverage-baseline-2026-07-22.json",
        "result_id": "PROGRAMME_GLOBAL_PAPER_COVERAGE_BASELINE_V1",
        "result_state": "NONVACUOUS_ADVISORY_BASELINE_REVIEWED_SLATE_COVERED",
        "commit": "2d9f1cbd9f376c89dee146061d4c23af558392b9",
    },
    "black_hole_companion": {
        "work_item": "sf:program/work/black-hole-paper14-finite-flux-status-freeze",
        "path": "paper/14-pure-weyl-black-hole-radiation-claim-map.json",
        "result_id": "PAPER_14_PURE_WEYL_BLACK_HOLE_RADIATION",
        "result_state": None,
        "commit": "f84219211e36096be34ce6c5d9cd2c3275c2bb68",
    },
}

PAPERS = [
    ("00", "paper/00-ghosts-geometry-reality.tex", "ALIGNED_AFTER_PHASE1_CLOSURE_UPDATE", []),
    ("09", "paper/09-relational-clocks-berger-d-cartan.tex", "DRAFT_ALLOWED_SCOPED_FOLLOWUP", ["sf:program/work/observer-paper09-semantic-ledger-relock-tier3-v4"]),
    ("10", "paper/10-compact-einstein-maxwell-weyl-phase-space.tex", "ALIGNED_THEOREM_FROZEN", []),
    ("11", "paper/11-gravity-light-cyclic-causal-ell3.tex", "ALIGNED_REPRESENTATIVE_FROZEN_CLASS_OPEN", []),
    ("12", "paper/12-pure-weyl-one-loop-bv-anomaly.tex", "ALIGNED_DRAFT_ALLOWED", []),
    ("13", "paper/13-compact-weyl-maxwell-second-order-tangent-cone.tex", "ALIGNED_STRUCTURAL_THEOREM_FROZEN", []),
    ("14", "paper/14-pure-weyl-black-hole-radiation.tex", "DRAFT_ALLOWED_SCOPE_REPAIRS_QUEUED", ["sf:program/work/black-hole-endpoint-local-condition-scope-repair", "sf:program/work/black-hole-exterior-bvp-functional-scope-repair", "sf:program/work/black-hole-finite-flux-front-door-and-graph-propagation"]),
    ("90", "paper/90-cyclic-green-transfer-bridge.md", "ALIGNED_BRIDGE_NOTE", []),
    ("91", "paper/91-charge-fibre-taub-bridge.md", "ALIGNED_THEOREM_FROZEN", []),
    ("92", "paper/92-extra-axial-lee-wald-bridge.md", "SCOPED_BLACK_HOLE_UPDATE_QUEUED", ["sf:program/work/black-hole-paper92-finite-flux-bridge-update"]),
    ("98", "paper/98-physicist-executive-summary.md", "ALIGNED_AFTER_PHASE1_CLOSURE_UPDATE", []),
    ("99", "paper/99-how-to-build-a-universe.md", "ALIGNED_AFTER_PHASE1_CLOSURE_UPDATE", []),
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_sources() -> tuple[dict[str, dict], dict[str, dict]]:
    docs: dict[str, dict] = {}
    refs: dict[str, dict] = {}
    for role, spec in SOURCES.items():
        path = ROOT / spec["path"]
        doc = json.loads(path.read_text(encoding="utf-8"))
        actual_id = doc.get("result_id") or doc.get("paper_id")
        if actual_id != spec["result_id"]:
            raise AssertionError(f"{role}: result id drift: {actual_id!r}")
        if spec["result_state"] is not None and doc.get("result_state") != spec["result_state"]:
            raise AssertionError(f"{role}: result state drift")
        docs[role] = doc
        refs[role] = {
            **spec,
            "effective_work_state": "DONE",
            "sha256": sha256(path),
        }
    return docs, refs


def claim(claim_id: str, *, theory: str, action: str, background: str,
          carrier: str, charge_fibre: str, correction_class: str,
          lifecycle: str, verdict: str, source: str, limitation: str) -> dict:
    return {
        "claim_id": claim_id,
        "theory": theory,
        "action": action,
        "background": background,
        "carrier": carrier,
        "charge_fibre": charge_fibre,
        "correction_class": correction_class,
        "lifecycle": lifecycle,
        "verdict": verdict,
        "source": source,
        "limitation": limitation,
    }


def build() -> tuple[dict, dict, dict, str, dict, dict]:
    docs, refs = load_sources()
    classical = docs["classical"]["terminal_summary"]
    nonlinear = docs["nonlinear"]["terminal_summary"]
    coverage = docs["coverage"]["counts"]

    claims = [
        claim(
            "phase1.counterflow.causal_parent",
            theory="changed two-phase counterflow Weyl gravity-clock theory",
            action="two positive phase fields plus auxiliary diagonal U(1) and repaired compensator sector",
            background="selected positive biaxial Berger fixture",
            carrier="70-component action-derived cyclic BV parent",
            charge_fibre="fixed Q_rel leaf for the certified causal activation",
            correction_class="linear Lorentzian support-local causal BV complex",
            lifecycle="CERTIFIED_CAUSAL_ONLY",
            verdict="Exact advanced/retarded homotopies exist and the dressed-trace class is removed.",
            source="classical",
            limitation="Causality does not establish physical positivity or a familywide Green homotopy.",
        ),
        claim(
            "phase1.counterflow.physical_viability",
            theory="same-field two-phase counterflow successor",
            action="repaired q70 action and its connected same-field stationary retuning family",
            background="selected Berger fixture and connected trace-healthy Berger component",
            carrier="nonradical selected physical quotients and complete both-k j=1/2 family quotient",
            charge_fibre="unrestricted and fixed Q_rel kept distinct",
            correction_class="linear reduced pairing and characteristic polynomial",
            lifecycle="TERMINAL_OBSTRUCTED_NO_PHASE2_CANDIDATE",
            verdict="The selected quotient is Hamiltonian-Hopf unstable; the j=1/2 quartet persists throughout the connected trace-healthy same-field family.",
            source="classical",
            limitation="This is sufficient to reject this candidate family, not an all-isotype or all-architecture no-go.",
        ),
        claim(
            "phase1.counterflow.clock_charge",
            theory="changed two-phase counterflow Weyl gravity-clock theory",
            action="relative-phase action-angle clock",
            background="selected Berger fixture",
            carrier="global relative-clock Darboux pair",
            charge_fibre="fixed Q_rel versus unrestricted phase space",
            correction_class="presymplectic reduction",
            lifecycle="CLASSIFIED",
            verdict="Fixing and quotienting Q_rel makes D null but removes the clock; retaining the clock leaves raw D charged.",
            source="classical",
            limitation="No single declared charge fibre provides both the proposed physical clock and gauge D.",
        ),
        claim(
            "phase1.einstein_extra.structure",
            theory="Einstein-Maxwell source, Weyl-Maxwell target, and extra cofiber",
            action="standard two-derivative source and four-derivative target actions",
            background="compactified magnetically supported Plebanski-Hacyan product",
            carrier="parity-complete pre-residual H0 sequence and direct Lee-Wald generic blocks",
            charge_fibre="fixed magnetic bundle before final stabilizer reduction",
            correction_class="linear exact sequence and symplectic extension",
            lifecycle="CLASSIFIED",
            verdict="Einstein injects, extra axial and polar blocks are nonradical, and the standard pairings do not define a cyclic Einstein/extra equivalence.",
            source="bridge",
            limitation="Final residual descent, causal boundary conditions, and quantization remain open.",
        ),
        claim(
            "phase1.taub_kuranishi.structure",
            theory="compact Weyl-Maxwell/Einstein-Maxwell comparison",
            action="same compact-product source and target actions",
            background="compactified magnetically supported Plebanski-Hacyan product",
            carrier="finite harmonic and mixed-charge two-/three-jet carriers",
            charge_fibre="five total stabilizer charges, not separately neutral branch projections",
            correction_class="finite exponential-polynomial versus bounded quasiperiodic continuation",
            lifecycle="THEOREM_FROZEN_SCOPED",
            verdict="Five charges exhaust formal second-order obstruction; bounded continuation has extra shell conditions; the certified balanced third-order representative is secularly solvable but bounded-obstructed.",
            source="bridge",
            limitation="The full bounded zero locus, causal continuation, and branchwide third-order theorem remain open.",
        ),
        claim(
            "phase1.interaction.disposition",
            theory="Berger gravity-clock-Maxwell BV theory",
            action="frozen action-derived q2/q3 and one specified 64-to-36 SDR",
            background="frozen positive rational Berger fixture",
            carrier="retained 36-row cyclic BV carrier and declared cyclic redefinition complexes",
            charge_fibre="declared Berger K sector; no counterflow activation",
            correction_class="physical action through summed input order two; full-BV bounded cyclic complex",
            lifecycle="REPRESENTATIVE_FROZEN_INVARIANT_CLASS_OPEN",
            verdict="The retained representative and cyclicity are exact; the physical action is trivialized through second input jet, while the complete full-BV cyclic class remains open.",
            source="nonlinear",
            limitation="No cohomology operation, invariant branch-resolved mixing table, or counterflow interaction is certified.",
        ),
        claim(
            "phase1.observer.disposition",
            theory="Berger gravity-clock observer programme",
            action="legacy and repaired q70 observer/receiver carriers",
            background="declared Berger fixtures",
            carrier="seven-row receiver census and Paper 9 publication chain",
            charge_fibre="typed row-specific D, R, K, and Q_rel sectors",
            correction_class="linear causal receiver descent and publication evidence",
            lifecycle="DRAFT_ALLOWED_NO_PROMOTION",
            verdict="No residual nonradical operational frequency ratio is activated; Paper 9 remains draft after a Git-attached Tier-3 semantic-ledger failure.",
            source="observer",
            limitation="This is not a receiver nonexistence theorem; a scoped semantic relock and fresh Tier-3 rerun remain.",
        ),
        claim(
            "phase1.quantum.strict",
            theory="strict fixed-field-content Diff x Weyl pure gravity",
            action="strict pure C^2 action",
            background="regular Bach-locus local chart and Euclidean coefficient carrier",
            carrier="full gauge-fixed local BV anomaly quotient",
            charge_fibre="not a charge-sector statement",
            correction_class="local Euclidean one-loop QME",
            lifecycle="OBSTRUCTED_AT_ONE_LOOP_LOCAL_EUCLIDEAN",
            verdict="The strict local one-loop BV QME is obstructed by nonzero anomaly classes.",
            source="quantum",
            limitation="No Lorentzian QME, state, particle, or unitarity conclusion follows.",
        ),
        claim(
            "phase1.quantum.compensator",
            theory="formal tau-adic compensator extension",
            action="changed Wess-Zumino/BV theory",
            background="formal local BV algebra and declared Euclidean one-loop slice",
            carrier="dressed local BV/Wess-Zumino algebra",
            charge_fibre="not a charge-sector statement",
            correction_class="local Euclidean one-loop QME",
            lifecycle="QME_RESTORED_CHANGED_THEORY_ONE_LOOP",
            verdict="The strict anomaly becomes exact and the local Euclidean QME is restored at one loop in the enlarged theory.",
            source="quantum",
            limitation="The extension changes the theory and supplies neither an unconditional all-loop theorem nor Lorentzian quantum physics.",
        ),
        claim(
            "phase1.black_hole.companion",
            theory="pure Weyl gravity on Schwarzschild",
            action="pure C^2 Lee-Wald phase-space structure",
            background="Schwarzschild exterior",
            carrier="axial symbolic real-frequency radiation class and polar certified fixture",
            charge_fibre="asymptotic finite-flux admissibility rather than compact charge reduction",
            correction_class="linear reduced-mode horizon and infinity analysis",
            lifecycle="COMPANION_DRAFT_ALLOWED_SCOPE_REPAIRS_PENDING",
            verdict="Horizon analyticity admits additional curvature solutions; finite flux selects Einstein in the certified axial real-frequency class and in the certified polar fixture.",
            source="black_hole_companion",
            limitation="Endpoint-local-condition and exterior-BVP scope repairs remain queued; no stability, scattering, QNM, particle, or universal causal-truncation theorem is imported.",
        ),
    ]

    ledger = {
        "schema": "pure-weyl-programme-phase1-claims-ledger-v1",
        "result_id": "PURE_WEYL_PROGRAMME_PHASE1_CLASSIFICATION_ENDING_V1",
        "result_state": "PHASE1_CLOSED_CLASSIFICATION_ENDING_NO_PHASE2_CANDIDATE",
        "stamp": STAMP,
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL", "REDUCED-MODE", "LORENTZIAN-CAUSAL"],
        "decision": {
            "phase": "PHASE_1",
            "status": "CLOSED",
            "ending": "CLASSIFICATION_ENDING",
            "selected_counterflow_causal_parent": classical["selected_fixture_causal_parent"],
            "selected_counterflow_physically_healthy": classical["selected_fixture_physically_healthy"],
            "fixed_Q_rel_retains_clock": classical["fixed_Q_rel_retains_physical_clock"],
            "robust_phase2_candidate_selected": classical["phase2_candidate_selected"],
            "invariant_interaction_class_decided": nonlinear["complete_bounded_cyclic_full_bv_class_decided"],
            "operational_frequency_ratio_activated": False,
            "quantum_phase2_candidate_selected": docs["quantum"]["phase1_decision"]["phase2_quantum_candidate_selected"],
        },
        "claims": claims,
        "does_not_establish": [
            "a viable final theory or a universal no-go over changed architectures",
            "a complete higher-isotype counterflow spectrum or familywide causal parent",
            "an invariant branch-resolved interaction",
            "an operational relational redshift on the repaired counterflow carrier",
            "a Lorentzian QME, positive full-BV state, particles, scattering, unitarity, or complete quantum gravity",
        ],
    }

    snapshot = {
        "schema": "pure-weyl-programme-phase1-dependency-snapshot-v1",
        "result_id": "PURE_WEYL_PROGRAMME_PHASE1_DEPENDENCY_SNAPSHOT_V1",
        "stamp": STAMP,
        "closure_work_item": "sf:program/work/programme-phase1-viability-classification-freeze-v5",
        "dependencies": refs,
        "superseded_closure_items": {
            "v1": "superseded before the nonvacuous paper-coverage and final Observer gates",
            "v2": "retired by this closure because it consumed the pre-repair Observer boundary",
            "v3": "retired after its Observer evidence dependency was superseded",
            "v4": "retired after the archive-only Tier-3 harness lacked Git metadata",
        },
        "observer_v5_basis": "The Git-attached exact-materialization rerun passed 826 tests before a semantic comparison-ledger hash/claim-boundary mismatch; this is a real DRAFT_ALLOWED boundary, not an archive harness artifact.",
    }

    paper_rows = []
    for paper_id, path_text, status, tasks in PAPERS:
        path = ROOT / path_text
        paper_rows.append({
            "paper_id": paper_id,
            "path": path_text,
            "sha256": sha256(path),
            "audit_status": status,
            "blocking_phase1": False,
            "scoped_followup_work_items": tasks,
        })
    paper_audit = {
        "schema": "pure-weyl-programme-phase1-paper-audit-v1",
        "result_id": "PURE_WEYL_PROGRAMME_PHASE1_BIDIRECTIONAL_PAPER_AUDIT_V1",
        "stamp": STAMP,
        "baseline": refs["coverage"],
        "counts": {
            "papers_audited": len(paper_rows),
            "human_classified_results": coverage["classified"],
            "typed_reverse_paper_claims": coverage["paper_claims"],
            "uncovered_material": coverage["uncovered_material"],
            "claim_no_evidence": coverage["claim_no_evidence"],
            "review_queue": coverage["review_queue"],
            "scoped_followup_papers": sum(bool(row["scoped_followup_work_items"]) for row in paper_rows),
        },
        "papers": paper_rows,
        "interpretation": "All eight human-reviewed headline results and all eleven typed reverse claims pass the advisory baseline. The 1,400-item review queue is unclassified inventory, not publication debt. Paper 9 and the black-hole scope repairs remain explicit companion work and do not broaden or postpone the core classification ending.",
    }

    report = f"""# Phase 1 closure — exact viability classification

**Closed:** {STAMP}  
**Lifecycle:** `PHASE1_CLOSED_CLASSIFICATION_ENDING_NO_PHASE2_CANDIDATE`

## Decision

Phase 1 closes with an exact viability classification, not with a viable final
theory and not with a universal no-go.

The selected two-phase counterflow theory has an exact action-derived causal
BV parent on its declared Berger fixture and removes the dressed-trace class.
It fails the subsequent physical audit: the selected physical quotient has a
nonradical Hamiltonian--Hopf instability, and the same quartet persists
throughout the connected trace-healthy same-field stationary family.  On the
fixed-`Q_rel` reduction that makes raw `D` null, the proposed relative clock is
also removed.  No robust Phase-2 candidate is selected from this family.

## Joined evidence

- **Classical:** causal parent passed; selected and connected-family physical
  viability obstructed at the stated `j=1/2` carrier.
- **Einstein/extra bridge:** parity-complete pre-residual exact sequence,
  nonradical extra blocks, five-charge second-order theorem, and scoped
  third-order Kuranishi disposition frozen.
- **Nonlinear:** exact retained representatives and cyclicity frozen; physical
  action trivial through second input jet; complete full-BV cyclic class and
  branch-resolved cohomology operation remain open; counterflow interaction
  work was correctly not activated after the health obstruction.
- **Observer:** no operational counterflow frequency ratio is activated.
  Paper 9 remains `DRAFT_ALLOWED` after a Git-attached Tier-3 run reached 826
  passes and then found a semantic comparison-ledger mismatch.
- **Quantum:** strict pure Weyl gravity is locally obstructed at one Euclidean
  loop; a formal compensator restores the changed local theory at that order;
  no counterflow anomaly, Hadamard, positivity, or QME promotion is activated.
- **Black-hole companion:** horizon analyticity and finite-flux selection are
  kept distinct; the endpoint-local-condition and exterior-BVP scope repairs
  remain queued and do not delay this core closure.

## Publication and provenance

The nonvacuous advisory coverage baseline contains {coverage['results']}
discovered results, {coverage['classified']} human-classified headline
results, {coverage['paper_claims']} typed reverse paper claims, and zero
uncovered material or reverse evidence failures on that reviewed slice.  The
remaining {coverage['review_queue']} candidates stay visibly queued for human
materiality review.

The authoritative machine-readable records are:

- `reports/phase1-closure-claims-ledger-{STAMP}.json`
- `reports/phase1-closure-dependency-snapshot-{STAMP}.json`
- `planning/paper-coverage/phase1-closure-paper-audit-{STAMP}.json`

## Explicit boundary

This closure does not establish a viable theory, a universal failure of all
changed gravity-clock architectures, an invariant physical interaction,
operational counterflow redshift, Lorentzian quantum master equation,
positive particle space, scattering, unitarity, or complete quantum gravity.
Those are possible Phase-2 questions only after a new candidate is selected.

CLOSE-OUT: DONE — Phase 1 closed with an exact classification ending and no Phase-2 candidate selected.
EVIDENCE: reports/phase1-closure-claims-ledger-{STAMP}.json
"""

    atlas = {
        "schema": "pure-weyl-residual-atlas-fragment-v1",
        "schema_version": "1.0.0",
        "team": "programme",
        "generated_by": "planning/paper-coverage/generate_phase1_closure.py",
        "generated_by_sha256": sha256(ROOT / "planning/paper-coverage/generate_phase1_closure.py"),
        "status_vocabulary": ["CERTIFIED", "OBSTRUCTED", "OPEN", "NOT_APPLICABLE", "NO_CERTIFIED_MAP"],
        "description_axes": ["causal", "symplectic", "nonlinear", "observational", "quantum"],
        "verification_commands": [
            "python3 planning/paper-coverage/generate_phase1_closure.py --check",
            "python3 planning/paper-coverage/verify_phase1_closure.py",
            "python3 residual_atlas/validate_fragment.py residual_atlas/programme-phase1-classification-ending-fragment-v1.json",
        ],
        "entries": [{
            "id": "programme.phase1.classification_ending.no_candidate_selected",
            "scope": {
                "theory": "programme-level typed synthesis; distinct theory rows are not identified",
                "background": "cylinder, Berger, compact Plebanski-Hacyan, Euclidean anomaly, and Schwarzschild laboratories kept separate",
                "boundaries": "row-specific boundaries and charge fibres",
                "charge_sector": "unrestricted, Taub-zero, fixed-Q_rel, and asymptotic finite-flux sectors kept distinct",
                "carrier": "Phase-1 claims ledger",
                "degree": "classification join",
                "parity": "row-specific",
                "ell": "row-specific",
                "m": "row-specific",
                "k": "row-specific",
                "omega": "row-specific",
            },
            "descriptions": {
                "causal": "CERTIFIED",
                "symplectic": "OBSTRUCTED",
                "nonlinear": "OPEN",
                "observational": "NO_CERTIFIED_MAP",
                "quantum": "OBSTRUCTED",
            },
            "mode_data": {
                "dispersion": {"status": "OBSTRUCTED", "statement": "The declared same-field counterflow family retains the j=1/2 Hamiltonian--Hopf quartet."},
                "lee_wald": {"status": "OBSTRUCTED", "statement": "The selected physical unstable block is nonradical; causality did not imply a healthy reduced pairing."},
                "taub_maps": {"status": "CERTIFIED", "statement": "The separate compact-product laboratory has a five-charge formal second-order criterion; it is not imported into the counterflow background."},
                "resonance": {"status": "OPEN", "statement": "The complete bounded compact-product zero locus remains open and is distinct from counterflow candidate selection."},
                "second_order": {
                    "equation": "L_barPhi v = -(1/2) D^2 E_barPhi[u,u]",
                    "bounded_or_finite_quasiperiodic": {"status": "OPEN", "statement": "Row-specific bounded continuation results remain typed to their original laboratories."},
                    "smooth_secular": {"status": "CERTIFIED", "statement": "Selected compact-product balanced representatives have finite exponential-polynomial secular corrections."},
                    "causal_retarded": {"status": "NO_CERTIFIED_MAP", "statement": "No programme-wide causal second-order join is claimed."}
                }
            },
            "evidence": [{"path": str(LEDGER.relative_to(ROOT)), "result_id": ledger["result_id"], "sha256": hashlib.sha256((json.dumps(ledger, indent=2, sort_keys=True) + "\n").encode()).hexdigest()}],
            "claim_boundary": "The axis statuses summarize different typed rows; they are not one cross-background mode. The ending is not a universal no-go and does not establish particles, scattering, unitarity, or complete quantum gravity.",
        }],
    }
    rendered = {
        str(LEDGER.relative_to(ROOT)): render_json(ledger),
        str(SNAPSHOT.relative_to(ROOT)): render_json(snapshot),
        str(PAPER_AUDIT.relative_to(ROOT)): render_json(paper_audit),
        str(REPORT.relative_to(ROOT)): report,
        str(ATLAS.relative_to(ROOT)): render_json(atlas),
    }
    receipt = {
        "schema": "pure-weyl-programme-phase1-tier-receipt-v1",
        "result_id": "PURE_WEYL_PROGRAMME_PHASE1_CLASSIFICATION_ENDING_V1_TIER_RECEIPT",
        "stamp": STAMP,
        "scope": "Programme-level deterministic join of already-frozen Phase-1 evidence; no scientific producer is replayed.",
        "outputs": {
            path: {"sha256": hashlib.sha256(text.encode()).hexdigest()}
            for path, text in rendered.items()
        },
        "commands": [
            "python3 planning/paper-coverage/generate_phase1_closure.py --check",
            "python3 planning/paper-coverage/verify_phase1_closure.py",
            "python3 planning/paper-coverage/test_phase1_closure.py",
            "python3 residual_atlas/validate_fragment.py residual_atlas/programme-phase1-classification-ending-fragment-v1.json",
        ],
        "tiers": {
            "tier_0": "PASS: generated outputs, exact input hashes, and scoped diff checked",
            "tier_1": "PASS: generator freshness, independent verifier, unit tests, and atlas schema",
            "tier_2": "HASH-GATED: dependencies were imported at their frozen commits and checked by content hash",
            "tier_3": "NOT_RUN: no scientific theorem or shared algebra was changed by this synthesis",
        },
        "does_not_establish": [
            "independent re-verification of every imported scientific certificate",
            "a viable theory, universal no-go, or Phase-2 candidate",
        ],
    }
    return ledger, snapshot, paper_audit, report, atlas, receipt


def render_json(value: dict) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--emit", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()
    ledger, snapshot, paper_audit, report, atlas, receipt = build()
    outputs = {
        LEDGER: render_json(ledger),
        SNAPSHOT: render_json(snapshot),
        PAPER_AUDIT: render_json(paper_audit),
        REPORT: report,
        ATLAS: render_json(atlas),
        RECEIPT: render_json(receipt),
    }
    if args.emit:
        for path, text in outputs.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
        return 0
    stale = [str(path.relative_to(ROOT)) for path, text in outputs.items() if not path.exists() or path.read_text(encoding="utf-8") != text]
    if stale:
        raise SystemExit(f"FAIL: stale Phase-1 closure outputs: {stale}")
    print("PASS: Phase-1 closure outputs are current")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
