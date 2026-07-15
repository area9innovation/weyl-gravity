#!/usr/bin/env python3
"""All-row nonminimal extension of the Berger classical unary complex.

Five antighost--multiplier quartets add twenty rows to the portable 34-row
minimal complex.  This module exports the exact 54-to-26 support-local cyclic
contraction and the exact curved five-direction companion used by the future
gauge fermion.  The canonical gauge-fixing shear itself remains a separate,
fail-closed gate.
"""

from __future__ import annotations

import argparse
from copy import deepcopy
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import sys

import sympy as sp

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from d_quotient_classical.backreacted_clock.berger_causal_witness_preflight import (
    _matrix_add,
    _matrix_from_record,
    _symbol,
)
from d_quotient_classical.backreacted_clock.berger_full_gauge_companion import (
    curved_companion,
    full_metric_gauge,
    metric_fibre_identification,
)
from d_quotient_classical.backreacted_clock.berger_linearized_bach_pbw import (
    ROOT,
    LinearOperator,
    ZERO,
    _compose_matrices,
    _matrix_record,
)


MINIMAL_CERTIFICATE = ROOT / "d_quotient_classical/certificates/BERGER_MINIMAL_34_PORTABLE_CONTRACTION.json"
Q1_CERTIFICATE = ROOT / "d_quotient_classical/certificates/BERGER_RETAINED_MINIMAL_OPERATOR.json"
CERTIFICATE_PATH = ROOT / "d_quotient_classical/certificates/BERGER_NONMINIMAL_ALGEBRAIC_COMPLETION.json"
REPORT_PATH = ROOT / "d_quotient_classical/reports/berger-nonminimal-algebraic-completion.md"
SCHEMA_PATH = ROOT / "d_quotient_classical/schema/berger-nonminimal-algebraic-completion-v1.schema.json"


MINIMAL_TO_EXTENDED = (
    0, 1, 2, 3, 4,
    5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16,
    27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38,
    49, 50, 51, 52, 53,
)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def _zero(rows: int, columns: int) -> list[list[LinearOperator]]:
    return [[ZERO for _ in range(columns)] for _ in range(rows)]


def _one(value: sp.Expr = sp.S.One) -> LinearOperator:
    return LinearOperator.from_terms(((0, (), value),))


def _numeric_record(record: dict[str, object]) -> sp.Matrix:
    matrix = _matrix_from_record(record)
    result = sp.zeros(len(matrix), len(matrix[0]))
    for row in range(len(matrix)):
        for column in range(len(matrix[0])):
            operator = matrix[row][column]
            if any(word for _, word, _ in operator.terms):
                raise AssertionError("expected an order-zero contraction record")
            result[row, column] = sum(
                coefficient for _, word, coefficient in operator.terms if not word
            )
    return result


def _record_from_numeric(matrix: sp.MatrixBase) -> dict[str, object]:
    operators = _zero(matrix.rows, matrix.cols)
    for row in range(matrix.rows):
        for column in range(matrix.cols):
            if matrix[row, column] != 0:
                operators[row][column] = _one(matrix[row, column])
    return _matrix_record(operators)


def _row_layout() -> list[dict[str, object]]:
    minimal = json.loads(MINIMAL_CERTIFICATE.read_text())["row_layout"]["component_rows"]
    rows: list[dict[str, object]] = []
    for old, new in enumerate(MINIMAL_TO_EXTENDED):
        source = minimal[old]
        rows.append(
            {
                "index": new,
                "row_id": source["row_id"],
                "degree": source["degree"],
                "sector": "minimal",
            }
        )
    labels = ("diff_1", "diff_2", "diff_3", "tau", "sigma")
    for index, label in enumerate(labels):
        rows.extend(
            (
                {"index": 17 + index, "row_id": f"b_{label}", "degree": 0, "sector": "nonminimal_multiplier"},
                {"index": 22 + index, "row_id": f"bar_c_star_{label}", "degree": 0, "sector": "nonminimal_antighost_dual"},
                {"index": 39 + index, "row_id": f"b_star_{label}", "degree": 1, "sector": "nonminimal_multiplier_dual"},
                {"index": 44 + index, "row_id": f"bar_c_{label}", "degree": 1, "sector": "nonminimal_antighost"},
            )
        )
    return sorted(rows, key=lambda row: row["index"])


