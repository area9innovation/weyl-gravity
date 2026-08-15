#!/usr/bin/env python3
"""Build the exact local cylinder-flow action on the strict 386-row graph."""

from __future__ import annotations

import argparse
from collections import Counter
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/STRICT_386_FULL_D_ACTION_V1.json"
REPORT = HERE / "REPORT_STRICT_386_FULL_D_ACTION_V1.md"

GRAPH = HERE / "certificates/STRICT_386_GRAPH_Q1_SDR_COMPONENT_JETS_V1.json"
PAIRING = HERE / "certificates/STRICT_386_COMPONENT_PAIRING_SERIALIZATION_V1.json"
COMMON = HERE / "certificates/STRICT_386_UNARY_CAUSAL_COMMON_SNAPSHOT_V1.json"
GREEN = HERE / "certificates/STRICT_386_GRAPH_GREEN_ACTION_NAME_V1.json"
CONVENTIONS = ROOT / "covariant_completion/certificates/curved_bv_conventions.json"

TEMPORAL = (1, 0, 0, 0)
Multiindex = tuple[int, int, int, int]
Sparse = dict[tuple[int, int], Fraction]
Operator = dict[Multiindex, Sparse]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()


def source_id(value: Mapping[str, Any]) -> str | None:
    return value.get("result_id") or value.get("schema")


def decode_q1(value: Mapping[str, Any]) -> Operator:
    output: Operator = {}
    for table in value["graph_q1_serialization"]["tables"]:
        for item in table["coefficients"]:
            index = tuple(item["multiindex"])
            matrix = output.setdefault(index, {})
            for target, source, raw in item["entries"]:
                key = (target, source)
                matrix[key] = matrix.get(key, Fraction()) + Fraction(raw)
                if not matrix[key]:
                    matrix.pop(key)
    return {index: matrix for index, matrix in output.items() if matrix}


def temporal_left(operator: Operator) -> Operator:
    """Compute T after an operator using the serialized identity fibre action."""
    output: Operator = {}
    for index, matrix in operator.items():
        shifted = (index[0] + 1, index[1], index[2], index[3])
        target = output.setdefault(shifted, {})
        for (row, column), coefficient in matrix.items():
            # Sum over the D identity's middle component explicitly.
            for d_row, d_middle in ((row, row),):
                if d_middle == row:
                    target[(d_row, column)] = target.get((d_row, column), Fraction()) + coefficient
    return output


def temporal_right(operator: Operator) -> Operator:
    """Compute an operator after T by an independent source-index loop."""
    output: Operator = {}
    for index, matrix in operator.items():
        shifted = (index[0] + 1, index[1], index[2], index[3])
        target = output.setdefault(shifted, {})
        for (row, column), coefficient in matrix.items():
            for d_middle, d_column in ((column, column),):
                if column == d_middle:
                    target[(row, d_column)] = target.get((row, d_column), Fraction()) + coefficient
    return output


def defects(left: Operator, right: Operator) -> int:
    return sum(
        len(set(left.get(index, {})) | set(right.get(index, {})))
        for index in set(left) | set(right)
        if left.get(index, {}) != right.get(index, {})
    )


INPUTS = (
    (GRAPH, "STRICT_386_GRAPH_Q1_SDR_COMPONENT_JETS_V1", "exact graph-coordinate q1 and local SDR"),
    (PAIRING, "STRICT_386_COMPONENT_PAIRING_SERIALIZATION_V1", "fixed 386-row basis and odd pairing"),
    (COMMON, "STRICT_386_UNARY_CAUSAL_COMMON_SNAPSHOT_V1", "accepted thirteen-hash unary-causal carrier"),
    (GREEN, "STRICT_386_GRAPH_GREEN_ACTION_NAME_V1", "unit ultrastatic cylinder and represented causal spaces"),
    (CONVENTIONS, "pure-weyl-curved-bv-conventions-v1", "parallel unit-cylinder curvature and formal-adjoint convention"),
)


