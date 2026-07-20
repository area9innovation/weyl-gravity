#!/usr/bin/env python3
"""Export the complete five-current PBW operation in portable row coordinates."""

from __future__ import annotations

import argparse
from collections import Counter
from copy import deepcopy
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from d_quotient_classical.relative.einstein_weyl_relative_five_stabilizer_current import (
    polarized_noether_current,
    stabilizer_action,
    stabilizer_vectors,
)


ROOT = Path(__file__).resolve().parents[2]
RESULT_ID = "EINSTEIN_WEYL_RELATIVE_FULL_FIVE_CURRENT_PBW_EXPORT_V1"
OUTPUT = ROOT / f"d_quotient_classical/certificates/{RESULT_ID}.json"
PAYLOAD = ROOT / "d_quotient_classical/generated/einstein_weyl_relative_full_five_current_pbw_export_v1/current_q2.json"
REPORT = ROOT / "d_quotient_classical/reports/einstein-weyl-relative-full-five-current-pbw-export.md"
SCHEMA = ROOT / "d_quotient_classical/schema/relative-full-five-current-pbw-export-v1.schema.json"
PAYLOAD_SCHEMA = ROOT / "d_quotient_classical/schema/relative-full-five-current-pbw-payload-v1.schema.json"
VERIFIER = ROOT / "d_quotient_classical/relative/verify_einstein_weyl_relative_full_five_current_pbw_export.py"
TESTS = ROOT / "d_quotient_classical/relative/tests/test_einstein_weyl_relative_full_five_current_pbw_export.py"
SOURCE_IMPLEMENTATION = ROOT / "d_quotient_classical/relative/einstein_weyl_relative_five_stabilizer_current.py"
CURRENT_LAYOUT = ROOT / "d_quotient_classical/generated/einstein_weyl_relative_five_current_de_rham_carrier_v1/layout.json"
SOURCE_LAYOUT = ROOT / "bridge/einstein_sector/generated/einstein_maxwell_product_linfinity_v1/row_layout.json"
DEPENDENCIES = {
    "five_current": ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_FIVE_STABILIZER_CURRENT_CONE_V1.json",
    "current_q2": ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_FIVE_CURRENT_DE_RHAM_Q2_V1.json",
    "current_carrier": ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_FIVE_CURRENT_DE_RHAM_CARRIER_V1.json",
    "cyclic_current": ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_CYCLIC_FIVE_CURRENT_CONE_V1.json",
    "source_layout": SOURCE_LAYOUT,
    "current_layout": CURRENT_LAYOUT,
}

GENERATORS = ["H", "P_x", "J_1", "J_2", "J_3"]
AXES = ["t", "x", "theta", "phi"]


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


