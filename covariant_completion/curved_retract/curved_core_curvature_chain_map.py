"""Curved 30-row core coordinates for the curvature chain map.

The auxiliary-to-curvature equation attachment was derived directly from
the curved action Hessian.  A later rank-14 diagnostic attempted to compose
that attachment with the *flat Fourier* equation projection.  This mixes two
coordinate systems: the true curved cotangent projection contains the full
formal adjoint of the local tangent shift, including its order-zero cylinder
curvature terms.

This module reconstructs the curved core projection coefficientwise.  If
``S_h=sum_I S_I nabla_(I)`` is the metric part of the auxiliary shift and
``D=J_aux[h,f]``, then on the fibre-identified equation row

``p_E = (D^-1 S_h^sharp D, 1, 0)``.

It proves that the already-certified attachment is exactly
``A_aux=A_core p_E``.  The field projection is simply ``p_M(h,f,v)=h``, so
the curvature state map, which is defined only from ``h``, already equals
``T_core p_M``.  The identity projection is also reconstructed.  Its
derivative part lands in the Weyl-scalar core identity and is annihilated by
``B_core``; consequently the existing order-zero ``B_aux`` is exactly
``B_core p_I`` and no derivative repair is present.

The remaining two ingredients are imported fail-closed by the verifier:
the exhaustive curved equation square and the actual curved all-row SDR.
Together with the directly checked metric-core identity square below, these
give both lifted chain relations without ordinary-symbol multiplication.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
from typing import Mapping

import sympy as sp

from covariant_completion.curved_operator.conventions import (
    SYMMETRIC_COORDINATES,
    _ordinary_system,
)
from covariant_completion.curved_operator.covariant_jets import CovariantJetBasis
from covariant_completion.curved_operator.rank14_full_cone_rees_gate import (
    _provisional_shift,
)
from covariant_completion.curved_operator.rank14_weyl_cotton_incoming_map_ledger import (
    Rank14WeylCottonIncomingMapLedger,
    _auxiliary_identity_map,
    _bach_to_curvature,
)
from covariant_completion.curved_operator.weyl_3plus1 import (
    tracefree_symmetric_spacetime_basis,
)
from covariant_completion.curved_retract.curvature_auxiliary_chain_map import (
    _digest_tables,
    _symmetric_coordinate_inclusion,
    _target_extraction,
)


Multiindex = tuple[int, int, int, int]
CoefficientTable = tuple[tuple[Multiindex, sp.Matrix], ...]


def _digest(matrix: sp.MatrixBase) -> str:
    return hashlib.sha256(
        sp.srepr(sp.ImmutableSparseMatrix(matrix)).encode("utf-8")
    ).hexdigest()


def _nonzero_count(matrix: sp.MatrixBase) -> int:
    return sum(int(value != 0) for value in matrix)


def _table_nonzero_count(table: CoefficientTable) -> int:
    return sum(_nonzero_count(matrix) for _, matrix in table)


def _metric_identity_tables() -> CoefficientTable:
    """Return ``C_core=(-2 div, trace)`` in the metric-core basis."""

    signature = (-1, 1, 1, 1)
    basis = tracefree_symmetric_spacetime_basis()
    output: list[tuple[Multiindex, sp.Matrix]] = []
    for derivative in range(4):
        coefficient = sp.zeros(5, 10)
        for column, tensor in enumerate(basis):
            for row in range(4):
                coefficient[row, column] = (
                    -2 * signature[derivative] * tensor[derivative, row]
                )
        multiindex = tuple(int(axis == derivative) for axis in range(4))
        output.append((multiindex, coefficient))
    output.append(((0, 0, 0, 0), sp.zeros(5, 10)))
    return tuple(output)


@dataclass(frozen=True)
class CurvedCoreCurvatureChainMap:
    """Exact curved core projections and their curvature attachments."""

    equation_projection_coefficients: CoefficientTable
    equation_attachment_coefficients: CoefficientTable
    independently_reconstructed_attachment: CoefficientTable
    core_equation_attachment: sp.Matrix
    core_equation_coordinate_map: sp.Matrix
    identity_projection_coefficients: CoefficientTable
    core_identity_attachment: sp.Matrix
    auxiliary_identity_attachment: sp.Matrix
    actual_core_identity_coefficients: CoefficientTable
    core_identity_defects: tuple[sp.Matrix, ...]

    @staticmethod
    def build() -> "CurvedCoreCurvatureChainMap":
        basis = CovariantJetBasis.build()
        geometry = basis.geometry
        source = _ordinary_system()
        shift = _provisional_shift(basis)
        multiindices = tuple(geometry.exhaustive_multiindices(2))

        # D is the nondegenerate h--f cross block in J_aux.  The curved
        # equation projection is the formal cotangent transform of the
        # triangular field shift, expressed on Ebar=J_aux^-1 E_raw.
        cross_pairing = source.field_fibre_pairing[:10, 10:20]
        cross_inverse = cross_pairing.inv()
        p_equation: dict[Multiindex, sp.Matrix] = {
            multiindex: sp.zeros(10, 24) for multiindex in multiindices
        }
        zero = (0, 0, 0, 0)
        p_equation[zero][:, 10:20] = sp.eye(10)

        shift_coefficients: dict[Multiindex, sp.Matrix] = {}
        for multiindex in multiindices:
            coefficient = sp.zeros(10)
            for column in range(10):
                metric = basis.covariant_monomial_symmetric(
                    column, multiindex, 2
                )
                image = shift.apply(metric, geometry.zero_covector())
                coefficient[:, column] = sp.Matrix(
                    [image[a][b].value for a, b in SYMMETRIC_COORDINATES]
                )
            shift_coefficients[multiindex] = coefficient
            p_equation[multiindex][:, :10] = (
                cross_inverse
                * ((-1) ** sum(multiindex) * coefficient.T)
                * cross_pairing
            )

        projection = _target_extraction() * _symmetric_coordinate_inclusion()
        raw_core = (
            _bach_to_curvature()
            * projection
            * source.tensor_pairing.inv()
        )
        core_attachment = (
            raw_core * cross_pairing
        ).applyfunc(sp.expand)

        # The metric identity certificate uses action-Bach coordinates
        # (trace-free scalar/mixed/spatial-STF plus one trace coordinate),
        # whereas the retained 30-row core uses paired symmetric cotangent
        # coordinates.  Keep this order-zero coordinate change explicit.
        trace_row = source.trace * source.tensor_pairing.inv() * cross_pairing
        core_coordinate_map = (
            projection * source.tensor_pairing.inv() * cross_pairing
        ).col_join(trace_row).applyfunc(sp.expand)
        action_bach_attachment = sp.zeros(40, 10)
        action_bach_attachment[10:15, 4:9] = -sp.eye(5) / 2
        action_bach_attachment[32:35, 1:4] = -sp.eye(3) / 2
        action_bach_attachment[38, 0] = -sp.Rational(3, 2)
        if (
            action_bach_attachment * core_coordinate_map
            != core_attachment
        ):
            raise AssertionError("paired core/action-Bach coordinate map drifted")

        # First construction: compose the metric-core attachment with the
        # exact curved cotangent projection.
        attachment = tuple(
            (
                multiindex,
                (core_attachment * p_equation[multiindex]).applyfunc(sp.expand),
            )
            for multiindex in multiindices
        )

        # Independent coordinate construction used by the exhaustive
        # curvature-equation certificate: build A_raw and only then convert
        # to the paired Ebar row with J_aux.
        independently_reconstructed: list[tuple[Multiindex, sp.Matrix]] = []
        for multiindex in multiindices:
            raw = sp.zeros(40, 24)
            if multiindex == zero:
                raw[:, :10] = raw_core
            raw[:, 10:20] = (
                raw_core
                * ((-1) ** sum(multiindex) * shift_coefficients[multiindex].T)
            )
            independently_reconstructed.append(
                (
                    multiindex,
                    (raw * source.field_fibre_pairing).applyfunc(sp.expand),
                )
            )

        # p_I is the cotangent lift of eta=xi_0-d sigma.  Its derivative
        # coefficients only enter the fifth (Weyl scalar) core identity.
        p_identity: dict[Multiindex, sp.Matrix] = {
            zero: sp.zeros(5, 9)
        }
        p_identity[zero][:4, 4:8] = sp.eye(4)
        p_identity[zero][4, 8] = 1
        signature = (1, -1, -1, -1)
        for axis in range(4):
            multiindex = tuple(int(index == axis) for index in range(4))
            p_identity[multiindex] = sp.zeros(5, 9)
            p_identity[multiindex][4, axis] = signature[axis]

        b_core = sp.zeros(14, 5)
        b_core[6:9, 1:4] = -sp.eye(3) / 4
        b_core[12, 0] = -sp.Rational(1, 4)
        b_auxiliary = (b_core * p_identity[zero]).applyfunc(sp.expand)

        # Direct coefficientwise metric-core square N A_core=B_core C_core.
        # C_core must be transformed to the same paired equation coordinates
        # as A_core; using the action-Bach table directly is the coordinate
        # mismatch which produced the spurious rank-four defect.
        ledger = Rank14WeylCottonIncomingMapLedger.build()
        action_identity = _metric_identity_tables()
        c_core = tuple(
            (
                multiindex,
                (coefficient * core_coordinate_map).applyfunc(sp.expand),
            )
            for multiindex, coefficient in action_identity
        )
        c_by_multiindex = dict(c_core)
        n_tables = ledger.identity_complex_tables
        n_by_multiindex = {
            (1, 0, 0, 0): n_tables[0],
            (0, 1, 0, 0): n_tables[1],
            (0, 0, 1, 0): n_tables[2],
            (0, 0, 0, 1): n_tables[3],
            zero: n_tables[4],
        }
        core_defects = tuple(
            (
                n_by_multiindex[multiindex] * core_attachment
                - b_core * c_by_multiindex[multiindex]
            ).applyfunc(sp.expand)
            for multiindex in (
                (1, 0, 0, 0),
                (0, 1, 0, 0),
                (0, 0, 1, 0),
                (0, 0, 0, 1),
                zero,
            )
        )

        result = CurvedCoreCurvatureChainMap(
            equation_projection_coefficients=tuple(sorted(p_equation.items())),
            equation_attachment_coefficients=attachment,
            independently_reconstructed_attachment=tuple(
                independently_reconstructed
            ),
            core_equation_attachment=core_attachment,
            core_equation_coordinate_map=core_coordinate_map,
            identity_projection_coefficients=tuple(sorted(p_identity.items())),
            core_identity_attachment=b_core,
            auxiliary_identity_attachment=b_auxiliary,
            actual_core_identity_coefficients=c_core,
            core_identity_defects=core_defects,
        )
        result.verify()
        return result

    def verify(self) -> None:
        if len(self.equation_projection_coefficients) != 15:
            raise AssertionError("curved p_E coefficient coverage drifted")
        if any(
            matrix.shape != (10, 24)
            for _, matrix in self.equation_projection_coefficients
        ):
            raise AssertionError("curved p_E coefficient shape drifted")
        if self.equation_attachment_coefficients != (
            self.independently_reconstructed_attachment
        ):
            raise AssertionError("A_core p_E does not equal the emitted A_aux")
        if self.core_equation_attachment.shape != (40, 10):
            raise AssertionError("metric-core attachment shape drifted")
        if self.core_equation_attachment.rank() != 9:
            raise AssertionError("metric-core attachment rank drifted")
        if self.core_equation_coordinate_map.shape != (10, 10):
            raise AssertionError("core equation coordinate map shape drifted")
        if self.core_equation_coordinate_map.rank() != 10:
            raise AssertionError("core equation coordinate map is degenerate")
        if len(self.identity_projection_coefficients) != 5:
            raise AssertionError("curved p_I coefficient coverage drifted")
        if any(
            matrix.shape != (5, 9)
            for _, matrix in self.identity_projection_coefficients
        ):
            raise AssertionError("curved p_I coefficient shape drifted")
        p_identity = dict(self.identity_projection_coefficients)
        for multiindex, matrix in p_identity.items():
            if sum(multiindex) and (
                self.core_identity_attachment * matrix != sp.zeros(14, 9)
            ):
                raise AssertionError("a derivative p_I term leaked into B_aux")
        if self.auxiliary_identity_attachment != _auxiliary_identity_map():
            raise AssertionError("B_core p_I does not equal the certified B_aux")
        if len(self.actual_core_identity_coefficients) != 5 or any(
            matrix.shape != (5, 10)
            for _, matrix in self.actual_core_identity_coefficients
        ):
            raise AssertionError("actual paired C_core table drifted")
        if any(defect != sp.zeros(14, 10) for defect in self.core_identity_defects):
            raise AssertionError("N A_core-B_core C_core is nonzero")

    def certificate(
        self,
        *,
        equation_certificate: Mapping[str, object],
        curved_retract_certificate: Mapping[str, object],
    ) -> dict[str, object]:
        self.verify()
        if equation_certificate.get("schema") != (
            "pure-weyl-curvature-auxiliary-equation-chain-map-v1"
        ):
            raise AssertionError("wrong curved equation-chain certificate")
        a_certificate = equation_certificate.get("A_equation")
        if not isinstance(a_certificate, Mapping):
            raise AssertionError("missing A_equation certificate")
        if not equation_certificate.get("first_chain_relation_exact"):
            raise AssertionError("the exhaustive curved equation square is open")
        t_certificate = equation_certificate.get("T_state")
        if not isinstance(t_certificate, Mapping) or not (
            t_certificate.get("operator") == "(C1,div C1)"
            and t_certificate.get("shape") == [26, 24]
            and t_certificate.get("maximum_order") == 3
        ):
            raise AssertionError("the metric-only curvature state map is unbound")
        if a_certificate.get("sha256") != _digest_tables(
            self.equation_attachment_coefficients
        ):
            raise AssertionError("curved A_aux table digest drifted")

        if curved_retract_certificate.get("schema") != (
            "pure-weyl-curved-deformation-retract-status-v1"
        ):
            raise AssertionError("wrong curved retract certificate")
        promotion = curved_retract_certificate.get("promotion_criteria")
        factorized = curved_retract_certificate.get("factorized_actual_curved_Q")
        if not isinstance(promotion, Mapping) or not (
            promotion.get("curved_p_is_chain_map") is True
            and promotion.get("actual_curved_Q_conjugation_verified") is True
            and promotion.get("all_full_BV_rows_included") is True
        ):
            raise AssertionError("the actual curved p_E/p_I chain map is open")
        if not isinstance(factorized, Mapping):
            raise AssertionError("missing factorized actual curved Q")
        chain_maps = factorized.get("chain_maps")
        exact_inputs = factorized.get("exact_inputs")
        if not isinstance(chain_maps, Mapping) or not (
            chain_maps.get("p_Q_aux_equals_Q_met_p") is True
        ):
            raise AssertionError("the curved Q projection square is open")
        if not isinstance(exact_inputs, Mapping) or exact_inputs.get(
            "companion"
        ) != "Y_gh C=K^sharp J_aux coefficientwise":
            raise AssertionError("the projected curved companion is unbound")

        p_equation = dict(self.equation_projection_coefficients)
        p_identity = dict(self.identity_projection_coefficients)
        nonzero_p_e = _table_nonzero_count(self.equation_projection_coefficients)
        derivative_p_i = sum(
            _nonzero_count(matrix)
            for multiindex, matrix in self.identity_projection_coefficients
            if sum(multiindex)
        )
        return {
            "schema": "pure-weyl-curved-core-curvature-chain-map-v1",
            "coordinate_correction": {
                "invalid_projection": "flat-Fourier p_E",
                "actual_projection": "p_E=(D^-1 S_h^sharp D,1,0)",
                "D": "J_aux[h,f] cross pairing",
                "full_curved_shift_orders": [0, 1, 2],
                "ordinary_symbol_substitution_used": False,
            },
            "metric_core": {
                "ranks": {"fields": 10, "equations": 10, "identities": 5},
                "p_M": "pointwise projection (h,f,v) -> h",
                "T_new": "T_core p_M=T_state; no correction",
                "reason": "T_state=(C1 h,div C1 h) has no f or v columns",
                "equation_coordinate_map": (
                    "paired symmetric core -> action-Bach plus trace"
                ),
                "equation_coordinate_map_rank": (
                    self.core_equation_coordinate_map.rank()
                ),
                "equation_coordinate_map_sha256": _digest(
                    self.core_equation_coordinate_map
                ),
            },
            "equation_projection": {
                "shape": [10, 24],
                "maximum_order": 2,
                "coefficient_multiindices": len(p_equation),
                "nonzero_coefficients": nonzero_p_e,
                "sha256": _digest_tables(self.equation_projection_coefficients),
            },
            "equation_attachment": {
                "formula": "A_new=A_core p_E",
                "shape": [40, 24],
                "maximum_order": 2,
                "coefficient_multiindices": len(
                    self.equation_attachment_coefficients
                ),
                "nonzero_coefficients": _table_nonzero_count(
                    self.equation_attachment_coefficients
                ),
                "independent_raw_then_paired_defect": 0,
                "sha256": _digest_tables(self.equation_attachment_coefficients),
                "matches_exhaustive_curved_equation_certificate": True,
            },
            "identity_projection": {
                "shape": [5, 9],
                "maximum_order": 1,
                "coefficient_multiindices": len(p_identity),
                "derivative_coefficients": derivative_p_i,
                "derivative_image": "Weyl-scalar core identity",
                "B_core_annihilates_derivative_image": True,
                "sha256": _digest_tables(self.identity_projection_coefficients),
            },
            "identity_attachment": {
                "formula": "B_new=B_core p_I",
                "shape": [14, 9],
                "maximum_order": 0,
                "nonzero_coefficients": _nonzero_count(
                    self.auxiliary_identity_attachment
                ),
                "derivative_repair_required": False,
                "sha256": _digest(self.auxiliary_identity_attachment),
            },
            "core_chain_squares": {
                "E_WC_T_core_minus_A_core_E_core": (
                    "pulled back from the exhaustive curved equation square"
                ),
                "N_A_core_minus_B_core_C_core_defect_counts": [
                    _nonzero_count(defect) for defect in self.core_identity_defects
                ],
                "metric_identity_square_exact": True,
                "actual_paired_C_core_sha256": _digest_tables(
                    self.actual_core_identity_coefficients
                ),
            },
            "lifted_chain_squares": {
                "E_WC_T_new_minus_A_new_E_aux": "zero",
                "N_A_new_minus_B_new_C_aux": "zero",
                "derivation": [
                    "T_new=T_core p_M and A_new=A_core p_E",
                    "p_E E_aux=E_core p_M from the actual curved SDR",
                    "A_new equals the exhaustive curved A_aux table",
                    "B_new=B_core p_I",
                    (
                        "p_I C_aux=C_core p_E is the equation-to-identity "
                        "block of p Q_aux=Q_core p in the factorized actual "
                        "curved SDR"
                    ),
                    "N A_core=B_core C_core coefficientwise",
                ],
                "exact": True,
                "projection_square_derivation": {
                    "source": "factorized_actual_curved_Q.chain_maps",
                    "all_row_identity": "p Q_aux=Q_core p",
                    "selected_block": "paired equations -> identities",
                    "selected_formula": "p_I C_aux=C_core p_E",
                    "formal_not_sampled": True,
                },
            },
            "support": {
                "finite_order": True,
                "maximum_projection_order": 2,
                "pointwise_inverse": "D^-1 only",
                "inverse_Laplacian_or_curl": False,
                "spectral_projector": False,
                "Green_operator": False,
            },
            "correction_to_rank14_rees_diagnostic": (
                "retain the existing curved A and order-zero B; replace the "
                "flat-Fourier p_E used in the diagnostic by the full curved "
                "cotangent projection before any PBW/Rees extraction"
            ),
            "warranted_atomic_flags": [
                "rank14_curved_core_projection_exact",
                "rank14_curved_attachment_chain_squares_exact",
            ],
            "status_flags_promoted": [],
            "proof_boundary": (
                "the corrected local chain carrier is exact; its mapping-cone "
                "contraction, Green inverse and causal homotopy remain separate"
            ),
            "fail_closed": True,
        }
