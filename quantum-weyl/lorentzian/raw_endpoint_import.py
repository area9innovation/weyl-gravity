"""Pinned exact consumer for the corrected raw Berger endpoint package.

The consumer deliberately replays the algebra from serialized sparse PBW
operators.  It does not execute the classical generator and it does not infer
Green hyperbolicity from principal-symbol compatibility.
"""

from __future__ import annotations

from functools import reduce
import hashlib
import json
from pathlib import Path
import re
import subprocess
from typing import Any, Iterable

import sympy as sp

from local_bv.schema_validation import validate_instance
from transfer.berger_gauge_fixed_nonminimal_import import (
    OperatorMatrix,
    _adjoint_transpose,
    _is_zero,
    _matrix_add,
    _multiply,
    _subtract,
    _zero,
)
from transfer.berger_retained_q1_import import ALPHA_B, U, V

from . import curved_witness_adapter as DRESSED_ADAPTER


LORENTZIAN_ROOT = Path(__file__).resolve().parent
ROOT = LORENTZIAN_ROOT.parents[1]
CLASSICAL_COMMIT = "3147774e10fe6b01e4f482783014ddc39f3de0ff"
SETTING_ID = "compact_positive_berger_clock_fixed_coupling_linearized"

TRANSPORT_CERTIFICATE = (
    "d_quotient_classical/certificates/"
    "BERGER_RAW_CLOCK_REATTACHED_WITNESS_TRANSPORT.json"
)
TRANSPORT_SCHEMA = (
    "d_quotient_classical/schema/"
    "berger-raw-clock-reattached-witness-transport-v1.schema.json"
)
PREFLIGHT_CERTIFICATE = (
    "d_quotient_classical/certificates/BERGER_RAW_ENDPOINT_GREEN_PREFLIGHT.json"
)
PREFLIGHT_SCHEMA = (
    "d_quotient_classical/schema/berger-raw-endpoint-green-preflight-v1.schema.json"
)
SOURCE_ARTIFACTS = (
    TRANSPORT_CERTIFICATE,
    TRANSPORT_SCHEMA,
    PREFLIGHT_CERTIFICATE,
    PREFLIGHT_SCHEMA,
    "d_quotient_classical/backreacted_clock/berger_raw_clock_reattached_witness_transport.py",
    "d_quotient_classical/backreacted_clock/berger_raw_endpoint_green_preflight.py",
    "d_quotient_classical/backreacted_clock/verify_berger_raw_clock_reattached_witness_transport.py",
    "d_quotient_classical/backreacted_clock/verify_berger_raw_endpoint_green_preflight.py",
    "d_quotient_classical/backreacted_clock/tests/test_berger_raw_clock_reattached_witness_transport.py",
    "d_quotient_classical/backreacted_clock/tests/test_berger_raw_endpoint_green_preflight.py",
    "d_quotient_classical/reports/berger-raw-clock-reattached-witness-transport.md",
    "d_quotient_classical/reports/berger-raw-endpoint-green-preflight.md",
)
_TOKEN = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
_ALLOWED_CHARACTERS = re.compile(r"^[0-9A-Za-z_+*/() -]+$")


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
        raise ValueError(f"missing pinned raw-endpoint artifact: {relative}")
    return result.stdout


def _git_json(relative: str) -> dict[str, Any]:
    payload = json.loads(_git_blob(relative))
    if not isinstance(payload, dict):
        raise ValueError(f"pinned JSON is not an object: {relative}")
    return payload


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


def _parse_rational_coefficient(value: str) -> sp.Expr:
    if (
        not value
        or _ALLOWED_CHARACTERS.fullmatch(value) is None
        or set(_TOKEN.findall(value)) - {"alpha_B", "u", "v"}
    ):
        raise ValueError("raw PBW coefficient uses an undeclared token")
    try:
        expression = sp.cancel(
            sp.sympify(value, locals={"alpha_B": ALPHA_B, "u": U, "v": V})
        )
        numerator, denominator = sp.fraction(expression)
        sp.Poly(numerator, ALPHA_B, U, V, domain=sp.QQ)
        sp.Poly(denominator, ALPHA_B, U, V, domain=sp.QQ)
    except (sp.SympifyError, TypeError, ValueError) as exc:
        raise ValueError("raw PBW coefficient is not an exact rational function") from exc
    normalized = sp.factor(expression)
    if normalized == 0:
        raise ValueError("raw PBW record retains a zero coefficient")
    return normalized


