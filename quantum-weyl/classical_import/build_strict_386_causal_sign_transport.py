#!/usr/bin/env python3
"""Build the strict-minimal sign transport onto the 386-row causal carrier."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/STRICT_386_CAUSAL_SIGN_TRANSPORT_V1.json"
REPORT = HERE / "REPORT_STRICT_386_CAUSAL_SIGN_TRANSPORT_V1.md"

INPUTS = (
    (
        "quantum-weyl/classical_import/certificates/CLASSICAL_IMPORT_GATE_V5_RECONCILIATION.json",
        "CLASSICAL_IMPORT_GATE_V5_RECONCILIATION",
        "current fail-closed strict import disposition",
    ),
    (
        "quantum-weyl/classical_import/certificates/STRICT_MINIMAL_BV_CYCLIC_SIGN_RECONCILIATION_V1.json",
        "STRICT_MINIMAL_BV_CYCLIC_SIGN_RECONCILIATION_V1",
        "canonical thirty-component endpoint sign convention",
    ),
    (
        "covariant_completion/certificates/curved_full_prolonged_green_homotopy_assembly.json",
        "pure-weyl-full-prolonged-green-homotopy-assembly-v1",
        "strict 386-row causal Green homotopy",
    ),
    (
        "covariant_completion/certificates/curved_deformation_retract_status.json",
        "pure-weyl-curved-deformation-retract-status-v1",
        "strict curved metric-core and auxiliary row decomposition",
    ),
)


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()


def load(relative: str) -> dict[str, Any]:
    return json.loads((ROOT / relative).read_text())


def source_id(value: Mapping[str, Any]) -> str | None:
    return value.get("result_id") or value.get("schema")


def endpoint_blocks() -> list[dict[str, Any]]:
    return [
        {
            "cochain_block": "G",
            "role": "Diff plus Weyl ghosts",
            "gate_generators": ["c", "omega"],
            "dimension": 5,
            "transport_sign": 1,
        },
        {
            "cochain_block": "M",
            "role": "metric field",
            "gate_generators": ["h"],
            "dimension": 10,
            "transport_sign": 1,
        },
        {
            "cochain_block": "E",
            "role": "metric antifield",
            "gate_generators": ["h_star"],
            "dimension": 10,
            "transport_sign": 1,
        },
        {
            "cochain_block": "I",
            "role": "Diff plus Weyl ghost antifields",
            "gate_generators": ["c_star", "omega_star"],
            "dimension": 5,
            "transport_sign": -1,
        },
    ]


def build() -> dict[str, Any]:
    gate, cyclic, causal, retract = (load(path) for path, _, _ in INPUTS)
    for value, (_, expected, _) in zip((gate, cyclic, causal, retract), INPUTS):
        if source_id(value) != expected:
            raise ValueError(f"dependency drift: {expected}")

    if gate["gate_disposition"]["gate_a_status"] != "FAIL_CLOSED":
        raise ValueError("Gate A unexpectedly passed")
    if gate["gate_disposition"]["accepted_common_snapshot_hashes"] != 0:
        raise ValueError("Gate V5 unexpectedly accepts a common snapshot")
    if not cyclic["claim_flags"]["CANONICAL_SIGN_TRANSLATION_CERTIFIED"]:
        raise ValueError("minimal sign translation unavailable")
    if cyclic["canonical_pairing"]["component_basis_dimension"] != 30:
        raise ValueError("minimal component dimension drift")
    if not causal.get("causal_green_homotopy"):
        raise ValueError("386-row causal Green homotopy unavailable")
    if causal["dimension_ledger"] != {
        "algebraically_contracted": 356,
        "causal_endpoint": 30,
        "identity": "386=356+30",
        "prolonged": 386,
    }:
        raise ValueError("386-row dimension ledger drift")
    if causal["endpoint_channel_assembly"]["full_endpoint_ranks"] != [5, 10, 10, 5]:
        raise ValueError("causal endpoint block ranks drift")
    if not retract["curved_deformation_retract"]:
        raise ValueError("curved deformation retract unavailable")
    if retract["factorized_actual_curved_Q"]["exact_inputs"]["cotangent_lift_full_66_row_pairing_defect"] != 0:
        raise ValueError("curved pairing input drift")

    blocks = endpoint_blocks()
    endpoint_signs = [
        block["transport_sign"]
        for block in blocks
        for _ in range(block["dimension"])
    ]
    full_signs = [1] * 356 + endpoint_signs
    if len(endpoint_signs) != 30 or len(full_signs) != 386:
        raise ValueError("transport dimension mismatch")
    if any(sign * sign != 1 for sign in full_signs):
        raise ValueError("transport is not involutive")

    proof_ledger = [
        {
            "check_id": "endpoint_type_dimension_bridge",
            "status": "VERIFIED",
            "equation": "30=(4+1)+10+10+(4+1)=5+10+10+5",
            "evidence": "the Gate-V5 generator groups match the causal endpoint G/M/E/I ranks",
        },
        {
            "check_id": "full_transport_involution",
            "status": "VERIFIED",
            "equation": "T_386=I_356 direct-sum diag(I_5,I_10,I_10,-I_5); T_386^2=I_386",
            "evidence": "381 positive and five negative diagonal entries over the integers",
        },
        {
            "check_id": "transported_unary_nilpotency",
            "status": "VERIFIED_BY_EXACT_CONJUGATION",
            "equation": "Q'=T_386 Q T_386 and (Q')^2=T_386 Q^2 T_386=0",
            "evidence": "T_386 is involutive and the source causal complex is a chain complex",
        },
        {
            "check_id": "transported_green_homotopy",
            "status": "VERIFIED_BY_EXACT_CONJUGATION",
            "equation": "Lambda'_plus/minus=T_386 Lambda_plus/minus T_386; Q'Lambda'+Lambda'Q'=I_386",
            "evidence": "conjugation transports the certified two-sided Green-homotopy identity",
        },
        {
            "check_id": "causal_support_and_orientation",
            "status": "VERIFIED",
            "equation": "supp(T_386 u)=supp(u)",
            "evidence": "T_386 is a pointwise order-zero signed bundle automorphism, so it neither enlarges support nor swaps advanced and retarded orientation",
        },
        {
            "check_id": "transported_adjoint_relation",
            "status": "VERIFIED_ON_TRANSPORTED_PAIRING",
            "equation": "omega'(x,y)=omega(T_386 x,T_386 y) implies (Lambda'_plus)^sharp'=Lambda'_minus",
            "evidence": "the source graded-adjoint theorem is invariant under simultaneous transport of operator and pairing",
        },
        {
            "check_id": "common_byte_identification",
            "status": "NOT_ESTABLISHED",
            "equation": "Gate-V5 accepted common hashes=0",
            "evidence": "matching dimensions and formula roles do not identify the Gate-V5 q1 bytes with the 386-row endpoint bytes",
        },
        {
            "check_id": "nonlinear_causal_compatibility",
            "status": "NOT_ESTABLISHED",
            "equation": "no transported q2/Green compatibility theorem",
            "evidence": "the four changed ordered q2 rows are local-algebraic data, while the 386 certificate is unary causal data",
        },
    ]

    value: dict[str, Any] = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "schema": "strict-386-causal-sign-transport-v1",
        "result_id": "STRICT_386_CAUSAL_SIGN_TRANSPORT_V1",
        "result_kind": "SAME_THEORY_CAUSAL_CONVENTION_STABILITY_CERTIFICATE",
        "result_state": "STRICT_386_CAUSAL_ARCHITECTURE_STABLE_UNDER_MINIMAL_SIGN_TRANSPORT_COMMON_HASH_OPEN",
        "lifecycle": "CLASSIFIED",
        "created": "2026-08-15",
        "repository_base_commit": "2a9cee84",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "question": "Does the canonical ghost-antifield sign repair invalidate the existing strict 386-row causal Green-homotopy architecture?",
        "answer": "No. The repaired thirty-component minimal carrier has exactly the 5/10/10/5 endpoint type profile of the strict 386-row causal complex. Extending its sign involution by the identity on the 356 algebraically contracted rows gives an exact pointwise involution T_386. Simultaneously conjugating Q and both Green homotopies preserves nilpotency, the two-sided homotopy identity, causal support, advanced/retarded orientation and the graded-adjoint relation with the transported pairing. This is a convention-stability theorem, not a common-byte import theorem: Gate A still accepts zero common hashes, the complete full-carrier pairing is not serialized, and no nonlinear q2/Green, Hadamard or QME claim follows.",
        "carrier_bridge": {
            "gate_minimal_component_dimension": 30,
            "causal_endpoint_dimension": 30,
            "causal_algebraic_complement_dimension": 356,
            "causal_full_dimension": 386,
            "endpoint_blocks": blocks,
            "gate_to_endpoint_permutation": [
                "(c_0,c_1,c_2,c_3,omega) -> G[0:5]",
                "h_(00,01,02,03,11,12,13,22,23,33) -> M[0:10]",
                "h_star_(00,01,02,03,11,12,13,22,23,33) -> E[0:10]",
                "(c_star_0,c_star_1,c_star_2,c_star_3,omega_star) -> I[0:5]",
            ],
            "compatibility_status": "TYPE_DIMENSION_AND_COMPLEX_ROLE_MATCH_COMMON_CONTENT_HASH_NOT_ESTABLISHED",
        },
        "transport": {
            "formula": "T_386=I_356 direct-sum diag(I_5,I_10,I_10,-I_5)",
            "positive_eigenvalue_multiplicity": full_signs.count(1),
            "negative_eigenvalue_multiplicity": full_signs.count(-1),
            "rank": len(full_signs),
            "determinant": -1,
            "involutive": True,
            "differential_order": 0,
            "support_effect": "EXACTLY_PRESERVED",
            "changed_endpoint_block": "I",
            "changed_gate_generators": ["c_star", "omega_star"],
            "q1_rows_changed": cyclic["sign_translation"]["changed_q1_component_ids"],
            "q2_rows_changed_but_not_causally_transferred": cyclic["sign_translation"]["changed_q2_component_ids"],
            "transported_differential": "Q'=T_386 Q T_386",
            "transported_green_homotopies": "Lambda'_plus/minus=T_386 Lambda_plus/minus T_386",
            "transported_pairing": "omega'(x,y)=omega(T_386 x,T_386 y)",
        },
        "proof_ledger": proof_ledger,
        "foundational_strength": {
            "fixed_carrier_transport_base": "PRA",
            "reason": "the wrapper uses only finite signed permutations, integer dimension arithmetic and equational substitution on a fixed 386-row block decomposition",
            "choice_operation_added_by_transport": False,
            "infinite_selection_added_by_transport": False,
            "analytic_causal_input": "inherited unchanged from the content-pinned LORENTZIAN-CAUSAL source certificate",
            "weakest_base_for_imported_causal_theorem": "NOT_ESTABLISHED",
            "reversal_or_choice_lower_bound": "NOT_ESTABLISHED",
        },
        "architecture_disposition": {
            "strict_386_route_invalidated_by_sign_repair": False,
            "strict_386_route_convention_stable": True,
            "same_theory_role_match": True,
            "same_operator_bytes_established": False,
            "causal_stage_preserved": True,
            "nonlinear_stage_preserved": False,
            "next_decisive_object": "A content-addressed endpoint inclusion identifying the translated Gate-V5 q1 and canonical pairing with the 30 causal endpoint rows, followed by extension across all 356 algebraic/nonminimal/auxiliary rows and a same-carrier q2/D compatibility theorem.",
        },
        "canonical_hashes": {},
        "provenance": {
            "inputs": [
                {
                    "path": path,
                    "result_or_schema_id": expected,
                    "sha256": file_hash(ROOT / path),
                    "role": role,
                }
                for path, expected, role in INPUTS
            ]
        },
        "claim_flags": {
            "STRICT_386_SIGN_TRANSPORT_INVOLUTIVE": True,
            "STRICT_386_UNARY_NILPOTENCY_PRESERVED": True,
            "STRICT_386_CAUSAL_GREEN_HOMOTOPY_PRESERVED": True,
            "STRICT_386_CAUSAL_SUPPORT_PRESERVED": True,
            "STRICT_386_GRADED_ADJOINT_PRESERVED_ON_TRANSPORTED_PAIRING": True,
            "STRICT_386_ARCHITECTURE_INVALIDATED_BY_GATE_V5": False,
            "GATE_V5_TO_386_COMMON_BYTES_IDENTIFIED": False,
            "FULL_386_CANONICAL_PAIRING_SERIALIZED": False,
            "STRICT_386_Q2_GREEN_COMPATIBILITY_CERTIFIED": False,
            "CLASSICAL_IMPORT_GATE_PASSED": False,
            "BRST_HADAMARD_STATE_CONSTRUCTED": False,
            "LORENTZIAN_QME_RESTORED": False,
        },
        "does_not_establish": [
            "a common content hash between the Gate-V5 local q1 bytes and the 386-row causal endpoint",
            "a serialized canonical odd pairing on all 386 rows",
            "cyclic compatibility of the 356-row algebraic/nonminimal/auxiliary complement",
            "compatibility of strict local q2 or D with the transported causal Green homotopy",
            "a passed classical import Gate A",
            "a Hadamard covariance, BRST Ward identity, positivity theorem, renormalized Lorentzian product or QME",
            "a weakest-base or choice-principle classification of the imported analytic causal theorem",
        ],
        "next_gate": "Serialize the endpoint inclusion/permutation and pairing on the exact 386-row bytes, prove coefficientwise equality with translated Gate-V5 q1, extend the canonical sign/pairing convention over the 356-row complement, and only then test q2/D compatibility with the causal contraction.",
        "schema_path": "quantum-weyl/classical_import/schema/strict-386-causal-sign-transport-v1.schema.json",
        "independent_checker": "quantum-weyl/classical_import/check_strict_386_causal_sign_transport.py",
        "human_report": "quantum-weyl/classical_import/REPORT_STRICT_386_CAUSAL_SIGN_TRANSPORT_V1.md",
    }
    value["canonical_hashes"] = {
        "carrier_bridge_sha256": digest(value["carrier_bridge"]),
        "transport_sha256": digest(value["transport"]),
        "proof_ledger_sha256": digest(proof_ledger),
        "foundational_strength_sha256": digest(value["foundational_strength"]),
        "architecture_disposition_sha256": digest(value["architecture_disposition"]),
    }
    return value


def render(value: Mapping[str, Any]) -> str:
    blocks = "\n".join(
        f"| `{row['cochain_block']}` | {row['role']} | {row['dimension']} | {row['transport_sign']:+d} |"
        for row in value["carrier_bridge"]["endpoint_blocks"]
    )
    checks = "\n".join(
        f"| `{row['check_id']}` | `{row['status']}` | {row['evidence']} |"
        for row in value["proof_ledger"]
    )
    return f"""# Strict 386-row causal sign transport

