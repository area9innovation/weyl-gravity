#!/usr/bin/env python3
"""Stream the complete five-current PBW operation through coefficient-jet order two."""

from __future__ import annotations

import argparse
from collections import defaultdict
from copy import deepcopy
from fractions import Fraction
import gzip
import hashlib
import io
from itertools import combinations_with_replacement
import json
from pathlib import Path
from typing import Any, Iterable

import sympy as sp
from jsonschema import Draft202012Validator

from bridge.einstein_sector.product_taylor_engine import COORDINATES, PAIRS
from d_quotient_classical.relative.einstein_weyl_relative_five_stabilizer_current import (
    coefficient_profile,
    stabilizer_vectors,
)


ROOT = Path(__file__).resolve().parents[2]
RESULT_ID = "EINSTEIN_WEYL_RELATIVE_FULL_FIVE_CURRENT_SECOND_JET_EXPORT_V1"
OUTPUT = ROOT / f"d_quotient_classical/certificates/{RESULT_ID}.json"
GENERATED = ROOT / "d_quotient_classical/generated/einstein_weyl_relative_full_five_current_second_jet_export_v1"
MANIFEST = GENERATED / "manifest.json"
REPORT = ROOT / "d_quotient_classical/reports/einstein-weyl-relative-full-five-current-second-jet-export.md"
SCHEMA = ROOT / "d_quotient_classical/schema/relative-full-five-current-second-jet-export-v1.schema.json"
MANIFEST_SCHEMA = ROOT / "d_quotient_classical/schema/relative-full-five-current-second-jet-manifest-v1.schema.json"
CHUNK_SCHEMA = ROOT / "d_quotient_classical/schema/relative-full-five-current-second-jet-chunk-v1.schema.json"
VERIFIER = ROOT / "d_quotient_classical/relative/verify_einstein_weyl_relative_full_five_current_second_jet_export.py"
TESTS = ROOT / "d_quotient_classical/relative/tests/test_einstein_weyl_relative_full_five_current_second_jet_export.py"
DEPENDENCIES = {
    "hessian_second_current_input": ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_HESSIAN_SECOND_CURRENT_INPUT_V1.json",
    "current_export_v1": ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_FULL_FIVE_CURRENT_PBW_EXPORT_V1.json",
    "current_payload_v1": ROOT / "d_quotient_classical/generated/einstein_weyl_relative_full_five_current_pbw_export_v1/current_q2.json",
}
HESSIAN_PAYLOAD = ROOT / "d_quotient_classical/generated/einstein_weyl_relative_hessian_second_current_input_v1/relative_hessian.json"

GENERATORS = ["H", "P_x", "J_1", "J_2", "J_3"]
AXES = ["t", "x", "theta", "phi"]
Profile = dict[tuple[int, ...], Fraction]
CurrentKey = tuple[int, tuple[int, ...], int, tuple[int, ...]]
LinearTerm = tuple[int, int, tuple[int, ...], Profile]


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise TypeError(path)
    return value


def _sha_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha(path: Path) -> str:
    return _sha_bytes(path.read_bytes())


def _artifact(path: Path, value: dict[str, Any]) -> dict[str, str]:
    return {
        "artifact_id": str(value.get("result_id", value.get("schema"))),
        "path": str(path.relative_to(ROOT)),
        "sha256": _sha(path),
    }


