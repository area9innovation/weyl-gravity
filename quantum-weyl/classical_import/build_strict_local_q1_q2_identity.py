#!/usr/bin/env python3
"""Build the exact strict pure-Weyl local arity-two identity certificate."""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

import cylinder_polarized_bach_evaluator as point
from local_q1_bach_flat import digest
from local_q1_q2_receiver import (
    channel_id,
    enumerate_channels,
    fixture_record,
    mutation_record,
)


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/STRICT_LOCAL_Q1_Q2_IDENTITY_V1.json"
REPORT = HERE / "REPORT_STRICT_LOCAL_Q1_Q2_IDENTITY_V1.md"
INPUTS = (
    (
        "quantum-weyl/classical_import/certificates/STRICT_PORTABLE_LOCAL_Q1_AST_V1.json",
        "STRICT_PORTABLE_LOCAL_Q1_AST_V1",
        "portable Bach-flat unary differential and square-zero theorem",
    ),
    (
        "quantum-weyl/classical_import/certificates/STRICT_SIX_ROW_SUSPENDED_Q2_AST_V1.json",
        "STRICT_SIX_ROW_SUSPENDED_Q2_AST_V1",
        "twenty-two ordered components of the complete six-row minimal q2 ledger",
    ),
    (
        "d_quotient_classical/certificates/CLASSICAL_MINIMAL_BV_ANTIFIELD_EXPORT_V2.json",
        "CLASSICAL_MINIMAL_BV_ANTIFIELD_EXPORT_V2",
        "authoritative strict minimal Q rows and nilpotent derived-atom calculus",
    ),
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(relative: str) -> dict[str, Any]:
    return json.loads((ROOT / relative).read_text())


def build() -> dict[str, Any]:
    q1, q2, exported = (load(path) for path, _, _ in INPUTS)
    for value, (_, result_id, _) in zip((q1, q2, exported), INPUTS):
        if value.get("result_id") != result_id:
            raise ValueError(f"dependency drift: {result_id}")
    if q1.get("claim_flags", {}).get("Q1_SQUARED_ZERO_CERTIFIED") is not True:
        raise ValueError("portable q1 is not square-zero certified")
    if q2.get("claim_flags", {}).get("Q2_KOSZUL_SYMMETRY_REPLAYED") is not True:
        raise ValueError("ordered q2 Koszul ledger unavailable")
    if q1.get("convention") != q2.get("convention"):
        raise ValueError("q1/q2 suspension convention mismatch")

    q1_components = q1["local_q1_ast"]["components"]
    ordered_q2 = q2["ordered_components"]
    primary = q2["primary_components"]
    parities = {item["symbol"]: item["Grassmann_parity"] for item in q2["generator_ledger"]}
    channels = enumerate_channels(q1_components, ordered_q2, parities)
    if len(channels) != 18 or sum(len(item["paths"]) for item in channels) != 51:
        raise ValueError("arity-two channel inventory drift")
    used_q1 = {path["q1_component_id"] for item in channels for path in item["paths"]}
    used_q2 = {path["q2_component_id"] for item in channels for path in item["paths"]}
    if used_q1 != {item["component_id"] for item in q1_components} or used_q2 != {item["component_id"] for item in ordered_q2}:
        raise ValueError("arity-two expansion does not touch every q1/q2 component")

    q1_by_id = {item["component_id"]: item for item in q1_components}
    q2_by_id = {item["component_id"]: item for item in ordered_q2}
    primary_by_id = {item["primary_id"]: item for item in primary}
    backgrounds = (
        ("conformal_cylinder", point.cylinder_background(5), 11, 23),
        ("minkowski", point.flat_background(5), 13, 29),
        ("flat_brinkmann", point.brinkmann_background(5), 17, 31),
    )
    fixtures = [
        fixture_record(
            channels,
            q1_by_id,
            q2_by_id,
            primary_by_id,
            name,
            background,
            left_seed=left_seed,
            right_seed=right_seed,
        )
        for name, background, left_seed, right_seed in backgrounds
    ]
    by_channel_id = {channel_id(item): item for item in channels}
    mutation_targets = (
        "q1q2__h__c__c",
        "q1q2__h_star__c__h",
        "q1q2__c_star__h__h",
        "q1q2__omega_star__h__h",
    )
    mutations = [
        mutation_record(
            by_channel_id[target],
            q1_by_id,
            q2_by_id,
            primary_by_id,
            point.cylinder_background(5),
            path_index=0,
            left_seed=37,
            right_seed=41,
        )
        for target in mutation_targets
    ]
    family_by_output = {
        "h": "DIFF_X_WEYL_GAUGE_ACTION_CLOSURE",
        "h_star": "BACH_EULER_DIFF_X_WEYL_EQUIVARIANCE",
        "c_star": "DIFFERENTIATED_DIFF_NOETHER_AND_COTANGENT_COVARIANCE",
        "omega_star": "DIFFERENTIATED_WEYL_NOETHER_AND_DENSITY_COVARIANCE",
    }
    families = []
    counts = Counter(item["output"] for item in channels)
    for output in ("h", "h_star", "c_star", "omega_star"):
        families.append(
            {
                "family_id": family_by_output[output],
                "output": output,
                "channel_count": counts[output],
                "channel_ids": [channel_id(item) for item in channels if item["output"] == output],
                "general_identity": {
                    "h": "closure of the semidirect Diff action on metrics and Weyl scalars",
                    "h_star": "second Frechet derivative of Diff/Weyl covariance of the natural Bach Euler density",
                    "c_star": "first and second Frechet derivatives of the Diff Noether identity, including cotangent transport",
                    "omega_star": "first and second Frechet derivatives of the Weyl trace identity, including density transport",
                }[output],
            }
        )
    proof_checks = [
        {"check_id": "q1_q2_channel_exhaustion", "status": "VERIFIED", "evidence": "18 typed channels and 51 composable paths use all five q1 and all twenty-two ordered q2 components"},
        {"check_id": "q1_q2_arity_two_nilpotency", "status": "VERIFIED", "evidence": "all four natural identity families vanish; three exact five-jet background fixtures replay every channel"},
        {"check_id": "receiver_mutation_sensitivity", "status": "VERIFIED", "evidence": "one sign flip in each of the four output families produces a nonzero exact defect"},
        {"check_id": "D_q1_commutator_zero", "status": "NOT_REPLAYED", "evidence": "the full local D action is not serialized"},
        {"check_id": "D_q2_derivation", "status": "NOT_REPLAYED", "evidence": "the full local D action is not serialized"},
        {"check_id": "BV_cyclicity_q2", "status": "NOT_REPLAYED", "evidence": "the common support-local BV pairing receiver is not serialized"},
    ]
    value: dict[str, Any] = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "schema": "strict-local-q1-q2-identity-v1",
        "result_id": "STRICT_LOCAL_Q1_Q2_IDENTITY_V1",
        "result_kind": "PORTABLE_SUPPORT_LOCAL_ARITY_TWO_MASTER_IDENTITY",
        "result_state": "Q1_Q2_ARITY_TWO_IDENTITY_CERTIFIED_D_AND_PAIRING_OPEN",
        "lifecycle": "CLASSIFIED",
        "created": "2026-08-15",
        "repository_base_commit": "b06af47e",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "convention": "suspended-graded-symmetric-factorial-v1",
        "scope": {
            "theory": "strict pure-Weyl minimal Diff x Weyl BV theory",
            "background_class": "smooth nondegenerate four-dimensional Bach-flat pseudo-Riemannian metrics",
            "carrier": "compactly supported smooth minimal BV sections with external graded-commutative coefficients",
            "identity": "[q1,q2](x,y)=q1(q2(x,y))+q2(q1(x),y)+(-1)^|x| q2(x,q1(y))=0",
            "locality": "SUPPORT_LOCAL_POLYDIFFERENTIAL",
            "coefficient_field": "Q for exact fixtures; tensor-natural real smooth operator semantics",
            "maximum_metric_fixture_jet_order": 5,
            "support_rule": "each composed output support lies in the intersection of the two input supports",
        },
        "channel_inventory": {
            "channel_count": 18,
            "composable_path_count": 51,
            "q1_component_count": 5,
            "ordered_q2_component_count": 22,
            "all_q1_components_used": True,
            "all_ordered_q2_components_used": True,
            "channels": channels,
        },
        "natural_identity_families": families,
        "proof_basis": {
            "status": "CERTIFIED",
            "argument": [
                "The imported strict minimal BV vector field is nilpotent on its exact derived-atom calculus.",
                "The portable q1 and q2 rows are respectively the first and second Taylor coefficients of those same natural Diff x Weyl, Bach Euler, and cotangent/Noether formulas at a Bach-flat base point.",
                "The arity-two coefficient of Q squared is therefore the four displayed differentiated natural identities; the typed receiver exhausts their 18 channels rather than sampling a subset.",
                "Exact five-jet evaluations are independent regression witnesses for the serialized signs, ordered-slot orientations, density terms, Hessian normalization, and Leibniz propagation; finite backgrounds are not used as the proof of generality.",
            ],
            "legacy_matrix_cartan_helper_used": False,
            "reason": "the local receiver must propagate coordinate derivatives and the Leibniz rule through natural operators",
        },
        "exact_receiver": {
            "engine": "quantum-weyl/classical_import/local_q1_q2_receiver.py",
            "fixture_records": fixtures,
            "mutation_records": mutations,
            "routine_independent_replay_background": "conformal_cylinder",
            "exhaustive_producer_background_count": 3,
        },
        "proof_checks": proof_checks,
        "canonical_hashes": {},
        "provenance": {
            "inputs": [
                {"path": path, "result_or_artifact_id": result_id, "sha256": sha(ROOT / path), "role": role}
                for path, result_id, role in INPUTS
            ],
            "implementation": [
                {"path": "quantum-weyl/classical_import/local_q1_q2_receiver.py", "sha256": sha(HERE / "local_q1_q2_receiver.py"), "role": "independent exact local arity-two receiver"}
            ],
        },
        "claim_flags": {
            "Q1_Q2_CHANNEL_INVENTORY_EXHAUSTIVE": True,
            "Q1_Q2_ARITY_TWO_NILPOTENCY_REPLAYED": True,
            "Q1_Q2_RECEIVER_MUTATION_SENSITIVE": True,
            "STRICT_FULL_LOCAL_D_ACTION_CERTIFIED": False,
            "D_Q1_COMMUTATOR_REPLAYED": False,
            "D_Q2_DERIVATION_REPLAYED": False,
            "BV_CYCLICITY_Q2_REPLAYED": False,
            "STRICT_SUPPORT_LOCAL_Q2_COMPLETE": False,
            "CLASSICAL_IMPORT_GATE_PASSED": False,
            "LORENTZIAN_CAUSAL_CERTIFIED": False,
            "QME_RESTORED": False,
        },
        "does_not_establish": [
            "a complete local D action, D/q1 commutation, or D/q2 derivation identity",
            "BV cyclicity for q1 or q2 on a common support-local pairing",
            "the complete seven-proof SUPPORT_LOCAL_Q2_EXPORT_CONTRACT",
            "a passed classical import Gate A",
            "a gauge-fixed normally or strongly hyperbolic Lorentzian BV operator",
            "a causal Green homotopy, Hadamard state, renormalized products, restored QME, positivity, or Lorentzian quantum theory",
        ],
        "schema_path": "quantum-weyl/classical_import/schema/strict-local-q1-q2-identity-v1.schema.json",
        "independent_checker": "quantum-weyl/classical_import/check_strict_local_q1_q2_identity.py",
        "human_report": "quantum-weyl/classical_import/REPORT_STRICT_LOCAL_Q1_Q2_IDENTITY_V1.md",
    }
    value["canonical_hashes"] = {
        "channel_inventory_sha256": digest(value["channel_inventory"]),
        "natural_identity_families_sha256": digest(families),
        "proof_basis_sha256": digest(value["proof_basis"]),
        "exact_receiver_sha256": digest(value["exact_receiver"]),
        "proof_checks_sha256": digest(proof_checks),
    }
    return value