def _exact_data() -> dict[str, object]:
    minimal = json.loads(MINIMAL_CERTIFICATE.read_text())
    q1 = json.loads(Q1_CERTIFICATE.read_text())
    if minimal["flags"]["BERGER_COMBINED_MINIMAL_CONTRACTION_ALL_34_ROWS"] is not True:
        raise AssertionError("portable minimal contraction dependency is not certified")

    iota_minimal = _numeric_record(minimal["contraction"]["iota_cl"])
    pi_minimal = _numeric_record(minimal["contraction"]["pi_cl"])
    s_minimal = _numeric_record(minimal["contraction"]["S_cl"])

    iota_nm = sp.zeros(54, 34)
    pi_nm = sp.zeros(34, 54)
    for minimal_index, extended_index in enumerate(MINIMAL_TO_EXTENDED):
        iota_nm[extended_index, minimal_index] = 1
        pi_nm[minimal_index, extended_index] = 1

    q_nm = sp.zeros(54)
    s_nm = sp.zeros(54)
    for index in range(5):
        q_nm[44 + index, 17 + index] = 1
        q_nm[39 + index, 22 + index] = 1
        s_nm[17 + index, 44 + index] = 1
        s_nm[22 + index, 39 + index] = 1

    iota_complete = iota_nm * iota_minimal
    pi_complete = pi_minimal * pi_nm
    s_complete = iota_nm * s_minimal * pi_nm + s_nm
    retained_projector = iota_complete * pi_complete
    complement = sp.eye(54) - retained_projector

    q_contractible = sp.zeros(54)
    q_clock = sp.zeros(34)
    q_clock[15, 4] = -1
    q_clock[16, 3] = 1
    q_clock[32, 28] = -1
    q_clock[33, 27] = 1
    q_contractible += iota_nm * q_clock * pi_nm + q_nm
    if pi_complete * iota_complete != sp.eye(26):
        raise AssertionError("complete pi-iota identity failed")
    if q_contractible * s_complete + s_complete * q_contractible != complement:
        raise AssertionError("54-row contraction identity failed")
    if s_complete * s_complete != sp.zeros(54):
        raise AssertionError("complete homotopy is not square zero")
    if pi_complete * s_complete != sp.zeros(26, 54):
        raise AssertionError("complete pi-S side condition failed")
    if s_complete * iota_complete != sp.zeros(54, 26):
        raise AssertionError("complete S-iota side condition failed")

    omega = sp.zeros(54)
    omega[0:5, 49:54] = sp.eye(5)
    omega[49:54, 0:5] = -sp.eye(5)
    omega[5:27, 27:49] = sp.eye(22)
    omega[27:49, 5:27] = -sp.eye(22)
    if sp.simplify(q_nm.T * omega + omega * q_nm) != sp.zeros(54):
        raise AssertionError("nonminimal unary extension is not cyclic")
    if sp.simplify(s_complete.T * omega + omega * s_complete) != sp.zeros(54):
        raise AssertionError("complete homotopy is not cyclic")

    companion = curved_companion()
    gauge = full_metric_gauge()
    ghost_witness = _compose_matrices(companion, gauge)
    hessian = _matrix_from_record(q1["q1_blocks"]["H_retained"])
    metric_candidate = _matrix_add(
        _compose_matrices(metric_fibre_identification(), hessian),
        _compose_matrices(gauge, companion),
    )
    momenta = sp.symbols("p0:4")
    wave = -momenta[0] ** 2 + sum(momenta[index] ** 2 for index in range(1, 4))
    if sp.simplify(_symbol(ghost_witness, 4) - wave**2 * sp.eye(5)) != sp.zeros(5):
        raise AssertionError("curved companion ghost principal drifted")
    if sp.simplify(_symbol(metric_candidate, 4) - wave**2 * sp.eye(10)) != sp.zeros(10):
        raise AssertionError("curved companion metric principal drifted")

    return {
        "minimal": minimal,
        "q1": q1,
        "q_nm": q_nm,
        "iota_nm": iota_nm,
        "pi_nm": pi_nm,
        "s_nm": s_nm,
        "iota_complete": iota_complete,
        "pi_complete": pi_complete,
        "s_complete": s_complete,
        "companion": companion,
        "ghost_witness": ghost_witness,
        "metric_candidate": metric_candidate,
    }


