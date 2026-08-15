#!/usr/bin/env python3
"""Serialize the strict 386-row hybrid basis and odd BV pairing exactly."""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/STRICT_386_COMPONENT_PAIRING_SERIALIZATION_V1.json"
REPORT = HERE / "REPORT_STRICT_386_COMPONENT_PAIRING_SERIALIZATION_V1.md"

CYCLIC = HERE / "certificates/STRICT_MINIMAL_BV_CYCLIC_SIGN_RECONCILIATION_V1.json"
ENDPOINT = HERE / "certificates/STRICT_386_ENDPOINT_Q1_CONTENT_BRIDGE_V1.json"
SUSPENSION = HERE / "certificates/STRICT_386_SUSPENDED_ADJOINT_BRIDGE_V1.json"
GENERALIZED = ROOT / "covariant_completion/certificates/generalized_auxiliary_contraction.json"
ORDINARY = ROOT / "covariant_completion/certificates/ordinary_derivative_auxiliary_system.json"
HYBRID = ROOT / "covariant_completion/certificates/curved_prolonged_hybrid_algebraic_projector.json"
MAPPING = ROOT / "covariant_completion/certificates/curved_curvature_mapping_cylinder_substitution.json"
MAPPING_KERNEL = ROOT / "covariant_completion/certificates/curved_curvature_mapping_cylinder_kernel.json"
ORDINARY_SOURCE = ROOT / "covariant_completion/auxiliary_witness/ordinary_derivative.py"

