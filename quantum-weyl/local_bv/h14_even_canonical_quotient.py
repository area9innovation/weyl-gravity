"""Orbit-first even AFN0 ``H^{1,4}`` candidate quotient.

This module deliberately does not enumerate the ambient 2.86-billion-graph
lower-form space.  It closes the two mixed top-form signatures left open by
the reverse-coverage ledger and assembles the smallest projected relative
complex that can decide the even Weyl-ghost candidates.
"""

from __future__ import annotations

from fractions import Fraction
from functools import lru_cache

from .algebra import canonical_sha256
from .basis_exhaustiveness import BasisExhaustivenessProof, grading_signature_manifest
from .curvature import (
    RIEMANN,
    bianchi_relation,
    differential_bianchi_relation,
    pair_partitions,
)
from .four_dimensional import schouten_endpoint_selections
from .quotient import RelationQuotient
from .relative_cohomology import SparseMatrix
from .tensors import (
    TensorExpression,
    TensorFactor,
    TensorMonomial,
    total_covariant_derivative,
)
from .triviality import box_r_triviality_analysis
from .weyl_target import WEYL_GHOST


TOP_BASIS = (
    "ANOM_OMEGA_C2",
    "ANOM_OMEGA_E4",
    "ANOM_OMEGA_R2",
    "ANOM_OMEGA_BOX_R",
    "MIXED_R_BOX_OMEGA",
    "MIXED_RICCI_HESS_OMEGA",
    "MIXED_GRAD_R_GRAD_OMEGA",
)

INCOMING_Q_BASIS = ("R_SQUARED",)
INCOMING_DH_BASIS = (
    "CURRENT_R_GRAD_OMEGA",
    "CURRENT_RICCI_GRAD_OMEGA",
    "CURRENT_OMEGA_GRAD_R",
)


def _fraction_payload(value: Fraction | int) -> dict[str, int]:
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def _vector_payload(vector: tuple[Fraction, ...]) -> list[dict[str, int]]:
    return [_fraction_payload(value) for value in vector]


def _matrix_payload(matrix: SparseMatrix) -> dict[str, object]:
    return matrix.canonical_payload()


def _mixed_signature(tensor_derivatives: int, ghost_derivatives: int) -> dict[str, object]:
    rows = grading_signature_manifest(1, "even")["refined_grading_signatures"]
    matches = [
        row
        for row in rows
        if row["curvature_count"] == 1
        and row["tensor_derivative_count"] == tensor_derivatives
        and row["ghost_derivative_order"] == ghost_derivatives
    ]
    if len(matches) != 1:
        raise AssertionError("the requested mixed signature is not unique")
    return matches[0]


def _mixed_monomial(
    pairing: tuple[tuple[int, int], ...], *, differentiated_curvature: bool
) -> TensorMonomial:
    if sorted(position for pair in pairing for position in pair) != list(range(6)):
        raise ValueError("a mixed pairing must cover six slots exactly once")
    labels = [0] * 6
    for index, (left, right) in enumerate(pairing):
        labels[left] = labels[right] = index
    if differentiated_curvature:
        factors = (
            TensorFactor(RIEMANN, tuple(labels[:4]), (labels[4],)),
            TensorFactor(WEYL_GHOST, (), (labels[5],)),
        )
    else:
        factors = (
            TensorFactor(RIEMANN, tuple(labels[:4])),
            TensorFactor(WEYL_GHOST, (), tuple(labels[4:6])),
        )
    return TensorMonomial(factors)


def _unique_relations(
    raw: tuple[TensorMonomial, ...], *, differentiated_curvature: bool
) -> tuple[TensorExpression, ...]:
    relations: dict[str, TensorExpression] = {}
    for monomial in raw:
        candidates = [bianchi_relation(monomial, 0)]
        if differentiated_curvature:
            candidates.append(differential_bianchi_relation(monomial, 0))
        for relation in candidates:
            if relation:
                relations.setdefault(relation.canonical_hash(), relation)
    return tuple(relations[digest] for digest in sorted(relations))


