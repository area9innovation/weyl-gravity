#!/usr/bin/env python3
"""Build the strict support-local q2/D source-to-receiver readiness audit."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DIRECTORY = ROOT / "quantum-weyl/classical_import"
RESULT = DIRECTORY / "certificates/STRICT_SUPPORT_LOCAL_Q2_D_READINESS_V1.json"
REPORT = DIRECTORY / "REPORT_STRICT_SUPPORT_LOCAL_Q2_D_READINESS_V1.md"
INPUTS = (
    ("field_bv_identification/certificates/minimal_bv_chain.json", "pure-weyl-field-bv-minimal-chain-v1", "strict minimal master action and exact unary finite-chain control"),
    ("bridge/certificates/CYLINDER_ARBITRARY_SUPPORT_FULL_BV_Q2_TIME_SLICE_CHAIN_MAP_OBSTRUCTION_V1.json", "CYLINDER_ARBITRARY_SUPPORT_FULL_BV_Q2_TIME_SLICE_CHAIN_MAP_OBSTRUCTION_V1", "complete minimal q2 source ansatz and finite-receiver unary obstruction"),
    ("quantum-weyl/classical_import/certificates/SUPPORT_LOCAL_Q2_EXPORT_CONTRACT.json", "SUPPORT_LOCAL_Q2_EXPORT_CONTRACT", "existing receiver contract and seven required proof checks"),
    ("quantum-weyl/classical_import/schema/support_local_q2_export.schema.json", "SUPPORT_LOCAL_Q2_EXPORT_SCHEMA_V1", "portable component and complete-row format"),
    ("quantum-weyl/classical_import/certificates/CLASSICAL_IMPORT_GATE_V3_RECONCILIATION.json", "CLASSICAL_IMPORT_GATE_V3_RECONCILIATION", "current fail-closed M2 disposition"),
    ("d_quotient_classical/certificates/compact_cylinder_d_charge_audit.json", "COMPACT_CYLINDER_D_CHARGE_AUDIT", "finite residual raw-D control only"),
)
PROOF_IDS = (
    "q1_squared_zero",
    "q1_q2_arity_two_nilpotency",
    "q2_koszul_symmetry",
    "q2_row_completeness",
    "D_q1_commutator_zero",
    "D_q2_derivation",
    "BV_cyclicity_q2",
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_hash(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def load(relative: str) -> dict[str, Any]:
    return json.loads((ROOT / relative).read_text())


def build() -> dict[str, Any]:
    minimal = load(INPUTS[0][0])
    obstruction = load(INPUTS[1][0])
    contract = load(INPUTS[2][0])
    gate = load(INPUTS[4][0])
    d_audit = load(INPUTS[5][0])
    if minimal.get("schema") != "pure-weyl-field-bv-minimal-chain-v1":
        raise ValueError("minimal strict BV source drift")
    if obstruction.get("result_id") != INPUTS[1][1]:
        raise ValueError("all-energy q2/receiver audit drift")
    if contract.get("result_id") != "SUPPORT_LOCAL_Q2_EXPORT_CONTRACT":
        raise ValueError("q2 receiver contract drift")
    if gate.get("result_id") != "CLASSICAL_IMPORT_GATE_V3_RECONCILIATION":
        raise ValueError("Gate V3 drift")
    ansatz = obstruction["local_q2_ansatz"]
    if not obstruction["classification"]["complete_minimal_q2_ansatz_declared"]:
        raise ValueError("complete source ansatz no longer declared")
    if obstruction["classification"]["portable_arbitrary_input_q2_component_payload_certified"]:
        raise ValueError("portable strict q2 already landed; readiness audit is stale")
    if tuple(contract["required_proof_checks"]) != PROOF_IDS:
        raise ValueError("receiver proof inventory drift")
    rows = []
    for item in ansatz["complete_minimal_roles"]:
        symbol = item["symbol"]
        hard_kernel = symbol == "hstar_mu_nu"
        rows.append({
            "symbol": symbol,
            "role": item["role"],
            "degree": item["degree"],
            "source_terms": item["q2_source_terms"],
            "source_status": "ACTION_DEFINED_COMPLETE_ROLE",
            "portable_component_status": "HARD_COEFFICIENT_KERNEL_OPEN" if hard_kernel else "NOT_COMPONENT_SERIALIZED",
            "remaining": (
                "Serialize the polarized second Bach variation together with the metric-antifield cotangent Diff/Weyl action in a receiver-evaluable tensor-natural AST."
                if hard_kernel
                else "Serialize the displayed gauge-algebra or cotangent-lift term with exact factorial and sign conventions in the receiver AST."
            ),
        })
    proof_status = {
        "q1_squared_zero": ("SCOPED_VERIFIED_INPUT", "The exact finite minimal chain and all-energy causal unary complex are existing controls; the future common payload must still replay its own q1 bytes."),
        "q1_q2_arity_two_nilpotency": ("NOT_COMPUTED_FOR_PORTABLE_STRICT_PAYLOAD", "No strict component payload exists on which the receiver can evaluate the arity-two master identity."),
        "q2_koszul_symmetry": ("TAYLOR_CONVENTION_DECLARED_NOT_REPLAYED", "The action source declares q2=(1/2)D^2Q, but no receiver checks the serialized polarized components."),
        "q2_row_completeness": ("SOURCE_ANSATZ_DECLARED_PAYLOAD_ABSENT", "All six minimal output roles are named, but complete component ledgers and hashes are absent."),
        "D_q1_commutator_zero": ("NOT_COMPUTED_ON_FULL_LOCAL_CARRIER", "Raw D is controlled on a selected intrinsic finite carrier, not on every local field, ghost and antifield row."),
        "D_q2_derivation": ("NOT_COMPUTED", "Neither a complete strict q2 payload nor the matching full local D action is available."),
        "BV_cyclicity_q2": ("ACTION_DERIVED_EXPECTED_NOT_REPLAYED", "The BV master action fixes a canonical cyclic origin, but the receiver has no component payload and pairing on which to replay cyclicity."),
    }
    proof_gates = [
        {"check_id": check_id, "status": proof_status[check_id][0], "boundary": proof_status[check_id][1]}
        for check_id in PROOF_IDS
    ]
    witness = obstruction["first_failed_gate"]["witness"]
    value: dict[str, Any] = {
        "schema": "strict-support-local-q2-d-readiness-v1",
        "result_id": "STRICT_SUPPORT_LOCAL_Q2_D_READINESS_V1",
        "result_kind": "SOURCE_TO_RECEIVER_READINESS_AUDIT",
        "lifecycle": "CLASSIFIED",
        "created": "2026-08-15",
        "repository_base_commit": "32ae3f3a890bcda07d2f51641ff0fa8f156be325",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE", "LORENTZIAN-CAUSAL"],
        "question": "Does existing repository evidence already close strict pure-Weyl M2, and if not, which part is an absent formula, which part is absent serialization or verification, and which apparent obstruction belongs only to the old finite time-slice receiver?",
        "answer": "No existing artifact closes M2, but the deficit is substantially narrower than an unknown interaction. The strict minimal master action is fixed, and an earlier all-energy audit declares a complete six-role action-defined q2 ansatz with maximum metric derivative order four and the correct support-intersection rule. What is absent is the portable component payload: no receiver-evaluable tensor-natural AST, complete component hashes, or independent q1q2, D-derivation and cyclicity replay exists. Five rows are gauge-algebra or cotangent-lift serialization tasks. The unique hard coefficient kernel is the metric-antifield row, which contains the polarized second variation of the Bach equation together with cotangent Diff/Weyl terms. The full local D action is also absent; a raw-D result on a selected finite intrinsic carrier is only a control. Separately, the known rank-64 E_5 obstruction rules out an SO(4,2)-equivariant SDR from the all-energy causal source to the old weights-2,3,4 receiver. It does not obstruct support-local q2 on the all-energy carrier. The correct route is therefore to export q2 and D on an all-energy rapid-decay or support-local carrier first, and only then build a compatible completed time-slice receiver.",
        "scope": {
            "theory": "strict pure-Weyl minimal Diff x Weyl BV theory",
            "background": ansatz["background"],
            "source_domain": ansatz["domain"],
            "taylor_convention": ansatz["taylor_convention"],
            "receiver_contract": contract["preflight"],
        },
        "source_completeness": {
            "master_action": ansatz["master_action"],
            "vector_field": ansatz["vector_field"],
            "minimal_output_roles": len(rows),
            "maximum_metric_derivative_order": ansatz["domain"]["maximum_metric_derivative_order"],
            "support_rule": ansatz["domain"]["support_rule"],
            "status": ansatz["status"],
        },
        "q2_row_readiness": rows,
        "proof_gate_readiness": proof_gates,
        "D_action_readiness": {
            "full_local_status": "NOT_SERIALIZED_OR_REPLAYED",
            "finite_control": {
                "artifact": INPUTS[5][1],
                "intrinsic_derived_carrier_preserved": d_audit["phase_spaces"]["P_der"]["D_action_preserves_phase_space"],
                "verdict": d_audit["phase_spaces"]["P_der"]["verdict"],
            },
            "boundary": "A finite residual raw-D action is not the local action on every strict field, ghost, antifield and nonminimal generator required by Gate A.",
        },
        "finite_receiver_obstruction": {
            "status": "OBSTRUCTED_BEFORE_Q2",
            "kind": obstruction["first_failed_gate"]["kind"],
            "energy": witness["energy"],
            "family": witness["family"],
            "source_cohomology_dimension": witness["both_chiralities_dimension"],
            "selected_target_dimension": witness["selected_target_weight_dimension"],
            "minimum_sdr_defect_rank": witness["minimum_sdr_defect_rank"],
            "does_not_obstruct": "support-local full-BV q2 on the all-energy local carrier",
        },
        "next_executable_cut": [
            {"order": 1, "object": "STRICT_Q2_KINEMATIC_AND_COTANGENT_COMPONENT_AST", "deliverable": "Serialize the five non-Bach output rows with exact local tensor operations, signs, factorial convention, complete row ledgers and hashes."},
            {"order": 2, "object": "STRICT_POLARIZED_SECOND_BACH_VARIATION", "deliverable": "Derive and serialize the metric-antifield D^2 Bach kernel through fourth metric-jet order, separately from the gauge-cotangent terms."},
            {"order": 3, "object": "STRICT_FULL_LOCAL_D_ACTION", "deliverable": "Serialize raw D on the same all-energy field/ghost/antifield carrier and distinguish it from compact weights and Berger K."},
            {"order": 4, "object": "STRICT_Q2_D_INDEPENDENT_RECEIVER", "deliverable": "Replay q1q2=0, Koszul symmetry, row completeness, [D,q1]=0, D derivation and BV cyclicity on the exact exported bytes."},
            {"order": 5, "object": "ALL_ENERGY_COMPLETED_TIME_SLICE_RECEIVER", "deliverable": "Only after the local export, construct a rapid-decay/Sobolev all-energy receiver retaining E_n for every n>=2 and the corresponding A/L towers."},
        ],
        "provenance": {
            "inputs": [
                {"path": path, "result_or_artifact_id": result_id, "sha256": sha(ROOT / path), "role": role}
                for path, result_id, role in INPUTS
            ]
        },
        "claim_flags": {
            "STRICT_MINIMAL_Q2_SOURCE_ANSATZ_COMPLETE": True,
            "STRICT_SUPPORT_LOCAL_Q2_COMPONENT_PAYLOAD_CERTIFIED": False,
            "STRICT_FULL_LOCAL_D_ACTION_CERTIFIED": False,
            "STRICT_Q1_Q2_IDENTITY_REPLAYED": False,
            "STRICT_D_Q2_DERIVATION_REPLAYED": False,
            "STRICT_BV_CYCLICITY_Q2_REPLAYED": False,
            "FINITE_SELECTED_RECEIVER_EQUIVARIANT_SDR_OBSTRUCTED": True,
            "ALL_ENERGY_SUPPORT_LOCAL_Q2_OBSTRUCTED": False,
            "CLASSICAL_IMPORT_GATE_PASSED": False,
            "LORENTZIAN_QUANTUM_THEORY": False,
            "QME_RESTORED": False,
        },
        "does_not_establish": [
            "a portable strict support-local q2 component payload",
            "the polarized second variation of the Bach equation",
            "a full local D action or D-Cartan homotopy",
            "any of the six interaction-side receiver identities",
            "an obstruction to strict support-local q2 on the all-energy carrier",
            "an all-energy completed time-slice receiver or residual SDR",
            "a passed classical import gate, Hadamard state, QME restoration or Lorentzian quantum theory",
        ],
        "independent_checker": {
            "path": "quantum-weyl/classical_import/check_strict_support_local_q2_d_readiness.py",
            "checks": [
                "six action-defined role rows", "unique D2-Bach hard kernel",
                "seven proof-gate dispositions", "rank-64 E5 receiver obstruction",
                "all-energy q2 non-obstruction firewall", "finite-D versus local-D firewall",
                "content-pinned provenance", "canonical digest",
            ],
            "expected_digest": "",
        },
        "human_report": "quantum-weyl/classical_import/REPORT_STRICT_SUPPORT_LOCAL_Q2_D_READINESS_V1.md",
    }
    value["independent_checker"]["expected_digest"] = canonical_hash({
        key: value[key]
        for key in (
            "scope", "source_completeness", "q2_row_readiness",
            "proof_gate_readiness", "D_action_readiness",
            "finite_receiver_obstruction", "next_executable_cut",
        )
    })
    return value


def render(value: dict[str, Any]) -> str:
    rows = "\n".join(
        f"| `{item['symbol']}` | {item['role']} | `{item['portable_component_status']}` | {item['remaining']} |"
        for item in value["q2_row_readiness"]
    )
    gates = "\n".join(
        f"| `{item['check_id']}` | `{item['status']}` | {item['boundary']} |"
        for item in value["proof_gate_readiness"]
    )
    cuts = "\n".join(
        f"{item['order']}. **`{item['object']}`** — {item['deliverable']}"
        for item in value["next_executable_cut"]
    )
    return f"""# Strict support-local q2/D readiness audit v1

