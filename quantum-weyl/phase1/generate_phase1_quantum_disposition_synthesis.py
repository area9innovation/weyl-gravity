#!/usr/bin/env python3
"""Generate the terminal Phase 1 quantum disposition synthesis."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
PHASE1 = ROOT / "quantum-weyl/phase1"
CERT = PHASE1 / "certificates/PHASE1_QUANTUM_DISPOSITION_SYNTHESIS_V1.json"
ATLAS = ROOT / "residual_atlas/phase1-quantum-disposition-synthesis-fragment-v1.json"
MATERIALITY = ROOT / "planning/paper-coverage/quantum-phase1-dispositions-2026-07-21.json"
REPORT = ROOT / "quantum-weyl/reports/phase1-quantum-disposition-synthesis-v1.md"

SOURCES = {
    "paper12_claim_map": ROOT / "paper/12-pure-weyl-one-loop-bv-anomaly-claim-map.json",
    "paper12_v3_receipt": ROOT / "quantum-weyl/relative/receipts/PAPER12_RELATIVE_OFFSHELL_ACTION_OBSTRUCTION_UPDATE_V3_TIER_RECEIPT.json",
    "minimal_ladder": ROOT / "d_quotient_classical/compensator/COMPENSATOR_MINIMAL_LADDER_SYNTHESIS_AFTER_LEVEL3B_V1.json",
    "minimal_ladder_receipt": ROOT / "d_quotient_classical/receipts/COMPENSATOR_MINIMAL_LADDER_SYNTHESIS_AFTER_LEVEL3B_V1_TIER_RECEIPT.json",
    "counterflow_viability": ROOT / "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_PHASE1_VIABILITY_CLASSIFICATION_V1.json",
    "counterflow_viability_receipt": ROOT / "d_quotient_classical/compensator/receipts/TWO_PHASE_COUNTERFLOW_PHASE1_VIABILITY_CLASSIFICATION_V1_TIER_RECEIPT.json",
    "berger_spectral_receiver": ROOT / "quantum-weyl/spectral/euclidean/certificates/BERGER_SCHUR_SPECTRAL_RECEIVER_NONDEFINITION_V1.json",
    "berger_spectral_receiver_receipt": ROOT / "quantum-weyl/transfer/receipts/BERGER_SCHUR_SPECTRAL_RECEIVER_NONDEFINITION_V1_TIER_RECEIPT.json",
    "paper12_v1_blocked_event": ROOT / "planning/events/quantum-paper12-relative-offshell-action-obstruction-update-BLOCKED-244d192067300dc0.json",
    "paper12_v2_blocked_event": ROOT / "planning/events/quantum-paper12-relative-offshell-action-obstruction-update-v2-BLOCKED-f94c920cdc796f68.json",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dump(value: Any) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()


def source_ref(path: Path, data: dict[str, Any]) -> dict[str, str]:
    return {
        "path": str(path.relative_to(ROOT)),
        "result_id": str(data.get("result_id") or data.get("id")),
        "sha256": sha(path),
    }


def lifecycle(
    state: str,
    dependency_tags: list[str],
    coefficient: str,
    qme: str,
    hadamard: str,
    selected_action: bool,
) -> dict[str, Any]:
    return {
        "state": state,
        "dependency_tags": dependency_tags,
        "coefficient_status": coefficient,
        "qme_status": qme,
        "hadamard_status": hadamard,
        "selected_action": selected_action,
    }


def scope(theory: str, background: str, carrier: str, charge: str) -> dict[str, str]:
    return {
        "theory": theory,
        "background": background,
        "boundaries": "declared local chart or compact Cauchy slices exactly as stated by the cited source",
        "charge_sector": charge,
        "carrier": carrier,
        "degree": "ghost number 1, form degree 4 unless explicitly marked classical or spectral",
        "parity": "even and odd tracked separately",
        "ell": "NOT_APPLICABLE_OR_NOT_EXPORTED",
        "m": "NOT_APPLICABLE_OR_NOT_EXPORTED",
        "k": "NOT_APPLICABLE_OR_NOT_EXPORTED",
        "omega": "NOT_APPLICABLE_OR_NOT_EXPORTED",
    }


def atlas_mode_data(
    *,
    dispersion: tuple[str, str],
    lee_wald: tuple[str, str],
    taub: tuple[str, str],
    resonance: tuple[str, str],
    bounded: tuple[str, str],
    secular: tuple[str, str],
    causal: tuple[str, str],
) -> dict[str, Any]:
    claim = lambda item: {"status": item[0], "statement": item[1]}  # noqa: E731
    return {
        "dispersion": claim(dispersion),
        "lee_wald": claim(lee_wald),
        "taub_maps": claim(taub),
        "resonance": claim(resonance),
        "second_order": {
            "equation": "L_barPhi v = -(1/2) D^2 E_barPhi[u,u]",
            "bounded_or_finite_quasiperiodic": claim(bounded),
            "smooth_secular": claim(secular),
            "causal_retarded": claim(causal),
        },
    }


def build() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], str]:
    data = {name: json.loads(path.read_text()) for name, path in SOURCES.items()}
    paper = data["paper12_claim_map"]
    ladder = data["minimal_ladder"]
    counterflow = data["counterflow_viability"]
    spectral = data["berger_spectral_receiver"]

    repair_rows = []
    for row in ladder["theory_space_table"]:
        repair_rows.append(
            {
                "family_id": row["family_id"],
                "terminal_verdict": row["terminal_verdict"],
                "action_scope": row["exact_action_ansatz"],
                "background_scope": row["exact_background_ansatz"],
                "selected_action": False,
                "quantum_promotions": {
                    "anomaly": "NOT_ACTIVATED",
                    "determinant": "NOT_ACTIVATED",
                    "qme": "NOT_ACTIVATED",
                    "hadamard": "NOT_ACTIVATED",
                },
                "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
            }
        )

    rows = [
        {
            "id": "STRICT_FIXED_FIELD_CONTENT_PURE_WEYL",
            "scope": scope(
                "strict fixed-field-content Diff x Weyl pure gravity",
                "regular Bach-locus local chart; Euclidean coefficient carrier",
                "full gauge-fixed local BV quotient; not a particle carrier",
                "not a charge-sector statement",
            ),
            "classical_imported": True,
            "brst_cocycle": "[omega C^2], [omega E4], [omega CdualC]",
            "brst_exactness": "three nonzero strict classes; omega BoxR exact",
            "pairing_status": "NOT_APPLICABLE_TO_LOCAL_ANOMALY_QUOTIENT",
            "complex_structure": "NO_CERTIFIED_MAP",
            "state_space": "NO_CERTIFIED_MAP",
            "lifecycle": lifecycle(
                "OBSTRUCTED",
                ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
                "COEFFICIENT_COMPUTED",
                "OBSTRUCTED_AT_ONE_LOOP_LOCAL_EUCLIDEAN",
                "NO_CERTIFIED_MAP",
                True,
            ),
            "exact_data": {
                "H14_even_dimension": paper["certified_claims"]["strict_full_gauge_fixed_H14_even_dimension"],
                "H14_odd_dimension": paper["certified_claims"]["strict_full_gauge_fixed_H14_odd_dimension"],
                "C2": paper["certified_claims"]["C2_coefficient"],
                "E4": paper["certified_claims"]["E4_coefficient"],
                "CdualC": paper["certified_claims"]["CdualC_coefficient"],
                "BoxR": paper["certified_claims"]["BoxR_coefficient"],
            },
            "does_not_establish": ["Lorentzian QME", "Hadamard state", "particle Hilbert space", "unitarity"],
        },
        {
            "id": "FORMAL_TAU_ADIC_COMPENSATOR_EXTENSION",
            "scope": scope(
                "formal tau-adic compensator extension of the strict action",
                "formal local BV algebra and declared Euclidean one-loop slice",
                "dressed local BV/Wess-Zumino algebra; not the strict quotient",
                "not a charge-sector statement",
            ),
            "classical_imported": True,
            "brst_cocycle": "strict anomaly vector imported into the enlarged formal algebra",
            "brst_exactness": "H_ext^(1,4)=0; the strict anomaly vector has a local Wess-Zumino primitive",
            "pairing_status": "NO_COMPLETE_TAU_ADIC_CAUSAL_PAIRING",
            "complex_structure": "NO_CERTIFIED_MAP",
            "state_space": "NO_CERTIFIED_MAP",
            "lifecycle": lifecycle(
                "QME_RESTORED",
                ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
                "COEFFICIENT_COMPUTED",
                "RESTORED_AT_ONE_LOOP_LOCAL_EUCLIDEAN; ALL_LOOP_ONLY_CONDITIONAL",
                "NO_CERTIFIED_MAP",
                True,
            ),
            "strict_equivalence": False,
            "equivalence_obstruction": "the passive dressed-trace class remains arbitrary and no complete causal tau-adic parent exists",
            "missing_inputs": {
                "actual_four_dimensional_regulator": paper["regulator_measure_status"]["actual_four_dimensional_regulator"],
                "dr_ms_module": paper["regulator_measure_status"]["dr_ms_strict_four_dimensional_module"],
                "global_anomalies_excluded": paper["explicit_nonclaims"]["global_anomalies_excluded"],
                "global_BRST_Hadamard_state": paper["explicit_nonclaims"]["global_BRST_Hadamard_state"],
                "renormalized_Lorentzian_products": paper["explicit_nonclaims"]["renormalized_Lorentzian_products"],
                "unconditional_all_loop_QME": paper["explicit_nonclaims"]["unconditional_all_loop_extended_QME"],
            },
            "does_not_establish": ["equivalence to strict Weyl gravity", "unconditional all-loop QME", "Lorentzian state", "unitarity"],
        },
        {
            "id": "SELECTED_RELATIVE_CHANGED_ACTION_REPAIR_ORBIT",
            "scope": scope(
                "action-changed Einstein-Q primary reduced theory",
                "declared compact magnetic product",
                "complete real parity-even Diff x U(1) local action quotient through four derivatives",
                "fixed-flux reduced carrier",
            ),
            "classical_imported": True,
            "brst_cocycle": "NOT_DEFINED_WITHOUT_CHANGED_MASTER_ACTION",
            "brst_exactness": "NOT_DEFINED",
            "pairing_status": "pairing-deformation orbit explicitly excluded",
            "complex_structure": "NO_CERTIFIED_MAP",
            "state_space": "NO_CERTIFIED_MAP",
            "lifecycle": lifecycle(
                "OBSTRUCTED",
                ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
                "NOT_COMPUTED",
                "UNDEFINED",
                "NO_CERTIFIED_MAP",
                False,
            ),
            "first_obstructions": paper["relative_offshell_changed_action_status"]["cokernel_witnesses"],
            "does_not_establish": ["changed master action", "relative anomaly coefficient", "relative QME", "Hadamard state"],
        },
        {
            "id": "TWO_PHASE_COUNTERFLOW_SUCCESSOR",
            "scope": scope(
                "same-field two-phase polar-clock Weyl action",
                "selected Berger causal fixture and connected trace-healthy same-field stationary family",
                "selected-fixture repaired q70 causal parent plus familywide j=1/2 physical quotient",
                "unrestricted and fixed Q_rel kept distinct",
            ),
            "classical_imported": True,
            "brst_cocycle": "NOT_ACTIVATED",
            "brst_exactness": "NOT_ACTIVATED",
            "pairing_status": "selected-fixture classical cyclic pairing only; no quantum promotion",
            "complex_structure": "NOT_ACTIVATED",
            "state_space": "NOT_ACTIVATED",
            "lifecycle": lifecycle(
                "NOT_ACTIVATED",
                ["LOCAL-ALGEBRAIC", "REDUCED-MODE", "LORENTZIAN-CAUSAL"],
                "NOT_COMPUTED",
                "NOT_ACTIVATED",
                "NOT_ACTIVATED",
                False,
            ),
            "classical_decision": counterflow["decision"],
            "quantum_promotions": {
                "action_specific_anomaly": "NOT_ACTIVATED",
                "determinant": "NOT_ACTIVATED",
                "qme": "NOT_ACTIVATED",
                "hadamard": "NOT_ACTIVATED",
            },
            "does_not_establish": counterflow["claim_boundary"]["does_not_establish"],
        },
        {
            "id": "SCALAR_FLAT_BERGER_SCHUR_METHOD",
            "scope": scope(
                "strict pure-Weyl Euclidean spectral method fixture",
                spectral["background_and_conventions"]["background"],
                "scalar-flat Berger Schur low blocks and partial-BV receiver",
                "primed scalar and one-form sectors only as explicitly exported",
            ),
            "classical_imported": True,
            "brst_cocycle": "NOT_APPLICABLE_METHOD_RESULT",
            "brst_exactness": "NOT_APPLICABLE_METHOD_RESULT",
            "pairing_status": "NOT_APPLICABLE_TO_PARTIAL_SPECTRAL_RECEIVER",
            "complex_structure": "NO_CERTIFIED_MAP",
            "state_space": "NO_CERTIFIED_MAP",
            "lifecycle": lifecycle(
                "CLASSIFIED",
                ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
                "NOT_COMPUTED",
                "UNDEFINED",
                "NO_CERTIFIED_MAP",
                False,
            ),
            "method_status": spectral["lifecycle_state"],
            "complete_carrier_functions": spectral["claim_flags"]["COMPLETE_FIVE_FUNCTIONS_COMPUTED"],
            "ordinary_B1_trace": "OBSTRUCTED_NOT_TRACE_CLASS",
            "does_not_establish": ["determinant", "anomaly coefficient", "QME", "Lorentzian Hadamard state"],
        },
    ]

    refs = {name: source_ref(SOURCES[name], data[name]) for name in SOURCES}
    cert = {
        "$schema": "../schema/phase1-quantum-disposition-synthesis-v1.schema.json",
        "schema": "phase1-quantum-disposition-synthesis-v1",
        "result_id": "PHASE1_QUANTUM_DISPOSITION_SYNTHESIS_V1",
        "result_state": "PHASE1_QUANTUM_CLASSIFICATION_FROZEN_NO_SUCCESSOR_SELECTED",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL", "REDUCED-MODE", "LORENTZIAN-CAUSAL"],
        "source_refs": refs,
        "theory_rows": rows,
        "minimal_repair_families": repair_rows,
        "phase1_decision": {
            "strict_fixed_field_content": "ONE_LOOP_LOCAL_BV_QME_OBSTRUCTED",
            "formal_tau_adic_extension": "ONE_LOOP_LOCAL_EUCLIDEAN_QME_RESTORED_IN_CHANGED_FORMAL_THEORY",
            "minimal_repair_union": ladder["result_state"],
            "counterflow_successor": "NOT_SELECTED_NO_ROBUST_STATIONARY_SAME_FIELD_CLOCK",
            "new_action_architecture_opened": False,
            "phase2_quantum_candidate_selected": False,
        },
        "mutation_expectations": {
            "strict_obstruction_promoted_to_restored": "REJECT",
            "tau_extension_identified_with_strict_theory": "REJECT",
            "conditional_all_loop_qme_promoted_to_unconditional": "REJECT",
            "terminal_repair_family_marked_selected": "REJECT",
            "counterflow_quantum_branch_activated": "REJECT",
            "berger_partial_spectral_method_called_qme": "REJECT",
            "relative_coefficient_invented": "REJECT",
            "stale_source_hash": "REJECT",
        },
        "provenance": {
            "source_commit": "9f5ad8cdf3e523cfd586cd22d9ba4179696727bc",
            "generator": "quantum-weyl/phase1/generate_phase1_quantum_disposition_synthesis.py",
            "generator_sha256": sha(Path(__file__)),
            "independent_verifier": "quantum-weyl/phase1/verify_phase1_quantum_disposition_synthesis.py",
        },
        "claim_boundary": (
            "This is a typed Phase 1 lifecycle synthesis, not a new coefficient calculation. It certifies the strict local one-loop obstruction, the changed formal tau-adic local restoration, terminal nonselection of every declared minimal repair family and the two-phase counterflow candidate, and nondefinition of the incomplete Berger spectral receiver. It does not establish strict/compensator equivalence, a changed-action anomaly coefficient, an unconditional all-loop or Lorentzian QME, a full-BV Hadamard state, particles, positivity, scattering or unitarity."
        ),
    }

    atlas = {
        "schema": "pure-weyl-residual-atlas-fragment-v1",
        "schema_version": "1.0.0",
        "team": "quantum",
        "generated_by": "quantum-weyl/phase1/generate_phase1_quantum_disposition_synthesis.py",
        "generated_by_sha256": sha(Path(__file__)),
        "status_vocabulary": ["CERTIFIED", "OBSTRUCTED", "OPEN", "NOT_APPLICABLE", "NO_CERTIFIED_MAP"],
        "description_axes": ["causal", "symplectic", "nonlinear", "observational", "quantum"],
        "entries": [
            {
                "id": "quantum.phase1.strict_weyl.local_anomaly_obstruction",
                "scope": rows[0]["scope"],
                "descriptions": {"causal": "NO_CERTIFIED_MAP", "symplectic": "NOT_APPLICABLE", "nonlinear": "NOT_APPLICABLE", "observational": "NOT_APPLICABLE", "quantum": "OBSTRUCTED"},
                "evidence": [refs["paper12_claim_map"]],
                "mode_data": atlas_mode_data(
                    dispersion=("NOT_APPLICABLE", "A local anomaly class is not a dispersion or particle mode."),
                    lee_wald=("NOT_APPLICABLE", "The local anomaly quotient does not carry a Lee-Wald particle pairing."),
                    taub=("NO_CERTIFIED_MAP", "No tangent-cone-to-interacting-BRST map is used in this theorem."),
                    resonance=("NOT_APPLICABLE", "No resonance claim is made."),
                    bounded=("NO_CERTIFIED_MAP", "No state-space evolution is defined by the local obstruction theorem."),
                    secular=("NO_CERTIFIED_MAP", "No nonlinear state-space evolution is defined."),
                    causal=("NO_CERTIFIED_MAP", "No Lorentzian products or QME are constructed."),
                ),
                "claim_boundary": "Does not establish: " + "; ".join(rows[0]["does_not_establish"]),
            },
            {
                "id": "quantum.phase1.tau_adic.formal_local_restoration",
                "scope": rows[1]["scope"],
                "descriptions": {"causal": "OBSTRUCTED", "symplectic": "NO_CERTIFIED_MAP", "nonlinear": "OPEN", "observational": "NOT_APPLICABLE", "quantum": "CERTIFIED"},
                "evidence": [refs["paper12_claim_map"], refs["minimal_ladder"]],
                "mode_data": atlas_mode_data(
                    dispersion=("NOT_APPLICABLE", "Formal local Wess-Zumino restoration is not a dispersion relation."),
                    lee_wald=("NO_CERTIFIED_MAP", "No complete tau-adic causal pairing is imported."),
                    taub=("NO_CERTIFIED_MAP", "No classical obstruction is mapped into interacting BRST."),
                    resonance=("NOT_APPLICABLE", "No resonance claim is made."),
                    bounded=("NO_CERTIFIED_MAP", "No state-space realization of the formal quartet is certified."),
                    secular=("OPEN", "The formal all-loop induction remains conditional on a declared QAP."),
                    causal=("OBSTRUCTED", "The passive dressed-trace carrier has no complete causal parent."),
                ),
                "claim_boundary": "Does not establish: " + "; ".join(rows[1]["does_not_establish"]),
            },
            {
                "id": "quantum.phase1.relative.changed_action_orbit_obstruction",
                "scope": rows[2]["scope"],
                "descriptions": {"causal": "NO_CERTIFIED_MAP", "symplectic": "NO_CERTIFIED_MAP", "nonlinear": "OBSTRUCTED", "observational": "NOT_APPLICABLE", "quantum": "NO_CERTIFIED_MAP"},
                "evidence": [refs["paper12_claim_map"], refs["paper12_v3_receipt"]],
                "mode_data": atlas_mode_data(
                    dispersion=("NOT_APPLICABLE", "The theorem is a local action-response cokernel."),
                    lee_wald=("NO_CERTIFIED_MAP", "Pairing-deformation orbits were not included."),
                    taub=("NO_CERTIFIED_MAP", "No relative tangent-cone map is defined."),
                    resonance=("NOT_APPLICABLE", "No resonance claim is made."),
                    bounded=("NO_CERTIFIED_MAP", "No changed action was selected."),
                    secular=("NO_CERTIFIED_MAP", "No changed master action was activated."),
                    causal=("NO_CERTIFIED_MAP", "No changed causal carrier was activated."),
                ),
                "claim_boundary": "Does not establish: " + "; ".join(rows[2]["does_not_establish"]),
            },
            {
                "id": "quantum.phase1.counterflow.successor_nonactivation",
                "scope": rows[3]["scope"],
                "descriptions": {"causal": "CERTIFIED", "symplectic": "OBSTRUCTED", "nonlinear": "NO_CERTIFIED_MAP", "observational": "NO_CERTIFIED_MAP", "quantum": "NO_CERTIFIED_MAP"},
                "evidence": [refs["counterflow_viability"]],
                "mode_data": atlas_mode_data(
                    dispersion=("OBSTRUCTED", "The j=1/2 Hamiltonian-Hopf quartet persists throughout the trace-healthy family."),
                    lee_wald=("CERTIFIED", "The unstable multiplicity-two residue sector is nonradical on the classical physical quotient."),
                    taub=("NO_CERTIFIED_MAP", "Candidate-specific nonlinear and quantum branches were not activated."),
                    resonance=("OPEN", "Stable-sector collisions do not remove the persistent quartet."),
                    bounded=("OBSTRUCTED", "No robust bounded quasiperiodic same-field clock survives."),
                    secular=("NO_CERTIFIED_MAP", "No candidate-specific q2 source was evaluated."),
                    causal=("CERTIFIED", "A causal parent is certified only on the selected fixture, not familywide."),
                ),
                "claim_boundary": "Does not establish: " + "; ".join(rows[3]["does_not_establish"]),
            },
            {
                "id": "quantum.phase1.berger.schur_partial_spectral_method",
                "scope": rows[4]["scope"],
                "descriptions": {"causal": "NOT_APPLICABLE", "symplectic": "NO_CERTIFIED_MAP", "nonlinear": "NOT_APPLICABLE", "observational": "NOT_APPLICABLE", "quantum": "OPEN"},
                "evidence": [refs["berger_spectral_receiver"]],
                "mode_data": atlas_mode_data(
                    dispersion=("OPEN", "Exact low blocks are known but the global primed spectrum and finite receiver are incomplete."),
                    lee_wald=("NO_CERTIFIED_MAP", "The partial Euclidean receiver has no Lorentzian symplectic crosswalk."),
                    taub=("NOT_APPLICABLE", "This is a spectral-method result, not a tangent-cone calculation."),
                    resonance=("OPEN", "Exceptional continuation and global crossings remain uncertified."),
                    bounded=("NOT_APPLICABLE", "No Lorentzian state-space mode is claimed."),
                    secular=("NOT_APPLICABLE", "No nonlinear evolution is claimed."),
                    causal=("NOT_APPLICABLE", "The carrier is Euclidean spectral."),
                ),
                "claim_boundary": "Does not establish: " + "; ".join(rows[4]["does_not_establish"]),
            },
        ],
        "verification_commands": [
            "python3 quantum-weyl/phase1/generate_phase1_quantum_disposition_synthesis.py --check",
            "python3 quantum-weyl/phase1/verify_phase1_quantum_disposition_synthesis.py",
            "python3 residual_atlas/validate_fragment.py residual_atlas/phase1-quantum-disposition-synthesis-fragment-v1.json",
        ],
    }

    materiality = {
        "schema": "pure-weyl-paper-materiality-record-v1",
        "result_id": "QUANTUM_PHASE1_PAPER_MATERIALITY_2026_07_21",
        "source_result_id": cert["result_id"],
        "source_sha256": hashlib.sha256(dump(cert)).hexdigest(),
        "records": [
            {"paper": "00", "materiality": "MATERIAL_PHASE1_QUANTUM_SYNTHESIS", "required_scope": "Separate strict obstruction, changed formal restoration and counterflow nonactivation.", "publication_edit": "NOT_PERFORMED_BY_QUANTUM_SYNTHESIS"},
            {"paper": "12", "materiality": "CURRENT_STRICT_AND_RELATIVE_RESULTS_PLUS_COUNTERFLOW_NONACTIVATION_BOUNDARY", "required_scope": "The v3 strict/relative publication chain is current; no counterflow coefficient, QME or Hadamard promotion follows from the failed classical selection gate.", "publication_edit": "NOT_PERFORMED_BY_QUANTUM_SYNTHESIS"},
            {"paper": "13", "materiality": "NO_HADAMARD_PROMOTION", "required_scope": "Do not identify local anomaly, formal compensator or partial Berger spectral rows with a full-BV state.", "publication_edit": "NOT_PERFORMED_BY_QUANTUM_SYNTHESIS"},
            {"paper": "98", "materiality": "MATERIAL_EXECUTIVE_PHASE1_QUANTUM_STATUS", "required_scope": "Record the strict obstruction, changed-theory formal restoration, no selected repair successor and open Lorentzian quantum theory.", "publication_edit": "NOT_PERFORMED_BY_QUANTUM_SYNTHESIS"},
            {"paper": "99", "materiality": "MATERIAL_PUBLIC_PHASE1_BOUNDARY", "required_scope": "No robust same-field counterflow candidate was selected, so its quantum success branch was not activated.", "publication_edit": "NOT_PERFORMED_BY_QUANTUM_SYNTHESIS"},
        ],
        "claim_boundary": "Reverse materiality records only; this work item is forbidden from directly editing Papers 00, 12 or 98 and performs no publication lifecycle promotion.",
    }

    report = """# Phase 1 quantum disposition synthesis