@dataclass(frozen=True)
class BergerNonminimalAlgebraicCompletion:
    payload: dict[str, object]

    @classmethod
    def build(cls) -> "BergerNonminimalAlgebraicCompletion":
        data = _exact_data()
        payload: dict[str, object] = {
            "schema": "pure-weyl-berger-nonminimal-algebraic-completion-v1",
            "result_id": "BERGER_NONMINIMAL_ALGEBRAIC_COMPLETION",
            "setting_id": data["minimal"]["setting_id"],
            "claim_status": "CERTIFIED_NONMINIMAL_DIRECT_SUM_GAUGE_SHEAR_OPEN",
            "dependency_tags": ["LOCAL-ALGEBRAIC"],
            "dependency_refs": {
                "minimal_34": {
                    "result_id": data["minimal"]["result_id"],
                    "sha256": _sha256(MINIMAL_CERTIFICATE),
                },
                "retained_classical_unary_q1": {
                    "result_id": data["q1"]["result_id"],
                    "sha256": _sha256(Q1_CERTIFICATE),
                },
            },
            "row_layout": {
                "total_rows": 54,
                "degree_ranks": [5, 22, 22, 5],
                "minimal_rows": 34,
                "nonminimal_rows": 20,
                "component_rows": _row_layout(),
                "ghost_order": ["diff_1", "diff_2", "diff_3", "tau", "sigma"],
            },
            "nonminimal_unary_extension": {
                "coordinate_rules": ["ell_1 b=bar_c", "ell_1 bar_c_star=b_star"],
                "matrix": _record_from_numeric(data["q_nm"]),
                "pointwise": True,
                "cyclic": True,
            },
            "contraction": {
                "minimal_iota": _record_from_numeric(data["iota_nm"]),
                "minimal_pi": _record_from_numeric(data["pi_nm"]),
                "S_nonminimal": _record_from_numeric(data["s_nm"]),
                "iota_cl": _record_from_numeric(data["iota_complete"]),
                "pi_cl": _record_from_numeric(data["pi_complete"]),
                "S_cl": _record_from_numeric(data["s_complete"]),
                "identity": "pi_cl iota_cl=1_26 and ell_1 S_cl+S_cl ell_1=1_54-iota_cl pi_cl",
                "side_conditions": ["S_cl^2=0", "pi_cl S_cl=0", "S_cl iota_cl=0"],
                "support_local": True,
                "maximum_differential_order": 0,
                "cyclic": True,
            },
            "gauge_fermion_template": {
                "formula": "Psi=<bar_c,T_Berger h+(alpha_nm/2)b>",
                "coordinate_presentation": "raw metric h with five Diff x Weyl gauge directions; clock SDR target uses dressed h_hat",
                "curved_companion": _matrix_record(data["companion"]),
                "companion_row_orders": [3, 3, 3, 3, 4],
                "ghost_principal_identity": "sigma_4(T_Berger K_full)=(zeta^2)^2 I_5",
                "metric_principal_identity": "sigma_4(J H_retained+K_full T_Berger)=(zeta^2)^2 I_10",
                "canonical_transform_applied": False,
            },
            "exact_checks": {
                "all_54_rows_enumerated": True,
                "nonminimal_unary_squared_zero": True,
                "nonminimal_unary_cyclic": True,
                "complete_54_to_26_contraction": True,
                "complete_contraction_side_conditions": True,
                "complete_homotopy_cyclic": True,
                "support_local_order_zero": True,
                "curved_companion_coefficientwise_derived": True,
                "ghost_scalar_biwave_principal": True,
                "metric_scalar_biwave_principal": True,
            },
            "flags": {
                "BERGER_NONMINIMAL_ROWS_COMPLETE": True,
                "BERGER_NONMINIMAL_DIRECT_SUM_CONTRACTION": True,
                "BERGER_COMPLETE_54_ROW_UNFIXED_CONTRACTION": True,
                "BERGER_CURVED_COMPANION_DERIVED": True,
                "BERGER_GAUGE_FERMION_CANONICAL_TRANSFORM": False,
                "BERGER_NONMINIMAL_COMPLETION": False,
                "BERGER_CURVED_CLOCK_REATTACHED_WITNESS": False,
                "CLASSICAL_SUPPORT_LOCAL_Q2": False,
                "BERGER_LOCAL_D_ACTION_EQUIVARIANT": False,
                "BERGER_GENERAL_KOSZUL_TATE_EXPORT": False,
                "BERGER_CAUSAL_GREEN_HOMOTOPY": False,
                "BERGER_HADAMARD_DATA": False,
                "CLASSICAL_SUPPORT_LOCAL_Q1_Q2_EXPORT": False,
            },
            "next_gate": "BERGER_GAUGE_FERMION_CANONICAL_TRANSFORM",
            "claim_boundary": "This certificate completes the twenty nonminimal direct-sum rows, the exact 54-to-26 support-local cyclic contraction, and the coefficientwise curved companion entering the gauge-fermion template. It does not apply the gauge-fermion canonical shear, certify the resulting gauge-fixed 54-row unary operator, construct ell_2 or local D-equivariance, export the general Koszul-Tate differential, or provide causal Green/Hadamard data.",
        }
        result = cls(payload)
        result.verify()
        return result

    def verify(self) -> None:
        if any(value is not True for value in self.payload["exact_checks"].values()):
            raise AssertionError("nonminimal exact check dropped")
        flags = self.payload["flags"]
        for key in (
            "BERGER_NONMINIMAL_ROWS_COMPLETE",
            "BERGER_NONMINIMAL_DIRECT_SUM_CONTRACTION",
            "BERGER_COMPLETE_54_ROW_UNFIXED_CONTRACTION",
            "BERGER_CURVED_COMPANION_DERIVED",
        ):
            if flags[key] is not True:
                raise AssertionError(f"proved nonminimal flag dropped: {key}")
        for key, value in flags.items():
            if key not in {
                "BERGER_NONMINIMAL_ROWS_COMPLETE",
                "BERGER_NONMINIMAL_DIRECT_SUM_CONTRACTION",
                "BERGER_COMPLETE_54_ROW_UNFIXED_CONTRACTION",
                "BERGER_CURVED_COMPANION_DERIVED",
            } and value is not False:
                raise AssertionError(f"downstream nonminimal flag promoted: {key}")
        if self.payload["next_gate"] != "BERGER_GAUGE_FERMION_CANONICAL_TRANSFORM":
            raise AssertionError("nonminimal next gate drifted")

    def certificate_text(self) -> str:
        return json.dumps(self.payload, indent=2, sort_keys=True) + "\n"

    def report_text(self) -> str:
        return r"""# Berger nonminimal algebraic completion

Five Diff--Weyl antighost--multiplier quartets add twenty rows to the portable
minimal complex. In the suspended tangent convention their arrows are

\[
b_A\longmapsto\bar c_A,
\qquad
\bar c_A^*\longmapsto b_A^*.
\]

The resulting 54-row complex contracts support-locally and cyclically onto
the retained 26-row complex with explicit
\((\iota_{\rm cl},\pi_{\rm cl},S_{\rm cl})\). All contraction entries are
pointwise.

The exact curved companion in the gauge-fermion template

\[
\Psi=\langle\bar c,T_{\rm Berger}h+\tfrac12\alpha_{\rm nm}b\rangle
\]

is also derived coefficientwise. Its metric and ghost principal blocks are
the certified scalar biwaves. The canonical gauge-fermion shear has not yet
been applied, so the combined `BERGER_NONMINIMAL_COMPLETION` flag remains
false. This is an algebraic direct-sum theorem, not yet the gauge-fixed causal
complex.
"""


