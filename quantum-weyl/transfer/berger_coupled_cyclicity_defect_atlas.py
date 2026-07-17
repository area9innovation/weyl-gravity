"""Exact localization atlas for the coupled Berger cyclicity obstruction."""

from __future__ import annotations

from collections import Counter
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any, Callable, Mapping

from . import berger_coupled_36_transfer_replay as replay_import
from . import berger_qsqrt10_replay as q10
from .berger_retained_26_q2_transfer import _cyclicity_defect


HERE = Path(__file__).resolve().parent
REPLAY_CERTIFICATE = HERE / "certificates/BERGER_COUPLED_36_TRANSFER_INDEPENDENT_REPLAY.json"
PAYLOAD_PATH = HERE / "certificates/BERGER_COUPLED_RETAINED_CYCLICITY_DEFECT_PAYLOAD.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_hash(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _category(index: int) -> str:
    if index < 3:
        return "gravity_ghost"
    if index < 13:
        return "gravity_metric"
    if index < 23:
        return "gravity_metric_antifield"
    if index < 26:
        return "gravity_ghost_antifield"
    if index == 26:
        return "Maxwell_ghost"
    if index < 31:
        return "Maxwell_potential"
    if index < 35:
        return "Maxwell_potential_antifield"
    return "Maxwell_ghost_antifield"


def _defect_payload(
    defect: Mapping[q10.TrilinearKey, q10.Q10], rows: list[dict[str, Any]]
) -> dict[str, Any]:
    entries = [
        [
            first,
            second,
            third,
            list(first_word),
            list(second_word),
            q10._coefficient(coefficient),
        ]
        for (first, second, third, first_word, second_word), coefficient in sorted(defect.items())
    ]
    body = {
        "schema": "quantum-weyl-berger-coupled-retained-cyclicity-defect-payload-v1",
        "result_id": "BERGER_COUPLED_RETAINED_CYCLICITY_DEFECT_PAYLOAD",
        "coefficient_field": "Q(sqrt(10))",
        "shape": [36, 36, 36],
        "row_ids": [row["row_id"] for row in rows],
        "entries": entries,
    }
    return {**body, "canonical_sha256": _canonical_hash(body)}


def _counter_rows(counter: Counter, fields: tuple[str, ...]) -> list[dict[str, Any]]:
    return [
        {**dict(zip(fields, key if isinstance(key, tuple) else (key,))), "count": count}
        for key, count in sorted(counter.items(), key=lambda item: (-item[1], item[0]))
    ]


def _scaled(
    q2: Mapping[q10.BilinearKey, q10.Q10], scale: Callable[[int], int | Fraction]
) -> dict[q10.BilinearKey, q10.Q10]:
    return {
        key: q10.qmul(value, (Fraction(scale(key[0])), Fraction(0)))
        for key, value in q2.items()
    }


def _flip_pairs(
    pairing: Mapping[tuple[int, int], q10.Q10], pairs: tuple[tuple[int, int], ...]
) -> dict[tuple[int, int], q10.Q10]:
    output = dict(pairing)
    for left, right in pairs:
        output[left, right] = q10.qneg(output[left, right])
        output[right, left] = q10.qneg(output[right, left])
    return output


def _lowered_zero_jet(
    q2: Mapping[q10.BilinearKey, q10.Q10],
    pairing: Mapping[tuple[int, int], q10.Q10],
    first: int,
    second: int,
    third: int,
) -> q10.Q10:
    total = q10.ZERO
    for (output, left, right, left_word, right_word), coefficient in q2.items():
        if left == first and right == second and not left_word and not right_word:
            pair_coefficient = pairing.get((output, third))
            if pair_coefficient is not None:
                total = q10.qadd(total, q10.qmul(coefficient, pair_coefficient))
    return total


