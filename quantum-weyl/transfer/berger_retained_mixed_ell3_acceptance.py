"""Independent exact consumer for the retained typed Berger mixed ell3.

The classical producer is not imported or executed.  Every artifact is read
from the pinned classical commit and replayed with the quantum-side exact
``Q(sqrt(10))`` PBW backend.
"""

from __future__ import annotations

from collections import defaultdict
from functools import lru_cache
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import time
from typing import Any, Mapping

from jsonschema import Draft202012Validator

from local_bv.schema_validation import validate_instance

from . import berger_mixed_q3_acceptance as arity3
from . import berger_qsqrt10_replay as q10
from .berger_coupled_36_transfer_replay import _parse_operator
from .berger_retained_26_q2_transfer import _transfer_inner, _transfer_outer


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CLASSICAL_COMMIT = "e99d0c1d39490de5261fc6ca1dc2aeaa0d149655"
TRANSFER = "d_quotient_classical/certificates/BERGER_RETAINED_MIXED_ELL3_TRANSFER.json"
TRANSFER_SCHEMA = "d_quotient_classical/schema/berger-retained-mixed-ell3-transfer-v1.schema.json"
CARRIER = "d_quotient_classical/certificates/BERGER_PORTABLE_COUPLED_64_TYPED_PAIRING_36_SDR.json"
CARRIER_SCHEMA = "d_quotient_classical/schema/berger-portable-coupled-64-typed-pairing-36-sdr-v1.schema.json"
LEGACY_CARRIER = "d_quotient_classical/certificates/BERGER_PORTABLE_COUPLED_64_UNARY_PAIRING_36_SDR.json"
LEGACY_CARRIER_SCHEMA = "d_quotient_classical/schema/berger-portable-coupled-64-unary-pairing-36-sdr-v1.schema.json"
FULL_Q2_MIXED = "d_quotient_classical/certificates/BERGER_SUPPORT_LOCAL_COUPLED_MAXWELL_Q2_TYPED_PAYLOAD.json"
FULL_Q3_MIXED = "d_quotient_classical/certificates/BERGER_SUPPORT_LOCAL_COUPLED_MAXWELL_Q3_PAYLOAD.json"
FULL_Q3_ROW_SCHEMA = "d_quotient_classical/schema/berger-support-local-coupled-maxwell-q3-row-v1.schema.json"
GRAVITY_Q2 = "d_quotient_classical/certificates/BERGER_SUPPORT_LOCAL_Q2_PAYLOAD.json"
RETAINED_Q2_MIXED = "d_quotient_classical/certificates/BERGER_RETAINED_TYPED_MIXED_ELL2_PAYLOAD.json"
RETAINED_Q2_SCHEMA = "d_quotient_classical/schema/berger-retained-typed-mixed-ell2-payload-v1.schema.json"
RETAINED_Q3_MIXED = "d_quotient_classical/certificates/BERGER_RETAINED_MIXED_ELL3_PAYLOAD.json"
RETAINED_Q3_SCHEMA = "d_quotient_classical/schema/berger-retained-mixed-ell3-payload-v1.schema.json"
RETAINED_Q3_ROW_SCHEMA = "d_quotient_classical/schema/berger-retained-mixed-ell3-row-v1.schema.json"

TRowKey = arity3.TRowKey


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
        raise ValueError(f"missing pinned retained ell3 artifact: {relative}")
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


def _strict(instance_path: str, schema_path: str) -> dict[str, Any]:
    instance, schema = _json(instance_path), _json(schema_path)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(instance)
    errors = validate_instance(instance, schema)
    if errors:
        raise ValueError(f"strict schema failure for {instance_path}: {'; '.join(errors)}")
    return instance


def _parse_q2(payload: Mapping[str, Any], total_rows: int) -> list[dict[arity3.BRowKey, q10.Q10]]:
    rows: list[dict[arity3.BRowKey, q10.Q10]] = [dict() for _ in range(total_rows)]
    seen: set[int] = set()
    for record in payload["rows"]:
        target = record["output"]
        if target in seen or not 0 <= target < total_rows:
            raise ValueError("bilinear output ledger is invalid")
        seen.add(target)
        body = {"output": target, "terms": record["terms"]}
        if record.get("canonical_sha256") not in (None, _canonical_hash(body)):
            raise ValueError(f"bilinear row hash drifted: {target}")
        for left, left_word, right, right_word, raw in record["terms"]:
            key = (left, right, q10._word(left_word), q10._word(right_word))
            q10._add(rows[target], key, arity3._coefficient(raw))
    return rows


