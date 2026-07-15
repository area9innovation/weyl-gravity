"""Finite HPL screen for the adjoint-tractor BGG detour compression.

The pointwise Kostant certificate supplies ``partial*`` and the harmonic
carriers.  This module adds the dual Lie-algebra cohomology differential,
the exact Kostant Laplacians and their rational generalized inverses.  The
finite homological-perturbation series then gives the differential splitting
symbols ``L0`` and ``L1``; both terminate after two corrections.

Two logically separate calculations are retained.

* In the flat associated-graded model, the complete finite HPL series is an
  exact chain map.  Its first BGG operator is the trace-free conformal Killing
  symbol (with the recorded factor ``1/2`` in project coordinates).
* In the cylinder metric splitting, the Schouten ``g_+1`` connection term is
  included.  If Levi-Civita derivatives are incorrectly treated as commuting,
  a nonzero lower-order chain defect remains.  This is the precise guard which
  prevents the pointwise/graded calculation from being promoted to a curved
  differential splitting.  The missing operation is the curvature-aware PBW
  composition of the Levi-Civita tensor slots, not another algebraic rank
  solve.

The parent Maxwell/Yang--Mills middle symbol is compressed and compared with
the action-derived endpoint Bach symbol as a bilinear Hessian.  This comparison
is exact at order four.  No lower-order Bach match or Green transfer is claimed.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from itertools import product
from pathlib import Path
from typing import Mapping

import sympy as sp

from .adjoint_tractor_kostant_compression import (
    AdjointTractorKostantCompression,
    _adjoint_basis,
    _coordinate_map,
    _digest_matrix,
    _parse_sparse,
    _sparse_matrix,
)
from .conventions import SYMMETRIC_COORDINATES
from .prolonged_metric_endpoint_complex import ProlongedMetricEndpointComplex


Multiindex = tuple[int, int, int, int]


def _adjoint_actions(
    generators: tuple[sp.Matrix, ...], basis: tuple[sp.Matrix, ...]
) -> tuple[sp.Matrix, ...]:
    embedded, left_inverse = _coordinate_map(basis)

    def coordinates(value: sp.Matrix) -> sp.Matrix:
        result = left_inverse * value.reshape(36, 1)
        if embedded * result != value.reshape(36, 1):
            raise AssertionError("adjoint action escaped so(4,2)")
        return result

    return tuple(
        sp.Matrix.hstack(
            *(
                coordinates(generator * value - value * generator)
                for value in basis
            )
        )
        for generator in generators
    )


def _wedge_zero(actions: tuple[sp.Matrix, ...]) -> sp.Matrix:
    return sp.Matrix.vstack(*actions)


def _wedge_one(actions: tuple[sp.Matrix, ...]) -> sp.Matrix:
    rows: list[sp.Matrix] = []
    for left in range(4):
        for right in range(left + 1, 4):
            block = sp.zeros(15, 60)
            block[:, 15 * right : 15 * (right + 1)] = actions[left]
            block[:, 15 * left : 15 * (left + 1)] = -actions[right]
            rows.append(block)
    return sp.Matrix.vstack(*rows)


def _exterior_symbols(covector: tuple[sp.Symbol, ...]) -> tuple[sp.Matrix, sp.Matrix]:
    zero = sp.Matrix.vstack(*(value * sp.eye(15) for value in covector))
    rows: list[sp.Matrix] = []
    for left in range(4):
        for right in range(left + 1, 4):
            block = sp.zeros(15, 60)
            block[:, 15 * right : 15 * (right + 1)] = covector[left] * sp.eye(15)
            block[:, 15 * left : 15 * (left + 1)] = -covector[right] * sp.eye(15)
            rows.append(block)
    return zero, sp.Matrix.vstack(*rows)


def _polynomial_matrix(
    matrix: sp.Matrix, covector: tuple[sp.Symbol, ...]
) -> dict[Multiindex, sp.Matrix]:
    maximum = max(
        (sp.Poly(value, *covector).total_degree() for value in matrix if value != 0),
        default=0,
    )
    result: dict[Multiindex, sp.Matrix] = {}
    for multiindex in product(range(maximum + 1), repeat=4):
        if sum(multiindex) > maximum:
            continue
        monomial = sp.prod(
            covector[axis] ** multiindex[axis] for axis in range(4)
        )
        coefficient = matrix.applyfunc(
            lambda value: (
                sp.Poly(value, *covector).coeff_monomial(monomial)
                if value != 0
                else sp.Integer(0)
            )
        )
        if coefficient != sp.zeros(*matrix.shape):
            result[multiindex] = coefficient
    return result


def _homogeneous(
    matrix: sp.Matrix, covector: tuple[sp.Symbol, ...], degree: int
) -> sp.Matrix:
    table = _polynomial_matrix(matrix, covector)
    return sum(
        (
            coefficient
            * sp.prod(
                covector[axis] ** multiindex[axis] for axis in range(4)
            )
            for multiindex, coefficient in table.items()
            if sum(multiindex) == degree
        ),
        sp.zeros(*matrix.shape),
    )


def _digest_table(table: Mapping[Multiindex, sp.Matrix]) -> str:
    payload = "\n".join(
        f"{multiindex}:{sp.srepr(sp.ImmutableSparseMatrix(table[multiindex]))}"
        for multiindex in sorted(table)
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _sparse_table(table: Mapping[Multiindex, sp.Matrix]) -> dict[str, object]:
    return {
        "entries": [
            {
                "multiindex": list(multiindex),
                "matrix": _sparse_matrix(table[multiindex]),
            }
            for multiindex in sorted(table)
        ],
        "sha256": _digest_table(table),
    }


def _parse_table(value: object) -> dict[Multiindex, sp.Matrix]:
    if not isinstance(value, Mapping) or not isinstance(value.get("entries"), list):
        raise AssertionError("malformed polynomial coefficient table")
    result: dict[Multiindex, sp.Matrix] = {}
    for item in value["entries"]:
        if not isinstance(item, Mapping):
            raise AssertionError("malformed polynomial table entry")
        multiindex = item.get("multiindex")
        if (
            not isinstance(multiindex, list)
            or len(multiindex) != 4
            or not all(isinstance(axis, int) for axis in multiindex)
        ):
            raise AssertionError("malformed polynomial multiindex")
        result[tuple(multiindex)] = _parse_sparse(item.get("matrix"))
    if _digest_table(result) != value.get("sha256"):
        raise AssertionError("polynomial table digest mismatch")
    return result


def _table_polynomial(
    table: Mapping[Multiindex, sp.Matrix], covector: tuple[sp.Symbol, ...]
) -> sp.Matrix:
    shape = next(iter(table.values())).shape
    return sum(
        (
            coefficient
            * sp.prod(covector[axis] ** multiindex[axis] for axis in range(4))
            for multiindex, coefficient in table.items()
        ),
        sp.zeros(*shape),
    )


@dataclass(frozen=True)
class AdjointTractorBGGDifferentialScreen:
    algebraic: AdjointTractorKostantCompression
    cohomology_d0: sp.Matrix
    cohomology_d1: sp.Matrix
    kostant_laplacian0: sp.Matrix
    kostant_laplacian1: sp.Matrix
    kostant_inverse0: sp.Matrix
    kostant_inverse1: sp.Matrix
    harmonic_projection0: sp.Matrix
    harmonic_projection1: sp.Matrix
    harmonic_p0: sp.Matrix
    harmonic_p1: sp.Matrix
    q1: sp.Matrix
    q2: sp.Matrix
    flat_L0: dict[Multiindex, sp.Matrix]
    flat_L1: dict[Multiindex, sp.Matrix]
    flat_P0: dict[Multiindex, sp.Matrix]
    flat_P1: dict[Multiindex, sp.Matrix]
    flat_H0: dict[Multiindex, sp.Matrix]
    flat_H1: dict[Multiindex, sp.Matrix]
    flat_i_equation: dict[Multiindex, sp.Matrix]
    flat_p_equation: dict[Multiindex, sp.Matrix]
    flat_i_identity: dict[Multiindex, sp.Matrix]
    flat_p_identity: dict[Multiindex, sp.Matrix]
    flat_K: dict[Multiindex, sp.Matrix]
    cylinder_L0_candidate: dict[Multiindex, sp.Matrix]
    cylinder_L1_candidate: dict[Multiindex, sp.Matrix]
    cylinder_chain_defect: dict[Multiindex, sp.Matrix]
    parent_middle_flat: dict[Multiindex, sp.Matrix]
    parent_middle_principal: dict[Multiindex, sp.Matrix]
    endpoint_bach_principal_bilinear: dict[Multiindex, sp.Matrix]
    endpoint_stf_embedding: sp.Matrix
    bach_normalization: sp.Rational | None

    @classmethod
    def build(
        cls,
        algebraic: AdjointTractorKostantCompression,
        endpoint: ProlongedMetricEndpointComplex,
    ) -> "AdjointTractorBGGDifferentialScreen":
        _, basis = _adjoint_basis()
        p_actions = _adjoint_actions(basis[:4], basis)
        k_actions = _adjoint_actions(basis[11:15], basis)
        cohomology_d0 = _wedge_zero(p_actions)
        cohomology_d1 = _wedge_one(p_actions)
        if cohomology_d1 * cohomology_d0 != sp.zeros(90, 15):
            raise AssertionError("Lie algebra cohomology square defect")

        laplacian0 = algebraic.d1 * cohomology_d0
        laplacian1 = (
            algebraic.d2 * cohomology_d1 + cohomology_d0 * algebraic.d1
        )
        inverse0 = (
            sp.Rational(3, 32) * laplacian0**2
            + sp.Rational(7, 16) * laplacian0
        )
        inverse1 = (
            sp.Rational(23, 576) * laplacian1**4
            + sp.Rational(287, 576) * laplacian1**3
            + sp.Rational(283, 144) * laplacian1**2
            + sp.Rational(361, 144) * laplacian1
        )
        projection0 = sp.eye(15) - laplacian0 * inverse0
        projection1 = sp.eye(60) - laplacian1 * inverse1
        harmonic_p0 = (
            (algebraic.i0.T * algebraic.i0).inv()
            * algebraic.i0.T
            * projection0
        )
        harmonic_p1 = (
            (algebraic.i1.T * algebraic.i1).inv()
            * algebraic.i1.T
            * projection1
        )
        q1 = inverse0 * algebraic.d1
        q2 = inverse1 * algebraic.d2

        covector = tuple(sp.symbols("tractor_bgg_zeta_0:4"))
        epsilon0, epsilon1 = _exterior_symbols(covector)
        n0 = q1 * epsilon0
        n1 = q2 * epsilon1
        flat_l0 = (algebraic.i0 - n0 * algebraic.i0 + n0**2 * algebraic.i0).applyfunc(sp.expand)
        flat_l1 = (algebraic.i1 - n1 * algebraic.i1 + n1**2 * algebraic.i1).applyfunc(sp.expand)
        flat_k = (
            harmonic_p1 * (cohomology_d0 + epsilon0) * flat_l0
        ).applyfunc(sp.expand)
        right0 = epsilon0 * q1
        right1 = epsilon1 * q2
        inverse_right0 = sp.eye(60) - right0 + right0**2
        inverse_right1 = sp.eye(90) - right1 + right1**2
        flat_p0 = harmonic_p0
        flat_p1 = (harmonic_p1 * inverse_right0).applyfunc(sp.expand)
        flat_h0 = (q1 * inverse_right0).applyfunc(sp.expand)
        flat_h1 = (q2 * inverse_right1).applyfunc(sp.expand)

        eta = sp.diag(-1, 1, 1, 1)
        sign_substitution = {value: -value for value in covector}

        def formal_adjoint_symbol(
            operator: sp.Matrix,
            source_pairing: sp.Matrix,
            target_pairing: sp.Matrix,
        ) -> sp.Matrix:
            return (
                source_pairing.inv()
                * operator.subs(sign_substitution, simultaneous=True).T
                * target_pairing
            ).applyfunc(sp.expand)

        flat_i_equation = formal_adjoint_symbol(
            flat_p1,
            algebraic.one_form_pairing,
            algebraic.endpoint_field_pairing,
        )
        flat_p_equation = formal_adjoint_symbol(
            flat_l1,
            algebraic.endpoint_field_pairing,
            algebraic.one_form_pairing,
        )
        flat_i_identity = formal_adjoint_symbol(
            flat_p0,
            algebraic.adjoint_pairing,
            algebraic.endpoint_ghost_pairing,
        )
        flat_p_identity = formal_adjoint_symbol(
            flat_l0,
            algebraic.endpoint_ghost_pairing,
            algebraic.adjoint_pairing,
        )

        # In the cylinder scale P_ab=diag(1/2,1/2,1/2,1/2).  With the
        # tractor order (rho,mu,sigma), the remaining connection term is
        # one half of the corresponding g_+1 action in every form slot.
        rho_actions = tuple(action / 2 for action in k_actions)
        rho0 = _wedge_zero(rho_actions)
        rho1 = _wedge_one(rho_actions)
        curved_n0 = q1 * (epsilon0 + rho0)
        curved_n1 = q2 * (epsilon1 + rho1)
        cylinder_l0 = (
            algebraic.i0
            - curved_n0 * algebraic.i0
            + curved_n0**2 * algebraic.i0
        ).applyfunc(sp.expand)
        cylinder_l1 = (
            algebraic.i1
            - curved_n1 * algebraic.i1
            + curved_n1**2 * algebraic.i1
        ).applyfunc(sp.expand)
        cylinder_k = (
            harmonic_p1
            * (cohomology_d0 + epsilon0 + rho0)
            * cylinder_l0
        ).applyfunc(sp.expand)
        # This is intentionally the commuting-derivative candidate.  Its
        # defect is the fail-closed receipt for the missing LC/PBW curvature.
        cylinder_defect = (
            (cohomology_d0 + epsilon0 + rho0) * cylinder_l0
            - cylinder_l1 * cylinder_k
        ).applyfunc(sp.expand)

        two_form_metric = sp.diag(
            *(
                eta[left, left] * eta[right, right]
                for left in range(4)
                for right in range(left + 1, 4)
            )
        )
        two_form_pairing = sp.kronecker_product(
            two_form_metric, algebraic.adjoint_pairing
        )
        parent_d1 = cohomology_d1 + epsilon1
        parent_d1_adjoint_symbol = (
            algebraic.one_form_pairing.inv()
            * parent_d1.subs(
                {value: -value for value in covector}, simultaneous=True
            ).T
            * two_form_pairing
        )
        parent_maxwell = (
            parent_d1_adjoint_symbol * parent_d1
        ).applyfunc(sp.expand)
        flat_l1_adjoint_symbol = flat_l1.subs(
            {value: -value for value in covector}, simultaneous=True
        ).T
        parent_middle = (
            flat_l1_adjoint_symbol
            * algebraic.one_form_pairing
            * parent_maxwell
            * flat_l1
        ).applyfunc(sp.expand)
        parent_middle_table = _polynomial_matrix(parent_middle, covector)
        if max(map(sum, parent_middle_table)) != 4:
            raise AssertionError("compressed parent detour order did not reduce to four")
        if (
            parent_middle * flat_k
        ).applyfunc(sp.expand) != sp.zeros(9, 4):
            raise AssertionError("compressed parent detour lost gauge annihilation")
        parent_principal = _homogeneous(parent_middle, covector, 4)

        stf_embedding = sp.zeros(10, 9)
        for column in range(9):
            for left in range(4):
                for right in range(left, 4):
                    row = SYMMETRIC_COORDINATES.index((left, right))
                    stf_embedding[row, column] = (
                        eta[right, right]
                        * algebraic.i1[15 * left + right, column]
                    )
        bach_principal = sum(
            (
                coefficient
                * sp.prod(
                    covector[axis] ** multiindex[axis] for axis in range(4)
                )
                for multiindex, coefficient in endpoint.bach_coefficients
                if sum(multiindex) == 4
            ),
            sp.zeros(10),
        )
        endpoint_bilinear = (
            stf_embedding.T
            * endpoint.field_pairing
            * bach_principal
            * stf_embedding
        ).applyfunc(sp.expand)

        normalization: sp.Rational | None = None
        for parent_value, endpoint_value in zip(parent_principal, endpoint_bilinear):
            if endpoint_value == 0:
                if parent_value != 0:
                    normalization = None
                    break
                continue
            ratio = sp.cancel(parent_value / endpoint_value)
            if not ratio.is_Rational:
                normalization = None
                break
            if normalization is None:
                normalization = sp.Rational(ratio)
            elif ratio != normalization:
                normalization = None
                break
        if normalization is not None and (
            parent_principal - normalization * endpoint_bilinear
        ).applyfunc(sp.expand) != sp.zeros(9):
            normalization = None

        theorem = cls(
            algebraic=algebraic,
            cohomology_d0=cohomology_d0,
            cohomology_d1=cohomology_d1,
            kostant_laplacian0=laplacian0,
            kostant_laplacian1=laplacian1,
            kostant_inverse0=inverse0,
            kostant_inverse1=inverse1,
            harmonic_projection0=projection0,
            harmonic_projection1=projection1,
            harmonic_p0=harmonic_p0,
            harmonic_p1=harmonic_p1,
            q1=q1,
            q2=q2,
            flat_L0=_polynomial_matrix(flat_l0, covector),
            flat_L1=_polynomial_matrix(flat_l1, covector),
            flat_P0=_polynomial_matrix(flat_p0, covector),
            flat_P1=_polynomial_matrix(flat_p1, covector),
            flat_H0=_polynomial_matrix(flat_h0, covector),
            flat_H1=_polynomial_matrix(flat_h1, covector),
            flat_i_equation=_polynomial_matrix(flat_i_equation, covector),
            flat_p_equation=_polynomial_matrix(flat_p_equation, covector),
            flat_i_identity=_polynomial_matrix(flat_i_identity, covector),
            flat_p_identity=_polynomial_matrix(flat_p_identity, covector),
            flat_K=_polynomial_matrix(flat_k, covector),
            cylinder_L0_candidate=_polynomial_matrix(cylinder_l0, covector),
            cylinder_L1_candidate=_polynomial_matrix(cylinder_l1, covector),
            cylinder_chain_defect=_polynomial_matrix(cylinder_defect, covector),
            parent_middle_flat=parent_middle_table,
            parent_middle_principal=_polynomial_matrix(parent_principal, covector),
            endpoint_bach_principal_bilinear=_polynomial_matrix(endpoint_bilinear, covector),
            endpoint_stf_embedding=stf_embedding,
            bach_normalization=normalization,
        )
        theorem.verify()
        return theorem

    def verify(self) -> None:
        if self.cohomology_d1 * self.cohomology_d0 != sp.zeros(90, 15):
            raise AssertionError("cohomology differential square defect")
        if self.kostant_laplacian0 * self.kostant_inverse0 != (
            sp.eye(15) - self.harmonic_projection0
        ):
            raise AssertionError("degree-zero Kostant inverse defect")
        if self.kostant_laplacian1 * self.kostant_inverse1 != (
            sp.eye(60) - self.harmonic_projection1
        ):
            raise AssertionError("degree-one Kostant inverse defect")
        if self.harmonic_p0 * self.algebraic.i0 != sp.eye(4):
            raise AssertionError("harmonic degree-zero projection defect")
        if self.harmonic_p1 * self.algebraic.i1 != sp.eye(9):
            raise AssertionError("harmonic degree-one projection defect")

        zeta = tuple(sp.symbols("tractor_bgg_zeta_0:4"))
        epsilon0, epsilon1 = _exterior_symbols(zeta)
        l0 = _table_polynomial(self.flat_L0, zeta)
        l1 = _table_polynomial(self.flat_L1, zeta)
        p0 = _table_polynomial(self.flat_P0, zeta)
        p1 = _table_polynomial(self.flat_P1, zeta)
        h0 = _table_polynomial(self.flat_H0, zeta)
        h1 = _table_polynomial(self.flat_H1, zeta)
        k = _table_polynomial(self.flat_K, zeta)
        if self.algebraic.d1 * (self.cohomology_d0 + epsilon0) * l0 != sp.zeros(15, 4):
            raise AssertionError("flat L0 splitting defect")
        if self.algebraic.d2 * (self.cohomology_d1 + epsilon1) * l1 != sp.zeros(60, 9):
            raise AssertionError("flat L1 splitting defect")
        if (
            (self.cohomology_d0 + epsilon0) * l0 - l1 * k
        ).applyfunc(sp.expand) != sp.zeros(60, 4):
            raise AssertionError("flat BGG chain-map defect")
        total0 = self.cohomology_d0 + epsilon0
        total1 = self.cohomology_d1 + epsilon1
        if (p0 * l0).applyfunc(sp.expand) != sp.eye(4):
            raise AssertionError("flat degree-zero differential retraction defect")
        if (p1 * l1).applyfunc(sp.expand) != sp.eye(9):
            raise AssertionError("flat degree-one differential retraction defect")
        if (
            h0 * total0 + l0 * p0
        ).applyfunc(sp.expand) != sp.eye(15):
            raise AssertionError("flat degree-zero differential homotopy defect")
        if (
            total0 * h0 + h1 * total1 + l1 * p1
        ).applyfunc(sp.expand) != sp.eye(60):
            raise AssertionError("flat degree-one differential homotopy defect")
        if (
            p1 * total0 - k * p0
        ).applyfunc(sp.expand) != sp.zeros(9, 15):
            raise AssertionError("flat BGG projection chain-map defect")
        i_equation = _table_polynomial(self.flat_i_equation, zeta)
        p_equation = _table_polynomial(self.flat_p_equation, zeta)
        i_identity = _table_polynomial(self.flat_i_identity, zeta)
        p_identity = _table_polynomial(self.flat_p_identity, zeta)
        if (p_equation * i_equation).applyfunc(sp.expand) != sp.eye(9):
            raise AssertionError("flat equation-row cyclic retraction defect")
        if (p_identity * i_identity).applyfunc(sp.expand) != sp.eye(4):
            raise AssertionError("flat identity-row cyclic retraction defect")
        if max(map(sum, self.flat_L0)) != 2 or max(map(sum, self.flat_L1)) != 2:
            raise AssertionError("finite HPL truncation order drifted")
        if max(map(sum, self.flat_K)) != 1:
            raise AssertionError("first BGG operator order drifted")
        parent_middle_flat = _table_polynomial(self.parent_middle_flat, zeta)
        if max(map(sum, self.parent_middle_flat)) != 4:
            raise AssertionError("flat parent detour order drifted")
        if (
            parent_middle_flat * k
        ).applyfunc(sp.expand) != sp.zeros(9, 4):
            raise AssertionError("flat parent detour gauge defect")
        if not self.cylinder_chain_defect:
            raise AssertionError("curvature-blind cylinder guard unexpectedly vanished")
        if max(map(sum, self.cylinder_chain_defect)) > 2:
            raise AssertionError("cylinder HPL defect order drifted")

        parent = _table_polynomial(self.parent_middle_principal, zeta)
        endpoint = _table_polynomial(self.endpoint_bach_principal_bilinear, zeta)
        if self.bach_normalization is not None:
            if (parent - self.bach_normalization * endpoint).applyfunc(sp.expand) != sp.zeros(9):
                raise AssertionError("recorded Bach normalization is false")

    @classmethod
    def from_payload(
        cls,
        algebraic: AdjointTractorKostantCompression,
        payload: Mapping[str, object],
    ) -> "AdjointTractorBGGDifferentialScreen":
        if payload.get("schema_version") != 1:
            raise AssertionError("wrong differential BGG screen schema")
        matrices = payload.get("matrices")
        tables = payload.get("tables")
        if not isinstance(matrices, Mapping) or not isinstance(tables, Mapping):
            raise AssertionError("differential BGG payload is incomplete")

        def matrix(name: str) -> sp.Matrix:
            return _parse_sparse(matrices[name])

        def table(name: str) -> dict[Multiindex, sp.Matrix]:
            return _parse_table(tables[name])

        raw_normalization = payload.get("bach_normalization")
        theorem = cls(
            algebraic=algebraic,
            cohomology_d0=matrix("cohomology_d0"),
            cohomology_d1=matrix("cohomology_d1"),
            kostant_laplacian0=matrix("kostant_laplacian0"),
            kostant_laplacian1=matrix("kostant_laplacian1"),
            kostant_inverse0=matrix("kostant_inverse0"),
            kostant_inverse1=matrix("kostant_inverse1"),
            harmonic_projection0=matrix("harmonic_projection0"),
            harmonic_projection1=matrix("harmonic_projection1"),
            harmonic_p0=matrix("harmonic_p0"),
            harmonic_p1=matrix("harmonic_p1"),
            q1=matrix("Q1"),
            q2=matrix("Q2"),
            flat_L0=table("flat_L0"),
            flat_L1=table("flat_L1"),
            flat_P0=table("flat_P0"),
            flat_P1=table("flat_P1"),
            flat_H0=table("flat_H0"),
            flat_H1=table("flat_H1"),
            flat_i_equation=table("flat_i_equation"),
            flat_p_equation=table("flat_p_equation"),
            flat_i_identity=table("flat_i_identity"),
            flat_p_identity=table("flat_p_identity"),
            flat_K=table("flat_K"),
            cylinder_L0_candidate=table("cylinder_L0_candidate"),
            cylinder_L1_candidate=table("cylinder_L1_candidate"),
            cylinder_chain_defect=table("cylinder_chain_defect"),
            parent_middle_flat=table("parent_middle_flat"),
            parent_middle_principal=table("parent_middle_principal"),
            endpoint_bach_principal_bilinear=table("endpoint_bach_principal_bilinear"),
            endpoint_stf_embedding=matrix("endpoint_stf_embedding"),
            bach_normalization=(
                None if raw_normalization is None else sp.Rational(raw_normalization)
            ),
        )
        theorem.verify()
        return theorem

    def payload(self) -> dict[str, object]:
        matrices = {
            "cohomology_d0": self.cohomology_d0,
            "cohomology_d1": self.cohomology_d1,
            "kostant_laplacian0": self.kostant_laplacian0,
            "kostant_laplacian1": self.kostant_laplacian1,
            "kostant_inverse0": self.kostant_inverse0,
            "kostant_inverse1": self.kostant_inverse1,
            "harmonic_projection0": self.harmonic_projection0,
            "harmonic_projection1": self.harmonic_projection1,
            "harmonic_p0": self.harmonic_p0,
            "harmonic_p1": self.harmonic_p1,
            "Q1": self.q1,
            "Q2": self.q2,
            "endpoint_stf_embedding": self.endpoint_stf_embedding,
        }
        tables = {
            "flat_L0": self.flat_L0,
            "flat_L1": self.flat_L1,
            "flat_P0": self.flat_P0,
            "flat_P1": self.flat_P1,
            "flat_H0": self.flat_H0,
            "flat_H1": self.flat_H1,
            "flat_i_equation": self.flat_i_equation,
            "flat_p_equation": self.flat_p_equation,
            "flat_i_identity": self.flat_i_identity,
            "flat_p_identity": self.flat_p_identity,
            "flat_K": self.flat_K,
            "cylinder_L0_candidate": self.cylinder_L0_candidate,
            "cylinder_L1_candidate": self.cylinder_L1_candidate,
            "cylinder_chain_defect": self.cylinder_chain_defect,
            "parent_middle_flat": self.parent_middle_flat,
            "parent_middle_principal": self.parent_middle_principal,
            "endpoint_bach_principal_bilinear": self.endpoint_bach_principal_bilinear,
        }
        return {
            "schema_version": 1,
            "arithmetic": "exact rational polynomial",
            "bach_normalization": (
                None if self.bach_normalization is None else str(self.bach_normalization)
            ),
            "matrices": {name: _sparse_matrix(value) for name, value in matrices.items()},
            "tables": {name: _sparse_table(value) for name, value in tables.items()},
        }

    def certificate(
        self,
        payload_sha256: str,
        dependency_sha256: Mapping[str, str],
    ) -> dict[str, object]:
        defect_entries = sum(
            value != 0 for matrix in self.cylinder_chain_defect.values() for value in matrix
        )
        return {
            "schema_version": 1,
            "result": "PASS_WITH_CURVED_BOUNDARY_OPEN",
            "dependency_tag": "LOCAL-ALGEBRAIC",
            "payload_sha256": payload_sha256,
            "dependencies": dict(dependency_sha256),
            "finite_HPL": {
                "kostant_laplacian_spectra": {
                    "degree_0": {"0": 4, "-2": 6, "-4": 5},
                    "degree_1": {"0": 9, "-1": 16, "-2": 15, "-4": 19, "-6": 1},
                },
                "Q_exact_rational": True,
                "L0_maximum_derivative_order": 2,
                "L1_maximum_derivative_order": 2,
                "series_terminates_after": 2,
                "flat_splitting_defects": 0,
                "flat_chain_map_defects": 0,
                "flat_differential_retraction_defects": 0,
                "flat_differential_homotopy_defects": 0,
                "flat_all_row_cyclic_maps": {
                    "parent": [15, 60, 60, 15],
                    "compressed": [4, 9, 9, 4],
                    "dual_rows_generated_by_formal_adjoint": True,
                    "dual_retraction_defects": 0,
                },
                "first_BGG_order": 1,
                "first_BGG_project_normalization": "K_BGG=(1/2) K_TF after vector/covector metric identification",
                "compressed_parent_detour_order": 4,
                "compressed_parent_detour_gauge_defects": 0,
            },
            "cylinder_metric_split_screen": {
                "Schouten_g_plus_term_included": True,
                "Levi_Civita_PBW_curvature_included": False,
                "commuting_derivative_chain_defect_entries": defect_entries,
                "commuting_derivative_chain_defect_sha256": _digest_table(self.cylinder_chain_defect),
                "interpretation": (
                    "The nonzero defect is the exact obstruction to treating the cylinder "
                    "Levi-Civita derivatives as commuting in the HPL formula.  It is not a "
                    "no-go for curved BGG splitting; the missing curvature commutators must "
                    "be supplied by a tensor-slot PBW implementation."
                ),
            },
            "middle_symbol_comparison": {
                "parent_operator": "delta^nabla d^nabla on adjoint-tractor one-forms",
                "compressed_order": 4,
                "endpoint_target": "S^T J_met Bach_bar S",
                "coefficientwise_principal_match": self.bach_normalization is not None,
                "normalization": (
                    None if self.bach_normalization is None else str(self.bach_normalization)
                ),
            },
            "literature_anchor": {
                "title": "Yang-Mills detour complexes and conformal geometry",
                "arxiv": "math/0606401",
                "use": "parent detour translation diagram and formal-adjoint compression",
            },
            "support": {
                "all_emitted_HPL_maps_finite_order": True,
                "pointwise_and_differential_candidates_support_local": True,
                "contains_nonlocal_projector": False,
                "contains_Green_operator": False,
            },
            "theorem_boundary": {
                "flat_associated_graded_BGG_chain_maps_exact": True,
                "curved_cylinder_BGG_chain_maps_exact": False,
                "curved_differential_homotopy_exact": False,
                "full_Bach_coefficient_match": False,
                "parent_green_homotopy_transferred": False,
                "next_required_step": (
                    "Implement the induced adjoint-tractor/form tensor slots in the "
                    "curvature-aware PBW composer, cancel the recorded cylinder chain "
                    "defect, and only then compare all Bach derivative orders."
                ),
            },
        }


def write_json(path: Path, value: Mapping[str, object]) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
