#!/usr/bin/env python3
"""Action-derived mixed gravity--Maxwell ``q3`` on the Berger BV complex.

This module deliberately starts below the certificate layer.  It constructs
the fourth Maxwell action derivative in raw metric/potential variables and
then applies the already-certified clock, nonminimal, and gauge-fermion
linear canonical maps.  The nonlinear covariant-ghost shear used by the
cyclic ``q2`` repair is applied in a separate final step; keeping the two
stages visible prevents an action coefficient from being fitted to a later
homological defect.

The expensive gravity--clock ``q3`` is not rebuilt here.  This file emits only
the sparse mixed Maxwell overlay.  The combined arity-three identity can
therefore be replayed after subtracting the independently certified pure
gravity identity row by row.
"""

from __future__ import annotations

from functools import lru_cache
from itertools import product
import json
import os
from pathlib import Path

import sympy as sp

if os.environ.get("BERGER_TAYLOR_ORDER") != "3":
    raise RuntimeError(
        "launch the mixed Maxwell q3 producer with BERGER_TAYLOR_ORDER=3"
    )

from d_quotient_classical.backreacted_clock import berger_support_local_q2 as engine
from d_quotient_classical.backreacted_clock.berger_gauge_fixed_nonminimal_completion import (
    _gauge_fermion_shear,
)
from d_quotient_classical.backreacted_clock.berger_nonminimal_algebraic_completion import (
    MINIMAL_TO_EXTENDED,
)
from d_quotient_classical.backreacted_clock.berger_support_local_coupled_maxwell_q2 import (
    APLUS_ROWS,
    A_ROWS,
    COMBINED_PARITIES,
    GRAVITY_ROWS,
    TOTAL_ROWS,
    _baseline_maxwell_q2_overlay,
    _degree_zero_shear_coboundary_row,
    _fixture_structure,
    build_coupled_q1_fixture,
    maxwell_covariant_ghost_shear,
)


RAW_GRAVITY_ROWS = 34
RAW_TOTAL_ROWS = 44
RAW_CM = 34
RAW_A_ROWS = tuple(range(35, 39))
RAW_APLUS_ROWS = tuple(range(39, 43))
RAW_CMPLUS = 43
ROOT = Path(__file__).resolve().parents[2]
GRAVITY_Q2_PAYLOAD = (
    ROOT / "d_quotient_classical/certificates/BERGER_SUPPORT_LOCAL_Q2_PAYLOAD.json"
)


def _identity_linear_matrix(size: int) -> list[list[engine.LinearOperator]]:
    result = engine._zero_linear_matrix(size, size)
    for index in range(size):
        result[index][index] = engine._one_linear()
    return result


def _block_extend_linear_map(
    gravity: list[list[engine.LinearOperator]],
    total: int,
) -> list[list[engine.LinearOperator]]:
    """Extend a square gravity map by the identity on appended Maxwell rows."""

    if len(gravity) > total or any(len(row) != len(gravity) for row in gravity):
        raise ValueError("gravity block is not square or does not fit")
    result = _identity_linear_matrix(total)
    for row, entries in enumerate(gravity):
        for column, value in enumerate(entries):
            result[row][column] = value
    return result


