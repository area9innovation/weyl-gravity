"""Pinned independent import of the bare-complex unary D-Cartan obstruction."""

from __future__ import annotations

from copy import deepcopy
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any

import sympy as sp

from local_bv.schema_validation import validate_instance

from .berger_gauge_fixed_nonminimal_import import _load_record as _load_operator_record
from .berger_retained_q1_import import (
    ALPHA_B,
    U,
    V,
    _load_record as _load_q1_record,
)


TRANSFER_ROOT = Path(__file__).resolve().parent
ROOT = TRANSFER_ROOT.parents[1]
CLASSICAL_COMMIT = "f6c42ce5e65318d6e982223999abdcefad10edb5"
CLASSICAL_CERTIFICATE = (
    "d_quotient_classical/certificates/"
    "BERGER_UNARY_D_CARTAN_MICROLOCAL_OBSTRUCTION.json"
)
CLASSICAL_SCHEMA = (
    "d_quotient_classical/schema/"
    "berger-unary-D-Cartan-microlocal-obstruction-v1.schema.json"
)
CLASSICAL_Q1 = "d_quotient_classical/certificates/BERGER_RETAINED_MINIMAL_OPERATOR.json"
CLASSICAL_D = "d_quotient_classical/certificates/BERGER_54_ROW_LOCAL_D_ACTION.json"
CLASSICAL_ARTIFACTS = (
    CLASSICAL_CERTIFICATE,
    CLASSICAL_SCHEMA,
    CLASSICAL_Q1,
    CLASSICAL_D,
    "d_quotient_classical/backreacted_clock/berger_unary_d_cartan_obstruction.py",
    "d_quotient_classical/backreacted_clock/verify_berger_unary_d_cartan_obstruction.py",
    "d_quotient_classical/backreacted_clock/tests/test_berger_unary_d_cartan_obstruction.py",
    "d_quotient_classical/reports/berger-unary-D-Cartan-microlocal-obstruction.md",
)
GAUGE_IMPORT = TRANSFER_ROOT / "certificates/BERGER_GAUGE_FIXED_NONMINIMAL_IMPORT.json"
D_IMPORT = TRANSFER_ROOT / "certificates/BERGER_54_ROW_LOCAL_D_IMPORT.json"
SCHEMA_ID = "quantum-weyl-berger-unary-d-cartan-obstruction-import-v1"


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
    if result.returncode:
        raise ValueError(f"missing pinned unary-obstruction artifact: {relative}")
    return result.stdout