Phase 1 closes without a selected quantum successor. Strict fixed-field-content
pure Weyl gravity has the certified local one-loop BV obstruction with even
coefficients 199/30 and -87/20 and a vanishing odd coefficient. The formal
tau-adic compensator extension makes the local anomaly vector exact and
restores the declared local Euclidean one-loop QME, but it is a changed formal
theory: its passive dressed-trace carrier remains obstructed and no actual
four-dimensional regulator, unconditional all-loop QAP, global anomaly
classification, Lorentzian products or full-BV Hadamard state has landed.

All nine separately declared minimal repair families terminate without a
selected action. The later two-phase counterflow action has a certified causal
parent only on its selected Berger fixture, while a persistent j=1/2
Hamiltonian-Hopf quartet excludes a robust same-field stationary clock across
the connected trace-healthy family. Its action-specific anomaly, determinant,
QME and Hadamard branches are therefore NOT_ACTIVATED rather than failed
coefficient calculations.

The scalar-flat Berger Schur programme remains an EUCLIDEAN-SPECTRAL method
result. Exact low blocks and local residue rows survive, but the ordinary B1
trace, finite global receiver functions, priming and subtraction data do not;
it supplies neither a determinant nor a QME.

The relative changed-action result remains a local action-cokernel obstruction.
It does not activate a changed master action or define a relative anomaly
coefficient. The original Paper 12 v1/v2 blocked events remain hash-pinned
provenance; the corrected v3 claim map is the publication-current source.
"""
    return cert, atlas, materiality, report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()
    cert, atlas, materiality, report = build()
    outputs = {CERT: dump(cert), ATLAS: dump(atlas), MATERIALITY: dump(materiality), REPORT: report.encode()}
    if args.write:
        for path, content in outputs.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
    else:
        for path, content in outputs.items():
            if not path.exists() or path.read_bytes() != content:
                raise SystemExit(f"STALE: {path.relative_to(ROOT)}")
    print("PHASE1_QUANTUM_DISPOSITION_SYNTHESIS_V1: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
