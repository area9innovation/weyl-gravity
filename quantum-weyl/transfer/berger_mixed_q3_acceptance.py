"""Independent exact consumer for the typed Berger gravity--Maxwell q3.

The classical producer is never imported or executed.  This module reads the
content-addressed portable tensors at the pinned commit, represents
``Q(sqrt(10))`` as two rational components, and recomputes the mixed arity-three
coderivation identity row by row.
"""

from __future__ import annotations

from collections import defaultdict
from fractions import Fraction
from functools import lru_cache
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import time
from typing import Any, Iterable, Mapping

from jsonschema import Draft202012Validator
from local_bv.schema_validation import validate_instance

from . import berger_coupled_36_transfer_replay as replay
from . import berger_qsqrt10_replay as q10


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CLASSICAL_COMMIT = "ba51c3853cbb51ef38083b40ceb7e9dda023efa7"
CERTIFICATE = "d_quotient_classical/certificates/BERGER_SUPPORT_LOCAL_COUPLED_MAXWELL_Q3.json"
Q2_TYPED = "d_quotient_classical/certificates/BERGER_SUPPORT_LOCAL_COUPLED_MAXWELL_Q2_TYPED_PAYLOAD.json"
Q3_PAYLOAD = "d_quotient_classical/certificates/BERGER_SUPPORT_LOCAL_COUPLED_MAXWELL_Q3_PAYLOAD.json"
GRAVITY_Q2 = "d_quotient_classical/certificates/BERGER_SUPPORT_LOCAL_Q2_PAYLOAD.json"
CARRIER = "d_quotient_classical/certificates/BERGER_PORTABLE_COUPLED_64_UNARY_PAIRING_36_SDR.json"
SCHEMAS = {
    CERTIFICATE: "d_quotient_classical/schema/berger-support-local-coupled-maxwell-q3-v1.schema.json",
    Q2_TYPED: "d_quotient_classical/schema/berger-support-local-coupled-maxwell-q2-typed-payload-v1.schema.json",
    Q3_PAYLOAD: "d_quotient_classical/schema/berger-support-local-coupled-maxwell-q3-payload-v1.schema.json",
}
ROW_SCHEMA = "d_quotient_classical/schema/berger-support-local-coupled-maxwell-q3-row-v1.schema.json"

Word = q10.Word
Q10 = q10.Q10
BRowKey = tuple[int, int, Word, Word]
TRowKey = tuple[int, int, int, Word, Word, Word]


def _git_prefix() -> str:
    return subprocess.check_output(
        ["git", "rev-parse", "--show-prefix"], cwd=ROOT, text=True
    ).strip()


@lru_cache(maxsize=None)
def _blob(relative: str) -> bytes:
    result = subprocess.run(
        ["git", "show", f"{CLASSICAL_COMMIT}:{_git_prefix()}{relative}"],
        cwd=ROOT,
        check=False,
        capture_output=True,
    )
    if result.returncode:
        raise ValueError(f"missing pinned mixed q3 artifact: {relative}")
    return result.stdout


def _json(relative: str) -> dict[str, Any]:
    value = json.loads(_blob(relative))
    if not isinstance(value, dict):
        raise ValueError(f"pinned JSON is not an object: {relative}")
    return value