def _write(result: BergerNonminimalAlgebraicCompletion) -> None:
    CERTIFICATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    CERTIFICATE_PATH.write_text(result.certificate_text())
    REPORT_PATH.write_text(result.report_text())


def _check(result: BergerNonminimalAlgebraicCompletion) -> None:
    if CERTIFICATE_PATH.read_text() != result.certificate_text():
        raise AssertionError("nonminimal certificate drifted")
    if REPORT_PATH.read_text() != result.report_text():
        raise AssertionError("nonminimal report drifted")


def _guards(result: BergerNonminimalAlgebraicCompletion) -> None:
    mutations = [
        ("drop rows", ("flags", "BERGER_NONMINIMAL_ROWS_COMPLETE"), False),
        ("drop contraction", ("flags", "BERGER_COMPLETE_54_ROW_UNFIXED_CONTRACTION"), False),
        ("promote gauge shear", ("flags", "BERGER_GAUGE_FERMION_CANONICAL_TRANSFORM"), True),
        ("promote combined completion", ("flags", "BERGER_NONMINIMAL_COMPLETION"), True),
        ("promote causal", ("flags", "BERGER_CAUSAL_GREEN_HOMOTOPY"), True),
        ("promote q2", ("flags", "CLASSICAL_SUPPORT_LOCAL_Q2"), True),
        ("skip next gate", ("next_gate",), "BERGER_CAUSAL_GREEN_HOMOTOPY"),
    ]
    for name, path, replacement in mutations:
        mutant = deepcopy(result.payload)
        target = mutant
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = replacement
        try:
            BergerNonminimalAlgebraicCompletion(mutant).verify()
        except AssertionError:
            continue
        raise AssertionError(f"mutation guard accepted: {name}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()
    result = BergerNonminimalAlgebraicCompletion.build()
    if args.write:
        _write(result)
    if args.check:
        _check(result)
    if args.guards:
        _guards(result)
    if not (args.write or args.check or args.guards):
        print(result.certificate_text(), end="")
    else:
        print("BERGER_NONMINIMAL_ALGEBRAIC_COMPLETION: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
