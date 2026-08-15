#!/usr/bin/env python3
"""Build the quartic cyclicity certificate for imported minimal-BV q3."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/STRICT_MINIMAL_BV_Q3_CYCLICITY_V1.json"
REPORT = HERE / "REPORT_STRICT_MINIMAL_BV_Q3_CYCLICITY_V1.md"
Q3_IMPORT = HERE / "certificates/STRICT_PURE_WEYL_MINIMAL_BV_Q3_IMPORT_V1.json"
ARITY3 = HERE / "certificates/STRICT_MINIMAL_BV_ARITY_THREE_IDENTITY_V1.json"
PAIRING = HERE / "certificates/STRICT_MINIMAL_BV_CYCLIC_SIGN_RECONCILIATION_V1.json"
CLASSICAL_Q3 = ROOT / "d_quotient_classical/certificates/CLASSICAL_MINIMAL_BV_Q3_EXPORT_V1.json"
ACTION = ROOT / "d_quotient_classical/minimal_bv_antifield/foundation/action_normalization.json"
INPUTS = (
    (Q3_IMPORT, "STRICT_PURE_WEYL_MINIMAL_BV_Q3_IMPORT_V1", "complete imported minimal q3"),
    (ARITY3, "STRICT_MINIMAL_BV_ARITY_THREE_IDENTITY_V1", "same-carrier arity-three identity"),
    (PAIRING, "STRICT_MINIMAL_BV_CYCLIC_SIGN_RECONCILIATION_V1", "canonical odd cotangent pairing and receiver sign translation"),
    (CLASSICAL_Q3, "CLASSICAL_MINIMAL_BV_Q3_EXPORT_V1", "authoritative q3 support and action-derived AST"),
    (ACTION, "PURE_WEYL_ACTION_NORMALIZATION_V2", "authoritative pure-Weyl action normalization"),
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def load(path: Path, expected: str) -> dict[str, Any]:
    value = json.loads(path.read_text())
    if value.get("result_id", value.get("schema")) != expected:
        raise ValueError(f"dependency identity drift: {expected}")
    return value


def build() -> dict[str, Any]:
    values = {path: load(path, expected) for path, expected, _ in INPUTS}
    q3, arity3, pairing, classical, action = (values[path] for path, _, _ in INPUTS)
    if q3.get("claim_flags", {}).get("AUTHORITATIVE_MINIMAL_BV_Q3_IMPORTED") is not True:
        raise ValueError("minimal q3 import unavailable")
    if arity3.get("claim_flags", {}).get("MINIMAL_BV_ARITY_THREE_IDENTITY_CERTIFIED") is not True:
        raise ValueError("minimal arity-three identity unavailable")
    if pairing.get("claim_flags", {}).get("CANONICAL_MINIMAL_BV_PAIRING_SERIALIZED") is not True:
        raise ValueError("canonical pairing unavailable")
    if action.get("Euler_coordinate") != classical.get("scope", {}).get("action_normalization"):
        raise ValueError("action/Euler normalization mismatch")

    canonical = pairing["canonical_pairing"]
    metric_entries = [
        item for item in canonical["entries"]
        if item["left"].startswith("h_") and item["right"].startswith("h_star_")
    ]
    if len(metric_entries) != 10 or [item["coefficient"] for item in metric_entries] != ["1", "2", "2", "2", "1", "2", "2", "1", "2", "1"]:
        raise ValueError("metric pairing weights drift")
    support = classical["minimal_q3_support"]
    if support.get("nonzero_row_count") != 1 or next(item for item in support["rows"] if item["output_generator"] == "g_star")["accepted_input_generators"] != ["g", "g", "g"]:
        raise ValueError("unique q3 cyclic sector drift")

    cyclic_form = {
        "form_id": "V4_PURE_WEYL_METRIC",
        "definition": "V4(h1,h2,h3,h4)=Omega(h4,q3(h1,h2,h3))",
        "component_formula": "integral sum_(mu<=nu) w_mu_nu h4_mu_nu D^3E_g(h1,h2,h3)^mu_nu",
        "metric_component_weights": [item["coefficient"] for item in metric_entries],
        "pairing_orientation": "field h on the left and antifield q3 output h_star on the right",
        "variational_identification": "V4=D^4 S_W(h1,h2,h3,h4) modulo a compact-support horizontal boundary term",
        "permutation_group": "S4",
        "Koszul_sign_for_all_metric_inputs": 1,
        "cyclicity_defect_mod_d": "0",
        "status": "CERTIFIED",
    }
    proof = {
        "proof_kind": "FOURTH_VARIATION_OF_LOCAL_ACTION_MODULO_HORIZONTAL_BOUNDARY",
        "argument": [
            "The imported q3 has exactly one nonzero component, q3(h1,h2,h3)=D^3E_g(h1,h2,h3) in the metric-antifield row.",
            "The canonical odd cotangent pairing in the action orientation contracts h4 with that metric-antifield density using weights one on diagonal and two on off-diagonal symmetric components.",
            "Because E_g is the Euler derivative delta S_W/delta g in the pinned normalization, the integrated contraction equals D^4S_W(h1,h2,h3,h4) modulo a horizontal boundary term.",
            "Mixed fourth variations of one local action commute; compact test support removes the integrated boundary term, so the four-linear vertex is S4-symmetric.",
            "Every metric input is even, hence each receiver cyclic Koszul sign is +1. The five zero q3 output rows create no additional quartic sectors.",
        ],
        "support_domain": canonical["support_domain"],
        "result_kind_boundary": "integrated local functionals modulo d; no pointwise equality of unintegrated density representatives is claimed",
        "status": "CERTIFIED",
    }
    convention_bridge = {
        "source_q3_convention": q3["scope"]["taylor_convention"],
        "pairing_sign_translation": pairing["sign_translation"]["formula"],
        "affected_q3_output_generator": "h_star",
        "translation_sign_on_h_star": pairing["sign_translation"]["generator_signs"]["h_star"],
        "translation_changes_q3": False,
        "reason": "the canonical sign translation is +1 on h and h_star; it changes only c_star and omega_star, whose q3 rows vanish",
    }

    value: dict[str, Any] = {
        "$schema": "../schema/strict-minimal-bv-q3-cyclicity-v1.schema.json",
        "schema": "strict-minimal-bv-q3-cyclicity-v1",
        "schema_path": "quantum-weyl/classical_import/schema/strict-minimal-bv-q3-cyclicity-v1.schema.json",
        "result_id": "STRICT_MINIMAL_BV_Q3_CYCLICITY_V1",
        "result_kind": "INTEGRATED_LOCAL_FUNCTIONAL_QUARTIC_BV_CYCLICITY",
        "result_state": "MINIMAL_Q3_ARITY_AND_CYCLICITY_CERTIFIED_386_CYCLIC_STABILIZATION_OPEN",
        "lifecycle": "CLASSIFIED",
        "created": "2026-08-15",
        "repository_base_commit": "0950df03e512b88436ab12212d0d9a9ac820c681",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "scope": {
            "theory": "strict pure-Weyl minimal BV theory",
            "result_kind": "integrated local functional modulo horizontal boundary terms",
            "carrier": "six-generator minimal BV carrier with the canonical odd cotangent pairing",
            "support": "one compactly supported argument; compact-compact-compact-compact is allowed",
            "coefficient_field": "Q for conventions; smooth real local action semantics",
        },
        "canonical_pairing_projection": {
            "parent_result_id": pairing["result_id"],
            "kind": canonical["kind"],
            "degree": canonical["degree"],
            "component_basis_dimension": canonical["component_basis_dimension"],
            "metric_entry_count": len(metric_entries),
            "off_diagonal_symmetric_tensor_weight": canonical["off_diagonal_symmetric_tensor_weight"],
            "metric_entries": metric_entries,
        },
        "cyclic_four_form": cyclic_form,
        "variational_proof": proof,
        "convention_bridge": convention_bridge,
        "gate_advancement": [
            {"gate": "MINIMAL_ARITY_THREE_Q_SQUARED", "status": "PASS"},
            {"gate": "MINIMAL_Q3_CYCLICITY", "status": "PASS"},
            {"gate": "STRICT_386_CYCLIC_STABILIZATION", "status": "OPEN"},
            {"gate": "STRICT_386_GENERAL_LAMBDA2_SOURCE_CLOSURE", "status": "OPEN"},
        ],
        "foundational_strength": {
            "classification": "FINITE_PAIRING_DATA_PLUS_LOCAL_VARIATIONAL_CALCULUS",
            "choice_operation_added": False,
            "Hilbert_completion_used": False,
            "Green_operator_used": False,
            "dependency_boundary": "LOCAL-ALGEBRAIC",
        },
        "claim_flags": {
            "MINIMAL_BV_ARITY_THREE_IDENTITY_CERTIFIED": True,
            "MINIMAL_BV_Q3_CYCLICITY_CERTIFIED": True,
            "QUARTIC_METRIC_VERTEX_S4_SYMMETRIC_MOD_D": True,
            "CANONICAL_PAIRING_SIGN_TRANSLATION_COMPATIBLE": True,
            "STRICT_386_Q3_STABILIZED": False,
            "STRICT_386_GENERAL_LAMBDA2_SOURCE_CLOSURE_CERTIFIED": False,
            "CLASSICAL_IMPORT_GATE_PASSED": False,
            "LORENTZIAN_CAUSAL_CERTIFIED": False,
            "HADAMARD_STATE_CONSTRUCTED": False,
            "QME_RESTORED": False,
        },
        "canonical_hashes": {},
        "provenance": {
            "inputs": [
                {"path": str(path.relative_to(ROOT)), "result_id": expected, "sha256": sha(path), "role": role}
                for path, expected, role in INPUTS
            ]
        },
        "does_not_establish": [
            "pointwise equality of cyclic density representatives before integration by parts",
            "a cyclic stabilization or L-infinity morphism to all 386 graph rows",
            "the 386-row arity-three identity or general lambda-squared source closure",
            "q3 compatibility with a causal Green homotopy or an analytic Moller map",
            "renormalized Lorentzian time-ordered products or a Hadamard state",
            "QME restoration, residual transfer, or a Lorentzian quantum theory",
        ],
        "next_gate": "Transport the accepted q1, q2, q3 and canonical pairing through one explicit linear BV-canonical stabilization to all 386 rows, then replay arity three and general lambda-squared source closure on the stabilized carrier.",
        "independent_checker": "quantum-weyl/classical_import/check_strict_minimal_bv_q3_cyclicity.py",
        "human_report": "quantum-weyl/classical_import/REPORT_STRICT_MINIMAL_BV_Q3_CYCLICITY_V1.md",
    }
    value["canonical_hashes"] = {
        "canonical_pairing_projection_sha256": digest(value["canonical_pairing_projection"]),
        "cyclic_four_form_sha256": digest(cyclic_form),
        "variational_proof_sha256": digest(proof),
        "convention_bridge_sha256": digest(convention_bridge),
        "gate_advancement_sha256": digest(value["gate_advancement"]),
        "foundational_strength_sha256": digest(value["foundational_strength"]),
    }
    return value


def render(value: Mapping[str, Any]) -> str:
    return f"""# Strict minimal-BV q3 cyclicity v1

