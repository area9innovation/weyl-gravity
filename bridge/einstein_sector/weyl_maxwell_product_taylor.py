"""Action-derived Weyl--Maxwell Taylor operations on the compact product.

This module constructs the physical Euler rows directly from

    S_WM = integral sqrt(-g) [ (alpha_B / 8) C^2 - F^2 / 4 ]

at the common rational Plebanski--Hacyan background.  It deliberately keeps
the coordinate-product coefficient jets until all derivatives have acted.
No Einstein equation or harmonic branch relation is used to manufacture a
Weyl--Maxwell coefficient.

The first gate exposed here is the physical Taylor tensor.  The complete
Diff x Weyl x U(1) cotangent lift is added only after the physical rows pass
the independent background, trace, Ward and formal-adjoint checks.
"""

from __future__ import annotations

from functools import lru_cache
from itertools import combinations, product

import sympy as sp

from bridge.einstein_sector.product_theta_jet_engine import (
    BZERO,
    JZERO,
    LZERO,
    PAIRS,
    PAIR_INDEX,
    SIN,
    TZERO,
    BilinearOperator,
    LinearOperator,
    TaylorJet,
    TrilinearOperator,
    compose_linear,
    formal_adjoint_matrix,
    graded_complete_bilinear,
    graded_complete_trilinear,
    metric_geometry,
    negative_transpose_bilinear_left,
    negative_transpose_bilinear_right,
    negative_transpose_trilinear_slot,
    sum_jets,
)


ALPHA_B = sp.Integer(3)
MAGNETIC_P = sp.Integer(1)
METRIC_FIELDS = tuple(range(10))
MAXWELL_FIELDS = tuple(range(10, 14))
GHOST_SLICE = tuple(range(0, 6))
FIELD_SLICE = tuple(range(6, 20))
EQUATION_SLICE = tuple(range(20, 34))
IDENTITY_SLICE = tuple(range(34, 40))
TOTAL_ROWS = 40
LAMBDA_GHOST = 4
WEYL_GHOST = 5
PARITIES = (1,) * 6 + (0,) * 14 + (1,) * 14 + (0,) * 6


def _field_strength() -> dict[tuple[int, int], TaylorJet]:
    output: dict[tuple[int, int], TaylorJet] = {}
    for first, second in product(range(4), repeat=2):
        background = sp.S.Zero
        if (first, second) == (2, 3):
            background = SIN * MAGNETIC_P
        elif (first, second) == (3, 2):
            background = -SIN * MAGNETIC_P
        output[(first, second)] = (
            TaylorJet.constant(background)
            + TaylorJet.field(MAXWELL_FIELDS[second]).derivative(first)
            - TaylorJet.field(MAXWELL_FIELDS[first]).derivative(second)
        )
    return output


def _schouten_and_weyl(geometry: dict[str, object]) -> tuple[
    dict[tuple[int, int], TaylorJet],
    dict[tuple[int, int, int, int], TaylorJet],
]:
    metric = geometry["metric"]
    riemann = geometry["riemann"]
    ricci = geometry["ricci"]
    scalar = geometry["scalar"]
    assert isinstance(metric, dict) and isinstance(riemann, dict)
    assert isinstance(ricci, dict) and isinstance(scalar, TaylorJet)
    schouten = {}
    for first, second in PAIRS:
        value = (
            ricci[(first, second)]
            - metric[(first, second)] * scalar.scale(sp.Rational(1, 6))
        ).scale(sp.Rational(1, 2))
        schouten[(first, second)] = value
        schouten[(second, first)] = value

    # C_abcd is a symmetric bilinear form on two-forms.  Building all 256
    # coordinate entries independently is the dominant exact-PBW cost even
    # though only 21 can be independent before the algebraic Bianchi and
    # trace identities.  Construct those 21 entries and expand the indexed
    # interface by exact aliases and signs.
    two_forms = tuple(combinations(range(4), 2))
    canonical_weyl = {}
    for left_index, (first, second) in enumerate(two_forms):
        for third, fourth in two_forms[left_index:]:
            lowered_riemann = sum_jets(
                metric[(first, target)]
                * riemann[(target, second, third, fourth)]
                for target in range(4)
            )
            canonical_weyl[((first, second), (third, fourth))] = (
                lowered_riemann
                - (
                    metric[(first, third)] * schouten[(fourth, second)]
                    - metric[(first, fourth)] * schouten[(third, second)]
                    - metric[(second, third)] * schouten[(fourth, first)]
                    + metric[(second, fourth)] * schouten[(third, first)]
                )
            )

    weyl = {}
    for first, second, third, fourth in product(range(4), repeat=4):
        if first == second or third == fourth:
            weyl[(first, second, third, fourth)] = JZERO
            continue
        left = tuple(sorted((first, second)))
        right = tuple(sorted((third, fourth)))
        sign = (1 if first < second else -1) * (1 if third < fourth else -1)
        if left <= right:
            value = canonical_weyl[(left, right)]
        else:
            value = canonical_weyl[(right, left)]
        weyl[(first, second, third, fourth)] = value.scale(sign)
    return schouten, weyl