def _sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _canonical_hash(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _coefficient(value: object) -> Q10:
    if not isinstance(value, dict) or set(value) != {"rational", "sqrt10"}:
        raise ValueError("coefficient escaped Q(sqrt(10))")

    def component(raw: object) -> Fraction:
        if type(raw) is int:
            return Fraction(raw)
        if (
            isinstance(raw, dict)
            and set(raw) == {"numerator", "denominator"}
            and type(raw["numerator"]) is int
            and type(raw["denominator"]) is int
            and raw["denominator"]
        ):
            return Fraction(raw["numerator"], raw["denominator"])
        raise ValueError("coefficient component is not an exact rational")

    return component(value["rational"]), component(value["sqrt10"])


def _word(exponents: Iterable[int]) -> Word:
    return tuple(
        axis for axis, count in enumerate(tuple(exponents)) for _ in range(count)
    )


def _strict_inputs() -> tuple[dict[str, Any], ...]:
    values: dict[str, dict[str, Any]] = {}
    for artifact, schema_path in SCHEMAS.items():
        instance, schema = _json(artifact), _json(schema_path)
        Draft202012Validator.check_schema(schema)
        if (
            schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema"
            or schema.get("additionalProperties") is not False
        ):
            raise ValueError(f"mixed q3 schema is not strict Draft 2020-12: {schema_path}")
        errors = validate_instance(instance, schema)
        if errors:
            raise ValueError(f"mixed q3 strict schema failure: {'; '.join(errors)}")
        values[artifact] = instance
    certificate = values[CERTIFICATE]
    if (
        certificate.get("result_id") != "BERGER_SUPPORT_LOCAL_COUPLED_MAXWELL_Q3"
        or certificate.get("dependency_tags") != ["LOCAL-ALGEBRAIC"]
        or certificate.get("flags", {}).get("BERGER_RETAINED_MIXED_ELL3_TRANSFER") is not False
        or certificate.get("flags", {}).get("BERGER_MIXED_Q3_INDEPENDENT_QUANTUM_ACCEPTANCE") is not False
        or certificate.get("flags", {}).get("QUANTUM_CLAIM") is not False
    ):
        raise ValueError("mixed q3 producer identity or claim boundary drifted")
    for dependency in certificate["dependency_refs"].values():
        if _sha256(_blob(dependency["path"])) != dependency["sha256"]:
            raise ValueError(f"mixed q3 dependency hash drifted: {dependency['path']}")
    return certificate, values[Q2_TYPED], values[Q3_PAYLOAD]


def _parse_q2(payload: Mapping[str, Any], total_rows: int) -> list[dict[BRowKey, Q10]]:
    rows: list[dict[BRowKey, Q10]] = [dict() for _ in range(total_rows)]
    for record in payload["rows"]:
        target = record["output"]
        if not 0 <= target < total_rows:
            raise ValueError("q2 output escaped declared row range")
        for left, left_word, right, right_word, raw in record["terms"]:
            key = (left, right, _word(left_word), _word(right_word))
            q10._add(rows[target], key, _coefficient(raw))
    return rows


def _parse_q3(payload: Mapping[str, Any]) -> list[dict[TRowKey, Q10]]:
    schema = _json(ROW_SCHEMA)
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)
    rows: list[dict[TRowKey, Q10]] = [dict() for _ in range(64)]
    seen: set[int] = set()
    for chunk in payload["chunks"]:
        raw = _blob(chunk["path"])
        if raw[4:8] != b"\x00\x00\x00\x00" or _sha256(raw) != chunk["file_sha256"]:
            raise ValueError(f"q3 chunk integrity failed: {chunk['output']}")
        record = json.loads(gzip.decompress(raw))
        validator.validate(record)
        body = {"output": record["output"], "terms": record["terms"]}
        if (
            _canonical_hash(body) != record["canonical_sha256"]
            or record["canonical_sha256"] != chunk["canonical_sha256"]
            or record["output"] in seen
        ):
            raise ValueError(f"q3 row canonical ledger failed: {chunk['output']}")
        seen.add(record["output"])
        for first, first_word, second, second_word, third, third_word, raw_coefficient in record["terms"]:
            key = (
                first,
                second,
                third,
                _word(first_word),
                _word(second_word),
                _word(third_word),
            )
            q10._add(rows[record["output"]], key, _coefficient(raw_coefficient))
    if seen != set(range(64)):
        raise ValueError("q3 row ledger is incomplete")
    return rows


@lru_cache(maxsize=None)
def _leibniz3(
    word: Word, first: Word, second: Word, third: Word
) -> tuple[tuple[Word, Word, Word, int], ...]:
    states: dict[tuple[Word, Word, Word], int] = {(first, second, third): 1}
    for axis in reversed(word):
        updated: dict[tuple[Word, Word, Word], int] = defaultdict(int)
        for (left, middle, right), multiplicity in states.items():
            updated[((axis, *left), middle, right)] += multiplicity
            updated[(left, (axis, *middle), right)] += multiplicity
            updated[(left, middle, (axis, *right))] += multiplicity
        states = dict(updated)
    return tuple((*key, value) for key, value in states.items())


def _add_ternary(
    output: dict[TRowKey, Q10], key: TRowKey, coefficient: Q10
) -> None:
    first, second, third, first_word, second_word, third_word = key
    for first_reduced, first_pbw in q10.pbw_word(first_word):
        for second_reduced, second_pbw in q10.pbw_word(second_word):
            for third_reduced, third_pbw in q10.pbw_word(third_word):
                q10._add(
                    output,
                    (first, second, third, first_reduced, second_reduced, third_reduced),
                    q10.qmul(
                        coefficient,
                        q10.qmul(first_pbw, q10.qmul(second_pbw, third_pbw)),
                    ),
                )


