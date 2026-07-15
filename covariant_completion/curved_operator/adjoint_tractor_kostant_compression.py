"""Exact pointwise Kostant compression of the adjoint-tractor detour rows.

This module implements the algebraic first stage of the conformal BGG
compression

``15 -> 60 -> 60 -> 15``  to  ``4 -> 9 -> 9 -> 4``.

The standard ``|1|`` grading of ``so(4,2)`` is used.  In a tractor splitting
the adjoint basis is ordered as

``P_a[4], M_ab[6], D[1], K_a[4]``.

The Kostant chain differential is contraction with ``ad(K_a)``.  Its first
two matrices have shapes ``15 x 60`` and ``60 x 90``.  Exact rational row
reduction gives homology dimensions four and nine.  The nine representatives
are selected inside ``V^* tensor g_-1``; hence they are precisely the
symmetric trace-free deformation slot rather than an arbitrary complement.

The dual equation and identity rows are not compressed independently.  They
are generated from the tractor trace pairing, which makes the row order
``G[4], M[9], E[9], I[4]`` cyclic by construction.

This is deliberately only a *pointwise* Kostant SDR.  It proves the local
algebraic carrier and supplies the data from which finite-order BGG splitting
operators can be constructed.  It does not claim that those differential
splitting operators intertwine the parent Yang--Mills detour operator with
the coefficient-complete cylinder Bach endpoint.  Consequently it does not
yet transfer a parent Green homotopy.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
from typing import Mapping

import sympy as sp


Matrix = sp.Matrix


def _digest_matrix(matrix: sp.MatrixBase) -> str:
    return hashlib.sha256(
        sp.srepr(sp.ImmutableSparseMatrix(matrix)).encode("utf-8")
    ).hexdigest()


def _sparse_matrix(matrix: sp.MatrixBase) -> dict[str, object]:
    return {
        "shape": [matrix.rows, matrix.cols],
        "entries": [
            [row, column, str(matrix[row, column])]
            for row in range(matrix.rows)
            for column in range(matrix.cols)
            if matrix[row, column] != 0
        ],
        "sha256": _digest_matrix(matrix),
    }


def _parse_sparse(value: object) -> Matrix:
    if not isinstance(value, Mapping):
        raise AssertionError("sparse matrix is not an object")
    shape = value.get("shape")
    entries = value.get("entries")
    if (
        not isinstance(shape, list)
        or len(shape) != 2
        or not all(isinstance(item, int) for item in shape)
        or not isinstance(entries, list)
    ):
        raise AssertionError("malformed sparse matrix")
    matrix = sp.zeros(shape[0], shape[1])
    for item in entries:
        if not isinstance(item, list) or len(item) != 3:
            raise AssertionError("malformed sparse matrix entry")
        row, column, coefficient = item
        if not isinstance(row, int) or not isinstance(column, int):
            raise AssertionError("non-integral sparse index")
        matrix[row, column] = sp.Rational(coefficient)
    if _digest_matrix(matrix) != value.get("sha256"):
        raise AssertionError("sparse matrix digest mismatch")
    return matrix


def _tractor_metric() -> Matrix:
    """The split tractor metric of signature ``(4,2)``."""

    eta = sp.diag(-1, 1, 1, 1)
    metric = sp.zeros(6)
    metric[0, 5] = metric[5, 0] = 1
    metric[1:5, 1:5] = eta
    return metric


def _adjoint_basis() -> tuple[tuple[str, ...], tuple[Matrix, ...]]:
    """Return the standard graded basis as exact six-by-six matrices."""

    eta = sp.diag(-1, 1, 1, 1)
    names: list[str] = []
    basis: list[Matrix] = []

    # g_-1 translations P(X).
    for axis in range(4):
        value = sp.zeros(6)
        value[1 + axis, 0] = 1
        for index in range(4):
            value[5, 1 + index] = -eta[index, axis]
        names.append(f"P{axis}")
        basis.append(value)

    # so(3,1) generators M_ab.
    for left in range(4):
        for right in range(left + 1, 4):
            value = sp.zeros(6)
            for row in range(4):
                for column in range(4):
                    value[1 + row, 1 + column] = (
                        int(row == left) * eta[right, column]
                        - int(row == right) * eta[left, column]
                    )
            names.append(f"M{left}{right}")
            basis.append(value)

    dilation = sp.zeros(6)
    dilation[0, 0] = -1
    dilation[5, 5] = 1
    names.append("D")
    basis.append(dilation)

    # g_+1 special conformal generators K(Z).
    for axis in range(4):
        value = sp.zeros(6)
        value[0, 1 + axis] = -1
        for index in range(4):
            value[1 + index, 5] = eta[index, axis]
        names.append(f"K{axis}")
        basis.append(value)

    return tuple(names), tuple(basis)


def _coordinate_map(basis: tuple[Matrix, ...]) -> tuple[Matrix, Matrix]:
    embedded = sp.Matrix.hstack(*(value.reshape(36, 1) for value in basis))
    left_inverse = (embedded.T * embedded).inv() * embedded.T
    if left_inverse * embedded != sp.eye(15):
        raise AssertionError("adjoint tractor coordinate map is singular")
    return embedded, left_inverse


def _kostant_differentials(
    basis: tuple[Matrix, ...],
) -> tuple[Matrix, Matrix]:
    """Build ``partial*_1`` and ``partial*_2`` exactly."""

    embedded, left_inverse = _coordinate_map(basis)

    def coordinates(value: Matrix) -> Matrix:
        result = left_inverse * value.reshape(36, 1)
        if embedded * result != value.reshape(36, 1):
            raise AssertionError("commutator escaped so(4,2)")
        return result

    ad_k = tuple(
        sp.Matrix.hstack(
            *(
                coordinates(generator * value - value * generator)
                for value in basis
            )
        )
        for generator in basis[11:15]
    )
    first = sp.Matrix.hstack(*ad_k)

    second_columns: list[Matrix] = []
    for left in range(4):
        for right in range(left + 1, 4):
            column = sp.zeros(60, 15)
            column[15 * right : 15 * (right + 1), :] = ad_k[left]
            column[15 * left : 15 * (left + 1), :] = -ad_k[right]
            second_columns.append(column)
    second = sp.Matrix.hstack(*second_columns)
    return first, second


def _standard_homology_one(first: Matrix) -> Matrix:
    """Select the nine STF representatives inside ``V^* tensor g_-1``."""

    p_slot = sp.zeros(60, 16)
    for form_axis in range(4):
        for translation_axis in range(4):
            p_slot[15 * form_axis + translation_axis, 4 * form_axis + translation_axis] = 1
    kernel = first * p_slot
    nullspace = kernel.nullspace()
    if len(nullspace) != 9:
        raise AssertionError("the deformation slot is not nine-dimensional")
    return p_slot * sp.Matrix.hstack(*nullspace)


@dataclass(frozen=True)
class AdjointTractorKostantCompression:
    """Exact algebraic SDR and its cyclic dual compression."""

    tractor_metric: Matrix
    adjoint_pairing: Matrix
    one_form_pairing: Matrix
    d1: Matrix
    d2: Matrix
    i0: Matrix
    p0: Matrix
    h0: Matrix
    i1: Matrix
    p1: Matrix
    h1: Matrix
    endpoint_ghost_pairing: Matrix
    endpoint_field_pairing: Matrix
    i_equation: Matrix
    p_equation: Matrix
    i_identity: Matrix
    p_identity: Matrix

    @classmethod
    def build(cls) -> "AdjointTractorKostantCompression":
        names, basis = _adjoint_basis()
        if names != (
            "P0", "P1", "P2", "P3",
            "M01", "M02", "M03", "M12", "M13", "M23", "D",
            "K0", "K1", "K2", "K3",
        ):
            raise AssertionError("adjoint tractor basis order drifted")
        tractor_metric = _tractor_metric()
        if any(
            value.T * tractor_metric + tractor_metric * value != sp.zeros(6)
            for value in basis
        ):
            raise AssertionError("adjoint basis is not so(4,2)")

        d1, d2 = _kostant_differentials(basis)
        if d1 * d2 != sp.zeros(15, 90):
            raise AssertionError("Kostant differential does not square to zero")
        if d1.rank() != 11 or d2.rank() != 40:
            raise AssertionError("unexpected Kostant ranks")

        pivot1 = tuple(d1.rref()[1])
        boundary0 = d1[:, list(pivot1)]
        lift1 = sp.eye(60)[:, list(pivot1)]
        i0 = sp.eye(15)[:, :4]
        decomposition0 = sp.Matrix.hstack(boundary0, i0)
        inverse0 = decomposition0.inv()
        p0 = inverse0[11:15, :]
        h0 = lift1 * inverse0[:11, :]

        pivot2 = tuple(d2.rref()[1])
        boundary1 = d2[:, list(pivot2)]
        lift2 = sp.eye(90)[:, list(pivot2)]
        i1 = _standard_homology_one(d1)
        decomposition1 = sp.Matrix.hstack(boundary1, i1, lift1)
        inverse1 = decomposition1.inv()
        p1 = inverse1[40:49, :]
        h1 = lift2 * inverse1[:40, :]

        adjoint_pairing = sp.Matrix(
            15, 15, lambda row, column: sp.trace(basis[row] * basis[column])
        )
        eta = sp.diag(-1, 1, 1, 1)
        one_form_pairing = sp.kronecker_product(eta.inv(), adjoint_pairing)
        endpoint_ghost_pairing = eta
        endpoint_field_pairing = sp.eye(9)

        # Cotangent rows are forced from the primal maps and pairings.
        i_identity = (
            adjoint_pairing.inv() * p0.T * endpoint_ghost_pairing
        )
        p_identity = (
            endpoint_ghost_pairing.inv() * i0.T * adjoint_pairing
        )
        i_equation = (
            one_form_pairing.inv() * p1.T * endpoint_field_pairing
        )
        p_equation = (
            endpoint_field_pairing.inv() * i1.T * one_form_pairing
        )

        theorem = cls(
            tractor_metric=tractor_metric,
            adjoint_pairing=adjoint_pairing,
            one_form_pairing=one_form_pairing,
            d1=d1,
            d2=d2,
            i0=i0,
            p0=p0,
            h0=h0,
            i1=i1,
            p1=p1,
            h1=h1,
            endpoint_ghost_pairing=endpoint_ghost_pairing,
            endpoint_field_pairing=endpoint_field_pairing,
            i_equation=i_equation,
            p_equation=p_equation,
            i_identity=i_identity,
            p_identity=p_identity,
        )
        theorem.verify()
        return theorem

    @classmethod
    def from_payload(
        cls, payload: Mapping[str, object]
    ) -> "AdjointTractorKostantCompression":
        if payload.get("schema_version") != 1:
            raise AssertionError("wrong adjoint-tractor compression schema")
        matrices = payload.get("matrices")
        if not isinstance(matrices, Mapping):
            raise AssertionError("compression matrices are missing")

        def get(name: str) -> Matrix:
            if name not in matrices:
                raise AssertionError(f"missing compression matrix {name}")
            return _parse_sparse(matrices[name])

        theorem = cls(
            tractor_metric=get("tractor_metric"),
            adjoint_pairing=get("adjoint_pairing"),
            one_form_pairing=get("one_form_pairing"),
            d1=get("kostant_d1"),
            d2=get("kostant_d2"),
            i0=get("i_G"),
            p0=get("p_G"),
            h0=get("h_0"),
            i1=get("i_M"),
            p1=get("p_M"),
            h1=get("h_1"),
            endpoint_ghost_pairing=get("Y_endpoint"),
            endpoint_field_pairing=get("J_endpoint"),
            i_equation=get("i_E"),
            p_equation=get("p_E"),
            i_identity=get("i_I"),
            p_identity=get("p_I"),
        )
        theorem.verify()
        return theorem

    def verify(self) -> None:
        shapes = {
            "d1": (self.d1, (15, 60)),
            "d2": (self.d2, (60, 90)),
            "i0": (self.i0, (15, 4)),
            "p0": (self.p0, (4, 15)),
            "h0": (self.h0, (60, 15)),
            "i1": (self.i1, (60, 9)),
            "p1": (self.p1, (9, 60)),
            "h1": (self.h1, (90, 60)),
            "iE": (self.i_equation, (60, 9)),
            "pE": (self.p_equation, (9, 60)),
            "iI": (self.i_identity, (15, 4)),
            "pI": (self.p_identity, (4, 15)),
        }
        for name, (matrix, shape) in shapes.items():
            if matrix.shape != shape:
                raise AssertionError(f"wrong {name} shape")

        if self.d1 * self.d2 != sp.zeros(15, 90):
            raise AssertionError("Kostant square defect")
        if self.d1.rank() != 11 or self.d2.rank() != 40:
            raise AssertionError("Kostant rank defect")
        if self.p0 * self.i0 != sp.eye(4):
            raise AssertionError("degree-zero retraction defect")
        if self.p1 * self.i1 != sp.eye(9):
            raise AssertionError("degree-one retraction defect")
        if self.d1 * self.i1 != sp.zeros(15, 9):
            raise AssertionError("degree-one representatives are not closed")
        if self.p0 * self.d1 != sp.zeros(4, 60):
            raise AssertionError("degree-zero projection sees boundaries")
        if self.p1 * self.d2 != sp.zeros(9, 90):
            raise AssertionError("degree-one projection sees boundaries")
        if self.d1 * self.h0 + self.i0 * self.p0 != sp.eye(15):
            raise AssertionError("degree-zero SDR defect")
        if (
            self.d2 * self.h1
            + self.h0 * self.d1
            + self.i1 * self.p1
            != sp.eye(60)
        ):
            raise AssertionError("degree-one SDR defect")

        # The chosen H1 representatives have support only in V* tensor P.
        if any(
            self.i1[row, column] != 0
            for row in range(60)
            for column in range(9)
            if row % 15 >= 4
        ):
            raise AssertionError("H1 escaped the STF deformation slot")
        eta = sp.diag(-1, 1, 1, 1)
        for column in range(9):
            tensor = sp.Matrix(
                4,
                4,
                lambda left, right: (
                    eta[right, right] * self.i1[15 * left + right, column]
                ),
            )
            if tensor != tensor.T:
                raise AssertionError("H1 representative is not symmetric")
            if sum(
                eta[axis, axis] * tensor[axis, axis] for axis in range(4)
            ) != 0:
                raise AssertionError("H1 representative is not trace-free")

        if self.adjoint_pairing.det() == 0 or self.one_form_pairing.det() == 0:
            raise AssertionError("parent tractor pairing is degenerate")
        if (
            self.endpoint_ghost_pairing.det() == 0
            or self.endpoint_field_pairing.det() == 0
        ):
            raise AssertionError("endpoint pairing is degenerate")
        if self.p_identity * self.i_identity != sp.eye(4):
            raise AssertionError("identity-row retraction defect")
        if self.p_equation * self.i_equation != sp.eye(9):
            raise AssertionError("equation-row retraction defect")
        if (
            self.i0.T * self.adjoint_pairing * self.i_identity
            != self.endpoint_ghost_pairing
        ):
            raise AssertionError("ghost/identity cyclic pullback defect")
        if (
            self.i1.T * self.one_form_pairing * self.i_equation
            != self.endpoint_field_pairing
        ):
            raise AssertionError("field/equation cyclic pullback defect")
        if (
            self.adjoint_pairing * self.i_identity * self.p_identity
            != (self.i0 * self.p0).T * self.adjoint_pairing
        ):
            raise AssertionError("dual degree-zero projector defect")
        if (
            self.one_form_pairing * self.i_equation * self.p_equation
            != (self.i1 * self.p1).T * self.one_form_pairing
        ):
            raise AssertionError("dual degree-one projector defect")

    def payload(self) -> dict[str, object]:
        matrices = {
            "tractor_metric": self.tractor_metric,
            "adjoint_pairing": self.adjoint_pairing,
            "one_form_pairing": self.one_form_pairing,
            "kostant_d1": self.d1,
            "kostant_d2": self.d2,
            "i_G": self.i0,
            "p_G": self.p0,
            "h_0": self.h0,
            "i_M": self.i1,
            "p_M": self.p1,
            "h_1": self.h1,
            "Y_endpoint": self.endpoint_ghost_pairing,
            "J_endpoint": self.endpoint_field_pairing,
            "i_E": self.i_equation,
            "p_E": self.p_equation,
            "i_I": self.i_identity,
            "p_I": self.p_identity,
        }
        return {
            "schema_version": 1,
            "arithmetic": "exact rational",
            "ambient_algebra": "so(4,2)",
            "grading": "g_-1[4] + (so(3,1)+R)[7] + g_+1[4]",
            "parent_rows": [15, 60, 60, 15],
            "compressed_rows": [4, 9, 9, 4],
            "matrices": {
                name: _sparse_matrix(matrix) for name, matrix in matrices.items()
            },
        }

    def certificate(self, payload_sha256: str) -> dict[str, object]:
        return {
            "schema_version": 1,
            "result": "PASS",
            "dependency_tag": "LOCAL-ALGEBRAIC",
            "payload_sha256": payload_sha256,
            "construction": {
                "ambient_algebra": "so(4,2)",
                "tractor_signature": [4, 2],
                "adjoint_grading_dimensions": [4, 7, 4],
                "parent_detour_row_ranks": [15, 60, 60, 15],
                "compressed_endpoint_row_ranks": [4, 9, 9, 4],
                "kostant_differential_ranks": [11, 40],
                "homology_dimensions": [4, 9],
                "homology_one_carrier": "V^* tensor g_-1 symmetric-tracefree kernel",
            },
            "exact_identities": {
                "kostant_square_zero": True,
                "p0_i0": "I_4",
                "p1_i1": "I_9",
                "d1_h0_plus_i0_p0": "I_15",
                "d2_h1_plus_h0_d1_plus_i1_p1": "I_60",
                "dual_rows_forced_by_pairing": True,
                "ghost_identity_pairing_pullback": "Y_endpoint",
                "field_equation_pairing_pullback": "J_endpoint",
                "cyclic_projector_defects": 0,
            },
            "support": {
                "pointwise_kostant_maps_support_local": True,
                "contains_inverse_laplacian": False,
                "contains_inverse_curl": False,
                "contains_helicity_or_TT_projector": False,
                "contains_green_operator": False,
            },
            "theorem_boundary": {
                "pointwise_kostant_sdr_exact": True,
                "cyclic_algebraic_compression_exact": True,
                "differential_BGG_splitting_operators_constructed": False,
                "parent_YM_detour_to_endpoint_intertwiner_coefficientwise": False,
                "endpoint_Bach_operator_match": False,
                "parent_green_homotopy_support_local_transfer_certified": False,
                "endpoint_green_homotopy": False,
                "conditional_transfer_statement": (
                    "If finite-order differential BGG inclusion/projection maps "
                    "intertwining the parent detour operator are certified, then "
                    "p Lambda_pm i is causal because differential pre/postcomposition "
                    "does not enlarge support.  The present pointwise SDR alone is "
                    "not such an intertwiner."
                ),
            },
            "claim": (
                "The standard adjoint-tractor Kostant rows compress exactly and "
                "cyclically from 15/60/60/15 to 4/9/9/4.  This establishes the "
                "pointwise BGG carrier but does not yet identify its differential "
                "detour operator with the curved metric endpoint."
            ),
        }


def write_json(path: Path, value: Mapping[str, object]) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