def _orbit_sector(*, differentiated_curvature: bool) -> dict[str, object]:
    pairings = tuple(pair_partitions(tuple(range(6))))
    raw = tuple(
        _mixed_monomial(pairing, differentiated_curvature=differentiated_curvature)
        for pairing in pairings
    )
    canonical = {
        monomial
        for raw_monomial in raw
        for sign, monomial in (raw_monomial.canonicalize(),)
        if sign and monomial is not None
    }
    basis = tuple(sorted(canonical, key=TensorMonomial.sort_key))
    relations = _unique_relations(
        raw, differentiated_curvature=differentiated_curvature
    )
    quotient = RelationQuotient(basis, relations)
    # A scalar five-index Schouten relation requires five contraction pairs.
    # These six-slot sectors have only three, so the exhaustive selector is
    # empty rather than merely unimplemented.
    schouten_candidates = sum(
        len(schouten_endpoint_selections(pairing)) for pairing in pairings
    )
    if schouten_candidates:
        raise AssertionError("unexpected four-dimensional Schouten carrier")
    return {
        "signature": _mixed_signature(
            1 if differentiated_curvature else 0,
            1 if differentiated_curvature else 2,
        ),
        "raw_pairings": pairings,
        "raw_pairing_count": len(pairings),
        "canonical_basis": basis,
        "canonical_orbit_count": len(basis),
        "relations": relations,
        "relation_rank": quotient.relation_rank,
        "quotient_dimension": quotient.quotient_dimension,
        "quotient": quotient,
        "signed_identical_factor_permutations": (
            "VACUOUS_NO_REPEATED_TENSOR_FACTOR"
        ),
        "grassmann_factor_sign": "PLUS_ONE_SINGLE_WEYL_GHOST_FACTOR",
        "algebraic_bianchi_status": "EXHAUSTIVE_GENERATED",
        "differential_bianchi_status": (
            "EXHAUSTIVE_GENERATED"
            if differentiated_curvature
            else "NOT_APPLICABLE_UNDIFFERENTIATED_CURVATURE"
        ),
        "four_dimensional_antisymmetrization_status": (
            "EXHAUSTIVE_EMPTY_FEWER_THAN_FIVE_CONTRACTION_PAIRS"
        ),
        "four_dimensional_antisymmetrization_candidate_count": 0,
    }


def _named_monomials() -> dict[str, TensorMonomial]:
    return {
        "MIXED_R_BOX_OMEGA": TensorMonomial(
            (
                TensorFactor(RIEMANN, (0, 1, 0, 1)),
                TensorFactor(WEYL_GHOST, (), (2, 2)),
            )
        ),
        "MIXED_RICCI_HESS_OMEGA": TensorMonomial(
            (
                TensorFactor(RIEMANN, (0, 1, 0, 2)),
                TensorFactor(WEYL_GHOST, (), (1, 2)),
            )
        ),
        "MIXED_DIV_RICCI_GRAD_OMEGA": TensorMonomial(
            (
                TensorFactor(RIEMANN, (0, 1, 1, 2), (0,)),
                TensorFactor(WEYL_GHOST, (), (2,)),
            )
        ),
        "MIXED_GRAD_R_GRAD_OMEGA": TensorMonomial(
            (
                TensorFactor(RIEMANN, (0, 1, 0, 1), (2,)),
                TensorFactor(WEYL_GHOST, (), (2,)),
            )
        ),
        "ANOM_OMEGA_BOX_R": TensorMonomial(
            (
                TensorFactor(WEYL_GHOST, ()),
                TensorFactor(RIEMANN, (0, 1, 0, 1), (2, 2)),
            )
        ),
    }


def _current_divergences() -> tuple[TensorExpression, ...]:
    currents = (
        (
            TensorMonomial(
                (
                    TensorFactor(RIEMANN, (1, 2, 1, 2)),
                    TensorFactor(WEYL_GHOST, (), (0,)),
                )
            ),
            0,
        ),
        (
            TensorMonomial(
                (
                    TensorFactor(RIEMANN, (0, 1, 0, 2)),
                    TensorFactor(WEYL_GHOST, (), (2,)),
                )
            ),
            1,
        ),
        (
            TensorMonomial(
                (
                    TensorFactor(WEYL_GHOST, ()),
                    TensorFactor(RIEMANN, (1, 2, 1, 2), (0,)),
                )
            ),
            0,
        ),
    )
    return tuple(
        total_covariant_derivative(current, free_index)
        for current, free_index in currents
    )


