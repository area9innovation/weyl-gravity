"""Independent physical-quartic cyclicity replay for retained Berger ell3.

The replay lowers the retained trilinear operation with the typed odd pairing,
transposes its first physical input through the invariant volume form, and
performs the formal PBW adjoint by exact integration by parts.  It deliberately
does not promote the separate ghost/antifield completion to an independently
checked full-BV cyclicity theorem.
"""

from __future__ import annotations

from collections import defaultdict
from fractions import Fraction
import time
from typing import Any, Mapping

from . import berger_mixed_q3_acceptance as arity3
from . import berger_qsqrt10_replay as q10
from .berger_coupled_36_transfer_replay import _parse_operator
from . import berger_retained_mixed_ell3_acceptance as retained


TRowKey = arity3.TRowKey


def _qdiv(left: q10.Q10, right: q10.Q10) -> q10.Q10:
    """Divide exactly in Q(sqrt(10))."""

    rational, radical = right
    norm = rational * rational - 10 * radical * radical
    if norm == 0:
        raise ValueError("zero typed-pairing weight")
    return (
        (left[0] * rational - 10 * left[1] * radical) / norm,
        (left[1] * rational - left[0] * radical) / norm,
    )


def _positive_weight(value: q10.Q10) -> q10.Q10:
    if value[1] or not value[0]:
        raise ValueError("typed pairing weight is not a nonzero rational")
    return abs(value[0]), Fraction(0)


def _formal_adjoint_distributions(
    word: q10.Word,
    first_word: q10.Word,
    second_word: q10.Word,
    third_word: q10.Word,
) -> tuple[tuple[q10.Word, q10.Word, q10.Word, int], ...]:
    """Move ``word`` off the transposed input onto the other three slots."""

    states: dict[tuple[q10.Word, q10.Word, q10.Word], int] = {
        (first_word, second_word, third_word): 1
    }
    for axis in word:
        updated: dict[tuple[q10.Word, q10.Word, q10.Word], int] = defaultdict(int)
        for (first, second, third), multiplicity in states.items():
            updated[((axis, *first), second, third)] += multiplicity
            updated[(first, (axis, *second), third)] += multiplicity
            updated[(first, second, (axis, *third))] += multiplicity
        states = dict(updated)
    sign = -1 if len(word) & 1 else 1
    return tuple((*key, sign * multiplicity) for key, multiplicity in states.items())


def _physical_transpose(
    ell3: list[dict[TRowKey, q10.Q10]],
    pairing: Mapping[q10.LinearKey, q10.Q10],
    degrees: tuple[int, ...],
    *,
    Maxwell_weight_mutation: bool = False,
) -> tuple[list[dict[TRowKey, q10.Q10]], list[dict[TRowKey, q10.Q10]]]:
    pair_by_left: dict[int, tuple[int, q10.Q10]] = {}
    pair_by_right: dict[int, tuple[int, q10.Q10]] = {}
    for (left, right, word), coefficient in pairing.items():
        if word or left in pair_by_left or right in pair_by_right:
            raise ValueError("typed retained pairing is not an order-zero bijection")
        pair_by_left[left] = right, coefficient
        pair_by_right[right] = left, coefficient
    if set(pair_by_left) != set(range(36)) or set(pair_by_right) != set(range(36)):
        raise ValueError("typed retained pairing is incomplete")

    actual: list[dict[TRowKey, q10.Q10]] = [dict() for _ in range(36)]
    predicted: list[dict[TRowKey, q10.Q10]] = [dict() for _ in range(36)]
    for output, row in enumerate(ell3):
        paired_field, output_pairing = pair_by_left[output]
        if degrees[output] != 1 or degrees[paired_field] != 0:
            continue
        output_weight = _positive_weight(output_pairing)
        if Maxwell_weight_mutation and output >= 26:
            output_weight = q10.ONE
        for key, coefficient in row.items():
            first, second, third, first_word, second_word, third_word = key
            if (degrees[first], degrees[second], degrees[third]) != (0, 0, 0):
                continue
            arity3._add_ternary(actual[output], key, coefficient)
            transposed_output, first_pairing = pair_by_right[first]
            first_weight = _positive_weight(first_pairing)
            if Maxwell_weight_mutation and transposed_output >= 26:
                first_weight = q10.ONE
            transposed_coefficient = q10.qmul(
                coefficient, _qdiv(output_weight, first_weight)
            )
            for (
                new_first_word,
                new_second_word,
                new_third_word,
                multiplicity,
            ) in _formal_adjoint_distributions(
                first_word, (), second_word, third_word
            ):
                arity3._add_ternary(
                    predicted[transposed_output],
                    (
                        paired_field,
                        second,
                        third,
                        new_first_word,
                        new_second_word,
                        new_third_word,
                    ),
                    q10.qscale(transposed_coefficient, multiplicity),
                )
    return actual, predicted


