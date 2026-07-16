"""Independent fail-closed import of the retained Berger minimal ``q1``.

The classical certificate supplies the complete 26-row minimal differential
in an invariant-frame PBW basis.  This module pins the mathematical theorem,
its classical registration, and the later schema repair separately.  It then
reconstructs the exact PBW operators without importing classical producer
code and verifies the adjoint, Noether, nilpotency, coverage, and locality
claims needed to accept ``q1`` as a nonlinear-transfer prerequisite.

This is not a classical contraction and contains no ``q2`` or ``D`` action.
"""

from __future__ import annotations

from copy import deepcopy
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import re
import subprocess
from typing import Any

import sympy as sp
from sympy.polys.polyerrors import PolynomialError


TRANSFER_ROOT = Path(__file__).resolve().parent
ROOT = TRANSFER_ROOT.parents[1]

THEOREM_COMMIT = "b37bf3bd504a7745fbe80448cd0ab578a3a135ea"
REGISTRATION_COMMIT = "d4b4fbdad2e0fff4aebf670df66f8c813a39e340"
SCHEMA_COMMIT = "e703df6d6f58c7e2592c7d01d1e452e919cd9923"

CERTIFICATE_RELATIVE = (
    "d_quotient_classical/certificates/BERGER_RETAINED_MINIMAL_OPERATOR.json"
)
SCHEMA_RELATIVE = (
    "d_quotient_classical/schema/berger-retained-minimal-operator-v1.schema.json"
)
LAYOUT_RELATIVE = (
    "d_quotient_classical/certificates/BERGER_RETAINED_MINIMAL_LAYOUT.json"
)
STATUS_RELATIVE = "d_quotient_classical/certificates/CLASSICAL_D_QUOTIENT_STATUS.json"
PRODUCER_RELATIVE = (
    "d_quotient_classical/backreacted_clock/berger_linearized_bach_pbw.py"
)
INDEPENDENT_VERIFIER_RELATIVE = (
    "d_quotient_classical/backreacted_clock/verify_berger_retained_minimal_operator.py"
)
SCHEMA_TEST_RELATIVE = (
    "d_quotient_classical/backreacted_clock/tests/"
    "test_berger_retained_minimal_operator_schema.py"
)
REPORT_RELATIVE = (
    "d_quotient_classical/reports/berger-retained-minimal-operator.md"
)

SCHEMA_ID = "quantum-weyl-berger-retained-minimal-q1-import-v1"
U, V, ALPHA_B = sp.symbols("u v alpha_B", nonzero=True, real=True)
_TOKEN = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
_ALLOWED_CHARACTERS = re.compile(r"^[0-9A-Za-z_+*/() -]+$")

EXPECTED_SHAPES = {
    "K_spatial": (10, 3),
    "H_retained": (10, 10),
    "minus_K_spatial_sharp": (3, 10),
}
EXPECTED_MAXIMUM_ORDERS = {
    "K_spatial": 1,
    "H_retained": 4,
    "minus_K_spatial_sharp": 1,
}

ScalarOperator = dict[tuple[int, ...], sp.Expr]
OperatorMatrix = list[list[ScalarOperator]]