def _mixed_coordinates(
    expression: TensorExpression,
    hessian: dict[str, object],
    gradient: dict[str, object],
) -> tuple[Fraction, Fraction, Fraction, Fraction]:
    """Coordinates ``(omega BoxR, R Boxomega, Ric Hessomega, gradR gradomega)``."""

    named = _named_monomials()
    h_basis = tuple(hessian["canonical_basis"])
    h_position = {monomial: index for index, monomial in enumerate(h_basis)}
    x = named["ANOM_OMEGA_BOX_R"].canonicalize()[1]
    if x is None:
        raise AssertionError("omega Box R canonicalized to zero")
    x_coefficient = Fraction()
    h_vector = [Fraction() for _ in h_basis]
    g_expression = TensorExpression()
    for monomial, coefficient in expression.terms.items():
        if monomial == x:
            x_coefficient += coefficient
        elif monomial in h_position:
            h_vector[h_position[monomial]] += coefficient
        else:
            g_expression = g_expression + coefficient * TensorExpression.monomial(monomial)
    g_coordinate = tuple(gradient["quotient"].free_coordinates(g_expression))
    if len(g_coordinate) != 1:
        raise AssertionError("gradient quotient did not reduce to one carrier")
    h_named = (
        named["MIXED_R_BOX_OMEGA"].canonicalize()[1],
        named["MIXED_RICCI_HESS_OMEGA"].canonicalize()[1],
    )
    if any(monomial is None for monomial in h_named):
        raise AssertionError("named Hessian carrier canonicalized to zero")
    h_coordinates = tuple(h_vector[h_position[monomial]] for monomial in h_named)
    return (x_coefficient, *h_coordinates, g_coordinate[0])


def _independent_columns(matrix: SparseMatrix) -> tuple[tuple[Fraction, ...], ...]:
    columns = matrix.columns()
    selected: list[tuple[Fraction, ...]] = []
    rank = 0
    for column in columns:
        candidate_columns = (*selected, column)
        candidate = SparseMatrix.from_dense(tuple(zip(*candidate_columns)))
        candidate_rank = candidate.rank()
        if candidate_rank > rank:
            selected.append(column)
            rank = candidate_rank
    return tuple(selected)


def _pair(left: tuple[Fraction, ...], right: tuple[Fraction, ...]) -> Fraction:
    return sum((a * b for a, b in zip(left, right)), Fraction())


def _wz_obstruction_analysis() -> dict[str, object]:
    """Reduce the sole even Weyl-consistency defect modulo ``d_h`` exactly."""

    current = TensorMonomial(
        (
            TensorFactor(WEYL_GHOST, ()),
            TensorFactor(RIEMANN, (1, 2, 1, 2)),
            TensorFactor(WEYL_GHOST, (), (0,)),
        )
    )
    divergence = total_covariant_derivative(current, 0)
    omega_r_box_omega = TensorMonomial(
        (
            TensorFactor(WEYL_GHOST, ()),
            TensorFactor(RIEMANN, (1, 2, 1, 2)),
            TensorFactor(WEYL_GHOST, (), (0, 0)),
        )
    )
    omega_grad_r_grad_omega = TensorMonomial(
        (
            TensorFactor(WEYL_GHOST, ()),
            TensorFactor(RIEMANN, (1, 2, 1, 2), (0,)),
            TensorFactor(WEYL_GHOST, (), (0,)),
        )
    )
    named = {}
    for label, monomial in (
        ("OMEGA_R_BOX_OMEGA", omega_r_box_omega),
        ("OMEGA_GRAD_R_GRAD_OMEGA", omega_grad_r_grad_omega),
    ):
        sign, canonical = monomial.canonicalize()
        if not sign or canonical is None:
            raise AssertionError(f"Wess-Zumino carrier vanished: {label}")
        named[label] = (sign, canonical)
    basis = tuple(
        sorted({canonical for _, canonical in named.values()}, key=TensorMonomial.sort_key)
    )
    if len(basis) != 2 or len(divergence.terms) != 2:
        raise AssertionError("Wess-Zumino target basis drifted")
    quotient = RelationQuotient(basis, (divergence,))
    if quotient.relation_rank != 1 or quotient.quotient_dimension != 1:
        raise AssertionError("Wess-Zumino d_h quotient is not one-dimensional")
    q_expression = 12 * TensorExpression.monomial(omega_r_box_omega)
    reduced = quotient.free_coordinates(q_expression)
    if len(reduced) != 1 or not reduced[0]:
        raise AssertionError("omega R^2 consistency defect reduced to zero")
    basis_position = {monomial: index for index, monomial in enumerate(basis)}
    q_matrix = SparseMatrix(
        len(basis),
        len(TOP_BASIS),
        {
            (
                basis_position[named["OMEGA_R_BOX_OMEGA"][1]],
                TOP_BASIS.index("ANOM_OMEGA_R2"),
            ): Fraction(12) * named["OMEGA_R_BOX_OMEGA"][0]
        },
    )
    dh_matrix = SparseMatrix(
        len(basis),
        1,
        {
            (basis_position[monomial], 0): coefficient
            for monomial, coefficient in divergence.terms.items()
        },
    )
    return {
        "target_basis": basis,
        "current": current,
        "divergence": divergence,
        "quotient": quotient,
        "q_matrix": q_matrix,
        "dh_matrix": dh_matrix,
        "reduced_obstruction_coefficient": reduced[0],
        "grassmann_square_term": (
            "ZERO_BY_SIGNED_IDENTICAL_GRAD_OMEGA_FACTOR_EXCHANGE"
        ),
    }


