#!/usr/bin/env python3
"""Independent replay of the strict 386-row nonminimal identity obstruction."""

from __future__ import annotations

from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/STRICT_386_NONMINIMAL_THEORY_IDENTITY_OBSTRUCTION_V1.json"
CLASSICAL = ROOT / "d_quotient_classical/certificates/CLASSICAL_ORDINARY_DERIVATIVE_AUXILIARY_CUBIC_EXPORT_V1.json"
Q2 = HERE / "certificates/STRICT_386_STABILIZED_Q2_LIFT_PREFLIGHT_V1.json"
PAIRING = HERE / "certificates/STRICT_386_COMPONENT_PAIRING_SERIALIZATION_V1.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def check(value: dict[str, Any] | None = None) -> list[str]:
    value = value or json.loads(RESULT.read_text())
    classical, q2, pairing = (json.loads(path.read_text()) for path in (CLASSICAL, Q2, PAIRING))
    errors: list[str] = []
    if value.get("result_id") != "STRICT_386_NONMINIMAL_THEORY_IDENTITY_OBSTRUCTION_V1" or value.get("result_kind") != "EXACT_SOURCE_VERSUS_TRIVIAL_STABILIZATION_NONLINEAR_IDENTITY_OBSTRUCTION":
        errors.append("identity/kind drift")
    if value.get("result_state") != "LITERAL_AND_LINEAR_THEORY_IDENTITY_REFUTED_NONLINEAR_EQUIVALENCE_OPEN" or value.get("lifecycle") != "CLASSIFIED" or value.get("dependency_tags") != ["LOCAL-ALGEBRAIC"]:
        errors.append("state/lifecycle/dependency drift")
    rows = pairing.get("component_basis", {}).get("rows", [])
    blocks = {row.get("block") for row in rows}
    if len(rows) != 386 or not {"AUX_F_HAT", "AUX_F_HAT_STAR", "AUX_V", "AUX_V_STAR"} <= blocks:
        errors.append("common carrier block drift")
    inert = q2.get("graph_transport_dag", {}).get("interaction_inert_blocks", [])
    comparison = value.get("exact_channel_comparison", {})
    try:
        source = Fraction(classical["auxiliary_cubic_interaction"]["witness"]["mixed_derivative_d_t_d_s_squared_at_zero"])
        candidate = Fraction(0) if {"AUX_F_HAT", "AUX_V"} <= set(inert) else None
        defect = source - candidate if candidate is not None else None
    except (KeyError, TypeError, ValueError, ZeroDivisionError):
        source = candidate = defect = None
    expected = {
        "common_coordinate_presentation": "linear generalized-auxiliary split before the curvature-graph shear",
        "cyclic_form_channel": "Omega(f_hat,q2(v,v))",
        "block_channel": ["AUX_F_HAT", "AUX_V", "AUX_V"],
        "source_ordinary_derivative_value": str(source),
        "candidate_trivial_stabilization_value": str(candidate),
        "source_minus_candidate_defect": str(defect),
        "source_nonzero_reason": "mixed third derivative of the authoritative ordinary-derivative action density",
        "candidate_zero_reason": "q2_split vanishes whenever a contractible input is present; AUX_F_HAT and AUX_V remain interaction-inert under the recorded linear shear",
        "literal_identity": False,
    }
    if comparison != expected or defect != -1:
        errors.append("exact source/candidate channel replay")
    disposition = value.get("theory_identity_disposition", {})
    if not (
        disposition.get("candidate_internal_q1_q2_and_cyclicity_certificates_preserved") is True
        and disposition.get("candidate_is_authoritative_ordinary_derivative_nonminimal_theory") is False
        and disposition.get("linear_canonical_shear_suffices_for_theory_identity") is False
        and disposition.get("nonlinear_canonical_or_L_infinity_equivalence_may_exist") is True
        and disposition.get("nonlinear_equivalence_constructed") is False
        and "Omega(f_hat,q2(v,v))=-1" in disposition.get("first_required_correction", "")
    ):
        errors.append("theory-identity disposition drift")
    flags = value.get("claim_flags", {})
    true_flags = ("AUTHORITATIVE_SOURCE_AUXILIARY_CUBIC_IMPORTED", "CANDIDATE_Q2_ZERO_CHANNEL_REPLAYED", "LITERAL_TRIVIAL_STABILIZATION_THEORY_IDENTITY_REFUTED", "LINEAR_SHEAR_ONLY_THEORY_IDENTITY_REFUTED")
    false_flags = ("CANDIDATE_INTERNAL_IDENTITIES_INVALIDATED", "NONLINEAR_CYCLIC_L_INFINITY_EQUIVALENCE_CONSTRUCTED", "NONLINEAR_CYCLIC_L_INFINITY_EQUIVALENCE_OBSTRUCTED", "AUTHORITATIVE_FULL_386_Q2_IMPORTED", "AUTHORITATIVE_FULL_386_Q3_IMPORTED", "CANDIDATE_CAUSAL_LAMBDA2_SOURCE_CLOSURE_CERTIFIED", "CLASSICAL_IMPORT_GATE_PASSED", "HADAMARD_STATE_CONSTRUCTED", "QME_RESTORED")
    if any(flags.get(key) is not True for key in true_flags) or any(flags.get(key) is not False for key in false_flags):
        errors.append("claim firewall drift")
    if value.get("canonical_hashes") != {
        "exact_channel_comparison_sha256": digest(comparison),
        "theory_identity_disposition_sha256": digest(disposition),
    }:
        errors.append("canonical hash drift")
    sources = ((CLASSICAL, classical["result_id"]), (Q2, q2["result_id"]), (PAIRING, pairing["result_id"]))
    expected_provenance = {(str(path.relative_to(ROOT)), result_id, sha(path)) for path, result_id in sources}
    actual_provenance = {(item.get("path"), item.get("result_id"), item.get("sha256")) for item in value.get("provenance", {}).get("inputs", [])}
    if actual_provenance != expected_provenance:
        errors.append("input provenance drift")
    return errors


def main() -> int:
    errors = check()
    print("STRICT_386_NONMINIMAL_THEORY_IDENTITY_OBSTRUCTION_V1: " + ("PASS" if not errors else "FAIL"))
    for error in errors:
        print("  - " + error)
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