def _load_rational_record(
    name: str, record: object, shape: tuple[int, int]
) -> OperatorMatrix:
    if not isinstance(record, dict) or set(record) != {"shape", "entries", "sha256"}:
        raise ValueError(f"{name} record fields drifted")
    if record["shape"] != list(shape):
        raise ValueError(f"{name} shape drifted")
    body = {"shape": record["shape"], "entries": record["entries"]}
    if record["sha256"] != _canonical_hash(body):
        raise ValueError(f"{name} internal record hash mismatch")
    output = _zero(*shape)
    seen: set[tuple[int, int]] = set()
    if not isinstance(record["entries"], list):
        raise ValueError(f"{name} entries are not a list")
    for item in record["entries"]:
        if not isinstance(item, list) or len(item) != 3:
            raise ValueError(f"{name} malformed entry")
        row, column, terms = item
        if (
            type(row) is not int
            or type(column) is not int
            or not 0 <= row < shape[0]
            or not 0 <= column < shape[1]
            or (row, column) in seen
            or not isinstance(terms, list)
            or not terms
        ):
            raise ValueError(f"{name} duplicate or out-of-range entry")
        operator: dict[tuple[int, ...], sp.Expr] = {}
        for term in terms:
            if not isinstance(term, list) or len(term) != 2:
                raise ValueError(f"{name} malformed PBW term")
            exponents, coefficient = term
            if (
                not isinstance(exponents, list)
                or len(exponents) != 4
                or any(type(count) is not int or count < 0 for count in exponents)
                or not isinstance(coefficient, str)
            ):
                raise ValueError(f"{name} malformed PBW monomial")
            word = tuple(
                axis for axis, count in enumerate(exponents) for _ in range(count)
            )
            if word in operator:
                raise ValueError(f"{name} repeats a PBW monomial")
            operator[word] = _parse_rational_coefficient(coefficient)
        output[row][column] = operator
        seen.add((row, column))
    return output


