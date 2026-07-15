"""Triangular-Green audit of the fixed-temporal pair-(1,6) branch.

The complete invariant spatial family has an intrinsic polynomial Jordan
chain.  A Jordan chain is not, by itself, an obstruction to Green
hyperbolicity: a triangular biwave system has exactly such a chain and has
two-sided advanced/retarded inverses by finite recursion.

This module locates the chain in the exact aligned 116-square Douglis
symbol.  In the transverse helicity-two basis

``(h22-h33, h23, f22-f33, f23)``

the symbol is the reducing direct summand

``[[q I2, 0], [4 rho^2 I2, q I2]]``.

Thus the certified chain ``a0=2 f23, a1=h23`` is physical, not a gradient
constraint or contractible-cone chain.  The generic triangular inverse

``[[G,0],[-G R G,G]]``

is checked noncommutatively from ``DG=GD=1``.

The calculation also gives the exact boundary of this shortcut.  Splitting
the equation-cotangent rows into their evolution and subsidiary bundles, the
natural ledger is ``(h,f,v,U,F#,C#,U#)``.  Its full principal support graph
has one reciprocal strongly-connected component ``(h,f,C#)`` of rank 34,
plus an open rank-four vector singleton.  The three remaining rank-26
curvature singletons have certified symmetric-hyperbolic diagonals and are
handled by finite recursion once the two open components are inverted.  The
aligned helicity-two projection is
covector dependent and is not a support-local bundle splitting.  No complete
Green witness or Green homotopy is promoted here.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
import hashlib
from typing import Mapping

import sympy as sp

from covariant_completion.minimal_witness.formal_operators import (
    OperatorPolynomial,
)

from .expanded_relative_witness_full_symbol import (
    COMPLETE_RANK,
    ExpandedRelativeFullSymbol,
)


LEDGER = (
    (0, 10, "h"),
    (10, 20, "f"),
    (20, 24, "v"),
    (24, 50, "U"),
    (50, 76, "F_sharp"),
    (76, 90, "C_sharp"),
    (90, 116, "U_sharp"),
)
LEDGER_DIMENSIONS = tuple(stop - start for start, stop, _ in LEDGER)
EXPECTED_EDGES = frozenset(
    {
        (0, 0),
        (5, 0),
        (0, 1),
        (1, 1),
        (5, 1),
        (2, 2),
        (3, 3),
        (0, 4),
        (1, 4),
        (4, 4),
        (0, 5),
        (1, 5),
        (5, 5),
        (6, 6),
    }
)


FormalMatrix = list[list[OperatorPolynomial]]


def _zero(size: int) -> FormalMatrix:
    return [
        [OperatorPolynomial.zero() for _ in range(size)]
        for _ in range(size)
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


def _reduce_diagonal_green(entry: OperatorPolynomial) -> OperatorPolynomial:
    values: dict[tuple[str, ...], Fraction] = {}
    for word, coefficient in entry.terms:
        reduced = word
        changed = True
        while changed:
            changed = False
            for index in range(max(0, len(reduced) - 1)):
                if reduced[index : index + 2] in (("D", "G"), ("G", "D")):
                    reduced = reduced[:index] + reduced[index + 2 :]
                    changed = True
                    break
        values[reduced] = values.get(reduced, Fraction()) + coefficient
    return OperatorPolynomial._from_dict(values)


def _identity_mod_diagonal_green(matrix: FormalMatrix) -> bool:
    size = len(matrix)
    for row in range(size):
        for column in range(size):
            expected = OperatorPolynomial.identity() if row == column else (
                OperatorPolynomial.zero()
            )
            if _reduce_diagonal_green(matrix[row][column]) != expected:
                return False
    return True


def _triangular_pair() -> tuple[FormalMatrix, FormalMatrix]:
    operator = _zero(2)
    operator[0][0] = OperatorPolynomial.atom("D")
    operator[1][0] = OperatorPolynomial.atom("R")
    operator[1][1] = OperatorPolynomial.atom("D")
    green = _zero(2)
    green[0][0] = OperatorPolynomial.atom("G")
    green[1][0] = (
        OperatorPolynomial.atom("G")
        * OperatorPolynomial.atom("R")
        * OperatorPolynomial.atom("G")
    ).scale(-1)
    green[1][1] = OperatorPolynomial.atom("G")
    return operator, green


def _digest(matrix: sp.MatrixBase) -> str:
    return hashlib.sha256(
        sp.srepr(sp.ImmutableSparseMatrix(matrix)).encode("utf-8")
    ).hexdigest()


def _support_edges(matrix: sp.MatrixBase) -> frozenset[tuple[int, int]]:
    edges: set[tuple[int, int]] = set()
    for target, (row_start, row_stop, _) in enumerate(LEDGER):
        for source, (column_start, column_stop, _) in enumerate(LEDGER):
            if any(
                matrix[row, column] != 0
                for row in range(row_start, row_stop)
                for column in range(column_start, column_stop)
            ):
                edges.add((source, target))
    return frozenset(edges)


def _strong_components(
    edges: frozenset[tuple[int, int]], size: int
) -> tuple[tuple[int, ...], ...]:
    """Small exact reachability implementation, deterministic by index."""

    adjacency = {
        node: {target for source, target in edges if source == node}
        for node in range(size)
    }

    def reachable(root: int) -> set[int]:
        seen = {root}
        pending = [root]
        while pending:
            current = pending.pop()
            for target in adjacency[current]:
                if target not in seen:
                    seen.add(target)
                    pending.append(target)
        return seen

    reaches = tuple(reachable(node) for node in range(size))
    remaining = set(range(size))
    result: list[tuple[int, ...]] = []
    while remaining:
        root = min(remaining)
        component = tuple(
            node
            for node in sorted(remaining)
            if node in reaches[root] and root in reaches[node]
        )
        result.append(component)
        remaining.difference_update(component)
    return tuple(result)


def _physical_inclusion_projection() -> tuple[sp.Matrix, sp.Matrix]:
    inclusion = sp.zeros(COMPLETE_RANK, 4)
    # h22-h33, h23, f22-f33, f23.
    inclusion[7, 0] = 1
    inclusion[9, 0] = -1
    inclusion[8, 1] = 1
    inclusion[17, 2] = 1
    inclusion[19, 2] = -1
    inclusion[18, 3] = 1

    projection = sp.zeros(4, COMPLETE_RANK)
    projection[0, 7] = sp.Rational(1, 2)
    projection[0, 9] = -sp.Rational(1, 2)
    projection[1, 8] = 1
    projection[2, 17] = sp.Rational(1, 2)
    projection[2, 19] = -sp.Rational(1, 2)
    projection[3, 18] = 1
    return inclusion, projection


def _nested(mapping: Mapping[str, object], key: str) -> Mapping[str, object]:
    value = mapping.get(key)
    if not isinstance(value, Mapping):
        raise AssertionError(f"missing mapping {key}")
    return value


@dataclass(frozen=True)
class ExpandedRelativeTriangularGreenAudit:
    full_symbol: ExpandedRelativeFullSymbol
    aligned_symbol: sp.Matrix
    physical_inclusion: sp.Matrix
    physical_projection: sp.Matrix
    physical_block: sp.Matrix
    support_edges: frozenset[tuple[int, int]]
    strong_components: tuple[tuple[int, ...], ...]

    @staticmethod
    def build() -> "ExpandedRelativeTriangularGreenAudit":
        full = ExpandedRelativeFullSymbol.build()
        tau, rho = sp.symbols("triangular_green_tau triangular_green_rho")
        aligned = full.symbol((tau, rho, 0, 0), separated=True)
        inclusion, projection = _physical_inclusion_projection()
        q = rho**2 - tau**2
        block = sp.diag(q, q, q, q)
        block[2, 0] = 4 * rho**2
        block[3, 1] = 4 * rho**2
        edges = _support_edges(aligned)
        result = ExpandedRelativeTriangularGreenAudit(
            full_symbol=full,
            aligned_symbol=aligned,
            physical_inclusion=inclusion,
            physical_projection=projection,
            physical_block=block,
            support_edges=edges,
            strong_components=_strong_components(edges, len(LEDGER)),
        )
        result.verify()
        return result

    def verify(self) -> None:
        if self.physical_projection * self.physical_inclusion != sp.eye(4):
            raise AssertionError("physical aligned inclusion has no left inverse")
        if (
            self.aligned_symbol * self.physical_inclusion
            != self.physical_inclusion * self.physical_block
        ):
            raise AssertionError("physical helicity-two subspace is not invariant")
        if (
            self.physical_projection * self.aligned_symbol
            != self.physical_block * self.physical_projection
        ):
            raise AssertionError("physical helicity-two block is not reducing")
        projector = self.physical_inclusion * self.physical_projection
        if projector * self.aligned_symbol != self.aligned_symbol * projector:
            raise AssertionError("aligned physical projector does not commute")
        if self.support_edges != EXPECTED_EDGES:
            raise AssertionError("natural block support graph drifted")
        if self.strong_components != ((0, 1, 5), (2,), (3,), (4,), (6,)):
            raise AssertionError("natural block SCC decomposition drifted")

        operator, green = _triangular_pair()
        if not _identity_mod_diagonal_green(_multiply(operator, green)):
            raise AssertionError("triangular candidate is not a right inverse")
        if not _identity_mod_diagonal_green(_multiply(green, operator)):
            raise AssertionError("triangular candidate is not a left inverse")

    def certificate(
        self,
        *,
        no_go_certificate: Mapping[str, object],
        helicity_certificate: Mapping[str, object],
        tt_factor_certificate: Mapping[str, object],
        green_bridge_certificate: Mapping[str, object],
    ) -> dict[str, object]:
        self.verify()
        if no_go_certificate.get("schema") != (
            "pure-weyl-expanded-relative-r6-first-order-no-go-v1"
        ):
            raise AssertionError("wrong complete-family no-go input")
        intrinsic = _nested(no_go_certificate, "intrinsic_polynomial_Jordan_chain")
        if not intrinsic.get(
            "all_46_parameter_directions_preserve_both_identities"
        ):
            raise AssertionError("parameter-uniform Jordan theorem regressed")
        if helicity_certificate.get("schema") != (
            "pure-weyl-curved-helicity-two-channel-v1"
        ) or not helicity_certificate.get("curved_helicity_two_channel"):
            raise AssertionError("helicity-two quotient certificate unavailable")
        weyl = _nested(helicity_certificate, "linearized_Weyl_symbol")
        if not weyl.get("is_isomorphism"):
            raise AssertionError("Weyl symbol no longer identifies the quotient")
        if tt_factor_certificate.get("schema") != (
            "pure-weyl-tt-local-factorization-v1"
        ) or not tt_factor_certificate.get("reduced_green_hyperbolic"):
            raise AssertionError("reduced TT Green factorization unavailable")
        if green_bridge_certificate.get("schema") != (
            "pure-weyl-prolonged-green-bridge-v1"
        ):
            raise AssertionError("wrong generic triangular Green theorem input")
        if not _nested(
            green_bridge_certificate, "finite_triangular_green_theorem"
        ).get("finite_no_Neumann_convergence_assumption"):
            raise AssertionError("generic triangular Green recursion regressed")

        tau, rho = sp.symbols("triangular_green_tau triangular_green_rho")
        null_block = self.physical_block.subs(tau, rho)
        nilpotent = null_block
        operator, green = _triangular_pair()
        central = self.strong_components[0]
        return {
            "schema": "pure-weyl-expanded-relative-triangular-green-audit-v1",
            "scope": (
                "fixed-temporal pair-(1,6), cyclic -2Pi branch; exact aligned "
                "principal symbol and natural six-bundle filtration"
            ),
            "cross_certificates": {
                "uniform_Jordan_no_go": (
                    "curved_expanded_relative_witness_r6_first_order_no_go.json"
                ),
                "helicity_two": "curved_helicity_two_channel.json",
                "reduced_TT_factorization": "tt_local_factorization.json",
                "generic_triangular_Green_theorem": (
                    "curved_prolonged_green_bridge.json"
                ),
            },
            "aligned_physical_reducing_block": {
                "covector": "(tau,rho,0,0)",
                "basis": ["h22-h33", "h23", "f22-f33", "f23"],
                "formula": "[[q I2,0],[4 rho^2 I2,q I2]]",
                "q": "rho^2-tau^2",
                "inclusion_projection_identity_defect": 0,
                "invariance_defect": 0,
                "coinvariance_defect": 0,
                "commuting_projector_defect": 0,
                "block_sha256": _digest(self.physical_block),
                "null_block_rank": nilpotent.rank(),
                "null_block_square_zero": nilpotent * nilpotent == sp.zeros(4),
                "Jordan_chains": [
                    "h22-h33 -> 4 rho^2 (f22-f33) -> 0",
                    "h23 -> 4 rho^2 f23 -> 0",
                ],
                "uniform_certificate_chain": "a0=2 f23, a1=h23",
                "classification": "physical helicity(+2)+helicity(-2)",
                "linearized_Weyl_symbol_isomorphism": True,
                "entirely_Q_contractible": False,
                "pure_constraint_extension": False,
            },
            "finite_recursive_Green_candidate": {
                "abstract_operator": "[[D,0],[R,D]]",
                "hypothesis": "D G_plus/minus=G_plus/minus D=1",
                "formula": "[[G,0],[-G R G,G]]",
                "left_inverse_defect": 0,
                "right_inverse_defect": 0,
                "same_sided_causal_support": True,
                "support_reason": (
                    "R is differential and finite compositions of same-sided "
                    "Green operators preserve J^+ or J^- support"
                ),
                "interpretation": (
                    "the physical Jordan block is compatible with a biwave/"
                    "triangular Green inverse and is not itself a Green no-go"
                ),
            },
            "natural_bundle_filtration": {
                "ledger": [entry[2] for entry in LEDGER],
                "dimensions": list(LEDGER_DIMENSIONS),
                "directed_edges_source_to_target": [
                    [LEDGER[source][2], LEDGER[target][2]]
                    for source, target in sorted(self.support_edges)
                ],
                "strong_components": [
                    [LEDGER[index][2] for index in component]
                    for component in self.strong_components
                ],
                "central_reciprocal_component": [
                    LEDGER[index][2] for index in central
                ],
                "central_reciprocal_rank": sum(
                    LEDGER_DIMENSIONS[index] for index in central
                ),
                "certified_symmetric_hyperbolic_singletons": [
                    "U",
                    "F_sharp",
                    "U_sharp",
                ],
                "open_singleton_blocks": ["v"],
                "finite_triangular_recursion_closes_curvature_tails_if_open_blocks_inverted": True,
                "central_SCC_Green_inverse_constructed": False,
            },
            "precise_remaining_obstruction": {
                "statement": (
                    "the existing natural six-bundle filtration leaves the "
                    "reciprocal rank-34 (h,f,C#) component and the independent "
                    "rank-four vector singleton; the generic finite triangular "
                    "theorem cannot invert diagonal components for which no "
                    "Green theorem has been supplied"
                ),
                "aligned_helicity_projection_is_covector_dependent": True,
                "pointwise_SO3_invariant_rank_two_projector_exists": False,
                "reason": (
                    "STF2 is an irreducible SO(3) fibre module, so an invariant "
                    "pointwise idempotent has rank zero or five, not two"
                ),
                "support_local_full_bundle_split_constructed": False,
                "coefficientwise_curved_rank34_Green_inverse_constructed": False,
                "coefficientwise_curved_rank4_vector_Green_inverse_constructed": False,
                "QLambda_plus_LambdaQ_verified": False,
            },
            "route_A_conclusion": {
                "Jordan_block_can_be_tolerated_by_generalized_Green_method": True,
                "physical_channel_recursive_formula_exact": True,
                "full_route_A_green_realization_complete": False,
                "next_exact_target": (
                    "split or directly invert the rank-34 reciprocal component "
                    "and rank-four vector singleton without TT/transverse "
                    "projectors, or change incidence so the physical Weyl block "
                    "is an explicit diagonal factor"
                ),
            },
            "prolonged_green_witness": False,
            "curvature_causal_green_operators": False,
            "causal_green_homotopy": False,
            "warranted_atomic_flags": [
                "fixed_temporal_16_physical_Jordan_classified",
                "fixed_temporal_16_physical_triangular_Green_formula",
                "fixed_temporal_16_natural_filtration_audited",
            ],
            "status_flags_promoted": [
                "fixed_temporal_16_physical_Jordan_classified",
                "fixed_temporal_16_physical_triangular_Green_formula",
                "fixed_temporal_16_natural_filtration_audited",
            ],
            "fail_closed": True,
        }