PAIRS = ((0, 0), (0, 1), (0, 2), (0, 3), (1, 1), (1, 2), (1, 3), (2, 2), (2, 3), (3, 3))
METRIC = (-1, 1, 1, 1)
CONE_BLOCKS = (
    ("X_U", 26, 0), ("X_Eq", 40, 1), ("X_Id", 14, 2),
    ("Y_U", 26, 1), ("Y_Eq", 40, 2), ("Y_Id", 14, 3),
    ("X_Id_sharp", 14, -1), ("X_Eq_sharp", 40, 0), ("X_U_sharp", 26, 1),
    ("Y_Id_sharp", 14, -2), ("Y_Eq_sharp", 40, -1), ("Y_U_sharp", 26, 0),
)
CONE_PAIRS = (
    ("X_U", "X_U_sharp", 1), ("X_Eq", "X_Eq_sharp", -1),
    ("X_Id", "X_Id_sharp", -1), ("Y_U", "Y_U_sharp", -1),
    ("Y_Eq", "Y_Eq_sharp", -1), ("Y_Id", "Y_Id_sharp", 1),
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def q(value: Fraction | int) -> str:
    value = Fraction(value)
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def exact_rank(matrix: list[list[Fraction]]) -> int:
    work = [row[:] for row in matrix]
    rows = len(work)
    columns = len(work[0]) if rows else 0
    rank = 0
    for column in range(columns):
        pivot = next((row for row in range(rank, rows) if work[row][column]), None)
        if pivot is None:
            continue
        work[rank], work[pivot] = work[pivot], work[rank]
        scale = work[rank][column]
        work[rank] = [entry / scale for entry in work[rank]]
        for row in range(rows):
            coefficient = work[row][column]
            if row != rank and coefficient:
                work[row] = [entry - coefficient * pivot_entry for entry, pivot_entry in zip(work[row], work[rank], strict=True)]
        rank += 1
        if rank == rows:
            break
    return rank


def half_dewitt() -> list[list[Fraction]]:
    basis: list[list[list[int]]] = []
    for mu, nu in PAIRS:
        tensor = [[0] * 4 for _ in range(4)]
        tensor[mu][nu] = tensor[nu][mu] = 1
        basis.append(tensor)
    tensor_pairing: list[list[int]] = []
    traces: list[int] = []
    for left in basis:
        traces.append(sum(METRIC[a] * left[a][a] for a in range(4)))
        row: list[int] = []
        for right in basis:
            row.append(sum(METRIC[a] * METRIC[b] * left[a][b] * right[b][a] for a in range(4) for b in range(4)))
        tensor_pairing.append(row)
    return [[Fraction(tensor_pairing[row][column], 2) - Fraction(traces[row] * traces[column], 4) for column in range(10)] for row in range(10)]


def add_rows() -> tuple[list[dict[str, Any]], dict[str, list[int]]]:
    rows: list[dict[str, Any]] = []
    blocks: dict[str, list[int]] = {}

    def block(name: str, labels: Iterable[str], degree: int, sector: str, basis: str) -> None:
        indices: list[int] = []
        for local, label in enumerate(labels):
            index = len(rows)
            indices.append(index)
            rows.append({"index": index, "row_id": label, "block": name, "local_index": local, "degree": degree, "sector": sector, "basis_source": basis})
        blocks[name] = indices

    tensor = [f"{a}{b}" for a, b in PAIRS]
    block("ENDPOINT_G", [*(f"c_{a}" for a in range(4)), "omega"], -1, "CAUSAL_ENDPOINT_30", "Gate-canonical minimal basis")
    block("ENDPOINT_M", (f"h_{name}" for name in tensor), 0, "CAUSAL_ENDPOINT_30", "Gate-canonical minimal basis")
    block("ENDPOINT_E", (f"h_star_{name}" for name in tensor), 1, "CAUSAL_ENDPOINT_30", "Gate-canonical minimal basis")
    block("ENDPOINT_I", [*(f"c_star_{a}" for a in range(4)), "omega_star"], 2, "CAUSAL_ENDPOINT_30", "Gate-canonical minimal basis")

    block("AUX_ETA", (f"eta_{a}" for a in range(4)), -1, "ALGEBRAIC_COMPLEMENT_36", "ordered generalized-auxiliary split")
    block("AUX_F_HAT", (f"f_hat_{name}" for name in tensor), 0, "ALGEBRAIC_COMPLEMENT_36", "ordered generalized-auxiliary split")
    block("AUX_V", (f"v_{a}" for a in range(4)), 0, "ALGEBRAIC_COMPLEMENT_36", "ordered generalized-auxiliary split")
    block("AUX_F_HAT_STAR", (f"f_hat_star_{name}" for name in tensor), 1, "ALGEBRAIC_COMPLEMENT_36", "ordered generalized-auxiliary split")
    block("AUX_V_STAR", (f"v_star_{a}" for a in range(4)), 1, "ALGEBRAIC_COMPLEMENT_36", "ordered generalized-auxiliary split")
    block("AUX_ETA_STAR", (f"eta_star_{a}" for a in range(4)), 2, "ALGEBRAIC_COMPLEMENT_36", "ordered generalized-auxiliary split")

    for name, dimension, degree in CONE_BLOCKS:
        block("CONE_" + name.upper(), (f"{name}[{index}]" for index in range(dimension)), degree, "ALGEBRAIC_COMPLEMENT_320", "split curvature mapping-cylinder basis")
    if len(rows) != 386:
        raise ValueError("hybrid row count drift")
    return rows, blocks


def add_entry(entries: list[dict[str, Any]], rows: list[dict[str, Any]], left: int, right: int, coefficient: Fraction | int, source: str) -> None:
    if coefficient:
        entries.append({"left_index": left, "right_index": right, "left": rows[left]["row_id"], "right": rows[right]["row_id"], "coefficient": q(coefficient), "source": source})


def build_pairing(rows: list[dict[str, Any]], blocks: dict[str, list[int]], cyclic: dict[str, Any]) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    by_label = {row["row_id"]: row["index"] for row in rows[:30]}
    for item in cyclic["canonical_pairing"]["entries"]:
        add_entry(entries, rows, by_label[item["left"]], by_label[item["right"]], Fraction(item["coefficient"]), "Gate endpoint canonical odd pairing")

    for local, sign in enumerate((1, -1, -1, -1)):
        left, right = blocks["AUX_ETA"][local], blocks["AUX_ETA_STAR"][local]
        add_entry(entries, rows, left, right, sign, "Y_aux=-metric on eta/eta_star")
        add_entry(entries, rows, right, left, -sign, "odd reverse orientation")
    de_witt = half_dewitt()
    if exact_rank(de_witt) != 10:
        raise ValueError("DeWitt auxiliary pairing lost rank")
    for left_local, matrix_row in enumerate(de_witt):
        for right_local, coefficient in enumerate(matrix_row):
            left, right = blocks["AUX_F_HAT"][left_local], blocks["AUX_F_HAT_STAR"][right_local]
            add_entry(entries, rows, left, right, coefficient, "J_aux half-DeWitt f_hat/f_hat_star block")
            add_entry(entries, rows, right, left, -coefficient, "odd reverse orientation")
    for local, sign in enumerate(METRIC):
        left, right = blocks["AUX_V"][local], blocks["AUX_V_STAR"][local]
        add_entry(entries, rows, left, right, sign, "J_aux metric v/v_star block")
        add_entry(entries, rows, right, left, -sign, "odd reverse orientation")

    for left_name, right_name, sign in CONE_PAIRS:
        left_block = blocks["CONE_" + left_name.upper()]
        right_block = blocks["CONE_" + right_name.upper()]
        for left, right in zip(left_block, right_block, strict=True):
            add_entry(entries, rows, left, right, sign, "mapping-cylinder odd incidence pairing")
            add_entry(entries, rows, right, left, -sign, "odd reverse orientation")
    return sorted(entries, key=lambda item: (item["left_index"], item["right_index"]))


INPUTS = (
    (CYCLIC, "STRICT_MINIMAL_BV_CYCLIC_SIGN_RECONCILIATION_V1", "thirty-row Gate endpoint pairing"),
    (ENDPOINT, "STRICT_386_ENDPOINT_Q1_CONTENT_BRIDGE_V1", "exact Gate-to-endpoint basis bridge"),
    (SUSPENSION, "STRICT_386_SUSPENDED_ADJOINT_BRIDGE_V1", "suspension character and projector-level Green theorem"),
    (GENERALIZED, "pure-weyl-support-local-generalized-auxiliary-retract-v1", "ordered 30+36 generalized-auxiliary split"),
    (ORDINARY, "pure-weyl-ordinary-derivative-auxiliary-system-v2", "J_aux and Y_aux normalization hashes"),
    (HYBRID, "pure-weyl-prolonged-hybrid-algebraic-projector-v1", "orthogonal 356+30 projector split"),
    (MAPPING_KERNEL, "pure-weyl-curvature-mapping-cylinder-kernel-v1", "component degrees and certified odd-incidence pairing signs"),
    (MAPPING, "pure-weyl-curvature-mapping-cylinder-substitution-v1", "complete sixteen-block mapping-cylinder order"),
)


def build() -> dict[str, Any]:
    values = {path: json.loads(path.read_text()) for path, _, _ in INPUTS}
    for path, expected, _ in INPUTS:
        actual = values[path].get("result_id") or values[path].get("schema")
        if actual != expected:
            raise ValueError(f"dependency identity drift: {path}")
    cyclic, endpoint, suspension, generalized, ordinary, hybrid, mapping_kernel, mapping = (values[path] for path, _, _ in INPUTS)
    if generalized["sdr"]["contractible_dimension"] != 36 or hybrid["minimal_dimension_ledger"]["algebraically_contracted"] != 356:
        raise ValueError("algebraic-complement dimension drift")
    if mapping["kernel"]["row_coverage"]["rows_enumerated"] != 16 or not mapping["coefficientwise_complete_prolonged_Q"]:
        raise ValueError("mapping-cylinder row authority unavailable")
    cone_ledger = {
        item["block"]: item["degree"]
        for item in mapping_kernel["complete_16_block_degree_ledger"][4:]
    }
    if cone_ledger != {name: degree for name, _, degree in CONE_BLOCKS}:
        raise ValueError("mapping-cylinder component degree ledger drift")
    cyclicity = mapping_kernel["odd_BV_cyclicity"]
    cone_pairing_signs = [sign for _, _, sign in CONE_PAIRS]
    if cone_pairing_signs != cyclicity["pairing_epsilon_X"] + cyclicity["pairing_epsilon_Y"]:
        raise ValueError("mapping-cylinder incidence pairing signs drift")
    if suspension["full_carrier_extension"]["R_386_negative"] != 10:
        raise ValueError("suspension predecessor drift")

    rows, blocks = add_rows()
    entries = build_pairing(rows, blocks, cyclic)
    sector_counts = {
        sector: sum(item["sector"] == sector for item in rows)
        for sector in ("CAUSAL_ENDPOINT_30", "ALGEBRAIC_COMPLEMENT_36", "ALGEBRAIC_COMPLEMENT_320")
    }
    entry_sector_counts = {
        "endpoint": sum(item["left_index"] < 30 for item in entries),
        "auxiliary_complement": sum(30 <= item["left_index"] < 66 for item in entries),
        "mapping_cone_complement": sum(item["left_index"] >= 66 for item in entries),
    }
    if sector_counts != {"CAUSAL_ENDPOINT_30": 30, "ALGEBRAIC_COMPLEMENT_36": 36, "ALGEBRAIC_COMPLEMENT_320": 320}:
        raise ValueError("sector closure drift")
    if entry_sector_counts != {"endpoint": 30, "auxiliary_complement": 60, "mapping_cone_complement": 320} or len(entries) != 410:
        raise ValueError("pairing entry count drift")
    entry_map = {(item["left_index"], item["right_index"]): Fraction(item["coefficient"]) for item in entries}
    if any(entry_map.get((right, left)) != -coefficient for (left, right), coefficient in entry_map.items()):
        raise ValueError("odd skew orientation drift")
    if any(rows[left]["degree"] + rows[right]["degree"] != 1 for left, right in entry_map):
        raise ValueError("pairing degree drift")
    pairing_matrix = [[Fraction(0) for _ in rows] for _ in rows]
    for (left, right), coefficient in entry_map.items():
        pairing_matrix[left][right] = coefficient
    pairing_rank = exact_rank(pairing_matrix)
    if pairing_rank != 386:
        raise ValueError(f"full component pairing lost rank: {pairing_rank}")

    t = [-1 if row["block"] == "ENDPOINT_I" else 1 for row in rows]
    t_sharp = [-1 if row["block"] == "ENDPOINT_G" else 1 for row in rows]
    r = [left * right for left, right in zip(t_sharp, t, strict=True)]
    if any(t[left] != t_sharp[right] for left, right in entry_map):
        raise ValueError("componentwise T adjoint relation drift")

    degree_counts = {str(degree): sum(row["degree"] == degree for row in rows) for degree in range(-2, 4)}
    pairing = {
        "kind": "EXACT_COMPONENT_ODD_BV_PAIRING_IN_HYBRID_GATE_BASIS",
        "degree": -1,
        "rank": pairing_rank,
        "nonzero_ordered_entry_count": len(entries),
        "sector_nonzero_ordered_entry_counts": entry_sector_counts,
        "entries": entries,
    }
    component_basis = {
        "ordering": "Gate endpoint 30; ordered generalized-auxiliary complement 36; split mapping-cylinder complement 320",
        "dimension": len(rows),
        "endpoint_dimension": 30,
        "algebraic_complement_dimension": 356,
        "algebraic_complement_split": "356=36+320",
        "sector_counts": sector_counts,
        "degree_counts": degree_counts,
        "rows": rows,
    }
    suspension_serialization = {
        "T_diagonal": t,
        "T_positive": t.count(1),
        "T_negative": t.count(-1),
        "T_sharp_gate_diagonal": t_sharp,
        "T_sharp_gate_positive": t_sharp.count(1),
        "T_sharp_gate_negative": t_sharp.count(-1),
        "R_diagonal": r,
        "R_positive": r.count(1),
        "R_negative": r.count(-1),
        "componentwise_T_adjoint_relation_replayed": True,
        "R_equals_T_sharp_T_componentwise": True,
    }
    value: dict[str, Any] = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "schema": "strict-386-component-pairing-serialization-v1",
        "result_id": "STRICT_386_COMPONENT_PAIRING_SERIALIZATION_V1",
        "result_kind": "SAME_THEORY_FULL_COMPONENT_BASIS_AND_ODD_PAIRING_SERIALIZATION",
        "result_state": "FULL_386_COMPONENT_BASIS_AND_PAIRING_SERIALIZED_OPERATOR_ADJOINT_BYTES_OPEN",
        "lifecycle": "CLASSIFIED",
        "created": "2026-08-15",
        "repository_base_commit": "7066e14d17bb37e6ad8dacdc10726dbb830ebec4",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "question": "Can the abstract cyclic 356+30 split be turned into one explicit 386-component hybrid Gate basis with a complete exact odd pairing table, without pretending that the full q1, Green, D or q2 operator coefficient tables have also been serialized?",
        "answer": "Yes. The retained thirty rows use the already certified Gate-canonical minimal basis. The algebraic complement is the direct sum of the exact thirty-six-row generalized-auxiliary doublet basis and all 320 split mapping-cylinder cone/cotangent rows. This gives 386 unique component records with degree, sector, block and local index. The Gate endpoint contributes 30 nonzero ordered pairing entries, the auxiliary complement contributes 60 exact rational entries from -metric, one-half DeWitt and metric blocks, and the cone complement contributes 320 signed incidence entries, for 410 entries and exact rank 386. The table is odd skew and every entry has total component degree one. On these same rows the suspension diagonals T, T^sharp_G and R are serialized and the componentwise identity T^T Omega=Omega T^sharp_G replays, giving the certified 381/5, 381/5 and 376/10 sign counts. This closes the missing component-basis and pairing-table object. It does not serialize the full prolonged q1, H_alg, endpoint inclusion/projection or advanced/retarded Green coefficient tables, so a component-by-component operator adjoint replay and one accepted common Gate-A snapshot hash remain open. Local D, q2, Hadamard and QME are not promoted.",
        "scope": {"theory": "strict pure-Weyl unary BV complex", "background": "unit conformal cylinder", "basis": "hybrid Gate endpoint plus exact split algebraic complement", "arithmetic": "finite exact rational component tables", "full_dimension": 386},
        "terminology_reconciliation": {
            "suspension_v1_field": "endpoint_exact_algebra.gate_pairing_nonzero_entries",
            "suspension_v1_value": 54,
            "precise_meaning": "nonzero entries of the unpulled-back endpoint DeWitt/ghost pairing used to calculate T^sharp",
            "gate_coordinate_endpoint_pairing_nonzero_entries": 30,
            "consequence": "The earlier 54 count was a coordinate-label imprecision, not an algebraic error; T^sharp and R are unchanged after exact Gate pullback.",
        },
        "component_basis": component_basis,
        "pairing_serialization": pairing,
        "suspension_serialization": suspension_serialization,
        "operator_adjoint_disposition": {
            "projector_level_suspended_green_adjoint_replayed": True,
            "componentwise_T_pairing_adjoint_replayed": True,
            "full_q1_component_table_serialized": False,
            "full_H_alg_component_table_serialized": False,
            "full_endpoint_inclusion_projection_component_tables_serialized": False,
            "full_advanced_retarded_green_component_tables_serialized": False,
            "every_component_operator_adjoint_replayed": False,
        },
        "foundational_strength": {"finite_serialization_base": "PRA", "choice_operation_added": False, "infinite_selection_added": False, "weakest_base_for_imported_analytic_causal_theorem": "NOT_ESTABLISHED"},
        "gate_disposition": {"full_386_component_basis_serialized": True, "full_386_component_pairing_serialized": True, "one_common_operator_snapshot_hash_accepted": False, "classical_import_gate_a_status": "FAIL_CLOSED", "q2_d_same_carrier_established": False},
        "claim_flags": {
            "STRICT_386_COMPONENT_BASIS_SERIALIZED": True,
            "STRICT_386_COMPONENT_PAIRING_SERIALIZED_IN_GATE_CONVENTION": True,
            "STRICT_386_COMPONENTWISE_T_ADJOINT_REPLAYED": True,
            "STRICT_386_ALL_OPERATOR_COMPONENT_ADJOINTS_REPLAYED": False,
            "STRICT_386_LOCAL_D_CERTIFIED": False,
            "STRICT_386_Q2_GREEN_COMPATIBILITY_CERTIFIED": False,
            "CLASSICAL_IMPORT_GATE_PASSED": False,
            "HADAMARD_STATE_CONSTRUCTED": False,
            "QME_RESTORED": False,
            "LORENTZIAN_QUANTUM_THEORY": False,
        },
        "does_not_establish": [
            "a serialized full prolonged q1 coefficient table in the hybrid basis",
            "serialized H_alg, endpoint inclusion/projection or advanced/retarded Green operator coefficients",
            "a component-by-component replay of every q1, projector and Green adjoint identity",
            "one accepted common Gate-A operator snapshot hash or a passed classical import gate",
            "local D or q2 compatibility on the common causal carrier",
            "a Hadamard state, Ward theorem, positivity result, renormalized Lorentzian products, QME restoration, residual transfer or Lorentzian quantum theory",
        ],
        "next_gate": "Serialize the full prolonged q1, H_alg, endpoint inclusion/projection and advanced/retarded Green coefficient tables in this exact 386-row hybrid basis, then independently replay every component adjoint and homotopy identity before introducing local D or q2.",
        "canonical_hashes": {},
        "provenance": {"inputs": [{"path": str(path.relative_to(ROOT)), "result_or_schema_id": expected, "sha256": sha(path), "role": role} for path, expected, role in INPUTS] + [{"path": str(ORDINARY_SOURCE.relative_to(ROOT)), "result_or_schema_id": "ORDINARY_AUXILIARY_PAIRING_SOURCE_FORMULAE", "sha256": sha(ORDINARY_SOURCE), "role": "explicit -metric, half-DeWitt and metric component formulae"}]},
        "independent_checker": {"path": "quantum-weyl/classical_import/check_strict_386_component_pairing_serialization.py", "expected_digest": ""},
        "human_report": "quantum-weyl/classical_import/REPORT_STRICT_386_COMPONENT_PAIRING_SERIALIZATION_V1.md",
    }
    value["canonical_hashes"] = {"component_basis_sha256": digest(component_basis), "pairing_serialization_sha256": digest(pairing), "suspension_serialization_sha256": digest(suspension_serialization)}
    projection = {key: value[key] for key in ("scope", "terminology_reconciliation", "component_basis", "pairing_serialization", "suspension_serialization", "operator_adjoint_disposition", "foundational_strength", "gate_disposition", "claim_flags", "does_not_establish", "next_gate", "canonical_hashes")}
    value["independent_checker"]["expected_digest"] = digest(projection)
    return value


