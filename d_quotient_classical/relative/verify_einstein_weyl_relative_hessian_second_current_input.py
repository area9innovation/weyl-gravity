#!/usr/bin/env python3
"""Independent fast replay of the relative Hessian second-current input."""

from __future__ import annotations

from collections import defaultdict
from fractions import Fraction
import hashlib
from itertools import combinations_with_replacement
import json
from pathlib import Path

from jsonschema import Draft202012Validator

from d_quotient_classical.relative.einstein_weyl_relative_hessian_green_current_cone import (
    relative_operator_terms,
)


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_HESSIAN_SECOND_CURRENT_INPUT_V1.json"
SCHEMA = ROOT / "d_quotient_classical/schema/relative-hessian-second-current-input-v1.schema.json"
PAYLOAD_SCHEMA = ROOT / "d_quotient_classical/schema/relative-hessian-second-current-payload-v1.schema.json"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


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
    if payload["term_count"] != len(payload["terms"]):
        raise AssertionError("payload term census drifted")

    actual = {}
    for item in payload["terms"]:
        key = (item["output_local"], item["input_local"], tuple(item["word"]))
        if key in actual:
            raise AssertionError(f"duplicate PBW monomial: {key}")
        if item["required_coefficient_jet_order"] != len(item["word"]) + 1:
            raise AssertionError(f"incomplete coefficient depth declaration: {key}")
        profile = {}
        previous = None
        for jet in item["coefficient_jets"]:
            word = tuple(jet["word"])
            if tuple(sorted(word)) != word or len(word) > item["required_coefficient_jet_order"]:
                raise AssertionError(f"invalid coefficient jet: {key}, {word}")
            if previous is not None and previous >= word:
                raise AssertionError(f"noncanonical coefficient profile: {key}")
            previous = word
            profile[word] = Fraction(jet["coefficient"])
        actual[key] = profile

    frozen_raw = defaultdict(lambda: defaultdict(Fraction))
    for output, incoming, word, profile in relative_operator_terms():
        for jet, value in profile.items():
            frozen_raw[(output, incoming, word)][jet] += value
    frozen = {
        key: {word: value for word, value in profile.items() if value}
        for key, profile in frozen_raw.items()
        if any(profile.values())
    }
    relevant_frozen = {
        key: {
            word: value
            for word, value in profile.items()
            if len(word) <= len(key[2]) + 1
        }
        for key, profile in frozen.items()
    }
    relevant_frozen = {key: profile for key, profile in relevant_frozen.items() if profile}
    if not set(relevant_frozen) <= set(actual):
        raise AssertionError("relative Hessian lost frozen action support")
    if len(set(actual) - set(relevant_frozen)) != payload["newly_visible_term_count"]:
        raise AssertionError("newly visible coefficient-support census drifted")
    replayed = 0
    for key, old_profile in relevant_frozen.items():
        comparison_order = 4 if len(key[2]) >= 3 else 2
        for word, value in old_profile.items():
            if len(word) <= comparison_order:
                replayed += 1
                if actual[key].get(word, Fraction()) != value:
                    raise AssertionError(f"coefficient overlap defect: {key}, {word}")

    fifth = sum(len(word) == 5 for profile in actual.values() for word in profile)
    third = sum(len(key[2]) <= 2 and len(word) == 3 for key, profile in actual.items() for word in profile)
    if fifth != certificate["payload"]["relative_fifth_jet_count"]:
        raise AssertionError("relative fifth-jet census drifted")
    if third != certificate["payload"]["relative_source_order_third_jet_count"]:
        raise AssertionError("relative source-order third-jet census drifted")
    if payload["raw_action_jet_census"]["target_fifth"] != certificate["payload"]["raw_target_fifth_jet_count"]:
        raise AssertionError("raw target fifth-jet census drifted")
    if payload["raw_action_jet_census"]["source_third"] != certificate["payload"]["raw_source_third_jet_count"]:
        raise AssertionError("raw source third-jet census drifted")
    flags = certificate["classification"]
    if any(
        flags[key]
        for key in (
            "five_current_second_jet_exported",
            "support_local_chain_map_A_constructed",
            "relative_q2_repaired",
            "causal_observable_particle_or_quantum_claim",
        )
    ):
        raise AssertionError("coefficient input overpromoted")
    return {
        "status": "PASS",
        "term_count": len(actual),
        "frozen_overlap_coefficients_replayed": replayed,
        "raw_target_fifth_jets": payload["raw_action_jet_census"]["target_fifth"],
        "raw_source_third_jets": payload["raw_action_jet_census"]["source_third"],
        "relative_fifth_jets": fifth,
        "relative_source_order_third_jets": third,
        "second_current_depth_complete": True,
    }


if __name__ == "__main__":
    print(json.dumps(verify(), indent=2, sort_keys=True))
