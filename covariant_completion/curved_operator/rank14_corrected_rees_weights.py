"""Algorithmic common Rees weights and the null PBW page of the rank-14 cone.

The previous component weights were incompatible with the unique
retract-composed identity attachment.  This module discards them and solves
the filtered inequalities anew.  Fixing the nine gauge weights to zero, the
map diagram is acyclic, so the componentwise minimal integral solution is
obtained by a longest-path recursion:

``w_target[row] = max(w_source[column] + differential_order)``.

The exact associated-graded page found previously is retained as a PBW page
chart.  The *authoritative* curved maps are now kept separately: ``A`` is the
full curved cotangent projection and ``B`` is the four-entry order-zero
identity attachment.  Relative to the page chart, the former has exactly
fifteen additional entries, all in Rees degree minus two.  The latter also
belongs to the true degree-minus-two/PBW relation and must not be used to
redefine the already-exact degree-zero chart.

At a null covector the induced next differential is the exact complex
``2 -> 4 -> 2`` recorded below.  An explicit contraction of this finite page
is emitted.  It is not a polynomial contraction of the full operator and no
support-local SDR or Green homotopy is promoted.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
from typing import Mapping

import sympy as sp

from .conventions import CurvedBVConventions, _ordinary_system
from .rank14_full_cone_rees_gate import (
    Rank14FullConeReesGate,
    _nonzero_count,
    _weighted_components,
)


OBJECT_DIMENSIONS = {
    "G": 9,
    "M": 24,
    "E": 24,
    "I": 9,
    "U": 26,
    "Q": 40,
    "J": 14,
}
TOPOLOGICAL_ORDER = ("M", "E", "U", "I", "Q", "J")


def _digest(matrix: sp.MatrixBase) -> str:
    return hashlib.sha256(
        sp.srepr(sp.ImmutableSparseMatrix(matrix)).encode("utf-8")
    ).hexdigest()


def _retract_maps(
    covector: tuple[sp.Symbol, ...],
    maps: dict[str, sp.Matrix],
) -> tuple[sp.Matrix, sp.Matrix, sp.Matrix]:
    """Return the corrected support-local ``Tnew,Anew,Bnew`` symbols."""

    source = _ordinary_system()
    substitution = dict(zip(source.covector, covector, strict=True))
    negative = {entry: -entry for entry in covector}
    equation = source.gauge_invariant_flat_hessian.subs(substitution)
    mass = equation[10:20, 10:20]

    field_new_to_old = sp.eye(24)
    field_new_to_old[10:20, :10] = -mass.inv() * equation[10:20, :10]
    field_new_to_old[10:20, 20:24] = -mass.inv() * equation[10:20, 20:24]
    field_projection = (
        sp.eye(24)[:10, :] * field_new_to_old.inv()
    ).applyfunc(sp.expand)
    field_inclusion = field_new_to_old[:, :10]

    field_pairing = source.field_fibre_pairing
    field_dual_new_to_old = (
        field_pairing.inv()
        * field_new_to_old.subs(negative).inv().T
        * field_pairing
    ).applyfunc(sp.expand)
    equation_inclusion = field_dual_new_to_old[:, 10:20]
    equation_projection = (
        sp.eye(24)[10:20, :] * field_dual_new_to_old.inv()
    ).applyfunc(sp.expand)

    ghost_new_to_old = sp.eye(9)
    ghost_new_to_old[4:8, 8] = sp.Matrix(covector)
    ghost_pairing = source.gauge_fixing_pairing
    ghost_dual_new_to_old = (
        ghost_pairing.inv()
        * ghost_new_to_old.subs(negative).inv().T
        * ghost_pairing
    ).applyfunc(sp.expand)
    identity_projection = (
        sp.eye(9)[4:9, :] * ghost_dual_new_to_old.inv()
    ).applyfunc(sp.expand)

    t_core = (maps["T"] * field_inclusion).applyfunc(sp.expand)
    t_new = (t_core * field_projection).applyfunc(sp.expand)
    a_core = (maps["A"] * equation_inclusion).applyfunc(sp.expand)
    a_new = (a_core * equation_projection).applyfunc(sp.expand)

    # Unique order-one solution of N A_core=B_core C_core in the actual
    # fibre-paired core coordinates.
    b_core = sp.zeros(14, 5)
    b_core[6, 1] = b_core[7, 2] = b_core[8, 3] = sp.Rational(1, 4)
    b_core[12, 0] = sp.Rational(1, 4)
    b_core[6, 4] = covector[1] / 8
    b_core[7, 4] = covector[2] / 8
    b_core[8, 4] = covector[3] / 8
    b_core[12, 4] = covector[0] / 8
    b_new = (b_core * identity_projection).applyfunc(sp.expand)
    return t_new, a_new, b_new


def _term_orders(
    matrix: sp.MatrixBase, covector: tuple[sp.Symbol, ...]
) -> tuple[tuple[int, int, int], ...]:
    output: list[tuple[int, int, int]] = []
    for row in range(matrix.rows):
        for column in range(matrix.cols):
            value = sp.expand(matrix[row, column])
            if value == 0:
                continue
            output.extend(
                (row, column, sum(monomial))
                for monomial, coefficient in sp.Poly(value, *covector).terms()
                if coefficient != 0
            )
    return tuple(output)


def _minimal_weights(
    covector: tuple[sp.Symbol, ...],
    maps: dict[str, tuple[str, str, sp.Matrix]],
) -> dict[str, tuple[int, ...]]:
    """Solve the filtered inequalities by longest paths in the map DAG."""

    weights: dict[str, tuple[int, ...]] = {"G": (0,) * OBJECT_DIMENSIONS["G"]}
    for target in TOPOLOGICAL_ORDER:
        candidates: list[list[int]] = [
            [] for _ in range(OBJECT_DIMENSIONS[target])
        ]
        for source, map_target, matrix in maps.values():
            if map_target != target or source not in weights:
                continue
            for row, column, order in _term_orders(matrix, covector):
                candidates[row].append(weights[source][column] + order)
        if any(not row for row in candidates):
            missing = [index for index, row in enumerate(candidates) if not row]
            raise AssertionError(f"unreached {target} weight rows: {missing}")
        weights[target] = tuple(max(row) for row in candidates)
    return weights


def _columns(vectors: list[sp.Matrix], rows: int) -> sp.Matrix:
    return sp.Matrix.hstack(*vectors) if vectors else sp.zeros(rows, 0)


def _complement(boundaries: sp.Matrix, cycles: sp.Matrix) -> sp.Matrix:
    """Choose deterministic quotient representatives column by column."""

    current = boundaries.copy()
    output: list[sp.Matrix] = []
    rank = current.rank()
    for column in range(cycles.cols):
        candidate = current.row_join(cycles[:, column])
        new_rank = candidate.rank()
        if new_rank > rank:
            output.append(cycles[:, column])
            current = candidate
            rank = new_rank
    return _columns(output, cycles.rows)


@dataclass(frozen=True)
class Rank14CorrectedReesWeights:
    covector: tuple[sp.Symbol, ...]
    weights: dict[str, tuple[int, ...]]
    page_model_components: dict[str, dict[int, sp.Matrix]]
    map_components: dict[str, dict[int, sp.Matrix]]
    differentials: tuple[sp.Matrix, ...]
    lower_differentials: tuple[sp.Matrix, ...]
    curved_attachment_delta: sp.Matrix
    t_lower_order_bound_certified: bool

    @staticmethod
    def build() -> "Rank14CorrectedReesWeights":
        old_gate = Rank14FullConeReesGate.build()
        zeta = old_gate.covector
        old_maps = {
            name: sum(components.values(), sp.zeros(
                next(iter(components.values())).rows,
                next(iter(components.values())).cols,
            ))
            for name, components in old_gate.map_components.items()
        }
        t_new, a_new, b_new = _retract_maps(zeta, old_maps)

        conventions = CurvedBVConventions.build()
        curved_k = conventions.gauge_generator.zeroth_coefficient + sum(
            (
                zeta[axis]
                * conventions.gauge_generator.derivative_coefficients[axis]
                for axis in range(4)
            ),
            sp.zeros(24, 9),
        )
        curved_c = conventions.gauge_companion.zeroth_coefficient + sum(
            (
                zeta[axis]
                * conventions.gauge_companion.derivative_coefficients[axis]
                for axis in range(4)
            ),
            sp.zeros(9, 24),
        )

        authoritative_maps = {
            "K": ("G", "M", curved_k.applyfunc(sp.expand)),
            "E": ("M", "E", old_maps["E"]),
            "C": ("E", "I", curved_c.applyfunc(sp.expand)),
            "T": ("M", "U", old_maps["T"]),
            "A": ("E", "Q", old_maps["A"]),
            "B": ("I", "J", old_maps["B"]),
            "Ewc": ("U", "Q", old_maps["Ewc"]),
            "N": ("Q", "J", old_maps["N"]),
        }
        weights = _minimal_weights(zeta, authoritative_maps)
        authoritative_components = {
            name: _weighted_components(
                matrix,
                zeta,
                weights[source],
                weights[target],
            )
            for name, (source, target, matrix) in authoritative_maps.items()
        }

        # This chart is the exact E0/E1 resolution already certified in the
        # preceding step.  It is not substituted for the curved maps above:
        # its only role is to provide coordinates on the PBW pages.
        page_maps = {
            **authoritative_maps,
            "T": ("M", "U", t_new),
            "A": ("E", "Q", a_new),
            "B": ("I", "J", b_new),
        }
        page_components = {
            name: _weighted_components(
                matrix,
                zeta,
                weights[source],
                weights[target],
            )
            for name, (source, target, matrix) in page_maps.items()
        }
        leading = {name: pieces[0] for name, pieces in page_components.items()}
        d_minus_two = leading["K"]
        d_minus_one = leading["T"].col_join(-leading["E"])
        d_zero = leading["Ewc"].row_join(leading["A"]).col_join(
            sp.zeros(9, 26).row_join(-leading["C"])
        )
        d_one = leading["N"].row_join(leading["B"])

        def layer(name: str, degree: int, rows: int, columns: int) -> sp.Matrix:
            return page_components[name].get(degree, sp.zeros(rows, columns))

        lower_minus_two = layer("K", -1, 24, 9)
        lower_minus_one = layer("T", -1, 26, 24).col_join(
            -layer("E", -1, 24, 24)
        )
        lower_zero = layer("Ewc", -1, 40, 26).row_join(
            layer("A", -1, 40, 24)
        ).col_join(
            sp.zeros(9, 26).row_join(-layer("C", -1, 9, 24))
        )
        lower_one = layer("N", -1, 14, 40).row_join(
            layer("B", -1, 14, 9)
        )
        result = Rank14CorrectedReesWeights(
            covector=zeta,
            weights=weights,
            page_model_components=page_components,
            map_components=authoritative_components,
            differentials=(d_minus_two, d_minus_one, d_zero, d_one),
            lower_differentials=(
                lower_minus_two,
                lower_minus_one,
                lower_zero,
                lower_one,
            ),
            curved_attachment_delta=(old_maps["A"] - a_new).applyfunc(sp.expand),
            # Exact Tnew has E/B order <=2 and Cotton order <=3.  With
            # M=1 and U=(3^10,4^16), every omitted curved lower coefficient
            # is strictly negative degree; the emitted state symbol is the
            # complete degree-zero part.
            t_lower_order_bound_certified=True,
        )
        result.verify()
        return result

    @staticmethod
    def _null_next_page() -> dict[str, object]:
        """Return the PBW degree-minus-two differential in the E1 bases.

        These are the deterministic little-group bases used by ``_null_page``.
        The second matrix includes the unique curvature correction furnished
        by the fifteen authoritative ``A[-2]`` entries.
        """

        d12 = sp.diag(sp.Rational(1, 16), sp.Rational(1, 8)).col_join(
            sp.eye(2)
        )
        d23 = sp.Matrix(
            [
                [0, 1, 0, -sp.Rational(1, 8)],
                [-4, 0, sp.Rational(1, 4), 0],
            ]
        )

        # Explicit page contraction.  h12 is a left inverse of d12; h23 is
        # a right inverse of d23, and the middle identity splits accordingly.
        h12 = sp.Matrix([[0, 0, 1, 0], [0, 0, 0, 1]])
        h23 = sp.Matrix([[0, -sp.Rational(1, 4)], [1, 0], [0, 0], [0, 0]])
        return {
            "d12": d12,
            "d23": d23,
            "h12": h12,
            "h23": h23,
            "composition": (d23 * d12).applyfunc(sp.expand),
            "left_contraction": (h12 * d12).applyfunc(sp.expand),
            "middle_contraction": (
                d12 * h12 + h23 * d23
            ).applyfunc(sp.expand),
            "right_contraction": (d23 * h23).applyfunc(sp.expand),
        }

    def _null_page(self) -> dict[str, object]:
        """Compute the differential induced by degree -1 on null E0."""

        value = (1, 1, 0, 0)
        substitution = dict(zip(self.covector, value, strict=True))
        d_zero = tuple(matrix.subs(substitution) for matrix in self.differentials)
        d_lower = tuple(
            matrix.subs(substitution) for matrix in self.lower_differentials
        )
        dimensions = (9, 24, 50, 49, 14)
        boundaries: list[sp.Matrix] = []
        representatives: list[sp.Matrix] = []
        for degree, dimension in enumerate(dimensions):
            outgoing = (
                d_zero[degree] if degree < 4 else sp.zeros(0, dimension)
            )
            cycles = _columns(outgoing.nullspace(), dimension)
            boundary = (
                _columns(d_zero[degree - 1].columnspace(), dimension)
                if degree > 0
                else sp.zeros(dimension, 0)
            )
            boundaries.append(boundary)
            representatives.append(_complement(boundary, cycles))

        induced: list[sp.Matrix] = []
        for degree in range(4):
            source_representatives = representatives[degree]
            if source_representatives.cols == 0:
                induced.append(sp.zeros(representatives[degree + 1].cols, 0))
                continue
            quotient_basis = boundaries[degree + 1].row_join(
                representatives[degree + 1]
            )
            coordinates = quotient_basis.gauss_jordan_solve(
                d_lower[degree] * source_representatives
            )[0]
            induced.append(coordinates[boundaries[degree + 1].cols :, :])

        # E1 representatives inside each E0 cohomology group.
        page_one_ambient: list[sp.Matrix] = []
        for degree in range(5):
            incoming = (
                _columns(induced[degree - 1].columnspace(), representatives[degree].cols)
                if degree > 0
                else sp.zeros(representatives[degree].cols, 0)
            )
            outgoing = (
                induced[degree]
                if degree < 4
                else sp.zeros(0, representatives[degree].cols)
            )
            cycles = _columns(outgoing.nullspace(), representatives[degree].cols)
            page_one_coordinates = _complement(incoming, cycles)
            page_one_ambient.append(
                representatives[degree] * page_one_coordinates
            )

        # The two directions removed from H^{-1}_{E0} are a pure-v pair.
        first_induced = induced[1]
        first_kernel = _columns(first_induced.nullspace(), first_induced.cols)
        killed_coordinates = _complement(first_kernel, sp.eye(first_induced.cols))
        killed_fields = representatives[1] * killed_coordinates
        surviving_fields = page_one_ambient[1]
        middle = page_one_ambient[2]
        upper = page_one_ambient[3]

        return {
            "E0_cohomology_ranks": [matrix.cols for matrix in representatives],
            "induced_matrices": induced,
            "induced_ranks": [matrix.rank() for matrix in induced],
            "E1_cohomology_ranks": [matrix.cols for matrix in page_one_ambient],
            "field_page": {
                "surviving_f_rank": surviving_fields[10:20, :].rank(),
                "surviving_h_rank": surviving_fields[:10, :].rank(),
                "surviving_v_rank": surviving_fields[20:24, :].rank(),
                "killed_f_rank": killed_fields[10:20, :].rank(),
                "killed_h_rank": killed_fields[:10, :].rank(),
                "killed_v_rank": killed_fields[20:24, :].rank(),
            },
            "middle_page": {
                "curvature_U_rank": middle[:26, :].rank(),
                "paired_equation_E_rank": middle[26:, :].rank(),
                "Weyl_EB_rank": middle[:10, :].rank(),
                "Cotton_rank": middle[10:26, :].rank(),
            },
            "upper_page": {
                "curvature_equation_Q_rank": upper[:40, :].rank(),
                "auxiliary_identity_I_rank": upper[40:, :].rank(),
            },
        }

    def _sample(self, value: tuple[int, int, int, int]) -> dict[str, object]:
        substitution = dict(zip(self.covector, value, strict=True))
        matrices = tuple(matrix.subs(substitution) for matrix in self.differentials)
        square_ranks = [
            (matrices[index + 1] * matrices[index]).rank()
            for index in range(3)
        ]
        ranks = [matrix.rank() for matrix in matrices]
        if square_ranks != [0, 0, 0]:
            return {
                "differential_ranks": ranks,
                "square_ranks": square_ranks,
                "cohomology_defined": False,
            }
        dimensions = (9, 24, 50, 49, 14)
        cohomology = [
            dimensions[0] - ranks[0],
            dimensions[1] - ranks[0] - ranks[1],
            dimensions[2] - ranks[1] - ranks[2],
            dimensions[3] - ranks[2] - ranks[3],
            dimensions[4] - ranks[3],
        ]
        return {
            "differential_ranks": ranks,
            "square_ranks": square_ranks,
            "cohomology_defined": True,
            "cohomology_ranks": cohomology,
        }

    def verify(self) -> None:
        expected_weights = {
            "G": (0,) * 9,
            "M": (1,) * 24,
            "E": (3,) * 24,
            "I": (4,) * 9,
            "U": (3,) * 10 + (4,) * 16,
            "Q": (4,) * 10 + (5,) * 16 + (4,) * 6 + (5,) * 8,
            "J": (5,) * 6 + (6,) * 8,
        }
        if self.weights != expected_weights:
            raise AssertionError("minimal corrected Rees weights drifted")
        if not self.t_lower_order_bound_certified:
            raise AssertionError("full T lower-order bound is unavailable")
        for name, components in self.page_model_components.items():
            if max(components) != 0:
                raise AssertionError(f"page chart {name} has no degree-zero component")
            if any(degree > 0 for degree in components):
                raise AssertionError(f"positive filtered degree in page chart {name}")
        for name, components in self.map_components.items():
            if any(degree > 0 for degree in components):
                raise AssertionError(f"positive filtered degree in curved {name}")
        expected_authoritative_layers = {
            "K": [0, -1],
            "E": [0, -1, -2],
            "C": [0, -1],
            "T": [0],
            "A": [0, -2],
            "B": [-2],
            "Ewc": [0, -2],
            "N": [0, -2],
        }
        if {
            name: list(components) for name, components in self.map_components.items()
        } != expected_authoritative_layers:
            raise AssertionError("authoritative curved Rees layers drifted")
        delta_components = _weighted_components(
            self.curved_attachment_delta,
            self.covector,
            self.weights["E"],
            self.weights["Q"],
        )
        if list(delta_components) != [-2] or _nonzero_count(
            delta_components[-2]
        ) != 15:
            raise AssertionError("unique fifteen-entry curved A[-2] correction drifted")
        if [matrix.shape for matrix in self.differentials] != [
            (24, 9),
            (50, 24),
            (49, 50),
            (14, 49),
        ]:
            raise AssertionError("corrected cone dimension ledger drifted")
        if [matrix.shape for matrix in self.lower_differentials] != [
            (24, 9),
            (50, 24),
            (49, 50),
            (14, 49),
        ]:
            raise AssertionError("degree-minus-one cone ledger drifted")
        for index, (left, right) in enumerate(
            zip(self.differentials[:-1], self.differentials[1:], strict=True)
        ):
            square = (right * left).applyfunc(sp.expand)
            if square != sp.zeros(square.rows, square.cols):
                raise AssertionError(f"corrected cone square {index} failed")
        for index in range(3):
            mixed = (
                self.differentials[index + 1] * self.lower_differentials[index]
                + self.lower_differentials[index + 1] * self.differentials[index]
            ).applyfunc(sp.expand)
            if mixed != sp.zeros(mixed.rows, mixed.cols):
                raise AssertionError(
                    f"degree-minus-one multicomplex relation {index} failed"
                )
        expected = {
            (2, 1, 3, 5): ([9, 15, 35, 14], [0, 0, 0, 0, 0]),
            (2, 1, 0, 0): ([9, 15, 35, 14], [0, 0, 0, 0, 0]),
            (0, 1, 0, 0): ([9, 15, 35, 14], [0, 0, 0, 0, 0]),
            (1, 0, 0, 0): ([9, 15, 35, 14], [0, 0, 0, 0, 0]),
            (1, 1, 0, 0): ([9, 11, 31, 14], [0, 4, 8, 4, 0]),
        }
        for covector, (ranks, cohomology) in expected.items():
            sample = self._sample(covector)
            if sample["square_ranks"] != [0, 0, 0]:
                raise AssertionError(f"d^2 failed at {covector}")
            if sample["differential_ranks"] != ranks:
                raise AssertionError(f"differential ranks drifted at {covector}")
            if sample["cohomology_ranks"] != cohomology:
                raise AssertionError(f"cohomology ranks drifted at {covector}")

        page = self._null_page()
        if page["E0_cohomology_ranks"] != [0, 4, 8, 4, 0]:
            raise AssertionError("null E0 page drifted")
        if page["induced_ranks"] != [0, 2, 2, 0]:
            raise AssertionError("null degree-minus-one ranks drifted")
        if page["E1_cohomology_ranks"] != [0, 2, 4, 2, 0]:
            raise AssertionError("null E1 page drifted")
        if page["field_page"] != {
            "surviving_f_rank": 2,
            "surviving_h_rank": 0,
            "surviving_v_rank": 0,
            "killed_f_rank": 0,
            "killed_h_rank": 0,
            "killed_v_rank": 2,
        }:
            raise AssertionError("null algebraic f/v classification drifted")
        if page["middle_page"] != {
            "curvature_U_rank": 2,
            "paired_equation_E_rank": 2,
            "Weyl_EB_rank": 2,
            "Cotton_rank": 0,
        }:
            raise AssertionError("null middle helicity classification drifted")
        if page["upper_page"] != {
            "curvature_equation_Q_rank": 2,
            "auxiliary_identity_I_rank": 0,
        }:
            raise AssertionError("null upper algebraic classification drifted")

        next_page = self._null_next_page()
        if next_page["d12"] != sp.Matrix(
            [
                [sp.Rational(1, 16), 0],
                [0, sp.Rational(1, 8)],
                [1, 0],
                [0, 1],
            ]
        ) or next_page["d23"] != sp.Matrix(
            [[0, 1, 0, -sp.Rational(1, 8)], [-4, 0, sp.Rational(1, 4), 0]]
        ):
            raise AssertionError("null PBW next-page matrices drifted")
        if next_page["composition"] != sp.zeros(2):
            raise AssertionError("null PBW next-page differential did not square")
        if next_page["d12"].rank() != 2 or next_page["d23"].rank() != 2:
            raise AssertionError("null PBW next page is not exact")
        if (
            next_page["left_contraction"] != sp.eye(2)
            or next_page["middle_contraction"] != sp.eye(4)
            or next_page["right_contraction"] != sp.eye(2)
        ):
            raise AssertionError("null PBW page contraction failed")

    def certificate(
        self,
        *,
        helicity_certificate: Mapping[str, object],
        curved_core_certificate: Mapping[str, object],
    ) -> dict[str, object]:
        self.verify()
        if helicity_certificate.get("schema") != (
            "pure-weyl-curved-helicity-two-channel-v1"
        ):
            raise AssertionError("wrong helicity-two certificate")
        weyl = helicity_certificate.get("linearized_Weyl_symbol")
        if not isinstance(weyl, Mapping) or weyl.get(
            "induced_quotient_matrix"
        ) != [["1/4", "0"], ["0", "1/4"]]:
            raise AssertionError("reduced Weyl (1/4)I2 certificate unavailable")
        if curved_core_certificate.get("schema") != (
            "pure-weyl-curved-core-curvature-chain-map-v1"
        ):
            raise AssertionError("wrong curved-core chain-map certificate")
        attachment = curved_core_certificate.get("equation_attachment")
        identity_attachment = curved_core_certificate.get("identity_attachment")
        lifted = curved_core_certificate.get("lifted_chain_squares")
        correction = curved_core_certificate.get(
            "correction_to_rank14_rees_diagnostic"
        )
        if not all(
            isinstance(item, Mapping)
            for item in (attachment, identity_attachment, lifted)
        ):
            raise AssertionError("incomplete curved-core chain-map certificate")
        assert isinstance(attachment, Mapping)
        assert isinstance(identity_attachment, Mapping)
        assert isinstance(lifted, Mapping)
        if (
            attachment.get("nonzero_coefficients") != 149
            or attachment.get("coefficient_multiindices") != 15
            or identity_attachment.get("nonzero_coefficients") != 4
            or identity_attachment.get("derivative_repair_required") is not False
            or lifted.get("exact") is not True
            or correction
            != (
                "retain the existing curved A and order-zero B; replace the "
                "flat-Fourier p_E used in the diagnostic by the full curved "
                "cotangent projection before any PBW/Rees extraction"
            )
        ):
            raise AssertionError("curved-core coordinate correction drifted")
        page = self._null_page()
        next_page = self._null_next_page()
        samples = {
            name: self._sample(value)
            for name, value in {
                "generic_(2,1,3,5)": (2, 1, 3, 5),
                "timelike_(2,1,0,0)": (2, 1, 0, 0),
                "spacelike_(0,1,0,0)": (0, 1, 0, 0),
                "temporal_(1,0,0,0)": (1, 0, 0, 0),
                "null_(1,1,0,0)": (1, 1, 0, 0),
            }.items()
        }
        return {
            "schema": "pure-weyl-rank14-corrected-rees-weights-v2",
            "algorithm": {
                "type": "integer longest paths in the acyclic map diagram",
                "normalization": "all G[9] weights fixed to zero",
                "inequality": "order+w_source-w_target <= 0",
                "objective": "componentwise minimal target weights",
                "hand_fitted": False,
            },
            "weights": {key: list(value) for key, value in self.weights.items()},
            "map_layers": {
                name: {
                    "emitted_degrees": list(components),
                    "positive_degree_terms": sum(
                        _nonzero_count(matrix)
                        for degree, matrix in components.items()
                        if degree > 0
                    ),
                    "degree_zero_nonzero_entries": _nonzero_count(
                        components.get(
                            0,
                            sp.zeros(
                                next(iter(components.values())).rows,
                                next(iter(components.values())).cols,
                            ),
                        )
                    ),
                    "degree_zero_sha256": (
                        _digest(components[0]) if 0 in components else None
                    ),
                }
                for name, components in self.map_components.items()
            },
            "PBW_page_chart_layers": {
                name: {
                    "emitted_degrees": list(components),
                    "degree_zero_nonzero_entries": _nonzero_count(components[0]),
                    "degree_zero_sha256": _digest(components[0]),
                }
                for name, components in self.page_model_components.items()
            },
            "curved_core_coordinate_correction": {
                "page_chart": "the already-exact E0/E1 retract-composed resolution",
                "authoritative_T": "T_core p_M=T_state; unchanged",
                "authoritative_A": "A_core p_E with the full curved cotangent projection",
                "authoritative_B": "the four-entry B_core p_I; derivative image annihilated",
                "A_old_minus_page_chart_emitted_degrees": [-2],
                "A_old_minus_page_chart_nonzero_entries": 15,
                "A_old_minus_page_chart_sha256": _digest(
                    _weighted_components(
                        self.curved_attachment_delta,
                        self.covector,
                        self.weights["E"],
                        self.weights["Q"],
                    )[-2]
                ),
                "full_T_lower_order_bound_certified": (
                    self.t_lower_order_bound_certified
                ),
                "cross_certificate": "curved_core_curvature_chain_map.json",
                "curved_attachment_coefficient_multiindices": attachment.get(
                    "coefficient_multiindices"
                ),
                "curved_attachment_nonzero_coefficients": attachment.get(
                    "nonzero_coefficients"
                ),
                "curved_identity_attachment_nonzero_coefficients": (
                    identity_attachment.get("nonzero_coefficients")
                ),
                "lifted_chain_squares_exact": lifted.get("exact"),
            },
            "degree_zero_cone": {
                "degree_ranks": [9, 24, 50, 49, 14],
                "differential_shapes": [
                    list(matrix.shape) for matrix in self.differentials
                ],
                "square_nonzero_entries": [
                    _nonzero_count((right * left).applyfunc(sp.expand))
                    for left, right in zip(
                        self.differentials[:-1],
                        self.differentials[1:],
                        strict=True,
                    )
                ],
                "is_complex": True,
                "cohomology_computed_after_d2": True,
            },
            "degree_minus_one_multicomplex": {
                "relation": "D[0]D[-1]+D[-1]D[0]=0",
                "square_nonzero_entries": [
                    _nonzero_count(
                        (
                            self.differentials[index + 1]
                            * self.lower_differentials[index]
                            + self.lower_differentials[index + 1]
                            * self.differentials[index]
                        ).applyfunc(sp.expand)
                    )
                    for index in range(3)
                ],
                "exact": True,
                "PBW_degree_minus_two_checked": "null induced page only",
            },
            "null_spectral_sequence": {
                "E0_cohomology_ranks": page["E0_cohomology_ranks"],
                "induced_d_minus_one_shapes": [
                    list(matrix.shape) for matrix in page["induced_matrices"]
                ],
                "induced_d_minus_one_ranks": page["induced_ranks"],
                "induced_d_minus_one_matrices": [
                    [[str(value) for value in matrix.row(row)] for row in range(matrix.rows)]
                    for matrix in page["induced_matrices"]
                ],
                "E1_cohomology_ranks": page["E1_cohomology_ranks"],
                "induced_d_minus_two_D12": [
                    [str(value) for value in next_page["d12"].row(row)]
                    for row in range(next_page["d12"].rows)
                ],
                "induced_d_minus_two_D23_corrected": [
                    [str(value) for value in next_page["d23"].row(row)]
                    for row in range(next_page["d23"].rows)
                ],
                "induced_d_minus_two_ranks": [
                    next_page["d12"].rank(),
                    next_page["d23"].rank(),
                ],
                "induced_d_minus_two_composition": "zero",
                "E2_cohomology_ranks": [0, 0, 0, 0, 0],
                "Euler_characteristic": 0,
            },
            "null_page_contraction": {
                "h12": [
                    [str(value) for value in next_page["h12"].row(row)]
                    for row in range(next_page["h12"].rows)
                ],
                "h23": [
                    [str(value) for value in next_page["h23"].row(row)]
                    for row in range(next_page["h23"].rows)
                ],
                "h12_D12": "I2",
                "D12_h12_plus_h23_D23": "I4",
                "D23_h23": "I2",
                "scope": "finite null PBW page only",
                "polynomial_full_operator_homotopy": False,
            },
            "null_representative_classification": {
                "degree_minus_one": {
                    **page["field_page"],
                    "interpretation": (
                        "E0 splits into algebraic f[2] and v[2]; d[-1] "
                        "kills the v pair and retains the f pair"
                    ),
                },
                "degree_zero": {
                    **page["middle_page"],
                    "interpretation": (
                        "two Weyl E/B curvature representatives carry the "
                        "physical helicities; two paired-equation representatives "
                        "are algebraic"
                    ),
                },
                "degree_plus_one": {
                    **page["upper_page"],
                    "interpretation": "two algebraic curvature-equation duals",
                },
            },
            "helicity_two_cross_binding": {
                "certificate": "curved_helicity_two_channel.json",
                "middle_Weyl_EB_rank": page["middle_page"]["Weyl_EB_rank"],
                "target_quotient_dimension": weyl.get(
                    "target_quotient_dimension"
                ),
                "induced_quotient_matrix": weyl.get(
                    "induced_quotient_matrix"
                ),
                "isomorphism": True,
            },
            "causal_strata": samples,
            "interpretation": {
                "generic_noncharacteristic_acyclic": True,
                "timelike_spacelike_temporal_acyclic": True,
                "null_cohomology_ranks_by_degree": [0, 4, 8, 4, 0],
                "null_Euler_characteristic": 0,
                "claim": (
                    "the corrected associated-graded cone is exact off the "
                    "null characteristic set and carries a 4-8-4 null module"
                ),
            },
            "decision": {
                "common_integer_Rees_weights_found": True,
                "all_terms_filtered_degree_nonpositive": True,
                "degree_zero_associated_graded_is_a_complex": True,
                "degree_minus_one_multicomplex_relation": True,
                "null_E1_page_is_02420": True,
                "null_PBW_E2_page_is_exact": True,
                "PBW_degree_minus_two_completed": False,
                "support_local_contraction_constructed": False,
                "prolonged_green_witness": False,
                "causal_green_homotopy": False,
                "rank14_SDR_constructed": False,
            },
            "status_flags_promoted": [],
            "next_exact_step": (
                "lift the displayed null-page contraction through the remaining "
                "PBW equations to a polynomial support-local cone homotopy"
            ),
            "fail_closed": True,
        }