def _parse_q3(
    payload: Mapping[str, Any], total_rows: int, row_schema_path: str
) -> list[dict[TRowKey, q10.Q10]]:
    schema = _json(row_schema_path)
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)
    rows: list[dict[TRowKey, q10.Q10]] = [dict() for _ in range(total_rows)]
    seen: set[int] = set()
    for chunk in payload["chunks"]:
        raw = _blob(chunk["path"])
        if raw[4:8] != b"\x00\x00\x00\x00" or _sha256(raw) != chunk["file_sha256"]:
            raise ValueError(f"trilinear chunk integrity failed: {chunk['output']}")
        record = json.loads(gzip.decompress(raw))
        validator.validate(record)
        output = record["output"]
        body = {"output": output, "terms": record["terms"]}
        if (
            output in seen
            or output != chunk["output"]
            or _canonical_hash(body) != record["canonical_sha256"]
            or record["canonical_sha256"] != chunk["canonical_sha256"]
        ):
            raise ValueError(f"trilinear row ledger failed: {output}")
        seen.add(output)
        for first, first_word, second, second_word, third, third_word, raw_coefficient in record["terms"]:
            key = (
                first,
                second,
                third,
                q10._word(first_word),
                q10._word(second_word),
                q10._word(third_word),
            )
            q10._add(rows[output], key, arity3._coefficient(raw_coefficient))
    if seen != set(range(total_rows)):
        raise ValueError("trilinear row ledger is incomplete")
    return rows


def _flatten_q2(rows: list[Mapping[arity3.BRowKey, q10.Q10]]) -> dict[q10.BilinearKey, q10.Q10]:
    return {
        (target, left, right, left_word, right_word): coefficient
        for target, row in enumerate(rows)
        for (left, right, left_word, right_word), coefficient in row.items()
    }


def _rows_q2(flat: Mapping[q10.BilinearKey, q10.Q10], size: int) -> list[dict[arity3.BRowKey, q10.Q10]]:
    rows: list[dict[arity3.BRowKey, q10.Q10]] = [dict() for _ in range(size)]
    for (target, left, right, left_word, right_word), coefficient in flat.items():
        q10._add(rows[target], (left, right, left_word, right_word), coefficient)
    return rows


def _precompose_contact(
    rows: list[Mapping[TRowKey, q10.Q10]],
    inclusion: Mapping[q10.LinearKey, q10.Q10],
) -> list[dict[TRowKey, q10.Q10]]:
    by_target: dict[int, list[tuple[int, q10.Word, q10.Q10]]] = defaultdict(list)
    for (target, source, word), coefficient in inclusion.items():
        by_target[target].append((source, word, coefficient))
    output: list[dict[TRowKey, q10.Q10]] = [dict() for _ in rows]
    for target, row in enumerate(rows):
        for (first, second, third, first_word, second_word, third_word), coefficient in row.items():
            for new_first, first_inner, first_coefficient in by_target.get(first, ()):
                for new_second, second_inner, second_coefficient in by_target.get(second, ()):
                    for new_third, third_inner, third_coefficient in by_target.get(third, ()):
                        arity3._add_ternary(
                            output[target],
                            (
                                new_first,
                                new_second,
                                new_third,
                                first_word + first_inner,
                                second_word + second_inner,
                                third_word + third_inner,
                            ),
                            q10.qmul(
                                coefficient,
                                q10.qmul(first_coefficient, q10.qmul(second_coefficient, third_coefficient)),
                            ),
                        )
    return output