def _bach_lower(geometry: dict[str, object]) -> dict[tuple[int, int], TaylorJet]:
    schouten, weyl = _schouten_and_weyl(geometry)
    return _bach_from_components(geometry, schouten, weyl)


def _bach_from_components(
    geometry: dict[str, object],
    schouten: dict[tuple[int, int], TaylorJet],
    weyl: dict[tuple[int, int, int, int], TaylorJet],
) -> dict[tuple[int, int], TaylorJet]:
    """Contract the Bach tensor from already-derived exact components.

    Keeping this contraction separate makes the expensive, deterministic
    action derivation checkpointable during Tier-2 production.  The exported
    certificate still comes from a fresh end-to-end build and is replayed
    independently from its serialized PBW tables.
    """

    divergence_cotton = _divergence_cotton(
        geometry,
        _cotton(_first_schouten(geometry, schouten)),
    )
    algebraic = _schouten_weyl_contraction(geometry, schouten, weyl)
    output = {}
    for first, second in PAIRS:
        value = divergence_cotton[(first, second)] + algebraic[(first, second)]
        output[(first, second)] = value
        output[(second, first)] = value
    return output


def _first_schouten(
    geometry: dict[str, object],
    schouten: dict[tuple[int, int], TaylorJet],
) -> dict[tuple[int, int, int], TaylorJet]:
    gamma = geometry["connection"]
    assert isinstance(gamma, dict)
    first_schouten = {}
    for axis in range(4):
        for first, second in PAIRS:
            value = schouten[(first, second)].derivative(axis) - sum_jets(
                gamma[(replacement, axis, first)]
                * schouten[(replacement, second)]
                + gamma[(replacement, axis, second)]
                * schouten[(first, replacement)]
                for replacement in range(4)
            )
            first_schouten[(axis, first, second)] = value
            first_schouten[(axis, second, first)] = value
    return first_schouten


def _cotton(
    first_schouten: dict[tuple[int, int, int], TaylorJet],
) -> dict[tuple[int, int, int], TaylorJet]:
    # Form the Cotton difference before differentiating again.  Expanding the
    # two second-Schouten terms separately postpones an exact cancellation and
    # causes catastrophic trilinear PBW expression swell.
    cotton = {}
    for second in range(4):
        for inner in range(4):
            cotton[(inner, inner, second)] = JZERO
        for inner, first in combinations(range(4), 2):
            value = first_schouten[(inner, first, second)] - first_schouten[
                (first, second, inner)
            ]
            cotton[(inner, first, second)] = value
            cotton[(first, inner, second)] = -value
    return cotton


def _divergence_cotton(
    geometry: dict[str, object],
    cotton: dict[tuple[int, int, int], TaylorJet],
) -> dict[tuple[int, int], TaylorJet]:
    divergence_cotton = {}
    for first, second in PAIRS:
        value = _divergence_cotton_row(geometry, cotton, first, second)
        divergence_cotton[(first, second)] = value
        divergence_cotton[(second, first)] = value
    return divergence_cotton


