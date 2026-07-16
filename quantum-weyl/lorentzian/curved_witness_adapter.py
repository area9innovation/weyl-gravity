"""Exact adapter for the Berger curved clock-reattached witness export."""

from __future__ import annotations

import argparse
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any, Iterable

import sympy as sp

from transfer.berger_gauge_fixed_nonminimal_import import (
    _adjoint_transpose,
    _is_zero,
    _load_record,
    _matrix_add,
    _multiply,
    _subtract,
    _zero,
)
LORENTZIAN_ROOT = Path(__file__).resolve().parent
ROOT = LORENTZIAN_ROOT.parents[1]
CLASSICAL_COMMIT = "445e26663d06764bc858ff0a004ba6178acce75f"
SETTING_ID = "compact_positive_berger_clock_fixed_coupling_linearized"
EXPORT_SCHEMA_ID = "quantum-weyl-berger-curved-witness-export-v1"

MINIMAL_CERTIFICATE = "d_quotient_classical/certificates/BERGER_MINIMAL_34_PORTABLE_CONTRACTION.json"
RETAINED_CERTIFICATE = "d_quotient_classical/certificates/BERGER_RETAINED_MINIMAL_OPERATOR.json"
NONMINIMAL_CERTIFICATE = "d_quotient_classical/certificates/BERGER_NONMINIMAL_ALGEBRAIC_COMPLETION.json"
GAUGE_CERTIFICATE = "d_quotient_classical/certificates/BERGER_GAUGE_FIXED_NONMINIMAL_COMPLETION.json"
SOURCE_ARTIFACTS = (
    MINIMAL_CERTIFICATE,
    RETAINED_CERTIFICATE,
    NONMINIMAL_CERTIFICATE,
    GAUGE_CERTIFICATE,
    "d_quotient_classical/schema/berger-minimal-34-portable-contraction-v1.schema.json",
    "d_quotient_classical/schema/berger-nonminimal-algebraic-completion-v1.schema.json",
    "d_quotient_classical/schema/berger-gauge-fixed-nonminimal-completion-v1.schema.json",
    "d_quotient_classical/backreacted_clock/berger_minimal_34_portable_contraction.py",
    "d_quotient_classical/backreacted_clock/berger_nonminimal_algebraic_completion.py",
    "d_quotient_classical/backreacted_clock/verify_berger_nonminimal_algebraic_completion.py",
)

OperatorMatrix = list[list[dict[tuple[int, ...], sp.Expr]]]


@lru_cache(maxsize=1)
def _git_prefix() -> str:
    return subprocess.run(
        ["git", "rev-parse", "--show-prefix"], cwd=ROOT, check=True,
        capture_output=True, text=True,
    ).stdout.strip()


def _git_blob(relative: str) -> bytes:
    result = subprocess.run(
        ["git", "show", f"{CLASSICAL_COMMIT}:{_git_prefix()}{relative}"],
        cwd=ROOT, check=False, capture_output=True,
    )
    if result.returncode != 0:
        raise ValueError(f"missing pinned curved-witness artifact: {relative}")
    return result.stdout


def _git_json(relative: str) -> dict[str, Any]:
    value = json.loads(_git_blob(relative))
    if not isinstance(value, dict):
        raise ValueError(f"pinned JSON is not an object: {relative}")
    return value


def _artifact(relative: str) -> dict[str, str]:
    return {
        "path": relative,
        "commit": CLASSICAL_COMMIT,
        "sha256": hashlib.sha256(_git_blob(relative)).hexdigest(),
    }


