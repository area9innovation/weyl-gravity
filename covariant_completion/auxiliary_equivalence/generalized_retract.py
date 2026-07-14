"""Exact 66-to-30 all-row contraction of the auxiliary Fourier complex.

The ordinary-derivative field Hessian has an algebraically invertible
``f--f`` block.  Shifting ``f`` by its exact equation-of-motion solution
block diagonalizes the Hessian.  Gauge invariance then makes the shifted
tensor gauge invariant.  Together with

``eta=xi_0-d sigma`` and ``Qv=-eta``

this leaves precisely three contractible arrows in the added BV cotangent
sector: the Stueckelberg ghost/field pair, the auxiliary tensor/equation
pair, and the dual field/ghost-antifield pair.

Every change is polynomial in the Fourier covector except for the inverse of
the pointwise auxiliary mass matrix.  Hence the corresponding covariant
formulas are finite-order differential or pointwise bundle maps and preserve
compact, spacelike-compact, and unrestricted smooth supports.  Their exact
curved lower-order chain-map reconstruction remains part of the separate
global witness certificate.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib

import sympy as sp

from covariant_completion.auxiliary_witness import OrdinaryDerivativeWeylSystem


def _digest(matrix: sp.MatrixBase) -> str:
    payload = sp.srepr(sp.ImmutableDenseMatrix(matrix)).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


@dataclass(frozen=True)
class GeneralizedAuxiliaryRetract:
    system: OrdinaryDerivativeWeylSystem
    ghost_new_to_old: sp.Matrix
    field_new_to_old: sp.Matrix
    shifted_gauge_map: sp.Matrix
    shifted_hessian: sp.Matrix
    original_differential: sp.Matrix
    total_new_to_old: sp.Matrix
    ordered_differential: sp.Matrix
    core_differential: sp.Matrix
    auxiliary_differential: sp.Matrix
    auxiliary_homotopy: sp.Matrix
    inclusion: sp.Matrix
    projection: sp.Matrix
    total_homotopy: sp.Matrix

    @staticmethod
    def build() -> "GeneralizedAuxiliaryRetract":
        system = OrdinaryDerivativeWeylSystem.build()
        zeta = system.covector
        equation = system.gauge_invariant_flat_hessian
        mass = equation[10:20, 10:20]

        # New ghosts are (xi_-2,eta,sigma); old xi_0=eta+d sigma.
        ghost_new_to_old = sp.eye(9)
        ghost_new_to_old[4:8, 8] = zeta

        # New fields are (h,f_hat,v), with
        # f_old=f_hat-M^{-1}(E_fh h+E_fv v).  This is the exact shifted
        # auxiliary variable, not merely a principal-symbol ansatz.
        field_new_to_old = sp.eye(24)
        field_new_to_old[10:20, 0:10] = (
            -mass.inv() * equation[10:20, 0:10]
        )
        field_new_to_old[10:20, 20:24] = (
            -mass.inv() * equation[10:20, 20:24]
        )

        shifted_gauge_map = sp.simplify(
            field_new_to_old.inv()
            * system.gauge_map
            * ghost_new_to_old
        )
        negative_covector = {component: -component for component in zeta}
        shifted_hessian = sp.simplify(
            field_new_to_old.subs(negative_covector).T
            * equation
            * field_new_to_old
        )

        # Lift both triangular changes to the cotangent rows.  The resulting
        # 66-by-66 similarity is the actual four-row BV change of basis, not
        # a dimension/rank surrogate.  With the row pairings J and Y, the
        # dual transformations are fixed by
        # U(-zeta)^T J U_dual=J and V(-zeta)^T Y V_dual=Y.
        field_pairing = system.field_fibre_pairing
        ghost_pairing = system.gauge_fixing_pairing
        field_dual_new_to_old = sp.simplify(
            field_pairing.inv()
            * field_new_to_old.subs(negative_covector).inv().T
            * field_pairing
        )
        ghost_dual_new_to_old = sp.simplify(
            ghost_pairing.inv()
            * ghost_new_to_old.subs(negative_covector).inv().T
            * ghost_pairing
        )

        original_differential = sp.zeros(66)
        original_differential[9:33, 0:9] = system.gauge_map
        original_differential[33:57, 9:33] = sp.simplify(
            field_pairing.inv() * equation
        )
        original_differential[57:66, 33:57] = system.gauge_condition

        total_new_to_old = sp.diag(
            ghost_new_to_old,
            field_new_to_old,
            field_dual_new_to_old,
            ghost_dual_new_to_old,
        )
        transformed_differential = sp.simplify(
            total_new_to_old.inv()
            * original_differential
            * total_new_to_old
        )

        # The retained 30 coordinates are
        #   (xi_-2,sigma; h; h^*; xi_-2^*,sigma^*)
        # where the equation and identity coordinates are selected using the
        # cross pairings J and Y.  The remaining 36 coordinates are exactly
        #   (eta; f_hat,v; f_hat^*,v^*; eta^*).
        core_indices = (
            list(range(0, 4))
            + [8]
            + list(range(9, 19))
            + list(range(43, 53))
            + list(range(61, 66))
        )
        auxiliary_indices = (
            list(range(4, 8))
            + list(range(19, 29))
            + list(range(29, 33))
            + list(range(33, 43))
            + list(range(53, 57))
            + list(range(57, 61))
        )
        order = core_indices + auxiliary_indices
        permutation = sp.eye(66)[:, order]
        ordered_differential = sp.simplify(
            permutation.T * transformed_differential * permutation
        )
        core_differential = ordered_differential[:30, :30]
        auxiliary_differential = ordered_differential[30:, 30:]

        # In auxiliary order the three nonzero arrows are
        # eta -> v, f_hat -> f_hat^*, and v^* -> eta^*.  Construct the
        # contraction from the exact extracted blocks, so its normalization
        # cannot drift from the BV pairings.
        arrow_eta_v = auxiliary_differential[14:18, 0:4]
        arrow_f_fstar = auxiliary_differential[18:28, 4:14]
        arrow_vstar_etastar = auxiliary_differential[32:36, 28:32]
        auxiliary_homotopy = sp.zeros(36)
        auxiliary_homotopy[0:4, 14:18] = -arrow_eta_v.inv()
        auxiliary_homotopy[4:14, 18:28] = -arrow_f_fstar.inv()
        auxiliary_homotopy[28:32, 32:36] = -arrow_vstar_etastar.inv()

        ordered_new_to_old = total_new_to_old * permutation
        inclusion_ordered = sp.eye(66)[:, :30]
        projection_ordered = inclusion_ordered.T
        homotopy_ordered = sp.zeros(66)
        homotopy_ordered[30:, 30:] = auxiliary_homotopy
        inclusion = sp.simplify(ordered_new_to_old * inclusion_ordered)
        projection = sp.simplify(
            projection_ordered * ordered_new_to_old.inv()
        )
        total_homotopy = sp.simplify(
            ordered_new_to_old * homotopy_ordered * ordered_new_to_old.inv()
        )

        result = GeneralizedAuxiliaryRetract(
            system=system,
            ghost_new_to_old=ghost_new_to_old,
            field_new_to_old=field_new_to_old,
            shifted_gauge_map=shifted_gauge_map,
            shifted_hessian=shifted_hessian,
            original_differential=original_differential,
            total_new_to_old=total_new_to_old,
            ordered_differential=ordered_differential,
            core_differential=core_differential,
            auxiliary_differential=auxiliary_differential,
            auxiliary_homotopy=auxiliary_homotopy,
            inclusion=inclusion,
            projection=projection,
            total_homotopy=total_homotopy,
        )
        result.verify()
        return result

    def verify(self) -> None:
        if self.ghost_new_to_old.det() != 1:
            raise AssertionError("the ghost change is not unipotent")
        if self.field_new_to_old.det() != 1:
            raise AssertionError("the shifted auxiliary change is not unipotent")

        # The shifted auxiliary tensor is gauge invariant, while the only
        # eta action is the unit Stueckelberg arrow eta -> -v.
        if self.shifted_gauge_map[10:20, :] != sp.zeros(10, 9):
            raise AssertionError("the shifted auxiliary tensor is not gauge invariant")
        if self.shifted_gauge_map[20:24, 4:8] != -sp.eye(4):
            raise AssertionError("the eta/v Stueckelberg arrow is not normalized")
        if self.shifted_gauge_map[20:24, 8] != sp.zeros(4, 1):
            raise AssertionError("sigma still acts on the Stueckelberg vector")

        # Exact formal congruence split of the quadratic Hessian.
        for rows, columns, shape in (
            (slice(10, 20), slice(0, 10), (10, 10)),
            (slice(10, 20), slice(20, 24), (10, 4)),
            (slice(0, 10), slice(10, 20), (10, 10)),
            (slice(20, 24), slice(10, 20), (4, 10)),
        ):
            if self.shifted_hessian[rows, columns] != sp.zeros(*shape):
                raise AssertionError("the auxiliary Hessian did not split exactly")
        if (
            self.shifted_hessian[10:20, 10:20]
            != self.system.auxiliary_mass_hessian
        ):
            raise AssertionError("the shifted auxiliary mass block changed")

        q = self.auxiliary_differential
        homotopy = self.auxiliary_homotopy
        if q * q != sp.zeros(36):
            raise AssertionError("the added all-row BV sector is not a complex")
        if q * homotopy + homotopy * q != -sp.eye(36):
            raise AssertionError("the added all-row BV sector did not contract")

        if self.ordered_differential[:30, 30:] != sp.zeros(30, 36):
            raise AssertionError("the retained core maps into the auxiliary sector")
        if self.ordered_differential[30:, :30] != sp.zeros(36, 30):
            raise AssertionError("the auxiliary sector maps into the retained core")
        if sp.simplify(
            self.core_differential * self.core_differential
        ) != sp.zeros(30):
            raise AssertionError("the retained 30-dimensional BV core is not a complex")

        inclusion = self.inclusion
        projection = self.projection
        if projection * inclusion != sp.eye(30):
            raise AssertionError("p i is not the identity")
        if sp.simplify(
            self.original_differential * inclusion
            - inclusion * self.core_differential
        ) != sp.zeros(66, 30):
            raise AssertionError("the 66-to-30 inclusion is not a chain map")
        if sp.simplify(
            projection * self.original_differential
            - self.core_differential * projection
        ) != sp.zeros(30, 66):
            raise AssertionError("the 66-to-30 projection is not a chain map")
        if sp.simplify(
            inclusion * projection
            - sp.eye(66)
            - self.original_differential * self.total_homotopy
            - self.total_homotopy * self.original_differential
        ) != sp.zeros(66):
            raise AssertionError("i p-1=Qk+kQ failed in the selected convention")

    def certificate(self, *, reverify: bool = True) -> dict[str, object]:
        if reverify:
            self.verify()
        return {
            "schema": "pure-weyl-support-local-generalized-auxiliary-retract-v1",
            "field_shift": (
                "f_hat=f+M^{-1}(E_fh h+E_fv v), with M=E_ff pointwise invertible"
            ),
            "ghost_shift": "eta=xi_0-d sigma",
            "exact_split": {
                "f_hat_gauge_variation": "zero",
                "Q_v": "-eta",
                "shifted_hessian": "E_metric(h,v) direct-sum M_f",
                "formal_congruence": "U(-zeta)^T E_aux(zeta) U(zeta)",
            },
            "all_added_bv_rows": [
                {"arrow": "eta -> -v", "dimension": 4},
                {"arrow": "f_hat -> M f_hat^*", "dimension": 10},
                {"arrow": "v^* -> -eta^*", "dimension": 4},
            ],
            "sdr": {
                "p_i": "identity",
                "i_p_minus_identity": "Qk+kQ",
                "full_auxiliary_complex_dimension": 66,
                "retained_metric_BV_core_dimension": 30,
                "contractible_dimension": 36,
                "mass_inverse_pointwise": True,
                "inclusion_shape": list(self.inclusion.shape),
                "projection_shape": list(self.projection.shape),
                "chain_map_identities": ["Q_aux i=i Q_met", "p Q_aux=Q_met p"],
            },
            "cotangent_lift": (
                "antifields transform by the inverse formal transpose of the "
                "unipotent field/ghost changes; the displayed dual arrow is its exact block"
            ),
            "support": {
                "compact": "preserved",
                "spacelike_compact": "preserved",
                "smooth_global": "preserved",
                "reason": (
                    "U and U^{-1} are finite differential operators; M^{-1} is a "
                    "pointwise bundle map"
                ),
            },
            "reattached_existing_summands": {
                "trace_Weyl": "certified pointwise doublet",
                "nonminimal": "certified antighost/multiplier cotangent doublets",
            },
            "matrix_sha256": {
                "ghost_new_to_old": _digest(self.ghost_new_to_old),
                "field_new_to_old": _digest(self.field_new_to_old),
                "shifted_gauge_map": _digest(self.shifted_gauge_map),
                "shifted_hessian": _digest(self.shifted_hessian),
                "original_differential": _digest(self.original_differential),
                "total_new_to_old": _digest(self.total_new_to_old),
                "ordered_differential": _digest(self.ordered_differential),
                "core_differential": _digest(self.core_differential),
                "auxiliary_differential": _digest(self.auxiliary_differential),
                "auxiliary_homotopy": _digest(self.auxiliary_homotopy),
                "inclusion": _digest(self.inclusion),
                "projection": _digest(self.projection),
                "total_homotopy": _digest(self.total_homotopy),
            },
            "theorem_boundary": (
                "the exact 66-to-30 Fourier-complex contraction is proved and all "
                "maps have support-local differential formulas.  Reconstructing "
                "their complete curved lower-order chain identities and the induced "
                "covariant boundary current remains a separate certificate"
            ),
        }