def _divergence_cotton_row(
    geometry: dict[str, object],
    cotton: dict[tuple[int, int, int], TaylorJet],
    first: int,
    second: int,
) -> TaylorJet:
    """Return one symmetric Bach differential component exactly."""

    if not (0 <= first <= second < 4):
        raise ValueError("Cotton-divergence row must use a canonical symmetric pair")
    inverse = geometry["inverse"]
    gamma = geometry["connection"]
    assert isinstance(inverse, dict) and isinstance(gamma, dict)
    contracted = []
    for outer, inner in product(range(4), repeat=2):
        derivative = cotton[(inner, first, second)].derivative(outer)
        derivative = derivative - sum_jets(
            gamma[(replacement, outer, inner)]
            * cotton[(replacement, first, second)]
            + gamma[(replacement, outer, first)]
            * cotton[(inner, replacement, second)]
            + gamma[(replacement, outer, second)]
            * cotton[(inner, first, replacement)]
            for replacement in range(4)
        )
        contracted.append(inverse[(outer, inner)] * derivative)
    return sum_jets(contracted)


def _schouten_weyl_contraction(
    geometry: dict[str, object],
    schouten: dict[tuple[int, int], TaylorJet],
    weyl: dict[tuple[int, int, int, int], TaylorJet],
) -> dict[tuple[int, int], TaylorJet]:
    inverse = geometry["inverse"]
    assert isinstance(inverse, dict)
    schouten_up = {}
    for first, second in PAIRS:
        value = sum_jets(
            inverse[(first, left)]
            * inverse[(second, right)]
            * schouten[(left, right)]
            for left, right in product(range(4), repeat=2)
        )
        schouten_up[(first, second)] = value
        schouten_up[(second, first)] = value
    output = {}
    for first, second in PAIRS:
        value = sum_jets(
            schouten_up[(inner, outer)]
            * weyl[(first, inner, second, outer)]
            for inner, outer in product(range(4), repeat=2)
        )
        output[(first, second)] = value
        output[(second, first)] = value
    return output


@lru_cache(maxsize=1)
def physical_euler_rows() -> tuple[TaylorJet, ...]:
    """Return ten metric and four Maxwell Euler-density Taylor rows."""

    geometry = metric_geometry()
    metric = geometry["metric"]
    inverse = geometry["inverse"]
    volume = geometry["volume_ratio"]
    assert isinstance(metric, dict) and isinstance(inverse, dict)
    assert isinstance(volume, TaylorJet)
    bach_lower = _bach_lower(geometry)

    field_strength = _field_strength()
    raised_field_strength = {
        (first, second): sum_jets(
            inverse[(first, left)]
            * inverse[(second, right)]
            * field_strength[(left, right)]
            for left, right in product(range(4), repeat=2)
        )
        for first, second in product(range(4), repeat=2)
    }
    invariant = sum_jets(
        field_strength[(first, second)] * raised_field_strength[(first, second)]
        for first, second in product(range(4), repeat=2)
    )
    stress_lower = {
        (first, second): sum_jets(
            inverse[(left, right)]
            * field_strength[(first, left)]
            * field_strength[(second, right)]
            for left, right in product(range(4), repeat=2)
        )
        - metric[(first, second)] * invariant.scale(sp.Rational(1, 4))
        for first, second in product(range(4), repeat=2)
    }

    metric_rows = []
    for first, second in PAIRS:
        multiplicity = 1 if first == second else 2
        raised_residual = sum_jets(
            inverse[(first, left)]
            * inverse[(second, right)]
            * (stress_lower[(left, right)] - bach_lower[(left, right)].scale(ALPHA_B))
            for left, right in product(range(4), repeat=2)
        )
        metric_rows.append(volume * raised_residual.scale(sp.Rational(multiplicity, 2)))

    potential_rows = []
    for target in range(4):
        divergence = sum_jets(
            (volume * raised_field_strength[(axis, target)]).scale(SIN).derivative(axis)
            for axis in range(4)
        ).scale(SIN.reciprocal())
        potential_rows.append(divergence)

    rows = tuple((*metric_rows, *potential_rows))
    if len(rows) != 14:
        raise AssertionError("Weyl--Maxwell physical row count drifted")
    for index, row in enumerate(rows):
        if not row.background.is_zero:
            raise AssertionError(f"common product is not on shell in row {index}: {row.background.values}")
    return rows


def physical_summary(
    rows: tuple[TaylorJet, ...] | None = None,
) -> dict[str, object]:
    """Summarize a frozen physical Taylor tuple without rebuilding it."""

    if rows is None:
        rows = physical_euler_rows()
    return {
        "row_count": len(rows),
        "q1_term_counts": [len(row.linear.terms) for row in rows],
        "q2_term_counts": [len(row.bilinear.terms) for row in rows],
        "q3_term_counts": [len(row.trilinear.terms) for row in rows],
        "maximum_orders": {
            "q1": max(row.linear.maximum_total_order for row in rows),
            "q2": max(row.bilinear.maximum_total_order for row in rows),
            "q3": max(row.trilinear.maximum_total_order for row in rows),
        },
        "coefficient_jet_base_point": "theta=pi/2",
    }