def _canonical_hash(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _embed(target: OperatorMatrix, block: OperatorMatrix, row: int, column: int) -> None:
    for block_row, values in enumerate(block):
        for block_column, operator in enumerate(values):
            target[row + block_row][column + block_column] = operator


def _build_q34(minimal: dict[str, Any], retained: dict[str, Any]) -> OperatorMatrix:
    q34 = _zero(34, 34)
    blocks = retained["q1_blocks"]
    _embed(q34, _load_record("K_spatial", blocks["K_spatial"], (10, 3)), 5, 0)
    _embed(q34, _load_record("H_retained", blocks["H_retained"], (10, 10)), 17, 5)
    _embed(
        q34,
        _load_record("minus_K_spatial_sharp", blocks["minus_K_spatial_sharp"], (3, 10)),
        29,
        17,
    )
    clock = _load_record(
        "clock_extension", minimal["classical_unary_q1"]["clock_extension"], (34, 34)
    )
    return _matrix_add(q34, clock)


def _validate_source_boundaries(
    minimal: dict[str, Any], retained: dict[str, Any],
    nonminimal: dict[str, Any], gauge: dict[str, Any],
) -> dict[str, Any]:
    component_rows = minimal.get("row_layout", {}).get("component_rows", [])
    if (
        minimal.get("result_id") != "BERGER_MINIMAL_34_PORTABLE_CONTRACTION"
        or minimal.get("claim_status") != "CERTIFIED_COMPLETE_MINIMAL_UNARY_CONTRACTION"
        or minimal.get("row_layout", {}).get("degree_ranks") != [5, 12, 12, 5]
        or len(component_rows) != 34
        or [row.get("index") for row in component_rows] != list(range(34))
        or len({row.get("row_id") for row in component_rows}) != 34
        or minimal.get("flags", {}).get("BERGER_CURVED_CLOCK_REATTACHED_WITNESS") is not False
    ):
        raise ValueError("minimal 34-row source boundary drifted")
    if retained.get("result_id") != "BERGER_RETAINED_MINIMAL_OPERATOR":
        raise ValueError("retained q1 source boundary drifted")
    if (
        nonminimal.get("result_id") != "BERGER_NONMINIMAL_ALGEBRAIC_COMPLETION"
        or nonminimal.get("flags", {}).get("BERGER_CURVED_COMPANION_DERIVED") is not True
        or nonminimal.get("flags", {}).get("BERGER_CURVED_CLOCK_REATTACHED_WITNESS") is not False
    ):
        raise ValueError("curved companion source boundary drifted")
    if (
        gauge.get("result_id") != "BERGER_GAUGE_FIXED_NONMINIMAL_COMPLETION"
        or gauge.get("gauge_fermion", {}).get("support_local") is not True
        or gauge.get("flags", {}).get("BERGER_CAUSAL_GREEN_HOMOTOPY") is not False
    ):
        raise ValueError("raw-to-dressed source boundary drifted")

    companion = _load_record(
        "curved_companion",
        nonminimal["gauge_fermion_template"]["curved_companion"],
        (5, 10),
    )
    raw_from_dressed = _load_record(
        "raw_metric_from_dressed",
        gauge["gauge_fermion"]["raw_metric_from_dressed"],
        (10, 12),
    )
    gauge_condition = _load_record(
        "gauge_condition_A", gauge["gauge_fermion"]["gauge_condition_A"], (5, 12)
    )
    if not _is_zero(_subtract(_multiply(companion, raw_from_dressed), gauge_condition)):
        raise ValueError("raw-to-dressed companion transport failed")
    q34 = _build_q34(minimal, retained)
    if not _is_zero(_multiply(q34, q34)):
        raise ValueError("reconstructed q34 is not nilpotent")
    return {
        "q34": q34,
        "companion": companion,
        "raw_from_dressed": raw_from_dressed,
        "gauge_condition": gauge_condition,
        "component_rows": component_rows,
        "hashes": {
            "q34_sha256": _matrix_record(q34)["sha256"],
            "curved_companion_sha256": nonminimal["gauge_fermion_template"]["curved_companion"]["sha256"],
            "raw_metric_from_dressed_sha256": gauge["gauge_fermion"]["raw_metric_from_dressed"]["sha256"],
            "transported_gauge_condition_sha256": gauge["gauge_fermion"]["gauge_condition_A"]["sha256"],
            "row_layout_sha256": _canonical_hash(minimal["row_layout"]),
        },
    }


def _require_fields(value: object, expected: Iterable[str], label: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != set(expected):
        raise ValueError(f"{label} fields drifted")
    return value


def _load_artifact_record(
    value: object, *, repository_root: Path, name: str, shape: tuple[int, int]
) -> OperatorMatrix:
    artifact = _require_fields(value, ("format", "path", "sha256"), name)
    if artifact["format"] != "JSON_EXACT_SPARSE_OPERATOR":
        raise ValueError(f"{name} format drifted")
    path = (repository_root / artifact["path"]).resolve()
    try:
        path.relative_to(repository_root.resolve())
    except ValueError as exc:
        raise ValueError(f"{name} escapes repository root") from exc
    if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != artifact["sha256"]:
        raise ValueError(f"{name} artifact hash mismatch")
    payload = json.loads(path.read_text(encoding="utf-8"))
    return _load_record(name, payload, shape)


def _first_coefficient_obstruction(
    matrix: OperatorMatrix, *, defect_kind: str,
    component_rows: list[dict[str, Any]],
) -> dict[str, Any] | None:
    candidates = []
    for row, values in enumerate(matrix):
        for column, operator in enumerate(values):
            for word, coefficient in operator.items():
                if coefficient != 0:
                    candidates.append((-len(word), row, column, word, sp.factor(coefficient)))
    if not candidates:
        return None
    _, row, column, word, coefficient = min(candidates)
    exponents = [word.count(axis) for axis in range(4)]
    output_coordinate = component_rows[row]
    input_coordinate = component_rows[column]
    return {
        "defect_kind": defect_kind,
        "row": row,
        "column": column,
        "pbw_order": len(word),
        "D_weight": len(word),
        "derivative_exponents": exponents,
        "field_content": {
            "output_field": output_coordinate["row_id"],
            "output_degree": output_coordinate["degree"],
            "input_field": input_coordinate["row_id"],
            "input_degree": input_coordinate["degree"],
        },
        "coefficient": str(coefficient),
        "normalized_dual_functional": (
            f"coefficient_extraction(row={row},column={column},exponents={exponents})/({sp.sstr(coefficient)})"
        ),
        "dual_pairing_on_defect": "1",
    }


def _matrix_record(matrix: OperatorMatrix) -> dict[str, Any]:
    entries = []
    for row, values in enumerate(matrix):
        for column, operator in enumerate(values):
            if operator:
                terms = []
                for word, coefficient in sorted(operator.items(), key=lambda item: (len(item[0]), item[0])):
                    terms.append([[word.count(axis) for axis in range(4)], str(sp.factor(coefficient))])
                entries.append([row, column, terms])
    body = {"shape": [len(matrix), len(matrix[0])], "entries": entries}
    return {**body, "sha256": hashlib.sha256(
        json.dumps(body, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()}


def evaluate_curved_witness_export(
    payload: object, *, repository_root: Path,
    source_data: dict[str, Any] | None = None,
) -> dict[str, Any]:
    record = _require_fields(
        payload,
        (
            "schema", "result_id", "result_state", "classical_commit",
            "dependency_tags", "setting_id", "row_layout", "operators",
            "coordinate_transport", "claim_boundary",
        ),
        "curved witness export",
    )
    if (
        record["schema"] != EXPORT_SCHEMA_ID
        or record["result_id"] != "BERGER_CURVED_CLOCK_REATTACHED_WITNESS"
        or record["result_state"] != "CURVED_WITNESS_CANDIDATE"
        or record["dependency_tags"] != ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"]
        or record["setting_id"] != SETTING_ID
        or record["row_layout"] != {"degree_ranks": [5, 12, 12, 5], "total_rows": 34}
        or not isinstance(record["claim_boundary"], str)
        or not record["claim_boundary"]
    ):
        raise ValueError("curved witness export identity or layout drifted")
    commit = record["classical_commit"]
    if not isinstance(commit, str) or len(commit) != 40 or any(
        character not in "0123456789abcdef" for character in commit
    ):
        raise ValueError("curved witness classical commit is invalid")
    transport = _require_fields(
        record["coordinate_transport"],
        (
            "curved_companion_sha256",
            "raw_metric_from_dressed_sha256",
            "transported_gauge_condition_sha256",
            "row_layout_sha256",
            "q34_sha256",
        ),
        "coordinate transport",
    )
    if source_data is None:
        source_data = _validate_source_boundaries(
            _git_json(MINIMAL_CERTIFICATE), _git_json(RETAINED_CERTIFICATE),
            _git_json(NONMINIMAL_CERTIFICATE), _git_json(GAUGE_CERTIFICATE),
        )
    if transport != source_data["hashes"]:
        raise ValueError("coordinate transport hashes drifted")
    result_context = {
        "classical_commit": commit,
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "setting_id": SETTING_ID,
    }
    operators = _require_fields(record["operators"], ("P34", "W34", "pairing34"), "operators")
    witness = _load_artifact_record(
        operators["W34"], repository_root=repository_root, name="W34", shape=(34, 34)
    )
    target = _load_artifact_record(
        operators["P34"], repository_root=repository_root, name="P34", shape=(34, 34)
    )
    pairing = _load_artifact_record(
        operators["pairing34"], repository_root=repository_root,
        name="pairing34", shape=(34, 34),
    )
    q34 = source_data["q34"]
    pairing_numeric = sp.zeros(34)
    for row in range(34):
        for column in range(34):
            if any(word for word in pairing[row][column]):
                raise ValueError("pairing34 is not an order-zero fibre pairing")
            pairing_numeric[row, column] = sum(pairing[row][column].values(), sp.S.Zero)
    if pairing_numeric.det() == 0:
        raise ValueError("pairing34 is degenerate")
    q_cyclic_defect = _matrix_add(
        _multiply(_adjoint_transpose(q34), pairing), _multiply(pairing, q34)
    )
    obstruction = _first_coefficient_obstruction(
        q_cyclic_defect,
        defect_kind="Q34_CYCLICITY",
        component_rows=source_data["component_rows"],
    )
    if obstruction is not None:
        return {
            **result_context,
            "verdict": "NONTRIVIAL_NORMALIZED_COEFFICIENT_OBSTRUCTION",
            "exact_primitive": None,
            "obstruction_witness": obstruction,
            "obstruction_scope": "SUBMITTED_CANDIDATE_ONLY_NOT_GLOBAL_NONEXISTENCE",
            "curved_witness_certified": False,
            "green_execution_authorized": False,
        }
    defect = _subtract(_matrix_add(_multiply(q34, witness), _multiply(witness, q34)), target)
    obstruction = _first_coefficient_obstruction(
        defect,
        defect_kind="QW_PLUS_WQ_MINUS_P",
        component_rows=source_data["component_rows"],
    )
    if obstruction is None:
        cyclic_defect = _matrix_add(
            _multiply(_adjoint_transpose(witness), pairing), _multiply(pairing, witness)
        )
        obstruction = _first_coefficient_obstruction(
            cyclic_defect,
            defect_kind="W34_CYCLICITY",
            component_rows=source_data["component_rows"],
        )
    if obstruction is not None:
        return {
            **result_context,
            "verdict": "NONTRIVIAL_NORMALIZED_COEFFICIENT_OBSTRUCTION",
            "exact_primitive": None,
            "obstruction_witness": obstruction,
            "obstruction_scope": "SUBMITTED_CANDIDATE_ONLY_NOT_GLOBAL_NONEXISTENCE",
            "curved_witness_certified": False,
            "green_execution_authorized": False,
        }
    return {
        **result_context,
        "verdict": "ADMISSIBLE_EXACT_CURVED_WITNESS",
        "exact_primitive": {
            "W34_sha256": operators["W34"]["sha256"],
            "P34_sha256": operators["P34"]["sha256"],
            "pairing34_sha256": operators["pairing34"]["sha256"],
        },
        "obstruction_witness": None,
        "obstruction_scope": None,
        "curved_witness_certified": True,
        "green_execution_authorized": False,
    }


def build_readiness_receipt() -> dict[str, Any]:
    minimal = _git_json(MINIMAL_CERTIFICATE)
    retained = _git_json(RETAINED_CERTIFICATE)
    nonminimal = _git_json(NONMINIMAL_CERTIFICATE)
    gauge = _git_json(GAUGE_CERTIFICATE)
    source = _validate_source_boundaries(minimal, retained, nonminimal, gauge)
    return {
        "schema": "quantum-weyl-berger-curved-witness-adapter-v1",
        "result_id": "BERGER_CURVED_CLOCK_REATTACHED_WITNESS_ADAPTER",
        "result_state": "CONSUMER_READY_AUTHORITATIVE_W34_INPUT_BLOCKED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "setting_id": SETTING_ID,
        "accepted_export_schema": EXPORT_SCHEMA_ID,
        "available_exact_input": {
            "minimal_34_unary_complex": "RECONSTRUCTED_AND_NILPOTENT",
            "curved_companion_5x10": "IMPORTED",
            "raw_to_dressed_map_10x12": "IMPORTED",
            "transported_gauge_condition_5x12": "IMPORTED",
            "coordinate_transport_identity": "T_raw o raw_from_dressed = A_dressed",
            "operator_hashes": source["hashes"],
        },
        "missing_object_ledger": {
            "W34": "NOT_EXPORTED",
            "P34": "NOT_EXPORTED",
            "pairing34": "NOT_EXPORTED_AS_PORTABLE_OPERATOR_RECORD",
        },
        "verdict": "INPUT_BLOCKED",
        "scientific_fixture_policy": "MECHANICS_FIXTURES_DO_NOT_SUBSTITUTE_FOR_PHYSICAL_EXPORT",
        "curved_witness_certified": False,
        "green_execution_authorized": False,
        "next_gate": "IMPORT_AUTHORITATIVE_W34_P34_PAIRING34",
        "provenance": {
            "classical_commit": CLASSICAL_COMMIT,
            "artifacts": [_artifact(path) for path in SOURCE_ARTIFACTS],
        },
        "claim_boundary": (
            "The exact companion transport and 34-row unary consumer are ready. The "
            "authoritative source has not exported W34, its target P34, or a portable "
            "pairing34 record, so no physical curved-witness verdict or causal Green "
            "claim is made."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--repository-root", type=Path, default=ROOT)
    args = parser.parse_args()
    payload = json.loads(args.input.read_text(encoding="utf-8"))
    verdict = evaluate_curved_witness_export(
        payload,
        repository_root=args.repository_root.resolve(),
    )
    print(json.dumps(verdict, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