def _fraction(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def _payload(deps: dict[str, dict[str, Any]]) -> dict[str, Any]:
    source_rows = sorted(
        (row for row in deps["source_layout"]["content"]["rows"] if row["degree"] == 0),
        key=lambda row: row["index"],
    )
    if len(source_rows) != 14:
        raise AssertionError("Einstein-Maxwell physical field layout drifted")
    source_by_local = {local: row for local, row in enumerate(source_rows)}

    current_rows = deps["current_layout"]["rows"]
    output_rows: dict[tuple[str, int], tuple[dict[str, Any], int]] = {}
    output_records = []
    for generator in GENERATORS:
        for axis in range(4):
            basis = [index for index in range(4) if index != axis]
            matches = [
                row for row in current_rows
                if row["chain"] == "primal"
                and row["form_degree"] == 3
                and row["generator"] == generator
                and row["basis_indices"] == basis
            ]
            if len(matches) != 1:
                raise AssertionError(f"missing P3 output row: {generator}:{axis}")
            sign = 1 if axis % 2 == 0 else -1
            output_rows[(generator, axis)] = matches[0], sign
            output_records.append({
                "generator": generator,
                "vector_density_component": AXES[axis],
                "component_axis": axis,
                "horizontal_three_form_basis": basis,
                "vector_density_to_form_sign": sign,
                "row": matches[0]["index"],
                "row_id": matches[0]["row_id"],
            })

    raw_terms: list[dict[str, Any]] = []
    counts: dict[str, int] = {}
    diagonal_counts: dict[str, int] = {}
    expanded_counts: dict[str, int] = {}
    vectors = stabilizer_vectors()
    if list(vectors) != GENERATORS:
        raise AssertionError("stabilizer ordering drifted")
    for generator in GENERATORS:
        current = polarized_noether_current(stabilizer_action(vectors[generator]))
        before = len(raw_terms)
        diagonal_count = 0
        expanded_count = 0
        for axis, rows in enumerate(current):
            output, sign = output_rows[(generator, axis)]
            for (left, left_word, right, right_word), profile in sorted(rows.items()):
                expanded_count += 1
                left_key = (left, left_word)
                right_key = (right, right_word)
                if left_key > right_key:
                    continue
                if left_key == right_key:
                    diagonal_count += 1
                encoded_profile = tuple(
                    (word, _fraction(sign * coefficient))
                    for word, coefficient in sorted(profile.items())
                    if coefficient
                )
                if not encoded_profile:
                    continue
                raw_terms.append({
                    "generator": generator,
                    "output": {"row": output["index"], "row_id": output["row_id"]},
                    "inputs": [
                        {
                            "local_field": left,
                            "row": source_by_local[left]["index"],
                            "row_id": source_by_local[left]["row_id"],
                            "word": list(left_word),
                        },
                        {
                            "local_field": right,
                            "row": source_by_local[right]["index"],
                            "row_id": source_by_local[right]["row_id"],
                            "word": list(right_word),
                        },
                    ],
                    "encoded_profile": encoded_profile,
                })
        counts[generator] = len(raw_terms) - before
        diagonal_counts[generator] = diagonal_count
        expanded_counts[generator] = expanded_count

    profile_values = sorted({term["encoded_profile"] for term in raw_terms})
    profile_index = {profile: index for index, profile in enumerate(profile_values)}
    coefficient_profiles = [
        {
            "index": index,
            "coefficient_jets": [
                {"word": list(word), "coefficient": coefficient}
                for word, coefficient in profile
            ],
        }
        for index, profile in enumerate(profile_values)
    ]
    terms = [
        {
            "generator": term["generator"],
            "output": term["output"],
            "inputs": term["inputs"],
            "coefficient_profile": profile_index[term["encoded_profile"]],
        }
        for term in raw_terms
    ]

    payload = {
        "schema": "pure-weyl-relative-full-five-current-pbw-payload-v1",
        "result_id": f"{RESULT_ID}_PAYLOAD",
        "background_id": "compact_magnetic_Plebanski_Hacyan_product",
        "coefficient_field": "Q",
        "operation": "q2(field,field)->K_P^1=Omega^3(M;g_stab^*)",
        "cochain_degree": 1,
        "source_carrier": deps["source_layout"]["carrier_id"],
        "target_carrier": deps["current_layout"]["result_id"],
        "field_order": [
            {"local_field": local, "row": row["index"], "row_id": row["row_id"], "bundle_id": row["bundle_id"]}
            for local, row in source_by_local.items()
        ],
        "output_rows": output_records,
        "generator_order": GENERATORS,
        "input_exchange_symmetry": "symmetric_expand_off_diagonal",
        "maximum_input_derivative_order": 4,
        "maximum_coefficient_jet_order": 1,
        "coefficient_profiles": coefficient_profiles,
        "coefficient_profile_count": len(coefficient_profiles),
        "canonical_term_counts": counts,
        "diagonal_term_counts": diagonal_counts,
        "expanded_term_counts": expanded_counts,
        "term_count": len(terms),
        "expanded_term_count": sum(expanded_counts.values()),
        "terms": terms,
        "claim_boundary": "This payload is the complete canonical symmetric coefficient-jet table for the five field-field Noether-current operations, converted from vector-density components to the declared horizontal P3 rows. It is not A, A1, A2, f2, a repaired relative q2 or a causal map.",
    }
    if payload["term_count"] != 30494 or len(coefficient_profiles) != 239 or counts != {
        "H": 4611, "P_x": 4611, "J_1": 4608, "J_2": 7296, "J_3": 9368,
    }:
        raise AssertionError(f"full five-current term census drifted: {counts}")
    if sum(2 * counts[name] - diagonal_counts[name] for name in GENERATORS) != payload["expanded_term_count"]:
        raise AssertionError("symmetric expansion census failed")
    return payload


def build() -> tuple[dict[str, Any], dict[str, Any]]:
    deps = {name: _load(path) for name, path in DEPENDENCIES.items()}
    if not deps["five_current"]["classification"]["all_five_off_shell_divergence_identities_exact"]:
        raise AssertionError("five-current identity unavailable")
    if not deps["current_q2"]["classification"]["current_interface_q1q2_identity_exact"]:
        raise AssertionError("five-current q2 identity unavailable")
    if not deps["cyclic_current"]["classification"]["arity_two_current_cone_cyclicity_exact"]:
        raise AssertionError("five-current cyclicity unavailable")
    payload = _payload(deps)
    rendered_payload = _render(payload)
    return {
        "schema": "pure-weyl-relative-full-five-current-pbw-export-v1",
        "result_id": RESULT_ID,
        "result_state": "COMPLETE_PORTABLE_FIVE_CURRENT_PBW_TABLE_EXPORTED_TOP_DESCENT_OPEN",
        "lifecycle_status": "COEFFICIENT_COMPUTED",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "scope": deps["current_q2"]["scope"],
        "dependencies": {name: _artifact(path, deps[name]) for name, path in DEPENDENCIES.items()},
        "payload": {
            "path": str(PAYLOAD.relative_to(ROOT)),
            "sha256": hashlib.sha256(rendered_payload.encode()).hexdigest(),
            "bytes": len(rendered_payload.encode()),
            "term_count": payload["term_count"],
            "expanded_term_count": payload["expanded_term_count"],
            "coefficient_profile_count": payload["coefficient_profile_count"],
            "generator_term_counts": payload["canonical_term_counts"],
            "maximum_input_derivative_order": payload["maximum_input_derivative_order"],
            "maximum_coefficient_jet_order": payload["maximum_coefficient_jet_order"],
        },
        "typing": {
            "domain": "Sym^2 of the 14 Einstein-Maxwell physical field rows",
            "codomain": "K_P^1=Omega^3(M;g_stab^*) with 20 declared primal rows",
            "vector_density_to_three_form": "J^mu maps to i_(partial_mu)(dt wedge dx wedge dtheta wedge dphi), with signs (+,-,+,-)",
            "ordered_input_table_is_symmetric": True,
            "coefficient_profiles_are_exact_rationals": True,
        },
        "classification": {
            "complete_full_five_current_pbw_export": True,
            "source_and_output_rows_typed": True,
            "coefficientwise_source_replay_exact": True,
            "support_local_chain_map_A_constructed": False,
            "top_descent_solved": False,
            "relative_q2_repaired": False,
            "causal_observable_particle_or_quantum_claim": False,
        },
        "next_gate": "DECLARE_THE_COMPLETE_INVARIANT_HOM_ORDER_ANSATZ_FOR_A1_A2_AND_SOLVE_TOP_DESCENT",
        "provenance": {
            "source_manifest": {
                str(path.relative_to(ROOT)): _sha(path)
                for path in (Path(__file__).resolve(), VERIFIER, TESTS, SCHEMA, PAYLOAD_SCHEMA, SOURCE_IMPLEMENTATION)
            },
            "verification_commands": [
                "PYTHONPATH=. python3 -m d_quotient_classical.relative.einstein_weyl_relative_full_five_current_pbw_export --check --guards",
                "PYTHONPATH=. python3 -m d_quotient_classical.relative.verify_einstein_weyl_relative_full_five_current_pbw_export",
                "python3 -m unittest d_quotient_classical.relative.tests.test_einstein_weyl_relative_full_five_current_pbw_export",
            ],
        },
        "claim_boundary": "This LOCAL-ALGEBRAIC export serializes every coefficient of the five support-local field-field current operations as a profile-deduplicated symmetric table in the exact source-field and primal-three-form row coordinates needed by the shifted relative lift. It replays an already certified operation rather than deriving a new current theorem. Its coefficient jets are complete through order one, so this artifact alone does not authorize differential postcomposition by A1 of positive order. It does not construct the current-to-Weyl chain map A, solve the top descent, repair relative q2, compare pairings or certify bounded, causal, observable, particle or quantum claims.",
    }, payload


def validate(certificate: dict[str, Any], payload: dict[str, Any]) -> None:
    schema = _load(SCHEMA)
    payload_schema = _load(PAYLOAD_SCHEMA)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator.check_schema(payload_schema)
    Draft202012Validator(schema).validate(certificate)
    Draft202012Validator(payload_schema).validate(payload)


def _render(value: object) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def _report(certificate: dict[str, Any]) -> str:
    counts = certificate["payload"]["generator_term_counts"]
    return f"""# Full five-current PBW export

The complete support-local current operation

\\[
q_2(u,v)=C_X(u,v)\\in\\Omega^3(M;\\mathfrak g_{{\\rm stab}}^*)
\\]

is now serialized in source-field and primal-three-form row coordinates.  The
payload contains `{certificate['payload']['term_count']}` exact canonical PBW
terms, split as `{counts}`.  Input derivative order is at most four and
coefficient jets are retained through order one.  Vector-density components
are converted to horizontal three-forms with signs `(+,-,+,-)`.  Symmetric
off-diagonal expansion recovers `{certificate['payload']['expanded_term_count']}`
ordered terms from `{certificate['payload']['coefficient_profile_count']}`
deduplicated coefficient profiles.

This closes only the portable-current input gate.  The invariant ansatz and
top descent for `A^1,A^2` remain open.
"""


def _guards(value: dict[str, Any], payload: dict[str, Any]) -> None:
    for key in (
        "support_local_chain_map_A_constructed", "top_descent_solved",
        "relative_q2_repaired", "causal_observable_particle_or_quantum_claim",
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
    args = parser.parse_args()
    certificate, payload = build()
    validate(certificate, payload)
    if args.write:
        PAYLOAD.parent.mkdir(parents=True, exist_ok=True)
        PAYLOAD.write_text(_render(payload))
        OUTPUT.write_text(_render(certificate))
        REPORT.write_text(_report(certificate))
    if args.check:
        if PAYLOAD.read_text() != _render(payload) or OUTPUT.read_text() != _render(certificate) or REPORT.read_text() != _report(certificate):
            raise AssertionError("full five-current PBW export drifted")
    if args.guards:
        _guards(certificate, payload)
    print(f"{RESULT_ID}: PASS")


if __name__ == "__main__":
    main()