def gauge_generator() -> tuple[LinearOperator, ...]:
    """Linear Diff x Weyl x U(1) action on fourteen physical fields."""

    background_metric = {(a, b): sp.S.Zero for a, b in product(range(4), repeat=2)}
    background_metric[(0, 0)] = -1
    background_metric[(1, 1)] = 1
    background_metric[(2, 2)] = 1
    background_metric[(3, 3)] = SIN * SIN
    background_field = {(a, b): sp.S.Zero for a, b in product(range(4), repeat=2)}
    background_field[(2, 3)] = SIN * MAGNETIC_P
    background_field[(3, 2)] = -SIN * MAGNETIC_P
    rows: list[LinearOperator] = []
    for first, second in PAIRS:
        terms = []
        for vector in range(4):
            derivative = background_metric[(first, second)].derivative(vector) if hasattr(background_metric[(first, second)], "derivative") else sp.S.Zero
            if derivative != 0:
                terms.append((vector, (), derivative))
            if background_metric[(vector, second)] != 0:
                terms.append((vector, (first,), background_metric[(vector, second)]))
            if background_metric[(first, vector)] != 0:
                terms.append((vector, (second,), background_metric[(first, vector)]))
        terms.append((WEYL_GHOST, (), 2 * background_metric[(first, second)]))
        rows.append(LinearOperator.from_terms(terms))
    for component in range(4):
        rows.append(LinearOperator.from_terms((
            *((vector, (), background_field[(vector, component)]) for vector in range(4)),
            (LAMBDA_GHOST, (component,), sp.S.One),
        )))
    return tuple(rows)


def _operator_matrix(rows: tuple[LinearOperator, ...], input_count: int) -> tuple[tuple[LinearOperator, ...], ...]:
    output = [[LZERO for _ in range(input_count)] for _ in rows]
    for row, operator in enumerate(rows):
        grouped = [[] for _ in range(input_count)]
        for component, word, coefficient in operator.terms:
            grouped[component].append((component, word, coefficient))
        for column in range(input_count):
            output[row][column] = LinearOperator.from_terms(grouped[column])
    return tuple(tuple(row) for row in output)


def _linear_matrix(rows: tuple[TaylorJet, ...]) -> tuple[tuple[LinearOperator, ...], ...]:
    output = [[LZERO for _ in range(14)] for _ in range(14)]
    for row, jet in enumerate(rows):
        grouped = [[] for _ in range(14)]
        for component, word, coefficient in jet.linear.terms:
            grouped[component].append((component, word, coefficient))
        for column in range(14):
            output[row][column] = LinearOperator.from_terms(grouped[column])
    return tuple(tuple(row) for row in output)


def _reindex_linear(operator: LinearOperator, mapping: dict[int, int]) -> LinearOperator:
    return LinearOperator.from_terms((mapping[component], word, coefficient) for component, word, coefficient in operator.terms)


def _shift_bilinear(operator: BilinearOperator, mapping: dict[int, int]) -> BilinearOperator:
    return BilinearOperator.from_terms((mapping[a], aw, mapping[b], bw, coefficient) for a, aw, b, bw, coefficient in operator.terms)


def _shift_trilinear(operator: TrilinearOperator, mapping: dict[int, int]) -> TrilinearOperator:
    return TrilinearOperator.from_terms((mapping[a], aw, mapping[b], bw, mapping[c], cw, coefficient) for a, aw, b, bw, c, cw, coefficient in operator.terms)


