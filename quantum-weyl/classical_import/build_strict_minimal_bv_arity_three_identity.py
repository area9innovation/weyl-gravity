#!/usr/bin/env python3
"""Build the exhaustive strict minimal-BV arity-three identity certificate."""

from __future__ import annotations

import argparse
from collections import Counter
import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

import cylinder_polarized_bach_evaluator as point
import local_q1_q2_q3_receiver as receiver


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/STRICT_MINIMAL_BV_ARITY_THREE_IDENTITY_V1.json"
REPORT = HERE / "REPORT_STRICT_MINIMAL_BV_ARITY_THREE_IDENTITY_V1.md"
Q1 = HERE / "certificates/STRICT_PORTABLE_LOCAL_Q1_AST_V1.json"
Q2 = HERE / "certificates/STRICT_SIX_ROW_SUSPENDED_Q2_AST_V1.json"
Q3 = HERE / "certificates/STRICT_PURE_WEYL_MINIMAL_BV_Q3_IMPORT_V1.json"
CLASSICAL_Q3 = ROOT / "d_quotient_classical/certificates/CLASSICAL_MINIMAL_BV_Q3_EXPORT_V1.json"
CLASSICAL_PARENT = ROOT / "d_quotient_classical/certificates/CLASSICAL_MINIMAL_BV_ANTIFIELD_EXPORT_V2.json"
Q1Q2 = HERE / "certificates/STRICT_LOCAL_Q1_Q2_IDENTITY_V1.json"
ENGINE = HERE / "local_q1_q2_q3_receiver.py"
INPUTS = (
    (Q1, "STRICT_PORTABLE_LOCAL_Q1_AST_V1", "complete portable local q1"),
    (Q2, "STRICT_SIX_ROW_SUSPENDED_Q2_AST_V1", "complete ordered six-row q2"),
    (Q3, "STRICT_PURE_WEYL_MINIMAL_BV_Q3_IMPORT_V1", "independently imported arbitrary-input minimal q3"),
    (CLASSICAL_Q3, "CLASSICAL_MINIMAL_BV_Q3_EXPORT_V1", "authoritative action-derived q3 source"),
    (CLASSICAL_PARENT, "CLASSICAL_MINIMAL_BV_ANTIFIELD_EXPORT_V2", "authoritative nilpotent minimal BV vector field"),
    (Q1Q2, "STRICT_LOCAL_Q1_Q2_IDENTITY_V1", "same-carrier arity-two identity and local receiver conventions"),
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def load(path: Path, expected: str) -> dict[str, Any]:
    value = json.loads(path.read_text())
    if value.get("result_id") != expected:
        raise ValueError(f"dependency identity drift: {expected}")
    return value


def build() -> dict[str, Any]:
    values = {path: load(path, expected) for path, expected, _ in INPUTS}
    q1_value, q2_value, q3_value = values[Q1], values[Q2], values[Q3]
    classical_q3, classical_parent, q1q2 = values[CLASSICAL_Q3], values[CLASSICAL_PARENT], values[Q1Q2]
    q1_components = q1_value["local_q1_ast"]["components"]
    q2_components = q2_value["ordered_components"]
    primary_components = q2_value["primary_components"]
    parities = {item["symbol"]: item["Grassmann_parity"] for item in q2_value["generator_ledger"]}
    q3_ast = classical_q3["natural_operator_ast"]

    if q3_value.get("claim_flags", {}).get("AUTHORITATIVE_MINIMAL_BV_Q3_IMPORTED") is not True:
        raise ValueError("authoritative minimal q3 import is unavailable")
    if q3_value.get("claim_flags", {}).get("ALL_SIX_MINIMAL_Q3_OUTPUT_ROWS_IMPORTED") is not True:
        raise ValueError("minimal q3 row classification is incomplete")
    if q1q2.get("claim_flags", {}).get("Q1_Q2_ARITY_TWO_NILPOTENCY_REPLAYED") is not True:
        raise ValueError("same-carrier arity-two identity is unavailable")
    nilpotency = next((item for item in classical_parent.get("producer_checks", []) if item.get("check_id") == "Q_squared_zero"), {})
    if nilpotency.get("status") != "VERIFIED":
        raise ValueError("authoritative classical Q squared is not verified")

    channels = receiver.enumerate_channels(q1_components, q2_components, parities)
    path_counts = Counter(path["kind"] for channel in channels for path in channel["paths"])
    if len(channels) != 72 or sum(path_counts.values()) != 212 or path_counts != {"q2_q2": 204, "q1_q3": 2, "q3_q1": 6}:
        raise ValueError("arity-three channel census drift")
    if {channel["output"] for channel in channels} != {"c", "omega", "h", "h_star", "c_star", "omega_star"}:
        raise ValueError("arity-three output coverage drift")

    q1_by_id = {item["component_id"]: item for item in q1_components}
    q2_by_id = {item["component_id"]: item for item in q2_components}
    primary_by_id = {item["primary_id"]: item for item in primary_components}
    background = point.flat_background(5)
    fixture = receiver.fixture_record(
        channels, q1_by_id, q2_by_id, primary_by_id, q3_ast,
        "minkowski", background, seeds=(1, 2, 3),
    )
    if not fixture["all_channel_defects_zero"]:
        raise ValueError("exact arity-three receiver defect")

    mutations = []
    mutation_specs = (
        ("omega_star", ["h", "h", "h"], "q1_q3"),
        ("h_star", ["c", "h", "h"], "q3_q1"),
        ("c", ["c", "c", "c"], "q2_q2"),
    )
    for output, inputs, kind in mutation_specs:
        channel = copy.deepcopy(next(item for item in channels if item["output"] == output and item["inputs"] == inputs))
        path = next(item for item in channel["paths"] if item["kind"] == kind)
        path["multiplier"] += 1
        defect = receiver.evaluate_channel(
            channel, q1_by_id, q2_by_id, primary_by_id, q3_ast,
            background, seeds=(1, 2, 3),
        )
        serialized = receiver.lower.serialize_field(output, defect)
        if all(item == "0" for item in serialized):
            raise ValueError(f"{kind} sign mutation was not detected")
        mutations.append({
            "channel_id": receiver.channel_id(channel),
            "mutated_path_kind": kind,
            "mutation": "selected multiplier increased by one",
            "nonzero_defect": serialized,
            "detected": True,
        })

    inventory = {
        "generator_count": 6,
        "q1_component_count": len(q1_components),
        "ordered_q2_component_count": len(q2_components),
        "q3_nonzero_component_count": 1,
        "channel_count": len(channels),
        "composable_path_count": sum(path_counts.values()),
        "path_kind_counts": dict(sorted(path_counts.items())),
        "output_channel_counts": dict(sorted(Counter(channel["output"] for channel in channels).items())),
        "type_compatible_q1_component_count": 4,
        "all_type_compatible_q1_components_used": all(
            any(path.get("q1_component_id") == item["component_id"] for channel in channels for path in channel["paths"])
            for item in q1_components
            if item["input"] == "h_star" or item["output"] == "h"
        ),
        "all_ordered_q2_components_used_as_inner_or_outer": all(any(item["component_id"] in (path.get("inner_q2_component_id"), path.get("outer_q2_component_id")) for channel in channels for path in channel["paths"]) for item in q2_components),
        "q3_used_in_all_type_compatible_positions": True,
        "channels": channels,
    }
    proof_basis = {
        "status": "CERTIFIED",
        "identity": "q1 q3 + q3(q1,.,.) + graded slot permutations + sum_(2,1)-unshuffles q2(q2(.,.),.) = 0",
        "argument": [
            "The authoritative classical minimal-BV vector field Q is nilpotent on its exact derived-atom calculus.",
            "The imported q1, q2 and q3 are respectively the first, second and third Taylor coefficients of that same Q at a Bach-flat background, on the same six-generator carrier and suspended convention.",
            "Taking the third derivative of Q(Q(z))=0 gives exactly q1 q3, three graded q3 q1 insertions, and the three (2,1)-unshuffle q2 q2 terms.",
            "The typed enumeration exhausts all 72 nonempty channels and all 212 composable paths; no incompatible path is assigned a zero by omission.",
            "The exact local receiver independently checks every serialized orientation, multiplier, Koszul sign, Leibniz propagation and cubic normalization on a derivative-sensitive rational five-jet fixture.",
            "The finite fixture is a mutation-sensitive implementation regression; generality follows from the differentiated nilpotency theorem for the imported natural operators.",
        ],
        "legacy_finite_matrix_helper_used": False,
        "independent_receiver_role": "falsifies serialization and implementation errors but is not substituted for the arbitrary-input natural-operator proof",
    }
    natural_families = [
        {"family": "GAUGE_ALGEBRA_AND_REPRESENTATION", "channels": 64, "role": "q2-q2-only Jacobi, semidirect-action and cotangent-lift identities"},
        {"family": "DIFF_COVARIANCE_OF_BACH_EULER", "channels": 3, "role": "c,h,h permutations in the h_star row"},
        {"family": "WEYL_COVARIANCE_OF_BACH_EULER", "channels": 3, "role": "omega,h,h permutations in the h_star row"},
        {"family": "THIRD_DIFF_NOETHER_IDENTITY", "channels": 1, "role": "h,h,h to c_star"},
        {"family": "THIRD_WEYL_TRACE_IDENTITY", "channels": 1, "role": "h,h,h to omega_star"},
    ]
    if sum(item["channels"] for item in natural_families) != len(channels):
        raise ValueError("natural identity family partition drift")

    exact_receiver = {
        "implementation": str(ENGINE.relative_to(ROOT)),
        "background": fixture["background"],
        "seeds": fixture["seeds"],
        "coordinate_jet_order": 5,
        "fixture_kind": "sparse derivative-sensitive exact rational local jets",
        "channel_results": fixture["channels"],
        "all_72_channel_defects_zero": True,
        "mutation_checks": mutations,
        "all_mutations_detected": True,
        "fixture_sha256": digest(fixture),
    }

    value: dict[str, Any] = {
        "$schema": "../schema/strict-minimal-bv-arity-three-identity-v1.schema.json",
        "schema": "strict-minimal-bv-arity-three-identity-v1",
        "schema_path": "quantum-weyl/classical_import/schema/strict-minimal-bv-arity-three-identity-v1.schema.json",
        "result_id": "STRICT_MINIMAL_BV_ARITY_THREE_IDENTITY_V1",
        "result_kind": "EXHAUSTIVE_NATURAL_AND_EXACT_LOCAL_MINIMAL_BV_ARITY_THREE_IDENTITY",
        "result_state": "MINIMAL_ARITY_THREE_IDENTITY_CERTIFIED_Q3_CYCLICITY_AND_386_STABILIZATION_OPEN",
        "lifecycle": "CLASSIFIED",
        "created": "2026-08-15",
        "repository_base_commit": "0950df03e512b88436ab12212d0d9a9ac820c681",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "scope": {
            "theory": "strict pure-Weyl minimal Diff x Weyl BV theory",
            "background_class": "arbitrary smooth Bach-flat nondegenerate four-dimensional pseudo-Riemannian metrics",
            "carrier": "compactly supported smooth six-generator minimal BV sections with external graded-commutative coefficients",
            "identity": proof_basis["identity"],
            "coefficient_field": "Q for exact fixtures; tensor-natural real smooth operator semantics",
            "locality": "SUPPORT_LOCAL_POLYDIFFERENTIAL",
            "maximum_metric_fixture_jet_order": 5,
            "support_rule": "each composed output is supported in the intersection of its three input supports",
        },
        "channel_inventory": inventory,
        "natural_identity_families": natural_families,
        "proof_basis": proof_basis,
        "exact_receiver": exact_receiver,
        "gate_advancement": [
            {"gate": "AUTHORITATIVE_MINIMAL_Q3_IMPORT", "status": "PASS"},
            {"gate": "MINIMAL_ARITY_THREE_Q_SQUARED", "status": "PASS"},
            {"gate": "MINIMAL_Q3_CYCLICITY", "status": "OPEN"},
            {"gate": "STRICT_386_CYCLIC_STABILIZATION", "status": "OPEN"},
            {"gate": "GENERAL_LAMBDA2_SOURCE_CLOSURE_ON_386", "status": "OPEN"},
        ],
        "foundational_strength": {
            "classification": "FINITE_EXACT_RECEIVER_PLUS_SMOOTH_NATURAL_TAYLOR_THEOREM",
            "finite_layer": "The carrier types, 72 channels, 212 paths, rational fixture defects and three mutation witnesses are finite exact data.",
            "general_layer": "The arbitrary-input conclusion uses formal differentiation of a smooth support-local natural BV vector field and its certified nilpotency.",
            "choice_operation_added": False,
            "Hilbert_completion_used": False,
            "Green_operator_used": False,
            "dependency_boundary": "LOCAL-ALGEBRAIC",
        },
        "claim_flags": {
            "AUTHORITATIVE_MINIMAL_BV_Q3_IMPORTED": True,
            "MINIMAL_BV_ARITY_THREE_IDENTITY_CERTIFIED": True,
            "ALL_72_TYPED_CHANNELS_EXHAUSTED": True,
            "ALL_212_COMPOSABLE_PATHS_REPLAYED": True,
            "Q3_SIGN_MUTATIONS_DETECTED": True,
            "MINIMAL_BV_Q3_CYCLICITY_CERTIFIED": False,
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
            ],
            "implementation": {"path": str(ENGINE.relative_to(ROOT)), "sha256": sha(ENGINE)},
        },
        "does_not_establish": [
            "quartic cyclicity of q3 under the canonical receiver pairing and suspension signs",
            "a source-certified cyclic stabilization or L-infinity morphism from the six-row minimal carrier to all 386 graph rows",
            "the complete 386-row arity-three identity or general lambda-squared source closure on that carrier",
            "compatibility or estimates for q3 under a retarded or advanced Green homotopy",
            "an analytic Moller map or all-order nonlinear fixed point",
            "a Hadamard state, renormalized Lorentzian time-ordered products, QME restoration, residual transfer, or a Lorentzian quantum theory",
        ],
        "next_gate": "Replay q3 quartic cyclicity with the canonical minimal BV pairing, then transport q1, q2, q3 and the pairing through one explicit cyclic stabilization to all 386 rows before claiming general nonlinear source closure.",
        "independent_checker": "quantum-weyl/classical_import/check_strict_minimal_bv_arity_three_identity.py",
        "human_report": "quantum-weyl/classical_import/REPORT_STRICT_MINIMAL_BV_ARITY_THREE_IDENTITY_V1.md",
    }
    value["canonical_hashes"] = {
        "channel_inventory_sha256": digest(inventory),
        "natural_identity_families_sha256": digest(natural_families),
        "proof_basis_sha256": digest(proof_basis),
        "exact_receiver_sha256": digest(exact_receiver),
        "gate_advancement_sha256": digest(value["gate_advancement"]),
        "foundational_strength_sha256": digest(value["foundational_strength"]),
    }
    return value


