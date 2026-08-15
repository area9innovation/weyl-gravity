#!/usr/bin/env python3
"""Build Gate-A v4 after the strict minimal local q1/q2 closure."""

from __future__ import annotations

import argparse
from copy import deepcopy
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
V3 = HERE / "certificates/CLASSICAL_IMPORT_GATE_V3_RECONCILIATION.json"
Q1 = HERE / "certificates/STRICT_PORTABLE_LOCAL_Q1_AST_V1.json"
Q2 = HERE / "certificates/STRICT_SIX_ROW_SUSPENDED_Q2_AST_V1.json"
IDENTITY = HERE / "certificates/STRICT_LOCAL_Q1_Q2_IDENTITY_V1.json"
RESULT = HERE / "certificates/CLASSICAL_IMPORT_GATE_V4_RECONCILIATION.json"
REPORT = HERE / "REPORT_GATE_V4.md"


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
        )
    }
    return sha256(
        dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()


def build() -> dict[str, Any]:
    previous, q1, q2, identity = (loads(path.read_text()) for path in (V3, Q1, Q2, IDENTITY))
    if previous.get("result_id") != "CLASSICAL_IMPORT_GATE_V3_RECONCILIATION" or previous.get("gate_disposition", {}).get("gate_a_status") != "FAIL_CLOSED":
        raise ValueError("V3 predecessor drift")
    if q1.get("claim_flags", {}).get("Q1_SQUARED_ZERO_CERTIFIED") is not True:
        raise ValueError("portable q1 input unavailable")
    if q2.get("claim_flags", {}).get("SIX_MINIMAL_Q2_ROW_LEDGERS_COMPLETE") is not True:
        raise ValueError("six-row q2 input unavailable")
    if identity.get("claim_flags", {}).get("Q1_Q2_ARITY_TWO_NILPOTENCY_REPLAYED") is not True:
        raise ValueError("strict arity-two identity unavailable")

    value = deepcopy(previous)
    value.update(
        {
            "schema": "quantum-weyl-classical-import-gate-v4-reconciliation-v1",
            "result_id": "CLASSICAL_IMPORT_GATE_V4_RECONCILIATION",
            "result_state": "MINIMAL_LOCAL_Q1_Q2_REPAIRED_D_PAIRING_FULL_CARRIER_OPEN",
            "created": "2026-08-15",
            "repository_base_commit": "909ce138347fc6d34aa2e00129be5d4124980f66",
            "question": "After certifying the portable Bach-flat strict minimal unary complex, all six minimal q2 rows, and the complete arity-two identity on those same bytes, which M2 obligations are now receiver-verified in scope, what remains for the common full carrier, and does Gate A pass?",
            "answer": "The strict minimal Diff x Weyl sector now has one portable local algebraic chain in a common suspension convention. Five nonzero q1 components are square-zero on the Bach-flat locus; twelve primary q2 kernels expand to twenty-two ordered components covering all six minimal outputs; and an independent jet-aware receiver exhausts eighteen q1q2 channels and fifty-one composable paths, using every q1 and q2 component. Three exact Bach-flat background fixtures vanish and four sign mutations expose nonzero defects. This promotes the support-local classical q2 export and q1q2 freeze check from different-theory controls to RECEIVER_VERIFIED_SCOPED. Gate A still fails closed. The payload is the strict minimal sector, not one complete full-carrier snapshot with all declared nonminimal/auxiliary rows, local D, common cyclic pairing, continuum residual SDR, SO(4,2) payload, and centered representatives. No required common snapshot hash is accepted. M2 is narrowed to the explicit D action and any full-carrier/nonminimal extension required by the receiver contract; M4 cyclicity remains independent. Nothing here establishes a Lorentzian Green homotopy or quantum lifecycle promotion.",
            "supersedes_for_current_status": "CLASSICAL_IMPORT_GATE_V3_RECONCILIATION",
            "human_report": "quantum-weyl/classical_import/REPORT_GATE_V4.md",
        }
    )
    q2_export = next(row for row in value["export_reconciliation"] if row["export_id"] == "support_local_classical_bv_q2")
    q2_export.update(
        {
            "status": "RECEIVER_VERIFIED_SCOPED",
            "evidence": ["STRICT_SIX_ROW_SUSPENDED_Q2_AST_V1", "STRICT_LOCAL_Q1_Q2_IDENTITY_V1"],
            "established": "All six strict minimal Diff x Weyl q2 output rows are portable support-local polydifferential operators in one suspension, with twenty-two ordered components and an independently replayed q1q2 identity.",
            "remaining_for_gate_a": "Extend or bind this minimal payload to the one common full carrier required by the export contract, including every retained nonminimal or auxiliary row, local D, pairing, residual maps and common hashes.",
            "boundary": "A complete minimal-sector q2 and arity-two identity do not supply local D, BV cyclicity, the nonminimal full carrier, residual contraction, or an accepted Gate-A snapshot hash.",
        }
    )
    q1q2_check = next(row for row in value["freeze_check_reconciliation"] if row["check_id"] == "q1_q2_arity_two_nilpotency")
    q1q2_check.update(
        {
            "status": "RECEIVER_VERIFIED_SCOPED",
            "evidence": ["STRICT_PORTABLE_LOCAL_Q1_AST_V1", "STRICT_LOCAL_Q1_Q2_IDENTITY_V1"],
            "established": "The local receiver reconstructs all eighteen typed minimal-sector channels and fifty-one paths and proves [q1,q2]=0 in four natural identity families on the Bach-flat strict carrier.",
            "remaining_for_gate_a": "Replay the identity on the eventual common full support-local snapshot if that snapshot adds nonminimal or auxiliary interaction rows beyond the certified strict minimal sector.",
            "boundary": "This exact local-algebraic arity-two theorem is not a D identity, cyclicity theorem, residual-transfer theorem, causal propagator, or quantum master equation.",
        }
    )
    for item in value["minimal_missing_bundle"]:
        if item["id"] == "M2_STRICT_Q2_D":
            item["object"] = "Bind the certified strict minimal q1/q2 payload to the common full support-local carrier, add every contract-required nonminimal or auxiliary interaction row, and serialize the complete local D action; then replay [D,q1]=0 and the D derivation identity."
            item["unlocks"] = ["full-carrier support-local q2 export", "D_q1_commutator_zero", "D_q2_derivation", "M4 cyclic comparison"]
    value["gate_disposition"].update(
        {
            "claim_state": "CLASSICAL_IMPORT_MINIMAL_Q1_Q2_REPAIRED_D_PAIRING_FULL_CARRIER_OPEN",
            "same_theory_receiver_verified_scoped": 9,
            "different_theory_controls": 1,
            "freeze_checks_receiver_verified_scoped": 6,
            "freeze_checks_different_theory": 3,
        }
    )
    value["m2_minimal_resolution"] = {
        "status": "STRICT_MINIMAL_Q1_Q2_AND_ARITY_TWO_IDENTITY_CERTIFIED",
        "evidence": [q1["result_id"], q2["result_id"], identity["result_id"]],
        "generator_count": len(q2["generator_ledger"]),
        "q1_component_count": len(q1["local_q1_ast"]["components"]),
        "q2_primary_component_count": len(q2["primary_components"]),
        "q2_ordered_component_count": len(q2["ordered_components"]),
        "q1q2_channel_count": identity["channel_inventory"]["channel_count"],
        "q1q2_path_count": identity["channel_inventory"]["composable_path_count"],
        "remaining": "The complete local D action, [D,q1], D derivation, common BV pairing/cyclicity, any full-carrier nonminimal extension, and accepted common snapshot hashes remain open.",
        "boundary": "This resolves the strict minimal local q1/q2 arity-two layer, not the complete M2/M4 full-carrier Gate-A bundle.",
    }
    value["provenance"]["inputs"] = [
        *previous["provenance"]["inputs"],
        {"path": str(V3.relative_to(ROOT)), "result_or_artifact_id": previous["result_id"], "sha256": file_hash(V3), "role": "immutable Gate-A V3 predecessor"},
        {"path": str(Q1.relative_to(ROOT)), "result_or_artifact_id": q1["result_id"], "sha256": file_hash(Q1), "role": "portable strict minimal q1 and q1-square theorem"},
        {"path": str(Q2.relative_to(ROOT)), "result_or_artifact_id": q2["result_id"], "sha256": file_hash(Q2), "role": "portable six-row ordered strict minimal q2 ledger"},
        {"path": str(IDENTITY.relative_to(ROOT)), "result_or_artifact_id": identity["result_id"], "sha256": file_hash(IDENTITY), "role": "independent strict minimal arity-two receiver theorem"},
    ]
    value["claim_flags"].update(
        {
            "STRICT_MINIMAL_LOCAL_Q1_Q2_SCOPED_REPLAY": True,
            "STRICT_MINIMAL_Q1_Q2_ARITY_TWO_IDENTITY": True,
        }
    )
    value["does_not_establish"] = [
        *previous["does_not_establish"],
        "that the strict minimal local q1/q2 carrier is already the complete common full support-local Gate-A carrier",
        "a local D action, D equivariance, BV cyclicity, causal Green homotopy, Hadamard state, or Lorentzian QME",
    ]
    value["next_gate"] = "Use STRICT_PORTABLE_LOCAL_Q1_AST_V1, STRICT_SIX_ROW_SUSPENDED_Q2_AST_V1 and STRICT_LOCAL_Q1_Q2_IDENTITY_V1 as the exact common minimal-sector control. Serialize the local D action on all six minimal generators and every contract-required nonminimal or auxiliary generator; independently replay [D,q1]=0 and the D derivation identity. In parallel serialize the common support-local BV pairing and replay q1/q2 cyclicity. Only then reconcile M2 with M4 and the full-carrier M1/M3/M5/M6 snapshot. Do not identify a minimal local algebra theorem with a causal Green homotopy or any quantum lifecycle state."
    value["independent_checker"] = {
        "path": "quantum-weyl/classical_import/check_classical_import_gate_v4_reconciliation.py",
        "checks": [
            "V3 predecessor content pin",
            "q1/q2/identity content pins",
            "twenty-export and ten-check order",
            "one minimal q2 scoped promotion only",
            "one q1q2 scoped promotion only",
            "eighteen-channel/fifty-one-path crosswalk",
            "D and pairing statuses unchanged",
            "zero accepted common hashes",
            "Gate-A fail-closed flags",
            "M2 minimal-versus-full-carrier boundary",
        ],
        "expected_digest": digest(value),
    }
    return value


def report(value: dict[str, Any]) -> str:
    resolution = value["m2_minimal_resolution"]
    q2_row = next(row for row in value["export_reconciliation"] if row["export_id"] == "support_local_classical_bv_q2")
    identity_row = next(row for row in value["freeze_check_reconciliation"] if row["check_id"] == "q1_q2_arity_two_nilpotency")
    return f"""# Classical import Gate-A reconciliation v4

**Result:** `{value['result_id']}`

**Lifecycle:** `{value['lifecycle']}`

**Gate A:** `{value['gate_disposition']['gate_a_status']}`

## Outcome

The strict minimal local algebraic layer is now one same-theory scoped result.
It contains **{resolution['q1_component_count']} q1 components**,
**{resolution['q2_ordered_component_count']} ordered q2 components**, and an
independent arity-two replay over **{resolution['q1q2_channel_count']} channels
and {resolution['q1q2_path_count']} paths**. Gate A remains fail closed.

## Scoped promotions

| Obligation | Status | Established | Still required |
|---|---|---|---|
| `support_local_classical_bv_q2` | `{q2_row['status']}` | {q2_row['established']} | {q2_row['remaining_for_gate_a']} |
| `q1_q2_arity_two_nilpotency` | `{identity_row['status']}` | {identity_row['established']} | {identity_row['remaining_for_gate_a']} |

No other export or freeze row changes status. In particular, local `D`, its
two identities, and BV cyclicity remain different-theory controls or blocked
until strict common-carrier bytes exist.

## M2 is narrowed, not closed

The minimal q1/q2 interaction layer is complete and mutation-sensitive. The
remaining M2 work is the local `D` action, `[D,q1]=0`, the `D` derivation
identity, and any nonminimal/full-carrier rows required by the export contract.
M4 must independently supply the common BV pairing and cyclicity. The finite
M3 residual contraction, residual SO(4,2) data and centered representatives
still have their own carrier and hash gates.

## Gate verdict

All seven required common snapshot hashes remain unaccepted. This v4
reconciliation therefore authorizes no publishable quantum result, residual
quantum transfer, Lorentzian propagator, Hadamard state, or QME promotion.

## Exact commands

```bash
python3 quantum-weyl/classical_import/build_classical_import_gate_v4_reconciliation.py --check
python3 quantum-weyl/classical_import/check_classical_import_gate_v4_reconciliation.py
python3 quantum-weyl/classical_import/verify_classical_import_gate_v4_reconciliation.py
python3 -m unittest quantum-weyl/classical_import/tests/test_classical_import_gate_v4_reconciliation.py
```

## What this does not establish

""" + "\n".join(f"- {item}." for item in value["does_not_establish"][-7:]) + "\n"


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
        print("CLASSICAL_IMPORT_GATE_V4_RECONCILIATION: " + ("generated artifacts current" if not stale else "stale: " + ", ".join(stale)))
        return bool(stale)
    for path, content in outputs:
        path.write_bytes(content)
    print("CLASSICAL_IMPORT_GATE_V4_RECONCILIATION: wrote certificate and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