@lru_cache(maxsize=1)
def h14_even_canonical_quotient_analysis() -> dict[str, object]:
    """Return the exact completed even AFN0 candidate quotient."""

    hessian = _orbit_sector(differentiated_curvature=False)
    gradient = _orbit_sector(differentiated_curvature=True)
    if not (
        hessian["raw_pairing_count"] == gradient["raw_pairing_count"] == 15
        and hessian["canonical_orbit_count"] == gradient["canonical_orbit_count"] == 2
        and hessian["quotient_dimension"] == 2
        and gradient["quotient_dimension"] == 1
    ):
        raise AssertionError("mixed orbit quotient dimensions drifted")

    named = _named_monomials()
    gradient_relation = gradient["quotient"].free_coordinates(
        TensorExpression.monomial(named["MIXED_DIV_RICCI_GRAD_OMEGA"])
    )
    gradient_generator = gradient["quotient"].free_coordinates(
        TensorExpression.monomial(named["MIXED_GRAD_R_GRAD_OMEGA"])
    )
    if gradient_relation != tuple(Fraction(-1, 2) * value for value in gradient_generator):
        raise AssertionError("contracted differential Bianchi coefficient drifted")

    divergences = _current_divergences()
    ibp_coordinates = tuple(
        _mixed_coordinates(expression, hessian, gradient)
        for expression in divergences
    )
    expected_ibp = (
        (Fraction(0), Fraction(1), Fraction(0), Fraction(1)),
        (Fraction(0), Fraction(0), Fraction(1), Fraction(1, 2)),
        (Fraction(1), Fraction(0), Fraction(0), Fraction(1)),
    )
    if ibp_coordinates != expected_ibp:
        raise AssertionError("generated integration-by-parts matrix drifted")

    top_position = {label: index for index, label in enumerate(TOP_BASIS)}
    q_entries = {
        (top_position["MIXED_R_BOX_OMEGA"], 0): Fraction(-12)
    }
    q_matrix = SparseMatrix(len(TOP_BASIS), len(INCOMING_Q_BASIS), q_entries)
    # The generated current coordinates are ordered X, H1, H2, G.
    mixed_rows = tuple(
        top_position[label]
        for label in (
            "ANOM_OMEGA_BOX_R",
            "MIXED_R_BOX_OMEGA",
            "MIXED_RICCI_HESS_OMEGA",
            "MIXED_GRAD_R_GRAD_OMEGA",
        )
    )
    dh_matrix = SparseMatrix(
        len(TOP_BASIS),
        len(INCOMING_DH_BASIS),
        {
            (mixed_rows[row], column): coefficient
            for column, coordinates in enumerate(ibp_coordinates)
            for row, coefficient in enumerate(coordinates)
            if coefficient
        },
    )
    boundary_matrix = SparseMatrix(
        len(TOP_BASIS),
        len(INCOMING_Q_BASIS) + len(INCOMING_DH_BASIS),
        {
            **q_matrix.entries,
            **{
                (row, column + len(INCOMING_Q_BASIS)): coefficient
                for (row, column), coefficient in dh_matrix.entries.items()
            },
        },
    )
    if boundary_matrix.rank() != 4:
        raise AssertionError("incoming relative boundary rank drifted")

    # After the complete intrinsic descendants are admitted, the only missing
    # direction in the seven-dimensional top carrier is omega R^2.  Reduce
    # its exact Q image against the only admissible ghost-two current.
    wz = _wz_obstruction_analysis()
    obstruction = SparseMatrix(
        1,
        len(TOP_BASIS),
        {
            (0, top_position["ANOM_OMEGA_R2"]): wz[
                "reduced_obstruction_coefficient"
            ]
        },
    )
    if obstruction.rank() != 1 or len(obstruction.nullspace()) != 6:
        raise AssertionError("Wess-Zumino closure kernel drifted")
    if obstruction.compose(boundary_matrix).entries:
        raise AssertionError("a relative boundary failed the closure obstruction")

    boundary_columns = _independent_columns(boundary_matrix)
    representatives = (
        tuple(Fraction(int(index == top_position["ANOM_OMEGA_C2"])) for index in range(len(TOP_BASIS))),
        tuple(Fraction(int(index == top_position["ANOM_OMEGA_E4"])) for index in range(len(TOP_BASIS))),
    )
    closure_span = SparseMatrix.from_dense(
        tuple(zip(*(boundary_columns + representatives)))
    )
    if closure_span.rank() != 6:
        raise AssertionError("projected closure span does not fill the obstruction kernel")
    quotient_dimension = closure_span.rank() - len(boundary_columns)
    if quotient_dimension != 2:
        raise AssertionError("even AFN0 candidate quotient dimension drifted")

    dual_witnesses = representatives
    for representative, witness in zip(representatives, dual_witnesses):
        if any(_pair(column, witness) for column in boundary_columns):
            raise AssertionError("dual witness does not annihilate boundaries")
        if _pair(representative, witness) != 1:
            raise AssertionError("dual witness normalization failed")

    top_manifest = {
        "basis": list(TOP_BASIS),
        "derivation": {
            "quadratic_curvature_ghost_sector": (
                "three four-dimensional scalar curvature-square carriers: C2, E4, R2"
            ),
            "single_curvature_two_tensor_derivatives": "omega BoxR modulo differential Bianchi",
            "pending_mixed_hessian_sector": "two orbit-first carriers",
            "pending_mixed_gradient_sector": "one carrier after differential Bianchi",
        },
    }
    orbit_manifest = {
        "hessian": {
            "raw_pairing_count": hessian["raw_pairing_count"],
            "canonical_orbit_count": hessian["canonical_orbit_count"],
            "quotient_dimension": hessian["quotient_dimension"],
        },
        "gradient": {
            "raw_pairing_count": gradient["raw_pairing_count"],
            "canonical_orbit_count": gradient["canonical_orbit_count"],
            "differential_bianchi_rank": gradient["relation_rank"],
            "quotient_dimension": gradient["quotient_dimension"],
        },
        "raw_graphs_materialized": 30,
        "ambient_raw_graphs_materialized": 0,
    }
    identity_manifest = {
        "contracted_differential_bianchi": "div_Ricci_grad_omega = -1/2 grad_R_grad_omega in canonical convention",
        "ibp_coordinates": [[_fraction_payload(value) for value in row] for row in ibp_coordinates],
        "q_matrix": _matrix_payload(q_matrix),
        "dh_matrix": _matrix_payload(dh_matrix),
        "closure_obstruction": _matrix_payload(obstruction),
        "outgoing_Q_matrix": _matrix_payload(wz["q_matrix"]),
        "outgoing_dh_matrix": _matrix_payload(wz["dh_matrix"]),
        "outgoing_dh_quotient_dimension": wz["quotient"].quotient_dimension,
        "boundary_rank": boundary_matrix.rank(),
        "closure_rank": closure_span.rank(),
    }
    proof = BasisExhaustivenessProof.create(
        basis_manifest=top_manifest,
        declared_bounds={
            "spacetime_dimension": 4,
            "ghost_number": 1,
            "form_degree": 4,
            "antifield_number": 0,
            "engineering_dimension": 4,
            "parity": "even",
            "ghost_species": "WEYL",
        },
        generator_algebra={
            "top_generators": ["Riemann", "covariant_derivative", "omega", "metric"],
            "lower_form_generators": ["R_squared", *INCOMING_DH_BASIS],
            "universal_diff_completion": "FACTORED_HASH_BOUND_EXISTING_TOWERS",
        },
        grading_solution={
            "coarse_signature_count": 9,
            "refined_signature_count": 5,
            "two_pending_mixed_signatures_resolved": True,
        },
        orbit_enumeration=orbit_manifest,
        identity_quotient=identity_manifest,
        proof_artifact={
            "top_kernel_equals_boundary_plus_representatives": True,
            "boundary_rank": 4,
            "closure_rank": 6,
            "quotient_dimension": quotient_dimension,
            "dual_pairings": [
                _fraction_payload(_pair(representative, witness))
                for representative, witness in zip(representatives, dual_witnesses)
            ],
        },
    )
    proof.verify(expected_basis_manifest_hash=canonical_sha256(top_manifest))

    triviality = box_r_triviality_analysis()
    if triviality["counterterm_coefficient"] != Fraction(-1, 12):
        raise AssertionError("omega Box R primitive coefficient drifted")

    return {
        "top_basis": TOP_BASIS,
        "hessian_sector": hessian,
        "gradient_sector": gradient,
        "contracted_bianchi_coefficient": Fraction(-1, 2),
        "ibp_coordinates": ibp_coordinates,
        "q_matrix": q_matrix,
        "dh_matrix": dh_matrix,
        "boundary_matrix": boundary_matrix,
        "closure_obstruction_matrix": obstruction,
        "wz_obstruction": wz,
        "closure_span_matrix": closure_span,
        "boundary_rank": boundary_matrix.rank(),
        "closure_rank": closure_span.rank(),
        "quotient_dimension": quotient_dimension,
        "representatives": representatives,
        "dual_witnesses": dual_witnesses,
        "basis_exhaustiveness_proof": proof,
        "omega_box_r_primitive_coefficient": triviality["counterterm_coefficient"],
        "analysis_sha256": canonical_sha256(
            {
                "top_manifest": top_manifest,
                "orbit_manifest": orbit_manifest,
                "identity_manifest": identity_manifest,
                "proof": proof.canonical_payload(),
            }
        ),
    }