def _git_json(relative: str) -> dict[str, Any]:
    value = json.loads(_git_blob(relative))
    if not isinstance(value, dict):
        raise ValueError(f"pinned unary-obstruction JSON is not an object: {relative}")
    return value


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_hash(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _artifact(relative: str) -> dict[str, str]:
    return {
        "path": relative,
        "commit": CLASSICAL_COMMIT,
        "sha256": _sha256_bytes(_git_blob(relative)),
    }


def _matrix_record(matrix: sp.Matrix) -> dict[str, object]:
    entries = [[sp.sstr(sp.factor(matrix[row, column])) for column in range(matrix.cols)] for row in range(matrix.rows)]
    body: dict[str, object] = {"shape": [matrix.rows, matrix.cols], "entries": entries}
    return {**body, "sha256": _canonical_hash(body)}


def _principal_symbol(
    matrix: list[list[dict[tuple[int, ...], sp.Expr]]],
    order: int,
    covector: tuple[int, int, int, int],
) -> sp.Matrix:
    specialization = {
        ALPHA_B: sp.Integer(5),
        U: 3 * sp.sqrt(10) / 20,
        V: 2 * sp.sqrt(10) / 3,
    }
    output = sp.zeros(len(matrix), len(matrix[0]))
    for row, values in enumerate(matrix):
        for column, operator in enumerate(values):
            value = sp.S.Zero
            for word, coefficient in operator.items():
                if len(word) == order:
                    monomial = sp.prod(covector[axis] for axis in word)
                    value += coefficient * monomial
            output[row, column] = sp.factor(value.subs(specialization))
            if output[row, column].free_symbols:
                raise ValueError("principal symbol retained undeclared parameters")
    return output


def _require_source_identity(payload: dict[str, Any], schema: dict[str, Any]) -> None:
    errors = validate_instance(payload, schema)
    if errors:
        raise ValueError(f"classical unary-obstruction schema validation failed: {errors}")
    expected_fields = {
        "schema", "result_id", "setting_id", "claim_status", "dependency_tags", "method_tags",
        "dependency_refs", "douglis_symbol_fixture", "normalized_field_class",
        "obstruction_argument", "exact_checks", "flags", "next_gate", "claim_boundary",
    }
    if set(payload) != expected_fields:
        raise ValueError("classical unary-obstruction field set drifted")
    if (
        payload.get("schema")
        != "pure-weyl-berger-unary-D-Cartan-microlocal-obstruction-v1"
        or payload.get("result_id") != "BERGER_UNARY_D_CARTAN_MICROLOCAL_OBSTRUCTION"
        or payload.get("claim_status")
        != "CERTIFIED_NO_LOCAL_UNARY_CARTAN_ON_BARE_COMPLEX"
        or payload.get("dependency_tags") != ["LOCAL-ALGEBRAIC"]
        or payload.get("method_tags") != ["MICROLOCAL-SYMBOL"]
        or payload.get("next_gate") != "BERGER_RESIDUAL_OR_CAUSAL_CARTAN_EXTENSION"
    ):
        raise ValueError("classical unary-obstruction identity or boundary drifted")


def validate_import(
    payload: dict[str, Any],
    schema: dict[str, Any],
    q1: dict[str, Any],
    d_action: dict[str, Any],
    gauge_import: dict[str, Any],
    d_import: dict[str, Any],
) -> dict[str, Any]:
    """Recompute the exact null-symbol class without producer code."""

    _require_source_identity(payload, schema)
    refs = payload["dependency_refs"]
    if (
        refs.get("retained_q1")
        != {"result_id": "BERGER_RETAINED_MINIMAL_OPERATOR", "sha256": _sha256_bytes(_git_blob(CLASSICAL_Q1))}
        or refs.get("local_D_action")
        != {"result_id": "BERGER_54_ROW_LOCAL_D_ACTION", "sha256": _sha256_bytes(_git_blob(CLASSICAL_D))}
    ):
        raise ValueError("unary-obstruction dependency hashes drifted")

    k, _ = _load_q1_record("K_spatial", q1["q1_blocks"]["K_spatial"])
    h, _ = _load_q1_record("H_retained", q1["q1_blocks"]["H_retained"])
    noether, _ = _load_q1_record(
        "minus_K_spatial_sharp", q1["q1_blocks"]["minus_K_spatial_sharp"]
    )
    d26 = _load_operator_record(
        "retained_D_action", d_action["retained_D_action"]["matrix"], (26, 26)
    )
    covector = (1, 1, 0, 0)
    k1 = _principal_symbol(k, 1, covector)
    h4 = _principal_symbol(h, 4, covector)
    l1 = _principal_symbol(noether, 1, covector)
    d1 = _principal_symbol(d26, 1, covector)
    if h4 * k1 != sp.zeros(10, 3) or l1 * h4 != sp.zeros(3, 10):
        raise ValueError("pinned null symbols do not form a complex")
    if d1 != sp.eye(26):
        raise ValueError("D symbol is not identity at the pinned null covector")

    representative = sp.eye(10)[:, 2]
    dual = sp.zeros(10, 1)
    dual[2], dual[5] = 1, -1
    if h4 * representative != sp.zeros(10, 1):
        raise ValueError("pinned representative is not H4-closed")
    if dual.T * k1 != sp.zeros(1, 3):
        raise ValueError("pinned dual does not annihilate the gauge image")
    if (dual.T * representative)[0] != 1:
        raise ValueError("pinned dual witness is not normalized")

    ranks = {"K1": int(k1.rank()), "H4": int(h4.rank()), "L1": int(l1.rank())}
    cohomology = [
        3 - ranks["K1"],
        10 - ranks["H4"] - ranks["K1"],
        10 - ranks["L1"] - ranks["H4"],
        3 - ranks["L1"],
    ]
    fixture = payload["douglis_symbol_fixture"]
    if (
        ranks != {"K1": 3, "H4": 1, "L1": 3}
        or cohomology != [0, 6, 6, 0]
        or fixture.get("covector") != list(covector)
        or fixture.get("metric_square") != 0
        or fixture.get("D_symbol") != 1
        or fixture.get("symbol_ranks") != ranks
        or fixture.get("cohomology_dimensions") != cohomology
    ):
        raise ValueError("unary-obstruction symbol ledger drifted")
    records = {
        "K1": _matrix_record(k1),
        "H4": _matrix_record(h4),
        "L1": _matrix_record(l1),
        "D1": _matrix_record(d1),
    }
    if fixture.get("specialized_symbol_sha256") != {
        name: _canonical_hash(record["entries"]) for name, record in records.items()
    }:
        raise ValueError("unary-obstruction specialized symbol hashes drifted")
    for name, matrix in {"K1": k1, "H4": h4, "L1": l1}.items():
        minor = fixture.get("rank_witness_minors", {}).get(name, {})
        rows, columns = minor.get("rows"), minor.get("columns")
        if (
            not isinstance(rows, list)
            or not isinstance(columns, list)
            or str(matrix.extract(rows, columns).det()) != minor.get("determinant")
            or sp.Rational(minor["determinant"]) == 0
        ):
            raise ValueError("unary-obstruction rank-minor witness drifted")
    witness = payload["normalized_field_class"]
    if (
        witness.get("representative") != [str(value) for value in representative]
        or witness.get("dual_witness") != [str(value) for value in dual]
        or witness.get("dual_on_representative") != "1"
    ):
        raise ValueError("unary-obstruction normalized witness drifted")

    gauge_checks = gauge_import.get("independent_checks", {})
    d_checks = d_import.get("independent_checks", {})
    if (
        gauge_import.get("result_id") != "BERGER_GAUGE_FIXED_NONMINIMAL_IMPORT"
        or gauge_import.get("coverage", {}).get("total_rows") != 54
        or not all(
            gauge_checks.get(name) is True
            for name in (
                "all_row_contraction_identity", "iota_cl_chain_map",
                "pi_cl_chain_map", "pi_cl_iota_cl_identity",
                "retained_complex_cohomology_preserved_by_SDR",
            )
        )
        or d_import.get("result_id") != "BERGER_54_ROW_LOCAL_D_ACTION_IMPORT"
        or not all(
            d_checks.get(name) is True
            for name in (
                "D_homotopy_equivariant", "D_iota_equivariant",
                "D_projection_equivariant", "q1_D_commutator_zero",
            )
        )
    ):
        raise ValueError("54-to-26 D-equivariant SDR dependency drifted")

    return {
        "schema": SCHEMA_ID,
        "result_id": "BERGER_UNARY_D_CARTAN_MICROLOCAL_OBSTRUCTION_IMPORT",
        "result_state": "BARE_26_AND_54_ROW_LOCAL_UNARY_D_CARTAN_EXACTLY_OBSTRUCTED_EXTENSION_REQUIRED",
        "lifecycle_layer": "CLASSICAL_BV",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "source_dependency_tags": payload["dependency_tags"],
        "source_method_tags": payload["method_tags"],
        "setting_id": payload["setting_id"],
        "obstructed_operator_class": {
            "arity": 1,
            "degree": -1,
            "finite_differential_order": True,
            "support_local": True,
            "bare_rows": [26, 54],
            "identity": "q1 iota_D^(1)+iota_D^(1) q1=D",
        },
        "exact_symbol_replay": {
            "covector": list(covector),
            "metric_square": 0,
            "D_symbol": 1,
            "symbol_ranks": ranks,
            "cohomology_dimensions": cohomology,
            **records,
        },
        "normalized_obstruction_witness": {
            "representative_name": "h_hat_02",
            "representative": [str(value) for value in representative],
            "dual_witness_name": "coefficient(h_hat_02)-coefficient(h_hat_12)",
            "dual_witness": [str(value) for value in dual],
            "H4_on_representative": "0",
            "dual_on_im_K1": "0",
            "dual_on_representative": "1",
            "D_symbol_on_class": "identity",
        },
        "independent_exact_checks": {
            "source_schema_valid": True,
            "source_dependency_hashes_match": True,
            "null_covector_nonzero": True,
            "D_symbol_invertible": True,
            "Douglis_symbol_is_complex": True,
            "symbol_cohomology_dimensions_recomputed": True,
            "field_representative_closed": True,
            "dual_annihilates_gauge_image": True,
            "dual_witness_normalized": True,
            "D_equivariant_SDR_descent_to_54_rows": True,
            "source_specialized_symbol_hashes_match": True,
            "source_rank_minor_witnesses_match": True,
        },
        "descent_to_54_rows": {
            "status": "VERIFIED_FROM_IMPORTED_D_EQUIVARIANT_SDR",
            "formula": "pi_cl iota_D,54^(1) iota_cl",
            "gauge_fixed_import_sha256": _sha256(GAUGE_IMPORT),
            "local_D_import_sha256": _sha256(D_IMPORT),
        },
        "claim_flags": {
            "BERGER_UNARY_D_CARTAN_LOCAL_BARE_COMPLEX_NO_GO": True,
            "BERGER_UNARY_D_CARTAN_EXISTENCE_FULL_4D": False,
            "BERGER_ARITY_TWO_D_CARTAN_SOURCE_FULL_4D": False,
            "BERGER_ARITY_TWO_D_CARTAN_FULL_4D": False,
            "BERGER_RESIDUAL_OR_CAUSAL_CARTAN_EXTENSION": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "BERGER_RESIDUAL_OR_CAUSAL_CARTAN_EXTENSION",
        "provenance": {
            "classical_commit": CLASSICAL_COMMIT,
            "classical_sources": [_artifact(path) for path in CLASSICAL_ARTIFACTS],
            "quantum_dependency_certificates": {
                str(GAUGE_IMPORT.relative_to(ROOT)): _sha256(GAUGE_IMPORT),
                str(D_IMPORT.relative_to(ROOT)): _sha256(D_IMPORT),
            },
        },
        "claim_boundary": (
            "This exact LOCAL-ALGEBRAIC microlocal import rules out a finite-order "
            "support-local unary D-Cartan homotopy on the declared bare retained "
            "26-row complex and, through the imported D-equivariant SDR, on its "
            "bare 54-row extension. It does not rule out residual/BFV rows, the "
            "derived zero-charge quotient, a causal Green extension, nonlocal "
            "homotopies, or any quantum construction."
        ),
    }


@lru_cache(maxsize=1)
def _build_cached() -> dict[str, Any]:
    return validate_import(
        _git_json(CLASSICAL_CERTIFICATE),
        _git_json(CLASSICAL_SCHEMA),
        _git_json(CLASSICAL_Q1),
        _git_json(CLASSICAL_D),
        json.loads(GAUGE_IMPORT.read_text(encoding="utf-8")),
        json.loads(D_IMPORT.read_text(encoding="utf-8")),
    )


def build_import() -> dict[str, Any]:
    return deepcopy(_build_cached())
