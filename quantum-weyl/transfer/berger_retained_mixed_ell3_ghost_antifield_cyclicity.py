"""Independent full-BV cyclicity replay for the retained Berger mixed ell3.

This extends the separately certified degree-zero physical transpose to the
288 retained ghost/antifield completion coefficients.  The suspended-Darboux
transpose uses the exact absolute component weights and the convention sign

    (-1)^(|x||u| + eps_2(x) + eps_2(u)),

where ``u`` is the component paired with the output and ``eps_2`` records a
degree-two ghost-antifield coordinate.  No producer code is imported.
"""

from __future__ import annotations

import time
from typing import Any, Mapping

from . import berger_mixed_q3_acceptance as arity3
from . import berger_qsqrt10_replay as q10
from .berger_coupled_36_transfer_replay import _parse_operator
from . import berger_retained_mixed_ell3_acceptance as retained
from .berger_retained_mixed_ell3_physical_cyclicity import (
    _defect_count,
    _formal_adjoint_distributions,
    _physical_pairing_weight_ledger,
    _positive_weight,
    _qdiv,
)


TRowKey = arity3.TRowKey


def _transpose_sign(first_degree: int, paired_output_degree: int) -> int:
    """Suspended Koszul sign with the degree-two Darboux polarization."""

    exponent = (
        ((first_degree & 1) * (paired_output_degree & 1))
        ^ (first_degree == 2)
        ^ (paired_output_degree == 2)
    )
    return -1 if exponent else 1


def _full_bv_transpose(
    ell3: list[dict[TRowKey, q10.Q10]],
    pairing: Mapping[q10.LinearKey, q10.Q10],
    degrees: tuple[int, ...],
    *,
    omit_degree_two_polarization: bool = False,
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
        paired_output, output_pairing = pair_by_left[output]
        output_weight = _positive_weight(output_pairing)
        for key, coefficient in row.items():
            first, second, third, first_word, second_word, third_word = key
            arity3._add_ternary(actual[output], key, coefficient)
            transposed_output, first_pairing = pair_by_right[first]
            first_weight = _positive_weight(first_pairing)
            if omit_degree_two_polarization:
                sign = (
                    -1
                    if (degrees[first] & 1) * (degrees[paired_output] & 1)
                    else 1
                )
            else:
                sign = _transpose_sign(degrees[first], degrees[paired_output])
            transposed_coefficient = q10.qscale(
                q10.qmul(coefficient, _qdiv(output_weight, first_weight)), sign
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
                        paired_output,
                        second,
                        third,
                        new_first_word,
                        new_second_word,
                        new_third_word,
                    ),
                    q10.qscale(transposed_coefficient, multiplicity),
                )
    return actual, predicted


def scientific_replay() -> dict[str, Any]:
    started = time.monotonic()
    carrier = retained._strict(retained.CARRIER, retained.CARRIER_SCHEMA)
    legacy = retained._strict(
        retained.LEGACY_CARRIER, retained.LEGACY_CARRIER_SCHEMA
    )
    payload = retained._strict(
        retained.RETAINED_Q3_MIXED, retained.RETAINED_Q3_SCHEMA
    )
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

    pairing_weight_ledger = _physical_pairing_weight_ledger(pairing, degrees)
    actual, predicted = _full_bv_transpose(ell3, pairing, degrees)
    defect_count, defect_rows = _defect_count(actual, predicted)
    _, mutant = _full_bv_transpose(
        ell3, pairing, degrees, omit_degree_two_polarization=True
    )
    mutation_defect_count, mutation_defect_rows = _defect_count(actual, mutant)

    physical = 0
    completion = 0
    completion_positive_sign = 0
    completion_negative_sign = 0
    completion_output_rows: set[int] = set()
    for output, row in enumerate(ell3):
        paired_output, _ = next(
            (right, coefficient)
            for (left, right, word), coefficient in pairing.items()
            if left == output and not word
        )
        for first, second, third, *_words in row:
            if degrees[output] == 1 and (
                degrees[first], degrees[second], degrees[third]
            ) == (0, 0, 0):
                physical += 1
                continue
            completion += 1
            completion_output_rows.add(output)
            if _transpose_sign(degrees[first], degrees[paired_output]) == 1:
                completion_positive_sign += 1
            else:
                completion_negative_sign += 1

    accepted = (
        physical == 25_662
        and completion == 288
        and completion_positive_sign == 120
        and completion_negative_sign == 168
        and defect_count == 0
        and defect_rows == 0
        and mutation_defect_count > 0
        and mutation_defect_rows > 0
    )
    return {
        "backend": "independent-Q(sqrt(10))-PBW-full-BV-quartic-cyclicity-v1",
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
            "retained_ell3_coefficient_count": sum(len(row) for row in ell3),
            "physical_quartic_coefficient_count": physical,
            "ghost_antifield_completion_coefficient_count": completion,
            "ghost_antifield_completion_output_rows": sorted(
                completion_output_rows
            ),
            "ghost_antifield_positive_transpose_sign_count": completion_positive_sign,
            "ghost_antifield_negative_transpose_sign_count": completion_negative_sign,
            "full_BV_cyclicity_defect_count": defect_count,
            "full_BV_cyclicity_defect_rows": defect_rows,
            "omitted_degree_two_polarization_mutation_defect_count": mutation_defect_count,
            "omitted_degree_two_polarization_mutation_defect_rows": mutation_defect_rows,
            "physical_pairing_weight_ledger": pairing_weight_ledger,
        },
        "verdict": (
            "ACCEPTED_RETAINED_MIXED_ELL3_FULL_BV_CYCLICITY_LOCAL_ALGEBRAIC"
            if accepted
            else "REJECTED_RETAINED_MIXED_ELL3_FULL_BV_CYCLICITY"
        ),
        "elapsed_seconds": round(time.monotonic() - started, 6),
    }


if __name__ == "__main__":
    import json

    print(json.dumps(scientific_replay(), indent=2, sort_keys=True))