def build_q1_from_physical(
    physical_rows: tuple[TaylorJet, ...],
) -> tuple[LinearOperator, ...]:
    """Build the unary coderivation from an authoritative physical snapshot."""

    output = [LZERO for _ in range(TOTAL_ROWS)]
    generator = gauge_generator()
    ghost_map = {index: GHOST_SLICE[index] for index in range(6)}
    field_map = {index: FIELD_SLICE[index] for index in range(14)}
    for local, operator in enumerate(generator):
        output[FIELD_SLICE[local]] = _reindex_linear(operator, ghost_map)
    for local, row in enumerate(physical_rows):
        output[EQUATION_SLICE[local]] = _reindex_linear(row.linear, field_map)
    adjoint = formal_adjoint_matrix(_operator_matrix(generator, 6))
    for ghost in range(6):
        terms = []
        for equation in range(14):
            terms.extend(
                (EQUATION_SLICE[component], word, -coefficient)
                for component, word, coefficient in adjoint[ghost][equation].terms
            )
        output[IDENTITY_SLICE[ghost]] = LinearOperator.from_terms(terms)
    result = tuple(output)
    defects = [compose_linear(row, result) for row in result]
    if any(defect.terms for defect in defects):
        raise AssertionError("Weyl--Maxwell minimal q1 is not nilpotent: " + str([(row, len(defect.terms)) for row, defect in enumerate(defects) if defect.terms]))
    return result


@lru_cache(maxsize=1)
def build_q1() -> tuple[LinearOperator, ...]:
    return build_q1_from_physical(physical_euler_rows())


def row_layout() -> list[dict[str, object]]:
    metric_names = [f"g_{first}{second}" for first, second in PAIRS]
    field_names = [*metric_names, *[f"A_{axis}" for axis in range(4)]]
    ghost_names = [*[f"c_{axis}" for axis in range(4)], "lambda_cov", "sigma_W"]
    rows = []
    for index, name in enumerate(ghost_names):
        bundle = "Diff_ghost" if index < 4 else ("U1_covariant_ghost" if index == LAMBDA_GHOST else "Weyl_scalar_ghost")
        rows.append({"index": GHOST_SLICE[index], "row_id": name, "degree": -1, "parity": "odd", "bundle_id": bundle, "dual_row": IDENTITY_SLICE[index]})
    for index, name in enumerate(field_names):
        rows.append({"index": FIELD_SLICE[index], "row_id": name, "degree": 0, "parity": "even", "bundle_id": "symmetric_covariant_2" if index < 10 else "U1_potential_covector", "dual_row": EQUATION_SLICE[index]})
    for index, name in enumerate(field_names):
        rows.append({"index": EQUATION_SLICE[index], "row_id": name + "_star", "degree": 1, "parity": "odd", "bundle_id": "Bach_Maxwell_Euler_density" if index < 10 else "Maxwell_Euler_density", "dual_row": FIELD_SLICE[index]})
    for index, name in enumerate(ghost_names):
        bundle = "Diff_identity_density" if index < 4 else ("U1_identity_density" if index == LAMBDA_GHOST else "Weyl_trace_identity_density")
        rows.append({"index": IDENTITY_SLICE[index], "row_id": name + "_star", "degree": 2, "parity": "even", "bundle_id": bundle, "dual_row": GHOST_SLICE[index]})
    return sorted(rows, key=lambda row: int(row["index"]))


def pairing_terms() -> list[dict[str, object]]:
    terms = []
    for left, right in [*zip(GHOST_SLICE, IDENTITY_SLICE), *zip(FIELD_SLICE, EQUATION_SLICE)]:
        terms.append({"left_row": left, "right_row": right, "coefficient": "1"})
        terms.append({"left_row": right, "right_row": left, "coefficient": "-1"})
    return terms


def _ghost_bracket() -> tuple[BilinearOperator, ...]:
    outputs = [BZERO for _ in range(6)]
    for target in range(4):
        outputs[target] = graded_complete_bilinear(BilinearOperator.from_terms(
            (GHOST_SLICE[vector], (), GHOST_SLICE[target], (vector,), sp.S.One)
            for vector in range(4)
        ), PARITIES)
    outputs[WEYL_GHOST] = graded_complete_bilinear(BilinearOperator.from_terms(
        (GHOST_SLICE[vector], (), GHOST_SLICE[WEYL_GHOST], (vector,), sp.S.One)
        for vector in range(4)
    ), PARITIES)
    return tuple(outputs)


def _covariant_u1_ghost_q2() -> BilinearOperator:
    return BilinearOperator.from_terms((
        (GHOST_SLICE[first], (), GHOST_SLICE[second], (),
         SIN * MAGNETIC_P if (first, second) == (2, 3) else -SIN * MAGNETIC_P)
        for first, second in ((2, 3), (3, 2))
    ))


