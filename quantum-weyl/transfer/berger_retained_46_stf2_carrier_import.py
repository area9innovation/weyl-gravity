"""Pinned independent import of the retained rank-46 STF2 graph carrier.

The classical handoff exports eight sparse PBW operator records over
``Q(sqrt(10))``.  This consumer reads them from the pinned classical commit
and independently replays the graph-SDR, cyclicity, locality, and STF2
right-inverse identities.  It never imports or executes the classical
producer.

The accepted object is a support-local cyclic carrier.  It is deliberately
not interpreted as an Einstein-like/extra-Weyl branch projector.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
from copy import deepcopy
from dataclasses import dataclass
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import re
import subprocess
from typing import Any, Mapping

import sympy as sp
from jsonschema import Draft202012Validator

from . import berger_qsqrt10_replay as q10


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CLASSICAL_COMMIT = "01ca7ba534fbd87f860cd57cf8a5f07603585989"
CLASSICAL_CERTIFICATE = "d_quotient_classical/certificates/BERGER_RETAINED_46_STF2_PROLONGATION_BRANCH_CARRIER_V1.json"
CLASSICAL_SCHEMA = "d_quotient_classical/schema/berger-retained-46-stf2-prolongation-branch-carrier-v1.schema.json"
TYPED_36 = "d_quotient_classical/certificates/BERGER_PORTABLE_COUPLED_64_TYPED_PAIRING_36_SDR.json"
CLASSICAL_PRODUCER = "d_quotient_classical/backreacted_clock/berger_retained_46_stf2_prolongation_branch_carrier.py"
CLASSICAL_VERIFIER = "d_quotient_classical/backreacted_clock/verify_berger_retained_46_stf2_prolongation_branch_carrier.py"
CLASSICAL_TEST = "d_quotient_classical/backreacted_clock/tests/test_berger_retained_46_stf2_prolongation_branch_carrier.py"
CLASSICAL_REPORT = "d_quotient_classical/reports/berger-retained-46-stf2-prolongation-branch-carrier.md"

SCHEMA = HERE / "schema/berger-retained-46-stf2-carrier-import-v1.schema.json"
OUTPUT = HERE / "certificates/BERGER_RETAINED_46_STF2_CARRIER_IMPORT.json"
REPORT = ROOT / "quantum-weyl/reports/berger-retained-46-stf2-carrier-import.md"
SOURCE_PATHS = (
    "quantum-weyl/transfer/berger_retained_46_stf2_carrier_import.py",
    "quantum-weyl/transfer/verify_berger_retained_46_stf2_carrier_import.py",
    "quantum-weyl/transfer/schema/berger-retained-46-stf2-carrier-import-v1.schema.json",
    "quantum-weyl/transfer/tests/test_berger_retained_46_stf2_carrier_import.py",
    "quantum-weyl/reports/berger-retained-46-stf2-carrier-import.md",
)

EXPECTED_ARTIFACTS = {
    "q1_46": (46, 46),
    "omega_46": (46, 46),
    "iota_36_to_46": (46, 36),
    "pi_46_to_36": (36, 46),
    "S_46": (46, 46),
    "stf2_extractor_T": (5, 10),
    "stf2_right_inverse_J": (10, 5),
    "stf2_wave_F": (5, 10),
}
EXPECTED_CHECKS = {
    "q1_46_squared_zero",
    "omega_46_antisymmetric",
    "q1_46_typed_cyclic",
    "pi_iota_identity",
    "iota_chain_map",
    "pi_chain_map",
    "contraction_identity",
    "homotopy_square_zero",
    "homotopy_iota_zero",
    "pi_homotopy_zero",
    "homotopy_typed_cyclic",
    "pairing_induced_by_iota",
    "stf2_right_inverse",
    "stf2_wave_order_two",
}

Word = tuple[int, ...]
Key = tuple[int, int, Word]


@dataclass(frozen=True)
class SparseOperator:
    shape: tuple[int, int]
    terms: Mapping[Key, q10.Q10]


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha256(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _canonical_hash(value: object) -> str:
    return _sha256_bytes(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    )


@lru_cache(maxsize=1)
def _git_prefix() -> str:
    return subprocess.run(
        ["git", "rev-parse", "--show-prefix"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def _git_blob(relative: str) -> bytes:
    result = subprocess.run(
        ["git", "show", f"{CLASSICAL_COMMIT}:{_git_prefix()}{relative}"],
        cwd=ROOT,
        check=False,
        capture_output=True,
    )
    if result.returncode != 0:
        raise ValueError(f"missing pinned rank-46 artifact: {relative}")
    return result.stdout


def _git_json(relative: str) -> dict[str, Any]:
    try:
        value = json.loads(_git_blob(relative))
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid pinned rank-46 JSON: {relative}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"pinned rank-46 JSON is not an object: {relative}")
    return value


def _artifact(relative: str) -> dict[str, str]:
    return {
        "path": relative,
        "commit": CLASSICAL_COMMIT,
        "sha256": _sha256_bytes(_git_blob(relative)),
    }


_COEFFICIENT_CHARS = re.compile(r"^[0-9A-Za-z_+*/() -]+$")
_TOKEN = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")


@lru_cache(maxsize=None)
def _coefficient(value: str) -> q10.Q10:
    if (
        not isinstance(value, str)
        or not value
        or _COEFFICIENT_CHARS.fullmatch(value) is None
        or set(_TOKEN.findall(value)) - {"sqrt"}
    ):
        raise ValueError("rank-46 coefficient escaped Q(sqrt(10))")
    try:
        expression = sp.sympify(value, locals={"sqrt": sp.sqrt})
        result = q10.qfrom_expr(expression)
    except (sp.SympifyError, TypeError, ValueError) as exc:
        raise ValueError("rank-46 coefficient is not exact in Q(sqrt(10))") from exc
    if result == q10.ZERO:
        raise ValueError("rank-46 record retains an explicit zero")
    return result


def _word(exponents: object) -> Word:
    if (
        not isinstance(exponents, list)
        or len(exponents) != 4
        or any(type(value) is not int or value < 0 for value in exponents)
    ):
        raise ValueError("rank-46 term has an invalid PBW exponent vector")
    return tuple(
        axis for axis, multiplicity in enumerate(exponents) for _ in range(multiplicity)
    )


def _parse_record(
    record: object, *, expected_shape: tuple[int, int], name: str
) -> SparseOperator:
    if not isinstance(record, dict) or set(record) != {"shape", "entries", "sha256"}:
        raise ValueError(f"{name} record fields drifted")
    if record["shape"] != list(expected_shape) or not isinstance(record["entries"], list):
        raise ValueError(f"{name} shape or entry inventory drifted")
    body = {"shape": record["shape"], "entries": record["entries"]}
    if record["sha256"] != _canonical_hash(body):
        raise ValueError(f"{name} internal record hash mismatch")
    output: dict[Key, q10.Q10] = {}
    last_pair = (-1, -1)
    for entry in record["entries"]:
        if not isinstance(entry, list) or len(entry) != 3:
            raise ValueError(f"{name} has a malformed matrix entry")
        row, column, raw_terms = entry
        if (
            type(row) is not int
            or type(column) is not int
            or not 0 <= row < expected_shape[0]
            or not 0 <= column < expected_shape[1]
            or (row, column) <= last_pair
            or not isinstance(raw_terms, list)
            or not raw_terms
        ):
            raise ValueError(f"{name} matrix support is invalid or unordered")
        last_pair = row, column
        last_word: Word | None = None
        for raw_word, raw_coefficient in raw_terms:
            word = _word(raw_word)
            if last_word is not None and word <= last_word:
                raise ValueError(f"{name} PBW terms are not strictly ordered")
            last_word = word
            coefficient = _coefficient(raw_coefficient)
            for reduced, factor in q10.pbw_word(word):
                q10._add(output, (row, column, reduced), q10.qmul(coefficient, factor))
    return SparseOperator(expected_shape, output)


def _identity(size: int) -> SparseOperator:
    return SparseOperator(
        (size, size), {(index, index, ()): q10.ONE for index in range(size)}
    )


def _add(*matrices: SparseOperator) -> SparseOperator:
    if not matrices or any(matrix.shape != matrices[0].shape for matrix in matrices):
        raise ValueError("rank-46 PBW matrix addition shape mismatch")
    output: dict[Key, q10.Q10] = {}
    for matrix in matrices:
        for key, coefficient in matrix.terms.items():
            q10._add(output, key, coefficient)
    return SparseOperator(matrices[0].shape, output)


def _negative(matrix: SparseOperator) -> SparseOperator:
    return SparseOperator(
        matrix.shape, {key: q10.qneg(value) for key, value in matrix.terms.items()}
    )


def _subtract(left: SparseOperator, right: SparseOperator) -> SparseOperator:
    return _add(left, _negative(right))


def _multiply(outer: SparseOperator, inner: SparseOperator) -> SparseOperator:
    if outer.shape[1] != inner.shape[0]:
        raise ValueError("rank-46 PBW matrix composition shape mismatch")
    outer_by_source: dict[int, list[tuple[int, Word, q10.Q10]]] = defaultdict(list)
    inner_by_target: dict[int, list[tuple[int, Word, q10.Q10]]] = defaultdict(list)
    for (row, middle, word), coefficient in outer.terms.items():
        outer_by_source[middle].append((row, word, coefficient))
    for (middle, column, word), coefficient in inner.terms.items():
        inner_by_target[middle].append((column, word, coefficient))
    output: dict[Key, q10.Q10] = {}
    for middle in set(outer_by_source) & set(inner_by_target):
        for row, outer_word, outer_coefficient in outer_by_source[middle]:
            for column, inner_word, inner_coefficient in inner_by_target[middle]:
                coefficient = q10.qmul(outer_coefficient, inner_coefficient)
                for word, factor in q10.pbw_word(outer_word + inner_word):
                    q10._add(output, (row, column, word), q10.qmul(coefficient, factor))
    return SparseOperator((outer.shape[0], inner.shape[1]), output)


def _adjoint(matrix: SparseOperator) -> SparseOperator:
    output: dict[Key, q10.Q10] = {}
    for (row, column, word), coefficient in matrix.terms.items():
        if len(word) % 2:
            coefficient = q10.qneg(coefficient)
        for reduced, factor in q10.pbw_word(tuple(reversed(word))):
            q10._add(output, (column, row, reduced), q10.qmul(coefficient, factor))
    return SparseOperator((matrix.shape[1], matrix.shape[0]), output)


def _maximum_order(matrix: SparseOperator) -> int:
    return max((len(key[2]) for key in matrix.terms), default=0)


def _load_inputs() -> tuple[dict[str, Any], dict[str, Any], dict[str, SparseOperator]]:
    certificate = _git_json(CLASSICAL_CERTIFICATE)
    schema = _git_json(CLASSICAL_SCHEMA)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(certificate)
    typed = _git_json(TYPED_36)
    artifacts: dict[str, SparseOperator] = {}
    if set(certificate["artifacts"]) != set(EXPECTED_ARTIFACTS):
        raise ValueError("rank-46 artifact inventory drifted")
    for name, shape in EXPECTED_ARTIFACTS.items():
        reference = certificate["artifacts"][name]
        relative = reference["path"]
        blob = _git_blob(relative)
        if _sha256_bytes(blob) != reference["sha256"]:
            raise ValueError(f"{name} file hash mismatch")
        record = json.loads(blob)
        artifacts[name] = _parse_record(record, expected_shape=shape, name=name)
        if len({(row, column) for row, column, _ in artifacts[name].terms}) != reference[
            "nonzero_row_pair_blocks"
        ] or _maximum_order(artifacts[name]) != reference["maximum_differential_order"]:
            raise ValueError(f"{name} diagnostics drifted")
    artifacts["q1_36"] = _parse_record(
        typed["retained_complex"]["classical_unary_q1"],
        expected_shape=(36, 36),
        name="q1_36",
    )
    artifacts["omega_36"] = _parse_record(
        typed["retained_complex"]["typed_cyclic_pairing"],
        expected_shape=(36, 36),
        name="omega_36",
    )
    return certificate, schema, artifacts


def _replay(m: Mapping[str, SparseOperator]) -> dict[str, bool]:
    q = m["q1_46"]
    omega = m["omega_46"]
    iota = m["iota_36_to_46"]
    projection = m["pi_46_to_36"]
    homotopy = m["S_46"]
    checks = {
        "q1_46_squared_zero": not _multiply(q, q).terms,
        "omega_46_antisymmetric": not _add(_adjoint(omega), omega).terms,
        "q1_46_typed_cyclic": not _add(
            _multiply(_adjoint(q), omega), _multiply(omega, q)
        ).terms,
        "pi_iota_identity": not _subtract(
            _multiply(projection, iota), _identity(36)
        ).terms,
        "iota_chain_map": not _subtract(
            _multiply(q, iota), _multiply(iota, m["q1_36"])
        ).terms,
        "pi_chain_map": not _subtract(
            _multiply(projection, q), _multiply(m["q1_36"], projection)
        ).terms,
        "contraction_identity": not _subtract(
            _add(_multiply(q, homotopy), _multiply(homotopy, q)),
            _subtract(_identity(46), _multiply(iota, projection)),
        ).terms,
        "homotopy_square_zero": not _multiply(homotopy, homotopy).terms,
        "homotopy_iota_zero": not _multiply(homotopy, iota).terms,
        "pi_homotopy_zero": not _multiply(projection, homotopy).terms,
        "homotopy_typed_cyclic": not _add(
            _multiply(_adjoint(homotopy), omega), _multiply(omega, homotopy)
        ).terms,
        "pairing_induced_by_iota": not _subtract(
            _multiply(_multiply(_adjoint(iota), omega), iota), m["omega_36"]
        ).terms,
        "stf2_right_inverse": not _subtract(
            _multiply(m["stf2_extractor_T"], m["stf2_right_inverse_J"]),
            _identity(5),
        ).terms,
        "stf2_wave_order_two": _maximum_order(m["stf2_wave_F"]) == 2,
    }
    if set(checks) != EXPECTED_CHECKS or not all(checks.values()):
        raise ValueError(f"independent rank-46 replay failed: {checks}")
    return checks


def build() -> dict[str, Any]:
    classical, _schema, matrices = _load_inputs()
    if (
        classical["result_state"] != "CERTIFIED_CYCLIC_GRAPH_CARRIER_PROJECTOR_OPEN"
        or classical["dependency_tags"] != ["LOCAL-ALGEBRAIC"]
        or classical["carrier"]["total_rows"] != 46
        or classical["carrier"]["degree_ranks"] != {"-1": 4, "0": 19, "1": 19, "2": 4}
        or classical["carrier"]["coefficient_field"] != "Q(sqrt(10))"
        or set(classical["exact_checks"]) != EXPECTED_CHECKS
        or any(value is not True for value in classical["exact_checks"].values())
    ):
        raise ValueError("classical rank-46 claim or carrier boundary drifted")
    flags = classical["flags"]
    if (
        flags["BERGER_RETAINED_46_STF2_PROLONGATION_BRANCH_CARRIER_V1"] is not True
        or flags["CYCLIC_GRAPH_SDR_46_TO_36"] is not True
        or any(
            flags[name] is not False
            for name in (
                "CANONICAL_BRANCH_PROJECTOR_CERTIFIED",
                "ELL3_BRANCH_MIXING_AUTHORIZED",
                "Q2_Q3_LIFT_MATERIALIZED",
                "K_BERGER_EQUIVARIANCE_CERTIFIED",
                "LORENTZIAN_CAUSAL",
                "QUANTUM_CLAIM",
            )
        )
    ):
        raise ValueError("classical rank-46 flags crossed the carrier boundary")

    checks = _replay(matrices)
    classical_paths = (
        CLASSICAL_CERTIFICATE,
        CLASSICAL_SCHEMA,
        TYPED_36,
        CLASSICAL_PRODUCER,
        CLASSICAL_VERIFIER,
        CLASSICAL_TEST,
        CLASSICAL_REPORT,
        *(classical["artifacts"][name]["path"] for name in sorted(EXPECTED_ARTIFACTS)),
    )
    source_manifest = {path: _sha256(ROOT / path) for path in SOURCE_PATHS}
    return {
        "schema": "quantum-weyl-berger-retained-46-stf2-carrier-import-v1",
        "result_id": "BERGER_RETAINED_46_STF2_CARRIER_IMPORT",
        "result_state": "PINNED_EXACT_CYCLIC_GRAPH_SDR_IMPORTED_PROJECTOR_OPEN",
        "lifecycle_layer": "OPTIONAL_CLASSICAL_BRANCH_INTERPRETATION_INPUT",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "classical_source": {
            "commit": CLASSICAL_COMMIT,
            "result_id": classical["result_id"],
            "result_state": classical["result_state"],
            "artifacts": {path: _artifact(path) for path in classical_paths},
        },
        "carrier": {
            "total_rows": 46,
            "retained_rows": 36,
            "degree_ranks": classical["carrier"]["degree_ranks"],
            "added_configuration_rows": 5,
            "added_cyclic_dual_rows": 5,
            "coefficient_field": "Q(sqrt(10))",
            "support_category": "FINITE_ORDER_SUPPORT_LOCAL",
            "interpretation": "cyclic graph prolongation with contractible STF2 complement; not a branch projector",
        },
        "independent_replay": {
            "backend": "quantum-two-rational-component-Q(sqrt(10))-PBW-v1",
            "producer_executed": False,
            "checks": checks,
            "all_checks_pass": True,
        },
        "operator_diagnostics": {
            name: {
                "shape": list(matrices[name].shape),
                "canonical_PBW_coefficients": len(matrices[name].terms),
                "maximum_differential_order": _maximum_order(matrices[name]),
            }
            for name in EXPECTED_ARTIFACTS
        },
        "claim_flags": {
            "RANK_46_SUPPORT_LOCAL_CARRIER_IMPORTED": True,
            "RANK_46_GRAPH_SDR_INDEPENDENTLY_REPLAYED": True,
            "RANK_46_SUPPORT_LOCAL_PROJECTOR_CONSTRUCTED": False,
            "ELL3_BRANCH_MIXING_AUTHORIZED": False,
            "Q2_Q3_LIFT_MATERIALIZED_ON_RANK_46": False,
            "K_BERGER_EQUIVARIANCE_CERTIFIED_ON_RANK_46": False,
            "LORENTZIAN_CAUSAL": False,
            "RANK_46_IS_QUANTUM_PREREQUISITE": False,
            "QME_RESTORED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "OPTIONAL_BERGER_RETAINED_46_STF2_BRANCH_PROJECTOR_OR_OBSTRUCTION_V1",
        "claim_boundary": (
            "This pinned LOCAL-ALGEBRAIC quantum consumer independently parses all eight exact "
            "Q(sqrt(10)) PBW operator records from classical commit 01ca7ba5 and replays the "
            "rank-46-to-36 cyclic graph-SDR identities coefficientwise. It accepts a finite-order "
            "support-local carrier with a contractible STF2 complement. It does not accept an "
            "Einstein-like/extra-Weyl/Maxwell branch projector, materialize q2 or q3 on rank 46, "
            "authorize an ell3 branch mixing table, prove K_Berger equivariance or Lorentzian "
            "causal support for this carrier, restore a QME, or make a quantum or particle claim. "
            "The carrier remains optional Paper-11 interpretation infrastructure and is not a "
            "prerequisite for the minimal-BV anomaly, Slavnov-breaking, or quantum-transfer path."
        ),
        "consumer_provenance": {
            "source_manifest": source_manifest,
            "source_manifest_sha256": _canonical_hash(source_manifest),
        },
        "verification_receipts": [
            {
                "test_tier": 1,
                "command": "PYTHONPATH=quantum-weyl python3 -m transfer.berger_retained_46_stf2_carrier_import --check",
                "status": "PASS",
                "elapsed_seconds": 2.09,
            },
            {
                "test_tier": 1,
                "command": "PYTHONPATH=quantum-weyl python3 -m transfer.verify_berger_retained_46_stf2_carrier_import",
                "status": "PASS",
                "elapsed_seconds": 1.98,
            },
            {
                "test_tier": 1,
                "command": "PYTHONPATH=quantum-weyl python3 -m unittest quantum-weyl/transfer/tests/test_berger_retained_46_stf2_carrier_import.py",
                "status": "PASS",
                "elapsed_seconds": 2.32,
            },
            {
                "test_tier": 1,
                "command": "PYTHONPATH=quantum-weyl python3 -m transfer.berger_retained_46_stf2_carrier_import --guards",
                "status": "PASS",
                "elapsed_seconds": 2.04,
            },
        ],
        "higher_tiers_not_run": {
            "tier_2": "The scoped import, exact replay, schema, and mutation tests cover this carrier-only change.",
            "tier_3": "No classical producer, shared PBW engine, nonlinear tensor, causal construction, QME lifecycle, theorem freeze, or release boundary changed.",
        },
    }


def validate(value: dict[str, Any]) -> None:
    flags = value.get("claim_flags", {})
    if (
        flags.get("RANK_46_SUPPORT_LOCAL_CARRIER_IMPORTED") is not True
        or flags.get("RANK_46_GRAPH_SDR_INDEPENDENTLY_REPLAYED") is not True
        or any(
            flags.get(name) is not False
            for name in (
                "RANK_46_SUPPORT_LOCAL_PROJECTOR_CONSTRUCTED",
                "ELL3_BRANCH_MIXING_AUTHORIZED",
                "Q2_Q3_LIFT_MATERIALIZED_ON_RANK_46",
                "K_BERGER_EQUIVARIANCE_CERTIFIED_ON_RANK_46",
                "LORENTZIAN_CAUSAL",
                "RANK_46_IS_QUANTUM_PREREQUISITE",
                "QME_RESTORED",
                "QUANTUM_CLAIM",
            )
        )
    ):
        raise ValueError("rank-46 carrier import crossed its claim boundary")
    if value.get("independent_replay", {}).get("all_checks_pass") is not True:
        raise ValueError("rank-46 independent replay was not accepted")


def _text(value: dict[str, Any]) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()
    value = build()
    validate(value)
    Draft202012Validator(json.loads(SCHEMA.read_text())).validate(value)
    if args.write:
        OUTPUT.write_text(_text(value))
    if args.check and OUTPUT.read_text() != _text(value):
        raise SystemExit(f"rank-46 carrier import is stale: {OUTPUT}")
    if args.guards:
        for flag in (
            "RANK_46_SUPPORT_LOCAL_PROJECTOR_CONSTRUCTED",
            "ELL3_BRANCH_MIXING_AUTHORIZED",
            "Q2_Q3_LIFT_MATERIALIZED_ON_RANK_46",
            "LORENTZIAN_CAUSAL",
            "QME_RESTORED",
            "QUANTUM_CLAIM",
        ):
            mutant = deepcopy(value)
            mutant["claim_flags"][flag] = True
            try:
                validate(mutant)
            except ValueError:
                continue
            raise AssertionError(f"rank-46 import mutation survived: {flag}")
    print("BERGER_RETAINED_46_STF2_CARRIER_IMPORT: PASS")


if __name__ == "__main__":
    main()
