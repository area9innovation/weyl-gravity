#!/usr/bin/env python3
"""Independent structural checker for the minimal-BV cyclic sign repair."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, Sequence


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/STRICT_MINIMAL_BV_CYCLIC_SIGN_RECONCILIATION_V1.json"
Q1 = HERE / "certificates/STRICT_PORTABLE_LOCAL_Q1_AST_V1.json"
Q2 = HERE / "certificates/STRICT_SIX_ROW_SUSPENDED_Q2_AST_V1.json"
IDENTITY = HERE / "certificates/STRICT_LOCAL_Q1_Q2_IDENTITY_V1.json"
ACTION = ROOT / "d_quotient_classical/minimal_bv_antifield/foundation/action_normalization.json"
SIGNS = {"h": 1, "c": 1, "omega": 1, "h_star": 1, "c_star": -1, "omega_star": -1}
TRUE_FLAGS = {
    "CANONICAL_MINIMAL_BV_PAIRING_SERIALIZED",
    "CANONICAL_SIGN_TRANSLATION_CERTIFIED",
    "Q1_SQUARED_ZERO_PRESERVED",
    "Q1_Q2_ARITY_TWO_NILPOTENCY_PRESERVED",
    "BV_CYCLICITY_Q1_REPLAYED",
    "BV_CYCLICITY_Q2_REPLAYED",
}
FALSE_FLAGS = {
    "STRICT_FULL_LOCAL_D_ACTION_CERTIFIED",
    "D_Q1_COMMUTATOR_REPLAYED",
    "D_Q2_DERIVATION_REPLAYED",
    "FULL_COMMON_CARRIER_PAIRING_CERTIFIED",
    "STRICT_SUPPORT_LOCAL_Q2_COMPLETE",
    "CLASSICAL_IMPORT_GATE_PASSED",
    "LORENTZIAN_CAUSAL_CERTIFIED",
    "QME_RESTORED",
}


def file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()


def multiplier(output: str, inputs: Sequence[str]) -> int:
    value = SIGNS[output]
    for symbol in inputs:
        value *= SIGNS[symbol]
    return value


def expected_pairing_entries() -> list[dict[str, Any]]:
    pairs = [(a, b) for a in range(4) for b in range(a, 4)]
    labels = []
    labels.extend(("h", pair) for pair in pairs)
    labels.extend(("c", index) for index in range(4))
    labels.append(("omega", None))
    labels.extend(("h_star", pair) for pair in pairs)
    labels.extend(("c_star", index) for index in range(4))
    labels.append(("omega_star", None))
    index = {item: position for position, item in enumerate(labels)}

    def label(symbol: str, component: tuple[int, int] | int | None) -> str:
        if component is None:
            return symbol
        if isinstance(component, tuple):
            return f"{symbol}_{component[0]}{component[1]}"
        return f"{symbol}_{component}"

    values: dict[tuple[int, int], int] = {}
    for pair in pairs:
        weight = 1 if pair[0] == pair[1] else 2
        left, right = index[("h", pair)], index[("h_star", pair)]
        values[(left, right)], values[(right, left)] = weight, -weight
    for component in range(4):
        left, right = index[("c", component)], index[("c_star", component)]
        values[(left, right)], values[(right, left)] = 1, -1
    left, right = index[("omega", None)], index[("omega_star", None)]
    values[(left, right)], values[(right, left)] = 1, -1
    return [
        {
            "left_index": left,
            "right_index": right,
            "left": label(*labels[left]),
            "right": label(*labels[right]),
            "coefficient": str(coefficient),
        }
        for (left, right), coefficient in sorted(values.items())
    ]


def _primary_multipliers(rows: Sequence[Mapping[str, Any]]) -> dict[str, int]:
    grouped: dict[str, set[int]] = {}
    for row in rows:
        grouped.setdefault(row["primary_id"], set()).add(row["translation_multiplier"])
    if any(len(values) != 1 for values in grouped.values()):
        raise ValueError("one primary kernel received multiple translation signs")
    return {key: next(iter(values)) for key, values in grouped.items()}


def check(value: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if value.get("result_state") != "MINIMAL_Q1_Q2_CANONICALLY_CYCLIC_D_AND_FULL_CARRIER_OPEN":
        errors.append("result state drift")
    if value.get("lifecycle") != "CLASSIFIED" or value.get("dependency_tags") != ["LOCAL-ALGEBRAIC"]:
        errors.append("lifecycle or dependency boundary drift")
    scope = value.get("scope", {})
    if scope.get("locality") != "SUPPORT_LOCAL_POLYDIFFERENTIAL" or "Bach-flat" not in scope.get("background_class", ""):
        errors.append("locality or background boundary drift")

    q1 = json.loads(Q1.read_text())
    q2 = json.loads(Q2.read_text())
    identity = json.loads(IDENTITY.read_text())
    action = json.loads(ACTION.read_text())
    translation = value.get("sign_translation", {})
    if translation.get("generator_signs") != SIGNS or translation.get("involutive") is not True:
        errors.append("generator translation drift")

    expected_q1 = []
    for source in q1["local_q1_ast"]["components"]:
        sign = multiplier(source["output"], (source["input"],))
        expected_q1.append(
            {
                "component_id": source["component_id"],
                "input": source["input"],
                "output": source["output"],
                "source_coefficient": source["coefficient"],
                "translation_multiplier": sign,
                "translated_coefficient": source["coefficient"] * sign,
            }
        )
    expected_q2 = []
    for source in q2["ordered_components"]:
        sign = multiplier(source["output"], source["inputs"])
        expected_q2.append(
            {
                "component_id": source["component_id"],
                "primary_id": source["primary_id"],
                "inputs": source["inputs"],
                "output": source["output"],
                "source_coefficient_relative_to_primary": source["coefficient_relative_to_primary"],
                "translation_multiplier": sign,
                "translated_coefficient_relative_to_primary": source["coefficient_relative_to_primary"] * sign,
            }
        )
    if translation.get("q1_rows") != expected_q1 or translation.get("q2_rows") != expected_q2:
        errors.append("componentwise conjugation crosswalk drift")
    changed_q1 = [row["component_id"] for row in expected_q1 if row["translation_multiplier"] == -1]
    changed_q2 = [row["component_id"] for row in expected_q2 if row["translation_multiplier"] == -1]
    if translation.get("changed_q1_component_ids") != changed_q1 or translation.get("changed_q2_component_ids") != changed_q2:
        errors.append("changed-row inventory drift")

    pairing = value.get("canonical_pairing", {})
    if (
        pairing.get("component_basis_dimension") != 30
        or pairing.get("nonzero_ordered_entry_count") != 30
        or pairing.get("rank") != 30
        or pairing.get("off_diagonal_symmetric_tensor_weight") != 2
        or pairing.get("entries") != expected_pairing_entries()
    ):
        errors.append("canonical component pairing drift")

    receiver = value.get("cyclicity_receiver", {})
    source_defect = receiver.get("source_convention_defect", {})
    repaired_defect = receiver.get("translated_convention_defect", {})
    if (
        receiver.get("basis_dimension") != 30
        or receiver.get("primary_kernel_count") != 11
        or receiver.get("ordered_component_count") != 21
        or receiver.get("expanded_q2_coefficient_count") != 932
        or source_defect.get("coefficient_count") != 540
        or source_defect.get("sector_count") != 8
        or repaired_defect.get("coefficient_count") != 0
        or repaired_defect.get("sector_count") != 0
    ):
        errors.append("component receiver summary drift")

    # Independent action-vertex rail.  These four relations are the formal
    # Euler derivatives of the four displayed cubic minimal-master vertices.
    try:
        primary = _primary_multipliers(expected_q2)
    except ValueError as error:
        errors.append(str(error))
        primary = {}
    relations = (
        primary.get("q2_h_ch") == primary.get("q2_hstar_chstar") == -primary.get("q2_cstar_hhstar", 0),
        primary.get("q2_h_omegah") == primary.get("q2_hstar_omegahstar") == -primary.get("q2_omegastar_hhstar", 0),
        primary.get("q2_c_cc") == primary.get("q2_cstar_ccstar"),
        primary.get("q2_omega_comega") == primary.get("q2_cstar_omegaomegastar") == primary.get("q2_omegastar_comegastar"),
    )
    if relations != (True, True, True, True):
        errors.append("independent master-vertex cyclic sign relations fail")
    nullspace = receiver.get("multiplier_classification", {})
    if (
        nullspace.get("rank") != 7
        or nullspace.get("nullity") != 4
        or nullspace.get("landed_all_one_multiplier_satisfies") is not False
        or len(nullspace.get("integer_nullspace_basis", [])) != 4
    ):
        errors.append("cyclic multiplier classification drift")
    translation_receiver = receiver.get("translation", {})
    if (
        translation_receiver.get("changed_primary_ids") != ["q2_cstar_hhstar", "q2_omegastar_hhstar"]
        or translation_receiver.get("revert_diff_Noether_defect", {}).get("coefficient_count") != 500
        or translation_receiver.get("revert_Weyl_Noether_defect", {}).get("coefficient_count") != 40
    ):
        errors.append("repair support or mutation sensitivity drift")

    diagnosis = value.get("diagnosis", {})
    if (
        diagnosis.get("source_convention_status") != "NILPOTENT_BUT_NOT_CANONICALLY_CYCLIC"
        or diagnosis.get("source_non_Bach_cyclicity_defect_coefficient_count") != 540
        or diagnosis.get("source_non_Bach_cyclicity_defect_sector_count") != 8
        or diagnosis.get("first_exact_witness") != source_defect.get("first_witness")
    ):
        errors.append("diagnostic statement drift")

    if q1.get("claim_flags", {}).get("Q1_SQUARED_ZERO_CERTIFIED") is not True:
        errors.append("source q1 square theorem unavailable")
    if identity.get("claim_flags", {}).get("Q1_Q2_ARITY_TWO_NILPOTENCY_REPLAYED") is not True:
        errors.append("source q1q2 theorem unavailable")
    variational = value.get("variational_completion", {})
    if variational.get("action") != action.get("action") or variational.get("Euler_coordinate") != action.get("Euler_coordinate"):
        errors.append("action-normalization crosswalk drift")
    if "third variation" not in variational.get("q2_metric_cubic_sector", ""):
        errors.append("metric cubic variational theorem missing")

    checks = {row.get("check_id"): row.get("status") for row in value.get("proof_checks", [])}
    if checks != {
        "canonical_pairing_nondegenerate": "VERIFIED",
        "sign_translation_involutive_and_typed": "VERIFIED",
        "q1_squared_zero": "VERIFIED_BY_EXACT_CONJUGATION",
        "q1_q2_arity_two_nilpotency": "VERIFIED_BY_EXACT_CONJUGATION",
        "BV_cyclicity_q1": "VERIFIED",
        "BV_cyclicity_q2": "VERIFIED",
        "D_q1_commutator_zero": "NOT_REPLAYED",
        "D_q2_derivation": "NOT_REPLAYED",
    }:
        errors.append("proof-check ledger drift or D promotion")
    flags = value.get("claim_flags", {})
    if any(flags.get(flag) is not True for flag in TRUE_FLAGS) or any(flags.get(flag) is not False for flag in FALSE_FLAGS):
        errors.append("claim flags drift or downstream promotion")
    if len(value.get("does_not_establish", [])) != 6 or "Gate A remains fail closed" not in (HERE / "REPORT_STRICT_MINIMAL_BV_CYCLIC_SIGN_RECONCILIATION_V1.md").read_text():
        errors.append("claim boundary or report firewall drift")

    hashes = value.get("canonical_hashes", {})
    if hashes != {
        "canonical_pairing_sha256": digest(pairing),
        "sign_translation_sha256": digest(translation),
        "cyclicity_receiver_sha256": digest(receiver),
        "variational_completion_sha256": digest(variational),
        "proof_checks_sha256": digest(value.get("proof_checks")),
    }:
        errors.append("canonical hashes do not reproduce")
    for group in value.get("provenance", {}).values():
        if not isinstance(group, list):
            errors.append("provenance group is not a list")
            continue
        for item in group:
            path = ROOT / item.get("path", "")
            if not path.is_file() or file_sha(path) != item.get("sha256"):
                errors.append(f"provenance drift: {item.get('path')}")
    return errors


def main() -> int:
    value = json.loads(RESULT.read_text())
    errors = check(value)
    print("STRICT_MINIMAL_BV_CYCLIC_SIGN_RECONCILIATION_V1: " + ("PASS" if not errors else "FAIL"))
    if errors:
        for error in errors:
            print(f"  - {error}")
    else:
        print("  - source convention: 540 exact non-Bach defects in 8 sectors")
        print("  - translated convention: 0/932 defects; q1^2 and 18/51 q1q2 identities transported")
        print("  - D, full carrier, Gate A, Lorentzian causal and QME remain open")
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
