#!/usr/bin/env python3
"""Independent structural checker for minimal-BV q3 cyclicity."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/STRICT_MINIMAL_BV_Q3_CYCLICITY_V1.json"
PAIRING = HERE / "certificates/STRICT_MINIMAL_BV_CYCLIC_SIGN_RECONCILIATION_V1.json"
CLASSICAL = ROOT / "d_quotient_classical/certificates/CLASSICAL_MINIMAL_BV_Q3_EXPORT_V1.json"
ACTION = ROOT / "d_quotient_classical/minimal_bv_antifield/foundation/action_normalization.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def check(value: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    pairing = json.loads(PAIRING.read_text())
    classical = json.loads(CLASSICAL.read_text())
    action = json.loads(ACTION.read_text())
    if value.get("result_id") != "STRICT_MINIMAL_BV_Q3_CYCLICITY_V1" or value.get("result_kind") != "INTEGRATED_LOCAL_FUNCTIONAL_QUARTIC_BV_CYCLICITY":
        errors.append("result identity or kind drift")
    if value.get("dependency_tags") != ["LOCAL-ALGEBRAIC"] or value.get("lifecycle") != "CLASSIFIED":
        errors.append("dependency tag or lifecycle drift")
    scope = value.get("scope", {})
    if scope.get("result_kind") != "integrated local functional modulo horizontal boundary terms" or scope.get("carrier") != "six-generator minimal BV carrier with the canonical odd cotangent pairing":
        errors.append("cyclicity result-kind or carrier drift")

    projection = value.get("canonical_pairing_projection", {})
    canonical = pairing["canonical_pairing"]
    expected_entries = [item for item in canonical["entries"] if item["left"].startswith("h_") and item["right"].startswith("h_star_")]
    if projection.get("parent_result_id") != pairing.get("result_id") or projection.get("metric_entries") != expected_entries:
        errors.append("canonical metric pairing projection drift")
    if projection.get("metric_entry_count") != 10 or projection.get("off_diagonal_symmetric_tensor_weight") != 2:
        errors.append("metric pairing rank or symmetric weight drift")

    form = value.get("cyclic_four_form", {})
    if form.get("variational_identification") != "V4=D^4 S_W(h1,h2,h3,h4) modulo a compact-support horizontal boundary term" or form.get("permutation_group") != "S4":
        errors.append("fourth-variation identification drift")
    if form.get("metric_component_weights") != ["1", "2", "2", "2", "1", "2", "2", "1", "2", "1"] or form.get("Koszul_sign_for_all_metric_inputs") != 1 or form.get("cyclicity_defect_mod_d") != "0" or form.get("status") != "CERTIFIED":
        errors.append("quartic cyclic form weights/sign/status drift")

    proof = value.get("variational_proof", {})
    argument = proof.get("argument", [])
    if proof.get("proof_kind") != "FOURTH_VARIATION_OF_LOCAL_ACTION_MODULO_HORIZONTAL_BOUNDARY" or len(argument) != 5:
        errors.append("variational proof inventory drift")
    if action.get("Euler_coordinate") != classical.get("scope", {}).get("action_normalization", "") or "D^4 S_W" not in form.get("variational_identification", ""):
        errors.append("authoritative action/Euler source drift")
    if "no pointwise equality" not in proof.get("result_kind_boundary", ""):
        errors.append("integrated-versus-pointwise boundary drift")

    bridge = value.get("convention_bridge", {})
    if bridge.get("pairing_sign_translation") != pairing["sign_translation"]["formula"] or bridge.get("translation_sign_on_h_star") != 1 or bridge.get("translation_changes_q3") is not False:
        errors.append("receiver sign-translation bridge drift")
    if classical.get("minimal_q3_support", {}).get("nonzero_row_count") != 1:
        errors.append("unique q3 sector source drift")

    gates = {item.get("gate"): item.get("status") for item in value.get("gate_advancement", [])}
    if gates != {"MINIMAL_ARITY_THREE_Q_SQUARED": "PASS", "MINIMAL_Q3_CYCLICITY": "PASS", "STRICT_386_CYCLIC_STABILIZATION": "OPEN", "STRICT_386_GENERAL_LAMBDA2_SOURCE_CLOSURE": "OPEN"}:
        errors.append("gate advancement drift or premature promotion")
    flags = value.get("claim_flags", {})
    true_flags = ("MINIMAL_BV_ARITY_THREE_IDENTITY_CERTIFIED", "MINIMAL_BV_Q3_CYCLICITY_CERTIFIED", "QUARTIC_METRIC_VERTEX_S4_SYMMETRIC_MOD_D", "CANONICAL_PAIRING_SIGN_TRANSLATION_COMPATIBLE")
    false_flags = ("STRICT_386_Q3_STABILIZED", "STRICT_386_GENERAL_LAMBDA2_SOURCE_CLOSURE_CERTIFIED", "CLASSICAL_IMPORT_GATE_PASSED", "LORENTZIAN_CAUSAL_CERTIFIED", "HADAMARD_STATE_CONSTRUCTED", "QME_RESTORED")
    if any(flags.get(name) is not True for name in true_flags) or any(flags.get(name) is not False for name in false_flags):
        errors.append("claim flags drift or premature promotion")
    foundations = value.get("foundational_strength", {})
    if foundations.get("dependency_boundary") != "LOCAL-ALGEBRAIC" or any(foundations.get(name) is not False for name in ("choice_operation_added", "Hilbert_completion_used", "Green_operator_used")):
        errors.append("foundational-strength boundary drift")
    expected_hashes = {
        "canonical_pairing_projection_sha256": digest(projection),
        "cyclic_four_form_sha256": digest(form),
        "variational_proof_sha256": digest(proof),
        "convention_bridge_sha256": digest(bridge),
        "gate_advancement_sha256": digest(value.get("gate_advancement")),
        "foundational_strength_sha256": digest(foundations),
    }
    if value.get("canonical_hashes") != expected_hashes:
        errors.append("canonical hashes do not reproduce")
    for item in value.get("provenance", {}).get("inputs", []):
        path = ROOT / item.get("path", "")
        if not path.is_file() or item.get("sha256") != sha(path):
            errors.append(f"provenance drift: {item.get('path')}")
    if len(value.get("does_not_establish", [])) < 6:
        errors.append("does-not-establish ledger shortened")
    return errors


def main() -> int:
    errors = check(json.loads(RESULT.read_text()))
    print("STRICT_MINIMAL_BV_Q3_CYCLICITY_V1_CHECK: " + ("PASS" if not errors else "FAIL"))
    if errors:
        for error in errors:
            print(f"  - {error}")
    else:
        print("  - fourth-variation cyclicity and canonical pairing signs replayed")
        print("  - 386-row cyclic stabilization remains fail closed")
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
