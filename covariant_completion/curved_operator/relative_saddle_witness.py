"""Exact incidence diagnostic for a two-way auxiliary--curvature witness.

For the split sixteen-block differential, there are eighteen degree-minus-one
relative entries, paired into nine odd-cotangent adjoint pairs.  No single
pair produces reciprocal same-degree auxiliary--curvature couplings.  The
smallest pair combination which couples the physical field row to both
curvature state copies is the pair labelled ``R`` and ``S`` below:

``W(Y_U)=R M``, ``W(E)=R^sharp Y_U^sharp``,
``W(X_U^sharp)=S M``, ``W(E)=S^sharp X_U``.

Its degree-zero core is the exact saddle

``[[A,R,S],[S^sharp E,L,0],[R^sharp E,0,L^sharp]]``

with ``A=E+KC``.  This module proves that block formula and the exact Schur
factorization.  It also records why this is not yet a Green theorem: the
Schur complement contains the nonlocal curvature Green operators, while the
unreduced saddle still has second-order ``E`` entries and therefore is not
the certified first-order symmetric-hyperbolic system.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
import hashlib

from covariant_completion.curved_retract.curvature_mapping_cylinder_kernel import (
    BLOCK_DEGREES,
    BLOCK_NAMES,
    CurvatureMappingCylinderKernel,
    Matrix,
    SIZE,
    _add,
    _degree_sign,
    _multiply,
    _scale,
    _zero,
)
from covariant_completion.minimal_witness.formal_operators import (
    OperatorPolynomial,
)

from .curvature_mapping_cylinder_witness import _split_witness


ADJOINT_RELATIVE_PAIRS = (
    ((0, 4), (12, 3)),
    ((0, 11), (5, 3)),
    ((0, 15), (7, 3)),
    ((1, 5), (11, 2)),
    ((1, 7), (15, 2)),
    ((1, 12), (4, 2)),
    ((2, 6), (10, 1)),
    ((2, 8), (14, 1)),
    ((3, 9), (13, 0)),
)

PRIMARY_RELATIVE_ENTRIES = tuple(pair[0] for pair in ADJOINT_RELATIVE_PAIRS)


def _digest(matrix: Matrix) -> str:
    payload = "\n".join(
        ",".join(entry.display() for entry in row) for row in matrix
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _pairing_dual_and_epsilon(
    pairing: Matrix,
) -> tuple[dict[int, int], dict[int, int]]:
    dual: dict[int, int] = {}
    epsilon: dict[int, int] = {}
    for row in range(SIZE):
        nonzero = [
            (column, entry)
            for column, entry in enumerate(pairing[row])
            if entry != OperatorPolynomial.zero()
        ]
        if len(nonzero) != 1:
            raise AssertionError("odd incidence pairing is not a perfect matching")
        column, entry = nonzero[0]
        if len(entry.terms) != 1 or entry.terms[0][0]:
            raise AssertionError("odd incidence pairing entry is not scalar")
        dual[row] = column
        epsilon[row] = int(entry.terms[0][1])
    return dual, epsilon


def _derived_partner(
    pairing: Matrix, row: int, column: int
) -> tuple[int, int, int]:
    """Derive the cyclic partner from W^sharp Omega-D Omega W=0."""

    dual, epsilon = _pairing_dual_and_epsilon(pairing)
    degree_sign = -1 if BLOCK_DEGREES[column] % 2 else 1
    numerator = epsilon[row]
    denominator = degree_sign * epsilon[column]
    if numerator % denominator:
        raise AssertionError("relative cyclic sign is not integral")
    return dual[column], dual[row], numerator // denominator


def _toggle_sharp(name: str) -> str:
    return name[:-5] if name.endswith("sharp") else name + "sharp"


def _relative_formal_adjoint(
    entry: OperatorPolynomial,
) -> OperatorPolynomial:
    return OperatorPolynomial._from_dict(
        {
            tuple(_toggle_sharp(name) for name in reversed(word)): coefficient
            for word, coefficient in entry.terms
        }
    )


def _relative_matrix_adjoint(matrix: Matrix) -> Matrix:
    return [
        [
            _relative_formal_adjoint(matrix[column][row])
            for column in range(SIZE)
        ]
        for row in range(SIZE)
    ]


def _cyclic_defect(matrix: Matrix, pairing: Matrix) -> Matrix:
    return _add(
        _multiply(_relative_matrix_adjoint(matrix), pairing),
        _scale(
            _multiply(_multiply(_degree_sign(), pairing), matrix),
            -1,
        ),
    )


def _relative_pair_matrix(
    pair_index: int, pairing: Matrix
) -> tuple[Matrix, int]:
    result = _zero()
    first = PRIMARY_RELATIVE_ENTRIES[pair_index]
    partner_row, partner_column, sign = _derived_partner(
        pairing, first[0], first[1]
    )
    second = (partner_row, partner_column)
    if second != ADJOINT_RELATIVE_PAIRS[pair_index][1]:
        raise AssertionError("derived relative partner incidence drifted")
    result[first[0]][first[1]] = OperatorPolynomial.atom(f"R{pair_index}")
    result[second[0]][second[1]] = OperatorPolynomial.atom(
        f"R{pair_index}sharp", sign
    )
    return result, sign


def _cross_edges(matrix: Matrix) -> set[tuple[int, int]]:
    return {
        (column, row)
        for row in range(SIZE)
        for column in range(SIZE)
        if matrix[row][column] != OperatorPolynomial.zero()
        and ((row < 4) != (column < 4))
    }


def _small_identity() -> Matrix:
    result = [
        [OperatorPolynomial.zero() for _ in range(3)] for _ in range(3)
    ]
    for index in range(3):
        result[index][index] = OperatorPolynomial.identity()
    return result


def _small_multiply(left: Matrix, right: Matrix) -> Matrix:
    result = [
        [OperatorPolynomial.zero() for _ in range(3)] for _ in range(3)
    ]
    for row in range(3):
        for column in range(3):
            for middle in range(3):
                result[row][column] = (
                    result[row][column]
                    + left[row][middle] * right[middle][column]
                )
    return result


def _reduce_inverse(entry: OperatorPolynomial) -> OperatorPolynomial:
    inverse_pairs = {
        ("D1", "G1"),
        ("G1", "D1"),
        ("D2", "G2"),
        ("G2", "D2"),
        ("Z", "H"),
        ("H", "Z"),
    }
    values: dict[tuple[str, ...], Fraction] = {}
    for word, coefficient in entry.terms:
        reduced = word
        changed = True
        while changed:
            changed = False
            for index in range(max(0, len(reduced) - 1)):
                if reduced[index : index + 2] in inverse_pairs:
                    reduced = reduced[:index] + reduced[index + 2 :]
                    changed = True
                    break
        values[reduced] = values.get(reduced, Fraction()) + coefficient
    return OperatorPolynomial._from_dict(values)


def _small_identity_mod_inverse(matrix: Matrix) -> bool:
    identity = _small_identity()
    return all(
        _reduce_inverse(
            matrix[row][column] + identity[row][column].scale(-1)
        )
        == OperatorPolynomial.zero()
        for row in range(3)
        for column in range(3)
    )


def _verify_schur_factors() -> None:
    """Check both triangular factors and the diagonal inverse exactly."""

    atom = OperatorPolynomial.atom
    one = OperatorPolynomial.identity()
    zero = OperatorPolynomial.zero()
    left = [
        [one, atom("B1") * atom("G1"), atom("B2") * atom("G2")],
        [zero, one, zero],
        [zero, zero, one],
    ]
    left_inverse = [
        [one, (atom("B1") * atom("G1")).scale(-1), (atom("B2") * atom("G2")).scale(-1)],
        [zero, one, zero],
        [zero, zero, one],
    ]
    right = [
        [one, zero, zero],
        [atom("G1") * atom("C1"), one, zero],
        [atom("G2") * atom("C2"), zero, one],
    ]
    right_inverse = [
        [one, zero, zero],
        [(atom("G1") * atom("C1")).scale(-1), one, zero],
        [(atom("G2") * atom("C2")).scale(-1), zero, one],
    ]
    diagonal = [
        [atom("Z"), zero, zero],
        [zero, atom("D1"), zero],
        [zero, zero, atom("D2")],
    ]
    diagonal_inverse = [
        [atom("H"), zero, zero],
        [zero, atom("G1"), zero],
        [zero, zero, atom("G2")],
    ]
    for forward, inverse in (
        (left, left_inverse),
        (right, right_inverse),
        (diagonal, diagonal_inverse),
    ):
        if not _small_identity_mod_inverse(_small_multiply(forward, inverse)):
            raise AssertionError("Schur factor has no right inverse")
        if not _small_identity_mod_inverse(_small_multiply(inverse, forward)):
            raise AssertionError("Schur factor has no left inverse")


@dataclass(frozen=True)
class RelativeSaddleWitnessDiagnostic:
    """Smallest reciprocal relative-witness incidence and its Schur boundary."""

    kernel: CurvatureMappingCylinderKernel
    relative_witness: Matrix
    total_witness: Matrix
    total_operator: Matrix
    single_pair_reciprocal_counts: tuple[int, ...]
    all_pair_reciprocal_node_pairs: tuple[tuple[int, int], ...]
    relative_partner_signs: tuple[int, ...]

    @staticmethod
    def build() -> "RelativeSaddleWitnessDiagnostic":
        kernel = CurvatureMappingCylinderKernel.build()
        q = kernel.split_differential
        counts: list[int] = []
        partner_signs: list[int] = []
        all_edges: set[tuple[int, int]] = set()
        for pair_index in range(len(ADJOINT_RELATIVE_PAIRS)):
            w_pair, sign = _relative_pair_matrix(pair_index, kernel.pairing)
            partner_signs.append(sign)
            if any(
                entry != OperatorPolynomial.zero()
                for row in _cyclic_defect(w_pair, kernel.pairing)
                for entry in row
            ):
                raise AssertionError("derived relative pair is not BV cyclic")
            p_pair = _add(_multiply(q, w_pair), _multiply(w_pair, q))
            edges = _cross_edges(p_pair)
            all_edges.update(edges)
            counts.append(sum((target, source) in edges for source, target in edges))

        reciprocal = tuple(
            sorted(
                {
                    tuple(sorted((source, target)))
                    for source, target in all_edges
                    if (target, source) in all_edges
                }
            )
        )

        # Pair 4 is (Y_U -> M, E -> Y_U#); pair 5 is
        # (X_U# -> M, E -> X_U).  Rename their entries R and S.
        relative = _zero()
        for pair_index, name in ((4, "R"), (5, "S")):
            primary_row, primary_column = PRIMARY_RELATIVE_ENTRIES[pair_index]
            partner_row, partner_column, sign = _derived_partner(
                kernel.pairing, primary_row, primary_column
            )
            relative[primary_row][primary_column] = OperatorPolynomial.atom(name)
            relative[partner_row][partner_column] = OperatorPolynomial.atom(
                name + "sharp", sign
            )
        total_witness = _add(_split_witness(), relative)
        total_operator = _add(
            _multiply(q, total_witness), _multiply(total_witness, q)
        )
        result = RelativeSaddleWitnessDiagnostic(
            kernel=kernel,
            relative_witness=relative,
            total_witness=total_witness,
            total_operator=total_operator,
            single_pair_reciprocal_counts=tuple(counts),
            all_pair_reciprocal_node_pairs=reciprocal,
            relative_partner_signs=tuple(partner_signs),
        )
        result.verify()
        return result

    def verify(self) -> None:
        self.kernel.verify()
        if len(ADJOINT_RELATIVE_PAIRS) != 9:
            raise AssertionError("relative witness pair ledger drifted")
        if any(self.single_pair_reciprocal_counts):
            raise AssertionError("a single relative pair unexpectedly made a saddle")
        if self.relative_partner_signs != (1,) * 9:
            raise AssertionError("oriented relative partner signs drifted")
        if len(self.all_pair_reciprocal_node_pairs) != 10:
            raise AssertionError("reciprocal node-pair classification drifted")
        for row in range(SIZE):
            for column in range(SIZE):
                if self.relative_witness[row][column] != OperatorPolynomial.zero():
                    if BLOCK_DEGREES[row] != BLOCK_DEGREES[column] - 1:
                        raise AssertionError("relative W does not have degree minus one")

        atom = OperatorPolynomial.atom
        nodes = (1, 4, 15)  # M, X_U, Y_U#.
        expected = (
            (
                atom("Eaux") + atom("K") * atom("C"),
                atom("R"),
                atom("S"),
            ),
            (
                atom("Ssharp") * atom("Eaux"),
                atom("pF") * atom("Ecurv"),
                OperatorPolynomial.zero(),
            ),
            (
                atom("Rsharp") * atom("Eaux"),
                OperatorPolynomial.zero(),
                atom("EcurvSharp") * atom("pFsharp"),
            ),
        )
        actual = tuple(
            tuple(self.total_operator[row][column] for column in nodes)
            for row in nodes
        )
        if actual != expected:
            raise AssertionError("minimal degree-zero saddle formula drifted")
        if any(
            entry != OperatorPolynomial.zero()
            for row in _cyclic_defect(
                self.relative_witness, self.kernel.pairing
            )
            for entry in row
        ):
            raise AssertionError("Delta W is not cyclic for the odd BV pairing")
        _verify_schur_factors()

    def certificate(self) -> dict[str, object]:
        self.verify()
        return {
            "schema": "pure-weyl-relative-saddle-witness-diagnostic-v1",
            "relative_degree_minus_one_classification": {
                "allowed_directed_entries": 18,
                "odd_cotangent_adjoint_pairs": 9,
                "partner_derivation": (
                    "for W[row,column]=R, cyclicity gives partner "
                    "W[dual(column),dual(row)]="
                    "epsilon(row)/((-1)^degree(column) epsilon(column)) Rsharp"
                ),
                "pairing_source": "oriented odd incidence matrix Omega from the corrected 16-block kernel",
                "derived_partner_signs": list(self.relative_partner_signs),
                "all_partner_signs_positive_in_current_orientation": True,
                "each_pair_BV_cyclicity_defect": 0,
                "single_pair_reciprocal_counts": list(
                    self.single_pair_reciprocal_counts
                ),
                "no_single_pair_makes_two_way_saddle": True,
                "reciprocal_node_pairs_available_from_pair_combinations": [
                    [BLOCK_NAMES[left], BLOCK_NAMES[right]]
                    for left, right in self.all_pair_reciprocal_node_pairs
                ],
            },
            "smallest_physical_saddle_candidate": {
                "relative_pairs": [4, 5],
                "entries": [
                    "W: Y_U -> M_aux is R",
                    "W: Ebar_aux -> Y_U_sharp is Rsharp",
                    "W: X_U_sharp -> M_aux is S",
                    "W: Ebar_aux -> X_U is Ssharp",
                ],
                "degree_zero_order": ["M_aux", "X_U", "Y_U_sharp"],
                "degree_zero_matrix": [
                    ["Eaux+K C", "R", "S"],
                    ["Ssharp Eaux", "L_26", "0"],
                    ["Rsharp Eaux", "0", "L_26sharp"],
                ],
                "two_way_aux_curvature_coupling": True,
                "degree_one_cotangent_partner_forced": True,
                "DeltaW_BV_cyclicity_identity": (
                    "DeltaW^(T,formal) Omega-D Omega DeltaW=0"
                ),
                "DeltaW_BV_cyclicity_defect": 0,
                "matrix_sha256": {
                    "W_relative": _digest(self.relative_witness),
                    "W_total_split": _digest(self.total_witness),
                    "P_total_split": _digest(self.total_operator),
                },
            },
            "exact_schur_factorization": {
                "D": "diag(L_26,L_26sharp)",
                "B": "[R,S]",
                "C": "[Ssharp Eaux,Rsharp Eaux]^T",
                "A": "Eaux+K C",
                "Z": "A-B diag(G_L,G_Lsharp) C",
                "factorization": (
                    "P=[[1,B G_D],[0,1]] diag(Z,D) "
                    "[[1,0],[G_D C,1]]"
                ),
                "inverse_if_Z_has_two_sided_causal_inverse": (
                    "right-to-left inverse of the displayed three factors"
                ),
                "finite_block_algebra": True,
            },
            "analytic_boundary": {
                "Schur_Z_is_local_differential_operator": False,
                "reason": "Z contains the curvature Green operators G_L",
                "therefore_Schur_condition_is_not_a_local_Green_witness_proof": True,
                "unreduced_saddle_maximum_order": 2,
                "first_order_symmetric_hyperbolic_certificate_applies": False,
                "missing_for_symmetric_hyperbolicity": [
                    "coefficient tables and fibre maps R,S",
                    "a local first-order reduction cancelling or prolonging every Eaux occurrence",
                    "a positive temporal symmetrizer for the complete coupled principal matrix",
                ],
            },
            "constructive_conclusion": (
                "pairs 4+5 are the smallest exact two-way field/curvature saddle; "
                "they identify the coefficient ansatz to investigate, but neither "
                "the nonlocal Schur condition nor the current order-two saddle "
                "closes Green hyperbolicity"
            ),
            "prolonged_green_witness": False,
            "curvature_causal_green_operators": False,
            "causal_green_homotopy": False,
            "warranted_atomic_flags": [],
            "status_flags_promoted": [],
            "fail_closed": True,
        }