def _q1_q3_row(
    target: int,
    q1_by_target: Mapping[int, list[tuple[int, Word, Q10]]],
    q3: list[dict[TRowKey, Q10]],
    parities: tuple[int, ...],
) -> dict[TRowKey, Q10]:
    defect: dict[TRowKey, Q10] = {}
    for middle, outer_word, outer_coefficient in q1_by_target.get(target, ()):
        for key, inner_coefficient in q3[middle].items():
            first, second, third, first_word, second_word, third_word = key
            for new_first, new_second, new_third, multiplicity in _leibniz3(
                outer_word, first_word, second_word, third_word
            ):
                _add_ternary(
                    defect,
                    (first, second, third, new_first, new_second, new_third),
                    q10.qscale(q10.qmul(outer_coefficient, inner_coefficient), multiplicity),
                )
    for key, q3_coefficient in q3[target].items():
        components = key[:3]
        words = key[3:]
        for slot in range(3):
            sign = -1 if sum(parities[components[index]] for index in range(slot)) & 1 else 1
            for source, inner_word, q1_coefficient in q1_by_target.get(components[slot], ()):
                new_components = list(components)
                new_words = list(words)
                new_components[slot] = source
                new_words[slot] = words[slot] + inner_word
                _add_ternary(
                    defect,
                    (*new_components, *new_words),
                    q10.qscale(q10.qmul(q3_coefficient, q1_coefficient), sign),
                )
    return defect


def _q2_q2_row(
    outer: Mapping[BRowKey, Q10],
    inner_rows: list[dict[BRowKey, Q10]],
    parities: tuple[int, ...],
) -> dict[TRowKey, Q10]:
    output: dict[TRowKey, Q10] = {}
    for (middle, last, outer_word, last_word), outer_coefficient in outer.items():
        for (first, second, first_word, second_word), inner_coefficient in inner_rows[middle].items():
            for (new_first, new_second), leibniz_coefficient in q10._leibniz(
                outer_word, first_word, second_word
            ).items():
                coefficient = q10.qmul(
                    outer_coefficient,
                    q10.qmul(inner_coefficient, leibniz_coefficient),
                )
                _add_ternary(
                    output,
                    (first, second, last, new_first, new_second, last_word),
                    coefficient,
                )
                swap_sign = -1 if parities[second] * parities[last] else 1
                _add_ternary(
                    output,
                    (first, last, second, new_first, last_word, new_second),
                    q10.qscale(coefficient, swap_sign),
                )
                rotate_sign = -1 if parities[last] * (parities[first] + parities[second]) & 1 else 1
                _add_ternary(
                    output,
                    (last, first, second, last_word, new_first, new_second),
                    q10.qscale(coefficient, rotate_sign),
                )
    return output


def _merge_rows(*rows: Mapping[TRowKey, Q10]) -> dict[TRowKey, Q10]:
    output: dict[TRowKey, Q10] = {}
    for row in rows:
        for key, coefficient in row.items():
            q10._add(output, key, coefficient)
    return output


def _symmetry_defects(
    rows: list[Mapping[tuple[Any, ...], Q10]], parities: tuple[int, ...], arity: int
) -> int:
    defects = 0
    for row in rows:
        for key, coefficient in row.items():
            components, words = key[:arity], key[arity:]
            for slot in range(arity - 1):
                new_components, new_words = list(components), list(words)
                new_components[slot], new_components[slot + 1] = new_components[slot + 1], new_components[slot]
                new_words[slot], new_words[slot + 1] = new_words[slot + 1], new_words[slot]
                expected = q10.qscale(
                    coefficient,
                    -1 if parities[components[slot]] * parities[components[slot + 1]] else 1,
                )
                if row.get((*new_components, *new_words), q10.ZERO) != expected:
                    defects += 1
    return defects