@lru_cache(maxsize=1)
def raw_maxwell_euler_jets() -> tuple[engine.Jet2, ...]:
    """Return ten raw Maxwell Euler densities through mixed order three.

    Local Taylor components are ``h_ab=0..9`` and ``A_a=10..13``.  The first
    ten outputs are the canonical covariant-metric equations.  The final four
    are the potential equations.  The anholonomic-frame expression

    ``E_A^b=e_a H^{ab}+1/2 C_ac^b H^{ac}``

    follows directly by varying ``-1/4 F_ab H^{ab}``; unimodularity removes
    an otherwise separate frame-divergence density.
    """

    metric = engine._metric()
    inverse = engine._inverse_metric(metric)
    density = engine._volume_density_ratio()
    potential = {axis: engine.Jet2.field(10 + axis) for axis in range(4)}
    field_strength: dict[tuple[int, int], engine.Jet2] = {}
    for first, second in product(range(4), repeat=2):
        value = potential[second].derivative(first) - potential[first].derivative(
            second
        )
        for target, coefficient in engine._structure(first, second).items():
            value = value - potential[target].scale(coefficient)
        field_strength[(first, second)] = value

    raised_field_strength = {
        (first, second): engine._sum_jets(
            inverse[(first, left)]
            * inverse[(second, right)]
            * field_strength[(left, right)]
            for left, right in product(range(4), repeat=2)
        )
        for first, second in product(range(4), repeat=2)
    }
    constitutive_density = {
        pair: density * value for pair, value in raised_field_strength.items()
    }

    trace = engine._sum_jets(
        inverse[(first, third)]
        * inverse[(second, fourth)]
        * field_strength[(first, second)]
        * field_strength[(third, fourth)]
        for first, second, third, fourth in product(range(4), repeat=4)
    )
    stress = {}
    for first, second in product(range(4), repeat=2):
        kinetic = engine._sum_jets(
            inverse[(left, right)]
            * field_strength[(first, left)]
            * field_strength[(second, right)]
            for left, right in product(range(4), repeat=2)
        )
        stress[(first, second)] = kinetic - metric[(first, second)] * trace.scale(
            sp.Rational(1, 4)
        )

    metric_rows = []
    for first, second in engine.PAIRS:
        multiplicity = 2 if first != second else 1
        raised = engine._sum_jets(
            inverse[(first, left)]
            * inverse[(second, right)]
            * stress[(left, right)]
            for left, right in product(range(4), repeat=2)
        )
        # The Maxwell contribution to alpha_B B-T is -T.  The canonical
        # covariant-metric row is -sqrt(-g) E^{ab}, hence the displayed plus.
        metric_rows.append(raised.scale(multiplicity) * density)

    potential_rows = []
    for target in range(4):
        value = engine._sum_jets(
            constitutive_density[(axis, target)].derivative(axis)
            for axis in range(4)
        )
        value = value + engine._sum_jets(
            constitutive_density[(first, second)].scale(
                sp.Rational(1, 2) * coefficient
            )
            for first, second in product(range(4), repeat=2)
            for output, coefficient in engine._structure(first, second).items()
            if output == target
        )
        potential_rows.append(value)
    return (*metric_rows, *potential_rows)


def _raw_component(component: int) -> int:
    if 0 <= component < 10:
        return 5 + component
    if 10 <= component < 14:
        return RAW_A_ROWS[component - 10]
    raise ValueError(f"unexpected raw Maxwell action component: {component}")


def _reindex_action_trilinear(
    operator: engine.TrilinearOperator,
) -> engine.TrilinearOperator:
    return engine.TrilinearOperator.from_terms(
        (
            _raw_component(first),
            first_word,
            _raw_component(second),
            second_word,
            _raw_component(third),
            third_word,
            coefficient,
        )
        for first, first_word, second, second_word, third, third_word, coefficient
        in operator.terms
    )


def _reindex_action_bilinear(
    operator: engine.BilinearOperator,
) -> engine.BilinearOperator:
    return engine.BilinearOperator.from_terms(
        (
            _raw_component(first),
            first_word,
            _raw_component(second),
            second_word,
            coefficient,
        )
        for first, first_word, second, second_word, coefficient in operator.terms
    )