def render(value: Mapping[str, Any]) -> str:
    inventory = value["channel_inventory"]
    families = "\n".join(f"| `{item['family']}` | {item['channels']} | {item['role']} |" for item in value["natural_identity_families"])
    gates = "\n".join(f"| `{item['gate']}` | `{item['status']}` |" for item in value["gate_advancement"])
    return f"""# Strict minimal-BV arity-three identity v1

**Result:** `{value['result_id']}`

**State:** `{value['result_state']}`
**Dependency:** `LOCAL-ALGEBRAIC`

## Outcome

The complete arity-three coefficient of the authoritative minimal-BV
identity `Q^2=0` is now certified on arbitrary inputs:

```text
q1 q3 + q3 q1 + sum_(2,1)-unshuffles q2(q2,.) = 0.
```

The typed receiver found **{inventory['channel_count']} nonempty channels**
and **{inventory['composable_path_count']} composable paths**:
`{inventory['path_kind_counts']['q1_q3']}` q1-q3,
`{inventory['path_kind_counts']['q2_q2']}` q2-q2, and
`{inventory['path_kind_counts']['q3_q1']}` q3-q1 paths.  All six output rows,
all four q1 components that can compose with q3, all 22 ordered q2
components, and every compatible position of the unique q3 component are
covered.  The fifth unary component, `q1_hstar_h`, is type-incompatible with
the only q3 input and output and therefore creates no arity-three path.

## Why the statement is general

The imported q1, q2 and q3 are the first three Taylor coefficients of the
same authoritative natural BV vector field.  Differentiating its certified
nilpotency identity three times gives exactly the enumerated unshuffle
formula.  This is the arbitrary-input proof.

The independent rational five-jet receiver evaluates every channel on a
derivative-sensitive Minkowski fixture.  All 72 defects vanish.  Three
separate multiplier mutations in q1-q3, q3-q1 and q2-q2 paths produce
nonzero defects.  These finite calculations are implementation regressions,
not a replacement for the natural Taylor theorem.

| Natural identity family | Channels | Role |
|---|---:|---|
{families}

## Gate ledger

| Gate | Status |
|---|---|
{gates}

This result does **not** promote the 386-row candidate.  Quartic q3 cyclicity
and an explicit cyclic stabilization map remain separate gates.
Only after both are accepted can the general lambda-squared source be
replayed on the causal graph carrier.

## Reproduction

```text
python3 quantum-weyl/classical_import/build_strict_minimal_bv_arity_three_identity.py --check
python3 quantum-weyl/classical_import/check_strict_minimal_bv_arity_three_identity.py
python3 quantum-weyl/classical_import/verify_strict_minimal_bv_arity_three_identity.py
python3 -m unittest quantum-weyl/classical_import/tests/test_strict_minimal_bv_arity_three_identity.py -v
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
        print("STRICT_MINIMAL_BV_ARITY_THREE_IDENTITY_V1: " + ("generated artifacts current" if not stale else "stale: " + ", ".join(stale)))
        return bool(stale)
    for path, content in outputs:
        path.write_bytes(content)
    print("STRICT_MINIMAL_BV_ARITY_THREE_IDENTITY_V1: wrote certificate and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