def scientific_replay(progress: callable | None = print) -> dict[str, Any]:
    started = time.monotonic()
    certificate, typed_payload, q3_payload = _strict_inputs()
    carrier = _json(CARRIER)
    full = carrier["full_complex"]
    degrees = tuple(row["degree"] for row in full["component_rows"])
    parities = tuple(degree & 1 for degree in degrees)
    q1 = replay._parse_operator(full["classical_unary_q1"], shape=(64, 64), name="q1")
    q1_by_target: dict[int, list[tuple[int, Word, Q10]]] = defaultdict(list)
    for (target, source, word), coefficient in q1.items():
        q1_by_target[target].append((source, word, coefficient))
    gravity = _parse_q2(_json(GRAVITY_Q2), 64)
    typed = _parse_q2(typed_payload, 64)
    full_q2 = [dict(row) for row in gravity]
    for target, row in enumerate(typed):
        for key, coefficient in row.items():
            q10._add(full_q2[target], key, coefficient)
    q3 = _parse_q3(q3_payload)
    if progress:
        progress("parsed exact q1, q2 and 59,598-term mixed q3")

    q2_symmetry = _symmetry_defects(typed, parities, 2)
    q3_symmetry = _symmetry_defects(q3, parities, 3)
    row_defects: list[int] = []
    for target in range(64):
        defect = _merge_rows(
            _q1_q3_row(target, q1_by_target, q3, parities),
            _q2_q2_row(gravity[target], typed, parities),
            _q2_q2_row(typed[target], full_q2, parities),
        )
        row_defects.append(len(defect))
        if progress and (target + 1) % 8 == 0:
            progress(f"mixed arity-three replay rows {target - 7:02d}..{target:02d}: exact")

    mutation_row = next(index for index, row in enumerate(q3) if row)
    mutated = [dict(row) for row in q3]
    mutation_key = next(iter(mutated[mutation_row]))
    mutated[mutation_row][mutation_key] = q10.qadd(mutated[mutation_row][mutation_key], q10.ONE)
    mutation_defect = _merge_rows(
        _q1_q3_row(mutation_row, q1_by_target, mutated, parities),
        _q2_q2_row(gravity[mutation_row], typed, parities),
        _q2_q2_row(typed[mutation_row], full_q2, parities),
    )
    if not mutation_defect:
        raise ValueError("localized q3 coefficient mutation was not rejected")

    diagnostics = {
        "q1_PBW_coefficient_count": len(q1),
        "gravity_q2_coefficient_count": sum(map(len, gravity)),
        "typed_mixed_q2_coefficient_count": sum(map(len, typed)),
        "mixed_q3_coefficient_count": sum(map(len, q3)),
        "mixed_q3_nonzero_rows": sum(bool(row) for row in q3),
        "typed_q2_graded_symmetry_defect_count": q2_symmetry,
        "typed_q3_graded_symmetry_defect_count": q3_symmetry,
        "mixed_arity_three_defect_count": sum(row_defects),
        "mixed_arity_three_defect_rows": sum(bool(value) for value in row_defects),
        "localized_mutation_row": mutation_row,
        "localized_mutation_defect_count": len(mutation_defect),
        "K_Berger_derivation_term_count": sum(map(len, q3)),
        "K_Berger_derivation_reason": "K_Berger is e0 on the frozen stationary rows; coefficients are constant and [e0,e_a]=0",
    }
    accepted = (
        q2_symmetry == 0
        and q3_symmetry == 0
        and not any(row_defects)
        and bool(mutation_defect)
        and diagnostics["mixed_q3_coefficient_count"] == 59_598
        and diagnostics["mixed_q3_nonzero_rows"] == 21
    )
    return {
        "backend": "independent-two-rational-component-Q(sqrt(10))-mixed-q3-v1",
        "classical_commit": CLASSICAL_COMMIT,
        "input_hashes": {
            "producer_certificate": _sha256(_blob(CERTIFICATE)),
            "typed_q2_payload": _sha256(_blob(Q2_TYPED)),
            "mixed_q3_manifest": _sha256(_blob(Q3_PAYLOAD)),
            "gravity_q2_payload": _sha256(_blob(GRAVITY_Q2)),
            "portable_unary_carrier": _sha256(_blob(CARRIER)),
        },
        "diagnostics": diagnostics,
        "verdict": "ACCEPTED_TYPED_MIXED_Q3_LOCAL_ALGEBRAIC" if accepted else "REJECTED_TYPED_MIXED_Q3_EXACT_DEFECT",
        "elapsed_seconds": round(time.monotonic() - started, 6),
        "producer_claim_status": certificate["claim_status"],
    }


if __name__ == "__main__":
    print(json.dumps(scientific_replay(), indent=2, sort_keys=True))
