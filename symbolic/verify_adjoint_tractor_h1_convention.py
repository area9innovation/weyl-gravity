#!/usr/bin/env python3
"""Audit the Lorentz sign/transpose convention on the H1 tractor carrier."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from typing import Callable

import sympy as sp


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from covariant_completion.curved_operator.adjoint_tractor_bgg_differential_screen import (
    _adjoint_actions,
)
from covariant_completion.curved_operator.adjoint_tractor_kostant_compression import (
    AdjointTractorKostantCompression,
    _adjoint_basis,
    _digest_matrix,
)


MATRIX_INPUT = (
    ROOT
    / "covariant_completion"
    / "certificates"
    / "adjoint_tractor_kostant_compression_matrices.json"
)
OUTPUT = (
    ROOT
    / "covariant_completion"
    / "certificates"
    / "adjoint_tractor_h1_convention_audit.json"
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _carrier_matrix(inclusion: sp.Matrix, column: int) -> sp.Matrix:
    """Extract H_a{}^b from the form-major P_b part of C1."""

    return sp.Matrix(
        4,
        4,
        lambda form, translation: inclusion[15 * form + translation, column],
    )


def _defect_summary(defect: sp.Matrix) -> dict[str, object]:
    values = sorted({str(value) for value in defect.todok().values()})
    return {
        "rank": defect.rank(),
        "nonzero_entries": len(defect.todok()),
        "nonzero_values": values,
        "sha256": _digest_matrix(defect),
    }


def build_certificate() -> dict[str, object]:
    algebraic = AdjointTractorKostantCompression.build()
    names, basis = _adjoint_basis()
    lorentz_names = names[4:10]
    adjoint_actions = _adjoint_actions(basis[4:10], basis)
    eta = sp.diag(-1, 1, 1, 1)
    lorentz_embedded = sp.Matrix.hstack(
        *(value.reshape(36, 1) for value in basis[4:10])
    )
    lorentz_left_inverse = (
        (lorentz_embedded.T * lorentz_embedded).inv() * lorentz_embedded.T
    )
    if lorentz_left_inverse * lorentz_embedded != sp.eye(6):
        raise AssertionError("exact Lorentz generator basis is singular")

    # The stored carrier has coefficients H_a{}^b in V^* tensor g_-1.
    # Lowering its translation index gives the covariant STF tensor h=H eta.
    symmetry_defects = []
    trace_defects = []
    for column in range(algebraic.i1.cols):
        mixed = _carrier_matrix(algebraic.i1, column)
        lowered = mixed * eta
        symmetry_defects.append(lowered - lowered.T)
        trace_defects.append(sp.trace(eta * lowered))

    if any(matrix != sp.zeros(4) for matrix in symmetry_defects):
        raise AssertionError("metric-lowered Kostant H1 carrier is not symmetric")
    if any(value != 0 for value in trace_defects):
        raise AssertionError("metric-lowered Kostant H1 carrier is not trace-free")

    projector_complement = sp.eye(60) - algebraic.i1 * algebraic.p1
    identity15 = sp.eye(15)
    identity4 = sp.eye(4)
    conventions: dict[str, Callable[[sp.Matrix], sp.Matrix]] = {
        "+R": lambda value: value,
        "-R": lambda value: -value,
        "+R^T": lambda value: value.T,
        "-R^T": lambda value: -value.T,
    }
    convention_defects: dict[str, object] = {}
    lorentz_metric_defects: dict[str, int] = {}
    metric_identification_defects: dict[str, int] = {}
    adjoint_restriction_defects: dict[str, int] = {}
    correct_diagonal_actions: list[sp.Matrix] = []

    for name, adjoint in zip(lorentz_names, adjoint_actions, strict=True):
        vector = adjoint[:4, :4]
        lorentz_metric_defects[name] = len((vector.T * eta + eta * vector).todok())
        metric_identification_defects[name] = len(
            (eta.inv() * (-vector.T) * eta - vector).todok()
        )
        adjoint_restriction_defects[name] = len(adjoint[4:, :4].todok())
        correct_diagonal_actions.append(
            sp.kronecker_product(-vector.T, identity15)
            + sp.kronecker_product(identity4, adjoint)
        )

    parent_representation_defects = 0
    induced_representation_defects = 0
    induced_actions = [
        algebraic.p1 * diagonal * algebraic.i1
        for diagonal in correct_diagonal_actions
    ]
    for left in range(6):
        for right in range(6):
            bracket = basis[4 + left] * basis[4 + right] - basis[4 + right] * basis[4 + left]
            coordinates = lorentz_left_inverse * bracket.reshape(36, 1)
            if lorentz_embedded * coordinates != bracket.reshape(36, 1):
                raise AssertionError("Lorentz commutator escaped the exact basis")
            expected_parent = sum(
                (
                    coordinates[index] * correct_diagonal_actions[index]
                    for index in range(6)
                ),
                sp.zeros(60),
            )
            parent_defect = (
                correct_diagonal_actions[left] * correct_diagonal_actions[right]
                - correct_diagonal_actions[right] * correct_diagonal_actions[left]
                - expected_parent
            )
            parent_representation_defects += len(parent_defect.todok())
            expected_induced = sum(
                (
                    coordinates[index] * induced_actions[index]
                    for index in range(6)
                ),
                sp.zeros(9),
            )
            induced_defect = (
                induced_actions[left] * induced_actions[right]
                - induced_actions[right] * induced_actions[left]
                - expected_induced
            )
            induced_representation_defects += len(induced_defect.todok())

    for convention, form_action in conventions.items():
        per_generator: dict[str, object] = {}
        total_nonzero = 0
        for name, adjoint in zip(lorentz_names, adjoint_actions, strict=True):
            vector = adjoint[:4, :4]
            diagonal = (
                sp.kronecker_product(form_action(vector), identity15)
                + sp.kronecker_product(identity4, adjoint)
            )
            defect = (projector_complement * diagonal * algebraic.i1).applyfunc(
                sp.expand
            )
            summary = _defect_summary(defect)
            total_nonzero += int(summary["nonzero_entries"])
            per_generator[name] = summary
        convention_defects[convention] = {
            "per_generator": per_generator,
            "total_nonzero_entries": total_nonzero,
            "all_generators_preserve_H1": total_nonzero == 0,
        }

    passing = [
        convention
        for convention, result in convention_defects.items()
        if result["all_generators_preserve_H1"]
    ]
    if passing != ["-R^T"]:
        raise AssertionError(f"H1 sign/transpose convention is not unique: {passing}")
    if any(lorentz_metric_defects.values()):
        raise AssertionError("exact translation action is not Lorentz")
    if any(metric_identification_defects.values()):
        raise AssertionError("covector/vector metric identification drifted")
    if any(adjoint_restriction_defects.values()):
        raise AssertionError("Lorentz action does not preserve g_-1")
    if parent_representation_defects or induced_representation_defects:
        raise AssertionError("diagonal Lorentz action is not a representation")

    return {
        "schema": "pure-weyl-adjoint-tractor-h1-convention-audit-v1",
        "dependency_tag": "LOCAL-ALGEBRAIC",
        "kostant_matrix_payload_sha256": _sha256(MATRIX_INPUT),
        "kostant_i1_sha256": _digest_matrix(algebraic.i1),
        "kostant_p1_sha256": _digest_matrix(algebraic.p1),
        "basis_order": list(lorentz_names),
        "translation_generator_matrices": {
            name: [[str(entry) for entry in row] for row in adjoint[:4, :4].tolist()]
            for name, adjoint in zip(lorentz_names, adjoint_actions, strict=True)
        },
        "derivation": {
            "raw_carrier": "H_a^b in Lambda^1 T* tensor g_-1",
            "metric_lowering": "h_ab = H_a^c eta_cb",
            "metric_lowered_carrier": "symmetric trace-free",
            "translation_action": "R_M from [M,P_b] = (R_M)^a_b P_a",
            "covector_action": "-R_M^T",
            "raw_diagonal_action": "C1(M)=(-R_M^T) tensor I_15 + I_4 tensor ad_M",
            "lowered_tensor_action": "delta h = -R_M^T h - h R_M",
            "metric_identification": "eta^-1(-R_M^T)eta=R_M",
            "overall_generator_reversal": (
                "simultaneously reversing both summands is M->-M, not a distinct "
                "sign/transpose convention"
            ),
        },
        "exact_prechecks": {
            "p1_i1_is_identity": algebraic.p1 * algebraic.i1 == sp.eye(9),
            "metric_lowered_symmetry_defects": 0,
            "metric_lowered_trace_defects": 0,
            "lorentz_metric_defects": lorentz_metric_defects,
            "metric_identification_defects": metric_identification_defects,
            "g_minus_one_restriction_defects": adjoint_restriction_defects,
            "parent_lorentz_representation_defects": parent_representation_defects,
            "induced_H1_lorentz_representation_defects": induced_representation_defects,
        },
        "gate": "(I_60-i1 p1) C1(M) i1 = 0 for every M in so(3,1)",
        "convention_defects": convention_defects,
        "unique_passing_convention_with_ad_M_fixed": "-R^T",
        "arbitrary_curvature_consequence": (
            "(I_60-i1 p1) C1(Omega) i1=0 for every so(3,1)-valued Omega"
        ),
        "claim_boundary": (
            "This fixes the H1 Lorentz slot convention only.  It does not by "
            "itself prove the complete curved PBW chain map or a Green transfer."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    args = parser.parse_args()

    certificate = build_certificate()
    if args.emit:
        OUTPUT.write_text(
            json.dumps(certificate, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print("wrote", OUTPUT.relative_to(ROOT))
    else:
        persisted = json.loads(OUTPUT.read_text(encoding="utf-8"))
        if persisted != certificate:
            raise AssertionError("persisted H1 convention audit drifted")

    alternatives = certificate["convention_defects"]
    for convention in ("+R", "-R", "+R^T", "-R^T"):
        ranks = [
            alternatives[convention]["per_generator"][name]["rank"]
            for name in certificate["basis_order"]
        ]
        nonzero = alternatives[convention]["total_nonzero_entries"]
        print(f"{convention:>4}: ranks={ranks}, total_nnz={nonzero}")
    print("[PASS] unique H1 convention: -R^T on the one-form slot")
    print("[PASS] arbitrary so(3,1)-valued curvature preserves the Kostant H1 carrier")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
