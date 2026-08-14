#!/usr/bin/env python3
"""Build the current, fail-closed reconciliation of classical import Gate A."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
RESULT = ROOT / "quantum-weyl/classical_import/certificates/CLASSICAL_IMPORT_GATE_V2_RECONCILIATION.json"
REPORT = ROOT / "quantum-weyl/classical_import/REPORT_GATE_V2.md"

INPUTS = [
    ("quantum-weyl/classical_import/certificates/CLASSICAL_IMPORT_CERTIFICATE.json", "CLASSICAL_IMPORT_CERTIFICATE", "historical receiver Gate A"),
    ("quantum-weyl/classical_import/snapshots/bootstrap-v1.json", "CLASSICAL_IMPORT_BOOTSTRAP_V1", "twenty-export and ten-check contract"),
    ("quantum-weyl/classical_import/certificates/CLASSICAL_MINIMAL_BV_ANTIFIELD_IMPORT_V2.json", "CLASSICAL_MINIMAL_BV_ANTIFIELD_IMPORT_V2", "same-theory bounded minimal-BV receiver replay"),
    ("quantum-weyl/classical_import/certificates/REPOSITORY_CLASSICAL_SNAPSHOT_COMPATIBILITY.json", "REPOSITORY_CLASSICAL_SNAPSHOT_COMPATIBILITY", "same-theory local-BV content bridge"),
    ("quantum-weyl/local_bv/certificates/GENERAL_NONMINIMAL_GAUGE_FIXED_CONTRACTION.json", "GENERAL_NONMINIMAL_GAUGE_FIXED_CONTRACTION", "same-theory regular-locus nonminimal contraction"),
    ("covariant_completion/certificates/curved_deformation_retract_status.json", "PURE_WEYL_CURVED_DEFORMATION_RETRACT_STATUS_V1", "strict auxiliary-to-metric retract; not residual SDR"),
    ("covariant_completion/certificates/curved_full_prolonged_green_homotopy_assembly.json", "PURE_WEYL_FULL_PROLONGED_GREEN_HOMOTOPY_ASSEMBLY_V1", "strict 386-row causal homotopy; not residual SDR"),
    ("covariant_completion/certificates/covariant_CKV_recovery.json", "PURE_WEYL_COVARIANT_CKV_RECOVERY_V1", "same-theory fifteen-generator endpoint recovery"),
    ("covariant_completion/certificates/curved_SO42_causal_transport_recognition.json", "PURE_WEYL_SO42_CAUSAL_TRANSPORT_RECOGNITION_V1", "same-theory cohomological SO(4,2) action"),
    ("covariant_completion/certificates/covariant_gram_transport.json", "PURE_WEYL_COVARIANT_GRAM_TRANSPORT_V1", "same-theory scoped pairing transport"),
    ("covariant_completion/certificates/covariant_H4_transport.json", "PURE_WEYL_COVARIANT_H4_TRANSPORT_V1", "same-theory named H4 transport"),
    ("quantum-weyl/transfer/certificates/BERGER_SUPPORT_LOCAL_Q2_SCIENTIFIC_REPLAY.json", "BERGER_SUPPORT_LOCAL_Q2_SCIENTIFIC_REPLAY", "different-theory q1/q2/D/cyclicity replay"),
    ("d_quotient_classical/certificates/CLASSICAL_D_QUOTIENT_STATUS.json", "CLASSICAL_D_QUOTIENT_STATUS", "scope-separating classical status synthesis"),
]

MIGRATED_VERIFIERS = [
    "ci/standalone_provenance.py",
    "reports/standalone-history-crosswalk.json",
    "quantum-weyl/classical_import/verify_snapshot.py",
    "quantum-weyl/classical_import/verify_antifield_export.py",
    "quantum-weyl/classical_import/verify_antifield_export_v2.py",
    "quantum-weyl/classical_import/verify_support_local_q2_export.py",
    "quantum-weyl/classical_import/analytic_operator_snapshot_attribution.py",
]

EXPORT_IDS = [
    "field_ghost_antifield_dictionary",
    "field_gradings",
    "local_classical_bv_differential_q0",
    "support_local_classical_bv_q2",
    "local_D_action_on_bv_generators",
    "gauge_fixed_nonminimal_contractions",
    "trace_sector_contraction",
    "conformal_killing_zero_modes_15",
    "residual_representation_matrices",
    "so42_structure_constants",
    "classical_inclusion_iota_cl",
    "classical_projection_pi_cl",
    "classical_homotopy_s_cl",
    "cyclic_pairing",
    "taub_moment_map_normalization",
    "bfv_suspension_convention",
    "positive_frequency_state_ledger",
    "normalized_weyl_square_representatives",
    "centered_cohomology_bases_h3_h4_h5",
    "residual_differential_q_res_0",
]

CHECK_IDS = [
    "q0_squared_zero",
    "q1_q2_arity_two_nilpotency",
    "D_q1_commutator_zero",
    "D_q2_derivation",
    "q2_cyclic_compatibility",
    "pi_cl_iota_cl_identity",
    "classical_contraction_identity",
    "q0_iota_intertwining",
    "pi_q0_intertwining",
    "cyclic_compatibility",
]

STATUS = {
    "RECEIVER_VERIFIED_SCOPED": "The quantum receiver independently replayed a same-theory object or identity, but only in a narrower declared scope than complete Gate A.",
    "CERTIFIED_DIFFERENT_THEORY": "A complete result exists for Berger or another changed theory and is recorded only as a control; it cannot enter the strict pure-Weyl snapshot.",
    "LEGACY_ACCEPTED_SCOPED": "The historical bootstrap accepted a portable bounded ledger, but it was never sufficient for the complete freeze by itself.",
    "SUPPORTING_EVIDENCE_ONLY": "Same-theory certificates establish related structure, names, transport or internal hashes without serializing the exact portable Gate-A payload.",
    "MISSING_PORTABLE_OBJECT": "No current certificate serializes the exact same-theory object required for independent receiver replay.",
    "BLOCKED_MISSING_COMMON_SNAPSHOT": "The identity cannot be replayed because its exact maps are absent from one common accepted strict pure-Weyl snapshot.",
}


def file_hash(path: str) -> str:
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def export(export_id: str, status: str, evidence: list[str], established: str, remaining: str, boundary: str) -> dict[str, Any]:
    return {"export_id": export_id, "status": status, "evidence": evidence, "established": established, "remaining_for_gate_a": remaining, "boundary": boundary}


def check_row(check_id: str, status: str, evidence: list[str], established: str, remaining: str, boundary: str) -> dict[str, Any]:
    return {"check_id": check_id, "status": status, "evidence": evidence, "established": established, "remaining_for_gate_a": remaining, "boundary": boundary}


def digest(value: dict[str, Any]) -> str:
    payload = {key: value[key] for key in ("standalone_history_replay", "status_vocabulary", "export_reconciliation", "freeze_check_reconciliation", "required_hash_disposition", "minimal_missing_bundle", "gate_disposition")}
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def build() -> dict[str, Any]:
    docs = {evidence_id: json.loads((ROOT / path).read_text()) for path, evidence_id, _ in INPUTS}
    old = docs["CLASSICAL_IMPORT_CERTIFICATE"]
    bootstrap = docs["CLASSICAL_IMPORT_BOOTSTRAP_V1"]
    minimal = docs["CLASSICAL_MINIMAL_BV_ANTIFIELD_IMPORT_V2"]
    compatibility = docs["REPOSITORY_CLASSICAL_SNAPSHOT_COMPATIBILITY"]
    nonminimal = docs["GENERAL_NONMINIMAL_GAUGE_FIXED_CONTRACTION"]
    retract = docs["PURE_WEYL_CURVED_DEFORMATION_RETRACT_STATUS_V1"]
    strict_green = docs["PURE_WEYL_FULL_PROLONGED_GREEN_HOMOTOPY_ASSEMBLY_V1"]
    ckv = docs["PURE_WEYL_COVARIANT_CKV_RECOVERY_V1"]
    so42 = docs["PURE_WEYL_SO42_CAUSAL_TRANSPORT_RECOGNITION_V1"]
    gram = docs["PURE_WEYL_COVARIANT_GRAM_TRANSPORT_V1"]
    h4 = docs["PURE_WEYL_COVARIANT_H4_TRANSPORT_V1"]
    berger = docs["BERGER_SUPPORT_LOCAL_Q2_SCIENTIFIC_REPLAY"]

    if old.get("gate_a_status") != "FAIL_CLOSED" or old.get("publishable_quantum_results_allowed") is not False:
        raise ValueError("historical gate boundary drift")
    if [row["export_id"] for row in bootstrap["required_exports"]] != EXPORT_IDS:
        raise ValueError("historical export contract drift")
    if [row["check_id"] for row in bootstrap["freeze_checks"]] != CHECK_IDS:
        raise ValueError("historical freeze-check contract drift")
    if not minimal["claim_flags"]["CLASSICAL_MINIMAL_BV_FILTRATION_IDENTITIES_EXACT"]:
        raise ValueError("minimal receiver replay missing")
    if compatibility.get("result_state") != "LOCAL_BV_CONTENT_HASHES_EQUAL_ACROSS_DISTINCT_COMMITS":
        raise ValueError("snapshot compatibility bridge missing")
    if not nonminimal["claim_flags"]["GENERAL_NONMINIMAL_DOUBLETS_CONTRACTED"]:
        raise ValueError("nonminimal contraction missing")
    if retract.get("curved_deformation_retract") is not True or retract.get("remaining") != []:
        raise ValueError("strict auxiliary retract missing")
    if strict_green.get("causal_green_homotopy") is not True:
        raise ValueError("strict causal homotopy missing")
    if ckv.get("status") is not True or not ckv["terminal_gate"]["status"]:
        raise ValueError("CKV recovery missing")
    if not so42["residual_action"]["strict_so42_action_on_cohomology"]:
        raise ValueError("SO42 action missing")
    if gram.get("status") is not True or h4["transported_result_when_gate_passes"]["H4"] != ["W_+^2", "W_-^2"]:
        raise ValueError("H4/pairing transport missing")
    if not berger["claim_flags"]["SCIENTIFIC_ARITY_TWO_IDENTITIES_INDEPENDENTLY_REPLAYED"]:
        raise ValueError("Berger replay missing")

    exports = [
        export("field_ghost_antifield_dictionary", "RECEIVER_VERIFIED_SCOPED", ["CLASSICAL_MINIMAL_BV_ANTIFIELD_IMPORT_V2", "REPOSITORY_CLASSICAL_SNAPSHOT_COMPATIBILITY"], "Six strict minimal generators and eighteen covariant atoms are imported with exact roles and hashes.", "One common full minimal, nonminimal, auxiliary and residual dictionary at the replacement snapshot commit.", "The accepted import is a bounded minimal-BV filtration, not the complete Gate-A carrier."),
        export("field_gradings", "RECEIVER_VERIFIED_SCOPED", ["CLASSICAL_MINIMAL_BV_ANTIFIELD_IMPORT_V2"], "Ghost, antifield, form, parity, dimension and derivative bounds are enforced on the imported minimal atoms.", "The same grading fields on every generator in the common full carrier.", "Scope projection to a bounded window is not an unrestricted local export."),
        export("local_classical_bv_differential_q0", "RECEIVER_VERIFIED_SCOPED", ["CLASSICAL_MINIMAL_BV_ANTIFIELD_IMPORT_V2"], "The receiver exactly replays delta, gamma, positive filtration rows and Q squared on the declared minimal atom set.", "A common full-carrier strict q0 payload, including every nonminimal, auxiliary and residual row required by Gate A.", "A bounded local filtration replay is not the complete residual contraction snapshot."),
        export("support_local_classical_bv_q2", "CERTIFIED_DIFFERENT_THEORY", ["BERGER_SUPPORT_LOCAL_Q2_SCIENTIFIC_REPLAY", "CLASSICAL_D_QUOTIENT_STATUS"], "A complete 54-row support-local q2 is independently replayed at the rational positive-Berger fixture.", "A complete arbitrary-support q2 for the strict pure-Weyl action on the same carrier and commit as all other Gate-A exports.", "Berger includes a positive clock and cannot supply the strict pure-Weyl tensor."),
        export("local_D_action_on_bv_generators", "CERTIFIED_DIFFERENT_THEORY", ["BERGER_SUPPORT_LOCAL_Q2_SCIENTIFIC_REPLAY", "CLASSICAL_D_QUOTIENT_STATUS"], "The local D action and its q1/q2 identities are replayed on all 54 Berger rows.", "The strict pure-Weyl D action on every field, ghost, antifield, nonminimal and residual generator.", "A Berger D action is not a strict pure-Weyl export."),
        export("gauge_fixed_nonminimal_contractions", "RECEIVER_VERIFIED_SCOPED", ["GENERAL_NONMINIMAL_GAUGE_FIXED_CONTRACTION"], "Ten Diff x Weyl nonminimal pointwise doublets and their jet-prolonged contraction are independently checked on the regular Bach locus.", "Bind these rows into the common full Gate-A snapshot and its residual SDR.", "The local nonminimal theorem does not provide causal Green data or residual homological projection."),
        export("trace_sector_contraction", "RECEIVER_VERIFIED_SCOPED", ["PURE_WEYL_CURVED_DEFORMATION_RETRACT_STATUS_V1", "PURE_WEYL_FULL_PROLONGED_GREEN_HOMOTOPY_ASSEMBLY_V1"], "Strict trace/Weyl and auxiliary rows have exact local contractions in the declared curved prolonged architecture.", "Serialize the precise trace projector and homotopy in the common Gate-A carrier and replay its compatibility with pi_cl and iota_cl.", "Auxiliary and causal endpoint contractions are not the residual SDR maps."),
        export("conformal_killing_zero_modes_15", "SUPPORTING_EVIDENCE_ONLY", ["PURE_WEYL_COVARIANT_CKV_RECOVERY_V1"], "All fifteen conformal generators and their covariant endpoint recovery are certified.", "Portable exact primal and dual zero-mode basis vectors with a canonical ordering and common-snapshot hash.", "Dimension, labels and transported action do not serialize the required basis vectors."),
        export("residual_representation_matrices", "SUPPORTING_EVIDENCE_ONLY", ["PURE_WEYL_SO42_CAUSAL_TRANSPORT_RECOGNITION_V1"], "A strict SO(4,2) action on cohomology and exact generator brackets are recognized.", "Explicit exact rho(G_a) matrices on the complete declared residual complex.", "A cohomological recognition theorem is not a portable matrix payload."),
        export("so42_structure_constants", "SUPPORTING_EVIDENCE_ONLY", ["PURE_WEYL_SO42_CAUSAL_TRANSPORT_RECOGNITION_V1"], "The proper conformal brackets are exact for all fifteen generators.", "The ordered exact structure-constant tensor serialized independently of implementation code.", "Verified bracket relations do not expose the tensor required by the receiver contract."),
        export("classical_inclusion_iota_cl", "MISSING_PORTABLE_OBJECT", ["PURE_WEYL_CURVED_DEFORMATION_RETRACT_STATUS_V1"], "An exact strict auxiliary-to-metric inclusion exists in a different retract.", "The full inclusion from the residual complex into the authoritative classical BV complex.", "The auxiliary-to-metric inclusion cannot be relabelled iota_cl; it has different source, target and theorem."),
        export("classical_projection_pi_cl", "MISSING_PORTABLE_OBJECT", ["PURE_WEYL_CURVED_DEFORMATION_RETRACT_STATUS_V1"], "An exact strict auxiliary-to-metric projection exists in a different retract.", "The homological projection pi_cl from the authoritative classical BV complex onto the residual complex.", "Reserve pi_cl for the residual projection; the auxiliary projection is not a substitute."),
        export("classical_homotopy_s_cl", "MISSING_PORTABLE_OBJECT", ["PURE_WEYL_CURVED_DEFORMATION_RETRACT_STATUS_V1", "PURE_WEYL_FULL_PROLONGED_GREEN_HOMOTOPY_ASSEMBLY_V1"], "Local auxiliary contractions and causal Green homotopies exist on strict scoped carriers.", "The full residual contraction homotopy s_cl paired with the required iota_cl and pi_cl.", "Neither an auxiliary SDR homotopy nor an advanced/retarded Green homotopy is s_cl."),
        export("cyclic_pairing", "SUPPORTING_EVIDENCE_ONLY", ["PURE_WEYL_COVARIANT_GRAM_TRANSPORT_V1", "GENERAL_NONMINIMAL_GAUGE_FIXED_CONTRACTION"], "Pairing compatibility is transported to the strict H4 Gram form and nonminimal canonical transformations preserve local BV contractions.", "A complete portable graded cyclic pairing on every common-snapshot Gate-A row.", "The residual Gram matrix and local doublet pairing are projections of, not substitutes for, the full cyclic pairing."),
        export("taub_moment_map_normalization", "LEGACY_ACCEPTED_SCOPED", ["CLASSICAL_IMPORT_CERTIFICATE"], "The historical receiver accepted the exact D-finite E/A/L normalization ledger.", "Re-pin it in the common replacement snapshot without broadening its D-finite scope.", "This bounded normalization never established full Gate A."),
        export("bfv_suspension_convention", "LEGACY_ACCEPTED_SCOPED", ["CLASSICAL_IMPORT_CERTIFICATE"], "The historical receiver accepted the selected closed-cylinder lambda=+1 convention.", "Re-pin the same convention in the common replacement snapshot.", "Selection is explicit but uniqueness is not claimed."),
        export("positive_frequency_state_ledger", "LEGACY_ACCEPTED_SCOPED", ["CLASSICAL_IMPORT_CERTIFICATE"], "The historical receiver accepted a D-finite algebraic polarization ledger.", "Keep it typed as a bounded state ledger; no analytic state is required to pass the local classical freeze.", "This ledger is neither Hadamard data nor a full off-shell state."),
        export("normalized_weyl_square_representatives", "SUPPORTING_EVIDENCE_ONLY", ["PURE_WEYL_COVARIANT_H4_TRANSPORT_V1", "PURE_WEYL_COVARIANT_GRAM_TRANSPORT_V1"], "The named classes W_+^2 and W_-^2 and their identity Gram form transport covariantly.", "Exact normalized coefficient vectors for W_+^2 v_- and W_-^2 v_- in a declared common residual basis.", "Names, parity and Gram normalization do not serialize representatives."),
        export("centered_cohomology_bases_h3_h4_h5", "SUPPORTING_EVIDENCE_ONLY", ["PURE_WEYL_COVARIANT_H4_TRANSPORT_V1", "PURE_WEYL_COVARIANT_CKV_RECOVERY_V1"], "The two centered H4 names and residual endpoint recovery are certified.", "Explicit exact centered H3 and H5 bases together with H4 in one ordered payload.", "H4 transport and adjacent cochain dimensions do not provide H3/H5 bases."),
        export("residual_differential_q_res_0", "SUPPORTING_EVIDENCE_ONLY", ["PURE_WEYL_SO42_CAUSAL_TRANSPORT_RECOGNITION_V1", "PURE_WEYL_COVARIANT_CKV_RECOVERY_V1"], "Strict residual action and endpoint recovery are certified at the cohomological level.", "A portable exact q_res^(0) matrix/action payload on the complete residual basis.", "Cohomological action recognition is not the residual differential serialization."),
    ]

    checks = [
        check_row("q0_squared_zero", "RECEIVER_VERIFIED_SCOPED", ["CLASSICAL_MINIMAL_BV_ANTIFIELD_IMPORT_V2"], "Q squared is independently replayed on every atom in the bounded strict minimal export.", "Replay q0 squared on every row of the common full Gate-A snapshot.", "The bounded minimal result cannot be promoted to omitted nonminimal, auxiliary or residual rows."),
        check_row("q1_q2_arity_two_nilpotency", "CERTIFIED_DIFFERENT_THEORY", ["BERGER_SUPPORT_LOCAL_Q2_SCIENTIFIC_REPLAY"], "The arity-two identity is independently replayed for the complete Berger q2.", "Supply and replay the strict pure-Weyl q2 on the common snapshot.", "The identity is coefficient- and theory-dependent."),
        check_row("D_q1_commutator_zero", "CERTIFIED_DIFFERENT_THEORY", ["BERGER_SUPPORT_LOCAL_Q2_SCIENTIFIC_REPLAY"], "The D/q1 commutator vanishes on the complete Berger carrier.", "Supply and independently replay strict pure-Weyl D and q1 rows on the common full carrier.", "The Berger generator and clock architecture cannot be identified with the strict target."),
        check_row("D_q2_derivation", "CERTIFIED_DIFFERENT_THEORY", ["BERGER_SUPPORT_LOCAL_Q2_SCIENTIFIC_REPLAY"], "The D derivation identity is independently replayed for Berger q2.", "Supply and independently replay strict pure-Weyl D and q2 rows on the common full carrier.", "A valid neighboring-theory identity is not a common-snapshot Gate-A result."),
        check_row("q2_cyclic_compatibility", "CERTIFIED_DIFFERENT_THEORY", ["BERGER_SUPPORT_LOCAL_Q2_SCIENTIFIC_REPLAY"], "BV cyclicity is independently replayed for the complete Berger q2 and pairing.", "Supply strict pure-Weyl q2 and the full common-snapshot cyclic pairing.", "Berger cyclicity cannot close the strict action's check."),
        check_row("pi_cl_iota_cl_identity", "BLOCKED_MISSING_COMMON_SNAPSHOT", [], "No current receiver certificate evaluates this identity on portable residual maps.", "Serialize exact pi_cl and iota_cl with common ordered source and target bases.", "Auxiliary projections and inclusions are maps in a different retract."),
        check_row("classical_contraction_identity", "BLOCKED_MISSING_COMMON_SNAPSHOT", [], "No current receiver certificate evaluates q0 s_cl+s_cl q0=1-iota_cl pi_cl on the full strict carrier.", "Serialize q0, s_cl, iota_cl and pi_cl in one common snapshot and replay the identity exactly.", "Causal Green homotopies and auxiliary contractions have different identities and domains."),
        check_row("q0_iota_intertwining", "BLOCKED_MISSING_COMMON_SNAPSHOT", [], "The full residual inclusion intertwiner is not available to the receiver.", "Serialize q0, iota_cl and q_res^(0) and replay q0 iota_cl=iota_cl q_res^(0).", "Cohomological transport does not expose the required matrices."),
        check_row("pi_q0_intertwining", "BLOCKED_MISSING_COMMON_SNAPSHOT", [], "The full residual projection intertwiner is not available to the receiver.", "Serialize pi_cl, q0 and q_res^(0) and replay pi_cl q0=q_res^(0) pi_cl.", "An endpoint recovery theorem is not a portable projection matrix."),
        check_row("cyclic_compatibility", "BLOCKED_MISSING_COMMON_SNAPSHOT", ["PURE_WEYL_COVARIANT_GRAM_TRANSPORT_V1"], "Scoped pairing transport reaches the correct residual H4 Gram form.", "Serialize the full cyclic pairing and residual SDR maps, then replay all adjointness and cyclic side conditions.", "A two-class Gram result does not prove cyclicity on every BV row."),
    ]

    required_hashes = {
        "field_dictionary_hash": {"accepted": None, "candidate": minimal["imported_export"]["canonical_hashes"]["generator_hash"], "candidate_scope": "BOUNDED_MINIMAL_BV_ONLY"},
        "differential_hash": {"accepted": None, "candidate": minimal["imported_export"]["canonical_hashes"]["differential_hash"], "candidate_scope": "BOUNDED_MINIMAL_BV_ONLY"},
        "q2_hash": {"accepted": None, "candidate": file_hash("quantum-weyl/transfer/certificates/BERGER_SUPPORT_LOCAL_Q2_SCIENTIFIC_REPLAY.json"), "candidate_scope": "DIFFERENT_THEORY_BERGER"},
        "D_action_hash": {"accepted": None, "candidate": file_hash("quantum-weyl/transfer/certificates/BERGER_SUPPORT_LOCAL_Q2_SCIENTIFIC_REPLAY.json"), "candidate_scope": "DIFFERENT_THEORY_BERGER"},
        "zero_mode_basis_hash": {"accepted": None, "candidate": None, "candidate_scope": "LABELS_AND_TRANSPORT_ONLY"},
        "pairing_hash": {"accepted": None, "candidate": file_hash("covariant_completion/certificates/covariant_gram_transport.json"), "candidate_scope": "SCOPED_TRANSPORT_NOT_FULL_PAIRING_PAYLOAD"},
        "representative_hash": {"accepted": None, "candidate": file_hash("covariant_completion/certificates/covariant_H4_transport.json"), "candidate_scope": "NAMES_AND_GRAM_NOT_COEFFICIENT_VECTORS"},
    }

    missing_bundle = [
        {"id": "M1_COMMON_STRICT_SNAPSHOT", "object": "One versioned strict pure-Weyl manifest and commit containing every Gate-A carrier, map and ordered basis, with no Berger or compensator rows.", "unlocks": ["all seven accepted top-level hashes", "independent common-domain replay"]},
        {"id": "M2_STRICT_Q2_D", "object": "Complete support-local strict pure-Weyl q2 and local D action on every field, ghost, antifield and nonminimal row.", "unlocks": ["q1_q2_arity_two_nilpotency", "D_q1_commutator_zero", "D_q2_derivation", "q2_cyclic_compatibility"]},
        {"id": "M3_RESIDUAL_SDR", "object": "Portable exact iota_cl, pi_cl and s_cl with ordered full and residual bases; auxiliary and causal homotopies remain separately named.", "unlocks": ["pi_cl_iota_cl_identity", "classical_contraction_identity", "q0_iota_intertwining", "pi_q0_intertwining"]},
        {"id": "M4_FULL_CYCLIC_PAIRING", "object": "The complete graded cyclic pairing on the common strict carrier, including all adjointness and side-condition conventions.", "unlocks": ["cyclic_compatibility", "q2_cyclic_compatibility"]},
        {"id": "M5_RESIDUAL_EXACT_PAYLOAD", "object": "Primal and dual fifteen-mode bases, exact SO(4,2) structure constants and representation matrices, and q_res^(0) on one ordered residual carrier.", "unlocks": ["zero_mode_basis_hash", "residual intertwiners", "independent residual action"]},
        {"id": "M6_CENTERED_REPRESENTATIVES", "object": "Exact normalized coefficient vectors for W_+^2 v_- and W_-^2 v_- plus explicit centered H3, H4 and H5 bases.", "unlocks": ["representative_hash", "independent centered-cohomology audit"]},
    ]

    value: dict[str, Any] = {
        "schema": "quantum-weyl-classical-import-gate-v2-reconciliation-v1",
        "result_id": "CLASSICAL_IMPORT_GATE_V2_RECONCILIATION",
        "result_state": "HISTORICAL_GATE_RECONCILED_PARTIAL_REPAIRS_CERTIFIED_REPLACEMENT_FREEZE_OPEN",
        "lifecycle": "CLASSIFIED",
        "created": "2026-08-15",
        "repository_base_commit": "54b46fdaabb3135822c7035e6f640940a66b0a29",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "question": "Do current certificates now pass the historical twenty-export, seven-hash and ten-identity classical import gate for strict pure-Weyl quantum work?",
        "answer": "No. Current evidence materially repairs the old bootstrap: the receiver independently replays the bounded strict minimal-BV filtration, the strict nonminimal contraction is complete on the regular Bach locus, scoped strict trace/auxiliary contractions and a 386-row causal homotopy exist, and the Berger branch independently closes q1/q2/D/cyclicity. The three pre-extraction monorepo commits used by the historical import are now replayed in this standalone repository by exact path-and-SHA-256 content resolution; their original identifiers and historical paths remain unchanged. That migration repair restores verification but adds no new scientific identity. The scientific results still do not inhabit one common strict pure-Weyl snapshot. Berger q2 and D are a different theory; auxiliary and causal homotopies are not the residual s_cl; transported H4 names and Gram data are not representative vectors or a full cyclic pairing. Gate A therefore remains fail-closed. Six explicit payload families, rather than the historical undifferentiated seventeen-row absence list, are now the minimal replacement bundle.",
        "supersedes_for_current_status": "CLASSICAL_IMPORT_CERTIFICATE",
        "historical_certificate_preserved": True,
        "standalone_history_replay": {
            "status": "VERIFIED_BY_EXACT_CONTENT",
            "historical_commits": [
                "a3fc926cc289e5a545933a43331e395328580e0e",
                "318589ffae21fb1ae1abfd046b2f367b05c52bab",
                "3e15eafa5e0bb8cbc3eb1d2ad79a669c54ce9cca",
            ],
            "proof_strategy": "Resolve each historical path against the filtered standalone Git history and accept only a blob whose SHA-256 equals the immutable certificate pin.",
            "historical_identifiers_preserved": True,
            "historical_paths_preserved": True,
            "verifier_sources": [
                {"path": path, "sha256": file_hash(path)} for path in MIGRATED_VERIFIERS
            ],
            "replayed_results": [
                "CLASSICAL_IMPORT_CERTIFICATE",
                "ANTIFIELD_EXPORT_V2_EXECUTABLE_CONTRACT",
                "CLASSICAL_MINIMAL_BV_ANTIFIELD_IMPORT_V2",
                "ANALYTIC_OPERATOR_CLASSICAL_SNAPSHOT_ATTESTATION",
                "REPOSITORY_CLASSICAL_SNAPSHOT_COMPATIBILITY",
            ],
            "boundary": "This repairs standalone provenance lookup only. It neither changes the authenticated bytes nor promotes any Gate-A export, identity, lifecycle state, or quantum claim.",
        },
        "status_vocabulary": [{"id": key, "meaning": meaning} for key, meaning in STATUS.items()],
        "export_reconciliation": exports,
        "freeze_check_reconciliation": checks,
        "required_hash_disposition": required_hashes,
        "minimal_missing_bundle": missing_bundle,
        "gate_disposition": {
            "gate_a_status": "FAIL_CLOSED",
            "claim_state": "CLASSICAL_IMPORT_PARTIALLY_REPAIRED",
            "publishable_quantum_results_allowed_by_gate_a": False,
            "exports_total": 20,
            "same_theory_receiver_verified_scoped": 5,
            "different_theory_controls": 2,
            "legacy_accepted_scoped": 3,
            "supporting_evidence_only": 7,
            "missing_portable_objects": 3,
            "freeze_checks_total": 10,
            "freeze_checks_receiver_verified_scoped": 1,
            "freeze_checks_different_theory": 4,
            "freeze_checks_blocked": 5,
            "accepted_common_snapshot_hashes": 0,
            "rule": "Gate A may become VERIFIED only when all twenty exports and seven hashes belong to one strict pure-Weyl snapshot and the receiver independently replays all ten identities on those exact bytes.",
        },
        "provenance": {"inputs": [{"path": path, "result_or_artifact_id": evidence_id, "sha256": file_hash(path), "role": role} for path, evidence_id, role in INPUTS]},
        "claim_flags": {
            "HISTORICAL_GATE_RECONCILED": True,
            "STANDALONE_HISTORY_REPLAY_VERIFIED": True,
            "LATER_REPAIRS_RECORDED": True,
            "STRICT_AND_BERGER_SCOPES_SEPARATED": True,
            "CLASSICAL_IMPORT_GATE_PASSED": False,
            "PUBLISHABLE_QUANTUM_RESULTS_ALLOWED_BY_GATE_A": False,
            "LORENTZIAN_QUANTUM_THEORY": False,
            "QME_RESTORED": False,
            "RESIDUAL_QUANTUM_TRANSFER_AUTHORIZED": False,
        },
        "does_not_establish": [
            "a passed classical freeze gate",
            "a new scientific identity from the standalone-history migration repair",
            "that Berger q2 or D belongs to strict pure-Weyl gravity",
            "that an auxiliary deformation retract is the residual SDR",
            "that a causal Green homotopy is s_cl",
            "a portable full cyclic pairing",
            "normalized Weyl-square representative coefficient vectors",
            "explicit centered H3 and H5 bases",
            "a BRST-compatible Hadamard state",
            "renormalized Lorentzian products",
            "QME restoration or residual quantum transfer",
        ],
        "next_gate": "Produce M1 through M6 as one content-addressed strict pure-Weyl snapshot, then implement an independent receiver that recomputes all seven canonical hashes and all ten freeze identities without importing producer proof booleans. The first irreducible coefficient task is M2: strict support-local q2 and D; the first irreducible homological task is M3: the residual iota_cl, pi_cl and s_cl payload.",
        "independent_checker": {
            "path": "quantum-weyl/classical_import/check_classical_import_gate_v2_reconciliation.py",
            "checks": ["standalone historical-commit replay firewall", "twenty-export identity and order", "ten-check identity and order", "scope-safe status assignment", "no accepted common hashes", "six-object missing bundle", "claim-flag firewall", "provenance hashes", "canonical reconciliation digest"],
            "expected_digest": "",
        },
        "human_report": "quantum-weyl/classical_import/REPORT_GATE_V2.md",
    }
    value["independent_checker"]["expected_digest"] = digest(value)
    return value


def render(value: dict[str, Any]) -> str:
    lines = [
        "# Classical import Gate A: current reconciliation",
        "",
        f"**Result:** `{value['result_id']}`",
        "",
        "## Outcome",
        "",
        value["answer"],
        "",
        "The historical certificate is preserved. This result supersedes only its use as the current status summary; it does not rewrite its snapshot or retroactively promote any row.",
        "",
        "## Standalone-history repair",
        "",
        "The three historical monorepo commit pins now replay in the standalone repository by exact path-and-SHA-256 content matching. Original commit identifiers and historical paths remain in the certificates. This is a provenance repair only: it restores independent verification of the same bytes and establishes no additional physical or mathematical claim.",
        "",
        "## Status language",
        "",
    ]
    for status in value["status_vocabulary"]:
        lines.append(f"- `{status['id']}` — {status['meaning']}")
    lines += ["", "## Twenty required exports", "", "| export | current status | what is now established | exact remainder |", "|---|---|---|---|"]
    for row in value["export_reconciliation"]:
        lines.append(f"| `{row['export_id']}` | `{row['status']}` | {row['established']} | {row['remaining_for_gate_a']} |")
    lines += ["", "## Ten freeze identities", "", "| identity | current status | established | exact remainder |", "|---|---|---|---|"]
    for row in value["freeze_check_reconciliation"]:
        lines.append(f"| `{row['check_id']}` | `{row['status']}` | {row['established']} | {row['remaining_for_gate_a']} |")
    lines += ["", "## Minimal replacement bundle", ""]
    for row in value["minimal_missing_bundle"]:
        lines.append(f"- **`{row['id']}`:** {row['object']} Unlocks: {', '.join(row['unlocks'])}.")
    gate = value["gate_disposition"]
    lines += ["", "## Gate verdict", "", f"Gate A remains **`{gate['gate_a_status']}`**. There are {gate['same_theory_receiver_verified_scoped']} same-theory scoped receiver repairs, {gate['different_theory_controls']} different-theory controls, {gate['legacy_accepted_scoped']} legacy scoped ledgers, {gate['supporting_evidence_only']} supporting-only rows, and {gate['missing_portable_objects']} entirely missing portable map objects. Of ten identities, one is receiver-verified only in a bounded strict scope, four are independently verified only for Berger, and five remain blocked on absent common-snapshot maps.", "", gate["rule"], "", "## Why the tempting substitutions fail", "", "- Berger q2 and D are exact, but the positive clock changes the theory.", "- The strict auxiliary-to-metric retract is exact, but its maps are not the residual `iota_cl`, `pi_cl`, and `s_cl`.", "- The strict 386-row advanced/retarded homotopy is causal analytic data, not the residual homological contraction.", "- Covariant H4 and Gram transport prove names and pairings at cohomology, not serialized representative vectors or the full BV cyclic pairing.", "", "## Reproduction", "", "```text", "python3 quantum-weyl/classical_import/build_classical_import_gate_v2_reconciliation.py --check", "python3 quantum-weyl/classical_import/check_classical_import_gate_v2_reconciliation.py", "python3 quantum-weyl/classical_import/verify_classical_import_gate_v2_reconciliation.py", "python3 -m unittest quantum-weyl/classical_import/tests/test_classical_import_gate_v2_reconciliation.py", "```", "", "## Boundaries", ""]
    lines += [f"- This does not establish {item}." for item in value["does_not_establish"]]
    return "\n".join(lines) + "\n"


def generated() -> tuple[bytes, bytes]:
    value = build()
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode(), render(value).encode()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result_bytes, report_bytes = generated()
    outputs = ((RESULT, result_bytes), (REPORT, report_bytes))
    stale = [str(path.relative_to(ROOT)) for path, content in outputs if not path.is_file() or path.read_bytes() != content]
    if args.check:
        print("CLASSICAL_IMPORT_GATE_V2_RECONCILIATION: " + ("generated artifacts current" if not stale else "stale: " + ", ".join(stale)))
        return bool(stale)
    for path, content in outputs:
        path.write_bytes(content)
    print("CLASSICAL_IMPORT_GATE_V2_RECONCILIATION: wrote certificate and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