def _require_fields(value: object, expected: Iterable[str], label: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != set(expected):
        raise ValueError(f"{label} fields drifted")
    return value


def _load_artifact(
    reference: object, *, name: str, shape: tuple[int, int]
) -> OperatorMatrix:
    record = _require_fields(reference, ("format", "path", "sha256"), name)
    if record["format"] != "JSON_EXACT_SPARSE_OPERATOR":
        raise ValueError(f"{name} format drifted")
    body = _git_blob(record["path"])
    if hashlib.sha256(body).hexdigest() != record["sha256"]:
        raise ValueError(f"{name} file hash mismatch")
    return _load_rational_record(name, json.loads(body), shape)


def _identity(rank: int) -> OperatorMatrix:
    result = _zero(rank, rank)
    for index in range(rank):
        result[index][index] = {(): sp.S.One}
    return result


def _embed(
    target: OperatorMatrix,
    block: OperatorMatrix,
    row_offset: int,
    column_offset: int,
) -> None:
    for row, values in enumerate(block):
        for column, operator in enumerate(values):
            target[row_offset + row][column_offset + column] = operator


def _block(
    matrix: OperatorMatrix, rows: range, columns: range
) -> OperatorMatrix:
    return [[matrix[row][column] for column in columns] for row in rows]


def _maximum_order(matrix: OperatorMatrix) -> int:
    return max(
        (len(word) for row in matrix for operator in row for word in operator),
        default=-1,
    )


def _coefficient_matrix(matrix: OperatorMatrix, word: tuple[int, ...]) -> sp.Matrix:
    return sp.Matrix(
        [[sp.factor(operator.get(word, sp.S.Zero)) for operator in row] for row in matrix]
    )


def _homogeneous_symbol(matrix: OperatorMatrix, order: int) -> sp.Matrix:
    momenta = sp.symbols("p0:4")
    return sp.Matrix(
        [
            [
                sp.factor(
                    sum(
                        coefficient * sp.prod(momenta[axis] for axis in word)
                        for word, coefficient in operator.items()
                        if len(word) == order
                    )
                )
                for operator in row
            ]
            for row in matrix
        ]
    )


def _constant_matrix(matrix: OperatorMatrix) -> sp.Matrix:
    if any(word for row in matrix for operator in row for word in operator):
        raise ValueError("expected an order-zero matrix")
    return _coefficient_matrix(matrix, ())


def _validate_source_payloads() -> tuple[dict[str, Any], dict[str, Any]]:
    transport = _git_json(TRANSPORT_CERTIFICATE)
    transport_schema = _git_json(TRANSPORT_SCHEMA)
    errors = validate_instance(transport, transport_schema)
    if errors:
        raise ValueError(f"raw transport source failed strict schema: {errors}")
    preflight = _git_json(PREFLIGHT_CERTIFICATE)
    preflight_schema = _git_json(PREFLIGHT_SCHEMA)
    errors = validate_instance(preflight, preflight_schema)
    if errors:
        raise ValueError(f"raw endpoint preflight failed strict schema: {errors}")
    if (
        transport.get("result_id")
        != "BERGER_RAW_CLOCK_REATTACHED_WITNESS_TRANSPORT"
        or transport.get("setting_id") != SETTING_ID
        or transport.get("claim_status")
        != "CERTIFIED_RAW_BV_TRANSPORT_PRINCIPAL_COMPATIBLE_GREEN_OPEN"
        or transport.get("dependency_tags")
        != ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"]
        or transport["flags"]["BERGER_RAW_CLOCK_REATTACHED_GREEN_INVERSION"]
        is not False
        or transport["flags"]["BERGER_26_ROW_CAUSAL_GREEN_HOMOTOPY"] is not False
    ):
        raise ValueError("raw transport source boundary drifted")
    if (
        preflight.get("result_id") != "BERGER_RAW_ENDPOINT_GREEN_PREFLIGHT"
        or preflight.get("setting_id") != SETTING_ID
        or preflight.get("claim_status")
        != "EXACT_FILTER_PREFLIGHT_GREEN_INVERSION_OPEN"
        or preflight["flags"]["BERGER_RAW_ENDPOINT_FILTERED_GREEN_EXTENSION"]
        is not False
        or preflight["flags"]["BERGER_26_ROW_CAUSAL_GREEN_HOMOTOPY"] is not False
    ):
        raise ValueError("raw endpoint preflight boundary drifted")
    if preflight["dependency_ref"] != {
        "result_id": transport["result_id"],
        "sha256": hashlib.sha256(_git_blob(TRANSPORT_CERTIFICATE)).hexdigest(),
    }:
        raise ValueError("raw endpoint preflight dependency drifted")
    return transport, preflight


def fast_receipt() -> dict[str, Any]:
    """Validate pinned schemas, file hashes, and internal sparse-record hashes."""

    transport, preflight = _validate_source_payloads()
    coordinate = transport["coordinate_transport"]["artifacts"]
    operators = transport["operators"]
    for name, shape in (
        ("raw_to_dressed_F12", (12, 12)),
        ("dressed_to_raw_C12", (12, 12)),
    ):
        _load_artifact(coordinate[name], name=name, shape=shape)
    for name in ("q34_raw", "W34_raw", "P34_raw", "pairing34_raw"):
        _load_artifact(operators[name], name=name, shape=(34, 34))
    return {
        "operator_hashes": {
            name: operators[name]["sha256"]
            for name in ("q34_raw", "W34_raw", "P34_raw", "pairing34_raw")
        },
        "coordinate_hashes": {
            name: coordinate[name]["sha256"]
            for name in ("raw_to_dressed_F12", "dressed_to_raw_C12")
        },
        "source_claim_status": transport["claim_status"],
        "preflight_claim_status": preflight["claim_status"],
        "order_six_polynomial_gcd": preflight["schur_audit"][
            "order_six_polynomial_gcd"
        ],
    }


def evaluate_raw_endpoint() -> dict[str, Any]:
    transport, preflight = _validate_source_payloads()
    coordinate = transport["coordinate_transport"]["artifacts"]
    operators = transport["operators"]
    f12 = _load_artifact(
        coordinate["raw_to_dressed_F12"], name="F12", shape=(12, 12)
    )
    c12 = _load_artifact(
        coordinate["dressed_to_raw_C12"], name="C12", shape=(12, 12)
    )
    q34 = _load_artifact(operators["q34_raw"], name="q34_raw", shape=(34, 34))
    w34 = _load_artifact(operators["W34_raw"], name="W34_raw", shape=(34, 34))
    p34 = _load_artifact(operators["P34_raw"], name="P34_raw", shape=(34, 34))
    pairing = _load_artifact(
        operators["pairing34_raw"], name="pairing34_raw", shape=(34, 34)
    )

    identity12 = _identity(12)
    if not _is_zero(_subtract(_multiply(f12, c12), identity12)):
        raise ValueError("F12 C12 identity failed")
    if not _is_zero(_subtract(_multiply(c12, f12), identity12)):
        raise ValueError("C12 F12 identity failed")
    if not _is_zero(_multiply(q34, q34)):
        raise ValueError("raw q34 is not nilpotent")
    if not _is_zero(
        _matrix_add(
            _multiply(_adjoint_transpose(q34), pairing),
            _multiply(pairing, q34),
        )
    ):
        raise ValueError("raw q34 cyclicity failed")
    if not _is_zero(
        _matrix_add(
            _multiply(_adjoint_transpose(w34), pairing),
            _multiply(pairing, w34),
        )
    ):
        raise ValueError("raw W34 cyclicity failed")
    if not _is_zero(
        _subtract(_matrix_add(_multiply(q34, w34), _multiply(w34, q34)), p34)
    ):
        raise ValueError("raw P34 != q34 W34 + W34 q34")
    if _constant_matrix(pairing).rank() != 34:
        raise ValueError("raw pairing is degenerate")

    # U maps raw coordinates to dressed coordinates.  The antifield block is
    # F^{-sharp}=C^sharp, so the complete transformation is BV canonical.
    u34 = _zero(34, 34)
    u34_inverse = _zero(34, 34)
    for offset, block, inverse in (
        (0, _identity(5), _identity(5)),
        (5, f12, c12),
        (17, _adjoint_transpose(c12), _adjoint_transpose(f12)),
        (29, _identity(5), _identity(5)),
    ):
        _embed(u34, block, offset, offset)
        _embed(u34_inverse, inverse, offset, offset)
    identity34 = _identity(34)
    if not _is_zero(_subtract(_multiply(u34, u34_inverse), identity34)):
        raise ValueError("raw-to-dressed 34-row roundtrip failed")
    if not _is_zero(_subtract(_multiply(u34_inverse, u34), identity34)):
        raise ValueError("dressed-to-raw 34-row roundtrip failed")
    if not _is_zero(
        _subtract(
            _multiply(_multiply(_adjoint_transpose(u34), pairing), u34),
            pairing,
        )
    ):
        raise ValueError("34-row coordinate transport is not BV canonical")

    dressed_sources = DRESSED_ADAPTER._validate_source_boundaries(
        DRESSED_ADAPTER._git_json(DRESSED_ADAPTER.MINIMAL_CERTIFICATE),
        DRESSED_ADAPTER._git_json(DRESSED_ADAPTER.RETAINED_CERTIFICATE),
        DRESSED_ADAPTER._git_json(DRESSED_ADAPTER.NONMINIMAL_CERTIFICATE),
        DRESSED_ADAPTER._git_json(DRESSED_ADAPTER.GAUGE_CERTIFICATE),
    )
    dressed_q34 = _multiply(_multiply(u34, q34), u34_inverse)
    if not _is_zero(_subtract(dressed_q34, dressed_sources["q34"])):
        raise ValueError("transported q34 does not reproduce the dressed unary complex")

    temporal = _coefficient_matrix(p34, (0, 0, 0, 0))
    ghost4 = temporal[0:5, 0:5]
    field4 = temporal[5:17, 5:17]
    antifield4 = temporal[17:29, 17:29]
    identity4 = temporal[29:34, 29:34]
    if ghost4 != sp.eye(5) or identity4 != sp.eye(5):
        raise ValueError("raw ghost/identity principal blocks drifted")
    if field4[:10, :10] != sp.eye(10):
        raise ValueError("raw metric principal block drifted")
    if antifield4[:10, :10] != sp.eye(10):
        raise ValueError("raw metric-antifield principal block drifted")
    if field4[10:12, 10:12] != sp.zeros(2, 2):
        raise ValueError("clock acquired an order-four diagonal")
    if field4[10:12, :10].rank() != 1:
        raise ValueError("metric-to-clock order-four rank drifted")

    a = _block(p34, range(5, 15), range(5, 15))
    b = _block(p34, range(5, 15), range(15, 17))
    c = _block(p34, range(15, 17), range(5, 15))
    d = _block(p34, range(15, 17), range(15, 17))
    if not _is_zero(_subtract(d, _identity(2))):
        raise ValueError("raw clock diagonal is not I2")
    bc = _multiply(b, c)
    orders = {
        "A_metric": _maximum_order(a),
        "B_clock_to_metric": _maximum_order(b),
        "C_metric_to_clock": _maximum_order(c),
        "D_clock": _maximum_order(d),
        "BC_schur_correction": _maximum_order(bc),
    }
    if orders != {
        "A_metric": 4,
        "B_clock_to_metric": 2,
        "C_metric_to_clock": 4,
        "D_clock": 0,
        "BC_schur_correction": 6,
    }:
        raise ValueError("raw endpoint differential-order profile drifted")
    if _is_zero(bc):
        raise ValueError("raw endpoint Schur correction vanished")
    bc6 = _homogeneous_symbol(bc, 6)
    nonzero = [sp.factor(value) for value in bc6 if value != 0]
    gcd = sp.factor(reduce(sp.gcd, nonzero))
    p0, p1, p2, p3 = sp.symbols("p0:4")
    wave = -p0**2 + p1**2 + p2**2 + p3**2
    wave_quotient = bc6.applyfunc(lambda value: sp.factor(value / wave))
    if any(sp.denom(value).has(p0, p1, p2, p3) for value in wave_quotient):
        raise ValueError("order-six Schur correction is not wave-divisible")
    if wave_quotient.rank() != 1:
        raise ValueError("wave-divided Schur symbol is not rank one")
    fixtures = {
        "timelike": {p0: 1, p1: 0, p2: 0, p3: 0},
        "spacelike": {p0: 0, p1: 1, p2: 0, p3: 0},
        "null": {p0: 1, p1: 1, p2: 0, p3: 0},
        "generic": {p0: 2, p1: 1, p2: 3, p3: 1},
    }
    ranks = {
        name: int(sp.simplify(bc6.subs(values)).rank())
        for name, values in fixtures.items()
    }
    if ranks != {"timelike": 1, "spacelike": 1, "null": 0, "generic": 1}:
        raise ValueError("order-six Schur rank fixtures drifted")

    source_gcd = sp.sympify(
        preflight["schur_audit"]["order_six_polynomial_gcd"],
        locals={
            "alpha_B": ALPHA_B,
            "u": U,
            "v": V,
            "p0": p0,
            "p1": p1,
            "p2": p2,
            "p3": p3,
        },
    )
    if sp.factor(gcd - source_gcd) != 0:
        raise ValueError("independent Schur gcd disagrees with the source receipt")

    return {
        "source_transport": transport,
        "source_preflight": preflight,
        "operator_hashes": {
            name: operators[name]["sha256"]
            for name in ("q34_raw", "W34_raw", "P34_raw", "pairing34_raw")
        },
        "coordinate_hashes": {
            name: coordinate[name]["sha256"]
            for name in ("raw_to_dressed_F12", "dressed_to_raw_C12")
        },
        "orders": orders,
        "schur_gcd": str(gcd),
        "schur_ranks": ranks,
    }


def source_artifacts() -> list[dict[str, str]]:
    transport = _git_json(TRANSPORT_CERTIFICATE)
    dynamic = [
        artifact["path"]
        for artifact in (
            *transport["coordinate_transport"]["artifacts"].values(),
            *transport["operators"].values(),
        )
    ]
    return [_artifact(path) for path in (*SOURCE_ARTIFACTS, *dynamic)]
