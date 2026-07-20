#!/usr/bin/env python3
"""Export the relative Hessian coefficient jets needed by a second-jet current."""

from __future__ import annotations

import argparse
from collections import defaultdict
from copy import deepcopy
from fractions import Fraction
import hashlib
from itertools import combinations_with_replacement
import json
from pathlib import Path
import pickle
from typing import Any, Iterable

from jsonschema import Draft202012Validator

from bridge.einstein_sector.einstein_maxwell_product_taylor import (
    EQUATION_SLICE as EINSTEIN_EQUATIONS,
    FIELD_SLICE as EINSTEIN_FIELDS,
    build_q1 as build_einstein_q1,
)
from bridge.einstein_sector.product_taylor_engine import (
    operation_record as einstein_operation_record,
)
from bridge.einstein_sector.product_theta_jet_engine import (
    operation_record as weyl_operation_record,
)
from d_quotient_classical.relative.einstein_weyl_relative_hessian_green_current_cone import (
    relative_operator_terms,
)


ROOT = Path(__file__).resolve().parents[2]
RESULT_ID = "EINSTEIN_WEYL_RELATIVE_HESSIAN_SECOND_CURRENT_INPUT_V1"
OUTPUT = ROOT / f"d_quotient_classical/certificates/{RESULT_ID}.json"
PAYLOAD = ROOT / "d_quotient_classical/generated/einstein_weyl_relative_hessian_second_current_input_v1/relative_hessian.json"
REPORT = ROOT / "d_quotient_classical/reports/einstein-weyl-relative-hessian-second-current-input.md"
SCHEMA = ROOT / "d_quotient_classical/schema/relative-hessian-second-current-input-v1.schema.json"
PAYLOAD_SCHEMA = ROOT / "d_quotient_classical/schema/relative-hessian-second-current-payload-v1.schema.json"
VERIFIER = ROOT / "d_quotient_classical/relative/verify_einstein_weyl_relative_hessian_second_current_input.py"
TESTS = ROOT / "d_quotient_classical/relative/tests/test_einstein_weyl_relative_hessian_second_current_input.py"

CHECKPOINT_FINGERPRINT = "ac923be427404bf66cac4adaf5b55f3400b03247d8e2f14091ac873f2cff046e"
CHECKPOINT = ROOT / "build/weyl_maxwell_product_linfinity_v1" / CHECKPOINT_FINGERPRINT
SOURCE_CACHE = ROOT / "build/einstein_weyl_relative_hessian_second_current_input_v1/einstein_records_order3.pkl"
SOURCE_CACHE_INPUTS = (
    ROOT / "bridge/einstein_sector/einstein_maxwell_product_taylor.py",
    ROOT / "bridge/einstein_sector/product_taylor_engine.py",
)
DEPENDENCIES = {
    "relative_hessian": ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_HESSIAN_GREEN_CURRENT_CONE_V1.json",
    "einstein_action": ROOT / "bridge/certificates/EINSTEIN_MAXWELL_PRODUCT_LINFINITY_THROUGH_ARITY_THREE_V1.json",
    "weyl_action": ROOT / "bridge/certificates/WEYL_MAXWELL_PRODUCT_LINFINITY_THROUGH_ARITY_THREE_V1.json",
    "einstein_q1": ROOT / "bridge/einstein_sector/generated/einstein_maxwell_product_linfinity_v1/q1.json",
    "weyl_q1": ROOT / "bridge/einstein_sector/generated/weyl_maxwell_product_linfinity_v1/q1.json",
}


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise TypeError(path)
    return value


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


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


