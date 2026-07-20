#!/usr/bin/env python3
"""Independent coefficient replay of the full five-current PBW export."""

from __future__ import annotations

from collections import Counter, defaultdict
from fractions import Fraction
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator

from d_quotient_classical.relative.einstein_weyl_relative_five_stabilizer_current import (
    antisymmetric_green_current_profiles,
    stabilizer_action,
    stabilizer_vectors,
)


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_FULL_FIVE_CURRENT_PBW_EXPORT_V1.json"
SCHEMA = ROOT / "d_quotient_classical/schema/relative-full-five-current-pbw-export-v1.schema.json"
PAYLOAD_SCHEMA = ROOT / "d_quotient_classical/schema/relative-full-five-current-pbw-payload-v1.schema.json"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _fraction(value: str) -> Fraction:
    return Fraction(value)


def _independent_current(action: list[tuple]) -> list[dict[tuple, dict[tuple[int, ...], Fraction]]]:
    """Compose the Green concomitant with the stabilizer and polarize independently."""

    by_output: dict[int, list[tuple]] = defaultdict(list)
    for term in action:
        by_output[term[0]].append(term)
    composed = [defaultdict(lambda: defaultdict(Fraction)) for _ in range(4)]
    for component, rows in enumerate(antisymmetric_green_current_profiles()):
        for (left, left_word, action_output, differentiated_word), current_profile in rows.items():
            for _, incoming, action_word, action_profile in by_output[action_output]:
                for mask in range(1 << len(differentiated_word)):
                    coefficient_word = tuple(sorted(
                        differentiated_word[index]
                        for index in range(len(differentiated_word))
                        if mask & (1 << index)
                    ))
                    field_word = tuple(sorted((*action_word, *(
                        differentiated_word[index]
                        for index in range(len(differentiated_word))
                        if not mask & (1 << index)
                    ))))
                    key = (left, left_word, incoming, field_word)
                    base_current = current_profile.get((), Fraction())
                    base_action = action_profile.get(coefficient_word, Fraction())
                    composed[component][key][()] += base_current * base_action
                    for axis in range(4):
                        composed[component][key][(axis,)] += (
                            current_profile.get((axis,), Fraction()) * base_action
                            + base_current * action_profile.get(tuple(sorted((*coefficient_word, axis))), Fraction())
                        )
    result = []
    for rows in composed:
        symmetric = defaultdict(lambda: defaultdict(Fraction))
        for (left, left_word, right, right_word), profile in rows.items():
            for word, coefficient in profile.items():
                symmetric[(left, left_word, right, right_word)][word] += coefficient / 2
                symmetric[(right, right_word, left, left_word)][word] += coefficient / 2
        result.append({
            key: {word: coefficient for word, coefficient in profile.items() if coefficient}
            for key, profile in symmetric.items()
            if any(profile.values())
        })
    return result


def verify() -> dict[str, object]:
    certificate = json.loads(CERTIFICATE.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(certificate)
    for relative, expected in certificate["provenance"]["source_manifest"].items():
        if _sha(ROOT / relative) != expected:
            raise AssertionError(f"source manifest drift: {relative}")
    for name, artifact in certificate["dependencies"].items():
        if _sha(ROOT / artifact["path"]) != artifact["sha256"]:
            raise AssertionError(f"dependency drift: {name}")

    payload_path = ROOT / certificate["payload"]["path"]
    if _sha(payload_path) != certificate["payload"]["sha256"]:
        raise AssertionError("payload hash drift")
    payload = json.loads(payload_path.read_text())
    payload_schema = json.loads(PAYLOAD_SCHEMA.read_text())
    Draft202012Validator.check_schema(payload_schema)
    Draft202012Validator(payload_schema).validate(payload)

    profiles = {
        profile["index"]: tuple(
            (tuple(item["word"]), _fraction(item["coefficient"]))
            for item in profile["coefficient_jets"]
        )
        for profile in payload["coefficient_profiles"]
    }
    if set(profiles) != set(range(239)) or len(set(profiles.values())) != 239:
        raise AssertionError("coefficient profiles are not canonical and deduplicated")

    output_by_generator_axis = {
        (row["generator"], row["component_axis"]): (row["row"], row["row_id"], row["vector_density_to_form_sign"])
        for row in payload["output_rows"]
    }
    actual = {}
    for term in payload["terms"]:
        left, right = term["inputs"]
        left_key = (left["local_field"], tuple(left["word"]))
        right_key = (right["local_field"], tuple(right["word"]))
        if left_key > right_key:
            raise AssertionError("payload contains a noncanonical symmetric input order")
        key = (term["generator"], term["output"]["row"], left_key, right_key)
        if key in actual:
            raise AssertionError("duplicate canonical current term")
        actual[key] = profiles[term["coefficient_profile"]]

    expected = {}
    vectors = stabilizer_vectors()
    for generator in payload["generator_order"]:
        current = _independent_current(stabilizer_action(vectors[generator]))
        for axis, rows in enumerate(current):
            output_row, _, sign = output_by_generator_axis[(generator, axis)]
            for (left, left_word, right, right_word), profile in rows.items():
                left_key = (left, left_word)
                right_key = (right, right_word)
                if left_key > right_key:
                    continue
                key = (generator, output_row, left_key, right_key)
                expected[key] = tuple(
                    (word, sign * coefficient)
                    for word, coefficient in sorted(profile.items())
                    if coefficient
                )
    if actual != expected:
        missing = next(iter(set(expected) - set(actual)), None)
        extra = next(iter(set(actual) - set(expected)), None)
        mismatch = next((key for key in set(actual) & set(expected) if actual[key] != expected[key]), None)
        raise AssertionError(f"current coefficient replay failed: missing={missing}, extra={extra}, mismatch={mismatch}")

    diagonals = Counter()
    canonical = Counter()
    for generator, _, left, right in actual:
        canonical[generator] += 1
        diagonals[generator] += left == right
    expanded = {generator: 2 * canonical[generator] - diagonals[generator] for generator in payload["generator_order"]}
    if dict(canonical) != payload["canonical_term_counts"] or dict(diagonals) != payload["diagonal_term_counts"] or expanded != payload["expanded_term_counts"]:
        raise AssertionError("symmetric expansion census drifted")

    flags = certificate["classification"]
    if any(flags[key] for key in (
        "support_local_chain_map_A_constructed", "top_descent_solved",
        "relative_q2_repaired", "causal_observable_particle_or_quantum_claim",
    )):
        raise AssertionError("portable export overpromoted")
    return {
        "status": "PASS",
        "canonical_terms": len(actual),
        "expanded_terms": sum(expanded.values()),
        "coefficient_profiles": len(profiles),
        "independent_coefficient_replay": True,
        "top_descent_open": True,
    }


if __name__ == "__main__":
    print(json.dumps(verify(), indent=2, sort_keys=True))
