#!/usr/bin/env python3
"""Import the first nonlinear auxiliary map and replay its decisive cubic cancellation."""

from __future__ import annotations
import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
CLASSICAL_MAP = ROOT / "d_quotient_classical/certificates/CLASSICAL_QUADRATIC_AUXILIARY_ELIMINATION_MAP_V1.json"
OBSTRUCTION = HERE / "certificates/STRICT_386_NONMINIMAL_THEORY_IDENTITY_OBSTRUCTION_V1.json"
Q2 = HERE / "certificates/STRICT_386_STABILIZED_Q2_LIFT_PREFLIGHT_V1.json"
PAIRING = HERE / "certificates/STRICT_386_COMPONENT_PAIRING_SERIALIZATION_V1.json"
RESULT = HERE / "certificates/STRICT_386_QUADRATIC_AUXILIARY_ELIMINATION_CHANNEL_V1.json"
REPORT = HERE / "REPORT_STRICT_386_QUADRATIC_AUXILIARY_ELIMINATION_CHANNEL_V1.md"

def sha(path: Path) -> str: return hashlib.sha256(path.read_bytes()).hexdigest()
def digest(value: object) -> str: return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()

def build() -> dict[str, Any]:
    classical, obstruction, q2, pairing = (json.loads(path.read_text()) for path in (CLASSICAL_MAP, OBSTRUCTION, Q2, PAIRING))
    if classical.get("result_id") != "CLASSICAL_QUADRATIC_AUXILIARY_ELIMINATION_MAP_V1": raise ValueError("classical quadratic map drift")
    if obstruction.get("result_id") != "STRICT_386_NONMINIMAL_THEORY_IDENTITY_OBSTRUCTION_V1": raise ValueError("obstruction drift")
    if q2.get("result_id") != "STRICT_386_STABILIZED_Q2_LIFT_PREFLIGHT_V1": raise ValueError("candidate q2 drift")
    rows = pairing.get("component_basis", {}).get("rows", [])
    blocks = {row.get("block") for row in rows}
    if len(rows) != 386 or not {"AUX_F_HAT", "AUX_F_HAT_STAR", "AUX_V", "AUX_V_STAR"} <= blocks: raise ValueError("386-row auxiliary carrier drift")
    fixture = classical["quadratic_auxiliary_map"]["fixture"]
    source = Fraction(obstruction["exact_channel_comparison"]["source_ordinary_derivative_value"])
    candidate = Fraction(obstruction["exact_channel_comparison"]["candidate_trivial_stabilization_value"])
    correction = Fraction(fixture["inverse_shift_mass_cross_mixed_polarization"])
    transformed = source + correction
    residual = transformed - candidate
    if (source, candidate, correction, transformed, residual) != (-1, 0, 1, 0, 0): raise AssertionError("quadratic pullback cancellation drift")
    channel = {
        "carrier_rows": 386,
        "source_to_split_map": classical["quadratic_auxiliary_map"]["full_source_to_split_map"],
        "source_to_split_homogeneous_quadratic_component": classical["quadratic_auxiliary_map"]["source_to_split_homogeneous_quadratic_component"],
        "source_to_split_second_Frechet_component": classical["quadratic_auxiliary_map"]["source_to_split_second_Frechet_component"],
        "split_to_source_inverse_quadratic_component": classical["quadratic_auxiliary_map"]["split_to_source_homogeneous_quadratic_component"],
        "input_blocks": ["AUX_V", "AUX_V"],
        "output_block": "AUX_F_HAT",
        "cyclic_form_channel": "Omega(f_hat,q2(v,v))",
        "pre_correction_source_value": str(source),
        "candidate_value": str(candidate),
        "inverse_shift_mass_cross_correction": str(correction),
        "transformed_source_value": str(transformed),
        "transformed_source_minus_candidate_residual": str(residual),
        "exact_channel_cancellation": residual == 0,
        "support_local": classical["quadratic_auxiliary_map"]["finite_order_local"],
        "uses_green_operator": classical["quadratic_auxiliary_map"]["uses_green_operator"],
        "uses_choice_principle": classical["quadratic_auxiliary_map"]["uses_choice_principle"],
    }
    boundary = {
        "first_required_quadratic_component_imported": True,
        "one_previously_obstructing_channel_closed": True,
        "source_certified_local_BV_canonical_lift_available": classical["quadratic_auxiliary_map"]["local_BV_cotangent_lift_is_canonical"],
        "receiver_componentwise_386_cotangent_lift_serialized": False,
        "remaining_shifted_cubic_families": ["h-f_hat-f_hat from metric dependence of sqrt(-g), A_g and the fibre pairing", "ghost/antifield channels from the nonlinear BV cotangent lift"],
        "complete_source_q2_pullback_replayed": False,
        "complete_source_q3_pullback_replayed": False,
        "full_cyclic_L_infinity_equivalence_constructed": False,
        "nonlinear_equivalence_obstructed": False,
    }
    value = {
        "$schema": "https://json-schema.org/draft/2020-12/schema", "schema": "strict-386-quadratic-auxiliary-elimination-channel-v1",
        "result_id": "STRICT_386_QUADRATIC_AUXILIARY_ELIMINATION_CHANNEL_V1",
        "result_kind": "INDEPENDENT_QUADRATIC_NONLINEAR_MAP_CHANNEL_PULLBACK_REPLAY",
        "result_state": "FIRST_QUADRATIC_EQUIVALENCE_COMPONENT_IMPORTED_CHANNEL_CLOSED_FULL_SOURCE_PULLBACK_OPEN",
        "lifecycle": "CLASSIFIED", "created": "2026-08-15", "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "scope": {"theory": "strict pure-Weyl ordinary-derivative auxiliary formulation", "background": "normal frame at zero vector", "carrier_rows": 386, "coefficient_field": "Q", "claim_scope": "one quadratic field-map component and one induced cubic cyclic channel"},
        "channel_pullback_replay": channel, "equivalence_boundary": boundary,
        "claim_flags": {
            "AUTHORITATIVE_QUADRATIC_AUXILIARY_MAP_IMPORTED": True, "F_HAT_V_V_PULLBACK_CHANNEL_CLOSED": True,
            "FIRST_NONLINEAR_EQUIVALENCE_COMPONENT_CONSTRUCTED": True, "CANDIDATE_INTERNAL_IDENTITIES_PRESERVED": True,
            "FULL_386_COTANGENT_LIFT_SERIALIZED": False, "FULL_SOURCE_Q2_PULLBACK_REPLAYED": False,
            "FULL_SOURCE_Q3_PULLBACK_REPLAYED": False, "FULL_CYCLIC_L_INFINITY_EQUIVALENCE_CONSTRUCTED": False,
            "NONLINEAR_EQUIVALENCE_OBSTRUCTED": False, "CLASSICAL_IMPORT_GATE_PASSED": False,
            "CAUSAL_LAMBDA2_SOURCE_CLOSURE_CERTIFIED": False, "HADAMARD_STATE_CONSTRUCTED": False, "QME_RESTORED": False
        },
        "does_not_establish": ["complete equality of source and candidate q2/q3", "a componentwise 386-row BV cotangent lift", "removal of metric-dependent f_hat-square interactions", "general lambda-squared causal source closure", "Gate A, Hadamard data, renormalized Lorentzian products, QME restoration, or residual transfer"],
        "canonical_hashes": {"channel_pullback_replay_sha256": digest(channel), "equivalence_boundary_sha256": digest(boundary)},
        "provenance": {"inputs": [
            {"path": str(CLASSICAL_MAP.relative_to(ROOT)), "result_id": classical["result_id"], "sha256": sha(CLASSICAL_MAP), "role": "authoritative exact quadratic auxiliary map"},
            {"path": str(OBSTRUCTION.relative_to(ROOT)), "result_id": obstruction["result_id"], "sha256": sha(OBSTRUCTION), "role": "pre-correction source/candidate obstruction"},
            {"path": str(Q2.relative_to(ROOT)), "result_id": q2["result_id"], "sha256": sha(Q2), "role": "exact trivial-stabilization candidate"},
            {"path": str(PAIRING.relative_to(ROOT)), "result_id": pairing["result_id"], "sha256": sha(PAIRING), "role": "common 386-row block and pairing carrier"}
        ]},
        "human_report": str(REPORT.relative_to(ROOT)),
        "next_gate": "Enumerate and independently replay every cubic channel induced by the exact nonlinear shift and its BV cotangent lift, beginning with h-f_hat-f_hat, before promoting a complete q2 pullback or Gate-A hash."
    }
    return value