@lru_cache(maxsize=1)
def build_raw_action_q3_overlay() -> tuple[engine.TrilinearOperator, ...]:
    """Return the raw 44-row fourth-action-derivative overlay."""

    rows = raw_maxwell_euler_jets()
    output = [engine.TZERO for _ in range(RAW_TOTAL_ROWS)]
    for equation in range(10):
        output[17 + equation] = _reindex_action_trilinear(
            rows[equation].trilinear
        )
    for component in range(4):
        output[RAW_APLUS_ROWS[component]] = _reindex_action_trilinear(
            rows[10 + component].trilinear
        )
    result = tuple(engine._fixture_trilinear(operator) for operator in output)
    for row, operator in enumerate(result):
        for permutation in ((1, 0, 2), (0, 2, 1)):
            if operator != operator.koszul_permuted(
                permutation,
                engine.RAW_PARITIES + (1,) + (0,) * 4 + (1,) * 4 + (0,),
            ):
                raise AssertionError(f"raw mixed q3 lost symmetry row={row}")
    return result


@lru_cache(maxsize=1)
def build_raw_action_q2_physical_overlay() -> tuple[engine.BilinearOperator, ...]:
    """Regression-only raw physical q2 emitted by the same action jets."""

    rows = raw_maxwell_euler_jets()
    output = [engine.BZERO for _ in range(RAW_TOTAL_ROWS)]
    for equation in range(10):
        output[17 + equation] = _reindex_action_bilinear(rows[equation].bilinear)
    for component in range(4):
        output[RAW_APLUS_ROWS[component]] = _reindex_action_bilinear(
            rows[10 + component].bilinear
        )
    return tuple(engine._fixture_bilinear(operator) for operator in output)


def _clock_transport_q3(
    raw: tuple[engine.TrilinearOperator, ...],
) -> tuple[engine.TrilinearOperator, ...]:
    canonical, inverse = engine._clock_canonical_maps_fixture()
    return engine._transform_trilinear_vector(
        raw,
        _block_extend_linear_map(canonical, RAW_TOTAL_ROWS),
        _block_extend_linear_map(inverse, RAW_TOTAL_ROWS),
    )


def _extend_nonminimal_q3(
    dressed: tuple[engine.TrilinearOperator, ...],
) -> tuple[engine.TrilinearOperator, ...]:
    index_map = {old: new for old, new in enumerate(MINIMAL_TO_EXTENDED)}
    index_map.update({RAW_CM + index: GRAVITY_ROWS + index for index in range(10)})
    output = [engine.TZERO for _ in range(TOTAL_ROWS)]
    for old_output, operator in enumerate(dressed):
        new_output = index_map[old_output]
        output[new_output] = engine._reindex_trilinear(operator, index_map)
    return tuple(output)


@lru_cache(maxsize=1)
def build_linear_transport_action_q3_overlay() -> tuple[engine.TrilinearOperator, ...]:
    """Transport the action q3 through all certified *linear* BV maps."""

    dressed = _clock_transport_q3(build_raw_action_q3_overlay())
    extended = _extend_nonminimal_q3(dressed)
    _raw_map, _condition, _nilpotent, shear, inverse = _gauge_fermion_shear()
    transported = engine._transform_trilinear_vector(
        extended,
        _block_extend_linear_map(shear, TOTAL_ROWS),
        _block_extend_linear_map(inverse, TOTAL_ROWS),
    )
    return tuple(engine._fixture_trilinear(operator) for operator in transported)


def _scale_maxwell_outputs_bilinear(
    operators: tuple[engine.BilinearOperator, ...], coefficient: sp.Expr
) -> tuple[engine.BilinearOperator, ...]:
    """Scale the ten Maxwell *outputs* of a binary coderivation."""

    return tuple(
        operator.scale(coefficient if output >= GRAVITY_ROWS else 1)
        for output, operator in enumerate(operators)
    )


def _scale_maxwell_outputs_trilinear(
    operators: tuple[engine.TrilinearOperator, ...], coefficient: sp.Expr
) -> tuple[engine.TrilinearOperator, ...]:
    """Scale the ten Maxwell *outputs* of a ternary coderivation."""

    return tuple(
        operator.scale(coefficient if output >= GRAVITY_ROWS else 1)
        for output, operator in enumerate(operators)
    )


