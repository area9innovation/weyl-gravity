"""Cyclic all-row lifts of the retained temporal scalar completion.

The temporal pair-(1,6) Douglis candidate needs a rank-three operator on the
retained auxiliary field row.  It is not enough to insert that operator in
``P``: it must be the anticommutator of the *actual* prolonged differential
with a degree-minus-one, odd-cyclic witness contribution.

This module performs that test in the exact sixteen-block mapping cylinder.
For a companion-like map ``X:M_aux -> G_aux`` its cyclic partner is the
formal adjoint ``Xsharp:I_aux -> Ebar_aux``.  Hence

``Delta W[ G,M ]=X``, ``Delta W[ Ebar,I ]=Xsharp``

gives the four forced split diagonal corrections

``Delta P_G=X K``, ``Delta P_M=K X``,
``Delta P_E=Xsharp C`` and ``Delta P_I=C Xsharp``.

In particular, there is no off-diagonal base/cone pollution; the endpoint
ghost/identity blocks are required by the chain anticommutator and are not
silently discarded.

The sparse temporal matrix used by the first Douglis certificate is in the
image of ``K(dt)`` and therefore has such a lift.  It is not self-adjoint in
the action pairing, so its forced cotangent partner is ``Dsharp``, not the
same matrix.  This is perfectly compatible with BV cyclicity, but it rules
out an identical same-block lift.  Two useful comparisons are also exact:

* the natural scalar-ghost projector is self-adjoint and gives identical
  paired blocks, but leaves the temporal Jordan defect;
* ``-2 Pi_(h00,f00,v0)`` has a cyclic lift with an adjoint partner and makes
  the corrected temporal Schur block diagonalizable.

All constructions are finite-order and use the parallel cylinder time
normal.  No arbitrary-covector hyperbolicity or Green flag is promoted.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib

import sympy as sp

from covariant_completion.curved_retract.curvature_mapping_cylinder_kernel import (
    BLOCK_NAMES,
    CurvatureMappingCylinderKernel,
    Matrix,
    SIZE,
    _add,
    _multiply,
    _zero,
)
from covariant_completion.minimal_witness.formal_operators import (
    OperatorPolynomial,
)

from .conventions import CurvedBVConventions
from .expanded_relative_witness_douglis import ExpandedRelativeDouglisCandidate
from .relative_saddle_witness import _cyclic_defect, _derived_partner


SCALAR_GHOST_INDICES = (0, 4, 8)  # xi_0, kappa_0, sigma


def _digest(matrix: sp.MatrixBase) -> str:
    return hashlib.sha256(
        sp.srepr(sp.ImmutableDenseMatrix(matrix)).encode("utf-8")
    ).hexdigest()


def _formal_digest(matrix: Matrix) -> str:
    payload = "\n".join(
        ",".join(entry.display() for entry in row) for row in matrix
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _nonzero_blocks(matrix: Matrix) -> tuple[tuple[int, int], ...]:
    zero = OperatorPolynomial.zero()
    return tuple(
        (row, column)
        for row in range(SIZE)
        for column in range(SIZE)
        if matrix[row][column] != zero
    )


def _scalar_ghost_projector() -> sp.Matrix:
    result = sp.zeros(9)
    for index in SCALAR_GHOST_INDICES:
        result[index, index] = 1
    return result


def _left_factor(generator: sp.MatrixBase, target: sp.MatrixBase) -> sp.Matrix:
    """Return the unique ``X`` with ``generator X=target``.

    The temporal generator has full column rank nine, so the displayed
    rational left inverse is exact and uniqueness follows immediately.
    """

    return (generator.T * generator).inv() * generator.T * target


def _forced_derivative_partner(
    companion_coefficient: sp.MatrixBase,
    field_pairing: sp.MatrixBase,
    ghost_pairing: sp.MatrixBase,
) -> sp.Matrix:
    """Formal-adjoint partner of a first-derivative companion coefficient."""

    return -field_pairing.inv() * companion_coefficient.T * ghost_pairing


def _generic_delta_w(kernel: CurvatureMappingCylinderKernel) -> Matrix:
    result = _zero()
    # Derive, rather than guess, the partner incidence and sign from
    # W^sharp Omega-D Omega W=0.
    partner_row, partner_column, sign = _derived_partner(kernel.pairing, 0, 1)
    if (partner_row, partner_column, sign) != (2, 3, 1):
        raise AssertionError("scalar endpoint cyclic partner drifted")
    result[0][1] = OperatorPolynomial.atom("Sscalar")
    result[2][3] = OperatorPolynomial.atom("Sscalarsharp", sign)
    return result


def _is_zero(matrix: Matrix) -> bool:
    zero = OperatorPolynomial.zero()
    return all(entry == zero for row in matrix for entry in row)


def _jordan_data(matrix: sp.MatrixBase) -> tuple[str, bool, dict[str, int]]:
    polynomial = sp.factor(matrix.charpoly().as_expr())
    eigenvalues = matrix.eigenvals()
    diagonalizable = all(
        len((matrix - eigenvalue * sp.eye(matrix.rows)).nullspace()) == multiplicity
        for eigenvalue, multiplicity in eigenvalues.items()
    )
    return str(polynomial), diagonalizable, {
        str(eigenvalue): int(multiplicity)
        for eigenvalue, multiplicity in eigenvalues.items()
    }


@dataclass(frozen=True)
class ExpandedRelativeScalarCyclicLift:
    """Exact endpoint-witness lift and its three temporal realizations."""

    conventions: CurvedBVConventions
    douglis: ExpandedRelativeDouglisCandidate
    kernel: CurvatureMappingCylinderKernel
    split_delta_w: Matrix
    prolonged_delta_w: Matrix
    split_delta_p: Matrix
    prolonged_delta_p: Matrix
    scalar_ghost_projector: sp.Matrix
    natural_scalar_diagonal: sp.Matrix
    sparse_companion_temporal: sp.Matrix
    sparse_partner_temporal: sp.Matrix
    sparse_partner_diagonal: sp.Matrix
    alternative_scalar_diagonal: sp.Matrix
    alternative_companion_temporal: sp.Matrix
    alternative_partner_temporal: sp.Matrix
    alternative_partner_diagonal: sp.Matrix

    @staticmethod
    def build() -> "ExpandedRelativeScalarCyclicLift":
        conventions = CurvedBVConventions.build()
        douglis = ExpandedRelativeDouglisCandidate.build()
        kernel = CurvatureMappingCylinderKernel.build()

        split_delta_w = _generic_delta_w(kernel)
        prolonged_delta_w = _multiply(
            _multiply(kernel.new_to_old, split_delta_w), kernel.old_to_new
        )
        split_delta_p = _add(
            _multiply(kernel.split_differential, split_delta_w),
            _multiply(split_delta_w, kernel.split_differential),
        )
        prolonged_delta_p = _add(
            _multiply(kernel.prolonged_differential, prolonged_delta_w),
            _multiply(prolonged_delta_w, kernel.prolonged_differential),
        )

        scalar = douglis.scalar_completion
        k0 = conventions.gauge_generator.derivative_coefficients[0]
        c0 = conventions.gauge_companion.derivative_coefficients[0]
        projector = _scalar_ghost_projector()
        natural = k0 * projector * c0

        sparse = scalar.gauge_scalar_diagonal
        sparse_companion = _left_factor(k0, sparse)
        sparse_partner = _forced_derivative_partner(
            sparse_companion, conventions.field_pairing, conventions.ghost_pairing
        )
        sparse_partner_diagonal = sparse_partner * c0

        field_projector = (
            scalar.gauge_scalar_embedding * scalar.gauge_scalar_embedding.T
        )
        alternative = -2 * field_projector
        alternative_companion = _left_factor(k0, alternative)
        alternative_partner = _forced_derivative_partner(
            alternative_companion,
            conventions.field_pairing,
            conventions.ghost_pairing,
        )
        alternative_partner_diagonal = alternative_partner * c0

        result = ExpandedRelativeScalarCyclicLift(
            conventions=conventions,
            douglis=douglis,
            kernel=kernel,
            split_delta_w=split_delta_w,
            prolonged_delta_w=prolonged_delta_w,
            split_delta_p=split_delta_p,
            prolonged_delta_p=prolonged_delta_p,
            scalar_ghost_projector=projector,
            natural_scalar_diagonal=natural,
            sparse_companion_temporal=sparse_companion,
            sparse_partner_temporal=sparse_partner,
            sparse_partner_diagonal=sparse_partner_diagonal,
            alternative_scalar_diagonal=alternative,
            alternative_companion_temporal=alternative_companion,
            alternative_partner_temporal=alternative_partner,
            alternative_partner_diagonal=alternative_partner_diagonal,
        )
        result.verify()
        return result

    def _field_shur(self, diagonal: sp.MatrixBase) -> sp.Matrix:
        scalar = self.douglis.scalar_completion
        # The corrected first-order adjoint sign gives B D^-1 C=+Pi_vector.
        return (
            scalar.paired_hessian_temporal
            + diagonal
            - scalar.vector_gauge_projector
        )

    def verify(self) -> None:
        self.conventions.verify()
        self.douglis.verify()
        self.kernel.verify()

        if not _is_zero(_cyclic_defect(self.split_delta_w, self.kernel.pairing)):
            raise AssertionError("split scalar Delta W is not odd BV cyclic")
        if not _is_zero(
            _cyclic_defect(self.prolonged_delta_w, self.kernel.pairing)
        ):
            raise AssertionError("prolonged scalar Delta W is not odd BV cyclic")

        expected = _zero()
        expected[0][0] = (
            OperatorPolynomial.atom("Sscalar") * OperatorPolynomial.atom("K")
        )
        expected[1][1] = (
            OperatorPolynomial.atom("K") * OperatorPolynomial.atom("Sscalar")
        )
        expected[2][2] = (
            OperatorPolynomial.atom("Sscalarsharp")
            * OperatorPolynomial.atom("C")
        )
        expected[3][3] = (
            OperatorPolynomial.atom("C")
            * OperatorPolynomial.atom("Sscalarsharp")
        )
        if self.split_delta_p != expected:
            raise AssertionError("scalar lift produced unexpected split cross terms")
        conjugated = _multiply(
            _multiply(self.kernel.new_to_old, self.split_delta_p),
            self.kernel.old_to_new,
        )
        if self.prolonged_delta_p != conjugated:
            raise AssertionError("prolonged scalar anticommutator did not conjugate")

        # The scalar ghost projector is a genuine orthogonal summand for the
        # action ghost pairing, so Pi C and K Pi are exact formal adjoints in
        # every derivative and zeroth-order coefficient.
        pi = self.scalar_ghost_projector
        y = self.conventions.ghost_pairing
        j = self.conventions.field_pairing
        if pi**2 != pi or y * pi != pi.T * y:
            raise AssertionError("scalar ghost projector is not Y-self-adjoint")
        for axis in range(4):
            k = self.conventions.gauge_generator.derivative_coefficients[axis]
            c = self.conventions.gauge_companion.derivative_coefficients[axis]
            if y * pi * c != -(k * pi).T * j:
                raise AssertionError("natural scalar derivative adjoint defect")
        kzero = self.conventions.gauge_generator.zeroth_coefficient
        czero = self.conventions.gauge_companion.zeroth_coefficient
        if y * pi * czero != (kzero * pi).T * j:
            raise AssertionError("natural scalar zeroth-order adjoint defect")

        scalar = self.douglis.scalar_completion
        k0 = self.conventions.gauge_generator.derivative_coefficients[0]
        c0 = self.conventions.gauge_companion.derivative_coefficients[0]
        sparse = scalar.gauge_scalar_diagonal
        if k0.rank() != 9 or k0.row_join(sparse).rank() != 9:
            raise AssertionError("sparse scalar diagonal is not in im K(dt)")
        if k0 * self.sparse_companion_temporal != sparse:
            raise AssertionError("sparse scalar companion factorization failed")
        sparse_sharp = j.inv() * sparse.T * j
        if self.sparse_partner_diagonal != sparse_sharp:
            raise AssertionError("sparse cotangent diagonal is not Dsharp")
        if (sparse_sharp - sparse).rank() != 4:
            raise AssertionError("sparse same-block cyclic obstruction drifted")

        natural = self.natural_scalar_diagonal
        if natural.rank() != 3 or j * natural != (j * natural).T:
            raise AssertionError("natural scalar diagonal is not J-self-adjoint")
        if natural == sparse or (natural - sparse).rank() != 2:
            raise AssertionError("natural/sparse scalar distinction drifted")
        if (
            scalar.gauge_scalar_embedding.T
            * natural
            * scalar.gauge_scalar_embedding
            != scalar.gauge_scalar_embedding.T
            * sparse
            * scalar.gauge_scalar_embedding
        ):
            raise AssertionError("natural lift changed the retained scalar restriction")

        alternative = self.alternative_scalar_diagonal
        if k0 * self.alternative_companion_temporal != alternative:
            raise AssertionError("alternative scalar companion factorization failed")
        alternative_sharp = j.inv() * alternative.T * j
        if self.alternative_partner_diagonal != alternative_sharp:
            raise AssertionError("alternative cotangent diagonal is not Dsharp")
        if (alternative_sharp - alternative).rank() != 4:
            raise AssertionError("alternative same-block cyclic obstruction drifted")

        expected_spectra = {
            "sparse": (1, "(lambda + 1)**24", False),
            "natural": (1, "(lambda + 1)**24", False),
            "alternative": (8, "(lambda + 1)**21*(lambda + 2)**3", True),
        }
        for name, diagonal in (
            ("sparse", sparse),
            ("natural", natural),
            ("alternative", alternative),
        ):
            shur = self._field_shur(diagonal)
            determinant, polynomial, diagonalizable = (
                int(sp.factor(shur.det())),
                *_jordan_data(shur)[:2],
            )
            expected_det, expected_polynomial, expected_diagonalizable = (
                expected_spectra[name]
            )
            if (
                shur.rank() != 24
                or determinant != expected_det
                or polynomial != expected_polynomial
                or diagonalizable != expected_diagonalizable
            ):
                raise AssertionError(f"{name} temporal Schur data drifted")

    def certificate(self) -> dict[str, object]:
        self.verify()
        scalar = self.douglis.scalar_completion
        sparse = scalar.gauge_scalar_diagonal

        def branch(name: str, diagonal: sp.Matrix) -> dict[str, object]:
            shur = self._field_shur(diagonal)
            polynomial, diagonalizable, eigenvalues = _jordan_data(shur)
            return {
                "name": name,
                "rank": diagonal.rank(),
                "sha256": _digest(diagonal),
                "field_Schur_formula": "Eaux_2(dt)+D-Pi_vector",
                "field_Schur_rank": shur.rank(),
                "field_Schur_determinant": int(sp.factor(shur.det())),
                "field_Schur_characteristic_polynomial": polynomial,
                "field_Schur_eigenvalues": eigenvalues,
                "field_Schur_diagonalizable": diagonalizable,
            }

        split_blocks = _nonzero_blocks(self.split_delta_p)
        prolonged_blocks = _nonzero_blocks(self.prolonged_delta_p)
        return {
            "schema": "pure-weyl-expanded-relative-scalar-cyclic-lift-v1",
            "actual_degree_minus_one_lift": {
                "split_entries": [
                    "Delta W[G_aux,M_aux]=Sscalar",
                    "Delta W[Ebar_aux,I_aux]=Sscalarsharp",
                ],
                "complete_split_anticommutator": {
                    "G_aux": "Sscalar K",
                    "M_aux": "K Sscalar",
                    "Ebar_aux": "Sscalarsharp C",
                    "I_aux": "C Sscalarsharp",
                    "all_curvature_cone_rows": "zero",
                },
                "cyclic_partner_derived_from_odd_pairing": True,
                "partner_sign": 1,
                "split_odd_cyclicity_defect": 0,
                "prolonged_odd_cyclicity_defect": 0,
                "split_P_equals_Q_DeltaW_plus_DeltaW_Q": True,
                "prolonged_P_equals_Q_DeltaW_plus_DeltaW_Q": True,
                "split_affected_blocks": [
                    [BLOCK_NAMES[row], BLOCK_NAMES[column]]
                    for row, column in split_blocks
                ],
                "split_unwanted_cross_blocks": 0,
                "prolonged_affected_blocks": [
                    [BLOCK_NAMES[row], BLOCK_NAMES[column]]
                    for row, column in prolonged_blocks
                ],
                "prolonged_cross_blocks_are_exact_canonical_conjugates": True,
                "all_16_rows_enumerated": True,
                "degree": -1,
                "support_local": True,
                "finite_differential_order": True,
                "uses_parallel_cylinder_time_normal": True,
            },
            "sparse_retained_diagonal": {
                **branch("sparse", sparse),
                "lies_in_image_K_dt": True,
                "rank_K_dt": 9,
                "rank_K_augmented_D": 9,
                "companion_factor_formula": "X=(K^T K)^-1 K^T D",
                "companion_factor_unique": True,
                "companion_factor_sha256": _digest(
                    self.sparse_companion_temporal
                ),
                "M_row_correction": "D_sparse",
                "Ebar_row_correction": "D_sparse_sharp=J^-1 D_sparse^T J",
                "D_sparse_sharp_minus_D_sparse_rank": 4,
                "identical_same_block_cyclic_lift_exists": False,
                "cyclic_lift_with_formal_adjoint_partner_exists": True,
                "nonidentical_partner_is_valid_for_BV_witness": True,
            },
            "natural_scalar_ghost_projection": {
                **branch("natural", self.natural_scalar_diagonal),
                "projector_indices": list(SCALAR_GHOST_INDICES),
                "projector_fields": ["xi_0", "kappa_0", "sigma"],
                "projector_idempotent": True,
                "projector_Y_self_adjoint": True,
                "companion": "Pi_scalar C",
                "forced_partner": "K Pi_scalar",
                "all_derivative_and_zeroth_adjoint_defects": 0,
                "M_and_Ebar_diagonals_identical": True,
                "J_self_adjoint": True,
                "equals_sparse_diagonal": False,
                "difference_from_sparse_rank": 2,
                "same_3_by_3_retained_scalar_restriction": True,
                "temporal_Jordan_obstruction_removed": False,
            },
            "diagonalizable_alternative": {
                **branch("alternative", self.alternative_scalar_diagonal),
                "formula": "-2 Pi_(h00,f00,v0)",
                "lies_in_image_K_dt": True,
                "companion_factor_sha256": _digest(
                    self.alternative_companion_temporal
                ),
                "M_row_correction": "D_alt",
                "Ebar_row_correction": "D_alt_sharp=J^-1 D_alt^T J",
                "D_alt_sharp_minus_D_alt_rank": 4,
                "identical_same_block_cyclic_lift_exists": False,
                "cyclic_lift_with_formal_adjoint_partner_exists": True,
                "nonidentical_partner_is_valid_for_BV_witness": True,
                "temporal_Jordan_obstruction_removed": True,
            },
            "formal_matrix_sha256": {
                "Delta_W_split": _formal_digest(self.split_delta_w),
                "Delta_W_prolonged": _formal_digest(self.prolonged_delta_w),
                "Delta_P_split": _formal_digest(self.split_delta_p),
                "Delta_P_prolonged": _formal_digest(self.prolonged_delta_p),
            },
            "analytic_boundary": {
                "arbitrary_covector_characteristic_certified": False,
                "common_positive_symmetrizer_certified": False,
                "lower_order_relative_witness_completed": False,
                "all_degree_Green_hyperbolicity_certified": False,
                "causal_Green_operators_constructed": False,
            },
            "constructive_conclusion": (
                "the retained rank-three scalar operator has an actual local "
                "odd-cyclic all-row endpoint lift.  The sparse and -2-projector "
                "choices necessarily acquire formal-adjoint cotangent blocks; "
                "the natural scalar-ghost projection gives identical paired "
                "blocks but retains the temporal Jordan defect.  The -2 branch "
                "removes that temporal defect and is the preferred next "
                "arbitrary-covector/symmetrizer candidate"
            ),
            "prolonged_green_witness": False,
            "curvature_causal_green_operators": False,
            "causal_green_homotopy": False,
            "warranted_atomic_flags": [],
            "status_flags_promoted": [],
            "fail_closed": True,
        }
