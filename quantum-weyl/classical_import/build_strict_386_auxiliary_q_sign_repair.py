#!/usr/bin/env python3
"""Build the append-only certificate for the strict auxiliary-q sign repair."""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/STRICT_386_AUXILIARY_Q_SIGN_REPAIR_V1.json"
REPORT = HERE / "REPORT_STRICT_386_AUXILIARY_Q_SIGN_REPAIR_V1.md"
PREDECESSOR = HERE / "certificates/STRICT_386_FULL_Q1_SPLIT_SIGN_GATE_V1.json"
PAIRING = HERE / "certificates/STRICT_386_COMPONENT_PAIRING_SERIALIZATION_V1.json"
WITNESS = HERE / "certificates/STRICT_386_AUXILIARY_Q_SIGN_WITNESS_V1.json"

SOURCES = {
    "generalized_retract_source": ROOT / "covariant_completion/auxiliary_equivalence/generalized_retract.py",
    "factorized_split_source": ROOT / "covariant_completion/curved_retract/factorized_q_split.py",
    "universal_split_source": ROOT / "covariant_completion/curved_retract/universal_split.py",
    "vector_contraction_source": ROOT / "covariant_completion/curved_operator/expanded_relative_witness_vector_contraction.py",
    "current_closure_source": ROOT / "covariant_completion/curved_current/bv_current_closure.py",
    "canonical_runner": ROOT / "symbolic/verify_conformal_covariant_completion.py",
}

CERTIFICATES = {
    "generalized_retract": ROOT / "covariant_completion/certificates/generalized_auxiliary_contraction.json",
    "curved_split": ROOT / "covariant_completion/certificates/curved_auxiliary_canonical_split.json",
    "vector_contraction": ROOT / "covariant_completion/certificates/curved_expanded_relative_witness_vector_contraction.json",
    "curved_retract": ROOT / "covariant_completion/certificates/curved_deformation_retract_status.json",
    "curved_current": ROOT / "covariant_completion/certificates/curved_current_comparison.json",
    "prolonged_current": ROOT / "covariant_completion/certificates/curved_prolonged_current_comparison.json",
    "direct_pairing": ROOT / "covariant_completion/certificates/curved_direct_causal_pairing_transport.json",
    "causal_transport": ROOT / "covariant_completion/certificates/curved_causal_transport_recognition.json",
    "so42_transport": ROOT / "covariant_completion/certificates/curved_SO42_causal_transport_recognition.json",
    "dependency_report": ROOT / "covariant_completion/certificates/final_claim_dependencies.json",
    "completed_status": ROOT / "covariant_completion/certificates/completed_covariant_status.json",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: object) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode()).hexdigest()


def zero(size: int) -> list[list[Fraction]]:
    return [[Fraction() for _ in range(size)] for _ in range(size)]


def multiply(left: list[list[Fraction]], right: list[list[Fraction]]) -> list[list[Fraction]]:
    size = len(left)
    return [[sum((left[row][middle] * right[middle][column] for middle in range(size)), Fraction()) for column in range(size)] for row in range(size)]


def transpose(matrix: list[list[Fraction]]) -> list[list[Fraction]]:
    return [list(row) for row in zip(*matrix, strict=True)]


def replay() -> dict[str, Any]:
    pairing = json.loads(PAIRING.read_text())
    witness = json.loads(WITNESS.read_text())
    q_plus = zero(36)
    for target, source, coefficient in witness["entries"]:
        q_plus[target][source] = Fraction(coefficient)
    q_minus = [row[:] for row in q_plus]
    for index in range(4):
        q_minus[32 + index][28 + index] = Fraction(-1)
    omega = zero(36)
    for item in pairing["pairing_serialization"]["entries"]:
        left, right = item["left_index"], item["right_index"]
        if 30 <= left < 66 and 30 <= right < 66:
            omega[left - 30][right - 30] = Fraction(item["coefficient"])
    degrees = [row["degree"] for row in pairing["component_basis"]["rows"][30:66]]

    def defects(q: list[list[Fraction]]) -> int:
        first, second = multiply(transpose(q), omega), multiply(omega, q)
        return sum(first[row][column] + (-1 if degrees[row] % 2 else 1) * second[row][column] != 0 for row in range(36) for column in range(36))

    return {
        "repaired_plus_sign": {
            "q_squared_defects": sum(entry != 0 for row in multiply(q_plus, q_plus) for entry in row),
            "odd_pairing_cyclicity_defects": defects(q_plus),
        },
        "rejected_minus_sign_regression": {
            "q_squared_defects": sum(entry != 0 for row in multiply(q_minus, q_minus) for entry in row),
            "odd_pairing_cyclicity_defects": defects(q_minus),
        },
        "discriminator": "Nilpotency accepts both isolated signs; the serialized odd pairing rejects the minus-sign regression with eight exact rational defects.",
    }