**Result:** `{value['result_id']}`

**Lifecycle:** `{value['lifecycle']}`

## Outcome

{value['answer']}

## Six output rows

| Symbol | Role | Portable status | Remaining work |
|---|---|---|---|
{rows}

Five rows are primarily exact serialization of gauge-algebra or cotangent-lift
terms already named by the master action.  The metric-antifield row is the
coefficient-heavy kernel because it contains the polarized second Bach
variation through fourth metric-jet order.

## Seven receiver gates

| Check | Current status | Why |
|---|---|---|
{gates}

## The obstruction belongs to the receiver, not q2

At energy five the all-energy source has a two-chirality `E` cohomology block
of dimension **{value['finite_receiver_obstruction']['source_cohomology_dimension']}**, while the old selected receiver has dimension
**{value['finite_receiver_obstruction']['selected_target_dimension']}** there.  Any equivariant SDR into that receiver has defect rank at
least **{value['finite_receiver_obstruction']['minimum_sdr_defect_rank']}**.  This failure occurs at unary order and does not obstruct a
support-local `q2` on the all-energy carrier.

## Next executable cut

{cuts}

## Reproduction

```text
python3 quantum-weyl/classical_import/build_strict_support_local_q2_d_readiness.py --check
python3 quantum-weyl/classical_import/check_strict_support_local_q2_d_readiness.py
python3 quantum-weyl/classical_import/verify_strict_support_local_q2_d_readiness.py
python3 -m unittest quantum-weyl/classical_import/tests/test_strict_support_local_q2_d_readiness.py
```

## What this does not establish

""" + "\n".join(f"- {item}." for item in value["does_not_establish"]) + "\n"


def generated() -> tuple[bytes, bytes]:
    value = build()
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode(), render(value).encode()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result_bytes, report_bytes = generated()
    outputs = ((RESULT, result_bytes), (REPORT, report_bytes))
    stale = [str(path.relative_to(ROOT)) for path, content in outputs if not path.is_file() or path.read_bytes() != content]
    if args.check:
        print("STRICT_SUPPORT_LOCAL_Q2_D_READINESS_V1: " + ("generated artifacts current" if not stale else "stale: " + ", ".join(stale)))
        return bool(stale)
    for path, content in outputs:
        path.write_bytes(content)
    print("STRICT_SUPPORT_LOCAL_Q2_D_READINESS_V1: wrote certificate and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
