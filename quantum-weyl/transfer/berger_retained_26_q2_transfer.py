"""Exact transfer of the complete Berger q2 from 54 bare rows to 26 retained rows.

The output is deliberately called ``q2_26``.  It is the binary Taylor
operation on the retained complex supplied by the 54-to-26 SDR, not yet a
minimal residual/cohomology bracket.
"""

from __future__ import annotations

from collections import defaultdict
from functools import lru_cache
import hashlib
import json
from typing import Any, Iterable, Mapping

from . import berger_gauge_fixed_nonminimal_import as gauge_import
from . import berger_qsqrt10_replay as q10
from . import berger_support_local_q2_import as q2_import


Q10 = q10.Q10
Word = q10.Word
LinearKey = q10.LinearKey
BilinearKey = q10.BilinearKey
RETAINED_DEGREES = (-1,) * 3 + (0,) * 10 + (1,) * 10 + (2,) * 3
RETAINED_ROW_IDS = (
    "c_spatial_1", "c_spatial_2", "c_spatial_3",
    "h_hat_00", "h_hat_01", "h_hat_02", "h_hat_03", "h_hat_11",
    "h_hat_12", "h_hat_13", "h_hat_22", "h_hat_23", "h_hat_33",
    "h_hat_star_00", "h_hat_star_01", "h_hat_star_02", "h_hat_star_03",
    "h_hat_star_11", "h_hat_star_12", "h_hat_star_13", "h_hat_star_22",
    "h_hat_star_23", "h_hat_star_33",
    "c_spatial_star_1", "c_spatial_star_2", "c_spatial_star_3",
)


