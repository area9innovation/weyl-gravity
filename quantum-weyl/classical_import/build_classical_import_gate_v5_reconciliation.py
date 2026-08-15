#!/usr/bin/env python3
"""Build Gate-A v5 after canonical minimal pairing/sign reconciliation."""

from __future__ import annotations

import argparse
from copy import deepcopy
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
V4 = HERE / "certificates/CLASSICAL_IMPORT_GATE_V4_RECONCILIATION.json"
CYCLIC = HERE / "certificates/STRICT_MINIMAL_BV_CYCLIC_SIGN_RECONCILIATION_V1.json"
RESULT = HERE / "certificates/CLASSICAL_IMPORT_GATE_V5_RECONCILIATION.json"
REPORT = HERE / "REPORT_GATE_V5.md"


def file_hash(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def digest(value: dict[str, Any]) -> str:
    payload = {
        key: value[key]
        for key in (
            "standalone_history_replay",
            "status_vocabulary",
            "export_reconciliation",
            "freeze_check_reconciliation",
            "required_hash_disposition",
            "minimal_missing_bundle",
            "gate_disposition",
            "m3_scoped_resolution",
            "m2_minimal_resolution",
            "m4_minimal_resolution",
        )
    }
    return sha256(
        dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()


def build() -> dict[str, Any]:
    previous, cyclic = (loads(path.read_text()) for path in (V4, CYCLIC))
    if previous.get("result_id") != "CLASSICAL_IMPORT_GATE_V4_RECONCILIATION" or previous.get("gate_disposition", {}).get("gate_a_status") != "FAIL_CLOSED":
        raise ValueError("V4 predecessor drift")
    flags = cyclic.get("claim_flags", {})
    if not all(flags.get(name) is True for name in ("CANONICAL_MINIMAL_BV_PAIRING_SERIALIZED", "BV_CYCLICITY_Q1_REPLAYED", "BV_CYCLICITY_Q2_REPLAYED")) or flags.get("CLASSICAL_IMPORT_GATE_PASSED") is not False:
        raise ValueError("cyclic sign reconciliation unavailable or over-promoted")

    value = deepcopy(previous)
    value.update(
        {
            "schema": "quantum-weyl-classical-import-gate-v5-reconciliation-v1",
            "result_id": "CLASSICAL_IMPORT_GATE_V5_RECONCILIATION",
            "result_state": "MINIMAL_Q1_Q2_PAIRING_CYCLIC_REPAIRED_D_FULL_CARRIER_OPEN",
            "created": "2026-08-15",
            "repository_base_commit": "6994434dd201a0ec6bfd6d835b1c981ac9df12b7",
            "question": "After discovering that the nilpotent strict minimal q1/q2 receiver convention is not cyclic under the canonical odd BV pairing, and certifying an involutive ghost-antifield sign translation that restores q1/q2 cyclicity without changing the L-infinity identities, which Gate-A M2/M4 rows are now receiver-verified, what remains for the common full carrier, and does Gate A pass?",
            "answer": "The source minimal convention is nilpotent but not canonically cyclic: an exact thirty-component receiver expands eleven non-Bach primary kernels into 932 bilinear coefficients, lowers them with the canonical odd cotangent pairing, performs formal integration by parts, and finds 540 defects in eight ordered sectors. The involution T(h,c,omega,h_star,c_star,omega_star)=(h,c,omega,h_star,-c_star,-omega_star) translates q1/q2 by exact conjugation. It changes two q1 components and four ordered q2 components, preserves q1 squared and the eighteen-channel/fifty-one-path q1q2 theorem, and yields zero non-Bach defects. The metric unary and cubic sectors are the second and third variations of the pinned local Weyl action. Thus the minimal canonical pairing export and q2 cyclic check become RECEIVER_VERIFIED_SCOPED. Gate A remains FAIL_CLOSED: the pairing and translation do not yet cover every nonminimal, auxiliary and residual row on one snapshot; local D and both D identities are absent; the continuum residual SDR, SO(4,2) payload, centered representatives and seven common hashes remain unresolved. No Lorentzian, Hadamard, QME or quantum claim follows.",
            "supersedes_for_current_status": "CLASSICAL_IMPORT_GATE_V4_RECONCILIATION",
            "human_report": "quantum-weyl/classical_import/REPORT_GATE_V5.md",
        }
    )

    exports = {row["export_id"]: row for row in value["export_reconciliation"]}
    checks = {row["check_id"]: row for row in value["freeze_check_reconciliation"]}
    exports["local_classical_bv_differential_q0"].update(
        {
            "evidence": [*exports["local_classical_bv_differential_q0"]["evidence"], cyclic["result_id"]],
            "established": "The strict minimal q1 payload and its canonical ghost-antifield sign translation are exact conjugates, so q1 squared remains zero in the pairing-compatible convention.",
            "remaining_for_gate_a": "Extend the translated convention and q0 to every nonminimal, auxiliary and residual row on the common full Gate-A carrier.",
            "boundary": "An exact minimal-sector conjugation does not serialize the full nonminimal/residual differential or its common snapshot hash.",
        }
    )
    exports["support_local_classical_bv_q2"].update(
        {
            "evidence": ["STRICT_SIX_ROW_SUSPENDED_Q2_AST_V1", "STRICT_LOCAL_Q1_Q2_IDENTITY_V1", cyclic["result_id"]],
            "established": "All six strict minimal q2 rows are portable in the canonical pairing-compatible sign convention; q1q2, Koszul symmetry and q2 cyclicity are exact in scope.",
            "remaining_for_gate_a": "Extend translated q2 to every retained nonminimal or auxiliary interaction row and bind it to local D, residual maps, pairing and common hashes on one full carrier.",
            "boundary": "The complete support-local export remains open because local D and the full-carrier extension are absent.",
        }
    )
    exports["cyclic_pairing"].update(
        {
            "status": "RECEIVER_VERIFIED_SCOPED",
            "evidence": [cyclic["result_id"]],
            "established": "The canonical support-local odd cotangent pairing is serialized on all thirty independent components of the six minimal generators, has rank thirty, and makes translated q1/q2 cyclic.",
            "remaining_for_gate_a": "Extend the pairing and sign convention to every nonminimal, auxiliary and residual common-snapshot row and replay SDR cyclic side conditions.",
            "boundary": "A nondegenerate cyclic minimal pairing is not the full common-carrier pairing and does not establish cyclicity of the residual SDR.",
        }
    )
    checks["q1_q2_arity_two_nilpotency"].update(
        {
            "evidence": ["STRICT_LOCAL_Q1_Q2_IDENTITY_V1", cyclic["result_id"]],
            "established": "The eighteen-channel/fifty-one-path minimal q1q2 identity is preserved exactly by the involutive canonical sign conjugation.",
            "remaining_for_gate_a": "Replay on the common full carrier if nonminimal or auxiliary interaction rows extend the translated minimal q2.",
            "boundary": "Conjugation preserves the scoped identity but supplies neither local D nor the common full-carrier snapshot.",
        }
    )
    checks["q2_cyclic_compatibility"].update(
        {
            "status": "RECEIVER_VERIFIED_SCOPED",
            "evidence": [cyclic["result_id"]],
            "established": "Translated minimal q2 has zero exact cyclicity defects: 932 non-Bach coefficients vanish modulo integration by parts and the metric cubic is the symmetric third action variation.",
            "remaining_for_gate_a": "Replay after extending the pairing and translated convention to the common full nonminimal/residual carrier.",
            "boundary": "Minimal q2 cyclicity does not establish full SDR cyclic compatibility or a Lorentzian/quantum statement.",
        }
    )

    for item in value["minimal_missing_bundle"]:
        if item["id"] == "M2_STRICT_Q2_D":
            item["object"] = "Bind the canonically translated and cyclic minimal q1/q2 payload to the common full carrier, add required nonminimal/auxiliary interaction rows, and serialize local D; then replay [D,q1] and D/q2."
            item["unlocks"] = ["full-carrier support-local q2 export", "D_q1_commutator_zero", "D_q2_derivation"]
        elif item["id"] == "M4_FULL_CYCLIC_PAIRING":
            item["object"] = "Extend the rank-thirty minimal canonical pairing and sign translation to every common-carrier nonminimal, auxiliary and residual row, then replay q1/q2 and residual-SDR cyclic side conditions."
            item["unlocks"] = ["full-carrier cyclic_pairing", "cyclic_compatibility", "full-carrier q2_cyclic_compatibility"]
    value["gate_disposition"].update(
        {
            "claim_state": "CLASSICAL_IMPORT_MINIMAL_Q1_Q2_PAIRING_CYCLIC_REPAIRED_D_FULL_CARRIER_OPEN",
            "same_theory_receiver_verified_scoped": 10,
            "different_theory_controls": 1,
            "supporting_evidence_only": 6,
            "freeze_checks_receiver_verified_scoped": 7,
            "freeze_checks_different_theory": 2,
        }
    )
    value["m2_minimal_resolution"].update(
        {
            "status": "STRICT_MINIMAL_Q1_Q2_ARITY_TWO_AND_CYCLIC_CONVENTION_CERTIFIED",
            "evidence": [*value["m2_minimal_resolution"]["evidence"], cyclic["result_id"]],
            "remaining": "The local D action, [D,q1], D derivation, full-carrier nonminimal/auxiliary extension and accepted common hashes remain open; minimal pairing/cyclicity is no longer missing.",
            "boundary": "This resolves q1/q2 and canonical cyclicity only on the strict minimal carrier, not the complete M2 full-carrier or D bundle.",
        }
    )
    value["m4_minimal_resolution"] = {
        "status": "STRICT_MINIMAL_CANONICAL_PAIRING_AND_Q1_Q2_CYCLICITY_CERTIFIED",
        "evidence": cyclic["result_id"],
        "component_basis_dimension": cyclic["canonical_pairing"]["component_basis_dimension"],
        "pairing_rank": cyclic["canonical_pairing"]["rank"],
        "expanded_non_Bach_q2_coefficient_count": cyclic["cyclicity_receiver"]["expanded_q2_coefficient_count"],
        "source_convention_defect_coefficient_count": cyclic["diagnosis"]["source_non_Bach_cyclicity_defect_coefficient_count"],
        "translated_convention_defect_coefficient_count": cyclic["cyclicity_receiver"]["translated_convention_defect"]["coefficient_count"],
        "remaining": "Nonminimal, auxiliary and residual pairing rows plus common-SDR adjointness and cyclic side conditions remain open.",
        "boundary": "The minimal rank-thirty pairing is a proper scoped subcarrier result, accepts no top-level Gate-A hash, and supplies no full residual-SDR cyclicity theorem.",
    }
    value["provenance"]["inputs"] = [
        *previous["provenance"]["inputs"],
        {"path": str(V4.relative_to(ROOT)), "result_or_artifact_id": previous["result_id"], "sha256": file_hash(V4), "role": "immutable Gate-A V4 predecessor"},
        {"path": str(CYCLIC.relative_to(ROOT)), "result_or_artifact_id": cyclic["result_id"], "sha256": file_hash(CYCLIC), "role": "canonical minimal pairing and cyclic sign reconciliation"},
    ]
    value["claim_flags"].update(
        {
            "STRICT_MINIMAL_CANONICAL_PAIRING_SCOPED_REPLAY": True,
            "STRICT_MINIMAL_Q1_Q2_CYCLICITY_SCOPED_REPLAY": True,
            "CANONICAL_GHOST_ANTIFIELD_SIGN_TRANSLATION": True,
        }
    )
    value["does_not_establish"] = [
        *previous["does_not_establish"],
        "that the minimal rank-thirty pairing already includes every nonminimal, auxiliary or residual Gate-A row",
        "that the source receiver convention is cyclic without the explicit ghost-antifield sign translation",
    ]
    value["next_gate"] = "Use STRICT_MINIMAL_BV_CYCLIC_SIGN_RECONCILIATION_V1 as the canonical minimal convention. Extend T, q1, q2 and the odd pairing together to every retained nonminimal and auxiliary row, and bind those bytes to the common support-local carrier. Independently select the background-specific residual generator D, serialize its action on that same carrier, and replay [D,q1] and D/q2. Then extend the finite residual SDR and cyclic side conditions to those common bytes and reconcile M1/M3/M5/M6. Do not promote the minimal cyclic theorem to a full-carrier, causal, Hadamard or QME claim."
    value["independent_checker"] = {
        "path": "quantum-weyl/classical_import/check_classical_import_gate_v5_reconciliation.py",
        "checks": [
            "V4 predecessor and cyclic-reconciliation pins",
            "twenty-export and ten-check order",
            "minimal q0/q2/q1q2 rebound to translated convention",
            "one cyclic-pairing scoped promotion",
            "one q2-cyclicity scoped promotion",
            "rank-thirty and 540-to-zero crosswalk",
            "D rows unchanged",
            "full cyclic-SDR check unchanged and blocked",
            "zero accepted common hashes",
            "Gate-A fail-closed counts",
            "M2/M4 minimal-versus-full-carrier boundary",
        ],
        "expected_digest": digest(value),
    }
    return value


def report(value: dict[str, Any]) -> str:
    m4 = value["m4_minimal_resolution"]
    pairing = next(row for row in value["export_reconciliation"] if row["export_id"] == "cyclic_pairing")
    cyclic = next(row for row in value["freeze_check_reconciliation"] if row["check_id"] == "q2_cyclic_compatibility")
    return f"""# Classical import Gate-A reconciliation v5

**Result:** `{value['result_id']}`

**Lifecycle:** `{value['lifecycle']}`

**Gate A:** `{value['gate_disposition']['gate_a_status']}`

## Outcome

The strict minimal carrier now has one explicit canonical pairing convention.
The source receiver convention was nilpotent but produced
**{m4['source_convention_defect_coefficient_count']} exact non-Bach cyclicity
defects**. The involution `c_star -> -c_star`,
`omega_star -> -omega_star` preserves q1 squared and all 18 q1q2 channels / 51
paths, and reduces the exact defect count to
**{m4['translated_convention_defect_coefficient_count']}**.

## Scoped promotions

| Obligation | Status | Established | Still required |
|---|---|---|---|
| `cyclic_pairing` | `{pairing['status']}` | {pairing['established']} | {pairing['remaining_for_gate_a']} |
| `q2_cyclic_compatibility` | `{cyclic['status']}` | {cyclic['established']} | {cyclic['remaining_for_gate_a']} |

The pairing has dimension and rank **{m4['pairing_rank']}**. The 932 non-Bach
coefficients are normalized modulo exact integration by parts. The Bach unary
and cubic sectors are the second and third variations of the pinned action.

## What remains

M4 is repaired only in the minimal sector. The sign convention, q1/q2 and
pairing must be extended to the nonminimal, auxiliary and residual rows on one
common carrier. General `cyclic_compatibility` remains blocked on the full
pairing and residual SDR.

M2 is now dominated by local `D`: its background-specific generator has not
been selected on the common carrier, and neither D identity has been replayed.
M1, M3, M5 and M6 still block all seven common snapshot hashes.

## Gate verdict

Gate A remains fail closed with zero accepted common snapshot hashes. This
repair authorizes no Lorentzian propagator, Hadamard state, renormalized
product, QME restoration or publishable quantum result.

## Reproduction

```bash
python3 quantum-weyl/classical_import/build_classical_import_gate_v5_reconciliation.py --check
python3 quantum-weyl/classical_import/check_classical_import_gate_v5_reconciliation.py
python3 quantum-weyl/classical_import/verify_classical_import_gate_v5_reconciliation.py
python3 -m unittest quantum-weyl/classical_import/tests/test_classical_import_gate_v5_reconciliation.py
```
"""


def generated() -> tuple[bytes, bytes]:
    value = build()
    return (dumps(value, indent=2, ensure_ascii=False) + "\n").encode(), report(value).encode()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    outputs = tuple(zip((RESULT, REPORT), generated()))
    stale = [str(path.relative_to(ROOT)) for path, content in outputs if not path.is_file() or path.read_bytes() != content]
    if args.check:
        print("CLASSICAL_IMPORT_GATE_V5_RECONCILIATION: " + ("generated artifacts current" if not stale else "stale: " + ", ".join(stale)))
        return bool(stale)
    for path, content in outputs:
        path.write_bytes(content)
    print("CLASSICAL_IMPORT_GATE_V5_RECONCILIATION: wrote certificate and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
