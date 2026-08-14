#!/usr/bin/env python3
"""Build the Gate-A successor after the strict D-finite residual SDR export."""
from __future__ import annotations

import argparse
from copy import deepcopy
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
V2 = ROOT / "quantum-weyl/classical_import/certificates/CLASSICAL_IMPORT_GATE_V2_RECONCILIATION.json"
SDR = ROOT / "quantum-weyl/classical_import/certificates/STRICT_DFINITE_RESIDUAL_SDR_V1.json"
RESULT = ROOT / "quantum-weyl/classical_import/certificates/CLASSICAL_IMPORT_GATE_V3_RECONCILIATION.json"
REPORT = ROOT / "quantum-weyl/classical_import/REPORT_GATE_V3.md"


def file_hash(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def digest(value: dict[str, Any]) -> str:
    payload = {
        key: value[key]
        for key in (
            "standalone_history_replay", "status_vocabulary", "export_reconciliation",
            "freeze_check_reconciliation", "required_hash_disposition",
            "minimal_missing_bundle", "gate_disposition", "m3_scoped_resolution",
        )
    }
    return sha256(dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def build() -> dict[str, Any]:
    previous = loads(V2.read_text())
    sdr = loads(SDR.read_text())
    if previous.get("result_id") != "CLASSICAL_IMPORT_GATE_V2_RECONCILIATION" or previous.get("gate_disposition", {}).get("gate_a_status") != "FAIL_CLOSED":
        raise ValueError("V2 predecessor drift")
    if sdr.get("result_id") != "STRICT_DFINITE_RESIDUAL_SDR_V1" or sdr.get("gate_a_effect", {}).get("gate_a_status") != "FAIL_CLOSED":
        raise ValueError("scoped SDR boundary drift")
    value = deepcopy(previous)
    value.update({
        "schema": "quantum-weyl-classical-import-gate-v3-reconciliation-v1",
        "result_id": "CLASSICAL_IMPORT_GATE_V3_RECONCILIATION",
        "result_state": "DFINITE_RESIDUAL_SDR_PORTABLE_COMMON_SUPPORT_LOCAL_FREEZE_OPEN",
        "created": "2026-08-15",
        "repository_base_commit": "1ffc17e215f5a5e55ce7c095bccd25210af0698c",
        "question": "After exporting and independently replaying the strict pure-Weyl D-finite residual SDR maps, which historical Gate-A obligations are now certified in scope, which carrier-extension gap remains, and does the common full classical freeze pass?",
        "answer": "The historical map-serialization absence is now closed in one exact same-theory scope: energies 2 through 6 of the BGG-adapted D x SO(4)-finite strict pure-Weyl split carrier. A standard-library receiver reconstructs and checks 4,490 full coordinates, 470 residual coordinates, q0, q_res^(0), iota_cl, pi_cl and s_cl, including all four historical SDR identities and normalized side conditions. Therefore the three map exports and four checks are promoted from missing or blocked to RECEIVER_VERIFIED_SCOPED. Gate A nevertheless remains fail-closed. The certified carrier is finite harmonic, uses the scalar test nonminimal doublet, and is not the one common full support-local carrier containing the complete Diff x Weyl nonminimal field domain, arbitrary-support local rows, full cyclic pairing, strict q2, D, residual SO(4,2) payload and centered representatives. No top-level Gate-A hash is accepted. M3 is narrowed from an unspecified missing serialization to the explicit task of extending or reconstructing the maps on that common carrier; it is not deleted or called globally complete.",
        "supersedes_for_current_status": "CLASSICAL_IMPORT_GATE_V2_RECONCILIATION",
        "human_report": "quantum-weyl/classical_import/REPORT_GATE_V3.md",
    })
    export_updates = {
        "classical_inclusion_iota_cl": (
            "The exact inclusion is serialized from 470 ordered W+/W- residual coordinates into 4,490 ordered full coordinates over energies two through six.",
            "Construct the inclusion on the one common full support-local strict carrier, including every required nonminimal and local row.",
            "A D-finite split inclusion is not an arbitrary-support field-theory inclusion and is not noncompact-equivariant as a chosen representative map.",
        ),
        "classical_projection_pi_cl": (
            "The exact homological projection is serialized from the same 4,490-coordinate finite carrier onto the ordered 470-coordinate residual carrier.",
            "Construct pi_cl on the one common full support-local strict carrier and bind it to the common pairing and residual payload.",
            "The certified finite projection cannot be promoted to a continuum or distributional projection.",
        ),
        "classical_homotopy_s_cl": (
            "The exact normalized contracting homotopy is serialized on all five finite split blocks and independently replayed.",
            "Construct s_cl on the one common full support-local strict carrier with the complete nonminimal field domain and shared conventions.",
            "This finite algebraic s_cl is neither an advanced/retarded Green homotopy nor the still-missing support-local full-carrier contraction.",
        ),
    }
    for row in value["export_reconciliation"]:
        if row["export_id"] in export_updates:
            established, remaining, boundary = export_updates[row["export_id"]]
            row.update({"status": "RECEIVER_VERIFIED_SCOPED", "evidence": ["STRICT_DFINITE_RESIDUAL_SDR_V1"], "established": established, "remaining_for_gate_a": remaining, "boundary": boundary})
    check_updates = {
        "pi_cl_iota_cl_identity": (
            "The receiver proves pi_cl iota_cl=1 on all 470 residual coordinates in the five-block D-finite direct sum.",
            "Replay the same identity on maps belonging to the common full support-local snapshot.",
            "Exact finite-block identity does not imply a common support-local carrier exists.",
        ),
        "classical_contraction_identity": (
            "The receiver proves iota_cl pi_cl=1-q0 s_cl-s_cl q0 on all 4,490 finite full coordinates.",
            "Replay the contraction identity on q0 and SDR maps from the common full support-local snapshot.",
            "The finite split contraction omits the complete nonminimal field domain and cannot be relabelled as a causal Green homotopy.",
        ),
        "q0_iota_intertwining": (
            "The receiver proves q0 iota_cl=iota_cl q_res^(0), with q_res^(0)=0, on every declared energy block.",
            "Replay the inclusion chain map on the common full support-local q0 and complete residual differential.",
            "A zero finite positive-energy residual differential is not the complete residual CE/BFV action.",
        ),
        "pi_q0_intertwining": (
            "The receiver proves pi_cl q0=q_res^(0) pi_cl on every declared energy block.",
            "Replay the projection chain map on the common full support-local q0 and complete residual differential.",
            "The finite split projection does not serialize the full SO(4,2) residual action or centered complex.",
        ),
    }
    for row in value["freeze_check_reconciliation"]:
        if row["check_id"] in check_updates:
            established, remaining, boundary = check_updates[row["check_id"]]
            row.update({"status": "RECEIVER_VERIFIED_SCOPED", "evidence": ["STRICT_DFINITE_RESIDUAL_SDR_V1"], "established": established, "remaining_for_gate_a": remaining, "boundary": boundary})
    for item in value["minimal_missing_bundle"]:
        if item["id"] == "M3_RESIDUAL_SDR":
            item["object"] = "Extend or reconstruct the certified D-finite iota_cl, pi_cl and s_cl on the one common full support-local strict pure-Weyl carrier, including complete nonminimal rows and shared pairing conventions; the finite payload remains the exact receiver control."
            item["unlocks"] = ["common-snapshot residual intertwiners", "full-carrier contraction identity", "M4 cyclic side conditions"]
    value["gate_disposition"].update({
        "claim_state": "CLASSICAL_IMPORT_DFINITE_SDR_REPAIRED_FULL_CARRIER_OPEN",
        "same_theory_receiver_verified_scoped": 8,
        "supporting_evidence_only": 7,
        "missing_portable_objects": 0,
        "freeze_checks_receiver_verified_scoped": 5,
        "freeze_checks_blocked": 1,
    })
    value["m3_scoped_resolution"] = {
        "status": "SCOPED_PORTABILITY_AND_IDENTITIES_CERTIFIED",
        "evidence": "STRICT_DFINITE_RESIDUAL_SDR_V1",
        "full_coordinates": sdr["global_direct_sum"]["full_dimension"],
        "residual_coordinates": sdr["global_direct_sum"]["residual_dimension"],
        "energies": sdr["scope"]["energies"],
        "residual_sdr_hash": sdr["global_direct_sum"]["residual_sdr_hash"],
        "remaining": sdr["gate_a_effect"]["remaining_m3_gap"],
        "boundary": "This resolves the missing portable object in a finite split scope, not the common full support-local M3 gate.",
    }
    value["provenance"]["inputs"] = [
        *previous["provenance"]["inputs"],
        {"path": str(V2.relative_to(ROOT)), "result_or_artifact_id": previous["result_id"], "sha256": file_hash(V2), "role": "immutable Gate-A V2 predecessor"},
        {"path": str(SDR.relative_to(ROOT)), "result_or_artifact_id": sdr["result_id"], "sha256": file_hash(SDR), "role": "same-theory scoped portable residual SDR and independent identity replay"},
    ]
    value["claim_flags"]["STRICT_DFINITE_M3_SCOPED_REPLAY"] = True
    value["does_not_establish"] = [
        *previous["does_not_establish"],
        "that the D-finite split residual SDR is the common full support-local Gate-A residual contraction",
        "that finite exact arithmetic proves the all-energy direct sum or continuum carrier",
    ]
    value["next_gate"] = "Use STRICT_DFINITE_RESIDUAL_SDR_V1 as the exact receiver control while constructing the one common support-local strict pure-Weyl carrier. For M3, extend or reconstruct iota_cl, pi_cl and s_cl with the complete Diff x Weyl nonminimal rows and M4 pairing conventions, then replay the same eight identities. In parallel, the first irreducible coefficient task remains M2: derive the arbitrary-support strict q2 and local D action from the target action on that same carrier. Do not import Berger coefficients, auxiliary projections or causal Green homotopies as substitutes."
    value["independent_checker"] = {
        "path": "quantum-weyl/classical_import/check_classical_import_gate_v3_reconciliation.py",
        "checks": [
            "V2 predecessor content pin", "D-finite SDR content pin", "twenty-export order",
            "ten-check order", "three-map scoped promotion only", "four-identity scoped promotion only",
            "zero accepted common hashes", "Gate-A fail-closed flags", "M3 carrier-extension boundary",
        ],
        "expected_digest": digest(value),
    }
    return value


def report(value: dict[str, Any]) -> str:
    exports = {row["export_id"]: row for row in value["export_reconciliation"]}
    checks = {row["check_id"]: row for row in value["freeze_check_reconciliation"]}
    map_rows = "\n".join(
        f"| `{name}` | `{exports[name]['status']}` | {exports[name]['remaining_for_gate_a']} |"
        for name in ("classical_inclusion_iota_cl", "classical_projection_pi_cl", "classical_homotopy_s_cl")
    )
    check_rows = "\n".join(
        f"| `{name}` | `{checks[name]['status']}` | {checks[name]['boundary']} |"
        for name in ("pi_cl_iota_cl_identity", "classical_contraction_identity", "q0_iota_intertwining", "pi_q0_intertwining")
    )
    return f"""# Classical import Gate-A reconciliation v3

**Result:** `{value['result_id']}`

**Lifecycle:** `{value['lifecycle']}`

**Gate A:** `{value['gate_disposition']['gate_a_status']}`

## Outcome

The historical residual-map portability gap is closed in one exact scope:
the strict pure-Weyl BGG-adapted `D`-finite blocks at energies two through six.
The receiver replays **{value['m3_scoped_resolution']['full_coordinates']} full**
and **{value['m3_scoped_resolution']['residual_coordinates']} residual**
coordinates.  Gate A remains fail-closed because these are not the maps on one
common full support-local carrier.

## Three map exports

| Export | Current status | Still required for Gate A |
|---|---|---|
{map_rows}

## Four freeze identities

| Check | Current status | Boundary |
|---|---|---|
{check_rows}

## M3 is narrowed, not deleted

The exact finite payload is now the receiver control.  The remaining M3 task is
to extend or reconstruct the maps with the complete nonminimal field domain and
shared cyclic conventions on the same support-local carrier required by M1,
M2 and M4.  A finite-mode direct sum does not prove that continuum object.

## Gate verdict

No accepted common snapshot hash exists.  Strict `q2`, `D`, the full cyclic
pairing, the complete residual SO(4,2) payload and centered representatives
remain outside one common snapshot.  No Hadamard, QME or residual-transfer
claim is promoted.

## Exact commands

```bash
python3 quantum-weyl/classical_import/build_classical_import_gate_v3_reconciliation.py --check
python3 quantum-weyl/classical_import/check_classical_import_gate_v3_reconciliation.py
python3 quantum-weyl/classical_import/verify_classical_import_gate_v3_reconciliation.py
python3 -m unittest quantum-weyl/classical_import/tests/test_classical_import_gate_v3_reconciliation.py
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
    result_bytes, report_bytes = generated()
    outputs = ((RESULT, result_bytes), (REPORT, report_bytes))
    stale = [str(path.relative_to(ROOT)) for path, content in outputs if not path.is_file() or path.read_bytes() != content]
    if args.check:
        if stale:
            print("CLASSICAL_IMPORT_GATE_V3_RECONCILIATION: stale: " + ", ".join(stale))
            return 1
        print("CLASSICAL_IMPORT_GATE_V3_RECONCILIATION: generated artifacts current")
        return 0
    for path, content in outputs:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
    print("CLASSICAL_IMPORT_GATE_V3_RECONCILIATION: wrote certificate and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
