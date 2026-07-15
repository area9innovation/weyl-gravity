#!/usr/bin/env python3
"""Gauge-fix the complete 54-row Berger unary BV complex canonically.

The gauge fermion is expressed in the dressed clock coordinates used by the
portable minimal contraction.  Its cotangent lift is an exact local
BV-canonical shear ``U=1+N`` with ``N^2=0``.  Conjugating the unfixed unary
differential and its contraction produces a portable gauge-fixed
``classical_unary_q1`` package.  Nonlinear ``ell_2``, local D-equivariance,
general nonlinear Koszul--Tate data, and causal/Hadamard structures remain
separate fail-closed gates.
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
    _identity_matrix,
    _matrix_add,
)
from d_quotient_classical.backreacted_clock.berger_full_gauge_companion import (
    curved_companion,
    full_metric_gauge,
)
from d_quotient_classical.backreacted_clock.berger_linearized_bach_pbw import (
    LinearOperator,
    ROOT,
    ZERO,
    _adjoint_matrix,
    _matrix_record,
)
from d_quotient_classical.backreacted_clock.berger_minimal_34_portable_contraction import (
    _exact_matrices as _minimal_exact_matrices,
)
from d_quotient_classical.backreacted_clock.berger_nonminimal_algebraic_completion import (
    MINIMAL_TO_EXTENDED,
)


UNFIXED_CERTIFICATE = ROOT / "d_quotient_classical/certificates/BERGER_NONMINIMAL_ALGEBRAIC_COMPLETION.json"
MINIMAL_CERTIFICATE = ROOT / "d_quotient_classical/certificates/BERGER_MINIMAL_34_PORTABLE_CONTRACTION.json"
CERTIFICATE_PATH = ROOT / "d_quotient_classical/certificates/BERGER_GAUGE_FIXED_NONMINIMAL_COMPLETION.json"
REPORT_PATH = ROOT / "d_quotient_classical/reports/berger-gauge-fixed-nonminimal-completion.md"
SCHEMA_PATH = ROOT / "d_quotient_classical/schema/berger-gauge-fixed-nonminimal-completion-v1.schema.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _zero(rows: int, columns: int) -> list[list[LinearOperator]]:
    return [[ZERO for _ in range(columns)] for _ in range(rows)]


def _one(value: sp.Expr = sp.S.One) -> LinearOperator:
    return LinearOperator.from_terms(((0, (), value),))


def _negative(matrix):
    return [[entry.scale(-1) for entry in row] for row in matrix]


def _subtract(left, right):
    return _matrix_add(left, _negative(right))


def _embed(target, block, row_indices, column_indices) -> None:
    rows = row_indices if isinstance(row_indices, tuple) else tuple(range(row_indices, row_indices + len(block)))
    columns = column_indices if isinstance(column_indices, tuple) else tuple(range(column_indices, column_indices + len(block[0])))
    for row, target_row in enumerate(rows):
        for column, target_column in enumerate(columns):
            target[target_row][target_column] = block[row][column]


def _sparse_multiply(outer, inner):
    """Exact PBW multiplication without dense zero compositions."""

    if len(outer[0]) != len(inner):
        raise ValueError("operator matrix shape mismatch")
    output = _zero(len(outer), len(inner[0]))
    inner_support = {
        middle: [(column, entry) for column, entry in enumerate(row) if entry.terms]
        for middle, row in enumerate(inner)
    }
    for row, entries in enumerate(outer):
        for middle, left in enumerate(entries):
            if not left.terms:
                continue
            for column, right in inner_support[middle]:
                output[row][column] = output[row][column] + left.compose(right)
    return output


def _is_zero(matrix) -> bool:
    return all(not entry.terms for row in matrix for entry in row)


def _maximum_order(matrix) -> int:
    return max((entry.maximum_order for row in matrix for entry in row if entry.terms), default=0)


def _unfixed_package():
    minimal = _minimal_exact_matrices()
    q_unfixed = _zero(54, 54)
    _embed(q_unfixed, minimal["q_full"], MINIMAL_TO_EXTENDED, MINIMAL_TO_EXTENDED)
    for index in range(5):
        q_unfixed[44 + index][17 + index] = _one()
        q_unfixed[39 + index][22 + index] = _one()

    minimal_iota = _zero(54, 34)
    minimal_pi = _zero(34, 54)
    for old, new in enumerate(MINIMAL_TO_EXTENDED):
        minimal_iota[new][old] = _one()
        minimal_pi[old][new] = _one()
    iota = _sparse_multiply(minimal_iota, minimal["inclusion"])
    projection = _sparse_multiply(minimal["projection"], minimal_pi)
    homotopy = _sparse_multiply(
        _sparse_multiply(minimal_iota, minimal["homotopy"]), minimal_pi
    )
    for index in range(5):
        homotopy[17 + index][44 + index] = _one()
        homotopy[22 + index][39 + index] = _one()
    return q_unfixed, iota, projection, homotopy


def _gauge_fermion_shear():
    gauge = full_metric_gauge()
    companion = curved_companion()
    raw_metric_from_dressed = _zero(10, 12)
    for index in range(10):
        raw_metric_from_dressed[index][index] = _one()
        raw_metric_from_dressed[index][10] = gauge[index][4].scale(-1)  # -K_sigma R
        raw_metric_from_dressed[index][11] = gauge[index][3]            # +K_tau Theta
    gauge_condition = _sparse_multiply(companion, raw_metric_from_dressed)
    gauge_condition_adjoint = _adjoint_matrix(gauge_condition)

    nilpotent = _zero(54, 54)
    # bar_c^* -> bar_c^* + A x + b/2
    _embed(nilpotent, gauge_condition, 22, 5)
    # x^* -> x^* - A^sharp bar_c and b^* -> b^* - bar_c/2.
    _embed(nilpotent, _negative(gauge_condition_adjoint), 27, 44)
    half = _one(sp.Rational(1, 2))
    for index in range(5):
        nilpotent[22 + index][17 + index] = half
        nilpotent[39 + index][44 + index] = half.scale(-1)

    identity = _identity_matrix(54)
    shear = _matrix_add(identity, nilpotent)
    inverse = _subtract(identity, nilpotent)
    return raw_metric_from_dressed, gauge_condition, nilpotent, shear, inverse


def _pairing():
    omega = _zero(54, 54)
    for index in range(5):
        omega[index][49 + index] = _one()
        omega[49 + index][index] = _one(-1)
    for index in range(22):
        omega[5 + index][27 + index] = _one()
        omega[27 + index][5 + index] = _one(-1)
    return omega


def _exact_data() -> dict[str, object]:
    unfixed = json.loads(UNFIXED_CERTIFICATE.read_text())
    if unfixed["flags"]["BERGER_COMPLETE_54_ROW_UNFIXED_CONTRACTION"] is not True:
        raise AssertionError("unfixed nonminimal dependency is not certified")
    q_unfixed, iota, projection, homotopy = _unfixed_package()
    raw_map, gauge_condition, nilpotent, shear, inverse = _gauge_fermion_shear()
    identity = _identity_matrix(54)
    if not _is_zero(_sparse_multiply(nilpotent, nilpotent)):
        raise AssertionError("gauge-fermion shear is not two-step nilpotent")
    if not _is_zero(_subtract(_sparse_multiply(shear, inverse), identity)):
        raise AssertionError("gauge-fermion inverse failed")

    omega = _pairing()
    canonical_defect = _subtract(
        _sparse_multiply(_sparse_multiply(_adjoint_matrix(shear), omega), shear),
        omega,
    )
    if not _is_zero(canonical_defect):
        raise AssertionError("gauge-fermion shear is not BV canonical")

    q_gauge_fixed = _sparse_multiply(_sparse_multiply(shear, q_unfixed), inverse)
    if not _is_zero(_sparse_multiply(q_gauge_fixed, q_gauge_fixed)):
        raise AssertionError("gauge-fixed classical unary differential is not nilpotent")

    iota_gauge_fixed = _sparse_multiply(shear, iota)
    projection_gauge_fixed = _sparse_multiply(projection, inverse)
    homotopy_gauge_fixed = _sparse_multiply(
        _sparse_multiply(shear, homotopy), inverse
    )
    retained_identity = _identity_matrix(26)
    if not _is_zero(
        _subtract(
            _sparse_multiply(projection_gauge_fixed, iota_gauge_fixed),
            retained_identity,
        )
    ):
        raise AssertionError("gauge-fixed pi-iota identity failed")
    contraction_defect = _subtract(
        _matrix_add(
            _sparse_multiply(q_gauge_fixed, homotopy_gauge_fixed),
            _sparse_multiply(homotopy_gauge_fixed, q_gauge_fixed),
        ),
        _subtract(
            identity,
            _sparse_multiply(iota_gauge_fixed, projection_gauge_fixed),
        ),
    )
    if not _is_zero(contraction_defect):
        raise AssertionError("gauge-fixed contraction identity failed")
    if not _is_zero(_sparse_multiply(homotopy_gauge_fixed, homotopy_gauge_fixed)):
        raise AssertionError("gauge-fixed homotopy is not square zero")
    if not _is_zero(_sparse_multiply(projection_gauge_fixed, homotopy_gauge_fixed)):
        raise AssertionError("gauge-fixed pi-S side condition failed")
    if not _is_zero(_sparse_multiply(homotopy_gauge_fixed, iota_gauge_fixed)):
        raise AssertionError("gauge-fixed S-iota side condition failed")

    return {
        "unfixed": unfixed,
        "raw_map": raw_map,
        "gauge_condition": gauge_condition,
        "nilpotent": nilpotent,
        "q_gauge_fixed": q_gauge_fixed,
        "iota": iota_gauge_fixed,
        "projection": projection_gauge_fixed,
        "homotopy": homotopy_gauge_fixed,
        "omega": omega,
    }


@dataclass(frozen=True)
class BergerGaugeFixedNonminimalCompletion:
    payload: dict[str, object]

    @classmethod
    def build(cls) -> "BergerGaugeFixedNonminimalCompletion":
        data = _exact_data()
        unfixed = data["unfixed"]
        payload: dict[str, object] = {
            "schema": "pure-weyl-berger-gauge-fixed-nonminimal-completion-v1",
            "result_id": "BERGER_GAUGE_FIXED_NONMINIMAL_COMPLETION",
            "setting_id": unfixed["setting_id"],
            "claim_status": "CERTIFIED_COMPLETE_GAUGE_FIXED_UNARY_CONTRACTION",
            "dependency_tags": ["LOCAL-ALGEBRAIC"],
            "dependency_refs": {
                "unfixed_nonminimal": {
                    "result_id": unfixed["result_id"],
                    "sha256": _sha256(UNFIXED_CERTIFICATE),
                },
                "minimal_34": {
                    "result_id": "BERGER_MINIMAL_34_PORTABLE_CONTRACTION",
                    "sha256": _sha256(MINIMAL_CERTIFICATE),
                },
            },
            "operator_semantics": {
                "portable_name": "classical_unary_q1",
                "mathematical_name": "ell_1_cl_gauge_fixed",
                "not_quantum_loop_operator": True,
                "normalization": "alpha_nm=1",
            },
            "row_layout": unfixed["row_layout"],
            "gauge_fermion": {
                "formula": "Psi=<bar_c,A(h_hat,R,Theta)+(1/2)b>",
                "raw_metric_relation": "h=h_hat+K_tau Theta-K_sigma R",
                "raw_metric_from_dressed": _matrix_record(data["raw_map"]),
                "gauge_condition_A": _matrix_record(data["gauge_condition"]),
                "canonical_shear_nilpotent_part": _matrix_record(data["nilpotent"]),
                "shear_formula": "U=1+N; U^{-1}=1-N; N^2=0",
                "maximum_differential_order": _maximum_order(data["nilpotent"]),
                "support_local": True,
                "BV_canonical": True,
            },
            "classical_unary_q1": {
                "matrix": _matrix_record(data["q_gauge_fixed"]),
                "shape": [54, 54],
                "degree_ranks": [5, 22, 22, 5],
                "construction": "U ell_1_unfixed U^{-1}",
                "squared_zero": True,
                "cyclic": True,
            },
            "contraction": {
                "iota_cl": _matrix_record(data["iota"]),
                "pi_cl": _matrix_record(data["projection"]),
                "S_cl": _matrix_record(data["homotopy"]),
                "cyclic_pairing": _matrix_record(data["omega"]),
                "identity": "pi_cl iota_cl=1_26 and ell_1 S_cl+S_cl ell_1=1_54-iota_cl pi_cl",
                "side_conditions": ["S_cl^2=0", "pi_cl S_cl=0", "S_cl iota_cl=0"],
                "support_local": True,
                "maximum_differential_order": max(
                    _maximum_order(data["iota"]),
                    _maximum_order(data["projection"]),
                    _maximum_order(data["homotopy"]),
                ),
                "cyclic": True,
            },
            "exact_checks": {
                "all_54_rows_included": True,
                "raw_to_dressed_gauge_condition_exact": True,
                "canonical_shear_nilpotent": True,
                "canonical_shear_invertible": True,
                "BV_pairing_preserved": True,
                "gauge_fixed_classical_unary_q1_squared_zero": True,
                "gauge_fixed_classical_unary_q1_cyclic_by_canonical_transport": True,
                "gauge_fixed_pi_iota_identity": True,
                "gauge_fixed_contraction_identity": True,
                "gauge_fixed_contraction_side_conditions": True,
                "support_local_finite_order": True,
            },
            "flags": {
                "BERGER_GAUGE_FERMION_CANONICAL_TRANSFORM": True,
                "BERGER_NONMINIMAL_COMPLETION": True,
                "BERGER_COMPLETE_GAUGE_FIXED_UNARY_EXPORT": True,
                "CLASSICAL_SUPPORT_LOCAL_Q2": False,
                "BERGER_LOCAL_D_ACTION_EQUIVARIANT": False,
                "BERGER_GENERAL_KOSZUL_TATE_EXPORT": False,
                "BERGER_CURVED_CLOCK_REATTACHED_WITNESS": False,
                "BERGER_CAUSAL_GREEN_HOMOTOPY": False,
                "BERGER_HADAMARD_DATA": False,
                "CLASSICAL_SUPPORT_LOCAL_Q1_Q2_EXPORT": False,
            },
            "quantum_handoff": {
                "available": [
                    "54-row field/ghost/antifield/nonminimal dictionary",
                    "complete gauge-fixed classical_unary_q1",
                    "iota_cl, pi_cl, S_cl",
                    "cyclic pairing",
                ],
                "missing": [
                    "support-local classical_binary_q2",
                    "local D_action_cl and equivariance",
                    "general nonlinear antifield/Koszul-Tate export",
                    "causal Green and Hadamard data",
                ],
            },
            "next_gate": "CLASSICAL_SUPPORT_LOCAL_Q2_AND_D_ACTION",
            "claim_boundary": "This certificate applies the selected local gauge fermion as an exact BV-canonical shear and exports the complete gauge-fixed 54-row classical unary differential, cyclic pairing, and support-local contraction. It does not construct classical ell_2, the local D action or equivariance, a general nonlinear Koszul-Tate differential, causal Green operators, Hadamard data, or any quantum correction.",
        }
        result = cls(payload)
        result.verify()
        return result

    def verify(self) -> None:
        if any(value is not True for value in self.payload["exact_checks"].values()):
            raise AssertionError("gauge-fixed exact check dropped")
        semantics = self.payload["operator_semantics"]
        if semantics["portable_name"] != "classical_unary_q1" or semantics["not_quantum_loop_operator"] is not True:
            raise AssertionError("classical unary semantics drifted")
        flags = self.payload["flags"]
        for key in (
            "BERGER_GAUGE_FERMION_CANONICAL_TRANSFORM",
            "BERGER_NONMINIMAL_COMPLETION",
            "BERGER_COMPLETE_GAUGE_FIXED_UNARY_EXPORT",
        ):
            if flags[key] is not True:
                raise AssertionError(f"proved gauge-fixed flag dropped: {key}")
        for key, value in flags.items():
            if key not in {
                "BERGER_GAUGE_FERMION_CANONICAL_TRANSFORM",
                "BERGER_NONMINIMAL_COMPLETION",
                "BERGER_COMPLETE_GAUGE_FIXED_UNARY_EXPORT",
            } and value is not False:
                raise AssertionError(f"downstream flag promoted: {key}")
        if self.payload["next_gate"] != "CLASSICAL_SUPPORT_LOCAL_Q2_AND_D_ACTION":
            raise AssertionError("gauge-fixed next gate drifted")

    def certificate_text(self) -> str:
        return json.dumps(self.payload, indent=2, sort_keys=True) + "\n"

    def report_text(self) -> str:
        return r"""# Berger gauge-fixed nonminimal completion

