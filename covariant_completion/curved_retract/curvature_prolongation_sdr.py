"""Support-local BV cotangent graph extension for Weyl and Cotton fields.

This module proves the algebraic/local part of curvature prolongation.  Start
with the complete four-row auxiliary BV complex

``ghost -> field -> equation/antifield -> identity-antifield``

and adjoin independent graph fields ``Psi`` and ``c`` together with their
defining equation/antifield rows.  In shifted variables

``Psi_hat = Psi-C1 h`` and ``c_hat = c-div(Psi)``

the two new pairs are the pointwise contractible arrows

``Psi_hat -> Psi_hat^*`` and ``c_hat -> c_hat^*``.

The change of variables is lifted once, as a BV cotangent transformation.
Consequently the base equation row receives the formal-adjoint correction
forced by ``C1`` and the Weyl equation row receives the correction forced by
``div``.  The ghost and identity-antifield rows are retained exactly.  No new
identity-antifield is added: the two algebraic graph equations have no new
Noether identity, and adding a zero identity row would create cohomology.

Everything is checked in a tiny exact noncommutative operator algebra.  The
result is deliberately narrower than the full prolonged BV theorem: it does
not insert the derived Bianchi/Bach evolution rows and does not construct a
Green witness.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
import hashlib

from covariant_completion.minimal_witness.formal_operators import (
    OperatorPolynomial,
)


Matrix = list[list[OperatorPolynomial]]


def _zero(rows: int, columns: int) -> Matrix:
    return [
        [OperatorPolynomial.zero() for _ in range(columns)]
        for _ in range(rows)
    ]


def _identity(size: int) -> Matrix:
    output = _zero(size, size)
    for index in range(size):
        output[index][index] = OperatorPolynomial.identity()
    return output


def _add(left: Matrix, right: Matrix) -> Matrix:
    return [
        [left[row][column] + right[row][column] for column in range(len(left[0]))]
        for row in range(len(left))
    ]


def _scale(matrix: Matrix, coefficient: int | Fraction) -> Matrix:
    return [[entry.scale(coefficient) for entry in row] for row in matrix]


def _multiply(left: Matrix, right: Matrix) -> Matrix:
    if len(left[0]) != len(right):
        raise ValueError("incompatible formal block matrices")
    output = _zero(len(left), len(right[0]))
    for row in range(len(left)):
        for column in range(len(right[0])):
            value = OperatorPolynomial.zero()
            for middle in range(len(right)):
                value = value + left[row][middle] * right[middle][column]
            output[row][column] = value
    return output


def _formal_adjoint(entry: OperatorPolynomial) -> OperatorPolynomial:
    adjoints = {
        "K": "Ksharp",
        "Ksharp": "K",
        "E": "E",
        "C": "Csharp",
        "Csharp": "C",
        "T": "Tsharp",
        "Tsharp": "T",
        "D": "Dsharp",
        "Dsharp": "D",
    }
    return OperatorPolynomial._from_dict(
        {
            tuple(adjoints[name] for name in reversed(word)): coefficient
            for word, coefficient in entry.terms
        }
    )


def _matrix_adjoint(matrix: Matrix) -> Matrix:
    return [
        [_formal_adjoint(matrix[column][row]) for column in range(len(matrix))]
        for row in range(len(matrix[0]))
    ]


def _reduce_complex_relations(entry: OperatorPolynomial) -> OperatorPolynomial:
    """Reduce only the two nilpotency relations of the retained base Q."""

    relations = {("E", "K"), ("C", "E")}
    values: dict[tuple[str, ...], Fraction] = {}
    for word, coefficient in entry.terms:
        if any(
            word[index : index + 2] in relations
            for index in range(max(0, len(word) - 1))
        ):
            continue
        values[word] = values.get(word, Fraction()) + coefficient
    return OperatorPolynomial._from_dict(values)


def _reduce_matrix(matrix: Matrix) -> Matrix:
    return [[_reduce_complex_relations(entry) for entry in row] for row in matrix]


def _is_zero(matrix: Matrix) -> bool:
    zero = OperatorPolynomial.zero()
    return all(entry == zero for row in matrix for entry in row)


def _digest(matrix: Matrix) -> str:
    payload = "\n".join(
        ",".join(entry.display() for entry in row) for row in matrix
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _operator_order(entry: OperatorPolynomial) -> int:
    orders = {"T": 2, "Tsharp": 2, "D": 1, "Dsharp": 1}
    return max(
        (sum(orders.get(atom, 0) for atom in word) for word, _ in entry.terms),
        default=0,
    )


def _matrix_order(matrix: Matrix) -> int:
    return max((_operator_order(entry) for row in matrix for entry in row), default=0)


@dataclass(frozen=True)
class CurvatureProlongationGraphSDR:
    """Exact block SDR for the BV-canonical Weyl/Cotton graph extension."""

    split_differential: Matrix
    new_to_old: Matrix
    old_to_new: Matrix
    prolonged_differential: Matrix
    base_differential: Matrix
    inclusion: Matrix
    projection: Matrix
    homotopy: Matrix
    bv_pairing: Matrix

    @staticmethod
    def build() -> "CurvatureProlongationGraphSDR":
        # Block order:
        #   0 ghost, 1 h, 2 Psi_hat, 3 c_hat,
        #   4 h^*, 5 Psi_hat^*, 6 c_hat^*, 7 identity-antifield.
        split_q = _zero(8, 8)
        split_q[1][0] = OperatorPolynomial.atom("K")
        split_q[4][1] = OperatorPolynomial.atom("E")
        split_q[7][4] = OperatorPolynomial.atom("C")
        split_q[5][2] = OperatorPolynomial.identity()
        split_q[6][3] = OperatorPolynomial.identity()

        # New/shifted -> old/unshifted field graph:
        #   Psi=Psi_hat+T h,
        #   c=c_hat+D Psi=c_hat+D Psi_hat+D T h.
        # Its cotangent lift is (L^sharp)^(-1), hence
        #   h^*_old=h^*_new-T^sharp Psi^*_new,
        #   Psi^*_old=Psi^*_new-D^sharp c^*_new.
        u = _identity(8)
        u[2][1] = OperatorPolynomial.atom("T")
        u[3][1] = OperatorPolynomial.atom("D") * OperatorPolynomial.atom("T")
        u[3][2] = OperatorPolynomial.atom("D")
        u[4][5] = OperatorPolynomial.atom("Tsharp", -1)
        u[5][6] = OperatorPolynomial.atom("Dsharp", -1)

        u_inverse = _identity(8)
        u_inverse[2][1] = OperatorPolynomial.atom("T", -1)
        u_inverse[3][2] = OperatorPolynomial.atom("D", -1)
        u_inverse[4][5] = OperatorPolynomial.atom("Tsharp")
        u_inverse[4][6] = (
            OperatorPolynomial.atom("Tsharp")
            * OperatorPolynomial.atom("Dsharp")
        )
        u_inverse[5][6] = OperatorPolynomial.atom("Dsharp")

        prolonged_q = _multiply(_multiply(u, split_q), u_inverse)

        # Retained four-row base complex in order ghost,h,h^*,identity^*.
        base_q = _zero(4, 4)
        base_q[1][0] = OperatorPolynomial.atom("K")
        base_q[2][1] = OperatorPolynomial.atom("E")
        base_q[3][2] = OperatorPolynomial.atom("C")
        base_indices = (0, 1, 4, 7)
        i0 = _zero(8, 4)
        p0 = _zero(4, 8)
        for base_index, prolonged_index in enumerate(base_indices):
            i0[prolonged_index][base_index] = OperatorPolynomial.identity()
            p0[base_index][prolonged_index] = OperatorPolynomial.identity()
        inclusion = _multiply(u, i0)
        projection = _multiply(p0, u_inverse)

        # q_aux k+k q_aux=-1 on each self-dual graph pair, matching the
        # repository convention ip-1=QH+HQ.
        h0 = _zero(8, 8)
        h0[2][5] = OperatorPolynomial.identity(-1)
        h0[3][6] = OperatorPolynomial.identity(-1)
        homotopy = _multiply(_multiply(u, h0), u_inverse)

        pairing = _zero(8, 8)
        for left, right in ((0, 7), (1, 4), (2, 5), (3, 6)):
            pairing[left][right] = OperatorPolynomial.identity()
            pairing[right][left] = OperatorPolynomial.identity()

        result = CurvatureProlongationGraphSDR(
            split_differential=split_q,
            new_to_old=u,
            old_to_new=u_inverse,
            prolonged_differential=prolonged_q,
            base_differential=base_q,
            inclusion=inclusion,
            projection=projection,
            homotopy=homotopy,
            bv_pairing=pairing,
        )
        result.verify()
        return result

    def verify(self) -> None:
        identity8 = _identity(8)
        identity4 = _identity(4)
        if self.split_differential[5][2] != OperatorPolynomial.identity():
            raise AssertionError("the shifted Weyl graph pair is not a unit arrow")
        if self.split_differential[6][3] != OperatorPolynomial.identity():
            raise AssertionError("the shifted Cotton graph pair is not a unit arrow")
        if _multiply(self.new_to_old, self.old_to_new) != identity8:
            raise AssertionError("the triangular graph map has no exact right inverse")
        if _multiply(self.old_to_new, self.new_to_old) != identity8:
            raise AssertionError("the triangular graph map has no exact left inverse")

        canonical_defect = _add(
            _multiply(
                _multiply(_matrix_adjoint(self.new_to_old), self.bv_pairing),
                self.new_to_old,
            ),
            _scale(self.bv_pairing, -1),
        )
        if not _is_zero(canonical_defect):
            raise AssertionError("the Weyl/Cotton graph shift is not BV canonical")

        if not _is_zero(
            _reduce_matrix(_multiply(self.split_differential, self.split_differential))
        ):
            raise AssertionError("the split prolonged differential is not nilpotent")
        if not _is_zero(
            _reduce_matrix(
                _multiply(self.prolonged_differential, self.prolonged_differential)
            )
        ):
            raise AssertionError("the unshifted prolonged differential is not nilpotent")
        if _multiply(self.projection, self.inclusion) != identity4:
            raise AssertionError("P I is not the retained identity")
        if not _is_zero(
            _reduce_matrix(
                _add(
                    _multiply(self.prolonged_differential, self.inclusion),
                    _scale(_multiply(self.inclusion, self.base_differential), -1),
                )
            )
        ):
            raise AssertionError("I is not a chain map")
        if not _is_zero(
            _reduce_matrix(
                _add(
                    _multiply(self.projection, self.prolonged_differential),
                    _scale(_multiply(self.base_differential, self.projection), -1),
                )
            )
        ):
            raise AssertionError("P is not a chain map")

        retract_defect = _add(
            _add(
                _multiply(self.inclusion, self.projection),
                _scale(identity8, -1),
            ),
            _scale(
                _add(
                    _multiply(self.prolonged_differential, self.homotopy),
                    _multiply(self.homotopy, self.prolonged_differential),
                ),
                -1,
            ),
        )
        if not _is_zero(_reduce_matrix(retract_defect)):
            raise AssertionError("I P-1=QH+HQ failed")

    def certificate(self, *, reverify: bool = True) -> dict[str, object]:
        if reverify:
            self.verify()
        return {
            "schema": "pure-weyl-support-local-curvature-graph-SDR-v1",
            "base_complex": {
                "rows": [
                    "gauge ghosts",
                    "auxiliary fields including h",
                    "equations/field antifields",
                    "Noether-identity/ghost-antifields",
                ],
                "minimal_dimension": 66,
                "retained_without_omission": True,
                "trace_Weyl_and_nonminimal_direct_summands": "identity",
            },
            "adjoined_rows": [
                {
                    "field": "Psi",
                    "dimension": 10,
                    "equation_antifield": "Psi_star",
                    "equation_dimension": 10,
                    "shift": "Psi_hat=Psi-C1 h",
                },
                {
                    "field": "c=div Psi",
                    "dimension": 16,
                    "equation_antifield": "c_star",
                    "equation_dimension": 16,
                    "shift": "c_hat=c-div Psi",
                },
            ],
            "minimal_prolonged_dimension": 118,
            "new_identity_antifields": 0,
            "identity_antifield_reason": (
                "the graph equations are algebraically independent and have no "
                "new Noether identity; the original identity-antifields remain present"
            ),
            "type_II_generator": (
                "F_graph=<h_new^*,h>+<Psi_new^*,Psi-C1 h>+"
                "<c_new^*,c-div Psi> plus unchanged base rows"
            ),
            "cotangent_lift": {
                "h_star_old": "h_star_new-C1^sharp Psi_star_new",
                "Psi_star_old": "Psi_star_new-div^sharp c_star_new",
                "c_star_old": "c_star_new",
                "formal_BV_pairing_defect": 0,
            },
            "SDR_maps": {
                "inclusion_fields": "h |-> (h,Psi=C1 h,c=div C1 h)",
                "inclusion_graph_equation_antifields": "zero",
                "projection_fields": "(h,Psi,c) |-> h",
                "projection_base_equation_antifield": (
                    "h_star+C1^sharp Psi_star+C1^sharp div^sharp c_star"
                ),
                "homotopy": (
                    "canonical conjugate of Psi_star |-> -Psi_hat and "
                    "c_star |-> -c_hat"
                ),
            },
            "exact_identities": {
                "U_inverse_U": "identity",
                "U_U_inverse": "identity",
                "Q_prol_squared": "zero modulo Q_aux_squared=0",
                "P_I": "identity",
                "Q_prol_I_minus_I_Q_aux": "zero",
                "P_Q_prol_minus_Q_aux_P": "zero",
                "I_P_minus_identity": "Q_prol H+H Q_prol",
            },
            "support": {
                "operators": {
                    "C1": 2,
                    "div": 1,
                    "div_C1": 3,
                    "C1_sharp": 2,
                    "div_sharp": 1,
                    "homotopy_max_order": _matrix_order(self.homotopy),
                },
                "finite_order_only": True,
                "pointwise_inverses_only": True,
                "inverse_Laplacian": False,
                "inverse_curl": False,
                "spectral_or_helicity_projector": False,
                "Green_operator": False,
                "compact": True,
                "spacelike_compact": True,
                "smooth_global": True,
            },
            "matrix_sha256": {
                "split_Q": _digest(self.split_differential),
                "new_to_old": _digest(self.new_to_old),
                "old_to_new": _digest(self.old_to_new),
                "unshifted_Q": _digest(self.prolonged_differential),
                "inclusion": _digest(self.inclusion),
                "projection": _digest(self.projection),
                "homotopy": _digest(self.homotopy),
            },
            "support_local_curvature_graph_retract": True,
            "support_local_prolongation_retract": False,
            "prolonged_BV_operator_identity": False,
            "theorem_boundary": (
                "this is the exact all-row graph/generalized-auxiliary SDR for "
                "Psi=C1 h and c=div Psi; promotion of the complete prolongation "
                "still requires inserting and checking the derived Bianchi/Bach, "
                "constraint, and identity rows of Q_prol"
            ),
            "fail_closed": True,
        }
