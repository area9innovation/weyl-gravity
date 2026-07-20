#!/usr/bin/env python3
"""Independent chunkwise replay of the five-current second-jet export."""

from __future__ import annotations

from collections import defaultdict
from fractions import Fraction
import gzip
import hashlib
from itertools import combinations_with_replacement
import json
from pathlib import Path

import sympy as sp
from jsonschema import Draft202012Validator

from bridge.einstein_sector.product_taylor_engine import COORDINATES, PAIRS
from d_quotient_classical.relative.einstein_weyl_relative_five_stabilizer_current import (
    coefficient_profile,
    stabilizer_vectors,
)


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_FULL_FIVE_CURRENT_SECOND_JET_EXPORT_V1.json"
SCHEMA = ROOT / "d_quotient_classical/schema/relative-full-five-current-second-jet-export-v1.schema.json"
MANIFEST_SCHEMA = ROOT / "d_quotient_classical/schema/relative-full-five-current-second-jet-manifest-v1.schema.json"
CHUNK_SCHEMA = ROOT / "d_quotient_classical/schema/relative-full-five-current-second-jet-chunk-v1.schema.json"
HESSIAN = ROOT / "d_quotient_classical/generated/einstein_weyl_relative_hessian_second_current_input_v1/relative_hessian.json"
V1 = ROOT / "d_quotient_classical/generated/einstein_weyl_relative_full_five_current_pbw_export_v1/current_q2.json"


def _sha_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha(path: Path) -> str:
    return _sha_bytes(path.read_bytes())


def _words(order: int):
    yield ()
    for degree in range(1, order + 1):
        yield from combinations_with_replacement(range(4), degree)


def _hessian_terms():
    payload = json.loads(HESSIAN.read_text())
    for term in payload["terms"]:
        yield (
            term["output_local"],
            term["input_local"],
            tuple(term["word"]),
            {tuple(jet["word"]): Fraction(jet["coefficient"]) for jet in term["coefficient_jets"]},
        )


def _independent_green_component(axis: int):
    ordered = defaultdict(lambda: defaultdict(Fraction))
    for equation, field, operator_word, profile in _hessian_terms():
        for position, current_axis in enumerate(operator_word):
            if current_axis != axis:
                continue
            before = operator_word[:position]
            after = operator_word[position + 1 :]
            for coefficient_choice in range(1 << len(before)):
                coefficient_word = tuple(sorted(
                    before[index] for index in range(len(before))
                    if coefficient_choice & (1 << index)
                ))
                first_word = tuple(sorted(
                    before[index] for index in range(len(before))
                    if not coefficient_choice & (1 << index)
                ))
                sign = Fraction(1 if position % 2 == 0 else -1)
                for jet in _words(2):
                    value = profile.get(tuple(sorted((*coefficient_word, *jet))), Fraction())
                    if value:
                        ordered[(equation, first_word, field, after)][jet] += sign * value
    result = defaultdict(lambda: defaultdict(Fraction))
    for (left, left_word, right, right_word), profile in ordered.items():
        for jet, value in profile.items():
            result[(left, left_word, right, right_word)][jet] += value / 2
            result[(right, right_word, left, left_word)][jet] -= value / 2
    return {
        key: {jet: value for jet, value in profile.items() if value}
        for key, profile in result.items()
        if any(profile.values())
    }


def _independent_action(vector: sp.Matrix):
    pair_index = {pair: index for index, pair in enumerate(PAIRS)}
    raw = []
    for output, (mu, nu) in enumerate(PAIRS):
        for rho in range(4):
            raw.append((output, output, (rho,), coefficient_profile(vector[rho], 5)))
            raw.append((output, pair_index[tuple(sorted((rho, nu)))], (), coefficient_profile(sp.diff(vector[rho], COORDINATES[mu]), 5)))
            raw.append((output, pair_index[tuple(sorted((mu, rho)))], (), coefficient_profile(sp.diff(vector[rho], COORDINATES[nu]), 5)))
    for mu in range(4):
        for rho in range(4):
            profile = coefficient_profile(vector[rho], 5)
            raw.append((10 + mu, 10 + mu, (rho,), profile))
            raw.append((10 + mu, 10 + rho, (mu,), {word: -value for word, value in profile.items()}))
    merged = defaultdict(lambda: defaultdict(Fraction))
    for output, incoming, word, profile in raw:
        for jet, value in profile.items():
            merged[(output, incoming, tuple(sorted(word)))][jet] += value
    return [
        (*key, {jet: value for jet, value in profile.items() if value})
        for key, profile in sorted(merged.items())
        if any(profile.values())
    ]


def _independent_component(current, action):
    actions = defaultdict(list)
    for row in action:
        actions[row[0]].append(row)
    composed = defaultdict(lambda: defaultdict(Fraction))
    for (left, left_word, action_output, differentiated), current_profile in current.items():
        for _, incoming, action_word, action_profile in actions[action_output]:
            for field_choice in range(1 << len(differentiated)):
                hit_coefficient = tuple(sorted(
                    differentiated[index] for index in range(len(differentiated))
                    if field_choice & (1 << index)
                ))
                field_word = tuple(sorted((*action_word, *(
                    differentiated[index] for index in range(len(differentiated))
                    if not field_choice & (1 << index)
                ))))
                key = (left, left_word, incoming, field_word)
                for result_jet in _words(2):
                    for product_choice in range(1 << len(result_jet)):
                        current_jet = tuple(result_jet[index] for index in range(len(result_jet)) if product_choice & (1 << index))
                        action_jet = tuple(result_jet[index] for index in range(len(result_jet)) if not product_choice & (1 << index))
                        composed[key][result_jet] += (
                            current_profile.get(current_jet, Fraction())
                            * action_profile.get(tuple(sorted((*hit_coefficient, *action_jet))), Fraction())
                        )
    symmetric = defaultdict(lambda: defaultdict(Fraction))
    for (left, left_word, right, right_word), profile in composed.items():
        for jet, value in profile.items():
            symmetric[(left, left_word, right, right_word)][jet] += value / 2
            symmetric[(right, right_word, left, left_word)][jet] += value / 2
    return {
        key: {jet: value for jet, value in profile.items() if value}
        for key, profile in symmetric.items()
        if any(profile.values())
    }