def render(value: dict[str, Any]) -> str:
    c = value["channel_pullback_replay"]
    return f"""# Strict 386-row quadratic auxiliary-elimination channel v1

**Result:** `{value['result_id']}`

The source-to-split map has quadratic vector component
`{c['source_to_split_homogeneous_quadratic_component']}`.  Expressing the
source action in split variables uses its inverse and contributes
**{c['inverse_shift_mass_cross_correction']}** to the previously obstructing
cyclic channel.  The exact ledger is

- source before correction: **{c['pre_correction_source_value']}**;
- inverse-shift mass cross term: **{c['inverse_shift_mass_cross_correction']}**;
- transformed source: **{c['transformed_source_value']}**;
- trivial-stabilization candidate: **{c['candidate_value']}**;
- residual: **{c['transformed_source_minus_candidate_residual']}**.

The first nonlinear correction is therefore constructed and closes this one
channel.  Full q2/q3 pullback, the componentwise BV cotangent lift, causal
source closure and Gate A remain open.

## Reproduction

```text
python3 quantum-weyl/classical_import/build_strict_386_quadratic_auxiliary_elimination_channel.py --check
python3 quantum-weyl/classical_import/check_strict_386_quadratic_auxiliary_elimination_channel.py
python3 quantum-weyl/classical_import/verify_strict_386_quadratic_auxiliary_elimination_channel.py
python3 -m unittest quantum-weyl.classical_import.tests.test_strict_386_quadratic_auxiliary_elimination_channel
```
"""

def generated() -> tuple[bytes, bytes]:
    value = build(); return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode(), render(value).encode()

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument("--check", action="store_true"); args = parser.parse_args()
    outputs = tuple(zip((RESULT, REPORT), generated())); stale = [str(path.relative_to(ROOT)) for path, content in outputs if not path.is_file() or path.read_bytes() != content]
    if args.check: print("STRICT_386_QUADRATIC_AUXILIARY_ELIMINATION_CHANNEL_V1: " + ("generated artifacts current" if not stale else "stale: " + ", ".join(stale))); return bool(stale)
    for path, content in outputs: path.write_bytes(content)
    print("STRICT_386_QUADRATIC_AUXILIARY_ELIMINATION_CHANNEL_V1: wrote result and report"); return 0

if __name__ == "__main__": raise SystemExit(main())
