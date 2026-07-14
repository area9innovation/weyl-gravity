"""Degree/sign-resolved cotangent mapping cylinder for curvature attachment.

The auxiliary-to-curvature chain map has primal components

``T : M_aux -> U``, ``A : E_aux -> Eq`` and ``B : I_aux -> Id``.

Here the auxiliary equation row is the *paired* row
``Ebar=J_aux^{-1} E_raw``.  Thus a coefficient map first derived on raw
Euler--Lagrange covectors must be converted by ``A=A_raw J_aux``.

Adjoining the autonomous curvature complex directly would duplicate its
physical cohomology.  The local attachment is instead a mapping cylinder:
add the contractible cone of the curvature complex and its cotangent dual.
In split variables the cone differential is manifestly contractible.  The
unshifted graph coordinates are obtained by the three primal shifts

``X_U += T M``, ``X_Eq += A E`` and ``X_Id += B I``

together with the forced cotangent shifts

``E += -Tsharp X_Usharp``, ``M += -Asharp X_Eqsharp`` and
``G += -Bsharp X_Idsharp``.

Each pair is one elementary type-II canonical shear.  Their ordered product
is checked exactly, including inverse, pairing, chain maps and the SDR sign
``ip-1=QH+HQ``.  Coefficient existence is an input from the separate T/A/B
certificates; no project status is promoted here.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
import hashlib

import sympy as sp

from covariant_completion.curved_operator.conventions import _ordinary_system
from covariant_completion.minimal_witness.formal_operators import OperatorPolynomial


Matrix = list[list[OperatorPolynomial]]
SIZE = 16
BLOCK_DEGREES = (-1, 0, 1, 2, 0, 1, 2, 1, 2, 3, -1, 0, 1, -2, -1, 0)
BLOCK_NAMES = (
    "G_aux",
    "M_aux",
    "Ebar_aux",
    "I_aux",
    "X_U",
    "X_Eq",
    "X_Id",
    "Y_U",
    "Y_Eq",
    "Y_Id",
    "X_Id_sharp",
    "X_Eq_sharp",
    "X_U_sharp",
    "Y_Id_sharp",
    "Y_Eq_sharp",
    "Y_U_sharp",
)
# Oriented odd incidence form.  For a displayed primal coordinate z and its
# cotangent z#, EPSILON[z]=Omega(z,z#), while Omega(z#,z)=-EPSILON[z].
# The auxiliary four-row block is already self-cotangent: Omega(G,I)=+1 and
# Omega(M,Ebar)=+1.  The X orientations match their auxiliary graph sources,
# so all three degree-zero type-II shears use the same minus-adjoint sign.
PAIRING_EPSILON = {
    0: 1,
    1: 1,
    2: -1,
    3: -1,
    4: 1,
    5: -1,
    6: -1,
    7: -1,
    8: -1,
    9: 1,
}


def _zero() -> Matrix:
    return [[OperatorPolynomial.zero() for _ in range(SIZE)] for _ in range(SIZE)]


def _identity() -> Matrix:
    result = _zero()
    for index in range(SIZE):
        result[index][index] = OperatorPolynomial.identity()
    return result


def _add(left: Matrix, right: Matrix) -> Matrix:
    return [
        [left[row][column] + right[row][column] for column in range(SIZE)]
        for row in range(SIZE)
    ]


def _scale(matrix: Matrix, coefficient: int | Fraction) -> Matrix:
    return [[entry.scale(coefficient) for entry in row] for row in matrix]


def _multiply(left: Matrix, right: Matrix) -> Matrix:
    result = _zero()
    for row in range(SIZE):
        for column in range(SIZE):
            entry = OperatorPolynomial.zero()
            for middle in range(SIZE):
                entry = entry + left[row][middle] * right[middle][column]
            result[row][column] = entry
    return result


def _formal_adjoint(entry: OperatorPolynomial) -> OperatorPolynomial:
    involution = {
        "K": "C",
        "C": "K",
        "Eaux": "Eaux",
        "Ecurv": "EcurvSharp",
        "EcurvSharp": "Ecurv",
        "Ncurv": "NcurvSharp",
        "NcurvSharp": "Ncurv",
        "T": "Tsharp",
        "Tsharp": "T",
        "A": "Asharp",
        "Asharp": "A",
        "B": "Bsharp",
        "Bsharp": "B",
    }
    return OperatorPolynomial._from_dict(
        {
            tuple(involution[name] for name in reversed(word)): coefficient
            for word, coefficient in entry.terms
        }
    )


def _matrix_adjoint(matrix: Matrix) -> Matrix:
    return [
        [_formal_adjoint(matrix[column][row]) for column in range(SIZE)]
        for row in range(SIZE)
    ]


def _degree_sign() -> Matrix:
    """Diagonal Koszul sign ``D_jj=(-1)^degree(j)``."""

    result = _zero()
    for index, degree in enumerate(BLOCK_DEGREES):
        result[index][index] = OperatorPolynomial.identity(
            -1 if degree % 2 else 1
        )
    return result


def _is_zero(matrix: Matrix) -> bool:
    zero = OperatorPolynomial.zero()
    return all(entry == zero for row in matrix for entry in row)


def _reduce_complex_relations(entry: OperatorPolynomial) -> OperatorPolynomial:
    relations = {
        ("Eaux", "K"),
        ("C", "Eaux"),
        ("Ncurv", "Ecurv"),
        ("EcurvSharp", "NcurvSharp"),
    }
    values: dict[tuple[str, ...], Fraction] = {}
    for word, coefficient in entry.terms:
        if any(
            word[index : index + 2] in relations
            for index in range(max(0, len(word) - 1))
        ):
            continue
        values[word] = values.get(word, Fraction()) + coefficient
    return OperatorPolynomial._from_dict(values)


def _reduce_chain_relations(entry: OperatorPolynomial) -> OperatorPolynomial:
    """Reduce the three primal chain squares and their formal adjoints."""

    zero_relations = {("T", "K"), ("C", "Tsharp")}
    rewrites = {
        ("Ecurv", "T"): ("A", "Eaux"),
        ("Ncurv", "A"): ("B", "C"),
        ("Tsharp", "EcurvSharp"): ("Eaux", "Asharp"),
        ("Asharp", "NcurvSharp"): ("K", "Bsharp"),
    }
    pending = list(entry.terms)
    values: dict[tuple[str, ...], Fraction] = {}
    while pending:
        word, coefficient = pending.pop()
        if any(
            word[index : index + 2] in zero_relations
            for index in range(max(0, len(word) - 1))
        ):
            continue
        replaced = False
        for index in range(max(0, len(word) - 1)):
            pair = word[index : index + 2]
            if pair in rewrites:
                pending.append(
                    (
                        word[:index] + rewrites[pair] + word[index + 2 :],
                        coefficient,
                    )
                )
                replaced = True
                break
        if not replaced:
            values[word] = values.get(word, Fraction()) + coefficient
    return OperatorPolynomial._from_dict(values)


def _is_zero_mod_complex(matrix: Matrix) -> bool:
    zero = OperatorPolynomial.zero()
    return all(
        _reduce_complex_relations(entry) == zero for row in matrix for entry in row
    )


def _digest(matrix: Matrix) -> str:
    payload = "\n".join(
        ",".join(entry.display() for entry in row) for row in matrix
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _sympy_digest(matrix: sp.MatrixBase) -> str:
    payload = sp.srepr(sp.ImmutableDenseMatrix(matrix)).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _elementary_shear(
    primal_target: int,
    primal_source: int,
    operator: str,
    source_cotangent: int,
    target_cotangent: int,
) -> tuple[Matrix, Matrix]:
    """Return one canonical shear and its exact inverse."""

    forward = _identity()
    inverse = _identity()
    forward[primal_target][primal_source] = OperatorPolynomial.atom(operator)
    inverse[primal_target][primal_source] = OperatorPolynomial.atom(operator, -1)
    adjoint = operator + "sharp"
    forward[source_cotangent][target_cotangent] = OperatorPolynomial.atom(
        adjoint, -1
    )
    inverse[source_cotangent][target_cotangent] = OperatorPolynomial.atom(adjoint)
    return forward, inverse


@dataclass(frozen=True)
class CurvatureMappingCylinderKernel:
    """Exact formal mapping-cylinder differential and support-local SDR."""

    split_differential: Matrix
    new_to_old: Matrix
    old_to_new: Matrix
    prolonged_differential: Matrix
    inclusion: Matrix
    projection: Matrix
    homotopy: Matrix
    pairing: Matrix
    field_pairing: sp.Matrix
    ghost_pairing: sp.Matrix

    @staticmethod
    def build() -> "CurvatureMappingCylinderKernel":
        # Block order:
        # 0..3 auxiliary G,M,E,I;
        # 4..6 primal cone X_U,X_Eq,X_Id;
        # 7..9 shifted cone Y_U,Y_Eq,Y_Id;
        # 10..12 dual X_Id#,X_Eq#,X_U#;
        # 13..15 dual Y_Id#,Y_Eq#,Y_U#.
        q = _zero()
        q[1][0] = OperatorPolynomial.atom("K")
        q[2][1] = OperatorPolynomial.atom("Eaux")
        q[3][2] = OperatorPolynomial.atom("C")

        # Cone(id_C): D(X)=dX+Y and D(Y)=-dY.
        q[5][4] = OperatorPolynomial.atom("Ecurv")
        q[6][5] = OperatorPolynomial.atom("Ncurv")
        q[7][4] = OperatorPolynomial.identity()
        q[8][5] = OperatorPolynomial.identity()
        q[9][6] = OperatorPolynomial.identity()
        q[8][7] = OperatorPolynomial.atom("Ecurv", -1)
        q[9][8] = OperatorPolynomial.atom("Ncurv", -1)

        # Cotangent dual cone is forced, not independently normalized.  For
        # D:Z_d->Z'_{d+1}, odd cyclicity gives the dual coefficient
        # (-1)^(d+1) epsilon(Z')/epsilon(Z) D^sharp.
        primal_cone = _zero()
        for row in range(4, 10):
            for column in range(4, 10):
                primal_cone[row][column] = q[row][column]
        primal_indices = (4, 5, 6, 7, 8, 9)
        dual_of = {
            4: 12,  # X_U <-> X_U#
            5: 11,  # X_Eq <-> X_Eq#
            6: 10,  # X_Id <-> X_Id#
            7: 15,  # Y_U <-> Y_U#
            8: 14,  # Y_Eq <-> Y_Eq#
            9: 13,  # Y_Id <-> Y_Id#
        }
        for source in primal_indices:
            for target in primal_indices:
                entry = primal_cone[target][source]
                if entry != OperatorPolynomial.zero():
                    sign = (
                        (-1) ** (BLOCK_DEGREES[source] + 1)
                        * PAIRING_EPSILON[target]
                        * PAIRING_EPSILON[source]
                    )
                    q[dual_of[source]][dual_of[target]] = (
                        _formal_adjoint(entry).scale(sign)
                    )

        # Pair auxiliary G-I, M-E and every cone block with its cotangent.
        # This is an odd skew incidence form, not an ordinary symmetric one.
        pairing = _zero()
        for left, right, epsilon in (
            (0, 3, 1),
            (1, 2, 1),
            (4, 12, 1),
            (5, 11, -1),
            (6, 10, -1),
            (7, 15, -1),
            (8, 14, -1),
            (9, 13, 1),
        ):
            pairing[left][right] = OperatorPolynomial.identity(epsilon)
            pairing[right][left] = OperatorPolynomial.identity(-epsilon)

        # Elementary type-II shifts.  The specified cotangent signs are the
        # central convention guarded by this module.
        shear_t, inverse_t = _elementary_shear(4, 1, "T", 2, 12)
        shear_a, inverse_a = _elementary_shear(5, 2, "A", 1, 11)
        shear_b, inverse_b = _elementary_shear(6, 3, "B", 0, 10)
        transform = _multiply(_multiply(shear_b, shear_a), shear_t)
        transform_inverse = _multiply(
            _multiply(inverse_t, inverse_a), inverse_b
        )
        prolonged = _multiply(_multiply(transform, q), transform_inverse)

        # Split inclusion/projection and cone contraction, conjugated once.
        split_i = _zero()
        split_p = _zero()
        for index in range(4):
            split_i[index][index] = OperatorPolynomial.identity()
            split_p[index][index] = OperatorPolynomial.identity()
        inclusion = _multiply(transform, split_i)
        projection = _multiply(split_p, transform_inverse)

        split_h = _zero()
        # On the primal cone h(Y)=-X gives Qh+hQ=-I.
        split_h[4][7] = OperatorPolynomial.identity(-1)
        split_h[5][8] = OperatorPolynomial.identity(-1)
        split_h[6][9] = OperatorPolynomial.identity(-1)
        # The cotangent contraction is fixed by the ordinary SDR equation;
        # graded cyclicity is checked independently below.
        split_h[15][12] = OperatorPolynomial.identity(-1)
        split_h[14][11] = OperatorPolynomial.identity(-1)
        split_h[13][10] = OperatorPolynomial.identity(-1)
        homotopy = _multiply(_multiply(transform, split_h), transform_inverse)

        ordinary = _ordinary_system()
        result = CurvatureMappingCylinderKernel(
            split_differential=q,
            new_to_old=transform,
            old_to_new=transform_inverse,
            prolonged_differential=prolonged,
            inclusion=inclusion,
            projection=projection,
            homotopy=homotopy,
            pairing=pairing,
            field_pairing=ordinary.field_fibre_pairing,
            ghost_pairing=ordinary.gauge_fixing_pairing,
        )
        result.verify()
        return result

    def verify(self) -> None:
        identity = _identity()
        if _multiply(self.new_to_old, self.old_to_new) != identity:
            raise AssertionError("mapping-cylinder transform has no right inverse")
        if _multiply(self.old_to_new, self.new_to_old) != identity:
            raise AssertionError("mapping-cylinder transform has no left inverse")
        if _multiply(self.pairing, self.pairing) != _scale(identity, -1):
            raise AssertionError("odd incidence pairing is not nondegenerate")
        canonical_defect = _add(
            _multiply(
                _multiply(_matrix_adjoint(self.new_to_old), self.pairing),
                self.new_to_old,
            ),
            _scale(self.pairing, -1),
        )
        if not _is_zero(canonical_defect):
            raise AssertionError("T/A/B mapping-cylinder shift is not canonical")
        if not _is_zero_mod_complex(
            _multiply(self.split_differential, self.split_differential)
        ):
            raise AssertionError("split mapping-cylinder differential is not nilpotent")
        if not _is_zero_mod_complex(
            _multiply(self.prolonged_differential, self.prolonged_differential)
        ):
            raise AssertionError("conjugated mapping-cylinder differential is not nilpotent")
        degree_sign = _degree_sign()
        split_cyclic_defect = _add(
            _multiply(_matrix_adjoint(self.split_differential), self.pairing),
            _multiply(
                _multiply(degree_sign, self.pairing),
                self.split_differential,
            ),
        )
        if not _is_zero(split_cyclic_defect):
            nonzero = [
                (row, column, split_cyclic_defect[row][column].display())
                for row in range(SIZE)
                for column in range(SIZE)
                if split_cyclic_defect[row][column]
                != OperatorPolynomial.zero()
            ]
            raise AssertionError("split Q is not odd cyclic: " + str(nonzero))
        prolonged_cyclic_defect = _add(
            _multiply(_matrix_adjoint(self.prolonged_differential), self.pairing),
            _multiply(
                _multiply(degree_sign, self.pairing),
                self.prolonged_differential,
            ),
        )
        if not _is_zero(prolonged_cyclic_defect):
            raise AssertionError("conjugated Q is not odd cyclic")

        base_identity = _zero()
        for index in range(4):
            base_identity[index][index] = OperatorPolynomial.identity()
        if _multiply(self.projection, self.inclusion) != base_identity:
            raise AssertionError("mapping-cylinder P I is not the base identity")
        if not _is_zero(
            _add(
                _multiply(self.prolonged_differential, self.inclusion),
                _scale(
                    _multiply(self.inclusion, self.split_differential), -1
                ),
            )
        ):
            raise AssertionError("mapping-cylinder inclusion is not a chain map")
        if not _is_zero(
            _add(
                _multiply(self.projection, self.prolonged_differential),
                _scale(
                    _multiply(self.split_differential, self.projection), -1
                ),
            )
        ):
            raise AssertionError("mapping-cylinder projection is not a chain map")
        retract_defect = _add(
            _add(
                _multiply(self.inclusion, self.projection),
                _scale(identity, -1),
            ),
            _scale(
                _add(
                    _multiply(self.prolonged_differential, self.homotopy),
                    _multiply(self.homotopy, self.prolonged_differential),
                ),
                -1,
            ),
        )
        if not _is_zero(retract_defect):
            nonzero = [
                (row, column, retract_defect[row][column].display())
                for row in range(SIZE)
                for column in range(SIZE)
                if retract_defect[row][column] != OperatorPolynomial.zero()
            ]
            raise AssertionError(
                "IP-1=QH+HQ failed in the mapping cylinder: " + str(nonzero)
            )
        # A cyclic contraction has the opposite degree-one Koszul sign from
        # the differential: <Hx,y>=(-1)^|x|<x,Hy>.
        homotopy_cyclic_defect = _add(
            _multiply(_matrix_adjoint(self.homotopy), self.pairing),
            _scale(
                _multiply(_multiply(degree_sign, self.pairing), self.homotopy),
                -1,
            ),
        )
        if not _is_zero(homotopy_cyclic_defect):
            nonzero = [
                (row, column, homotopy_cyclic_defect[row][column].display())
                for row in range(SIZE)
                for column in range(SIZE)
                if homotopy_cyclic_defect[row][column]
                != OperatorPolynomial.zero()
            ]
            raise AssertionError("mapping-cylinder H is not odd cyclic: " + str(nonzero))

        # Convention guard: A_raw acts on raw EL covectors, whereas the
        # four-row Q input is Ebar=J^{-1}E_raw.  Hence A=A_raw J.
        if self.field_pairing.shape != (24, 24) or self.field_pairing.rank() != 24:
            raise AssertionError("J_aux is not a perfect field pairing")
        if self.field_pairing * self.field_pairing.inv() != sp.eye(24):
            raise AssertionError("paired/raw equation conversion failed")
        if self.ghost_pairing.shape != (9, 9) or self.ghost_pairing.rank() != 9:
            raise AssertionError("Y_aux is not a perfect ghost pairing")
        if self.ghost_pairing * self.ghost_pairing.inv() != sp.eye(9):
            raise AssertionError("ghost/identity pairing conversion failed")

        for row in range(SIZE):
            for column in range(SIZE):
                if self.split_differential[row][column] != OperatorPolynomial.zero():
                    if BLOCK_DEGREES[row] != BLOCK_DEGREES[column] + 1:
                        raise AssertionError(
                            f"Q arrow {BLOCK_NAMES[column]}->{BLOCK_NAMES[row]} "
                            "does not raise degree by one"
                        )
                if self.new_to_old[row][column] != OperatorPolynomial.zero():
                    if BLOCK_DEGREES[row] != BLOCK_DEGREES[column]:
                        raise AssertionError("canonical shear is not degree zero")
                if self.pairing[row][column] != OperatorPolynomial.zero():
                    if BLOCK_DEGREES[row] + BLOCK_DEGREES[column] != 1:
                        raise AssertionError("incidence pairing does not have degree one")

        chain_defects = (
            OperatorPolynomial.atom("T") * OperatorPolynomial.atom("K"),
            OperatorPolynomial.atom("Ecurv") * OperatorPolynomial.atom("T")
            + (
                OperatorPolynomial.atom("A")
                * OperatorPolynomial.atom("Eaux")
            ).scale(-1),
            OperatorPolynomial.atom("Ncurv") * OperatorPolynomial.atom("A")
            + (
                OperatorPolynomial.atom("B") * OperatorPolynomial.atom("C")
            ).scale(-1),
            OperatorPolynomial.atom("C") * OperatorPolynomial.atom("Tsharp"),
            OperatorPolynomial.atom("Tsharp")
            * OperatorPolynomial.atom("EcurvSharp")
            + (
                OperatorPolynomial.atom("Eaux")
                * OperatorPolynomial.atom("Asharp")
            ).scale(-1),
            OperatorPolynomial.atom("Asharp")
            * OperatorPolynomial.atom("NcurvSharp")
            + (
                OperatorPolynomial.atom("K")
                * OperatorPolynomial.atom("Bsharp")
            ).scale(-1),
        )
        if any(
            _reduce_chain_relations(defect) != OperatorPolynomial.zero()
            for defect in chain_defects
        ):
            raise AssertionError("primal/cotangent chain-map relation drifted")

    def certificate(self) -> dict[str, object]:
        self.verify()
        return {
            "schema": "pure-weyl-curvature-mapping-cylinder-kernel-v1",
            "auxiliary_four_row_degrees": {
                "G[9]": -1,
                "M[24]": 0,
                "Ebar[24]": 1,
                "I[9]": 2,
            },
            "curvature_complex_degrees": {
                "U[26]": 0,
                "Eq[40]": 1,
                "Id[14]": 2,
            },
            "complete_16_block_degree_ledger": [
                {
                    "index": index,
                    "block": BLOCK_NAMES[index],
                    "degree": BLOCK_DEGREES[index],
                }
                for index in range(SIZE)
            ],
            "degree_checks": {
                "every_split_Q_arrow_raises_degree_by_one": True,
                "every_canonical_shear_has_degree_zero": True,
                "every_incidence_pairing_has_total_degree_one": True,
            },
            "odd_BV_cyclicity": {
                "pairing": "Omega(z,zsharp)=epsilon_z, Omega(zsharp,z)=-epsilon_z",
                "pairing_epsilon_auxiliary": [1, 1, -1, -1],
                "pairing_epsilon_X": [1, -1, -1],
                "pairing_epsilon_Y": [-1, -1, 1],
                "Koszul_degree_sign": "D_jj=(-1)^degree(j)",
                "dual_arrow_rule": (
                    "D:Z_d->Z'_(d+1) induces "
                    "(-1)^(d+1) epsilon_Z'/epsilon_Z Dsharp"
                ),
                "split_Q_cyclicity_defect": 0,
                "prolonged_Q_cyclicity_defect": 0,
                "homotopy_cyclicity_defect": 0,
                "cyclicity_identity": "Q^(T,formal) Omega+D Omega Q=0",
                "cyclic_homotopy_identity": (
                    "H^(T,formal) Omega-D Omega H=0"
                ),
            },
            "equation_normalization": {
                "four_row_equation": "Ebar=J_aux^{-1} E_raw",
                "raw_to_paired_map": "A=A_raw J_aux",
                "p_equation_domain": "paired Ebar row",
                "J_aux_shape": list(self.field_pairing.shape),
                "J_aux_rank": self.field_pairing.rank(),
                "J_aux_sha256": _sympy_digest(self.field_pairing),
                "Y_aux_shape": list(self.ghost_pairing.shape),
                "Y_aux_rank": self.ghost_pairing.rank(),
                "Y_aux_sha256": _sympy_digest(self.ghost_pairing),
                "odd_curvature_incidence_sha256": _digest(self.pairing),
                "conversion_defect": 0,
            },
            "primal_graph_shifts": [
                "X_U -> X_U+T M",
                "X_Eq -> X_Eq+A Ebar",
                "X_Id -> X_Id+B I",
            ],
            "forced_cotangent_shifts": [
                "Ebar -> Ebar-Tsharp X_Usharp",
                "M -> M-Asharp X_Eqsharp",
                "G -> G-Bsharp X_Idsharp",
            ],
            "cotangent_direction": (
                "T,A,B map auxiliary primal rows to curvature primal rows; "
                "their adjoints map curvature dual rows contravariantly into "
                "auxiliary cotangent rows"
            ),
            "mapping_cylinder": {
                "attachment": "Cone(identity_curvature) plus cotangent dual",
                "autonomous_curvature_direct_sum_used": False,
                "reason": "a direct sum would duplicate the E/A/L module",
                "split_cone_contractible": True,
                "new_to_old_inverse_defect": 0,
                "BV_pairing_defect": 0,
                "odd_BV_pairing_squared": "-identity",
                "odd_BV_cyclicity_defect": 0,
                "Q_squared": "zero",
                "P_I": "identity",
                "chain_maps": "exact",
                "I_P_minus_identity": "QH+HQ",
                "homotopy_sign": "IP-1=QH+HQ",
            },
            "coefficient_inputs": {
                "T_state": "order 3, from C1 and div C1",
                "A_equation": "order 2, paired Ebar normalization",
                "B_identity": "order 0, rank 4",
                "chain_relations": [
                    "T K_aux=0",
                    "E_curv T=A Ebar",
                    "N_curv A=B C_aux",
                ],
                "formal_adjoint_chain_relations": [
                    "C_aux Tsharp=0",
                    "Tsharp E_curv_sharp=Ebar Asharp",
                    "Asharp N_curv_sharp=K_aux Bsharp",
                ],
                "primal_and_adjoint_relation_defects": 0,
            },
            "support": {
                "finite_differential_orders_only": True,
                "inverse_Laplacian_or_curl": False,
                "spectral_projector": False,
                "Green_operator": False,
                "compact": True,
                "spacelike_compact": True,
                "smooth_global": True,
            },
            "exact_formal_kernel": True,
            "coefficientwise_complete_prolonged_Q": False,
            "reason_for_fail_closed": (
                "the kernel fixes degrees, signs and cotangent incidence, but "
                "the complete expanded coefficient matrix has not yet been "
                "instantiated in this 16-block cone basis"
            ),
            "warranted_atomic_flags": [],
            "status_flags_promoted": [],
            "matrix_sha256": {
                "split_Q": _digest(self.split_differential),
                "canonical_transform": _digest(self.new_to_old),
                "prolonged_Q": _digest(self.prolonged_differential),
                "inclusion": _digest(self.inclusion),
                "projection": _digest(self.projection),
                "homotopy": _digest(self.homotopy),
                "odd_pairing": _digest(self.pairing),
            },
            "fail_closed": True,
        }
