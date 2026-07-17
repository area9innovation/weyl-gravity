#!/usr/bin/env python3
"""Identify the geometric generator represented by the frozen 54-row action.

The rotating clock background is fixed by ``K=D-omega R`` rather than by the
raw cylinder translation ``D``.  This exact two-component calculation audits
the co-rotating clock transformation and binds its conclusion to the frozen
54-row local-generator certificate.  It deliberately does not construct the
affine/curved Cartan homotopy for raw ``D``.
"""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
LOCAL_ACTION = ROOT / "d_quotient_classical/certificates/BERGER_54_ROW_LOCAL_D_ACTION.json"
CLOCK_SEED = ROOT / "d_quotient_classical/certificates/BERGER_CLOCK_REDUCED_CHARGE_SEED.json"
CERTIFICATE_PATH = ROOT / "d_quotient_classical/certificates/BERGER_GENERATOR_CONJUGATION_AUDIT.json"
REPORT_PATH = ROOT / "d_quotient_classical/reports/berger-generator-conjugation-audit.md"
SCHEMA_PATH = ROOT / "d_quotient_classical/schema/berger-generator-conjugation-audit-v1.schema.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _exact_conjugation() -> dict[str, object]:
    t = sp.symbols("t", real=True)
    omega, rho = sp.symbols("omega rho", nonzero=True, real=True)
    psi_1 = sp.Function("psi_1")(t)
    psi_2 = sp.Function("psi_2")(t)
    psi = sp.Matrix([psi_1, psi_2])
    rotation_generator = sp.Matrix([[0, -1], [1, 0]])
    rotating_frame = sp.Matrix(
        [
            [sp.cos(omega * t), -sp.sin(omega * t)],
            [sp.sin(omega * t), sp.cos(omega * t)],
        ]
    )
    identity = sp.eye(2)
    if sp.simplify(rotating_frame.T * rotating_frame - identity) != sp.zeros(2):
        raise AssertionError("clock rotation is not orthogonal")
    if sp.simplify(sp.diff(rotating_frame, t) - omega * rotation_generator * rotating_frame) != sp.zeros(2):
        raise AssertionError("clock rotation derivative has the wrong sign")

    background_dressed = sp.Matrix([rho, 0])
    background_raw = rotating_frame * background_dressed
    raw_D_background = sp.simplify(sp.diff(background_raw, t))
    raw_K_background = sp.simplify(
        raw_D_background - omega * rotation_generator * background_raw
    )
    if raw_D_background == sp.zeros(2, 1):
        raise AssertionError("raw D unexpectedly fixes the rotating clock")
    if raw_K_background != sp.zeros(2, 1):
        raise AssertionError("K does not fix the rotating clock")

    raw_field = rotating_frame * (background_dressed + psi)
    dressed_D = sp.simplify(rotating_frame.T * sp.diff(raw_field, t))
    dressed_K = sp.simplify(
        rotating_frame.T
        * (sp.diff(raw_field, t) - omega * rotation_generator * raw_field)
    )
    expected_D = sp.diff(psi, t) + omega * rotation_generator * (background_dressed + psi)
    expected_K = sp.diff(psi, t)
    if sp.simplify(dressed_D - expected_D) != sp.zeros(2, 1):
        raise AssertionError("raw D conjugation identity failed")
    if sp.simplify(dressed_K - expected_K) != sp.zeros(2, 1):
        raise AssertionError("K conjugation identity failed")

    return {
        "rotation_generator": [[0, -1], [1, 0]],
        "raw_background": ["rho*cos(omega*t)", "rho*sin(omega*t)"],
        "raw_D_background": ["-omega*rho*sin(omega*t)", "omega*rho*cos(omega*t)"],
        "raw_K_background": ["0", "0"],
        "dressed_D_action": "partial_t psi + omega R psi + omega R (rho,0)",
        "dressed_K_action": "partial_t psi",
        "raw_D_zero_arity": ["0", "omega*rho"],
        "raw_D_unary": "partial_t I_2 + omega R",
        "K_zero_arity": ["0", "0"],
        "K_unary": "partial_t I_2",
    }