def _volume_jet(word: tuple[int, ...]) -> Fraction:
    if any(axis != 2 for axis in word) or len(word) % 2:
        return Fraction()
    return Fraction((-1) ** (len(word) // 2))


def _multiply_by_volume(
    profile: dict[tuple[int, ...], Fraction],
    maximum_order: int,
) -> dict[tuple[int, ...], Fraction]:
    output: dict[tuple[int, ...], Fraction] = defaultdict(Fraction)
    for word in _words(maximum_order):
        for mask in range(1 << len(word)):
            left = tuple(word[index] for index in range(len(word)) if mask & (1 << index))
            right = tuple(word[index] for index in range(len(word)) if not mask & (1 << index))
            output[word] += profile.get(left, Fraction()) * _volume_jet(right)
    return {word: value for word, value in output.items() if value}


def _record_profile(record: dict[str, Any]) -> dict[tuple[int, ...], Fraction]:
    return {
        tuple(item["word"]): Fraction(item["coefficient"])
        for item in record["coefficient_jets"]
    }


def _source_records(
    use_cache: bool = True,
) -> list[tuple[int, int, tuple[int, ...], dict[tuple[int, ...], Fraction]]]:
    cache_key = tuple(_sha(path) for path in SOURCE_CACHE_INPUTS)
    if use_cache and SOURCE_CACHE.is_file():
        cached_key, cached_records = pickle.loads(SOURCE_CACHE.read_bytes())
        if cached_key == cache_key:
            return cached_records
    rows = build_einstein_q1()
    output = []
    for local_output, row in enumerate(EINSTEIN_EQUATIONS):
        for record in einstein_operation_record(rows[row], output_row=local_output, coefficient_jet_order=3):
            incoming = record["inputs"][0]["row"] - EINSTEIN_FIELDS[0]
            if 0 <= incoming < 14:
                output.append((local_output, incoming, tuple(record["inputs"][0]["word"]), _record_profile(record)))
    SOURCE_CACHE.parent.mkdir(parents=True, exist_ok=True)
    SOURCE_CACHE.write_bytes(pickle.dumps((cache_key, output), protocol=5))
    return output


def _target_records() -> list[tuple[int, int, tuple[int, ...], dict[tuple[int, ...], Fraction]]]:
    q1_dir = CHECKPOINT / "q1"
    if not (q1_dir / "stage.done.json").is_file():
        raise FileNotFoundError(
            "missing content-addressed Weyl q1 checkpoint; run "
            "`PYTHONPATH=. python3 -m bridge.einstein_sector.run_weyl_maxwell_product_checkpointed --resume`"
        )
    output = []
    for local_output, row in enumerate(range(20, 34)):
        operator = pickle.loads((q1_dir / f"row-{row:02d}.pkl").read_bytes())
        for record in weyl_operation_record(operator, output_row=local_output, coefficient_jet_order=5):
            incoming = record["inputs"][0]["row"] - 6
            if 0 <= incoming < 14:
                output.append((local_output, incoming, tuple(record["inputs"][0]["word"]), _record_profile(record)))
    return output


def _combine(
    target: list[tuple[int, int, tuple[int, ...], dict[tuple[int, ...], Fraction]]],
    source: list[tuple[int, int, tuple[int, ...], dict[tuple[int, ...], Fraction]]],
) -> list[dict[str, Any]]:
    combined: dict[tuple[int, int, tuple[int, ...]], dict[tuple[int, ...], Fraction]] = defaultdict(
        lambda: defaultdict(Fraction)
    )
    for sign, records in ((Fraction(1), target), (Fraction(-1), source)):
        for output, incoming, word, profile in records:
            maximum_order = len(word) + 1
            for jet, coefficient in _multiply_by_volume(profile, maximum_order).items():
                combined[(output, incoming, word)][jet] += sign * coefficient
    terms = []
    for (output, incoming, word), profile in sorted(combined.items()):
        jets = [
            {"word": list(jet), "coefficient": _fraction_string(coefficient)}
            for jet, coefficient in sorted(profile.items())
            if coefficient
        ]
        if jets:
            terms.append(
                {
                    "output_local": output,
                    "input_local": incoming,
                    "word": list(word),
                    "required_coefficient_jet_order": len(word) + 1,
                    "coefficient_jets": jets,
                }
            )
    return terms


def _checkpoint_provenance() -> dict[str, Any]:
    q1_dir = CHECKPOINT / "q1"
    stage = q1_dir / "stage.done.json"
    rows = [q1_dir / f"row-{row:02d}.pkl" for row in range(20, 34)]
    return {
        "fingerprint": CHECKPOINT_FINGERPRINT,
        "checkpoint_stage_record_sha256": _sha(stage),
        "physical_equation_row_sha256": {_path.name: _sha(_path) for _path in rows},
        "rebuild_command": "PYTHONPATH=. python3 -m bridge.einstein_sector.run_weyl_maxwell_product_checkpointed --resume",
        "role": "content-addressed action-derived acceleration for target coefficient jets of orders five; not a separately committed mathematical input",
    }


def _render(value: object) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def build_payload(use_source_cache: bool = True) -> dict[str, Any]:
    target = _target_records()
    source = _source_records(use_source_cache)
    raw_target_fifth = sum(
        len(jet) == 5
        for _, _, _, profile in target
        for jet in profile
    )
    raw_source_third = sum(
        len(jet) == 3
        for _, _, _, profile in source
        for jet in profile
    )
    terms = _combine(target, source)
    old: dict[tuple[int, int, tuple[int, ...]], dict[tuple[int, ...], Fraction]] = defaultdict(
        lambda: defaultdict(Fraction)
    )
    for output, incoming, word, profile in relative_operator_terms():
        for jet, coefficient in profile.items():
            old[(output, incoming, word)][jet] += coefficient
    old = {
        key: {jet: coefficient for jet, coefficient in profile.items() if coefficient}
        for key, profile in old.items()
        if any(profile.values())
    }
    relevant_old = {
        key: {
            jet: coefficient
            for jet, coefficient in profile.items()
            if len(jet) <= len(key[2]) + 1
        }
        for key, profile in old.items()
    }
    relevant_old = {key: profile for key, profile in relevant_old.items() if profile}
    new = {
        (term["output_local"], term["input_local"], tuple(term["word"])): {
            tuple(item["word"]): Fraction(item["coefficient"])
            for item in term["coefficient_jets"]
        }
        for term in terms
    }
    if not set(relevant_old) <= set(new):
        missing = sorted(set(relevant_old) - set(new))
        raise AssertionError(f"frozen relative Hessian support is not retained: {missing[:5]}")
    for key, old_profile in relevant_old.items():
        operator_order = len(key[2])
        replay_order = 4 if operator_order >= 3 else 2
        for word, coefficient in old_profile.items():
            if len(word) <= replay_order and new[key].get(word, Fraction()) != coefficient:
                raise AssertionError(f"frozen relative Hessian replay failed: {key}, {word}")
    jet_counts = {
        str(order): sum(
            len(item["coefficient_jets"])
            for item in terms
            if len(item["word"]) == order
        )
        for order in range(5)
    }
    return {
        "schema": "pure-weyl-relative-hessian-second-current-payload-v1",
        "result_id": f"{RESULT_ID}_PAYLOAD",
        "background_id": "compact_magnetic_Plebanski_Hacyan_product",
        "coefficient_field": "Q",
        "operator": "sin(theta)*(E_Weyl-Maxwell-E_Einstein-Maxwell)",
        "maximum_operator_order": 4,
        "current_coefficient_jet_order": 2,
        "profile_completeness_rule": "an operator monomial of order r carries coefficient jets through order r+1, exactly sufficient for two coefficient derivatives of its Green concomitant",
        "term_count": len(terms),
        "newly_visible_term_count": len(set(new) - set(relevant_old)),
        "raw_action_jet_census": {
            "target_fifth": raw_target_fifth,
            "source_third": raw_source_third,
        },
        "coefficient_jet_counts_by_operator_order": jet_counts,
        "terms": terms,
        "claim_boundary": "This portable LOCAL-ALGEBRAIC payload extends only the action-derived relative physical Hessian coefficient profiles needed to differentiate its Green concomitant twice. It is not a current, a relative lift, a repaired q2, a causal operator or a particle claim.",
    }


def build_certificate(payload: dict[str, Any]) -> dict[str, Any]:
    dependencies = {name: _artifact(path, _load(path)) for name, path in DEPENDENCIES.items()}
    rendered = _render(payload).encode()
    relative_fifth_count = sum(
        1
        for term in payload["terms"]
        for jet in term["coefficient_jets"]
        if len(jet["word"]) == 5
    )
    relative_source_order_third = sum(
        1
        for term in payload["terms"]
        if len(term["word"]) <= 2
        for jet in term["coefficient_jets"]
        if len(jet["word"]) == 3
    )
    return {
        "schema": "pure-weyl-relative-hessian-second-current-input-v1",
        "result_id": RESULT_ID,
        "result_state": "ACTION_DERIVED_RELATIVE_HESSIAN_JETS_SUFFICIENT_FOR_SECOND_CURRENT_DERIVATIVES",
        "lifecycle_status": "COEFFICIENT_COMPUTED",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "scope": {
            "theory": "Einstein-Maxwell source relative to Weyl-Maxwell target",
            "background": "compact magnetic Plebanski-Hacyan product",
            "boundaries": "local coefficient jets at the homogeneous equatorial base point",
            "charge_sector": "physical 14-field relative Hessian before five-stabilizer precomposition",
            "carrier": "14 source fields to 14 relative Euler rows",
            "degree": "unary Hessian input", "parity": "even physical sector",
            "ell": "not harmonic-reduced", "m": "not harmonic-reduced",
            "k": "arbitrary local covector", "omega": "arbitrary local covector",
        },
        "dependencies": dependencies,
        "payload": {
            "path": str(PAYLOAD.relative_to(ROOT)),
            "sha256": hashlib.sha256(rendered).hexdigest(),
            "bytes": len(rendered),
            "term_count": payload["term_count"],
            "newly_visible_term_count": payload["newly_visible_term_count"],
            "maximum_operator_order": payload["maximum_operator_order"],
            "maximum_coefficient_jet_order": 5,
            "raw_target_fifth_jet_count": payload["raw_action_jet_census"]["target_fifth"],
            "raw_source_third_jet_count": payload["raw_action_jet_census"]["source_third"],
            "relative_fifth_jet_count": relative_fifth_count,
            "relative_source_order_third_jet_count": relative_source_order_third,
        },
        "derivation": {
            "source": "Einstein-Maxwell q1 rebuilt directly from the authoritative action Taylor producer through coefficient order three",
            "target": "Weyl-Maxwell q1 read from the content-addressed checkpoint produced by the authoritative action Taylor producer through coefficient order five",
            "density": "exact multivariate Leibniz multiplication by sin(theta)",
            "required_order": "Green telescoping of an order-r monomial followed by two coefficient derivatives needs Hessian coefficient jets through r+1",
            "frozen_lower_jet_replay": "all existing target jets through order four and source jets through order two agree coefficientwise on their declared domains",
        },
        "checkpoint_provenance": _checkpoint_provenance(),
        "classification": {
            "action_derived_relative_hessian_profiles_extended": True,
            "second_current_coefficient_derivatives_authorized": True,
            "five_current_second_jet_exported": False,
            "support_local_chain_map_A_constructed": False,
            "relative_q2_repaired": False,
            "causal_observable_particle_or_quantum_claim": False,
        },
        "next_gate": "STREAM_THE_FIVE_CURRENT_COEFFICIENT_JETS_THROUGH_ORDER_TWO",
        "provenance": {
            "source_manifest": {
                str(path.relative_to(ROOT)): _sha(path)
                for path in (Path(__file__).resolve(), VERIFIER, TESTS, SCHEMA, PAYLOAD_SCHEMA)
            },
            "verification_commands": [
                "PYTHONPATH=. python3 -m d_quotient_classical.relative.einstein_weyl_relative_hessian_second_current_input --check --guards",
                "PYTHONPATH=. python3 -m d_quotient_classical.relative.verify_einstein_weyl_relative_hessian_second_current_input",
                "python3 -m unittest d_quotient_classical.relative.tests.test_einstein_weyl_relative_hessian_second_current_input",
                "PYTHONPATH=. python3 -m d_quotient_classical.relative.einstein_weyl_relative_hessian_second_current_input --deep-rebuild",
            ],
        },
        "claim_boundary": "This LOCAL-ALGEBRAIC certificate closes the previously missing coefficient-depth prerequisite for a second-jet Green-current export. The deep rail rebuilds the Einstein coefficients from the action and reads the content-addressed action-derived Weyl checkpoint; the fast independent rail checks exact density calculus, profile completeness and every overlap with the frozen unary exports. It does not itself export the five currents, solve the 406-parameter chain system, construct A or f2, repair the relative q2 or establish any bounded, causal, observable, particle or quantum claim.",
    }


def validate(certificate: dict[str, Any], payload: dict[str, Any]) -> None:
    schema = _load(SCHEMA)
    payload_schema = _load(PAYLOAD_SCHEMA)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator.check_schema(payload_schema)
    Draft202012Validator(schema).validate(certificate)
    Draft202012Validator(payload_schema).validate(payload)


def _report(certificate: dict[str, Any]) -> str:
    return f"""# Relative Hessian input for second current jets

The action-derived relative physical Hessian now carries exactly the
coefficient depth needed to differentiate its Green concomitant twice.  An
operator monomial of order `r` is exported through coefficient-jet order
`r+1`; the complete payload has `{certificate['payload']['term_count']}` PBW
monomials.  The action rebuild contains
`{certificate['payload']['raw_target_fifth_jet_count']}` raw target fifth jets
and `{certificate['payload']['raw_source_third_jet_count']}` raw source third
jets.  Exact densitization and relative subtraction reduce these to
`{certificate['payload']['relative_fifth_jet_count']}` relative fifth jets and
`{certificate['payload']['relative_source_order_third_jet_count']}` relative
third jets on source-order monomials.  Thus the formerly unavailable odd-depth
coefficients are proved zero rather than silently truncated.

This closes only the coefficient-depth prerequisite.  The five-current
second-jet export and the 406-parameter order-one chain solve remain open.
"""


def _guards(value: dict[str, Any], payload: dict[str, Any]) -> None:
    for key in (
        "five_current_second_jet_exported",
        "support_local_chain_map_A_constructed",
        "relative_q2_repaired",
        "causal_observable_particle_or_quantum_claim",
    ):
        mutant = deepcopy(value)
        mutant["classification"][key] = True
        try:
            validate(mutant, payload)
        except Exception:
            continue
        raise AssertionError(f"mutation guard accepted classification.{key}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--guards", action="store_true")
    parser.add_argument("--deep-rebuild", action="store_true")
    args = parser.parse_args()
    if args.write or args.deep_rebuild:
        payload = build_payload(use_source_cache=not args.deep_rebuild)
        certificate = build_certificate(payload)
    else:
        payload = _load(PAYLOAD)
        certificate = build_certificate(payload)
    validate(certificate, payload)
    if args.write:
        PAYLOAD.parent.mkdir(parents=True, exist_ok=True)
        PAYLOAD.write_text(_render(payload))
        OUTPUT.write_text(_render(certificate))
        REPORT.write_text(_report(certificate))
    if args.check:
        if OUTPUT.read_text() != _render(certificate) or REPORT.read_text() != _report(certificate):
            raise AssertionError("relative Hessian second-current input outputs drifted")
    if args.deep_rebuild:
        if PAYLOAD.read_text() != _render(payload):
            raise AssertionError("deep action-derived relative Hessian rebuild drifted")
    if args.guards:
        _guards(certificate, payload)
    print(f"{RESULT_ID}: PASS")


if __name__ == "__main__":
    main()
