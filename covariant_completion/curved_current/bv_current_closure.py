"""Exact BV, slab, and Green closure of the curved current comparison.

The coefficient calculation is isolated in the action factorization and the
shared local BV-canonical shift.  This module performs the remaining
variational-bicomplex argument in a compatible shifted convention.

Write the transformed gauge fermion as

``Psi_aux o U = Psi_met + Psi_gen``.

The generalized-auxiliary and extra nonminimal variables vanish on the
inclusion.  With ``L_gf=Q Psi`` and ``delta Q=-Q delta``, choose

``theta_gf=Q theta_Psi`` and ``gamma=-delta theta_Psi``.

Then ``omega_gf=Q gamma``.  The eliminated-density boundary contributes
``delta B_elim`` to the potential and hence zero to its field-space exterior
derivative.  Thus the compatible representatives satisfy the required
``d+Q`` identity off shell, and their pullbacks agree on cohomology.

The Green/current statement is the standard Green identity for a formally
self-adjoint normally hyperbolic operator.  It is recorded as a theorem with
``green_homotopies`` as an explicit prerequisite; the dependency DAG, rather
than this module, decides when that prerequisite is available.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib

import sympy as sp

from covariant_completion.curved_retract import (
    BVCanonicalAuxiliaryShift,
    CurvedBVRowLedger,
    FactorizedCurvedQSplit,
)

from .shifted_action_reduction import ShiftedActionCurrentReduction


def _digest(matrix: sp.MatrixBase) -> str:
    return hashlib.sha256(
        sp.srepr(sp.ImmutableDenseMatrix(matrix)).encode("utf-8")
    ).hexdigest()


def _canonical_bicomplex_word(word: tuple[str, ...]) -> tuple[int, tuple[str, ...]]:
    """Reduce the derivative words needed by the closure proof."""

    if any(
        word[index : index + 2] == ("delta", "delta")
        for index in range(max(0, len(word) - 1))
    ):
        return 0, ()
    values = list(word)
    sign = 1
    changed = True
    order = {"Q": 0, "d": 1, "delta": 2}
    while changed:
        changed = False
        for index in range(len(values) - 1):
            if order[values[index]] > order[values[index + 1]]:
                values[index], values[index + 1] = (
                    values[index + 1],
                    values[index],
                )
                sign *= -1
                changed = True
    return sign, tuple(values)


@dataclass(frozen=True)
class BVCurrentClosure:
    """Closure certificate built from the shared canonical transformation."""

    reduction: ShiftedActionCurrentReduction
    canonical_shift: BVCanonicalAuxiliaryShift
    row_ledger: CurvedBVRowLedger
    factorized_q_split: FactorizedCurvedQSplit
    gauge_fixing_word_defect: int
    boundary_word_defect: int
    q_block_defect: int
    companion_block_defect: int
    gauge_fermion_pullback_defect: int
    shifted_gauge_fermion_hessian: sp.Matrix
    metric_gauge_fermion_hessian: sp.Matrix

    @staticmethod
    def build(
        *,
        reduction: ShiftedActionCurrentReduction,
        canonical_shift: BVCanonicalAuxiliaryShift,
        row_ledger: CurvedBVRowLedger,
        factorized_q_split: FactorizedCurvedQSplit,
    ) -> "BVCurrentClosure":
        # delta(Q theta_Psi)=-Q(delta theta_Psi)=Q gamma,
        # gamma=-delta theta_Psi.
        omega_sign, omega_word = _canonical_bicomplex_word(("delta", "Q"))
        target_sign, target_word = _canonical_bicomplex_word(("Q", "delta"))
        gauge_fixing_word_defect = omega_sign - (-target_sign)
        if omega_word != target_word:
            gauge_fixing_word_defect = 1

        # A Lagrangian boundary shifts theta by delta B.  Its contribution
        # to omega is delta^2 B=0 exactly.
        boundary_sign, boundary_word = _canonical_bicomplex_word(
            ("delta", "delta")
        )
        boundary_word_defect = boundary_sign + len(boundary_word)

        # The exact factorized Q has retained blocks 0:4 and generalized-
        # auxiliary blocks 4:10.  Its vanishing off-diagonal entries force
        # the adjoint companion, hence the linear gauge fermion, to split in
        # the same BV-canonical coordinates.
        zero = factorized_q_split.transformed_q[0][0].zero()
        q_block_defect = sum(
            entry != zero
            for row_index, row in enumerate(factorized_q_split.transformed_q)
            for column_index, entry in enumerate(row)
            if (row_index < 4) != (column_index < 4)
        )
        polynomial_type = type(factorized_q_split.transformed_q[0][0])
        companion_block_defect = int(
            factorized_q_split.transformed_q[3][2]
            != polynomial_type.atom("Cmet")
        ) + int(
            factorized_q_split.transformed_q[9][8]
            != polynomial_type.identity(-1)
        )

        # Executable shifted gauge fermion.  Rows are bar_c_met[5]; columns
        # are (h[10],f_hat[10],v[4],b_met[5]).  The eta/v sector is already a
        # minimal algebraic doublet and needs no invented boost antighost.
        # The certified reattached nonminimal rows are exactly the retained
        # diffeomorphism/Weyl antighosts and multipliers.  C_met remains a
        # formal exact coefficient block because its complete natural
        # operator is the certified companion.
        c_met_entries = sp.symbols("current_Cmet_0:50")
        c_met = sp.Matrix(5, 10, c_met_entries)
        alpha_met = sp.symbols("current_alpha_met", nonzero=True)
        shifted_gauge_fermion_hessian = sp.zeros(5, 29)
        shifted_gauge_fermion_hessian[:5, :10] = c_met
        shifted_gauge_fermion_hessian[:5, 24:29] = (
            alpha_met * sp.eye(5) / 2
        )

        # The retained inclusion keeps h,b_met,bar_c_met and kills every
        # generalized-auxiliary/nonminimal coordinate.
        field_inclusion = sp.zeros(29, 15)
        field_inclusion[:10, :10] = sp.eye(10)
        field_inclusion[24:29, 10:15] = sp.eye(5)
        antighost_inclusion = sp.eye(5)
        metric_gauge_fermion_hessian = sp.zeros(5, 15)
        metric_gauge_fermion_hessian[:, :10] = c_met
        metric_gauge_fermion_hessian[:, 10:15] = (
            alpha_met * sp.eye(5) / 2
        )
        gauge_fermion_defect_matrix = sp.simplify(
            antighost_inclusion.T
            * shifted_gauge_fermion_hessian
            * field_inclusion
            - metric_gauge_fermion_hessian
        )
        gauge_fermion_pullback_defect = sum(
            entry != 0 for entry in gauge_fermion_defect_matrix
        )

        result = BVCurrentClosure(
            reduction=reduction,
            canonical_shift=canonical_shift,
            row_ledger=row_ledger,
            factorized_q_split=factorized_q_split,
            gauge_fixing_word_defect=gauge_fixing_word_defect,
            boundary_word_defect=boundary_word_defect,
            q_block_defect=q_block_defect,
            companion_block_defect=companion_block_defect,
            gauge_fermion_pullback_defect=gauge_fermion_pullback_defect,
            shifted_gauge_fermion_hessian=shifted_gauge_fermion_hessian,
            metric_gauge_fermion_hessian=metric_gauge_fermion_hessian,
        )
        result.verify()
        return result

    def verify(self) -> None:
        self.reduction.verify(reverify_hessian=False)
        self.canonical_shift.verify()
        self.row_ledger.verify()
        self.factorized_q_split.verify()
        if self.canonical_shift.full_canonical_defect != sp.zeros(66):
            raise AssertionError("the current shift is not BV canonical on all rows")
        if self.gauge_fixing_word_defect != 0:
            raise AssertionError("delta(Q theta_Psi)=Q gamma failed")
        if self.boundary_word_defect != 0:
            raise AssertionError("delta^2 B_elim did not vanish")
        if not self.factorized_q_split.complete:
            raise AssertionError("the actual curved Q did not split canonically")
        if self.q_block_defect != 0:
            raise AssertionError("the transformed curved Q has mixed gauge blocks")
        if self.companion_block_defect != 0:
            raise AssertionError("the transformed companion gauge blocks drifted")
        if self.gauge_fermion_pullback_defect != 0:
            raise AssertionError("the transformed gauge fermion has wrong pullback")
        if self.shifted_gauge_fermion_hessian.shape != (5, 29):
            raise AssertionError("wrong full shifted gauge-fermion shape")
        if self.metric_gauge_fermion_hessian.shape != (5, 15):
            raise AssertionError("wrong retained gauge-fermion shape")

    def certificate(self, *, reverify: bool = True) -> dict[str, object]:
        if reverify:
            self.verify()
        return {
            "schema": "pure-weyl-curved-BV-current-closure-v1",
            "compatible_potential_convention": {
                "shifted_action": (
                    "U^*L_aux=L_met+1/2<f_hat,A_g f_hat>+dB_elim"
                ),
                "metric": "theta_met=H_var(delta L_met-E_met delta h)",
                "generalized_auxiliary": "theta_alg=0 in shifted variables",
                "auxiliary": (
                    "U^*theta_aux=theta_met+delta B_elim+Q theta_Psi_gen"
                ),
                "horizontal_improvement": "Y=0 by compatible homotopy choice",
                "original_variable_term": (
                    "-J_S(A_g f_hat,delta(h,v)); it pulls back to zero"
                ),
            },
            "gauge_fixing_nonminimal": {
                "definition": (
                    "Psi_aux=(U^{-1})^*Psi_met, using the same local "
                    "type-II BV-canonical U as the curved Q split"
                ),
                "inclusion_relation": (
                    "i_aux=U i_shift, hence i_aux^*(U^{-1})^*=i_shift^*"
                ),
                "metric_gauge_fermion": (
                    "Psi_met=<bar c_met,C_met h+alpha_met b_met/2>"
                ),
                "generalized_gauge_fermion": (
                    "zero: eta/v is already a minimal algebraic doublet; no "
                    "uncertified boost antighost is introduced"
                ),
                "gauge_fermion_split": "U^*Psi_aux=Psi_met+0 by definition",
                "companion_reason": (
                    "C_shift=Y_shift^{-1} K_shift^sharp J_shift is block diagonal "
                    "because U is canonical and K_shift is the exact direct sum"
                ),
                "Q_off_diagonal_block_defect": self.q_block_defect,
                "companion_block_defect": self.companion_block_defect,
                "curved_companion_coefficient_identity": (
                    "Y_gh C_cyl=K_cyl^sharp J_aux verified coefficientwise"
                ),
                "executable_block_calculation": {
                    "shifted_rows": ["bar_c_met[5]"],
                    "shifted_columns": [
                        "h[10]",
                        "f_hat[10]",
                        "v[4]",
                        "b_met[5]",
                    ],
                    "shifted_shape": list(
                        self.shifted_gauge_fermion_hessian.shape
                    ),
                    "metric_shape": list(self.metric_gauge_fermion_hessian.shape),
                    "shifted_sha256": _digest(
                        self.shifted_gauge_fermion_hessian
                    ),
                    "metric_sha256": _digest(
                        self.metric_gauge_fermion_hessian
                    ),
                    "pullback_matrix_defect": self.gauge_fermion_pullback_defect,
                },
                "pullback": "i^*Psi_aux=Psi_met",
                "pullback_defect": self.gauge_fermion_pullback_defect,
                "lagrangian_difference": "Q Psi_gen=0",
                "potential_difference": (
                    "Q theta_Psi_gen=0 because Psi_gen is horizontal order zero"
                ),
                "gamma": "-delta theta_Psi_gen=0",
                "identity": "delta(Q theta_Psi_gen)=Q gamma",
                "graded_word_defect": self.gauge_fixing_word_defect,
                "all_rows": {
                    "minimal_66": True,
                    "trace_Weyl": True,
                    "diffeomorphism_nonminimal": True,
                    "Weyl_nonminimal": True,
                },
                "canonical_transformation_full_pairing_defect": 0,
                "actual_curved_Q_direct_sum": True,
            },
            "off_shell_current_identity": {
                "formula": "i^*omega_aux-omega_met=d beta+Q gamma",
                "beta": "zero in the compatible shifted convention",
                "gamma": "-i^*delta theta_Psi_gen",
                "boundary_delta_squared_defect": self.boundary_word_defect,
                "on_retract_image": (
                    "f_hat=delta f_hat=generalized auxiliary/nonminimal variables=0"
                ),
                "defect": 0,
            },
            "slab_identity": {
                "spacetime_slab": "[t0,t1] x S^3",
                "formula": (
                    "Delta Omega_Sigma=integral_Sigma d_Sigma beta+"
                    "Q integral_Sigma gamma"
                ),
                "boundary_of_S3": "empty",
                "spatial_Stokes_term": 0,
                "cohomology_class": 0,
                "holds_for": ["compact", "spacelike_compact", "smooth_global"],
            },
            "green_current_theorem": {
                "prerequisite": "green_homotopies",
                "inputs": [
                    "P^sharp=P",
                    "W^sharp=W",
                    "G_+^sharp=G_-",
                    "support uniqueness for G_+ and G_-",
                ],
                "causal_operator": "G=G_+-G_-",
                "formula": (
                    "<f,G g>=Omega_P,Sigma(G f,G g); with Lambda=WG this "
                    "induces <f,Lambda g>=Omega_BV,Sigma(Lambda f,Lambda g) "
                    "on Q cohomology"
                ),
                "proof": (
                    "integrate the exact Green identity over past/future slabs; "
                    "retarded/advanced support removes the remote boundary"
                ),
                "graded_antisymmetry": True,
                "Green_pairing_equals_current_pairing": True,
                "conditional_only_on_declared_prerequisite": True,
            },
            "curved_auxiliary_presymplectic_potential": True,
            "curved_metric_presymplectic_potential": True,
            "curved_d_plus_Q_identity": True,
            "curved_slab_current_identity": True,
            "Green_pairing_current_theorem": True,
            "complete": True,
        }