def _gauge_field_action() -> tuple[BilinearOperator, ...]:
    outputs = [BZERO for _ in range(14)]
    for first, second in PAIRS:
        local_output = PAIR_INDEX[(first, second)]
        terms = []
        for vector in range(4):
            ghost = GHOST_SLICE[vector]
            terms.append((ghost, (), FIELD_SLICE[local_output], (vector,), sp.S.One))
            terms.append((ghost, (first,), FIELD_SLICE[PAIR_INDEX[tuple(sorted((vector, second)))]], (), sp.S.One))
            terms.append((ghost, (second,), FIELD_SLICE[PAIR_INDEX[tuple(sorted((first, vector)))]], (), sp.S.One))
        terms.append((GHOST_SLICE[WEYL_GHOST], (), FIELD_SLICE[local_output], (), sp.Integer(2)))
        outputs[local_output] = graded_complete_bilinear(BilinearOperator.from_terms(terms), PARITIES)
    for component in range(4):
        terms = []
        for vector in range(4):
            ghost = GHOST_SLICE[vector]
            terms.append((ghost, (), FIELD_SLICE[10 + component], (vector,), sp.S.One))
            terms.append((ghost, (), FIELD_SLICE[10 + vector], (component,), -sp.S.One))
        outputs[10 + component] = graded_complete_bilinear(BilinearOperator.from_terms(terms), PARITIES)
    return tuple(outputs)


def _ordered_gauge_part(operator: BilinearOperator) -> BilinearOperator:
    return BilinearOperator.from_terms(term for term in operator.terms if term[0] in GHOST_SLICE and term[2] in FIELD_SLICE)


def build_q2_from_physical(
    physical_rows: tuple[TaylorJet, ...],
) -> tuple[BilinearOperator, ...]:
    """Build the binary coderivation from an authoritative physical snapshot."""

    outputs = [BZERO for _ in range(TOTAL_ROWS)]
    ghost_bracket = _ghost_bracket()
    for output, operator in enumerate(ghost_bracket):
        outputs[GHOST_SLICE[output]] = outputs[GHOST_SLICE[output]] + operator
    outputs[GHOST_SLICE[LAMBDA_GHOST]] = outputs[GHOST_SLICE[LAMBDA_GHOST]] + _covariant_u1_ghost_q2()
    gauge_action = _gauge_field_action()
    for local_output, operator in enumerate(gauge_action):
        outputs[FIELD_SLICE[local_output]] = outputs[FIELD_SLICE[local_output]] + operator
        ordered = _ordered_gauge_part(operator)
        for field_input, mate in negative_transpose_bilinear_right(ordered, dual_output=EQUATION_SLICE[local_output]).items():
            outputs[EQUATION_SLICE[field_input - FIELD_SLICE[0]]] = outputs[EQUATION_SLICE[field_input - FIELD_SLICE[0]]] + graded_complete_bilinear(mate, PARITIES)
        for ghost_input, mate in negative_transpose_bilinear_left(ordered, dual_output=EQUATION_SLICE[local_output]).items():
            outputs[IDENTITY_SLICE[ghost_input]] = outputs[IDENTITY_SLICE[ghost_input]] + graded_complete_bilinear(mate, PARITIES)
    field_map = {index: FIELD_SLICE[index] for index in range(14)}
    for local_output, equation in enumerate(physical_rows):
        outputs[EQUATION_SLICE[local_output]] = outputs[EQUATION_SLICE[local_output]] + _shift_bilinear(equation.bilinear, field_map)
    all_ghost_rows = (*ghost_bracket[:4], _covariant_u1_ghost_q2(), ghost_bracket[WEYL_GHOST])
    for local_output, operator in enumerate(all_ghost_rows):
        for ghost_input, mate in negative_transpose_bilinear_right(operator, dual_output=IDENTITY_SLICE[local_output]).items():
            outputs[IDENTITY_SLICE[ghost_input]] = outputs[IDENTITY_SLICE[ghost_input]] + graded_complete_bilinear(mate, PARITIES)
    result = tuple(outputs)
    for output, operator in enumerate(result):
        if operator != operator.koszul_swapped(PARITIES):
            raise AssertionError(f"q2 lost Koszul symmetry on row {output}")
    return result