def _postcompose_contact(
    rows: list[Mapping[TRowKey, q10.Q10]],
    projection: Mapping[q10.LinearKey, q10.Q10],
    retained_rows: int,
) -> tuple[list[dict[TRowKey, q10.Q10]], int]:
    by_source: dict[int, list[tuple[int, q10.Word, q10.Q10]]] = defaultdict(list)
    for (target, source, word), coefficient in projection.items():
        by_source[source].append((target, word, coefficient))
    output: list[dict[TRowKey, q10.Q10]] = [dict() for _ in range(retained_rows)]
    contributions = 0
    for middle, row in enumerate(rows):
        for target, outer_word, outer_coefficient in by_source.get(middle, ()):
            for key, coefficient in row.items():
                first, second, third, first_word, second_word, third_word = key
                for new_first, new_second, new_third, multiplicity in arity3._leibniz3(
                    outer_word, first_word, second_word, third_word
                ):
                    contributions += 1
                    arity3._add_ternary(
                        output[target],
                        (first, second, third, new_first, new_second, new_third),
                        q10.qscale(q10.qmul(outer_coefficient, coefficient), multiplicity),
                    )
    return output, contributions


def _transfer_contact(
    rows: list[Mapping[TRowKey, q10.Q10]],
    inclusion: Mapping[q10.LinearKey, q10.Q10],
    projection: Mapping[q10.LinearKey, q10.Q10],
) -> tuple[list[dict[TRowKey, q10.Q10]], int, int]:
    intermediate = _precompose_contact(rows, inclusion)
    output, outer = _postcompose_contact(intermediate, projection, 36)
    return output, sum(map(len, intermediate)), outer


def _exchange_exact(
    outer: Mapping[q10.BilinearKey, q10.Q10],
    inclusion2: Mapping[q10.BilinearKey, q10.Q10],
    inclusion: Mapping[q10.LinearKey, q10.Q10],
    projection: Mapping[q10.LinearKey, q10.Q10],
    parities: tuple[int, ...],
) -> tuple[list[dict[TRowKey, q10.Q10]], int, int, int, int]:
    """Construct one full ``pi q2(I2,iota)`` unshuffle sector exactly."""

    inner_by_output: dict[int, list[tuple[int, int, q10.Word, q10.Word, q10.Q10]]] = defaultdict(list)
    for (target, first, second, first_word, second_word), coefficient in inclusion2.items():
        inner_by_output[target].append(
            (first, second, first_word, second_word, coefficient)
        )
    inclusion_by_target: dict[int, list[tuple[int, q10.Word, q10.Q10]]] = defaultdict(list)
    for (target, source, word), coefficient in inclusion.items():
        inclusion_by_target[target].append((source, word, coefficient))

    full: list[dict[TRowKey, q10.Q10]] = [dict() for _ in range(64)]
    raw_incidence = 0
    unshuffle_contributions = 0
    for (target, middle, direct, outer_word, direct_word), outer_coefficient in outer.items():
        for first, second, first_word, second_word, inner_coefficient in inner_by_output.get(middle, ()):
            raw_incidence += 1
            for new_direct, iota_word, iota_coefficient in inclusion_by_target.get(direct, ()):
                for (new_first, new_second), leibniz_coefficient in q10._leibniz(
                    outer_word, first_word, second_word
                ).items():
                    coefficient = q10.qmul(
                        outer_coefficient,
                        q10.qmul(
                            inner_coefficient,
                            q10.qmul(iota_coefficient, leibniz_coefficient),
                        ),
                    )
                    direct_derivative = direct_word + iota_word
                    arity3._add_ternary(
                        full[target],
                        (
                            first,
                            second,
                            new_direct,
                            new_first,
                            new_second,
                            direct_derivative,
                        ),
                        coefficient,
                    )
                    arity3._add_ternary(
                        full[target],
                        (
                            first,
                            new_direct,
                            second,
                            new_first,
                            direct_derivative,
                            new_second,
                        ),
                        q10.qscale(
                            coefficient,
                            -1 if parities[second] * parities[new_direct] else 1,
                        ),
                    )
                    arity3._add_ternary(
                        full[target],
                        (
                            new_direct,
                            first,
                            second,
                            direct_derivative,
                            new_first,
                            new_second,
                        ),
                        q10.qscale(
                            coefficient,
                            -1
                            if (
                                parities[new_direct]
                                * (parities[first] + parities[second])
                            )
                            & 1
                            else 1,
                        ),
                    )
                    unshuffle_contributions += 3
    full_coefficient_count = sum(map(len, full))
    projected, projection_contributions = _postcompose_contact(full, projection, 36)
    return (
        projected,
        raw_incidence,
        unshuffle_contributions,
        full_coefficient_count,
        projection_contributions,
    )