def _canonical_hash(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def _require_hash(value: object, label: str) -> str:
    if (
        not isinstance(value, str)
        or len(value) != 64
        or any(character not in "0123456789abcdef" for character in value)
    ):
        raise ValueError(f"{label} must be a lowercase SHA-256 digest")
    return value


@lru_cache(maxsize=1)
def _git_prefix() -> str:
    return subprocess.run(
        ["git", "rev-parse", "--show-prefix"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def _git_blob(relative: str, *, commit: str) -> bytes:
    result = subprocess.run(
        ["git", "show", f"{commit}:{_git_prefix()}{relative}"],
        cwd=ROOT,
        check=False,
        capture_output=True,
    )
    if result.returncode != 0:
        raise ValueError(f"missing pinned classical artifact {relative} at {commit}")
    return result.stdout


def _git_json(relative: str, *, commit: str) -> dict[str, Any]:
    try:
        value = json.loads(_git_blob(relative, commit=commit))
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid pinned JSON {relative} at {commit}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"pinned JSON is not an object: {relative}")
    return value


def _artifact(relative: str, *, commit: str) -> dict[str, str]:
    return {
        "path": relative,
        "commit": commit,
        "sha256": hashlib.sha256(_git_blob(relative, commit=commit)).hexdigest(),
    }


def _require_fields(value: object, fields: set[str], label: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != fields:
        raise ValueError(f"{label} has the wrong field set")
    return value


def _validate_schema(schema: dict[str, Any]) -> None:
    if (
        schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema"
        or schema.get("$id")
        != "https://area9.dk/schemas/pure-weyl-berger-retained-minimal-operator-v1.schema.json"
    ):
        raise ValueError("classical retained-q1 schema identity drifted")
    q1 = schema.get("properties", {}).get("q1_blocks")
    if not isinstance(q1, dict) or q1.get("additionalProperties") is not False:
        raise ValueError("classical retained-q1 block schema is not strict")
    required = q1.get("required")
    properties = q1.get("properties")
    if not isinstance(required, list) or not isinstance(properties, dict):
        raise ValueError("classical retained-q1 block properties are undefined")
    if set(required) != set(EXPECTED_SHAPES) or set(properties) != set(EXPECTED_SHAPES):
        raise ValueError("classical retained-q1 schema block inventory drifted")
    definitions = schema.get("$defs")
    if not isinstance(definitions, dict) or set(
        ("pbwOperatorRecord", "pbwMatrixEntry", "pbwTerm")
    ) - set(definitions):
        raise ValueError("classical retained-q1 strict PBW definitions are missing")
    for name, shape in EXPECTED_SHAPES.items():
        all_of = properties[name].get("allOf")
        if (
            not isinstance(all_of, list)
            or len(all_of) != 2
            or all_of[0].get("$ref") != "#/$defs/pbwOperatorRecord"
            or all_of[1].get("properties", {}).get("shape", {}).get("const")
            != list(shape)
        ):
            raise ValueError(f"classical retained-q1 schema shape drifted: {name}")


def _expected_layout_rows() -> list[tuple[str, int, str]]:
    rows: list[tuple[str, int, str]] = []
    for component in ("1", "2", "3"):
        rows.append((f"c_spatial_{component}", -1, "odd"))
    for component in ("00", "01", "02", "03", "11", "12", "13", "22", "23", "33"):
        rows.append((f"h_hat_{component}", 0, "even"))
    for component in ("00", "01", "02", "03", "11", "12", "13", "22", "23", "33"):
        rows.append((f"h_hat_star_{component}", 1, "odd"))
    for component in ("1", "2", "3"):
        rows.append((f"c_spatial_star_{component}", 2, "even"))
    return rows


def _validate_layout(layout: dict[str, Any], expected_digest: object) -> None:
    if (
        layout.get("schema") != "pure-weyl-berger-retained-minimal-layout-v1"
        or layout.get("result_id") != "BERGER_RETAINED_MINIMAL_LAYOUT"
        or layout.get("claim_status") != "CERTIFIED_TYPED_LAYOUT"
        or layout.get("dependency_tags") != ["LOCAL-ALGEBRAIC"]
        or _canonical_hash(layout) != expected_digest
    ):
        raise ValueError("classical retained-q1 layout identity or digest drifted")
    rows = layout.get("component_rows")
    if not isinstance(rows, list) or len(rows) != 26:
        raise ValueError("classical retained-q1 layout does not contain 26 rows")
    observed = []
    for index, row in enumerate(rows):
        if not isinstance(row, dict) or row.get("index") != index:
            raise ValueError("classical retained-q1 layout index drifted")
        observed.append((row.get("row_id"), row.get("degree"), row.get("parity")))
    if observed != _expected_layout_rows():
        raise ValueError("classical retained-q1 authoritative row order drifted")


@lru_cache(maxsize=None)
def _parse_coefficient(value: str) -> sp.Expr:
    if (
        not value
        or _ALLOWED_CHARACTERS.fullmatch(value) is None
        or set(_TOKEN.findall(value)) - {"alpha_B", "u", "v"}
    ):
        raise ValueError("PBW coefficient uses an undeclared expression token")
    try:
        expression = sp.sympify(
            value,
            locals={"alpha_B": ALPHA_B, "u": U, "v": V},
        )
        polynomial = sp.Poly(expression, ALPHA_B, U, V, domain=sp.QQ)
    except (sp.SympifyError, PolynomialError, TypeError, ValueError) as exc:
        raise ValueError("PBW coefficient is not an exact declared polynomial") from exc
    normalized = sp.factor(polynomial.as_expr())
    if normalized == 0:
        raise ValueError("PBW certificate retains a zero coefficient")
    return normalized


def _structure(first: int, second: int) -> dict[int, sp.Expr]:
    return {
        (1, 2): {3: U},
        (2, 1): {3: -U},
        (2, 3): {1: V},
        (3, 2): {1: -V},
        (3, 1): {2: V},
        (1, 3): {2: -V},
    }.get((first, second), {})


@lru_cache(maxsize=None)
def _reduce_word(word: tuple[int, ...]) -> tuple[tuple[tuple[int, ...], sp.Expr], ...]:
    inversion = next(
        (index for index in range(len(word) - 1) if word[index] > word[index + 1]),
        None,
    )
    if inversion is None:
        return ((word, sp.S.One),)
    left, right = word[inversion], word[inversion + 1]
    swapped = word[:inversion] + (right, left) + word[inversion + 2 :]
    output = dict(_reduce_word(swapped))
    for target, coefficient in _structure(left, right).items():
        shorter = word[:inversion] + (target,) + word[inversion + 2 :]
        for reduced, nested in _reduce_word(shorter):
            output[reduced] = output.get(reduced, 0) + coefficient * nested
    return tuple(
        (reduced, sp.factor(coefficient))
        for reduced, coefficient in sorted(output.items())
        if sp.factor(coefficient) != 0
    )


def _normalize(terms: ScalarOperator) -> ScalarOperator:
    output: ScalarOperator = {}
    for word, coefficient in terms.items():
        for reduced, factor in _reduce_word(word):
            output[reduced] = output.get(reduced, 0) + coefficient * factor
    return {
        word: value
        for word, coefficient in sorted(output.items())
        if (value := sp.factor(sp.cancel(coefficient))) != 0
    }


def _add(*operators: ScalarOperator) -> ScalarOperator:
    terms: ScalarOperator = {}
    for operator in operators:
        for word, coefficient in operator.items():
            terms[word] = terms.get(word, 0) + coefficient
    return _normalize(terms)


def _scale(operator: ScalarOperator, coefficient: sp.Expr) -> ScalarOperator:
    return _normalize({word: coefficient * value for word, value in operator.items()})


def _compose(outer: ScalarOperator, inner: ScalarOperator) -> ScalarOperator:
    # Distinct pairs of monomials can produce the same concatenated word.
    # Accumulate those products before PBW reduction; a dict comprehension
    # would silently retain only the final cross term.
    products: ScalarOperator = {}
    for outer_word, outer_coefficient in outer.items():
        for inner_word, inner_coefficient in inner.items():
            word = outer_word + inner_word
            products[word] = (
                products.get(word, sp.S.Zero)
                + outer_coefficient * inner_coefficient
            )
    return _normalize(products)


def _adjoint(operator: ScalarOperator) -> ScalarOperator:
    return _normalize(
        {
            tuple(reversed(word)): (-1) ** len(word) * coefficient
            for word, coefficient in operator.items()
        }
    )


def _load_record(
    name: str,
    record: object,
) -> tuple[OperatorMatrix, dict[str, object]]:
    value = _require_fields(record, {"shape", "entries", "sha256"}, name)
    expected_shape = EXPECTED_SHAPES[name]
    if value["shape"] != list(expected_shape):
        raise ValueError(f"{name} PBW shape drifted")
    entries = value["entries"]
    if not isinstance(entries, list):
        raise ValueError(f"{name} PBW entries are not a list")
    body = {"shape": value["shape"], "entries": entries}
    if _require_hash(value["sha256"], f"{name} PBW") != _canonical_hash(body):
        raise ValueError(f"{name} PBW record hash mismatch")

    rows, columns = expected_shape
    matrix: OperatorMatrix = [[{} for _ in range(columns)] for _ in range(rows)]
    seen_entries: set[tuple[int, int]] = set()
    term_count = 0
    maximum_order = -1
    for entry in entries:
        if not isinstance(entry, list) or len(entry) != 3:
            raise ValueError(f"{name} has a malformed PBW matrix entry")
        row, column, terms = entry
        if (
            not isinstance(row, int)
            or isinstance(row, bool)
            or not 0 <= row < rows
            or not isinstance(column, int)
            or isinstance(column, bool)
            or not 0 <= column < columns
            or (row, column) in seen_entries
        ):
            raise ValueError(f"{name} has a duplicate or out-of-range matrix entry")
        seen_entries.add((row, column))
        if not isinstance(terms, list) or not terms:
            raise ValueError(f"{name} has an empty PBW matrix entry")
        operator: ScalarOperator = {}
        for term in terms:
            if not isinstance(term, list) or len(term) != 2:
                raise ValueError(f"{name} has a malformed PBW term")
            exponents, coefficient = term
            if (
                not isinstance(exponents, list)
                or len(exponents) != 4
                or any(
                    not isinstance(order, int) or isinstance(order, bool) or order < 0
                    for order in exponents
                )
            ):
                raise ValueError(f"{name} has an invalid PBW exponent vector")
            word = tuple(
                axis
                for axis, multiplicity in enumerate(exponents)
                for _ in range(multiplicity)
            )
            if word in operator:
                raise ValueError(f"{name} repeats a PBW monomial")
            if not isinstance(coefficient, str):
                raise ValueError(f"{name} PBW coefficient is not a string")
            operator[word] = _parse_coefficient(coefficient)
            term_count += 1
            maximum_order = max(maximum_order, len(word))
        matrix[row][column] = operator
    if maximum_order != EXPECTED_MAXIMUM_ORDERS[name]:
        raise ValueError(f"{name} maximum differential order drifted")
    return matrix, {
        "shape": list(expected_shape),
        "sha256": value["sha256"],
        "nonzero_matrix_entries": len(entries),
        "pbw_term_count": term_count,
        "maximum_differential_order": maximum_order,
    }


def _multiply(outer: OperatorMatrix, inner: OperatorMatrix) -> OperatorMatrix:
    if len(outer[0]) != len(inner):
        raise ValueError("PBW operator matrix shape mismatch")
    return [
        [
            _add(
                *(
                    _compose(outer[row][middle], inner[middle][column])
                    for middle in range(len(inner))
                )
            )
            for column in range(len(inner[0]))
        ]
        for row in range(len(outer))
    ]


def _all_zero(matrix: OperatorMatrix) -> bool:
    return all(not value for row in matrix for value in row)


def validate_classical_retained_q1(
    payload: dict[str, Any],
    schema: dict[str, Any],
    layout: dict[str, Any],
) -> dict[str, dict[str, object]]:
    """Validate and independently reproduce the retained minimal-q1 claims."""

    _validate_schema(schema)
    required = {
        "schema",
        "result_id",
        "setting_id",
        "claim_status",
        "dependency_tags",
        "layout_ref",
        "coefficient_ring",
        "pbw_convention",
        "action_inputs",
        "q1_blocks",
        "bach_PBW_term_counts_by_order",
        "exact_checks",
        "flags",
        "next_gate",
        "claim_boundary",
    }
    if set(payload) != required:
        raise ValueError("classical retained-q1 certificate has the wrong field set")
    if (
        payload["schema"] != "pure-weyl-berger-retained-minimal-operator-v1"
        or payload["result_id"] != "BERGER_RETAINED_MINIMAL_OPERATOR"
        or payload["setting_id"]
        != "compact_positive_berger_clock_fixed_coupling_linearized"
        or payload["claim_status"] != "CERTIFIED_COMPLETE_MINIMAL_Q1"
        or payload["dependency_tags"] != ["LOCAL-ALGEBRAIC"]
        or payload["coefficient_ring"]
        != "Q(alpha_B,u,v)[e0,e1,e2,e3]_PBW with u=c/a^2, v=1/c"
    ):
        raise ValueError("classical retained-q1 identity or scope drifted")
    layout_ref = _require_fields(
        payload["layout_ref"],
        {"result_id", "payload_sha256", "component_count"},
        "retained-q1 layout reference",
    )
    if layout_ref["result_id"] != "BERGER_RETAINED_MINIMAL_LAYOUT" or layout_ref[
        "component_count"
    ] != 26:
        raise ValueError("classical retained-q1 layout reference drifted")
    _validate_layout(layout, layout_ref["payload_sha256"])

    convention = payload["pbw_convention"]
    if (
        convention.get("ordered_words") != "e0^n0 e1^n1 e2^n2 e3^n3"
        or convention.get("formal_adjoint")
        != "e_mu^sharp=-e_mu in the unimodular invariant Berger frame"
        or convention.get("commutators")
        != {
            "[e0,ei]": "0",
            "[e1,e2]": "u e3",
            "[e2,e3]": "v e1",
            "[e3,e1]": "v e2",
        }
    ):
        raise ValueError("classical retained-q1 PBW convention drifted")

    blocks = payload["q1_blocks"]
    if not isinstance(blocks, dict) or set(blocks) != set(EXPECTED_SHAPES):
        raise ValueError("classical retained-q1 block inventory drifted")
    gauge, gauge_summary = _load_record("K_spatial", blocks["K_spatial"])
    hessian, hessian_summary = _load_record("H_retained", blocks["H_retained"])
    noether, noether_summary = _load_record(
        "minus_K_spatial_sharp", blocks["minus_K_spatial_sharp"]
    )

    for row in range(10):
        for column in range(10):
            if _add(hessian[row][column], _scale(_adjoint(hessian[column][row]), -1)):
                raise ValueError("retained Berger Hessian is not formally self-adjoint")
    for row in range(3):
        for column in range(10):
            if _add(noether[row][column], _adjoint(gauge[column][row])):
                raise ValueError("retained Berger Noether row is not minus K sharp")
    if not _all_zero(_multiply(hessian, gauge)):
        raise ValueError("retained Berger H K Noether composition is nonzero")
    if not _all_zero(_multiply(noether, hessian)):
        raise ValueError("retained Berger minus-K-sharp H composition is nonzero")

    flags = payload["flags"]
    for name in (
        "retained_Bach_lower_order_PBW_complete",
        "retained_q1_coefficients_complete",
        "retained_q1_squared_verified",
        "retained_cyclicity_verified",
        "BERGER_RETAINED_MINIMAL_OPERATOR",
    ):
        if flags.get(name) is not True:
            raise ValueError(f"classical retained-q1 proved flag dropped: {name}")
    for name in (
        "BERGER_NONMINIMAL_COMPLETION",
        "BERGER_CAUSAL_GREEN_HOMOTOPY",
        "CLASSICAL_SUPPORT_LOCAL_Q1_Q2_EXPORT",
    ):
        if flags.get(name) is not False:
            raise ValueError(f"classical retained-q1 downstream gate promoted: {name}")
    if payload["next_gate"] != "BERGER_NONMINIMAL_COMPLETION":
        raise ValueError("classical retained-q1 next gate drifted")
    return {
        "K_spatial": gauge_summary,
        "H_retained": hessian_summary,
        "minus_K_spatial_sharp": noether_summary,
    }


def _validate_registration(status: dict[str, Any], theorem_sha256: str) -> None:
    if (
        status.get("schema") != "pure-weyl-classical-d-quotient-status-v1"
        or status.get("claim_state") != "PARTIAL"
        or status.get("source_commit") != THEOREM_COMMIT
    ):
        raise ValueError("classical retained-q1 registration identity drifted")
    matches = [
        item
        for item in status.get("evidence_artifacts", [])
        if item.get("evidence_id") == "berger_retained_minimal_operator"
    ]
    if len(matches) != 1:
        raise ValueError("classical retained-q1 registration is absent or duplicated")
    evidence = matches[0]
    if (
        evidence.get("path") != CERTIFICATE_RELATIVE
        or evidence.get("sha256") != theorem_sha256
        or evidence.get("dependency_tags") != ["LOCAL-ALGEBRAIC"]
    ):
        raise ValueError("classical retained-q1 registration provenance drifted")


@lru_cache(maxsize=1)
def _build_import_cached() -> dict[str, Any]:
    theorem_blob = _git_blob(CERTIFICATE_RELATIVE, commit=THEOREM_COMMIT)
    repaired_blob = _git_blob(CERTIFICATE_RELATIVE, commit=SCHEMA_COMMIT)
    if theorem_blob != repaired_blob:
        raise ValueError("retained-q1 certificate changed during the schema-only repair")
    theorem_sha256 = hashlib.sha256(theorem_blob).hexdigest()
    payload = json.loads(theorem_blob)
    schema = _git_json(SCHEMA_RELATIVE, commit=SCHEMA_COMMIT)
    layout = _git_json(LAYOUT_RELATIVE, commit=THEOREM_COMMIT)
    summaries = validate_classical_retained_q1(payload, schema, layout)
    _validate_registration(
        _git_json(STATUS_RELATIVE, commit=REGISTRATION_COMMIT), theorem_sha256
    )

    classical_sources = {
        "operator_certificate": _artifact(CERTIFICATE_RELATIVE, commit=THEOREM_COMMIT),
        "portable_schema": _artifact(SCHEMA_RELATIVE, commit=SCHEMA_COMMIT),
        "retained_layout": _artifact(LAYOUT_RELATIVE, commit=THEOREM_COMMIT),
        "classical_registration": _artifact(
            STATUS_RELATIVE, commit=REGISTRATION_COMMIT
        ),
        "operator_producer": _artifact(PRODUCER_RELATIVE, commit=THEOREM_COMMIT),
        "classical_independent_verifier": _artifact(
            INDEPENDENT_VERIFIER_RELATIVE, commit=SCHEMA_COMMIT
        ),
        "schema_regression_test": _artifact(
            SCHEMA_TEST_RELATIVE, commit=SCHEMA_COMMIT
        ),
        "classical_report": _artifact(REPORT_RELATIVE, commit=THEOREM_COMMIT),
    }
    return {
        "schema": SCHEMA_ID,
        "result_id": "BERGER_RETAINED_MINIMAL_Q1_IMPORT",
        "result_state": "RETAINED_26_ROW_MINIMAL_Q1_IMPORTED_ND2_INPUT_INCOMPLETE",
        "lifecycle_layer": "CLASSICAL_BV",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "setting_id": "compact_positive_berger_clock_fixed_coupling_linearized",
        "phase_space_id": "positive_berger_fixed_coupling_linearized_solutions",
        "classical_result": {
            "result_id": payload["result_id"],
            "claim_status": payload["claim_status"],
            "theorem_commit": THEOREM_COMMIT,
            "registration_commit": REGISTRATION_COMMIT,
            "portable_schema_commit": SCHEMA_COMMIT,
            "certificate_sha256": theorem_sha256,
            "schema_sha256": classical_sources["portable_schema"]["sha256"],
            "layout_payload_sha256": payload["layout_ref"]["payload_sha256"],
        },
        "coverage": {
            "retained_minimal_rows": 26,
            "retained_minimal_q1_rows_complete": True,
            "contracted_clock_rows_separate": 8,
            "full_minimal_rows": 34,
            "nonminimal_rows_complete": False,
            "complete_classical_contraction": False,
        },
        "operator_summary": {
            "coefficient_ring": payload["coefficient_ring"],
            "ordered_pbw_basis": payload["pbw_convention"]["ordered_words"],
            "blocks": summaries,
        },
        "independent_checks": {
            "draft_2020_12_strict_pbw_contract": "VERIFIED_NATIVE_SUBSET_AND_AJV_UPSTREAM",
            "schema_repair_preserves_theorem_blob": True,
            "authoritative_26_row_layout": True,
            "exact_declared_polynomial_coefficients": True,
            "canonical_block_hashes": True,
            "finite_differential_order_support_locality": True,
            "H_retained_formally_self_adjoint": True,
            "minus_K_spatial_sharp_exact": True,
            "H_retained_K_spatial_zero": True,
            "minus_K_spatial_sharp_H_retained_zero": True,
            "q1_retained_squared_zero": True,
            "q1_retained_cyclic": True,
        },
        "nd2_gate": {
            "retained_minimal_q1": "AVAILABLE_VERIFIED_PREREQUISITE",
            "support_local_q1_q2_D": "NOT_AVAILABLE",
            "classical_contraction": "NOT_AVAILABLE",
            "admissibility_policy": "NOT_AVAILABLE",
            "physical_execution_authorized": False,
            "next_gate": "BERGER_NONMINIMAL_COMPLETION_AND_SUPPORT_LOCAL_Q2_D_EXPORT",
        },
        "provenance": {
            "classical_sources": classical_sources,
            "classical_sources_sha256": _canonical_hash(classical_sources),
        },
        "claim_boundary": (
            "The complete support-local cyclic 26-row retained minimal q1 is "
            "independently imported as a LOCAL-ALGEBRAIC prerequisite. The eight-row "
            "clock SDR remains a separate partial import. Nonminimal rows, a complete "
            "classical contraction, q2, the D action and equivariance, admissibility, "
            "causal Green theory, and every interacting or quantum verdict remain open."
        ),
    }


def build_import() -> dict[str, Any]:
    return deepcopy(_build_import_cached())
