#!/usr/bin/env python3
"""Build Gate-A v21 after the represented D-finite M3R comparison."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
V20 = HERE / "certificates/CLASSICAL_IMPORT_GATE_V20_RECONCILIATION.json"
M3R = HERE / "certificates/STRICT_ENDPOINT_TO_RESIDUAL_SPECTRAL_COMPARISON_V1.json"
RESULT = HERE / "certificates/CLASSICAL_IMPORT_GATE_V21_RECONCILIATION.json"
REPORT = HERE / "REPORT_GATE_V21.md"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: dict[str, Any]) -> str:
    keys = (
        "export_reconciliation", "freeze_check_reconciliation", "required_hash_disposition",
        "minimal_missing_bundle", "gate_disposition", "m3_scoped_resolution",
        "m3_type_and_locality_resolution", "m3l_common_endpoint_sdr_binding_resolution",
        "m3r_typed_residual_comparison_resolution", "m4_typed_local_cyclicity_resolution",
        "m5_residual_exact_payload_resolution", "m6_centered_representatives_resolution",
        "transitive_provenance_drift",
    )
    return hashlib.sha256(json.dumps(
        {key: value[key] for key in keys},
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode()).hexdigest()


def one(items: list[dict[str, Any]], key: str, wanted: str) -> dict[str, Any]:
    matches = [item for item in items if item.get(key) == wanted]
    if len(matches) != 1:
        raise ValueError(f"expected one {key}={wanted}, got {len(matches)}")
    return matches[0]


def build() -> dict[str, Any]:
    previous = json.loads(V20.read_text(encoding="utf-8"))
    comparison = json.loads(M3R.read_text(encoding="utf-8"))
    if previous.get("result_id") != "CLASSICAL_IMPORT_GATE_V20_RECONCILIATION":
        raise ValueError("Gate V20 predecessor drift")
    if previous["gate_disposition"]["gate_a_status"] != "FAIL_CLOSED":
        raise ValueError("Gate V20 was not fail closed")
    if comparison.get("result_id") != "STRICT_ENDPOINT_TO_RESIDUAL_SPECTRAL_COMPARISON_V1":
        raise ValueError("M3R identity drift")
    flags = comparison["claim_flags"]
    if flags["M3R_TYPED_RESIDUAL_COMPARISON_CONSTRUCTED"] is not True:
        raise ValueError("M3R is not constructed")
    if flags["HARMONIC_ANALYSIS_SUPPORT_LOCAL"] is not False:
        raise ValueError("M3R locality firewall drift")
    if flags["M4R_TYPED_RESIDUAL_CYCLICITY_COMPLETE"] is not False:
        raise ValueError("M4R firewall drift")

    value = deepcopy(previous)
    value.update({
        "schema": "quantum-weyl-classical-import-gate-v21-reconciliation-v1",
        "result_id": "CLASSICAL_IMPORT_GATE_V21_RECONCILIATION",
        "result_state": "M3R_REPRESENTED_DFINITE_COMPLETE_M1_M4R_OPEN_GATE_FAIL_CLOSED",
        "created": "2026-08-16",
        "repository_base_commit": "a9e72163907537e6dd2b9f36ec36fed64b3c617c",
        "question": "Does the represented finite endpoint-to-W+/W- comparison close M3R, and what remains before Gate A can freeze?",
        "answer": "Yes, exactly in the declared REDUCED-MODE category. All 470 energies-two-through-six residual coordinates now have explicit chirality, E/A/L and magnetic labels, a bijective crosswalk to the portable residual SDR, normalized represented metric preimages, pi iota=1 and both q0 chain identities. M3R is therefore complete on the represented D-finite global domain. The harmonic restriction is not support-local, raw all-magnetic coordinate matrices and smooth completion are not claimed, and no Gate-A hash is accepted by this scoped comparison. Gate A remains fail closed with M4R residual cyclicity and M1 common freeze open.",
        "supersedes_for_current_status": previous["result_id"],
        "human_report": "quantum-weyl/classical_import/REPORT_GATE_V21.md",
    })
    value["minimal_missing_bundle"] = [
        item for item in previous["minimal_missing_bundle"]
        if item["id"] != "M3R_TYPED_RESIDUAL_COMPARISON"
    ]

    for export_id in ("classical_inclusion_iota_cl", "classical_projection_pi_cl"):
        item = one(value["export_reconciliation"], "export_id", export_id)
        item["evidence"] = list(dict.fromkeys([*item["evidence"], comparison["result_id"]]))
        item["established"] += " M3R now binds that finite split map to an explicit 470-name endpoint-harmonic comparison."
        item["remaining_for_gate_a"] = "Bind the represented D-finite comparison and its M4R pairing into the one M1 common freeze manifest; no arbitrary-support promotion is required or allowed."
        item["boundary"] = "The M3R comparison is global and D-finite. It is not a support-local map on compactly supported sections and does not certify smooth completion."

    for check_id in ("q0_iota_intertwining", "pi_q0_intertwining"):
        item = one(value["freeze_check_reconciliation"], "check_id", check_id)
        item["evidence"] = list(dict.fromkeys([*item["evidence"], comparison["result_id"]]))
        item["established"] += " The identities now replay against the explicit represented M3R name crosswalk."
        item["remaining_for_gate_a"] = "Pin the exact comparison bytes under M1 and replay the final common-manifest hash closure."
        item["boundary"] = "This is a finite REDUCED-MODE chain comparison, not a local-support or all-energy intertwiner."

    cyclic_check = one(value["freeze_check_reconciliation"], "check_id", "cyclic_compatibility")
    cyclic_check.update({
        "status": "BLOCKED_MISSING_TYPED_RESIDUAL_CYCLICITY",
        "evidence": list(dict.fromkeys([*cyclic_check["evidence"], comparison["result_id"]])),
        "established": "M4L closes every local pairing identity and M3R now fixes the exact 470-mode residual comparison and normalization names.",
        "remaining_for_gate_a": "Derive the induced W+/W- pairing and replay M4R adjointness and cyclic side conditions on the fixed M3R ordering.",
        "boundary": "M3R supplies comparison maps but does not by itself prove that a chosen residual pairing is nondegenerate or cyclic.",
    })

    value["m3r_typed_residual_comparison_resolution"] = {
        "status": "M3R_RECEIVER_VERIFIED_SCOPED_COMPLETE_M4R_OPEN",
        "evidence": comparison["result_id"],
        "certificate_sha256": sha(M3R),
        "source_category": comparison["scope"]["source_category"],
        "target_category": comparison["scope"]["target_category"],
        "energy_blocks": comparison["exact_replay"]["energy_blocks"],
        "residual_coordinates": comparison["exact_replay"]["represented_residual_coordinates"],
        "ordered_crosswalk_defects": comparison["exact_replay"]["ordered_crosswalk_defects"],
        "chain_identity_defects": sum(
            comparison["exact_replay"][key]
            for key in (
                "dfinite_pi_iota_identity_defects",
                "dfinite_q0_iota_chain_defects",
                "dfinite_pi_q0_chain_defects",
            )
        ),
        "harmonic_analysis_support_local": False,
        "all_energy_or_smooth_completion_certified": False,
        "M3R_TYPED_RESIDUAL_COMPARISON": "COMPLETE_IN_REPRESENTED_DFINITE_ENERGIES_2_THROUGH_6",
        "M4R_TYPED_RESIDUAL_CYCLICITY": "OPEN",
        "accepted_common_snapshot_hashes_added": 0,
    }
    value["m4_typed_local_cyclicity_resolution"]["M4R_TYPED_RESIDUAL_CYCLICITY"] = "OPEN_READY_AFTER_M3R"
    value["gate_disposition"].update({
        "claim_state": "CLASSICAL_IMPORT_M3L_M3R_M4L_COMPLETE_M1_M4R_OPEN",
        "accepted_common_snapshot_hashes": 1,
        "gate_a_status": "FAIL_CLOSED",
        "publishable_quantum_results_allowed_by_gate_a": False,
    })
    value["provenance"]["inputs"] = [
        *previous["provenance"]["inputs"],
        {
            "path": str(V20.relative_to(ROOT)),
            "result_or_artifact_id": previous["result_id"],
            "sha256": sha(V20),
            "role": "immutable Gate-A V20 predecessor",
        },
        {
            "path": str(M3R.relative_to(ROOT)),
            "result_or_artifact_id": comparison["result_id"],
            "sha256": sha(M3R),
            "role": "receiver-verified represented D-finite endpoint-to-residual comparison",
        },
    ]
    value["claim_flags"].update({
        "M3R_TYPED_RESIDUAL_COMPARISON_CONSTRUCTED": True,
        "M3R_ORDERED_470_MODE_CROSSWALK_BIJECTIVE": True,
        "M3R_CHAIN_IDENTITIES_REPLAYED": True,
        "HARMONIC_ANALYSIS_SUPPORT_LOCAL": False,
        "ALL_ENERGY_OR_SMOOTH_COMPLETION_CERTIFIED": False,
        "M4R_TYPED_RESIDUAL_CYCLICITY_COMPLETE": False,
        "FULL_RESIDUAL_CYCLIC_PAIRING_CERTIFIED": False,
        "COMMON_GATE_A_FREEZE_BOUND": False,
        "CLASSICAL_IMPORT_GATE_PASSED": False,
        "PUBLISHABLE_QUANTUM_RESULTS_ALLOWED_BY_GATE_A": False,
        "HADAMARD_STATE_CONSTRUCTED": False,
        "QME_RESTORED": False,
        "RESIDUAL_QUANTUM_TRANSFER_AUTHORIZED": False,
    })
    value["does_not_establish"] = list(dict.fromkeys([
        *previous["does_not_establish"],
        "support-locality of the represented harmonic restriction or a comparison on arbitrary smooth sections and distributions",
        "raw unsplit coordinate matrices for all 470 magnetic modes or an all-energy completion",
        "M4R residual cyclicity, a new accepted Gate-A hash, or the M1 common freeze",
    ]))
    value["next_gate"] = "Derive the residual W+/W- pairing on the fixed M3R basis, replay M4R cyclic side conditions, and then bind M1 and replay the final all-object freeze before any Hadamard or QME promotion."
    value["independent_checker"] = {
        "path": "quantum-weyl/classical_import/check_classical_import_gate_v21_reconciliation.py",
        "checks": [
            "V20 predecessor and M3R content pins",
            "independent M3R receiver replay",
            "unchanged twenty exports, ten checks and one accepted hash",
            "M3R removal from the missing bundle with M1/M4R retained",
            "470-mode crosswalk and zero chain-defect projection",
            "global reduced-mode/support-locality and smooth-completion firewalls",
            "Gate-A/Hadamard/QME/residual-transfer firewalls",
            "canonical reconciliation digest",
        ],
        "expected_digest": "",
    }
    value["independent_checker"]["expected_digest"] = digest(value)
    return value


def render(value: dict[str, Any]) -> str:
    resolution = value["m3r_typed_residual_comparison_resolution"]
    return f"""# Classical import Gate-A reconciliation v21

