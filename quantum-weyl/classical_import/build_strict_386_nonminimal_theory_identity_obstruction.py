#!/usr/bin/env python3
"""Compare the exact q2 trivial stabilization with the first authoritative auxiliary cubic channel."""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
CLASSICAL = ROOT / "d_quotient_classical/certificates/CLASSICAL_ORDINARY_DERIVATIVE_AUXILIARY_CUBIC_EXPORT_V1.json"
Q2 = HERE / "certificates/STRICT_386_STABILIZED_Q2_LIFT_PREFLIGHT_V1.json"
PAIRING = HERE / "certificates/STRICT_386_COMPONENT_PAIRING_SERIALIZATION_V1.json"
RESULT = HERE / "certificates/STRICT_386_NONMINIMAL_THEORY_IDENTITY_OBSTRUCTION_V1.json"
REPORT = HERE / "REPORT_STRICT_386_NONMINIMAL_THEORY_IDENTITY_OBSTRUCTION_V1.md"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def build() -> dict[str, Any]:
    classical = json.loads(CLASSICAL.read_text())
    q2 = json.loads(Q2.read_text())
    pairing = json.loads(PAIRING.read_text())
    if classical.get("result_id") != "CLASSICAL_ORDINARY_DERIVATIVE_AUXILIARY_CUBIC_EXPORT_V1":
        raise ValueError("classical auxiliary cubic export drift")
    if q2.get("result_id") != "STRICT_386_STABILIZED_Q2_LIFT_PREFLIGHT_V1":
        raise ValueError("candidate q2 preflight drift")
    if pairing.get("result_id") != "STRICT_386_COMPONENT_PAIRING_SERIALIZATION_V1":
        raise ValueError("386-row pairing drift")
    rows = pairing.get("component_basis", {}).get("rows", [])
    blocks = {row.get("block") for row in rows}
    if not {"AUX_F_HAT", "AUX_F_HAT_STAR", "AUX_V", "AUX_V_STAR"} <= blocks:
        raise ValueError("auxiliary block names absent from common carrier")
    inert = q2.get("graph_transport_dag", {}).get("interaction_inert_blocks", [])
    if "AUX_F_HAT" not in inert or "AUX_V" not in inert:
        raise ValueError("candidate q2 no longer declares the witness blocks inert")
    source_value = Fraction(classical["auxiliary_cubic_interaction"]["witness"]["mixed_derivative_d_t_d_s_squared_at_zero"])
    candidate_value = Fraction(0)
    defect = source_value - candidate_value
    if defect != -1:
        raise AssertionError("theory-identity witness drift")

    comparison = {
        "common_coordinate_presentation": "linear generalized-auxiliary split before the curvature-graph shear",
        "cyclic_form_channel": "Omega(f_hat,q2(v,v))",
        "block_channel": ["AUX_F_HAT", "AUX_V", "AUX_V"],
        "source_ordinary_derivative_value": str(source_value),
        "candidate_trivial_stabilization_value": str(candidate_value),
        "source_minus_candidate_defect": str(defect),
        "source_nonzero_reason": "mixed third derivative of the authoritative ordinary-derivative action density",
        "candidate_zero_reason": "q2_split vanishes whenever a contractible input is present; AUX_F_HAT and AUX_V remain interaction-inert under the recorded linear shear",
        "literal_identity": False,
    }
    disposition = {
        "candidate_internal_q1_q2_and_cyclicity_certificates_preserved": True,
        "candidate_is_authoritative_ordinary_derivative_nonminimal_theory": False,
        "linear_canonical_shear_suffices_for_theory_identity": False,
        "nonlinear_canonical_or_L_infinity_equivalence_may_exist": True,
        "nonlinear_equivalence_constructed": False,
        "first_required_correction": "a quadratic auxiliary-elimination component whose pullback reproduces Omega(f_hat,q2(v,v))=-1",
        "gate_consequence": "The candidate q2/q3 hashes remain excluded from Gate A until a nonlinear source-to-candidate map or complete authoritative interaction ledger is imported.",
    }
    value = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "schema": "strict-386-nonminimal-theory-identity-obstruction-v1",
        "result_id": "STRICT_386_NONMINIMAL_THEORY_IDENTITY_OBSTRUCTION_V1",
        "result_kind": "EXACT_SOURCE_VERSUS_TRIVIAL_STABILIZATION_NONLINEAR_IDENTITY_OBSTRUCTION",
        "result_state": "LITERAL_AND_LINEAR_THEORY_IDENTITY_REFUTED_NONLINEAR_EQUIVALENCE_OPEN",
        "lifecycle": "CLASSIFIED",
        "created": "2026-08-15",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "scope": {
            "theory": "strict pure-Weyl ordinary-derivative auxiliary formulation versus the 386-row trivial-stabilization candidate",
            "background": "unit conformal cylinder normal frame",
            "carrier_rows": 386,
            "comparison_scope": "one exact cubic cyclic-form channel sufficient to refute literal equality",
            "coefficient_field": "Q",
        },
        "exact_channel_comparison": comparison,
        "theory_identity_disposition": disposition,
        "claim_flags": {
            "AUTHORITATIVE_SOURCE_AUXILIARY_CUBIC_IMPORTED": True,
            "CANDIDATE_Q2_ZERO_CHANNEL_REPLAYED": True,
            "LITERAL_TRIVIAL_STABILIZATION_THEORY_IDENTITY_REFUTED": True,
            "LINEAR_SHEAR_ONLY_THEORY_IDENTITY_REFUTED": True,
            "CANDIDATE_INTERNAL_IDENTITIES_INVALIDATED": False,
            "NONLINEAR_CYCLIC_L_INFINITY_EQUIVALENCE_CONSTRUCTED": False,
            "NONLINEAR_CYCLIC_L_INFINITY_EQUIVALENCE_OBSTRUCTED": False,
            "AUTHORITATIVE_FULL_386_Q2_IMPORTED": False,
            "AUTHORITATIVE_FULL_386_Q3_IMPORTED": False,
            "CANDIDATE_CAUSAL_LAMBDA2_SOURCE_CLOSURE_CERTIFIED": False,
            "CLASSICAL_IMPORT_GATE_PASSED": False,
            "HADAMARD_STATE_CONSTRUCTED": False,
            "QME_RESTORED": False,
        },
        "does_not_establish": [
            "that the candidate q1/q2/q3 algebra is internally inconsistent",
            "nonexistence of a nonlinear cyclic L-infinity equivalence",
            "the complete authoritative 386-row q2 or q3",
            "general lambda-squared source closure or q2/q3/Green compatibility",
            "Gate A, a Hadamard state, Lorentzian renormalized products, QME restoration, or residual transfer",
        ],
        "canonical_hashes": {
            "exact_channel_comparison_sha256": digest(comparison),
            "theory_identity_disposition_sha256": digest(disposition),
        },
        "provenance": {
            "inputs": [
                {"path": str(CLASSICAL.relative_to(ROOT)), "result_id": classical["result_id"], "sha256": sha(CLASSICAL), "role": "authoritative action-derived auxiliary cubic channel"},
                {"path": str(Q2.relative_to(ROOT)), "result_id": q2["result_id"], "sha256": sha(Q2), "role": "exact trivial-stabilization candidate and inert-block ledger"},
                {"path": str(PAIRING.relative_to(ROOT)), "result_id": pairing["result_id"], "sha256": sha(PAIRING), "role": "common 386-row block names and cyclic pairing carrier"},
            ]
        },
        "human_report": str(REPORT.relative_to(ROOT)),
        "next_gate": "Construct and certify the quadratic term of the nonlinear auxiliary-elimination/cyclic L-infinity map, beginning with the f_hat-v-v channel, then replay q2 and q3 source pullback identities before causal Green composition.",
    }
    return value