@lru_cache(maxsize=1)
def typed_covariant_ghost_shear() -> tuple[engine.BilinearOperator, ...]:
    """The shear raised with the nonlinear Maxwell Darboux normalization.

    The arity-two repair originally multiplied every Maxwell output by two
    while leaving the displayed odd pairing fixed.  That gives the right
    *lowered* cubic tensor, but output scaling is not functorial under
    coderivation composition.  The nonlinear presentation instead places
    the factor two in the Maxwell pairing.  Raising the same canonical shear
    with that pairing divides its Maxwell output rows by two.
    """

    return tuple(
        engine._fixture_bilinear(operator)
        for operator in _scale_maxwell_outputs_bilinear(
            maxwell_covariant_ghost_shear(), sp.Rational(1, 2)
        )
    )


def _degree_zero_typed_shear_coboundary_row(
    target: int,
) -> engine.BilinearOperator:
    q1 = build_coupled_q1_fixture()
    shear = typed_covariant_ghost_shear()
    defect = engine.BZERO
    for middle, outer in enumerate(q1[target]):
        if outer.terms and shear[middle].terms:
            defect = defect + engine._apply_output_linear(outer, shear[middle])
    if shear[target].terms:
        defect = defect - engine._precompose_bilinear_slot(
            shear[target], q1, slot=0, parities=COMBINED_PARITIES
        )
        defect = defect - engine._precompose_bilinear_slot(
            shear[target],
            q1,
            slot=1,
            parities=COMBINED_PARITIES,
            second_slot_q1_sign=True,
        )
    return engine._fixture_bilinear(defect)


@lru_cache(maxsize=1)
def build_typed_maxwell_q2_overlay() -> tuple[engine.BilinearOperator, ...]:
    """Return the nonlinear typed q2 overlay.

    With ``S=diag(I_54,2 I_10)``, the old arity-two export is ``S q2``
    while its pairing is ``Omega``.  This presentation is ``q2`` with
    pairing ``Omega S``.  The lowered cubic tensors agree exactly:

    ``Omega (S q2) = (Omega S) q2``.
    """

    baseline = _baseline_maxwell_q2_overlay()
    result = tuple(
        engine._fixture_bilinear(
            operator + _degree_zero_typed_shear_coboundary_row(output)
        )
        for output, operator in enumerate(baseline)
    )
    for output, operator in enumerate(result):
        if operator != operator.koszul_swapped(COMBINED_PARITIES):
            raise AssertionError(f"typed Maxwell q2 lost symmetry row={output}")
    return result


def _binary_coderivation_bracket_row(
    target: int,
    left: tuple[engine.BilinearOperator, ...],
    right: tuple[engine.BilinearOperator, ...],
) -> engine.TrilinearOperator:
    """Return ``[left,right]`` for degrees one and zero, respectively."""

    return engine._fixture_trilinear(
        engine._q2_composed_with_q2_row(left[target], right, COMBINED_PARITIES)
        - engine._q2_composed_with_q2_row(right[target], left, COMBINED_PARITIES)
    )


def _exact_rational(value: int | dict[str, int]) -> sp.Rational:
    if isinstance(value, int):
        return sp.Rational(value)
    return sp.Rational(value["numerator"], value["denominator"])


def _word(multiindex: list[int]) -> tuple[int, ...]:
    return tuple(
        axis for axis, multiplicity in enumerate(multiindex) for _ in range(multiplicity)
    )


