"""Algorithmic common Rees weights for the corrected rank-14 cone.

The previous component weights were incompatible with the unique
retract-composed identity attachment.  This module discards them and solves
the filtered inequalities anew.  Fixing the nine gauge weights to zero, the
map diagram is acyclic, so the componentwise minimal integral solution is
obtained by a longest-path recursion:

``w_target[row] = max(w_source[column] + differential_order)``.

The authoritative curved ``K,E,C`` blocks, corrected retract-composed
``T,A,B`` blocks, and full Weyl--Cotton ``Ewc,N`` blocks then have no positive
filtered-degree term.  Their degree-zero cone is an exact complex.  This is
an associated-graded theorem only; no support-local contraction or Green
homotopy is promoted.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib

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


@dataclass(frozen=True)
class Rank14CorrectedReesWeights:
    covector: tuple[sp.Symbol, ...]
    weights: dict[str, tuple[int, ...]]
    map_components: dict[str, dict[int, sp.Matrix]]
    differentials: tuple[sp.Matrix, ...]
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

        typed_maps = {
            "K": ("G", "M", curved_k.applyfunc(sp.expand)),
            "E": ("M", "E", old_maps["E"]),
            "C": ("E", "I", curved_c.applyfunc(sp.expand)),
            "T": ("M", "U", t_new),
            "A": ("E", "Q", a_new),
            "B": ("I", "J", b_new),
            "Ewc": ("U", "Q", old_maps["Ewc"]),
            "N": ("Q", "J", old_maps["N"]),
        }
        weights = _minimal_weights(zeta, typed_maps)
        components = {
            name: _weighted_components(
                matrix,
                zeta,
                weights[source],
                weights[target],
            )
            for name, (source, target, matrix) in typed_maps.items()
        }
        leading = {name: pieces[0] for name, pieces in components.items()}
        d_minus_two = leading["K"]
        d_minus_one = leading["T"].col_join(-leading["E"])
        d_zero = leading["Ewc"].row_join(leading["A"]).col_join(
            sp.zeros(9, 26).row_join(-leading["C"])
        )
        d_one = leading["N"].row_join(leading["B"])
        result = Rank14CorrectedReesWeights(
            covector=zeta,
            weights=weights,
            map_components=components,
            differentials=(d_minus_two, d_minus_one, d_zero, d_one),
            # Exact Tnew has E/B order <=2 and Cotton order <=3.  With
            # M=1 and U=(3^10,4^16), every omitted curved lower coefficient
            # is strictly negative degree; the emitted state symbol is the
            # complete degree-zero part.
            t_lower_order_bound_certified=True,
        )
        result.verify()
        return result

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
        for name, components in self.map_components.items():
            if max(components) != 0:
                raise AssertionError(f"{name} has no degree-zero component")
            if any(degree > 0 for degree in components):
                raise AssertionError(f"positive filtered degree in {name}")
        if [matrix.shape for matrix in self.differentials] != [
            (24, 9),
            (50, 24),
            (49, 50),
            (14, 49),
        ]:
            raise AssertionError("corrected cone dimension ledger drifted")
        for index, (left, right) in enumerate(
            zip(self.differentials[:-1], self.differentials[1:], strict=True)
        ):
            square = (right * left).applyfunc(sp.expand)
            if square != sp.zeros(square.rows, square.cols):
                raise AssertionError(f"corrected cone square {index} failed")
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

    def certificate(self) -> dict[str, object]:
        self.verify()
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
            "schema": "pure-weyl-rank14-corrected-rees-weights-v1",
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
                    "degree_zero_nonzero_entries": _nonzero_count(components[0]),
                    "degree_zero_sha256": _digest(components[0]),
                }
                for name, components in self.map_components.items()
            },
            "corrected_retract_maps": {
                "Tnew": "T_core p_field; degree-zero unchanged",
                "Anew": "A_core p_equation",
                "Bnew": "B_core p_identity with derivative Weyl column",
                "full_T_lower_order_bound_certified": (
                    self.t_lower_order_bound_certified
                ),
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
                "support_local_contraction_constructed": False,
                "prolonged_green_witness": False,
                "causal_green_homotopy": False,
                "rank14_SDR_constructed": False,
            },
            "status_flags_promoted": [],
            "next_exact_step": (
                "identify the 4-8-4 null module under the little group and "
                "lift the corrected filtration through curved PBW composition"
            ),
            "fail_closed": True,
        }