def _defect_count(
    actual: list[dict[TRowKey, q10.Q10]],
    predicted: list[dict[TRowKey, q10.Q10]],
) -> tuple[int, int]:
    coefficients = 0
    rows = 0
    for expected, computed in zip(actual, predicted, strict=True):
        defects = sum(
            expected.get(key, q10.ZERO) != computed.get(key, q10.ZERO)
            for key in set(expected) | set(computed)
        )
        coefficients += defects
        rows += bool(defects)
    return coefficients, rows


def scientific_replay() -> dict[str, Any]:
    started = time.monotonic()
    carrier = retained._strict(retained.CARRIER, retained.CARRIER_SCHEMA)
    legacy = retained._strict(retained.LEGACY_CARRIER, retained.LEGACY_CARRIER_SCHEMA)
    payload = retained._strict(retained.RETAINED_Q3_MIXED, retained.RETAINED_Q3_SCHEMA)
    ell3 = retained._parse_q3(payload, 36, retained.RETAINED_Q3_ROW_SCHEMA)
    pairing = _parse_operator(
        carrier["retained_complex"]["typed_cyclic_pairing"],
        shape=(36, 36),
        name="typed_omega36",
    )
    degrees = tuple(
        row["degree"] for row in legacy["retained_complex"]["component_rows"]
    )
    if len(degrees) != 36:
        raise ValueError("retained degree ledger drifted")

    actual, predicted = _physical_transpose(ell3, pairing, degrees)
    defect_count, defect_rows = _defect_count(actual, predicted)
    mutant_actual, mutant_predicted = _physical_transpose(
        ell3, pairing, degrees, Maxwell_weight_mutation=True
    )
    if mutant_actual != actual:
        raise ValueError("pairing-weight mutation changed the imported ell3")
    mutation_defect_count, mutation_defect_rows = _defect_count(
        actual, mutant_predicted
    )

    total = sum(map(len, ell3))
    physical = sum(map(len, actual))
    gravity_physical = sum(map(len, actual[:26]))
    Maxwell_physical = physical - gravity_physical
    nonphysical = total - physical
    accepted = (
        total == 25_950
        and physical == 25_662
        and defect_count == 0
        and defect_rows == 0
        and mutation_defect_count > 0
        and mutation_defect_rows > 0
        and nonphysical == 288
    )
    return {
        "backend": "independent-Q(sqrt(10))-PBW-physical-quartic-cyclicity-v1",
        "classical_commit": retained.CLASSICAL_COMMIT,
        "input_hashes": {
            "typed_carrier": retained._sha256(retained._blob(retained.CARRIER)),
            "legacy_layout_carrier": retained._sha256(
                retained._blob(retained.LEGACY_CARRIER)
            ),
            "retained_mixed_ell3_manifest": retained._sha256(
                retained._blob(retained.RETAINED_Q3_MIXED)
            ),
        },
        "diagnostics": {
            "retained_ell3_coefficient_count": total,
            "physical_quartic_coefficient_count": physical,
            "physical_gravity_output_coefficient_count": gravity_physical,
            "physical_Maxwell_output_coefficient_count": Maxwell_physical,
            "physical_quartic_cyclicity_defect_count": defect_count,
            "physical_quartic_cyclicity_defect_rows": defect_rows,
            "Maxwell_pairing_weight_mutation_defect_count": mutation_defect_count,
            "Maxwell_pairing_weight_mutation_defect_rows": mutation_defect_rows,
            "nonphysical_ghost_antifield_completion_coefficient_count": nonphysical,
        },
        "verdict": (
            "ACCEPTED_RETAINED_MIXED_ELL3_PHYSICAL_QUARTIC_CYCLICITY_LOCAL_ALGEBRAIC"
            if accepted
            else "REJECTED_RETAINED_MIXED_ELL3_PHYSICAL_QUARTIC_CYCLICITY"
        ),
        "elapsed_seconds": round(time.monotonic() - started, 6),
    }


if __name__ == "__main__":
    import json

    print(json.dumps(scientific_replay(), indent=2, sort_keys=True))