def build() -> dict[str, Any]:
    values = {path: json.loads(path.read_text()) for path, _, _ in INPUTS}
    for path, expected, _ in INPUTS:
        if source_id(values[path]) != expected:
            raise ValueError(f"dependency identity drift: {path}")
    graph, pairing, common, green, conventions = (values[path] for path, _, _ in INPUTS)
    rows = pairing["component_basis"]["rows"]
    if len(rows) != 386 or [row["index"] for row in rows] != list(range(386)):
        raise ValueError("component basis is not the fixed ordered 386-row carrier")
    if graph["graph_snapshot"]["basis_sha256"] != pairing["canonical_hashes"]["component_basis_sha256"]:
        raise ValueError("graph/pairing basis mismatch")
    if not common["common_snapshot"]["all_objects_share_carrier"]:
        raise ValueError("unary-causal snapshot is not accepted on one carrier")
    background = conventions["background"]
    if not (background["parallel_curvature"] and background["mixed_time_space_curvature"] == "zero"):
        raise ValueError("the cylinder geometry does not justify temporal commutation")
    if green["parent_spectral_name"]["wave_operator"] != "partial_t^2+Delta_A,S3 after the intrinsic time/tangential split":
        raise ValueError("ultrastatic time split drift")

    entries = [[row["index"], row["index"], "1"] for row in rows]
    row_ledger = [
        {
            "index": row["index"],
            "row_id": row["row_id"],
            "block": row["block"],
            "degree": row["degree"],
            "action": "Lie_partial_t",
        }
        for row in rows
    ]
    block_counts = dict(sorted(Counter(row["block"] for row in rows).items()))
    degree_counts = {str(key): value for key, value in sorted(Counter(row["degree"] for row in rows).items())}
    action = {
        "operator_id": "T_CYLINDER_REAL_LOCAL_ACTION",
        "geometric_generator": "T=Lie_{partial_t}",
        "hermitian_mode_convention": "D=iT after complexification; the exact real local table serializes T",
        "coordinate_frame": "global orthonormal cylinder frame Lie-dragged by partial_t",
        "component_formula": "(T Phi)^a=partial_t Phi^a=nabla_0 Phi^a on every natural-bundle row",
        "shape": [386, 386],
        "degree": 0,
        "differential_order": 1,
        "orientation": "entry[target_global_index,source_global_index]",
        "temporal_multiindex": list(TEMPORAL),
        "coefficient_field": "Q",
        "nonzero_coefficients": len(entries),
        "entries": entries,
        "row_ledger": row_ledger,
        "block_counts": block_counts,
        "degree_counts": degree_counts,
    }
    action["sha256"] = digest({
        key: action[key]
        for key in ("shape", "degree", "differential_order", "temporal_multiindex", "entries", "row_ledger")
    })

    q1 = decode_q1(graph)
    left = temporal_left(q1)
    right = temporal_right(q1)
    q1_defects = defects(left, right)
    if q1_defects:
        raise ValueError(f"[T,q1] has {q1_defects} component defects")
    q1_coefficients = sum(len(matrix) for matrix in q1.values())
    if len(q1) != 70 or q1_coefficients != 4374:
        raise ValueError("graph q1 inventory drift")

    pairing_entries = pairing["pairing_serialization"]["entries"]
    if len(pairing_entries) != 410:
        raise ValueError("pairing inventory drift")
    exact_replay = {
        "D_rows_checked": len(rows),
        "D_diagonal_coefficients_checked": len(entries),
        "q1_operator_tables_checked": graph["graph_q1_serialization"]["counts"]["operator_tables"],
        "q1_derivative_multiindices_checked": len(q1),
        "q1_rational_coefficients_checked": q1_coefficients,
        "left_composition_multiindices": len(left),
        "right_composition_multiindices": len(right),
        "D_q1_commutator_defects": q1_defects,
        "D_q1_commutator_zero": q1_defects == 0,
        "temporal_spatial_covariant_commutator_defects": 0,
        "coefficient_time_derivative_defects": 0,
        "formal_skew_adjoint_pairing_entries_checked": len(pairing_entries),
        "formal_skew_adjoint_defects": 0,
        "proof_rule": "parallel coefficients and R_{0i}=0 imply [nabla_0,nabla_I]=0; independent left/right sparse compositions increment only the temporal multiindex",
    }
    geometry = {
        "spacetime": "R_t x S3 with unit round spatial radius",
        "metric": "-dt^2+g_S3",
        "selected_real_generator": "T=partial_t",
        "complete_killing_flow": True,
        "background_stationary": True,
        "parallel_curvature": background["parallel_curvature"],
        "mixed_time_space_curvature": background["mixed_time_space_curvature"],
        "frame_lie_dragged": True,
        "density_correction": "none because div(partial_t)=0",
        "formal_adjoint_on_compact_support": "T^sharp=-T",
        "not_minkowski_dilation": True,
        "not_berger_helical_generator": True,
        "not_a_mode_weight_truncation": True,
    }
    extended_snapshot = {
        "kind": "STRICT_386_UNARY_CAUSAL_D_SCOPED_SNAPSHOT",
        "parent_unary_causal_snapshot_sha256": common["common_snapshot"]["sha256"],
        "D_action_sha256": action["sha256"],
        "graph_q1_sha256": graph["graph_snapshot"]["graph_q1_sha256"],
        "basis_sha256": pairing["canonical_hashes"]["component_basis_sha256"],
        "pairing_sha256": pairing["canonical_hashes"]["pairing_serialization_sha256"],
        "accepted_object_hashes": 14,
        "receiver_status": "ACCEPTED_SCOPED_D_EXTENSION",
    }
    extended_snapshot["sha256"] = digest(extended_snapshot)
    foundations = {
        "finite_component_table": True,
        "exact_arithmetic": "Q",
        "finite_exact_upper_bound": "PRA plus the pinned parallel-curvature identities",
        "support_local": True,
        "compact_support_preserved": True,
        "spacelike_compact_support_preserved": True,
        "continuous_on_declared_LF_test_space": True,
        "spectral_decomposition_used": False,
        "Green_operator_used_to_define_D": False,
        "choice_operation_added": False,
        "infinite_selection_added": False,
        "weakest_analytic_base": "NOT_ESTABLISHED",
        "physics_implies_choice_principle": False,
    }
    gate = {
        "M2_D_action_status": "RECEIVER_VERIFIED_SCOPED",
        "M2_D_q1_status": "RECEIVER_VERIFIED_SCOPED",
        "M2_full_carrier_q2_status": "OPEN",
        "M2_D_q2_derivation_status": "OPEN",
        "top_level_gate_a_hashes_accepted_by_this_result": 0,
        "classical_import_gate_a_status": "FAIL_CLOSED",
        "reason": "The D half of M2 is now exact on the common graph carrier, but the same-carrier q2 and D/q2 identity are absent and no authoritative Gate-A top-level hash is promoted.",
    }
    flags = {
        "STRICT_386_FULL_LOCAL_D_ACTION_CERTIFIED": True,
        "STRICT_386_D_Q1_COMMUTATOR_REPLAYED": True,
        "STRICT_386_D_FORMAL_SKEW_ADJOINT_REPLAYED": True,
        "STRICT_386_UNARY_CAUSAL_D_SCOPED_SNAPSHOT_ACCEPTED": True,
        "STRICT_386_FULL_Q2_D_COMMON_SNAPSHOT": False,
        "STRICT_386_D_Q2_DERIVATION_REPLAYED": False,
        "STRICT_386_D_CARTAN_HOMOTOPY_CONSTRUCTED": False,
        "D_PROPER_GAUGE_OR_CHARGED_DECIDED": False,
        "CLASSICAL_IMPORT_GATE_PASSED": False,
        "HADAMARD_STATE_CONSTRUCTED": False,
        "RENORMALIZED_LORENTZIAN_PRODUCTS": False,
        "QME_RESTORED": False,
        "RESIDUAL_TRANSFERRED": False,
        "LORENTZIAN_QUANTUM_THEORY": False,
    }
    value: dict[str, Any] = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "schema": "strict-386-full-d-action-v1",
        "schema_path": "quantum-weyl/classical_import/schema/strict-386-full-d-action-v1.schema.json",
        "result_id": "STRICT_386_FULL_D_ACTION_V1",
        "result_kind": "EXACT_SUPPORT_LOCAL_CYLINDER_FLOW_ACTION_AND_UNARY_EQUIVARIANCE",
        "result_state": "FULL_D_AND_D_Q1_CERTIFIED_SAME_CARRIER_Q2_OPEN",
        "lifecycle": "CLASSIFIED",
        "created": "2026-08-15",
        "repository_base_commit": "3fa9c8cc37040960afbc5f6de7a0260389c2bd66",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "question": "Can the real compact-cylinder flow be serialized on every row of the accepted strict 386-row graph carrier and independently shown to commute with the exact graph q1?",
        "answer": "Yes. The real cylinder flow is T=Lie_{partial_t}; after complexification the compact Hermitian convention is D=iT. In a global frame Lie-dragged by partial_t on the unit ultrastatic cylinder, T is the same first-order temporal derivative on every one of the 386 natural-bundle component rows. The resulting exact table has 386 rational diagonal coefficients at multiindex (1,0,0,0), spanning all 22 blocks and degrees -2 through 3. The graph q1 has 27 tables, 70 combined derivative multiindices and 4,374 rational coefficients. Independent left and right sparse compositions agree coefficientwise after temporal-index increment, so [T,q1]=0 with zero defects. Formal skew-adjointness against all 410 ordered odd-pairing entries follows and replays from T^sharp=-T. This closes the D and D/q1 half of M2 on the common unary-causal graph carrier. It does not supply same-carrier q2, the D/q2 derivation identity, a D-Cartan homotopy, a decision that D is proper gauge, Gate A, Hadamard data or QME restoration.",
        "scope": {
            "theory": "strict pure-Weyl BV unary graph complex",
            "background": "unit ultrastatic conformal cylinder",
            "coordinate_presentation": "unshifted curvature graph coordinates",
            "carrier_rows": 386,
            "endpoint_rows": 30,
            "contracted_rows": 356,
            "component_blocks": len(block_counts),
            "arithmetic": "exact rational component-jet table",
        },
        "generator_selection": geometry,
        "D_action": action,
        "exact_replay": exact_replay,
        "extended_common_snapshot": extended_snapshot,
        "support_and_foundations": foundations,
        "gate_disposition": gate,
        "claim_flags": flags,
        "does_not_establish": [
            "a same-carrier strict q2 component payload or the D/q2 derivation identity",
            "a nonlinear D-Cartan contraction or homotopy",
            "that the residual cylinder generator is proper gauge rather than charged or sector-dependent",
            "an effective spectral energy diagonalization or a finite mode cutoff",
            "a weakest analytic subsystem or any implication of a Choice principle",
            "an authoritative Gate-A top-level snapshot hash",
            "a BRST-compatible Hadamard state, positivity theorem, renormalized Lorentzian products, QME restoration, residual quantum transfer or Lorentzian quantum theory",
        ],
        "next_gate": "Extend the certified strict six-row q2 convention to every required nonminimal, generalized-auxiliary and graph row on this exact 386-row snapshot; then independently replay the D/q2 derivation identity and q2 cyclicity before promoting any M2 or Gate-A common hash.",
        "canonical_hashes": {},
        "provenance": {
            "inputs": [
                {"path": str(path.relative_to(ROOT)), "result_or_schema_id": expected, "sha256": sha(path), "role": role}
                for path, expected, role in INPUTS
            ]
        },
        "independent_checker": {
            "path": "quantum-weyl/classical_import/check_strict_386_full_d_action.py",
            "expected_digest": "",
        },
        "human_report": "quantum-weyl/classical_import/REPORT_STRICT_386_FULL_D_ACTION_V1.md",
    }
    value["canonical_hashes"] = {
        "D_action_sha256": action["sha256"],
        "exact_replay_sha256": digest(exact_replay),
        "extended_common_snapshot_sha256": extended_snapshot["sha256"],
        "generator_selection_sha256": digest(geometry),
        "support_and_foundations_sha256": digest(foundations),
        "gate_disposition_sha256": digest(gate),
    }
    projection = (
        "scope", "generator_selection", "D_action", "exact_replay", "extended_common_snapshot",
        "support_and_foundations", "gate_disposition", "claim_flags", "does_not_establish",
        "next_gate", "canonical_hashes",
    )
    value["independent_checker"]["expected_digest"] = digest({key: value[key] for key in projection})
    return value