def _canonical_hash(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _parse_operator(
    record: Mapping[str, Any], *, shape: tuple[int, int], name: str
) -> dict[LinearKey, Q10]:
    if record.get("shape") != list(shape) or not isinstance(record.get("entries"), list):
        raise ValueError(f"{name} shape drifted")
    body = {"shape": record["shape"], "entries": record["entries"]}
    if record.get("sha256") != _canonical_hash(body):
        raise ValueError(f"{name} record hash drifted")
    output: dict[tuple[Any, ...], Q10] = {}
    for target, source, terms in record["entries"]:
        for exponents, raw_coefficient in terms:
            expression = q10.arrival.parse_coefficient(raw_coefficient).subs(
                q2_import.SPECIALIZATION
            )
            coefficient = q10.qfrom_expr(expression)
            for word, pbw_coefficient in q10.pbw_word(q10._word(exponents)):
                q10._add(
                    output,
                    (target, source, word),
                    q10.qmul(coefficient, pbw_coefficient),
                )
    return output  # type: ignore[return-value]


def _retained_q1() -> dict[LinearKey, Q10]:
    q1 = gauge_import._git_json(gauge_import.RETAINED_RELATIVE)
    output: dict[LinearKey, Q10] = {}
    for name, shape, row_offset, column_offset in (
        ("K_spatial", (10, 3), 3, 0),
        ("H_retained", (10, 10), 13, 3),
        ("minus_K_spatial_sharp", (3, 10), 23, 13),
    ):
        parsed = _parse_operator(q1["q1_blocks"][name], shape=shape, name=name)
        for (target, source, word), coefficient in parsed.items():
            q10._add(
                output,
                (target + row_offset, source + column_offset, word),
                coefficient,
            )
    return output  # type: ignore[return-value]


def _retained_pairing() -> dict[tuple[int, int], Q10]:
    pairing: dict[tuple[int, int], Q10] = {}
    for source, dual in (
        *((index, index + 23) for index in range(3)),
        *((index, index + 10) for index in range(3, 13)),
    ):
        pairing[source, dual] = q10.ONE
        pairing[dual, source] = q10.qneg(q10.ONE)
    return pairing


def _cyclicity_defect(
    q2: Mapping[BilinearKey, Q10],
    pairing: Mapping[tuple[int, int], Q10],
    degrees: tuple[int, ...],
) -> dict[q10.TrilinearKey, Q10]:
    """Dimension-generic form of the certified odd-Darboux cyclic check."""

    lhs: dict[q10.TrilinearKey, Q10] = {}
    unsigned_rhs: dict[q10.TrilinearKey, Q10] = {}
    pair_by_left: dict[int, list[tuple[int, Q10]]] = defaultdict(list)
    for (left, right), coefficient in pairing.items():
        pair_by_left[left].append((right, coefficient))
    if (
        len(pair_by_left) != len(degrees)
        or any(len(values) != 1 for values in pair_by_left.values())
        or any(
            coefficient not in {q10.ONE, q10.qneg(q10.ONE)}
            or pairing.get((right, left)) != q10.qneg(coefficient)
            for left, ((right, coefficient),) in pair_by_left.items()
        )
    ):
        raise ValueError("retained cyclic pairing is not odd Darboux")
    dual_slot = {
        index: values[0][1] == q10.qneg(q10.ONE)
        for index, values in pair_by_left.items()
    }
    for (output, first, second, first_word, second_word), coefficient in q2.items():
        for third, pair_coefficient in pair_by_left.get(output, ()):
            lowered = q10.qmul(coefficient, pair_coefficient)
            q10._add_trilinear_normalized(
                lhs, first, second, third, first_word, second_word, (), lowered
            )
            q10._add_trilinear_normalized(
                unsigned_rhs,
                third,
                first,
                second,
                (),
                first_word,
                second_word,
                lowered,
            )
    defect: dict[q10.TrilinearKey, Q10] = {}
    for key in set(lhs) | set(unsigned_rhs):
        first, second, _third, _first_word, _second_word = key
        coefficient = unsigned_rhs.get(key, q10.ZERO)
        if dual_slot[second] ^ bool(
            (degrees[first] & 1) * (degrees[second] & 1)
        ):
            coefficient = q10.qneg(coefficient)
        q10._add(
            defect,
            key,
            q10.qadd(lhs.get(key, q10.ZERO), q10.qneg(coefficient)),
        )
    return defect


def _transfer_inner(
    q2: Mapping[BilinearKey, Q10], iota: Mapping[LinearKey, Q10]
) -> tuple[dict[BilinearKey, Q10], int]:
    iota_by_target: dict[int, list[tuple[int, Word, Q10]]] = defaultdict(list)
    for (target, source, word), coefficient in iota.items():
        iota_by_target[target].append((source, word, coefficient))
    output: dict[BilinearKey, Q10] = {}
    contributions = 0
    for (target, left, right, left_word, right_word), coefficient in q2.items():
        for new_left, left_inner, left_coefficient in iota_by_target.get(left, ()):
            for new_right, right_inner, right_coefficient in iota_by_target.get(right, ()):
                contributions += 1
                q10._add_bilinear_normalized(
                    output,
                    (
                        target,
                        new_left,
                        new_right,
                        left_word + left_inner,
                        right_word + right_inner,
                    ),
                    q10.qmul(
                        coefficient,
                        q10.qmul(left_coefficient, right_coefficient),
                    ),
                )
    return output, contributions


def _transfer_outer(
    intermediate: Mapping[BilinearKey, Q10], projection: Mapping[LinearKey, Q10]
) -> tuple[dict[BilinearKey, Q10], int]:
    projection_by_source: dict[int, list[tuple[int, Word, Q10]]] = defaultdict(list)
    for (target, source, word), coefficient in projection.items():
        projection_by_source[source].append((target, word, coefficient))
    output: dict[BilinearKey, Q10] = {}
    contributions = 0
    for (middle, left, right, left_word, right_word), coefficient in intermediate.items():
        for target, outer_word, projection_coefficient in projection_by_source.get(
            middle, ()
        ):
            for (new_left_word, new_right_word), leibniz_coefficient in q10._leibniz(
                outer_word, left_word, right_word
            ).items():
                contributions += 1
                q10._add_bilinear_normalized(
                    output,
                    (target, left, right, new_left_word, new_right_word),
                    q10.qmul(
                        projection_coefficient,
                        q10.qmul(coefficient, leibniz_coefficient),
                    ),
                )
    return output, contributions


def _payload_rows(q2_26: Mapping[BilinearKey, Q10]) -> list[dict[str, object]]:
    rows: list[list[list[object]]] = [[] for _ in range(26)]
    for (target, left, right, left_word, right_word), coefficient in sorted(q2_26.items()):
        rows[target].append(
            [
                left,
                q10._exponents(left_word),
                right,
                q10._exponents(right_word),
                q10._coefficient(coefficient),
            ]
        )
    return [{"output": index, "terms": terms} for index, terms in enumerate(rows)]


def _maximum_order(q2_26: Mapping[BilinearKey, Q10]) -> int:
    return max(
        (len(left_word) + len(right_word) for _, _, _, left_word, right_word in q2_26),
        default=0,
    )


@lru_cache(maxsize=1)
def compute_retained_q2() -> tuple[dict[str, Any], dict[str, Any]]:
    imported_q2 = q2_import.import_support_local_q2()
    gauge_payload = gauge_import._git_json(gauge_import.CERTIFICATE_RELATIVE)
    contraction = gauge_payload["contraction"]
    iota = _parse_operator(contraction["iota_cl"], shape=(54, 26), name="iota_cl")
    projection = _parse_operator(
        contraction["pi_cl"], shape=(26, 54), name="pi_cl"
    )
    q2_54 = q10._parse_scientific_q2()
    intermediate, inner_contributions = _transfer_inner(q2_54, iota)
    q2_26, outer_contributions = _transfer_outer(intermediate, projection)

    q1_26 = _retained_q1()
    nilpotency = q10.arity_two_defect(q1_26, q2_26, RETAINED_DEGREES)
    cyclicity = _cyclicity_defect(q2_26, _retained_pairing(), RETAINED_DEGREES)
    rows = _payload_rows(q2_26)
    payload_body = {
        "schema": "quantum-weyl-berger-retained-26-q2-payload-v1",
        "setting_id": q10.arrival.SETTING_ID,
        "classical_q2_commit": imported_q2.parsed.classical_commit,
        "shape": [26, 26, 26],
        "coefficient_field": "Q(sqrt(10))",
        "operation_name": "q2_26",
        "factorial_convention": q10.arrival.CONVENTION,
        "row_ids": list(RETAINED_ROW_IDS),
        "degrees": list(RETAINED_DEGREES),
        "rows": rows,
    }
    payload_hash = _canonical_hash(payload_body)
    payload = {**payload_body, "canonical_sha256": payload_hash}
    summary = {
        "input": {
            "q2_54_canonical_sha256": imported_q2.parsed.q2_sha256,
            "q2_54_term_count": imported_q2.parsed.term_count,
            "iota_cl_sha256": contraction["iota_cl"]["sha256"],
            "pi_cl_sha256": contraction["pi_cl"]["sha256"],
        },
        "operation": {
            "name": "q2_26",
            "formula": "q2_26=pi_26 q2_54(iota_26 tensor iota_26)",
            "target": "retained_26_row_complex",
            "not_yet": "minimal_residual_or_cohomology_ell2",
            "nonzero_coefficient_count": len(q2_26),
            "nonzero_output_rows": sum(bool(row["terms"]) for row in rows),
            "maximum_total_jet_order": _maximum_order(q2_26),
            "payload_canonical_sha256": payload_hash,
        },
        "work_ledger": {
            "q2_54_PBW_coefficients": len(q2_54),
            "iota_PBW_coefficients": len(iota),
            "pi_PBW_coefficients": len(projection),
            "inner_raw_contributions": inner_contributions,
            "after_inner_canonical_coefficients": len(intermediate),
            "outer_Leibniz_contributions": outer_contributions,
        },
        "exact_checks": {
            "cohomological_degree_one": all(
                RETAINED_DEGREES[target]
                == RETAINED_DEGREES[left] + RETAINED_DEGREES[right] + 1
                for target, left, right, _, _ in q2_26
            ),
            "q1_q2_arity_two_nilpotency": not nilpotency,
            "odd_Darboux_BV_cyclicity": not cyclicity,
            "exact_quadratic_field": True,
            "no_floating_point": True,
        },
        "defects": {
            "q1_q2": q10._summary(nilpotency, kind="q1_q2"),
            "BV_cyclicity": q10._summary(cyclicity, kind="cyclicity"),
        },
    }
    if not all(summary["exact_checks"].values()):
        raise ValueError("retained q2_26 failed an exact identity")
    return payload, summary