def _merge(*rows: Mapping[TRowKey, q10.Q10]) -> dict[TRowKey, q10.Q10]:
    result: dict[TRowKey, q10.Q10] = {}
    for row in rows:
        for key, coefficient in row.items():
            q10._add(result, key, coefficient)
    return result


def _relative_identity(
    q1: Mapping[q10.LinearKey, q10.Q10],
    gravity_q2: list[dict[arity3.BRowKey, q10.Q10]],
    mixed_q2: list[dict[arity3.BRowKey, q10.Q10]],
    ell3: list[dict[TRowKey, q10.Q10]],
    parities: tuple[int, ...],
) -> list[int]:
    q1_by_target: dict[int, list[tuple[int, q10.Word, q10.Q10]]] = defaultdict(list)
    for (target, source, word), coefficient in q1.items():
        q1_by_target[target].append((source, word, coefficient))
    full_q2 = [dict(row) for row in gravity_q2]
    for target, row in enumerate(mixed_q2):
        for key, coefficient in row.items():
            q10._add(full_q2[target], key, coefficient)
    counts = []
    for target in range(36):
        defect = _merge(
            arity3._q1_q3_row(target, q1_by_target, ell3, parities),
            arity3._q2_q2_row(gravity_q2[target], mixed_q2, parities),
            arity3._q2_q2_row(mixed_q2[target], full_q2, parities),
        )
        counts.append(len(defect))
    return counts


def _mutation_defect(
    q1: Mapping[q10.LinearKey, q10.Q10],
    ell3: list[dict[TRowKey, q10.Q10]],
    parities: tuple[int, ...],
) -> tuple[int, int, int]:
    q1_by_target: dict[int, list[tuple[int, q10.Word, q10.Q10]]] = defaultdict(list)
    for (target, source, word), coefficient in q1.items():
        q1_by_target[target].append((source, word, coefficient))
    for row_index, row in enumerate(ell3):
        for key in sorted(row):
            delta = [dict() for _ in range(36)]
            delta[row_index][key] = q10.ONE
            count = sum(
                len(arity3._q1_q3_row(target, q1_by_target, delta, parities))
                for target in range(36)
            )
            if count:
                return row_index, list(sorted(row)).index(key), count
    raise ValueError("no retained ell3 mutation was detected by the arity-three identity")