def build() -> tuple[dict[str, Any], dict[str, Any]]:
    replay_certificate = json.loads(REPLAY_CERTIFICATE.read_text())
    if (
        replay_certificate.get("result_state")
        != "TRANSFER_AND_Q1Q2_REPLAYED_CYCLICITY_OBSTRUCTION_FOUND"
        or replay_certificate.get("cyclicity_obstruction", {}).get(
            "retained_36_defect_coefficient_count"
        )
        != 953
    ):
        raise ValueError("independent replay obstruction dependency drifted")

    carrier = replay_import._git_json(replay_import.CARRIER_RELATIVE)
    retained = carrier["retained_complex"]
    rows = retained["component_rows"]
    degrees = tuple(row["degree"] for row in rows)
    q1 = replay_import._parse_operator(
        retained["classical_unary_q1"], shape=(36, 36), name="q36"
    )
    pairing = replay_import._pairing(retained["cyclic_pairing"])
    q2 = replay_import._parse_transferred(
        replay_import._git_json(replay_import.TRANSFER_PAYLOAD_RELATIVE)
    )
    defect = _cyclicity_defect(q2, pairing, degrees)
    if len(defect) != 953 or q10.arity_two_defect(q1, q2, degrees):
        raise ValueError("obstructed retained fixture drifted")
    payload = _defect_payload(defect, rows)

    field_categories: Counter = Counter()
    Maxwell_slots: Counter = Counter()
    jet_orders: Counter = Counter()
    degree_triples: Counter = Counter()
    row_triples: Counter = Counter()
    rationality: Counter = Counter()
    coefficients: Counter = Counter()
    for (first, second, third, first_word, second_word), coefficient in defect.items():
        field_categories[_category(first), _category(second), _category(third)] += 1
        Maxwell_slots[sum(index >= 26 for index in (first, second, third))] += 1
        jet_orders[len(first_word) + len(second_word)] += 1
        degree_triples[degrees[first], degrees[second], degrees[third]] += 1
        row_triples[rows[first]["row_id"], rows[second]["row_id"], rows[third]["row_id"]] += 1
        rationality["sqrt10_bearing" if coefficient[1] else "rational_only"] += 1
        coefficients[coefficient] += 1

    Maxwell_pairs = ((26, 35), (27, 31), (28, 32), (29, 33), (30, 34))
    ghost_pair = (Maxwell_pairs[0],)
    potential_pairs = Maxwell_pairs[1:]
    pairing_sweep = []
    for name, pairs in (
        ("exported", ()),
        ("flip_Maxwell_ghost_pair", ghost_pair),
        ("flip_all_Maxwell_potential_pairs", potential_pairs),
        ("flip_entire_Maxwell_pairing", Maxwell_pairs),
    ):
        candidate_pairing = _flip_pairs(pairing, pairs)
        pairing_sweep.append(
            {
                "convention": name,
                "retained_cyclicity_defect_count": len(
                    _cyclicity_defect(q2, candidate_pairing, degrees)
                ),
            }
        )

    scaling_cases = (
        ("exported", lambda output: 1),
        ("uniform_Maxwell_output_x2", lambda output: 2 if output >= 26 else 1),
        (
            "cyclic_but_nonchain_sector_scaling",
            lambda output: -2 if output in (26, 35) else 2 if output >= 26 else 1,
        ),
    )
    scaling_sweep = []
    for name, scale in scaling_cases:
        candidate = _scaled(q2, scale)
        scaling_sweep.append(
            {
                "convention": name,
                "retained_cyclicity_defect_count": len(
                    _cyclicity_defect(candidate, pairing, degrees)
                ),
                "retained_q1_q2_defect_count": len(
                    q10.arity_two_defect(q1, candidate, degrees)
                ),
            }
        )

    row_by_id = {row["row_id"]: row["index"] for row in rows}
    h00 = row_by_id["h_hat_00"]
    A1 = row_by_id["A_1"]
    hstar00 = row_by_id["h_hat_star_00"]
    Aplus1 = row_by_id["A_plus_1"]
    orbit = {
        "rows": {"h_hat_00": h00, "A_1": A1, "h_hat_star_00": hstar00, "A_plus_1": Aplus1},
        "raw_q2_coefficients": {
            "q2_A1_A1_to_h_hat_star_00": q10._coefficient(
                q2[hstar00, A1, A1, (), ()]
            ),
            "q2_h_hat_00_A1_to_A_plus_1": q10._coefficient(
                q2[Aplus1, h00, A1, (), ()]
            ),
            "q2_A1_h_hat_00_to_A_plus_1": q10._coefficient(
                q2[Aplus1, A1, h00, (), ()]
            ),
        },
        "lowered_cubic_orbit": [
            {
                "slots": ["h_hat_00", "A_1", "A_1"],
                "coefficient": q10._coefficient(
                    _lowered_zero_jet(q2, pairing, h00, A1, A1)
                ),
            },
            {
                "slots": ["A_1", "h_hat_00", "A_1"],
                "coefficient": q10._coefficient(
                    _lowered_zero_jet(q2, pairing, A1, h00, A1)
                ),
            },
            {
                "slots": ["A_1", "A_1", "h_hat_00"],
                "coefficient": q10._coefficient(
                    _lowered_zero_jet(q2, pairing, A1, A1, h00)
                ),
            },
        ],
        "normalized_defect_witnesses": [
            {
                "slots": [rows[index]["row_id"] for index in key[:3]],
                "left_word": list(key[3]),
                "right_word": list(key[4]),
                "coefficient": q10._coefficient(value),
            }
            for key, value in sorted(defect.items())
            if key[:3] in ((h00, A1, A1), (A1, A1, h00))
            and not key[3]
            and not key[4]
        ],
        "factor_two_diagnosis": (
            "the gravity-antifield output coefficient is 40/9 while each Maxwell-antifield "
            "output coefficient is 20/9; multiplying all Maxwell-output q2 terms by two "
            "repairs this orbit and all 938 potential-sector defects without breaking q1/q2"
        ),
    }

    certificate = {
        "schema": "quantum-weyl-berger-coupled-cyclicity-defect-atlas-v1",
        "result_id": "BERGER_COUPLED_CYCLICITY_DEFECT_ATLAS",
        "result_state": "EXACT_DEFECT_LOCALIZED_FACTOR_TWO_PARTIAL_REPAIR_IDENTIFIED",
        "lifecycle_layer": "CLASSICAL_BV_IMPORT_DIAGNOSTIC",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "dependency_ref": {
            "path": str(REPLAY_CERTIFICATE.relative_to(HERE.parents[1])),
            "result_id": replay_certificate["result_id"],
            "sha256": _sha256(REPLAY_CERTIFICATE),
        },
        "defect_payload": {
            "path": str(PAYLOAD_PATH.relative_to(HERE.parents[1])),
            "entry_count": len(payload["entries"]),
            "canonical_sha256": payload["canonical_sha256"],
        },
        "retained_atlas": {
            "total_defect_coefficients": len(defect),
            "Maxwell_slot_counts": _counter_rows(Maxwell_slots, ("Maxwell_slots",)),
            "jet_order_counts": _counter_rows(jet_orders, ("total_jet_order",)),
            "field_category_counts": _counter_rows(
                field_categories, ("first", "second", "third")
            ),
            "degree_triple_counts": _counter_rows(
                degree_triples, ("first_degree", "second_degree", "third_degree")
            ),
            "coefficient_field_counts": _counter_rows(rationality, ("kind",)),
            "distinct_coefficients": len(coefficients),
            "top_row_triples": _counter_rows(
                Counter(dict(row_triples.most_common(20))),
                ("first", "second", "third"),
            ),
        },
        "minimal_hAA_fixture": orbit,
        "convention_sweep": {
            "pairing_sign_cases": pairing_sweep,
            "output_scaling_cases": scaling_sweep,
            "verdict": (
                "natural Maxwell pairing sign flips do not reduce the 953-term defect; "
                "uniform Maxwell-output x2 preserves q1/q2 and reduces it to the 15-term "
                "ghost-density sector; the only tested diagonal output scaling that makes "
                "cyclicity vanish creates 108 q1/q2 defects and is inadmissible"
            ),
        },
        "claim_flags": {
            "EXACT_RETAINED_CYCLICITY_DEFECT_ATLAS": True,
            "EVERY_DEFECT_HAS_EXACTLY_TWO_MAXWELL_LEGS": True,
            "PHYSICAL_HAA_FACTOR_TWO_SEAM": True,
            "PAIRING_SIGN_ONLY_REPAIR_FOUND": False,
            "UNIFORM_MAXWELL_OUTPUT_X2_PRESERVES_Q1Q2": True,
            "UNIFORM_MAXWELL_OUTPUT_X2_COMPLETE_REPAIR": False,
            "COMPLETE_ADMISSIBLE_CYCLIC_REPAIR_FOUND": False,
            "MIXED_Q3_TRANSFERRED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "REPAIR_REMAINING_15_GHOST_DENSITY_DEFECTS_WITH_Q1Q2_PRESERVED",
        "claim_boundary": (
            "This LOCAL-ALGEBRAIC diagnostic exports all 953 normalized retained cyclicity "
            "defect coefficients and localizes them by field content, cohomological degree, "
            "jet order and row triple. Every defect has exactly two Maxwell legs; 800 lie in "
            "the physical hAA sector, 138 in the diffeomorphism-ghost/potential-antifield "
            "completion and 15 in the Maxwell ghost-density completion. A uniform factor two "
            "on Maxwell-output q2 terms preserves the retained q1/q2 identity and removes the "
            "first 938 defects, but it leaves the 15 ghost-density defects. A further tested "
            "sector sign scaling makes cyclicity vanish only by creating 108 q1/q2 defects, so "
            "it is explicitly inadmissible. This atlas is a repair target, not a corrected q2, "
            "mixed-q3, causal, QME, particle, unitarity or quantum theorem."
        ),
    }
    _validate(certificate, payload)
    return certificate, payload


def _validate(certificate: dict[str, Any], payload: dict[str, Any]) -> None:
    atlas = certificate["retained_atlas"]
    flags = certificate["claim_flags"]
    scaling = {
        row["convention"]: row
        for row in certificate["convention_sweep"]["output_scaling_cases"]
    }
    if (
        atlas["total_defect_coefficients"] != 953
        or payload["canonical_sha256"] != _canonical_hash(
            {key: payload[key] for key in payload if key != "canonical_sha256"}
        )
        or scaling["uniform_Maxwell_output_x2"]["retained_cyclicity_defect_count"] != 15
        or scaling["uniform_Maxwell_output_x2"]["retained_q1_q2_defect_count"] != 0
        or scaling["cyclic_but_nonchain_sector_scaling"]["retained_cyclicity_defect_count"] != 0
        or scaling["cyclic_but_nonchain_sector_scaling"]["retained_q1_q2_defect_count"] != 108
        or flags["COMPLETE_ADMISSIBLE_CYCLIC_REPAIR_FOUND"] is not False
        or flags["QUANTUM_CLAIM"] is not False
    ):
        raise ValueError("cyclicity defect atlas boundary drifted")