def _fraction_string(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def _words(maximum_order: int) -> Iterable[tuple[int, ...]]:
    yield ()
    for order in range(1, maximum_order + 1):
        yield from combinations_with_replacement(range(4), order)


def _render(value: object) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def _compact(value: object) -> bytes:
    return (json.dumps(value, separators=(",", ":"), sort_keys=True) + "\n").encode()


def _gzip(value: bytes) -> bytes:
    output = io.BytesIO()
    with gzip.GzipFile(filename="", fileobj=output, mode="wb", mtime=0, compresslevel=9) as stream:
        stream.write(value)
    return output.getvalue()


def _hessian_terms() -> list[tuple[int, int, tuple[int, ...], Profile]]:
    payload = _load(HESSIAN_PAYLOAD)
    return [
        (
            term["output_local"],
            term["input_local"],
            tuple(term["word"]),
            {
                tuple(item["word"]): Fraction(item["coefficient"])
                for item in term["coefficient_jets"]
            },
        )
        for term in payload["terms"]
    ]


def _green_component(axis: int) -> dict[CurrentKey, Profile]:
    raw: dict[CurrentKey, Profile] = defaultdict(lambda: defaultdict(Fraction))
    derivative_words = tuple(_words(2))
    for output, incoming, word, profile in _hessian_terms():
        for position, current_axis in enumerate(word):
            if current_axis != axis:
                continue
            prefix = word[:position]
            suffix = word[position + 1 :]
            for mask in range(1 << len(prefix)):
                coefficient_word = tuple(sorted(prefix[index] for index in range(len(prefix)) if mask & (1 << index)))
                left_word = tuple(sorted(prefix[index] for index in range(len(prefix)) if not mask & (1 << index)))
                key = (output, left_word, incoming, suffix)
                sign = Fraction((-1) ** position)
                for derivative in derivative_words:
                    raw[key][derivative] += sign * profile.get(tuple(sorted((*coefficient_word, *derivative))), Fraction())
    antisymmetric: dict[CurrentKey, Profile] = defaultdict(lambda: defaultdict(Fraction))
    for (left, left_word, right, right_word), profile in raw.items():
        for derivative, value in profile.items():
            antisymmetric[(left, left_word, right, right_word)][derivative] += value / 2
            antisymmetric[(right, right_word, left, left_word)][derivative] -= value / 2
    return {
        key: {word: value for word, value in profile.items() if value}
        for key, profile in antisymmetric.items()
        if any(profile.values())
    }


def _merge_linear(raw: list[LinearTerm]) -> list[LinearTerm]:
    combined: dict[tuple[int, int, tuple[int, ...]], Profile] = defaultdict(lambda: defaultdict(Fraction))
    for output, incoming, word, profile in raw:
        for derivative, value in profile.items():
            combined[(output, incoming, tuple(sorted(word)))][derivative] += value
    return [
        (output, incoming, word, {jet: value for jet, value in profile.items() if value})
        for (output, incoming, word), profile in sorted(combined.items())
        if any(profile.values())
    ]


def _action(generator: sp.Matrix) -> list[LinearTerm]:
    raw: list[LinearTerm] = []
    pair_index = {pair: index for index, pair in enumerate(PAIRS)}
    for output, (mu, nu) in enumerate(PAIRS):
        for rho in range(4):
            raw.append((output, output, (rho,), coefficient_profile(generator[rho], 5)))
            first_input = pair_index[tuple(sorted((rho, nu)))]
            second_input = pair_index[tuple(sorted((mu, rho)))]
            raw.append((output, first_input, (), coefficient_profile(sp.diff(generator[rho], COORDINATES[mu]), 5)))
            raw.append((output, second_input, (), coefficient_profile(sp.diff(generator[rho], COORDINATES[nu]), 5)))
    for mu in range(4):
        output = 10 + mu
        for rho in range(4):
            profile = coefficient_profile(generator[rho], 5)
            raw.append((output, output, (rho,), profile))
            raw.append((output, 10 + rho, (mu,), {word: -value for word, value in profile.items()}))
    return _merge_linear(raw)


def _compose_component(current: dict[CurrentKey, Profile], action: list[LinearTerm]) -> dict[CurrentKey, Profile]:
    by_output: dict[int, list[LinearTerm]] = defaultdict(list)
    for term in action:
        by_output[term[0]].append(term)
    one_sided: dict[CurrentKey, Profile] = defaultdict(lambda: defaultdict(Fraction))
    output_jets = tuple(_words(2))
    for (left, left_word, action_output, differentiated_word), current_profile in current.items():
        for _, incoming, action_word, action_profile in by_output[action_output]:
            for derivative_mask in range(1 << len(differentiated_word)):
                coefficient_word = tuple(sorted(
                    differentiated_word[index]
                    for index in range(len(differentiated_word))
                    if derivative_mask & (1 << index)
                ))
                field_word = tuple(sorted((*action_word, *(
                    differentiated_word[index]
                    for index in range(len(differentiated_word))
                    if not derivative_mask & (1 << index)
                ))))
                key = (left, left_word, incoming, field_word)
                for output_jet in output_jets:
                    for jet_mask in range(1 << len(output_jet)):
                        current_jet = tuple(output_jet[index] for index in range(len(output_jet)) if jet_mask & (1 << index))
                        action_jet = tuple(output_jet[index] for index in range(len(output_jet)) if not jet_mask & (1 << index))
                        one_sided[key][output_jet] += (
                            current_profile.get(current_jet, Fraction())
                            * action_profile.get(tuple(sorted((*coefficient_word, *action_jet))), Fraction())
                        )
    symmetric: dict[CurrentKey, Profile] = defaultdict(lambda: defaultdict(Fraction))
    for (left, left_word, right, right_word), profile in one_sided.items():
        for jet, value in profile.items():
            symmetric[(left, left_word, right, right_word)][jet] += value / 2
            symmetric[(right, right_word, left, left_word)][jet] += value / 2
    return {
        key: {word: value for word, value in profile.items() if value}
        for key, profile in symmetric.items()
        if any(profile.values())
    }


def _metadata() -> tuple[dict[str, Any], dict[str, Any], dict[tuple[str, int], dict[str, Any]]]:
    v1 = _load(DEPENDENCIES["current_payload_v1"])
    source_by_local = {row["local_field"]: row for row in v1["field_order"]}
    output_rows = {(row["generator"], row["component_axis"]): row for row in v1["output_rows"]}
    return v1, source_by_local, output_rows


def _chunk(
    generator: str,
    axis: int,
    current: dict[CurrentKey, Profile],
    action: list[LinearTerm],
    source_by_local: dict[int, dict[str, Any]],
    output_row: dict[str, Any],
) -> dict[str, Any]:
    rows = _compose_component(current, action)
    sign = Fraction(output_row["vector_density_to_form_sign"])
    raw_terms = []
    diagonal_count = 0
    expanded_count = 0
    for (left, left_word, right, right_word), profile in sorted(rows.items()):
        expanded_count += 1
        left_key = (left, left_word)
        right_key = (right, right_word)
        if left_key > right_key:
            continue
        if left_key == right_key:
            diagonal_count += 1
        encoded = tuple(
            (word, _fraction_string(sign * value))
            for word, value in sorted(profile.items())
            if value
        )
        if encoded:
            raw_terms.append((left, left_word, right, right_word, encoded))
    profiles = sorted({item[4] for item in raw_terms})
    profile_index = {profile: index for index, profile in enumerate(profiles)}
    terms = []
    for left, left_word, right, right_word, profile in raw_terms:
        terms.append(
            {
                "inputs": [
                    {
                        "local_field": left,
                        "row": source_by_local[left]["row"],
                        "row_id": source_by_local[left]["row_id"],
                        "word": list(left_word),
                    },
                    {
                        "local_field": right,
                        "row": source_by_local[right]["row"],
                        "row_id": source_by_local[right]["row_id"],
                        "word": list(right_word),
                    },
                ],
                "coefficient_profile": profile_index[profile],
            }
        )
    return {
        "schema": "pure-weyl-relative-full-five-current-second-jet-chunk-v1",
        "result_id": f"{RESULT_ID}_{generator}_{AXES[axis]}",
        "generator": generator,
        "component_axis": axis,
        "vector_density_component": AXES[axis],
        "output": {"row": output_row["row"], "row_id": output_row["row_id"]},
        "vector_density_to_form_sign": output_row["vector_density_to_form_sign"],
        "maximum_input_derivative_order": 4,
        "maximum_coefficient_jet_order": 2,
        "input_exchange_symmetry": "symmetric_expand_off_diagonal",
        "coefficient_profiles": [
            {
                "index": index,
                "coefficient_jets": [
                    {"word": list(word), "coefficient": value}
                    for word, value in profile
                ],
            }
            for index, profile in enumerate(profiles)
        ],
        "coefficient_profile_count": len(profiles),
        "canonical_term_count": len(terms),
        "diagonal_term_count": diagonal_count,
        "expanded_term_count": expanded_count,
        "terms": terms,
    }


def build_outputs() -> tuple[dict[str, Any], dict[str, Any], list[tuple[Path, bytes]]]:
    dependencies = {name: _load(path) for name, path in DEPENDENCIES.items()}
    hessian_certificate = dependencies["hessian_second_current_input"]
    if not hessian_certificate["classification"]["second_current_coefficient_derivatives_authorized"]:
        raise AssertionError("second-current Hessian coefficient depth is unavailable")
    v1, source_by_local, output_rows = _metadata()
    vectors = stabilizer_vectors()
    actions = {name: _action(vectors[name]) for name in GENERATORS}
    chunks = []
    files = []
    total_terms = total_expanded = total_profiles = 0
    generator_counts = defaultdict(int)
    for axis in range(4):
        green = _green_component(axis)
        for generator_index, generator in enumerate(GENERATORS):
            chunk = _chunk(
                generator,
                axis,
                green,
                actions[generator],
                source_by_local,
                output_rows[(generator, axis)],
            )
            plain = _compact(chunk)
            compressed = _gzip(plain)
            path = GENERATED / f"{generator_index:02d}-{axis:02d}-{generator}-{AXES[axis]}.json.gz"
            record = {
                "generator": generator,
                "component_axis": axis,
                "path": str(path.relative_to(ROOT)),
                "sha256": _sha_bytes(compressed),
                "uncompressed_sha256": _sha_bytes(plain),
                "bytes": len(compressed),
                "uncompressed_bytes": len(plain),
                "canonical_term_count": chunk["canonical_term_count"],
                "expanded_term_count": chunk["expanded_term_count"],
                "coefficient_profile_count": chunk["coefficient_profile_count"],
            }
            chunks.append(record)
            files.append((path, compressed))
            total_terms += chunk["canonical_term_count"]
            total_expanded += chunk["expanded_term_count"]
            total_profiles += chunk["coefficient_profile_count"]
            generator_counts[generator] += chunk["canonical_term_count"]
    manifest = {
        "schema": "pure-weyl-relative-full-five-current-second-jet-manifest-v1",
        "result_id": f"{RESULT_ID}_MANIFEST",
        "background_id": "compact_magnetic_Plebanski_Hacyan_product",
        "coefficient_field": "Q",
        "operation": "q2(field,field)->K_P^1=Omega^3(M;g_stab^*)",
        "generator_order": GENERATORS,
        "axis_order": AXES,
        "field_order": v1["field_order"],
        "output_rows": v1["output_rows"],
        "maximum_input_derivative_order": 4,
        "maximum_coefficient_jet_order": 2,
        "chunk_encoding": "deterministic-gzip-of-canonical-compact-json; mtime=0; empty filename",
        "chunk_count": len(chunks),
        "canonical_term_count": total_terms,
        "expanded_term_count": total_expanded,
        "local_coefficient_profile_count": total_profiles,
        "generator_term_counts": dict(generator_counts),
        "chunks": chunks,
        "claim_boundary": "This manifest and its twenty content-addressed chunks are the complete second-coefficient-jet extension of the five field-field current operations. They do not construct A, f2, a repaired relative q2 or a causal map.",
    }
    manifest_bytes = _render(manifest).encode()
    certificate = {
        "schema": "pure-weyl-relative-full-five-current-second-jet-export-v1",
        "result_id": RESULT_ID,
        "result_state": "COMPLETE_STREAMED_FIVE_CURRENT_SECOND_COEFFICIENT_JETS_EXPORTED",
        "lifecycle_status": "COEFFICIENT_COMPUTED",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "scope": hessian_certificate["scope"] | {
            "charge_sector": "five connected spacetime stabilizer currents",
            "carrier": "Sym^2 of 14 source fields to 20 primal horizontal three-form rows",
            "degree": "arity-two current operation",
        },
        "dependencies": {name: _artifact(path, dependencies[name]) for name, path in DEPENDENCIES.items()},
        "manifest": {
            "path": str(MANIFEST.relative_to(ROOT)),
            "sha256": _sha_bytes(manifest_bytes),
            "bytes": len(manifest_bytes),
            "chunk_count": len(chunks),
            "canonical_term_count": total_terms,
            "expanded_term_count": total_expanded,
            "generator_term_counts": dict(generator_counts),
            "maximum_coefficient_jet_order": 2,
        },
        "streaming": {
            "unit": "one generator and one vector-density component",
            "maximum_live_chunks": 1,
            "global_profile_table_materialized": False,
            "deterministic_compression": True,
            "content_addressed_chunks": True,
        },
        "classification": {
            "complete_full_five_current_second_jet_export": True,
            "coefficientwise_v1_overlap_replayed": True,
            "support_local_chain_map_A_constructed": False,
            "order_one_top_descent_solved": False,
            "relative_q2_repaired": False,
            "causal_observable_particle_or_quantum_claim": False,
        },
        "next_gate": "SOLVE_OR_OBSTRUCT_THE_406_PARAMETER_ORDER_ONE_CHAIN_SYSTEM",
        "provenance": {
            "source_manifest": {
                str(path.relative_to(ROOT)): _sha(path)
                for path in (Path(__file__).resolve(), VERIFIER, TESTS, SCHEMA, MANIFEST_SCHEMA, CHUNK_SCHEMA)
            },
            "verification_commands": [
                "PYTHONPATH=. python3 -m d_quotient_classical.relative.einstein_weyl_relative_full_five_current_second_jet_export --check --guards",
                "PYTHONPATH=. python3 -m d_quotient_classical.relative.verify_einstein_weyl_relative_full_five_current_second_jet_export",
                "python3 -m unittest d_quotient_classical.relative.tests.test_einstein_weyl_relative_full_five_current_second_jet_export",
            ],
        },
        "claim_boundary": "This LOCAL-ALGEBRAIC artifact closes the coefficient-depth input required to compose an order-one A1 with every one of the five support-local field-field currents. The payload is streamed into twenty independently hashed deterministic gzip chunks, so no all-current in-memory table is required. It does not solve the 406-parameter chain system, construct A or f2, repair relative q2, compare pairings or establish bounded, causal, observable, particle or quantum claims.",
    }
    return certificate, manifest, files


def validate(certificate: dict[str, Any], manifest: dict[str, Any], files: list[tuple[Path, bytes]]) -> None:
    schema = _load(SCHEMA)
    manifest_schema = _load(MANIFEST_SCHEMA)
    chunk_schema = _load(CHUNK_SCHEMA)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator.check_schema(manifest_schema)
    Draft202012Validator.check_schema(chunk_schema)
    Draft202012Validator(schema).validate(certificate)
    Draft202012Validator(manifest_schema).validate(manifest)
    by_path = {str(path.relative_to(ROOT)): data for path, data in files}
    for record in manifest["chunks"]:
        data = by_path[record["path"]]
        chunk = json.loads(gzip.decompress(data))
        Draft202012Validator(chunk_schema).validate(chunk)


def _report(certificate: dict[str, Any]) -> str:
    return f"""# Streamed five-current second-jet export

The complete five-current table is now exported through coefficient-jet order
two as `{certificate['manifest']['chunk_count']}` deterministic,
content-addressed gzip chunks.  The chunks contain
`{certificate['manifest']['canonical_term_count']}` canonical symmetric terms
(`{certificate['manifest']['expanded_term_count']}` after ordered expansion),
split by generator and vector-density component.  Generation and verification
hold at most one chunk live at a time.

This closes the current-input prerequisite for the 406-parameter order-one
chain solve.  No positive-order lift or repaired relative `q2` is claimed.
"""


def _guards(value: dict[str, Any], manifest: dict[str, Any], files: list[tuple[Path, bytes]]) -> None:
    for key in (
        "support_local_chain_map_A_constructed",
        "order_one_top_descent_solved",
        "relative_q2_repaired",
        "causal_observable_particle_or_quantum_claim",
    ):
        mutant = deepcopy(value)
        mutant["classification"][key] = True
        try:
            validate(mutant, manifest, files)
        except Exception:
            continue
        raise AssertionError(f"mutation guard accepted classification.{key}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()
    certificate, manifest, files = build_outputs()
    validate(certificate, manifest, files)
    if args.write:
        GENERATED.mkdir(parents=True, exist_ok=True)
        for path, data in files:
            path.write_bytes(data)
        MANIFEST.write_text(_render(manifest))
        OUTPUT.write_text(_render(certificate))
        REPORT.write_text(_report(certificate))
    if args.check:
        for path, data in files:
            if path.read_bytes() != data:
                raise AssertionError(f"current second-jet chunk drifted: {path}")
        if MANIFEST.read_text() != _render(manifest) or OUTPUT.read_text() != _render(certificate) or REPORT.read_text() != _report(certificate):
            raise AssertionError("current second-jet export metadata drifted")
    if args.guards:
        _guards(certificate, manifest, files)
    print(f"{RESULT_ID}: PASS")


if __name__ == "__main__":
    main()