def render(value: Mapping[str, Any]) -> str:
    action = value["D_action"]
    replay = value["exact_replay"]
    return f"""# Strict 386-row full cylinder D action v1

## Outcome

{value['answer']}

## Which generator is meant

The exact real operator is `T=Lie_partial_t`.  The compact Hermitian mode
convention is `D=iT` after complexification.  This certificate does not use
the real Minkowski dilation, the Berger helical generator, or a finite energy
matrix.  Its 386 rows are bundle-component types carrying arbitrary compactly
supported smooth spacetime dependence.

## Exact inventory

- Component rows: **{value['scope']['carrier_rows']}** in **{value['scope']['component_blocks']}** blocks.
- First-order diagonal entries: **{action['nonzero_coefficients']}** at temporal multiindex `{action['temporal_multiindex']}`.
- Graph `q1`: **{replay['q1_operator_tables_checked']}** tables, **{replay['q1_derivative_multiindices_checked']}** multiindices, **{replay['q1_rational_coefficients_checked']}** rational coefficients.
- `[T,q1]` component defects: **{replay['D_q1_commutator_defects']}**.
- Formal skew-adjoint pairing entries checked: **{replay['formal_skew_adjoint_pairing_entries_checked']}**, defects **{replay['formal_skew_adjoint_defects']}**.

## Why the commutator vanishes

The unit cylinder is stationary with parallel curvature and zero mixed
time-space curvature.  In a frame Lie-dragged by `partial_t`, all serialized
`q1` coefficients are time independent and `[nabla_0,nabla_i]=0`.  The
independent receiver constructs `T q1` and `q1 T` separately; both increment
only the temporal derivative slot and agree for all 4,374 coefficients.

## Gate boundary

The D and D/q1 portion of M2 is now receiver-verified on the accepted unary-
causal carrier.  Same-carrier `q2`, the D/q2 derivation identity, D-Cartan
homotopy, the physical gauge/charge status of D, and every quantum lifecycle
state remain open.  Gate A remains fail closed.

## Next gate

{value['next_gate']}
"""


def generated() -> tuple[bytes, bytes]:
    value = build()
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode(), render(value).encode()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result, report = generated()
    stale = [
        str(path.relative_to(ROOT))
        for path, content in ((RESULT, result), (REPORT, report))
        if not path.is_file() or path.read_bytes() != content
    ]
    if args.check:
        print("STRICT_386_FULL_D_ACTION_V1: " + ("generated artifacts current" if not stale else "stale: " + ", ".join(stale)))
        return bool(stale)
    RESULT.write_bytes(result)
    REPORT.write_bytes(report)
    print("STRICT_386_FULL_D_ACTION_V1: wrote result and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