**Result:** `{value['result_id']}`

**State:** `{value['result_state']}`

**Dependencies:** `LOCAL-ALGEBRAIC`, `LORENTZIAN-CAUSAL`

## Outcome

The Gate-V5 ghost-antifield sign repair does **not** invalidate the existing
strict 386-row causal architecture. Its thirty-component minimal carrier has
exactly the endpoint profile of the causal complex:

| endpoint block | role | dimension | sign |
|---|---|---:|---:|
{blocks}

Extending the endpoint involution by the identity on the 356 algebraically
contracted rows gives

```text
T_386 = I_356 direct-sum diag(I_5,I_10,I_10,-I_5).
```

It has 381 positive and five negative diagonal entries. Conjugating the unary
differential and both Green homotopies transports the exact chain-homotopy
identity. Because the map is pointwise and order zero, support and causal
orientation are unchanged. Transporting the pairing at the same time preserves
the graded-adjoint relation.

## What this decides

The strict target-theory causal route survives the newly discovered convention
repair. We therefore do not need to rebuild its hyperbolic architecture merely
because `c_star` and `omega_star` change sign.

This is not yet the missing import bridge. The match is exact at the level of
types, dimensions and complex roles, but Gate V5 accepts zero common hashes.
The certificate does not identify the local q1 bytes with the endpoint bytes,
serialize the pairing on all 386 rows, or prove nonlinear q2/D compatibility.

## Exact checks

| check | status | meaning |
|---|---|---|
{checks}

## Foundational strength

For the fixed carrier, the transport wrapper is primitive-recursive finite
algebra: signed permutations, integer counts and equational substitution. It
adds neither a choice operation nor an infinite selection. The weakest base of
the imported analytic causal theorem itself has not been established, so the
PRA classification must not be widened to the whole Green theorem.

## Next gate

{value['next_gate']}

## Reproduction

```bash
python3 quantum-weyl/classical_import/build_strict_386_causal_sign_transport.py --check
python3 quantum-weyl/classical_import/check_strict_386_causal_sign_transport.py
python3 quantum-weyl/classical_import/verify_strict_386_causal_sign_transport.py
python3 -m unittest quantum-weyl/classical_import/tests/test_strict_386_causal_sign_transport.py
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
        print(
            "STRICT_386_CAUSAL_SIGN_TRANSPORT_V1: "
            + ("generated artifacts current" if not stale else "stale: " + ", ".join(stale))
        )
        return bool(stale)
    for path, content in outputs:
        path.write_bytes(content)
    print("STRICT_386_CAUSAL_SIGN_TRANSPORT_V1: wrote certificate and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