**Result:** `{value['result_id']}`

**State:** `{value['result_state']}`
**Dependency:** `LOCAL-ALGEBRAIC`

## Outcome

The imported minimal q3 is cyclic under the repository's canonical odd BV
pairing.  Its only nonzero sector is

```text
V4(h1,h2,h3,h4) = Omega(h4, q3(h1,h2,h3))
                   = D^4 S_W(h1,h2,h3,h4) mod d.
```

The fourth variation of one local action is symmetric in all four metric
directions.  All metric directions are even, so the cyclic Koszul sign is
`+1`.  The receiver sign translation is also `+1` on `h` and `h_star`; its
minus signs occur only on the two ghost-antifield rows, whose q3 components
are identically zero.

This is an integrated-local-functional statement modulo horizontal boundary
terms.  It deliberately does not claim pointwise equality of unintegrated
density representatives.  Compact support is the boundary condition that
makes the integrated cyclic identity exact.

The minimal carrier now has both the complete arity-three identity and q3
cyclicity.  The next unresolved object is the explicit 386-row cyclic
stabilization; no full-carrier promotion is made here.

## Reproduction

```text
python3 quantum-weyl/classical_import/build_strict_minimal_bv_q3_cyclicity.py --check
python3 quantum-weyl/classical_import/check_strict_minimal_bv_q3_cyclicity.py
python3 quantum-weyl/classical_import/verify_strict_minimal_bv_q3_cyclicity.py
python3 -m unittest quantum-weyl/classical_import/tests/test_strict_minimal_bv_q3_cyclicity.py -v
```

## Does not establish

""" + "\n".join(f"- {item}." for item in value["does_not_establish"]) + "\n"


def generated() -> tuple[bytes, bytes]:
    value = build()
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode(), render(value).encode()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    outputs = tuple(zip((RESULT, REPORT), generated()))
    stale = [str(path.relative_to(ROOT)) for path, content in outputs if not path.is_file() or path.read_bytes() != content]
    if args.check:
        print("STRICT_MINIMAL_BV_Q3_CYCLICITY_V1: " + ("generated artifacts current" if not stale else "stale: " + ", ".join(stale)))
        return bool(stale)
    for path, content in outputs:
        path.write_bytes(content)
    print("STRICT_MINIMAL_BV_Q3_CYCLICITY_V1: wrote certificate and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