The selected gauge fermion is expressed in the dressed clock coordinates by

\[
\Psi=\langle\bar c,A(\widehat h,R,\Theta)+\tfrac12b\rangle,
\qquad
h=\widehat h+K_\tau\Theta-K_\sigma R.
\]

Its cotangent lift is the exact finite-order canonical shear (U=1+N), with
(N^2=0) and (U^{-1}=1-N). Exact PBW conjugation gives the complete
54-row gauge-fixed `classical_unary_q1`. The transformed
\((\iota_{\rm cl},\pi_{\rm cl},S_{\rm cl})\) obey the contraction identity,
side conditions, cyclicity, and support locality.

This closes the unary nonminimal prerequisite. The decisive nonlinear handoff
remains open: support-local \(\ell^{\rm cl}_2\), the local (D)-action and
equivariance, general nonlinear Koszul--Tate data, and causal/Hadamard data.
"""


def _write(result: BergerGaugeFixedNonminimalCompletion) -> None:
    CERTIFICATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    CERTIFICATE_PATH.write_text(result.certificate_text())
    REPORT_PATH.write_text(result.report_text())


def _check(result: BergerGaugeFixedNonminimalCompletion) -> None:
    if CERTIFICATE_PATH.read_text() != result.certificate_text():
        raise AssertionError("gauge-fixed certificate drifted")
    if REPORT_PATH.read_text() != result.report_text():
        raise AssertionError("gauge-fixed report drifted")


def _guards(result: BergerGaugeFixedNonminimalCompletion) -> None:
    mutations = [
        ("drop canonical shear", ("flags", "BERGER_GAUGE_FERMION_CANONICAL_TRANSFORM"), False),
        ("drop completion", ("flags", "BERGER_NONMINIMAL_COMPLETION"), False),
        ("promote q2", ("flags", "CLASSICAL_SUPPORT_LOCAL_Q2"), True),
        ("promote D", ("flags", "BERGER_LOCAL_D_ACTION_EQUIVARIANT"), True),
        ("promote KT", ("flags", "BERGER_GENERAL_KOSZUL_TATE_EXPORT"), True),
        ("promote causal", ("flags", "BERGER_CAUSAL_GREEN_HOMOTOPY"), True),
        ("skip nonlinear gate", ("next_gate",), "BERGER_CAUSAL_GREEN_HOMOTOPY"),
    ]
    for name, path, replacement in mutations:
        mutant = deepcopy(result.payload)
        target = mutant
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = replacement
        try:
            BergerGaugeFixedNonminimalCompletion(mutant).verify()
        except AssertionError:
            continue
        raise AssertionError(f"mutation guard accepted: {name}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()
    result = BergerGaugeFixedNonminimalCompletion.build()
    if args.write:
        _write(result)
    if args.check:
        _check(result)
    if args.guards:
        _guards(result)
    if not (args.write or args.check or args.guards):
        print(result.certificate_text(), end="")
    else:
        print("BERGER_GAUGE_FIXED_NONMINIMAL_COMPLETION: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