@lru_cache(maxsize=1)
def _gravity_q2_zero_extended() -> tuple[engine.BilinearOperator, ...]:
    """Parse the frozen 54-row q2 without rebuilding the large gravity jets."""

    payload = json.loads(GRAVITY_Q2_PAYLOAD.read_text())
    if payload.get("shape") != [54, 54, 54] or len(payload.get("rows", ())) != 54:
        raise AssertionError("gravity q2 payload shape drifted")
    output = [engine.BZERO for _ in range(TOTAL_ROWS)]
    for row in payload["rows"]:
        terms = []
        for left, left_multiindex, right, right_multiindex, encoded in row["terms"]:
            coefficient = _exact_rational(encoded["rational"])
            coefficient += _exact_rational(encoded["sqrt10"]) * engine.SQRT10
            terms.append(
                (
                    left,
                    _word(left_multiindex),
                    right,
                    _word(right_multiindex),
                    coefficient,
                )
            )
        output[row["output"]] = engine.BilinearOperator.from_terms(terms)
    return tuple(output)


@lru_cache(maxsize=1)
def _full_action_q2() -> tuple[engine.BilinearOperator, ...]:
    gravity = _gravity_q2_zero_extended()
    maxwell = _baseline_maxwell_q2_overlay()
    return tuple(
        engine._fixture_bilinear(gravity[row] + maxwell[row])
        for row in range(TOTAL_ROWS)
    )


@lru_cache(maxsize=1)
def build_typed_mixed_q3_overlay() -> tuple[engine.TrilinearOperator, ...]:
    """Return the complete mixed Maxwell q3 overlay in the typed pairing.

    If ``B`` is the action-derived binary operation, ``A`` its action-derived
    ternary operation, and ``F`` the typed degree-zero binary canonical
    shear, the finite canonical transformation gives

    ``q2 = B+[q1,F]`` and
    ``q3 = A+[B,F]+1/2[[q1,F],F]``.

    This is derived from the action and the certified BV-canonical shear; no
    residual-mode coefficient or nilpotency defect is fitted.
    """

    action_q3 = build_linear_transport_action_q3_overlay()
    baseline_q2 = _full_action_q2()
    shear = typed_covariant_ghost_shear()
    delta = tuple(
        _degree_zero_typed_shear_coboundary_row(output)
        for output in range(TOTAL_ROWS)
    )
    result = []
    for target in range(TOTAL_ROWS):
        value = action_q3[target]
        value = value + _binary_coderivation_bracket_row(
            target, baseline_q2, shear
        )
        value = value + _binary_coderivation_bracket_row(
            target, delta, shear
        ).scale(sp.Rational(1, 2))
        result.append(engine._fixture_trilinear(value))
    output = tuple(result)
    for row, operator in enumerate(output):
        for permutation in ((1, 0, 2), (0, 2, 1)):
            if operator != operator.koszul_permuted(
                permutation, COMBINED_PARITIES
            ):
                raise AssertionError(f"typed mixed q3 lost symmetry row={row}")
    return output


def diagnostics() -> dict[str, object]:
    raw = build_raw_action_q3_overlay()
    transported = build_linear_transport_action_q3_overlay()
    typed_q2 = build_typed_maxwell_q2_overlay()
    typed_q3 = build_typed_mixed_q3_overlay()
    return {
        "raw_term_count": sum(len(row.terms) for row in raw),
        "raw_nonzero_rows": [index for index, row in enumerate(raw) if row.terms],
        "transported_term_count": sum(len(row.terms) for row in transported),
        "transported_nonzero_rows": [
            index for index, row in enumerate(transported) if row.terms
        ],
        "maximum_total_jet_order": max(
            row.maximum_total_order for row in transported
        ),
        "typed_q2_term_count": sum(len(row.terms) for row in typed_q2),
        "typed_q3_term_count": sum(len(row.terms) for row in typed_q3),
        "typed_q3_nonzero_rows": [
            index for index, row in enumerate(typed_q3) if row.terms
        ],
        "typed_q3_maximum_total_jet_order": max(
            row.maximum_total_order for row in typed_q3
        ),
    }


if __name__ == "__main__":
    import json

    print(json.dumps(diagnostics(), indent=2, sort_keys=True))