**Result:** `{value['result_id']}`
**Dependencies:** `LOCAL-ALGEBRAIC`, `REDUCED-MODE`, `LORENTZIAN-CAUSAL`
**Gate A:** `FAIL_CLOSED`

M3R is complete in the represented D-finite global category.  The receiver
reconstructs {resolution['residual_coordinates']} ordered W+/W- mode names at
energies two through six, checks a bijective E/A/L magnetic crosswalk, and
replays the retraction and both q0 chain identities with zero defects.

This does not make harmonic analysis support-local and does not supply raw
all-magnetic coordinate matrices or an all-energy smooth completion.  No new
top-level hash is accepted.  Gate A remains fail closed with M4R residual
cyclicity and M1 common freeze open.

## Reproduction

```text
python3 quantum-weyl/classical_import/build_classical_import_gate_v21_reconciliation.py --check
python3 quantum-weyl/classical_import/check_classical_import_gate_v21_reconciliation.py
python3 -m unittest quantum-weyl/classical_import/tests/test_classical_import_gate_v21_reconciliation.py
```
"""


def generated() -> tuple[bytes, bytes]:
    value = build()
    return (
        (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode(),
        render(value).encode(),
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    outputs = tuple(zip((RESULT, REPORT), generated()))
    stale = [
        str(path.relative_to(ROOT))
        for path, content in outputs
        if not path.is_file() or path.read_bytes() != content
    ]
    if args.check:
        print("CLASSICAL_IMPORT_GATE_V21_RECONCILIATION: " + (
            "generated artifacts current" if not stale else "stale: " + ", ".join(stale)
        ))
        return bool(stale)
    for path, content in outputs:
        path.write_bytes(content)
    print("CLASSICAL_IMPORT_GATE_V21_RECONCILIATION: wrote certificate and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
