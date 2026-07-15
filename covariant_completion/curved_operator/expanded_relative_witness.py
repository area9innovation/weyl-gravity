"""Complete invariant-incidence audit for relative mapping-cylinder witnesses.

This is deliberately a principal, representation-theoretic diagnostic.  It
enumerates every degree-minus-one odd-cotangent pair in the exact sixteen
block mapping cylinder and allows the corresponding map to range over the
complete ``SO(3)``-invariant Hom space.

The audit finds three two-pair incidences which make reciprocal saddles in
all four auxiliary degrees.  It also proves a narrowly scoped obstruction:
if the two central auxiliary diagonal symbols are demoted completely and
one relies on the curvature diagonals plus arbitrary invariant relative
couplings, the temporal principal matrix has rank at most 113 of 116.  The
missing three directions are rotation scalars.  Thus a successful expanded
witness must retain/prolong a three-scalar central auxiliary block; this is
not a no-go for such a witness or for Green hyperbolicity.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations

from covariant_completion.minimal_witness.formal_operators import (
    OperatorPolynomial,
)
from covariant_completion.curved_retract.curvature_mapping_cylinder_kernel import (
    BLOCK_DEGREES,
    BLOCK_NAMES,
    CurvatureMappingCylinderKernel,
    SIZE,
    _add,
    _multiply,
)

from .relative_saddle_witness import (
    ADJOINT_RELATIVE_PAIRS,
    _cyclic_defect,
    _relative_pair_matrix,
)


# Multiplicities of spin 0, 1 and 2 irreducibles in the cylinder SO(3)
# decomposition.  Dimensions are recovered with weights 1,3,5.
SO3_MULTIPLICITIES = (
    (3, 2, 0),  # G_aux: two spacetime vectors plus one scalar
    (5, 3, 2),  # M_aux: two symmetric tensors plus one vector
    (5, 3, 2),
    (3, 2, 0),
    (0, 2, 4),  # U=(E,B,A,C,x,y)
    (2, 6, 4),  # Eq=26 evolution plus 14 constraints
    (2, 4, 0),  # Id=(q,r,a,c,s,t)
    (0, 2, 4),
    (2, 6, 4),
    (2, 4, 0),
    (2, 4, 0),
    (2, 6, 4),
    (0, 2, 4),
    (2, 4, 0),
    (2, 6, 4),
    (0, 2, 4),
)
IRREP_DIMENSIONS = (1, 3, 5)
AUXILIARY_NODES = (0, 1, 2, 3)


def _dimension(multiplicities: tuple[int, int, int]) -> int:
    return sum(a * b for a, b in zip(multiplicities, IRREP_DIMENSIONS, strict=True))


def _hom_dimension(source: int, target: int) -> int:
    return sum(
        a * b
        for a, b in zip(
            SO3_MULTIPLICITIES[source], SO3_MULTIPLICITIES[target], strict=True
        )
    )


def _nonzero_edges(matrix: list[list[OperatorPolynomial]]) -> set[tuple[int, int]]:
    zero = OperatorPolynomial.zero()
    return {
        (column, row)
        for row in range(SIZE)
        for column in range(SIZE)
        if matrix[row][column] != zero
    }


def _rank_through_partners(auxiliary: int, partners: tuple[int, ...]) -> int:
    available = tuple(
        sum(SO3_MULTIPLICITIES[node][spin] for node in partners)
        for spin in range(3)
    )
    return sum(
        IRREP_DIMENSIONS[spin]
        * min(SO3_MULTIPLICITIES[auxiliary][spin], available[spin])
        for spin in range(3)
    )


@dataclass(frozen=True)
class ExpandedRelativeWitnessAudit:
    """Exact all-pair incidence and central scalar-rank obstruction."""

    pair_edges: tuple[frozenset[tuple[int, int]], ...]
    invariant_hom_dimensions: tuple[int, ...]
    reciprocal_partners: tuple[tuple[int, ...], ...]
    minimal_global_saddles: tuple[tuple[int, int], ...]
    cross_rank_bounds: tuple[int, ...]

    @staticmethod
    def build() -> "ExpandedRelativeWitnessAudit":
        kernel = CurvatureMappingCylinderKernel.build()
        pair_edges: list[frozenset[tuple[int, int]]] = []
        hom_dimensions: list[int] = []
        for pair_index, (primary, _) in enumerate(ADJOINT_RELATIVE_PAIRS):
            witness, _ = _relative_pair_matrix(pair_index, kernel.pairing)
            if any(
                entry != OperatorPolynomial.zero()
                for row in _cyclic_defect(witness, kernel.pairing)
                for entry in row
            ):
                raise AssertionError("relative pair lost odd BV cyclicity")
            operator = _add(
                _multiply(kernel.split_differential, witness),
                _multiply(witness, kernel.split_differential),
            )
            pair_edges.append(frozenset(_nonzero_edges(operator)))
            hom_dimensions.append(_hom_dimension(primary[1], primary[0]))

        def partners(selected: tuple[int, ...], auxiliary: int) -> tuple[int, ...]:
            edges = set().union(*(pair_edges[index] for index in selected))
            return tuple(
                node
                for node in range(4, SIZE)
                if BLOCK_DEGREES[node] == BLOCK_DEGREES[auxiliary]
                and (auxiliary, node) in edges
                and (node, auxiliary) in edges
            )

        minimal: list[tuple[int, int]] = []
        for selected in combinations(range(len(pair_edges)), 2):
            if all(partners(selected, auxiliary) for auxiliary in AUXILIARY_NODES):
                minimal.append(selected)
        all_selected = tuple(range(len(pair_edges)))
        reciprocal = tuple(partners(all_selected, auxiliary) for auxiliary in AUXILIARY_NODES)
        result = ExpandedRelativeWitnessAudit(
            pair_edges=tuple(pair_edges),
            invariant_hom_dimensions=tuple(hom_dimensions),
            reciprocal_partners=reciprocal,
            minimal_global_saddles=tuple(minimal),
            cross_rank_bounds=tuple(
                _rank_through_partners(auxiliary, reciprocal[auxiliary])
                for auxiliary in AUXILIARY_NODES
            ),
        )
        result.verify()
        return result

    def verify(self) -> None:
        if len(self.pair_edges) != 9:
            raise AssertionError("relative-pair coverage is incomplete")
        if self.invariant_hom_dimensions != (4, 18, 4, 36, 14, 14, 22, 36, 14):
            raise AssertionError("complete invariant Hom dimensions drifted")
        if sum(self.invariant_hom_dimensions) != 162:
            raise AssertionError("relative invariant parameter count drifted")
        if self.minimal_global_saddles != ((1, 6), (1, 7), (2, 7)):
            raise AssertionError("global reciprocal saddle classification drifted")
        expected_partners = (
            (10, 14),
            (4, 11, 15),
            (5, 7, 12),
            (6, 8),
        )
        if self.reciprocal_partners != expected_partners:
            raise AssertionError("complete reciprocal partner ledger drifted")
        if self.cross_rank_bounds != (9, 21, 21, 9):
            raise AssertionError("invariant cross-rank bounds drifted")
        if any(_dimension(rep) != size for rep, size in zip(
            SO3_MULTIPLICITIES,
            (9, 24, 24, 9, 26, 40, 14, 26, 40, 14, 14, 40, 26, 14, 40, 26),
            strict=True,
        )):
            raise AssertionError("SO(3) decomposition does not recover block ranks")

    def certificate(self) -> dict[str, object]:
        self.verify()
        central_curvature_dimension = sum(
            _dimension(SO3_MULTIPLICITIES[node])
            for node in self.reciprocal_partners[1]
        )
        central_total = 24 + central_curvature_dimension
        central_rank_bound = central_curvature_dimension + self.cross_rank_bounds[1]
        return {
            "schema": "pure-weyl-expanded-relative-witness-incidence-v1",
            "complete_relative_space": {
                "odd_adjoint_pairs": 9,
                "directed_entries": 18,
                "SO3_invariant_parameter_dimension": sum(self.invariant_hom_dimensions),
                "pairwise_Hom_dimensions": list(self.invariant_hom_dimensions),
                "each_pair_odd_BV_cyclic": True,
                "incidence_linear_combinations_exhausted": True,
                "SO3_family_scope": (
                    "complete relative to the declared block multiplicities"
                ),
                "rotation_generator_commutants_constructed": False,
            },
            "minimal_all_auxiliary_degree_reciprocal_saddles": {
                "pair_sets_zero_based": [list(pair) for pair in self.minimal_global_saddles],
                "pair_sets": ["1+6", "1+7", "2+7"],
                "balanced_relative_order_conditions": {
                    "1+6": "ord(R1)+ord(R6)=1",
                    "1+7": "ord(R1)+ord(R7)=2",
                    "2+7": "ord(R2)+ord(R7)=1",
                },
                "constructive_candidate": (
                    "pairs 1+6 with orders (0,1), or pairs 2+7 with orders (0,1), "
                    "give reciprocal order-(1,2) central couplings compatible with "
                    "auxiliary order 2 and curvature order 1"
                ),
            },
            "complete_reciprocal_partner_ledger": {
                BLOCK_NAMES[auxiliary]: [BLOCK_NAMES[node] for node in partners]
                for auxiliary, partners in zip(
                    AUXILIARY_NODES, self.reciprocal_partners, strict=True
                )
            },
            "invariant_cross_rank": {
                "auxiliary_block_dimensions": [9, 24, 24, 9],
                "maximum_ranks_through_all_reciprocal_curvature_partners": list(
                    self.cross_rank_bounds
                ),
                "defects": [0, 3, 3, 0],
                "central_missing_representation": "three copies of spin 0",
            },
            "scoped_temporal_no_go": {
                "assumption": (
                    "the central 24-component auxiliary diagonal is entirely "
                    "subprincipal; curvature diagonals are temporally invertible; "
                    "all relative maps are arbitrary SO(3)-invariant maps"
                ),
                "central_block_dimension": central_total,
                "central_temporal_rank_upper_bound": central_rank_bound,
                "central_temporal_rank_defect_lower_bound": central_total - central_rank_bound,
                "invertible_support_local_block_change_can_repair_rank": False,
                "reason": "left/right local invertible principal transformations preserve rank",
                "positive_temporal_symmetrizer_possible_under_assumption": False,
            },
            "constructive_boundary": (
                "the complete relative incidence does expose lower-order two-pair "
                "candidates, but every successful witness must retain or locally "
                "prolong the three central scalar directions; coefficient tables, "
                "characteristics and a symmetrizer remain to be solved"
            ),
            "scope": (
                "exact incidence/rank theorem relative to the declared SO(3) "
                "multiplicity ledger, and a no-go only for demoting the complete "
                "central auxiliary diagonal; an independent coefficientwise "
                "rotation-generator commutant certificate remains open"
            ),
            "prolonged_green_witness": False,
            "curvature_causal_green_operators": False,
            "causal_green_homotopy": False,
            "warranted_atomic_flags": [],
            "status_flags_promoted": [],
            "fail_closed": True,
        }