def _decode_chunk(chunk):
    profiles = {
        profile["index"]: {
            tuple(item["word"]): Fraction(item["coefficient"])
            for item in profile["coefficient_jets"]
        }
        for profile in chunk["coefficient_profiles"]
    }
    if set(profiles) != set(range(len(profiles))):
        raise AssertionError("chunk coefficient profiles are not consecutively indexed")
    actual = {}
    for term in chunk["terms"]:
        left, right = term["inputs"]
        left_key = (left["local_field"], tuple(left["word"]))
        right_key = (right["local_field"], tuple(right["word"]))
        if left_key > right_key:
            raise AssertionError("noncanonical symmetric input order")
        key = (left_key[0], left_key[1], right_key[0], right_key[1])
        if key in actual:
            raise AssertionError("duplicate canonical term")
        actual[key] = profiles[term["coefficient_profile"]]
    return actual


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
    manifest_path = ROOT / certificate["manifest"]["path"]
    if _sha(manifest_path) != certificate["manifest"]["sha256"]:
        raise AssertionError("manifest hash drift")
    manifest = json.loads(manifest_path.read_text())
    manifest_schema = json.loads(MANIFEST_SCHEMA.read_text())
    chunk_schema = json.loads(CHUNK_SCHEMA.read_text())
    Draft202012Validator.check_schema(manifest_schema)
    Draft202012Validator.check_schema(chunk_schema)
    Draft202012Validator(manifest_schema).validate(manifest)

    vectors = stabilizer_vectors()
    actions = {name: _independent_action(vectors[name]) for name in manifest["generator_order"]}
    green = {}
    total = expanded = profiles = 0
    actual_v2 = {}
    for record in manifest["chunks"]:
        path = ROOT / record["path"]
        data = path.read_bytes()
        if _sha_bytes(data) != record["sha256"]:
            raise AssertionError(f"chunk hash drift: {path}")
        plain = gzip.decompress(data)
        if _sha_bytes(plain) != record["uncompressed_sha256"]:
            raise AssertionError(f"chunk plain hash drift: {path}")
        chunk = json.loads(plain)
        Draft202012Validator(chunk_schema).validate(chunk)
        axis = chunk["component_axis"]
        if axis not in green:
            green[axis] = _independent_green_component(axis)
        expected_rows = _independent_component(green[axis], actions[chunk["generator"]])
        sign = Fraction(chunk["vector_density_to_form_sign"])
        expected = {}
        for key, profile in expected_rows.items():
            left = (key[0], key[1])
            right = (key[2], key[3])
            if left <= right:
                expected[key] = {jet: sign * value for jet, value in profile.items() if value}
        actual = _decode_chunk(chunk)
        if actual != expected:
            missing = next(iter(set(expected) - set(actual)), None)
            extra = next(iter(set(actual) - set(expected)), None)
            mismatch = next((key for key in set(actual) & set(expected) if actual[key] != expected[key]), None)
            raise AssertionError(f"independent second-jet replay failed: {chunk['result_id']}, missing={missing}, extra={extra}, mismatch={mismatch}")
        for key, profile in actual.items():
            actual_v2[(chunk["generator"], chunk["output"]["row"], key)] = profile
        total += len(actual)
        expanded += chunk["expanded_term_count"]
        profiles += chunk["coefficient_profile_count"]

    v1 = json.loads(V1.read_text())
    v1_profiles = {
        profile["index"]: {
            tuple(item["word"]): Fraction(item["coefficient"])
            for item in profile["coefficient_jets"]
        }
        for profile in v1["coefficient_profiles"]
    }
    overlap = 0
    for term in v1["terms"]:
        left, right = term["inputs"]
        key = (
            term["generator"],
            term["output"]["row"],
            (
                left["local_field"], tuple(left["word"]),
                right["local_field"], tuple(right["word"]),
            ),
        )
        restricted = {
            jet: value
            for jet, value in actual_v2[key].items()
            if len(jet) <= 1
        }
        if restricted != v1_profiles[term["coefficient_profile"]]:
            raise AssertionError(f"V1 overlap defect: {key}")
        overlap += 1
    if total != manifest["canonical_term_count"] or expanded != manifest["expanded_term_count"]:
        raise AssertionError("manifest current census drifted")
    if profiles != manifest["local_coefficient_profile_count"]:
        raise AssertionError("manifest local profile census drifted")
    flags = certificate["classification"]
    if any(flags[key] for key in (
        "support_local_chain_map_A_constructed",
        "order_one_top_descent_solved",
        "relative_q2_repaired",
        "causal_observable_particle_or_quantum_claim",
    )):
        raise AssertionError("second-jet export overpromoted")
    return {
        "status": "PASS",
        "chunks": manifest["chunk_count"],
        "canonical_terms": total,
        "expanded_terms": expanded,
        "local_profiles": profiles,
        "v1_terms_replayed": overlap,
        "independent_second_jet_replay": True,
    }


if __name__ == "__main__":
    print(json.dumps(verify(), indent=2, sort_keys=True))