@lru_cache(maxsize=1)
def scientific_replay(progress: callable | None = print) -> dict[str, Any]:
    started = time.monotonic()
    transfer = _strict(TRANSFER, TRANSFER_SCHEMA)
    carrier = _strict(CARRIER, CARRIER_SCHEMA)
    legacy_carrier = _strict(LEGACY_CARRIER, LEGACY_CARRIER_SCHEMA)
    retained_q2_payload = _strict(RETAINED_Q2_MIXED, RETAINED_Q2_SCHEMA)
    retained_q3_payload = _strict(RETAINED_Q3_MIXED, RETAINED_Q3_SCHEMA)
    for dependency in transfer["dependency_refs"].values():
        if _sha256(_blob(dependency["path"])) != dependency["sha256"]:
            raise ValueError(f"retained ell3 dependency hash drifted: {dependency['path']}")

    full = carrier["full_complex"]
    retained = carrier["retained_complex"]
    contraction = carrier["contraction"]
    inclusion = _parse_operator(contraction["iota_36_to_64"], shape=(64, 36), name="iota36")
    projection = _parse_operator(contraction["pi_64_to_36"], shape=(36, 64), name="pi36")
    homotopy = _parse_operator(contraction["S_64"], shape=(64, 64), name="S64")
    q1 = _parse_operator(retained["classical_unary_q1"], shape=(36, 36), name="q36")
    parities = tuple(
        row["degree"] & 1
        for row in legacy_carrier["retained_complex"]["component_rows"]
    )
    if len(parities) != 36:
        raise ValueError("retained parity ledger drifted")

    gravity_full = _parse_q2(_json(GRAVITY_Q2), 64)
    mixed_full = _parse_q2(_json(FULL_Q2_MIXED), 64)
    q3_full = _parse_q3(_json(FULL_Q3_MIXED), 64, FULL_Q3_ROW_SCHEMA)
    mixed_retained = _parse_q2(retained_q2_payload, 36)
    ell3_expected = _parse_q3(retained_q3_payload, 36, RETAINED_Q3_ROW_SCHEMA)
    if progress:
        progress("parsed typed carrier, q2 and retained/full mixed ell3 payloads")

    contact, contact_inner_count, contact_outer_count = _transfer_contact(
        q3_full, inclusion, projection
    )
    contact_missing = sum(len(set(expected) - set(computed)) for expected, computed in zip(ell3_expected, contact))
    contact_extra = sum(len(set(computed) - set(expected)) for expected, computed in zip(ell3_expected, contact))
    contact_changed = sum(
        computed.get(key) != expected.get(key)
        for expected, computed in zip(ell3_expected, contact)
        for key in set(expected) & set(computed)
    )
    if contact_missing or contact_extra or contact_changed:
        raise ValueError(
            f"retained contact mismatch missing={contact_missing} extra={contact_extra} changed={contact_changed}"
        )
    if progress:
        progress("all 25,950 retained contact coefficients replayed exactly")

    mixed_intermediate, _ = _transfer_inner(_flatten_q2(mixed_full), inclusion)
    mixed_retained_computed, _ = _transfer_outer(mixed_intermediate, projection)
    if mixed_retained_computed != _flatten_q2(mixed_retained):
        raise ValueError("retained typed mixed ell2 transfer drifted")
    gravity_intermediate, _ = _transfer_inner(_flatten_q2(gravity_full), inclusion)
    gravity_retained_flat, _ = _transfer_outer(gravity_intermediate, projection)
    gravity_i2_flat, _ = _transfer_outer(gravity_intermediate, homotopy)
    mixed_i2_flat, _ = _transfer_outer(mixed_intermediate, homotopy)
    gravity_i2_flat = {key: q10.qneg(value) for key, value in gravity_i2_flat.items()}
    mixed_i2_flat = {key: q10.qneg(value) for key, value in mixed_i2_flat.items()}
    gravity_i2_support = sorted({target for target, *_ in gravity_i2_flat})
    mixed_i2_support = sorted({target for target, *_ in mixed_i2_flat})
    if gravity_i2_support != [37, 38] or mixed_i2_support != [38]:
        raise ValueError("second inclusion support drifted")

    gravity_flat = _flatten_q2(gravity_full)
    mixed_flat = _flatten_q2(mixed_full)
    exchange_parts = {}
    raw_exchange_candidates = {}
    exchange_unshuffle_contributions = {}
    exchange_full_coefficient_counts = {}
    exchange_projection_contributions = {}
    for name, outer, inner in (
        ("gravity_outer_mixed_inner", gravity_flat, mixed_i2_flat),
        ("mixed_outer_gravity_inner", mixed_flat, gravity_i2_flat),
        ("mixed_outer_mixed_inner", mixed_flat, mixed_i2_flat),
    ):
        (
            exchange_parts[name],
            raw_exchange_candidates[name],
            exchange_unshuffle_contributions[name],
            exchange_full_coefficient_counts[name],
            exchange_projection_contributions[name],
        ) = _exchange_exact(outer, inner, inclusion, projection, parities)
    exchange_counts = {
        name: sum(map(len, rows)) for name, rows in exchange_parts.items()
    }
    if any(exchange_counts.values()):
        raise ValueError(f"exchange exact zero failed: {exchange_counts}")
    if progress:
        progress("all three q2 S q2 exchange sectors vanish exactly after retained projection")

    gravity_retained = _rows_q2(gravity_retained_flat, 36)
    identity_counts = _relative_identity(q1, gravity_retained, mixed_retained, ell3_expected, parities)
    if any(identity_counts):
        raise ValueError(f"retained arity-three identity defects: {identity_counts}")
    mutation_row, mutation_term_index, mutation_defects = _mutation_defect(q1, ell3_expected, parities)
    if progress:
        progress("all 36 retained arity-three rows close; mutation rejected")

    term_count = sum(map(len, ell3_expected))
    full_q3_term_count = sum(map(len, q3_full))
    full_q3_nonzero_rows = sum(bool(row) for row in q3_full)
    gravity_output_terms = sum(len(row) for row in ell3_expected[:26])
    maxwell_output_terms = term_count - gravity_output_terms
    input_maxwell_counts = {str(count): 0 for count in range(4)}
    for row in ell3_expected:
        for first, second, third, *_ in row:
            input_maxwell_counts[str(sum(index >= 26 for index in (first, second, third)))] += 1

    diagnostics = {
        "full_mixed_q3_coefficient_count": full_q3_term_count,
        "full_mixed_q3_nonzero_rows": full_q3_nonzero_rows,
        "retained_ell2_coefficient_count": len(mixed_retained_computed),
        "retained_ell3_coefficient_count": term_count,
        "retained_ell3_nonzero_rows": sum(bool(row) for row in ell3_expected),
        "contact_missing_count": contact_missing,
        "contact_extra_count": contact_extra,
        "contact_changed_count": contact_changed,
        "contact_intermediate_coefficient_count": contact_inner_count,
        "contact_outer_Leibniz_contribution_count": contact_outer_count,
        "gravity_inclusion2_coefficient_count": len(gravity_i2_flat),
        "mixed_inclusion2_coefficient_count": len(mixed_i2_flat),
        "gravity_inclusion2_support": gravity_i2_support,
        "mixed_inclusion2_support": mixed_i2_support,
        "raw_exchange_candidate_counts": raw_exchange_candidates,
        "exchange_unshuffle_contribution_counts": exchange_unshuffle_contributions,
        "exchange_full_coefficient_counts": exchange_full_coefficient_counts,
        "exchange_projection_contribution_counts": exchange_projection_contributions,
        "exchange_final_coefficient_counts": exchange_counts,
        "retained_arity_three_defect_count": sum(identity_counts),
        "retained_arity_three_defect_rows": sum(bool(value) for value in identity_counts),
        "mutation_row": mutation_row,
        "mutation_term_index": mutation_term_index,
        "mutation_defect_count": mutation_defects,
        "gravity_output_term_count": gravity_output_terms,
        "Maxwell_output_term_count": maxwell_output_terms,
        "input_Maxwell_leg_counts": input_maxwell_counts,
    }
    accepted = (
        term_count == 25_950
        and full_q3_term_count == 59_598
        and full_q3_nonzero_rows == 21
        and diagnostics["retained_ell2_coefficient_count"] == 1_474
        and diagnostics["retained_ell3_nonzero_rows"] == 18
        and not any(exchange_counts.values())
        and not any(identity_counts)
        and mutation_defects > 0
    )
    return {
        "backend": "independent-Q(sqrt(10))-PBW-retained-ell3-v1",
        "classical_commit": CLASSICAL_COMMIT,
        "input_hashes": {
            "transfer_certificate": _sha256(_blob(TRANSFER)),
            "typed_carrier": _sha256(_blob(CARRIER)),
            "legacy_layout_carrier": _sha256(_blob(LEGACY_CARRIER)),
            "full_typed_mixed_q2": _sha256(_blob(FULL_Q2_MIXED)),
            "full_mixed_q3_manifest": _sha256(_blob(FULL_Q3_MIXED)),
            "retained_mixed_q2": _sha256(_blob(RETAINED_Q2_MIXED)),
            "retained_mixed_q3_manifest": _sha256(_blob(RETAINED_Q3_MIXED)),
        },
        "diagnostics": diagnostics,
        "verdict": "ACCEPTED_RETAINED_MIXED_ELL3_ZERO_EXCHANGE_LOCAL_ALGEBRAIC" if accepted else "REJECTED_RETAINED_MIXED_ELL3_EXACT_DEFECT",
        "elapsed_seconds": round(time.monotonic() - started, 6),
        "producer_claim_status": transfer["claim_status"],
    }


if __name__ == "__main__":
    print(json.dumps(scientific_replay(), indent=2, sort_keys=True))