def render(value: Mapping[str, Any]) -> str:
    families = "\n".join(
        f"| `{item['family_id']}` | `{item['output']}` | {item['channel_count']} | {item['general_identity']} |"
        for item in value["natural_identity_families"]
    )
    fixtures = "\n".join(
        f"| `{item['background']}` | {item['channel_count']} | {item['path_count']} | `{item['all_channels_zero']}` |"
        for item in value["exact_receiver"]["fixture_records"]
    )
    checks = "\n".join(
        f"| `{item['check_id']}` | `{item['status']}` | {item['evidence']} |"
        for item in value["proof_checks"]
    )
    return f"""# Strict local q1/q2 arity-two identity v1

**Result:** `{value['result_id']}`

**State:** `{value['result_state']}`

**Dependency:** `LOCAL-ALGEBRAIC`

## Outcome

The first nonlinear master identity for the strict minimal pure-Weyl BV
complex is now certified in the common portable suspension convention:

```text
[q1,q2](x,y)
  = q1(q2(x,y)) + q2(q1(x),y) + (-1)^|x| q2(x,q1(y))
  = 0.
```

The typed expansion contains **18 channels** and **51 composable paths**. It
uses all five nonzero `q1` components and all twenty-two ordered `q2`
components. No uncomposed row is hidden outside the verdict.

## Four identity families

| Family | Output | Channels | General identity |
|---|---|---:|---|
{families}

The general theorem comes from differentiating the natural Diff/Weyl action,
the Bach Euler covariance laws, and the two Noether identities at a Bach-flat
base point. The exact coordinate fixtures below are regression witnesses for
the serialized operator bytes and signs; three examples are not treated as a
proof by induction or extrapolation.

## Exact local receiver

| Bach-flat background | Channels | Paths | All defects zero |
|---|---:|---:|---|
{fixtures}

Each run uses rational normalized metric five-jets and independently generated
field, ghost, and antifield jets. One sign is then flipped in a representative
channel from each output family; all four mutations produce nonzero exact
defects. The receiver does not use the legacy finite-dimensional Cartan matrix
helper because this calculation must propagate coordinate jets and Leibniz
rules through the natural differential operators.

## Gate ledger

| Check | Status | Evidence or remaining input |
|---|---|---|
{checks}

This closes `q1q2=0`, but it does not complete the downstream export contract.
The next algebraic goal is a common support-local BV pairing and full local
`D` action, followed by `[D,q1]=0`, the `D` derivation identity for `q2`, and
BV cyclicity. Gate A remains fail closed until those independent bytes and
receivers exist.

## Reproduction

```text
PYTHONPATH=quantum-weyl/classical_import python3 quantum-weyl/classical_import/build_strict_local_q1_q2_identity.py --check
PYTHONPATH=quantum-weyl/classical_import python3 quantum-weyl/classical_import/check_strict_local_q1_q2_identity.py
PYTHONPATH=quantum-weyl/classical_import python3 quantum-weyl/classical_import/verify_strict_local_q1_q2_identity.py
python3 -m unittest quantum-weyl/classical_import/tests/test_strict_local_q1_q2_identity.py -v
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
        print("STRICT_LOCAL_Q1_Q2_IDENTITY_V1: " + ("generated artifacts current" if not stale else "stale: " + ", ".join(stale)))
        return bool(stale)
    for path, content in outputs:
        path.write_bytes(content)
    print("STRICT_LOCAL_Q1_Q2_IDENTITY_V1: wrote certificate and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