def render(value: dict[str, Any]) -> str:
    c = value["exact_channel_comparison"]
    return f"""# Strict 386-row nonminimal theory-identity obstruction v1

**Result:** `{value['result_id']}`

## Outcome

The exact source/candidate comparison is nonzero in the cyclic channel
`{c['cyclic_form_channel']}`:

- authoritative ordinary-derivative action: **{c['source_ordinary_derivative_value']}**;
- trivial-stabilization candidate: **{c['candidate_trivial_stabilization_value']}**;
- source minus candidate: **{c['source_minus_candidate_defect']}**.

The candidate is therefore not literally the authoritative nonminimal action,
and the recorded linear shear cannot make it so.  Its internal q1/q2/q3,
cyclicity and D-equivariance certificates remain valid.  The missing object is
now sharper: a nonlinear auxiliary-elimination or cyclic L-infinity map whose
first quadratic correction reproduces this channel.

## Reproduction

```text
python3 quantum-weyl/classical_import/build_strict_386_nonminimal_theory_identity_obstruction.py --check
python3 quantum-weyl/classical_import/check_strict_386_nonminimal_theory_identity_obstruction.py
python3 quantum-weyl/classical_import/verify_strict_386_nonminimal_theory_identity_obstruction.py
python3 -m unittest quantum-weyl.classical_import.tests.test_strict_386_nonminimal_theory_identity_obstruction
```

## Boundary

This is an obstruction to literal and linear theory identity, not an obstruction
to nonlinear equivalence and not a causal, Hadamard, or QME result.
"""


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
        print("STRICT_386_NONMINIMAL_THEORY_IDENTITY_OBSTRUCTION_V1: " + ("generated artifacts current" if not stale else "stale: " + ", ".join(stale)))
        return bool(stale)
    RESULT.write_bytes(result)
    REPORT.write_bytes(report)
    print("STRICT_386_NONMINIMAL_THEORY_IDENTITY_OBSTRUCTION_V1: wrote result and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