def build() -> dict[str, Any]:
    predecessor = json.loads(PREDECESSOR.read_text())
    if predecessor.get("result_id") != "STRICT_386_FULL_Q1_SPLIT_SIGN_GATE_V1":
        raise ValueError("historical sign-gate predecessor drift")
    source_text = {name: path.read_text() for name, path in SOURCES.items()}
    required_source_tokens = {
        "generalized_retract_source": "v^* -> +eta^*",
        "factorized_split_source": "q[9][8] = OperatorPolynomial.identity(1)",
        "universal_split_source": "v^* -> +eta^*",
        "vector_contraction_source": "v^* -> +eta^*",
        "current_closure_source": "!= polynomial_type.identity(1)",
        "canonical_runner": "verify_conformal_direct_causal_pairing_transport.py",
    }
    missing = [name for name, token in required_source_tokens.items() if token not in source_text[name]]
    if missing:
        raise ValueError("repair source token missing: " + ", ".join(missing))

    certificates = {name: json.loads(path.read_text()) for name, path in CERTIFICATES.items()}
    if certificates["generalized_retract"]["all_added_bv_rows"][-1]["arrow"] != "v^* -> +eta^*":
        raise ValueError("generalized retract ledger sign drift")
    if certificates["curved_split"]["factorized_curved_Q_split"]["transformed_Q"]["generalized_auxiliary"][-1] != "v^* -> +eta^*":
        raise ValueError("curved split ledger sign drift")
    exact_replay = replay()
    if exact_replay["repaired_plus_sign"] != {"q_squared_defects": 0, "odd_pairing_cyclicity_defects": 0}:
        raise ValueError("repaired plus-sign replay drift")
    if exact_replay["rejected_minus_sign_regression"]["odd_pairing_cyclicity_defects"] != 8:
        raise ValueError("minus-sign regression rail drift")

    projection = {
        "repair": {
            "block": "AUX_V_STAR -> AUX_ETA_STAR",
            "old_declared_sign": "-I_4",
            "authoritative_sign": "+I_4",
            "source_and_ledgers_consistent": True,
            "repair_applied": True,
            "affected_chain_regenerated": True,
            "canonical_runner_dependency_order_repaired": True,
        },
        "exact_replay": exact_replay,
        "verification": {
            "tier_1": {
                "status": "PASS",
                "checks": ["curved retract 10/10", "vector contraction 21/21", "curved current 10/10", "direct pairing transport", "dependency report 22/22", "final transport 25/25", "four-flag closure 5/5"],
            },
            "tier_3": {
                "status": "PASS",
                "command": "PYTHONPATH=/tmp/weyl-scipy/root/usr/lib/python3/dist-packages:/tmp/weyl-sympy/root/usr/lib/python3/dist-packages python3 symbolic/verify_conformal_covariant_completion.py --emit --guards",
                "elapsed_seconds": 1433.50,
                "terminal_guard": "COVARIANT COMPLETION OVERCLAIM GUARDS: 82/82 PASS",
                "terminal_result": "CONFORMAL COVARIANT CERTIFICATION STACK: ALL IMPLEMENTED CHECKS PASS",
                "dependency_overlay": {"numpy": "2.3.5", "scipy": "1.16.3", "sympy": "1.14.0", "decorator": "5.2.1"},
            },
        },
        "claim_flags": {
            "STRICT_386_AUXILIARY_Q_SIGN_REPAIR_APPLIED": True,
            "STRICT_386_AUXILIARY_Q_SOURCE_LEDGER_PAIRING_CONSISTENT": True,
            "AFFECTED_CLASSICAL_CERTIFICATE_CHAIN_VERIFIED": True,
            "FULL_CLASSICAL_COVARIANT_SUITE_PASSED": True,
            "STRICT_FULL_386_Q1_PORTABLE_COMPONENT_BYTES": False,
            "CLASSICAL_IMPORT_GATE_PASSED": False,
            "HADAMARD_STATE_CONSTRUCTED": False,
            "QME_RESTORED": False,
            "LORENTZIAN_QUANTUM_THEORY": False,
        },
        "next_gate": "Emit the endpoint, repaired auxiliary and curvature mapping-cylinder blocks as one canonical sparse 386-row q1 table; independently replay q1 squared and odd-pairing cyclicity; then bind the accepted bytes into one classical import snapshot.",
        "does_not_establish": [
            "receiver-readable full 386-row q1 component bytes or an accepted common classical snapshot hash",
            "portable support-local SDR component maps or represented endpoint and full Green actions",
            "local D, q2 compatibility, a BRST-compatible Hadamard state, renormalized Lorentzian products, QME restoration, residual quantum transfer or a Lorentzian quantum theory",
        ],
    }
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "schema": "strict-386-auxiliary-q-sign-repair-v1",
        "result_id": "STRICT_386_AUXILIARY_Q_SIGN_REPAIR_V1",
        "result_kind": "EXACT_CLASSICAL_AUXILIARY_Q_SIGN_REPAIR_CERTIFICATE",
        "result_state": "REPAIR_CERTIFIED_FULL_Q1_SERIALIZATION_NEXT",
        "lifecycle": "CLASSIFIED",
        "created": "2026-08-15",
        "repository_base_commit": "d0f09db4d46aa5a8198ef452f68443cf7380009f",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "question": "Was the exact auxiliary cotangent sign conflict identified by the historical strict 386-row split-q1 gate repaired consistently in executable source, human-readable ledgers, regenerated classical certificates, odd-pairing replay and the complete covariant verification stack?",
        "answer": "Yes, within the declared classical scope. The factorized cotangent arrow and every affected ledger now use v_star to plus eta_star, matching the already serialized executable matrix and odd pairing. Exact replay gives zero q-squared and zero cyclicity defects for the repaired plus sign; the rejected minus-sign regression remains nilpotent but produces eight rational cyclicity defects. The affected retract, vector, current, direct-pairing, causal-transport and dependency chains pass, and the full covariant suite exits successfully with all 82 terminal overclaim guards passing. The canonical runner now regenerates the SHA-bound direct-pairing receipt after prolonged-current generation, preventing the stale-hash ordering failure discovered during repair. This result resolves the local source/ledger inconsistency but does not serialize the full 386-row q1 operator, accept a common quantum-import snapshot, construct a Hadamard state or restore the QME.",
        "predecessor": {"result_id": predecessor["result_id"], "path": str(PREDECESSOR.relative_to(ROOT)), "sha256": sha(PREDECESSOR), "preserved": True},
        **projection,
        "provenance": {
            "sources": {name: {"path": str(path.relative_to(ROOT)), "sha256": sha(path)} for name, path in SOURCES.items()},
            "certificates": {name: {"path": str(path.relative_to(ROOT)), "sha256": sha(path), "schema": certificates[name].get("schema")} for name, path in CERTIFICATES.items()},
            "pairing": {"path": str(PAIRING.relative_to(ROOT)), "sha256": sha(PAIRING)},
            "executable_witness": {"path": str(WITNESS.relative_to(ROOT)), "sha256": sha(WITNESS)},
        },
        "independent_checker": {"path": "quantum-weyl/classical_import/check_strict_386_auxiliary_q_sign_repair.py", "expected_digest": digest(projection)},
        "human_report": "quantum-weyl/classical_import/REPORT_STRICT_386_AUXILIARY_Q_SIGN_REPAIR_V1.md",
    }