def canonical_quotient_payload() -> dict[str, object]:
    analysis = h14_even_canonical_quotient_analysis()
    hessian = analysis["hessian_sector"]
    gradient = analysis["gradient_sector"]
    return {
        "result_id": "AFN0_H14_EVEN_CANONICAL_QUOTIENT",
        "result_state": "COMPLETE_AFN0_EVEN_CANDIDATE_QUOTIENT",
        "classical_commit": "UNFROZEN",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "scope_label": "AFN0_ONLY",
        "bounds": {
            "spacetime_dimension": 4,
            "ghost_number": 1,
            "form_degree": 4,
            "antifield_number": 0,
            "engineering_dimension": 4,
            "parity": "even",
            "ghost_species": "WEYL",
        },
        "enumeration_policy": {
            "mode": "ORBIT_FIRST_TWO_PENDING_MIXED_SIGNATURES",
            "ambient_raw_graph_count": 2_860_932_903,
            "ambient_raw_graphs_materialized": 0,
            "target_raw_pairings_materialized": (
                hessian["raw_pairing_count"] + gradient["raw_pairing_count"]
            ),
        },
        "canonical_sectors": [
            {
                "sector_id": "RIEMANN_TIMES_HESSIAN_OMEGA",
                "signature": hessian["signature"],
                "raw_pairing_count": hessian["raw_pairing_count"],
                "signed_symmetry_orbit_count": hessian["canonical_orbit_count"],
                "bianchi_relation_rank": hessian["relation_rank"],
                "canonical_quotient_dimension": hessian["quotient_dimension"],
                "canonical_basis": [
                    monomial.canonical_payload()
                    for monomial in hessian["canonical_basis"]
                ],
                "identity_status": {
                    "signed_identical_factor_permutations": hessian["signed_identical_factor_permutations"],
                    "curvature_bianchi": hessian["algebraic_bianchi_status"],
                    "grassmann_signs": hessian["grassmann_factor_sign"],
                    "four_dimensional_antisymmetrization": hessian["four_dimensional_antisymmetrization_status"],
                },
            },
            {
                "sector_id": "GRAD_RIEMANN_TIMES_GRAD_OMEGA",
                "signature": gradient["signature"],
                "raw_pairing_count": gradient["raw_pairing_count"],
                "signed_symmetry_orbit_count": gradient["canonical_orbit_count"],
                "bianchi_relation_rank": gradient["relation_rank"],
                "canonical_quotient_dimension": gradient["quotient_dimension"],
                "canonical_basis": [
                    monomial.canonical_payload()
                    for monomial in gradient["canonical_basis"]
                ],
                "contracted_differential_bianchi_coefficient": _fraction_payload(
                    analysis["contracted_bianchi_coefficient"]
                ),
                "identity_status": {
                    "signed_identical_factor_permutations": gradient["signed_identical_factor_permutations"],
                    "curvature_bianchi": gradient["algebraic_bianchi_status"],
                    "differential_bianchi": gradient["differential_bianchi_status"],
                    "grassmann_signs": gradient["grassmann_factor_sign"],
                    "four_dimensional_antisymmetrization": gradient["four_dimensional_antisymmetrization_status"],
                },
            },
        ],
        "top_basis": list(analysis["top_basis"]),
        "smallest_relative_sector": {
            "incoming_q_basis": list(INCOMING_Q_BASIS),
            "incoming_dh_basis": list(INCOMING_DH_BASIS),
            "Q_matrix": _matrix_payload(analysis["q_matrix"]),
            "d_h_matrix": _matrix_payload(analysis["dh_matrix"]),
            "combined_boundary_matrix": _matrix_payload(analysis["boundary_matrix"]),
            "closure_obstruction_matrix": _matrix_payload(
                analysis["closure_obstruction_matrix"]
            ),
            "outgoing_Q_matrix": _matrix_payload(
                analysis["wz_obstruction"]["q_matrix"]
            ),
            "outgoing_d_h_matrix": _matrix_payload(
                analysis["wz_obstruction"]["dh_matrix"]
            ),
            "outgoing_target_basis": [
                monomial.canonical_payload()
                for monomial in analysis["wz_obstruction"]["target_basis"]
            ],
            "outgoing_current": analysis["wz_obstruction"][
                "current"
            ].canonical_payload(),
            "outgoing_d_h_quotient_dimension": analysis["wz_obstruction"][
                "quotient"
            ].quotient_dimension,
            "reduced_omega_R2_obstruction_coefficient": _fraction_payload(
                analysis["wz_obstruction"][
                    "reduced_obstruction_coefficient"
                ]
            ),
            "boundary_rank": analysis["boundary_rank"],
            "closure_rank": analysis["closure_rank"],
            "quotient_dimension": analysis["quotient_dimension"],
            "integration_by_parts_coordinates": [
                [_fraction_payload(value) for value in row]
                for row in analysis["ibp_coordinates"]
            ],
        },
        "classes": [
            {
                "representative_id": representative_id,
                "relative_cohomology_status": "NONTRIVIAL",
                "representative_coordinates": _vector_payload(representative),
                "dual_witness_type": "COMPLETE_NONTRIVIALITY_WITNESS",
                "dual_witness_coordinates": _vector_payload(witness),
                "dual_pairing": _fraction_payload(_pair(representative, witness)),
            }
            for representative_id, representative, witness in zip(
                ("ANOM_OMEGA_C2", "ANOM_OMEGA_E4"),
                analysis["representatives"],
                analysis["dual_witnesses"],
            )
        ],
        "exact_classes": [
            {
                "representative_id": "ANOM_OMEGA_BOX_R",
                "relative_cohomology_status": "EXACT",
                "primitive_id": "R_SQUARED",
                "primitive_coefficient": _fraction_payload(
                    analysis["omega_box_r_primitive_coefficient"]
                ),
                "current_id": "CURRENT_R_GRAD_OMEGA_MINUS_OMEGA_GRAD_R",
            }
        ],
        "basis_exhaustiveness_proof": analysis[
            "basis_exhaustiveness_proof"
        ].canonical_payload(),
        "checks": {
            "two_pending_mixed_signatures_resolved": "VERIFIED",
            "orbit_first_no_ambient_expansion": "VERIFIED",
            "curvature_and_differential_bianchi": "VERIFIED",
            "grassmann_signs": "VERIFIED",
            "integration_by_parts": "VERIFIED",
            "four_dimensional_antisymmetrization": "VERIFIED_EXHAUSTIVE_EMPTY",
            "exact_Q_and_d_h_matrices": "VERIFIED",
            "closure_kernel_equals_boundaries_plus_two_classes": "VERIFIED",
            "dual_witnesses_normalized": "VERIFIED",
        },
        "claim_boundary": [
            "This is the complete even Weyl-ghost AFN0 candidate quotient at dimension four.",
            "It does not include antifield-dependent classes or promote the full minimal BV quotient.",
            "It is LOCAL-ALGEBRAIC and is not a D-anomaly, anomaly coefficient, restored QME, residual transfer, or Lorentzian result.",
        ],
        "analysis_sha256": analysis["analysis_sha256"],
    }