def build() -> dict[str, object]:
    local_action = json.loads(LOCAL_ACTION.read_text())
    clock_seed = json.loads(CLOCK_SEED.read_text())
    conjugation = _exact_conjugation()
    if local_action["geometric_definition"]["dressed_frame_action"] != "D=e_0 on every dressed component coefficient":
        raise AssertionError("frozen dressed-frame rule drifted")
    if local_action["D_action"]["coordinate_rule"] != "D(row_A)=e_0 row_A for A=0,...,53":
        raise AssertionError("frozen 54-row coordinate rule drifted")
    if clock_seed["conventions"]["internal_rotation"] != "R(T_1,T_2)=(-T_2,T_1)":
        raise AssertionError("internal rotation convention drifted")
    if clock_seed["helical_presymplectic_audit"]["background_scalar_action"] != "L_D T=omega R T":
        raise AssertionError("background D action drifted")

    payload = {
        "schema": "pure-weyl-berger-generator-conjugation-audit-v1",
        "result_id": "BERGER_GENERATOR_CONJUGATION_AUDIT",
        "setting_id": "compact_positive_berger_clock_q_9_over_40",
        "claim_status": "CERTIFIED_GENERATOR_CORRECTION",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "source_manifest": {
            "local_54_row_action": {
                "path": str(LOCAL_ACTION.relative_to(ROOT)),
                "sha256": _sha256(LOCAL_ACTION),
            },
            "clock_charge_seed": {
                "path": str(CLOCK_SEED.relative_to(ROOT)),
                "sha256": _sha256(CLOCK_SEED),
            },
        },
        "conventions": {
            "D": "partial_t on the original fields",
            "R": "R(T_1,T_2)=(-T_2,T_1)",
            "K": "D-omega R",
            "clock_dressing": "T=exp(omega*t*R)((rho,0)+psi)",
        },
        "exact_conjugation": conjugation,
        "interpretation": {
            "frozen_e0_generator": "K=D-omega R",
            "raw_D_in_dressed_coordinates": "affine: zero-arity omega R(rho,0), unary e0+omega R",
            "legacy_artifact_name": "BERGER_54_ROW_LOCAL_D_ACTION",
            "legacy_D_label_is_geometrically_K": True,
        },
        "exact_checks": {
            "rotation_derivative_exact": True,
            "raw_D_does_not_fix_background": True,
            "K_fixes_background": True,
            "raw_D_has_nonzero_zero_arity_in_dressed_coordinates": True,
            "frozen_e0_action_equals_K_unary_action": True,
            "source_hashes_pinned": True,
        },
        "flags": {
            "EXPORTED_UNARY_GENERATOR_IS_K": True,
            "EXPORTED_UNARY_GENERATOR_IS_ORIGINAL_D": False,
            "AFFINE_D_ZERO_ARITY_NONZERO": True,
            "PAPER09_K_CARTAN_INTERPRETATION": True,
            "PAPER09_D_CARTAN_AS_PREVIOUSLY_WRITTEN": False,
            "AFFINE_D_CARTAN_CONSTRUCTED": False,
            "THEOREM_FROZEN": False,
        },
        "next_gate": "PAPER09_RESTATE_BV_CARTAN_FOR_K_OR_CONSTRUCT_AFFINE_D_CARTAN",
        "claim_boundary": (
            "The exact co-rotating conjugation proves that the frozen e_0 action on the 54-row dressed complex represents K=D-omega R. The original cylinder translation D is affine about the rotating background and has a nonzero zero-arity component. Existing unary-through-ternary Cartan certificates therefore prove a K-Cartan theorem, not an affine D-Cartan theorem. No affine D Cartan primitive or all-orders theorem is constructed here."
        ),
    }
    verify(payload)
    return payload


def verify(payload: dict[str, object]) -> None:
    if payload["schema"] != "pure-weyl-berger-generator-conjugation-audit-v1":
        raise AssertionError("schema drifted")
    _exact_conjugation()
    for item in payload["source_manifest"].values():
        path = ROOT / item["path"]
        if _sha256(path) != item["sha256"]:
            raise AssertionError(f"source hash drifted: {path}")
    if not all(payload["exact_checks"].values()):
        raise AssertionError("an exact conjugation check is false")
    flags = payload["flags"]
    for key in (
        "EXPORTED_UNARY_GENERATOR_IS_K",
        "AFFINE_D_ZERO_ARITY_NONZERO",
        "PAPER09_K_CARTAN_INTERPRETATION",
    ):
        if flags[key] is not True:
            raise AssertionError(f"required generator flag is false: {key}")
    for key in (
        "EXPORTED_UNARY_GENERATOR_IS_ORIGINAL_D",
        "PAPER09_D_CARTAN_AS_PREVIOUSLY_WRITTEN",
        "AFFINE_D_CARTAN_CONSTRUCTED",
        "THEOREM_FROZEN",
    ):
        if flags[key] is not False:
            raise AssertionError(f"forbidden generator promotion: {key}")


def report_text(payload: dict[str, object]) -> str:
    return f"""# Berger generator conjugation audit

With

```text
R(T1,T2)=(-T2,T1),
T=exp(omega t R)((rho,0)+psi),
K=D-omega R,
```

exact differentiation gives

```text
exp(-omega t R) D T = partial_t psi + omega R psi + omega R(rho,0),
exp(-omega t R) K T = partial_t psi.
```

Thus the frozen all-row rule `e_0 I_54` represents `K`, whose background is
fixed.  Raw cylinder translation `D` is affine in these coordinates and has
nonzero zero-arity component `(0,omega rho)`.

Result: `{payload['result_id']}`.  The prior unary-through-ternary certificates
remain exact after being interpreted as a `K`-Cartan theorem.  They do not
construct the affine `D`-Cartan homotopy.
"""


def _write(payload: dict[str, object]) -> None:
    CERTIFICATE_PATH.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    REPORT_PATH.write_text(report_text(payload))


def _check(payload: dict[str, object]) -> None:
    if json.loads(CERTIFICATE_PATH.read_text()) != payload:
        raise AssertionError("generator conjugation certificate drifted")
    if REPORT_PATH.read_text() != report_text(payload):
        raise AssertionError("generator conjugation report drifted")


def _guards(payload: dict[str, object]) -> None:
    mutations = (
        ("misidentify e0 as D", "EXPORTED_UNARY_GENERATOR_IS_ORIGINAL_D", True),
        ("erase affine term", "AFFINE_D_ZERO_ARITY_NONZERO", False),
        ("promote affine theorem", "AFFINE_D_CARTAN_CONSTRUCTED", True),
        ("freeze theorem", "THEOREM_FROZEN", True),
    )
    for name, key, value in mutations:
        changed = deepcopy(payload)
        changed["flags"][key] = value
        try:
            verify(changed)
        except AssertionError:
            continue
        raise AssertionError(f"mutation guard failed: {name}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()
    payload = build()
    if args.write:
        _write(payload)
    if args.check:
        _check(payload)
    if args.guards:
        _guards(payload)
    print("BERGER_GENERATOR_CONJUGATION_AUDIT: PASS")
    print("frozen e0 generator=K; raw D affine with nonzero arity zero")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