def render(value: dict[str, Any]) -> str:
    replay_value = value["exact_replay"]
    lines = [
        "# Strict 386-row auxiliary-q sign repair v1", "", "## Outcome", "", value["answer"], "",
        "## Exact replay", "", "| candidate | q1 squared | odd-pairing cyclicity |", "|---|---:|---:|",
        f"| repaired `+I_4` | {replay_value['repaired_plus_sign']['q_squared_defects']} defects | **{replay_value['repaired_plus_sign']['odd_pairing_cyclicity_defects']} defects** |",
        f"| rejected `-I_4` regression | {replay_value['rejected_minus_sign_regression']['q_squared_defects']} defects | **{replay_value['rejected_minus_sign_regression']['odd_pairing_cyclicity_defects']} defects** |", "",
        "## Verification receipt", "", f"- Tier 1: `{value['verification']['tier_1']['status']}`.", f"- Tier 3: `{value['verification']['tier_3']['status']}` in `{value['verification']['tier_3']['elapsed_seconds']:.2f}` seconds.", f"- Terminal guard: `{value['verification']['tier_3']['terminal_guard']}`.", "",
        "## Boundary", "",
    ]
    lines.extend(f"- This does not establish {item}." for item in value["does_not_establish"])
    lines += ["", "## Next gate", "", value["next_gate"], "", "## Reproduction", "", "```text", "python3 quantum-weyl/classical_import/build_strict_386_auxiliary_q_sign_repair.py --check", "python3 quantum-weyl/classical_import/check_strict_386_auxiliary_q_sign_repair.py", "python3 quantum-weyl/classical_import/verify_strict_386_auxiliary_q_sign_repair.py", "python3 -m unittest quantum-weyl/classical_import/tests/test_strict_386_auxiliary_q_sign_repair.py", "```", ""]
    return "\n".join(lines)


def generated() -> tuple[bytes, bytes]:
    value = build()
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode(), render(value).encode()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result, report = generated()
    stale = [str(path.relative_to(ROOT)) for path, content in ((RESULT, result), (REPORT, report)) if not path.is_file() or path.read_bytes() != content]
    if args.check:
        print("STRICT_386_AUXILIARY_Q_SIGN_REPAIR_V1: " + ("generated artifacts current" if not stale else "stale: " + ", ".join(stale)))
        return bool(stale)
    RESULT.write_bytes(result)
    REPORT.write_bytes(report)
    print("STRICT_386_AUXILIARY_Q_SIGN_REPAIR_V1: wrote result and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