@lru_cache(maxsize=1)
def build_q2() -> tuple[BilinearOperator, ...]:
    return build_q2_from_physical(physical_euler_rows())


def _covariant_u1_ghost_q3_ordered() -> TrilinearOperator:
    terms = []
    for first, second in product(range(4), repeat=2):
        terms.append((GHOST_SLICE[first], (), GHOST_SLICE[second], (), FIELD_SLICE[10 + second], (first,), sp.S.One))
        terms.append((GHOST_SLICE[first], (), GHOST_SLICE[second], (), FIELD_SLICE[10 + first], (second,), -sp.S.One))
    return TrilinearOperator.from_terms(terms)


def build_q3_from_physical(
    physical_rows: tuple[TaylorJet, ...],
) -> tuple[TrilinearOperator, ...]:
    """Build the ternary coderivation from an authoritative physical snapshot."""

    outputs = [TZERO for _ in range(TOTAL_ROWS)]
    field_map = {index: FIELD_SLICE[index] for index in range(14)}
    for local_output, equation in enumerate(physical_rows):
        outputs[EQUATION_SLICE[local_output]] = _shift_trilinear(equation.trilinear, field_map)
    ordered = _covariant_u1_ghost_q3_ordered()
    outputs[GHOST_SLICE[LAMBDA_GHOST]] = graded_complete_trilinear(ordered, PARITIES).scale(sp.Rational(1, 2))
    for field_input, mate in negative_transpose_trilinear_slot(ordered, slot=2, dual_output=IDENTITY_SLICE[LAMBDA_GHOST]).items():
        outputs[EQUATION_SLICE[field_input - FIELD_SLICE[0]]] = outputs[EQUATION_SLICE[field_input - FIELD_SLICE[0]]] - graded_complete_trilinear(mate, PARITIES).scale(sp.Rational(1, 2))
    for ghost_input, mate in negative_transpose_trilinear_slot(ordered, slot=0, dual_output=IDENTITY_SLICE[LAMBDA_GHOST]).items():
        outputs[IDENTITY_SLICE[ghost_input]] = outputs[IDENTITY_SLICE[ghost_input]] - graded_complete_trilinear(mate, PARITIES)
    result = tuple(outputs)
    for output, operator in enumerate(result):
        for permutation in ((1, 0, 2), (0, 2, 1)):
            if operator != operator.koszul_permuted(permutation, PARITIES):
                raise AssertionError(f"q3 lost Koszul symmetry on row {output}, permutation {permutation}")
    return result


@lru_cache(maxsize=1)
def build_q3() -> tuple[TrilinearOperator, ...]:
    return build_q3_from_physical(physical_euler_rows())


def _apply_output_linear_bilinear(outer: LinearOperator, rows: tuple[BilinearOperator, ...]) -> BilinearOperator:
    values = []
    for middle, word, coefficient in outer.terms:
        current = rows[middle]
        for axis in word:
            current = current.derivative(axis)
        values.append(current.scale(coefficient))
    return BilinearOperator.from_terms(term for value in values for term in value.terms)


def _precompose_bilinear_q1(operator: BilinearOperator, q1: tuple[LinearOperator, ...], *, slot: int) -> BilinearOperator:
    terms = []
    for left, left_word, right, right_word, coefficient in operator.terms:
        if slot == 0:
            current = q1[left]
            for axis in left_word:
                current = current.derivative(axis)
            terms.extend((new_left, new_word, right, right_word, coefficient * value) for new_left, new_word, value in current.terms)
        elif slot == 1:
            current = q1[right]
            for axis in right_word:
                current = current.derivative(axis)
            sign = -1 if PARITIES[left] else 1
            terms.extend((left, left_word, new_right, new_word, sign * coefficient * value) for new_right, new_word, value in current.terms)
        else:
            raise ValueError("bilinear slot must be zero or one")
    return BilinearOperator.from_terms(terms)


def arity_two_defects(
    q1: tuple[LinearOperator, ...] | None = None,
    q2: tuple[BilinearOperator, ...] | None = None,
) -> tuple[BilinearOperator, ...]:
    if q1 is None:
        q1 = build_q1()
    if q2 is None:
        q2 = build_q2()
    output = []
    for target in range(TOTAL_ROWS):
        defect = _apply_output_linear_bilinear(q1[target], q2)
        if q2[target].terms:
            defect = defect + _precompose_bilinear_q1(q2[target], q1, slot=0)
            defect = defect + _precompose_bilinear_q1(q2[target], q1, slot=1)
        output.append(defect)
    return tuple(output)


