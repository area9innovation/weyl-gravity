#!/usr/bin/env python3
"""Independent exact verifier for the tau-adic causal trace obstruction."""

from __future__ import annotations

from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = (
    ROOT
    / "d_quotient_classical/certificates/"
    "TAU_ADIC_VACUUM_CYLINDER_CAUSAL_BV_TRACE_OBSTRUCTION_V1.json"
)
SCHEMA = (
    ROOT
    / "d_quotient_classical/schema/"
    "tau-adic-vacuum-cylinder-causal-bv-trace-obstruction-v1.schema.json"
)

Matrix = list[list[Fraction]]


def _digest(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _fraction(value: int | dict[str, int]) -> Fraction:
    if isinstance(value, int):
        return Fraction(value)
    return Fraction(value["numerator"], value["denominator"])


def _matrix(record: dict[str, Any]) -> Matrix:
    canonical = {
        "row_count": record["row_count"],
        "column_count": record["column_count"],
        "entries": record["entries"],
    }
    if _digest(canonical) != record["sha256"]:
        raise AssertionError("sparse matrix content hash mismatch")
    value = [
        [Fraction() for _ in range(record["column_count"])]
        for _ in range(record["row_count"])
    ]
    for entry in record["entries"]:
        row = entry["row"]
        column = entry["column"]
        if not (
            0 <= row < record["row_count"]
            and 0 <= column < record["column_count"]
        ):
            raise AssertionError("sparse matrix entry is outside its shape")
        if value[row][column]:
            raise AssertionError("duplicate sparse matrix entry")
        value[row][column] = _fraction(entry["coefficient"])
    return value


def _zero(rows: int, columns: int) -> Matrix:
    return [[Fraction() for _ in range(columns)] for _ in range(rows)]


def _identity(dimension: int) -> Matrix:
    value = _zero(dimension, dimension)
    for index in range(dimension):
        value[index][index] = Fraction(1)
    return value


def _transpose(value: Matrix) -> Matrix:
    return [list(row) for row in zip(*value)]


def _add(left: Matrix, right: Matrix) -> Matrix:
    return [
        [a + b for a, b in zip(left_row, right_row)]
        for left_row, right_row in zip(left, right)
    ]


def _multiply(left: Matrix, right: Matrix) -> Matrix:
    return [
        [
            sum(
                (left[i][k] * right[k][j] for k in range(len(right))),
                Fraction(),
            )
            for j in range(len(right[0]))
        ]
        for i in range(len(left))
    ]


def _inverse(value: Matrix) -> Matrix:
    dimension = len(value)
    work = [row[:] + unit[:] for row, unit in zip(value, _identity(dimension))]
    for column in range(dimension):
        pivot = next(
            (
                row
                for row in range(column, dimension)
                if work[row][column]
            ),
            None,
        )
        if pivot is None:
            raise AssertionError("declared canonical change is singular")
        work[column], work[pivot] = work[pivot], work[column]
        scale = work[column][column]
        work[column] = [entry / scale for entry in work[column]]
        for row in range(dimension):
            if row == column:
                continue
            scale = work[row][column]
            if scale:
                work[row] = [
                    entry - scale * pivot_entry
                    for entry, pivot_entry in zip(
                        work[row], work[column]
                    )
                ]
    return [row[dimension:] for row in work]


def _rank(value: Matrix) -> int:
    work = [row[:] for row in value]
    rows = len(work)
    columns = len(work[0]) if work else 0
    rank = 0
    for column in range(columns):
        pivot = next(
            (row for row in range(rank, rows) if work[row][column]),
            None,
        )
        if pivot is None:
            continue
        work[rank], work[pivot] = work[pivot], work[rank]
        pivot_value = work[rank][column]
        work[rank] = [entry / pivot_value for entry in work[rank]]
        for row in range(rank + 1, rows):
            scale = work[row][column]
            if scale:
                work[row] = [
                    entry - scale * pivot_entry
                    for entry, pivot_entry in zip(work[row], work[rank])
                ]
        rank += 1
    return rank


def _check_dependencies(value: dict[str, Any]) -> dict[str, dict[str, Any]]:
    loaded: dict[str, dict[str, Any]] = {}
    for name, reference in value["dependencies"].items():
        path = ROOT / reference["path"]
        if hashlib.sha256(path.read_bytes()).hexdigest() != reference["sha256"]:
            raise AssertionError(f"dependency hash mismatch: {name}")
        payload = json.loads(path.read_text(encoding="utf-8"))
        artifact_id = (
            payload.get("result_id")
            or payload.get("schema")
            or path.stem
        )
        if artifact_id != reference["artifact_id"]:
            raise AssertionError(f"dependency identity mismatch: {name}")
        loaded[name] = payload

    strict = loaded["strict_minimal_BV"]
    g_row = next(
        row
        for row in strict["differential"]["Q"]["rows"]
        if row["source_atom"] == "g"
    )
    terms = {
        (entry["coefficient"], tuple(entry["factors"]))
        for entry in g_row["image"]["terms"]
    }
    if terms != {(2, ("g", "omega")), (1, ("Lie_g",))}:
        raise AssertionError("strict local Weyl normalization changed")
    if (
        loaded["strict_action_and_gauge_normalization"]["source"][
            "gauge_transformations"
        ]["Weyl"]
        != "delta g=g sigma, delta b=d sigma, delta phi=0"
    ):
        raise AssertionError("causal endpoint Weyl normalization changed")
    wz = loaded["WZ_minimal_cotangent_lift"]
    if (
        wz["master_term"]["derived_rows"]["Q_tau"]
        != "L_xi tau + omega"
        or wz["dressed_cotangent_change"]["g_hat"]
        != "exp(-2 tau) g"
    ):
        raise AssertionError("Wess-Zumino convention changed")
    if (
        loaded["strict_386_Green_homotopy"]["causal_green_homotopy"]
        is not True
    ):
        raise AssertionError("strict causal input is not certified")
    if (
        "fifteen non-compactly-supported smooth modes"
        not in loaded["global_CKV_guard"]["global_ckv_guard"]
    ):
        raise AssertionError("global conformal-Killing guard changed")
    return loaded


def verify(value: dict[str, Any]) -> None:
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    errors = sorted(
        Draft202012Validator(schema).iter_errors(value),
        key=lambda error: list(error.path),
    )
    if errors:
        raise AssertionError(
            "schema failure: "
            + "; ".join(error.message for error in errors[:8])
        )
    _check_dependencies(value)

    scalar = value["scalar_trace_obstruction"]
    if scalar["fixture_scope"] != "ZEROTH_ORDER_WEYL_TRACE_SUBQUOTIENT":
        raise AssertionError("scalar fixture scope changed")
    if scalar["original_basis"] != [
        "sigma",
        "phi_trace",
        "tau",
        "phi_trace_star",
        "tau_hat_star",
        "sigma_star",
    ]:
        raise AssertionError("original scalar basis changed")
    if scalar["degrees"] != [-1, 0, 0, 1, 1, 2]:
        raise AssertionError("scalar degree ledger changed")

    q = _matrix(scalar["Q_original"])
    pairing = _matrix(scalar["odd_pairing_original"])
    transform = _matrix(scalar["canonical_change_old_from_dressed"])
    stored_inverse = _matrix(scalar["canonical_change_inverse"])
    q_dressed = _matrix(scalar["Q_dressed"])
    pairing_dressed = _matrix(scalar["odd_pairing_dressed"])

    expected_q = _zero(6, 6)
    expected_q[1][0] = Fraction(1)
    expected_q[2][0] = Fraction(1, 2)
    expected_q[5][3] = Fraction(-1)
    expected_q[5][4] = Fraction(-1, 2)
    if q != expected_q:
        raise AssertionError("normalization-sensitive scalar Q changed")

    expected_pairing = _zero(6, 6)
    for field, antifield in ((0, 5), (1, 3), (2, 4)):
        expected_pairing[field][antifield] = Fraction(1)
        expected_pairing[antifield][field] = Fraction(-1)
    if pairing != expected_pairing:
        raise AssertionError("canonical scalar pairing changed")

    inverse = _inverse(transform)
    if inverse != stored_inverse:
        raise AssertionError("stored canonical inverse is not exact")
    if (
        _multiply(q, q) != _zero(6, 6)
        or _add(
            _multiply(_transpose(q), pairing),
            _multiply(pairing, q),
        )
        != _zero(6, 6)
    ):
        raise AssertionError("nilpotency or cyclicity failed")
    if _multiply(_multiply(inverse, q), transform) != q_dressed:
        raise AssertionError("dressed differential was not conjugated")
    if (
        _multiply(_multiply(_transpose(transform), pairing), transform)
        != pairing_dressed
        or pairing_dressed != pairing
    ):
        raise AssertionError("dressed change is not BV canonical")

    expected_dressed = _zero(6, 6)
    expected_dressed[2][0] = Fraction(1)
    expected_dressed[5][4] = Fraction(-1)
    if q_dressed != expected_dressed:
        raise AssertionError("dressed quartet-plus-trace normal form changed")
    rank = _rank(q_dressed)
    if (
        rank != 2
        or scalar["rank_Q"] != rank
        or scalar["subquotient_homology_dimension"] != 6 - 2 * rank
        or scalar["subquotient_homology_dimension"] != 2
    ):
        raise AssertionError("scalar homology dimension changed")

    class_statuses = []
    for record in scalar["normalized_nonboundary_witnesses"]:
        class_statuses.append(
            (record["class_id"], record["full_carrier_status"])
        )
        cycle = _matrix(record["cycle"])
        dual = _matrix(record["dual"])
        if (
            _multiply(q_dressed, cycle) != _zero(6, 1)
            or _multiply(dual, q_dressed) != _zero(1, 6)
            or _multiply(dual, cycle) != [[Fraction(1)]]
        ):
            raise AssertionError("normalized nonboundary witness failed")
    if class_statuses != [
        (
            "DRESSED_CONFORMAL_TRACE_FIELD",
            "PROMOTED_BY_COMPACT_SUPPORT_STOKES_WITNESS",
        ),
        (
            "DRESSED_CONFORMAL_TRACE_COTANGENT",
            "SUBQUOTIENT_ONLY_DIFF_COMPANION_NOT_REMOVED",
        ),
    ]:
        raise AssertionError("obstruction class ledger changed")

    principal = scalar["principal_symbol"]
    support = scalar["compact_support_witness"]
    if (
        principal["Green_inverse_exists"] is not False
        or principal["defect_is_finite_zero_mode"] is not False
        or support["cycle_identity"]
        != "q0(f u)=Bach_linearized(f g_bar)=0"
        or "integral div(xi)" not in support[
            "diffeomorphism_boundary_identity"
        ]
        or support["Weyl_boundary_identity"]
        != "lambda_u(g_bar sigma, sigma/2)=0"
        or "p_end" not in support["lift_to_386"]
        or "exactly fifteen CKV modes"
        not in support["global_CKV_nonmembership"]
        or "one-sided noncompact primitives"
        not in support["dual_functional_scope"]
    ):
        raise AssertionError("support/principal obstruction was promoted")

    classification = value["carrier_classification"]
    for key in (
        "minimal_extension",
        "nonminimal_gauge_fixed_extension",
        "finite_auxiliary_cyclic_extension",
        "past_compact_complete_carrier",
        "future_compact_complete_carrier",
        "time_slice_complete_carrier",
    ):
        if classification[key] != "OBSTRUCTED":
            raise AssertionError(f"carrier disposition changed: {key}")

    if value["claim_flags"] != {
        "STRICT_386_ROW_CAUSAL_COMPLEX_IMPORTED": True,
        "TAU_ADIC_CANONICAL_SCALAR_EXTENSION_ASSEMBLED": True,
        "COMPLETE_DECLARED_FINITE_DIFFERENTIAL_CLASS_OBSTRUCTED": True,
        "FULL_TAU_ADIC_CLASSICAL_CAUSAL_BV_CARRIER": False,
        "FULL_TAU_ADIC_BRST_HADAMARD_KERNEL": False,
        "LORENTZIAN_QME_RESTORED": False,
        "PHYSICAL_POSITIVITY_CERTIFIED": False,
        "PARTICLE_INTERPRETATION_AUTHORIZED": False,
    }:
        raise AssertionError("claim boundary flags changed")


def main() -> None:
    value = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    verify(value)
    print(
        "PASS: independently verified the exact compact-support dressed-trace "
        "homology obstruction to the declared tau-adic causal BV carrier"
    )


if __name__ == "__main__":
    main()