def render(value: dict[str, Any]) -> str:
    basis = value["component_basis"]
    pairing = value["pairing_serialization"]
    signs = value["suspension_serialization"]
    return f"""# Strict 386-row component pairing serialization v1

## Outcome

{value['answer']}

## Exact carrier inventory

- Endpoint: **{basis['endpoint_dimension']}** Gate-canonical rows.
- Generalized-auxiliary complement: **36** rows.
- Mapping-cylinder cone/cotangent complement: **320** rows.
- Total: **386** rows, with the algebraic complement split `356=36+320`.

## Exact pairing

The serialized odd pairing has **{pairing['nonzero_ordered_entry_count']}**
nonzero ordered rational entries and exact rank **{pairing['rank']}**:

- Gate endpoint: **30** entries;
- generalized-auxiliary complement: **60** entries;
- mapping-cylinder complement: **320** entries.

Every entry has total component degree one and its reverse entry has the
negative coefficient.  The componentwise relation `T^T Omega=Omega T^sharp_G`
replays.  The sign ledgers are `T: {signs['T_positive']}+/{signs['T_negative']}-`,
`T^sharp_G: {signs['T_sharp_gate_positive']}+/{signs['T_sharp_gate_negative']}-`,
and `R: {signs['R_positive']}+/{signs['R_negative']}-`.

## Coordinate clarification

The earlier count 54 is the nonzero count of the endpoint DeWitt/ghost pairing
before the exact Gate pullback.  In Gate component coordinates the endpoint
pairing has 30 nonzero ordered entries.  This changes no suspension algebra:
`T^sharp_G` and `R=T^sharp_G T` are the same.

## Remaining operator gate

The basis and pairing are now bytes.  The full prolonged `q1`, `H_alg`,
endpoint inclusion/projection and advanced/retarded Green operators are not
yet component tables in this hybrid basis.  Consequently the projector-level
Green theorem remains valid, but an independent component-by-component replay
of every operator adjoint is still open.

## Does not establish

""" + "\n".join(f"- {item}" for item in value["does_not_establish"]) + f"""

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
    stale = [str(path.relative_to(ROOT)) for path, content in ((RESULT, result), (REPORT, report)) if not path.is_file() or path.read_bytes() != content]
    if args.check:
        print("STRICT_386_COMPONENT_PAIRING_SERIALIZATION_V1: " + ("generated artifacts current" if not stale else "stale: " + ", ".join(stale)))
        return bool(stale)
    RESULT.write_bytes(result)
    REPORT.write_bytes(report)
    print("STRICT_386_COMPONENT_PAIRING_SERIALIZATION_V1: wrote result and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