def _apply_output_linear_trilinear(outer: LinearOperator, rows: tuple[TrilinearOperator, ...]) -> TrilinearOperator:
    values = []
    for middle, word, coefficient in outer.terms:
        current = rows[middle]
        for axis in word:
            current = current.derivative(axis)
        values.append(current.scale(coefficient))
    return TrilinearOperator.from_terms(term for value in values for term in value.terms)


def _precompose_trilinear_q1(operator: TrilinearOperator, q1: tuple[LinearOperator, ...], *, slot: int) -> TrilinearOperator:
    terms = []
    for first, first_word, second, second_word, third, third_word, coefficient in operator.terms:
        rows = (first, second, third)
        words = (first_word, second_word, third_word)
        current = q1[rows[slot]]
        for axis in words[slot]:
            current = current.derivative(axis)
        sign = -1 if sum(PARITIES[rows[index]] for index in range(slot)) % 2 else 1
        for new_row, new_word, value in current.terms:
            new_rows = list(rows)
            new_words = list(words)
            new_rows[slot] = new_row
            new_words[slot] = new_word
            terms.append((new_rows[0], new_words[0], new_rows[1], new_words[1], new_rows[2], new_words[2], sign * coefficient * value))
    return TrilinearOperator.from_terms(terms)


def _q2_q2_row(outer: BilinearOperator, q2: tuple[BilinearOperator, ...]) -> TrilinearOperator:
    terms = []
    for middle, outer_word, last, last_word, outer_coefficient in outer.terms:
        current = q2[middle]
        for axis in outer_word:
            current = current.derivative(axis)
        for first, first_word, second, second_word, inner_coefficient in current.terms:
            coefficient = outer_coefficient * inner_coefficient
            terms.append((first, first_word, second, second_word, last, last_word, coefficient))
            swap_sign = -1 if PARITIES[second] * PARITIES[last] else 1
            terms.append((first, first_word, last, last_word, second, second_word, swap_sign * coefficient))
            rotate_sign = -1 if PARITIES[last] * (PARITIES[first] + PARITIES[second]) % 2 else 1
            terms.append((last, last_word, first, first_word, second, second_word, rotate_sign * coefficient))
    return TrilinearOperator.from_terms(terms)


def arity_three_defect_row(
    target: int,
    q1: tuple[LinearOperator, ...] | None = None,
    q2: tuple[BilinearOperator, ...] | None = None,
    q3: tuple[TrilinearOperator, ...] | None = None,
) -> TrilinearOperator:
    if q1 is None:
        q1 = build_q1()
    if q2 is None:
        q2 = build_q2()
    if q3 is None:
        q3 = build_q3()
    defect = _q2_q2_row(q2[target], q2)
    defect = defect + _apply_output_linear_trilinear(q1[target], q3)
    if q3[target].terms:
        for slot in range(3):
            defect = defect + _precompose_trilinear_q1(q3[target], q1, slot=slot)
    return defect


def unary_checks(
    rows: tuple[TaylorJet, ...] | None = None,
) -> dict[str, object]:
    if rows is None:
        rows = physical_euler_rows()
    generator = gauge_generator()
    ward = [len(compose_linear(row.linear, generator).terms) for row in rows]
    if any(ward):
        raise AssertionError(f"Weyl--Maxwell Hessian failed gauge invariance: {ward}")
    hessian = _linear_matrix(rows)
    adjoint = formal_adjoint_matrix(hessian)
    adjoint_defects = []
    for row in range(14):
        for column in range(14):
            defect = hessian[row][column] - adjoint[row][column]
            if defect.terms:
                adjoint_defects.append((row, column, len(defect.terms)))
    if adjoint_defects:
        raise AssertionError(f"Weyl--Maxwell Hessian lost formal self-adjointness: {adjoint_defects[:12]}")
    return {
        "gauge_generator_row_count": len(generator),
        "hessian_ward_defect_term_counts": ward,
        "formal_adjoint_defects": adjoint_defects,
        "coefficient_jet_base_point": "theta=pi/2",
    }


if __name__ == "__main__":
    import json

    print(json.dumps(physical_summary(), indent=2, sort_keys=True))
