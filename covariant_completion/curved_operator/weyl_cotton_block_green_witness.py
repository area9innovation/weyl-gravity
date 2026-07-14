"""Generalized block Green witness for the Weyl--Cotton analytic kernel.

Let ``L`` be the exact constraint-adjusted 26-state evolution, ``K`` its
fourteen-component constraint operator, ``R`` the compatible-source
operator and ``S`` the fourteen-state subsidiary evolution.  The exact
curved sourced identity is

``S K = R L``.

It makes the compatibility sequence

``U --(L,K)--> F + C --(-R,S)--> I``

a differential complex.  On the block order ``(U,F,C,I,G,G*)``, where
``G -> G*`` denotes the shifted Weyl/Cotton graph pairs, choose

``W(F)=U``, ``W(I)=C`` and ``W(G*)=G``.

Then ``P=QW+WQ`` is block triangular with diagonal blocks
``L,L,S,S,1,1`` and sole possible off-diagonal block ``K-R``.  In the
canonical coefficient identification used by the cylinder calculation,
``K`` and ``R`` have the same natural-operator table, so that block also
vanishes.

This is an exact witness for the curvature compatibility kernel and the
algebraic graph rows.  It is not yet the complete prolonged BV witness:
the metric/auxiliary gauge rows, their cotangent-adjoint rows and the
nonminimal summands have not been assembled with this mapping cone.
Accordingly no project status flag is promoted here.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
import hashlib

import sympy as sp

from covariant_completion.curved_retract.curvature_prolongation_sdr import (
    CurvatureProlongationGraphSDR,
)
from covariant_completion.minimal_witness.formal_operators import (
    OperatorPolynomial,
)

from .weyl_cotton_hyperbolic import (
    CONSTRAINT_SLICES,
    STATE_SLICES,
    ConstraintAdjustedWeylCottonEvolution,
    _put,
)


FormalMatrix = list[list[OperatorPolynomial]]


def _zero(size: int) -> FormalMatrix:
    return [
        [OperatorPolynomial.zero() for _ in range(size)] for _ in range(size)
    ]


def _identity(size: int) -> FormalMatrix:
    result = _zero(size)
    for index in range(size):
        result[index][index] = OperatorPolynomial.identity()
    return result


def _add(left: FormalMatrix, right: FormalMatrix) -> FormalMatrix:
    return [
        [
            left[row][column] + right[row][column]
            for column in range(len(left))
        ]
        for row in range(len(left))
    ]


def _multiply(left: FormalMatrix, right: FormalMatrix) -> FormalMatrix:
    size = len(left)
    result = _zero(size)
    for row in range(size):
        for column in range(size):
            entry = OperatorPolynomial.zero()
            for middle in range(size):
                entry = entry + left[row][middle] * right[middle][column]
            result[row][column] = entry
    return result


def _reduce_integrability(entry: OperatorPolynomial) -> OperatorPolynomial:
    """Reduce the exact natural-operator relation ``S K=R L``."""

    values: dict[tuple[str, ...], Fraction] = {}
    for word, coefficient in entry.terms:
        reduced = word
        while True:
            try:
                position = next(
                    index
                    for index in range(len(reduced) - 1)
                    if reduced[index : index + 2] == ("S", "K")
                )
            except StopIteration:
                break
            reduced = (
                reduced[:position]
                + ("R", "L")
                + reduced[position + 2 :]
            )
        values[reduced] = values.get(reduced, Fraction()) + coefficient
    return OperatorPolynomial._from_dict(values)


def _reduce_matrix(matrix: FormalMatrix) -> FormalMatrix:
    return [[_reduce_integrability(entry) for entry in row] for row in matrix]


def _is_zero(matrix: FormalMatrix) -> bool:
    zero = OperatorPolynomial.zero()
    return all(entry == zero for row in matrix for entry in row)


def _digest(matrix: FormalMatrix) -> str:
    payload = "\n".join(
        ",".join(entry.display() for entry in row) for row in matrix
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _table_digest(tables: tuple[sp.Matrix, ...]) -> str:
    payload = "\n".join(
        sp.srepr(sp.ImmutableDenseMatrix(table)) for table in tables
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _constraint_definition_tables(
    adjusted: ConstraintAdjustedWeylCottonEvolution,
) -> tuple[sp.Matrix, ...]:
    """Reconstruct ``K(U)=(q,r,a,c,s,t)`` independently of source rows."""

    spatial: list[sp.Matrix] = []
    for axis, (divergence, vector_curl) in enumerate(
        zip(
            adjusted.divergence_coefficients,
            adjusted.vector_curl_coefficients,
            strict=True,
        )
    ):
        coefficient = sp.zeros(14, 26)
        _put(coefficient, CONSTRAINT_SLICES[0], STATE_SLICES[0], -divergence)
        _put(coefficient, CONSTRAINT_SLICES[1], STATE_SLICES[1], -divergence)
        _put(coefficient, CONSTRAINT_SLICES[2], STATE_SLICES[2], divergence)
        _put(
            coefficient,
            CONSTRAINT_SLICES[2],
            STATE_SLICES[5],
            sp.Rational(1, 2) * vector_curl,
        )
        _put(coefficient, CONSTRAINT_SLICES[3], STATE_SLICES[3], divergence)
        _put(
            coefficient,
            CONSTRAINT_SLICES[3],
            STATE_SLICES[4],
            -sp.Rational(1, 2) * vector_curl,
        )
        _put(
            coefficient,
            CONSTRAINT_SLICES[4],
            STATE_SLICES[4],
            sp.eye(3)[axis, :],
        )
        _put(
            coefficient,
            CONSTRAINT_SLICES[5],
            STATE_SLICES[5],
            sp.eye(3)[axis, :],
        )
        spatial.append(coefficient)
    zeroth = sp.zeros(14, 26)
    _put(zeroth, CONSTRAINT_SLICES[0], STATE_SLICES[4], sp.eye(3))
    _put(zeroth, CONSTRAINT_SLICES[1], STATE_SLICES[5], sp.eye(3))
    return (sp.zeros(14, 26), *spatial, zeroth)


@dataclass(frozen=True)
class WeylCottonBlockGreenWitness:
    """Exact mapping-cone witness and its analytic input certificates."""

    differential: FormalMatrix
    witness: FormalMatrix
    witness_operator: FormalMatrix
    expected_witness_operator: FormalMatrix
    adjusted: ConstraintAdjustedWeylCottonEvolution
    graph_sdr: CurvatureProlongationGraphSDR
    constraint_table_sha256: str
    source_table_sha256: str

    @staticmethod
    def build() -> "WeylCottonBlockGreenWitness":
        # Abstract block order and ranks:
        # U[26], F[26], C[14], I[14], G[26], G*[26].
        q = _zero(6)
        q[1][0] = OperatorPolynomial.atom("L")
        q[2][0] = OperatorPolynomial.atom("K")
        q[3][1] = OperatorPolynomial.atom("R", -1)
        q[3][2] = OperatorPolynomial.atom("S")
        q[5][4] = OperatorPolynomial.identity()

        w = _zero(6)
        w[0][1] = OperatorPolynomial.identity()
        w[2][3] = OperatorPolynomial.identity()
        w[4][5] = OperatorPolynomial.identity()

        assembled = _add(_multiply(q, w), _multiply(w, q))
        expected = _zero(6)
        expected[0][0] = OperatorPolynomial.atom("L")
        expected[1][1] = OperatorPolynomial.atom("L")
        expected[2][1] = (
            OperatorPolynomial.atom("K")
            + OperatorPolynomial.atom("R", -1)
        )
        expected[2][2] = OperatorPolynomial.atom("S")
        expected[3][3] = OperatorPolynomial.atom("S")
        expected[4][4] = OperatorPolynomial.identity()
        expected[5][5] = OperatorPolynomial.identity()

        adjusted = ConstraintAdjustedWeylCottonEvolution.build()
        graph_sdr = CurvatureProlongationGraphSDR.build()

        # K and R are distinct typed copies but use the same exact natural
        # coefficient table in this cylinder realization.
        constraint_tables = _constraint_definition_tables(adjusted)
        source_tables = (
            sp.zeros(14, 26),
            *adjusted.source_compatibility_spatial_coefficients,
            adjusted.source_compatibility_zeroth_coefficient,
        )

        result = WeylCottonBlockGreenWitness(
            differential=q,
            witness=w,
            witness_operator=assembled,
            expected_witness_operator=expected,
            adjusted=adjusted,
            graph_sdr=graph_sdr,
            constraint_table_sha256=_table_digest(constraint_tables),
            source_table_sha256=_table_digest(source_tables),
        )
        result.verify()
        return result

    def verify(self) -> None:
        self.adjusted.verify()
        self.graph_sdr.verify()
        if not _is_zero(
            _reduce_matrix(_multiply(self.differential, self.differential))
        ):
            raise AssertionError("the compatibility differential is not nilpotent")
        if self.witness_operator != self.expected_witness_operator:
            raise AssertionError("P=QW+WQ block identity failed")
        if not _is_zero(
            _reduce_matrix(
                _add(
                    _multiply(self.differential, self.witness_operator),
                    [
                        [entry.scale(-1) for entry in row]
                        for row in _multiply(
                            self.witness_operator, self.differential
                        )
                    ],
                )
            )
        ):
            raise AssertionError("Q P=P Q failed")
        if (
            self.adjusted.commuting_symbol_defect
            + self.adjusted.sphere_curvature_correction
            != sp.zeros(14, 26)
        ):
            raise AssertionError("the exact curved S K=R L identity failed")
        if self.constraint_table_sha256 != self.source_table_sha256:
            raise AssertionError("canonical K/R coefficient identification drifted")
        for coefficient in self.adjusted.evolution_spatial_coefficients:
            weighted = self.adjusted.evolution_symmetrizer * coefficient
            if weighted != weighted.T:
                raise AssertionError("L is no longer symmetric hyperbolic")
        for coefficient in self.adjusted.constraint_spatial_coefficients:
            weighted = self.adjusted.constraint_symmetrizer * coefficient
            if weighted != weighted.T:
                raise AssertionError("S is no longer symmetric hyperbolic")

    def certificate(self) -> dict[str, object]:
        self.verify()
        return {
            "schema": "pure-weyl-cotton-block-green-witness-v1",
            "scope": "curvature compatibility kernel plus shifted graph pairs",
            "block_order": [
                "U[26]",
                "F[26]",
                "C[14]",
                "I[14]",
                "G[26]",
                "G_star[26]",
            ],
            "compatibility_complex": {
                "first_arrow": "U -> F+C: (L,K)",
                "second_arrow": "F+C -> I: (-R,S)",
                "nilpotency_relation": "S K=R L",
                "curved_unit_S3_correction_included": True,
                "Q_squared": "zero",
            },
            "backward_witness": {
                "F_to_U": "identity",
                "I_to_C": "identity",
                "G_star_to_G": "identity",
                "differential_order": 0,
                "support_local": True,
            },
            "exact_block_identities": {
                "P_equals_QW_plus_WQ": True,
                "Q_P_equals_P_Q": True,
                "degree_U": "L",
                "degree_F_plus_C": "[[L,0],[K-R,S]]",
                "degree_I": "S",
                "graph_degrees": "identity",
            },
            "canonical_source_identification": {
                "K_and_R_coefficient_tables_equal": True,
                "table_sha256": self.constraint_table_sha256,
                "consequence": "the displayed K-R triangular block vanishes",
            },
            "green_hyperbolic_diagonal_blocks": {
                "L_26": {
                    "type": "first-order symmetric hyperbolic",
                    "positive_symmetrizer": True,
                    "causal_characteristics": True,
                },
                "S_14": {
                    "type": "first-order symmetric hyperbolic subsidiary",
                    "positive_symmetrizer": True,
                    "causal_characteristics": True,
                },
                "graph": {
                    "type": "pointwise identity",
                    "retarded_equals_advanced": True,
                },
            },
            "triangular_green_formula": {
                "general_middle_block": (
                    "G_mid=[[G_L,0],[-G_S (K-R) G_L,G_S]]"
                ),
                "canonical_K_equals_R": "G_mid=diag(G_L,G_S)",
                "causal_support_preserved": True,
            },
            "analytic_kernel_consequence": {
                "degreewise_G_plus_minus_exist": True,
                "reason": (
                    "symmetric-hyperbolic L and S on the globally hyperbolic "
                    "cylinder, plus algebraic graph identities"
                ),
                "conditional_chain_commutation": "QG=GQ by two-sided uniqueness",
                "conditional_homotopy": (
                    "Lambda_plus/minus=W G_plus/minus and "
                    "Q Lambda+Lambda Q=1"
                ),
            },
            "graph_input": {
                "shifted_pairs": ["Psi_hat -> Psi_hat_star", "c_hat -> c_hat_star"],
                "pointwise_contractible": True,
                "BV_canonical_graph_shift": True,
                "support_local_SDR": True,
            },
            "missing_for_complete_prolonged_BV_witness": [
                "an all-degree Q_prol embedding this compatibility mapping cone into the retained metric/auxiliary ghost-field-antifield rows",
                "the cotangent/formal-adjoint companion of the L,K,R,S mapping-cone rows with the project BV signs and fibre pairings",
                "explicit triangular couplings to the gauge-wave, trace/Weyl and nonminimal blocks",
                "a proof that the analytic-kernel Green inverses are the diagonal blocks of one two-sided G_plus/minus on every prolonged BV degree",
                "graded adjoint identities needed for Green/current pairing compatibility",
            ],
            "prolonged_BV_operator_identity": False,
            "prolonged_green_witness": False,
            "curvature_causal_green_operators": False,
            "causal_green_homotopy": False,
            "warranted_atomic_flags": [],
            "status_flags_promoted": [],
            "matrix_sha256": {
                "Q_kernel": _digest(self.differential),
                "W_kernel": _digest(self.witness),
                "P_kernel": _digest(self.witness_operator),
            },
            "theorem_boundary": (
                "The exact compatibility-kernel and graph block witness is now "
                "constructed.  It cannot be promoted to the complete prolonged "
                "BV witness until the retained gauge/cotangent rows are assembled "
                "with this mapping cone and checked on every degree."
            ),
            "fail_closed": True,
        }
