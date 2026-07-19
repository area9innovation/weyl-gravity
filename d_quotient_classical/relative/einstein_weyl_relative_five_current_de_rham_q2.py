#!/usr/bin/env python3
"""Certify the action-derived arity-two extension of the five-current carrier."""

from __future__ import annotations

import argparse
from collections import defaultdict
from copy import deepcopy
from fractions import Fraction
from functools import lru_cache
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from d_quotient_classical.relative.einstein_weyl_relative_five_stabilizer_current import (
    polarized_euler_source,
    stabilizer_action,
    stabilizer_vectors,
)
from d_quotient_classical.relative.einstein_weyl_relative_hessian_green_current_cone import (
    relative_operator_terms,
)


ROOT = Path(__file__).resolve().parents[2]
RESULT_ID = "EINSTEIN_WEYL_RELATIVE_FIVE_CURRENT_DE_RHAM_Q2_V1"
OUTPUT = ROOT / f"d_quotient_classical/certificates/{RESULT_ID}.json"
REPORT = ROOT / "d_quotient_classical/reports/einstein-weyl-relative-five-current-de-rham-q2.md"
SCHEMA = ROOT / "d_quotient_classical/schema/relative-five-current-de-rham-q2-v1.schema.json"
VERIFIER = ROOT / "d_quotient_classical/relative/verify_einstein_weyl_relative_five_current_de_rham_q2.py"
TESTS = ROOT / "d_quotient_classical/relative/tests/test_einstein_weyl_relative_five_current_de_rham_q2.py"
GENERATED = ROOT / "d_quotient_classical/generated/einstein_weyl_relative_five_current_de_rham_q2_v1/operations.json"

DEPENDENCIES = {
    "de_rham_carrier": ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_FIVE_CURRENT_DE_RHAM_CARRIER_V1.json",
    "five_current": ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_FIVE_STABILIZER_CURRENT_CONE_V1.json",
    "cyclic_current": ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_CYCLIC_FIVE_CURRENT_CONE_V1.json",
    "relative_hessian": ROOT / "d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_HESSIAN_GREEN_CURRENT_CONE_V1.json",
}

Profile = dict[tuple[int, ...], Fraction]
LinearTerm = tuple[int, int, tuple[int, ...], Profile]
OperationKey = tuple[int, tuple[int, ...], int, tuple[int, ...]]


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise TypeError(f"expected object: {path}")
    return value


def _artifact(path: Path, value: dict[str, Any]) -> dict[str, str]:
    return {
        "artifact_id": str(value.get("result_id", value.get("schema"))),
        "path": str(path.relative_to(ROOT)),
        "sha256": _sha(path),
    }


def _add(table: dict, key: tuple, value: Fraction) -> None:
    if value:
        table[key] += value


def _fraction(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def density_dual_action(action: list[LinearTerm]) -> list[LinearTerm]:
    """Return ``L_E=-L_F^sharp`` for the coordinate-density field/equation pairing."""

    raw: list[LinearTerm] = []
    for output, incoming, word, profile in action:
        if not word:
            raw.append((incoming, output, (), {jet: -value for jet, value in profile.items()}))
            continue
        if len(word) != 1:
            raise ValueError("the stabilizer action must be first order")
        axis = word[0]
        # - (a partial_axis)^sharp = a partial_axis + partial_axis(a).
        raw.append((incoming, output, word, dict(profile)))
        lower_jets: set[tuple[int, ...]] = set()
        for jet in profile:
            if axis in jet:
                mutable = list(jet)
                mutable.remove(axis)
                lower_jets.add(tuple(mutable))
        derivative_profile = {
            jet: profile[tuple(sorted((*jet, axis)))]
            for jet in lower_jets
            if profile.get(tuple(sorted((*jet, axis))), 0)
        }
        if derivative_profile:
            raw.append((incoming, output, (), derivative_profile))
    combined: dict[tuple[int, int, tuple[int, ...]], dict[tuple[int, ...], Fraction]] = defaultdict(
        lambda: defaultdict(Fraction)
    )
    for output, incoming, word, profile in raw:
        for jet, value in profile.items():
            _add(combined[(output, incoming, word)], jet, value)
    return [
        (output, incoming, word, {jet: value for jet, value in profile.items() if value})
        for (output, incoming, word), profile in sorted(combined.items())
        if any(profile.values())
    ]


def equation_field_moment_map(action: list[LinearTerm]) -> dict[OperationKey, Profile]:
    r"""Return ``M_X(e,v)=1/2(v L_E e-e L_F v)`` coefficientwise."""

    output: dict[OperationKey, dict[tuple[int, ...], Fraction]] = defaultdict(
        lambda: defaultdict(Fraction)
    )
    for target, incoming, word, profile in density_dual_action(action):
        for jet, value in profile.items():
            _add(output[(incoming, word, target, ())], jet, value / 2)
    for target, incoming, word, profile in action:
        for jet, value in profile.items():
            _add(output[(target, (), incoming, word)], jet, -value / 2)
    return {
        key: {jet: value for jet, value in profile.items() if value}
        for key, profile in output.items()
        if any(profile.values())
    }


def substitute_hessian_first_slot(moment: dict[OperationKey, Profile]) -> dict[OperationKey, Fraction]:
    """Substitute ``e=E(u)`` into the first moment-map input at the base point."""

    by_equation: dict[int, list[tuple]] = defaultdict(list)
    for term in relative_operator_terms():
        by_equation[term[0]].append(term)
    output: dict[OperationKey, Fraction] = defaultdict(Fraction)
    for (equation, equation_word, right, right_word), moment_profile in moment.items():
        moment_base = moment_profile.get((), 0)
        if not moment_base:
            continue
        for _, field, hessian_word, hessian_profile in by_equation[equation]:
            for mask in range(1 << len(equation_word)):
                coefficient_word = tuple(
                    sorted(
                        equation_word[index]
                        for index in range(len(equation_word))
                        if mask & (1 << index)
                    )
                )
                extra_field_word = tuple(
                    equation_word[index]
                    for index in range(len(equation_word))
                    if not mask & (1 << index)
                )
                field_word = tuple(sorted((*hessian_word, *extra_field_word)))
                _add(
                    output,
                    (field, field_word, right, right_word),
                    moment_base * hessian_profile.get(coefficient_word, 0),
                )
    return {key: value for key, value in output.items() if value}


def symmetrized_hessian_pullback(moment: dict[OperationKey, Profile]) -> dict[OperationKey, Fraction]:
    one_sided = substitute_hessian_first_slot(moment)
    output: dict[OperationKey, Fraction] = defaultdict(Fraction)
    for (left, left_word, right, right_word), value in one_sided.items():
        _add(output, (left, left_word, right, right_word), value)
        _add(output, (right, right_word, left, left_word), value)
    return {key: value for key, value in output.items() if value}


def _table_digest(table: dict[OperationKey, Any]) -> str:
    records = []
    for (left, left_word, right, right_word), value in sorted(table.items()):
        if isinstance(value, dict):
            encoded = [[list(jet), _fraction(coefficient)] for jet, coefficient in sorted(value.items())]
        else:
            encoded = _fraction(value)
        records.append([left, list(left_word), right, list(right_word), encoded])
    return hashlib.sha256(json.dumps(records, separators=(",", ":")).encode()).hexdigest()


def _linear_digest(terms: list[LinearTerm]) -> str:
    records = [
        [output, incoming, list(word), [[list(jet), _fraction(value)] for jet, value in sorted(profile.items())]]
        for output, incoming, word, profile in terms
    ]
    return hashlib.sha256(json.dumps(records, separators=(",", ":")).encode()).hexdigest()


def _serialize_moment(table: dict[OperationKey, Profile]) -> list[dict[str, Any]]:
    return [
        {
            "equation": {"field": left, "word": list(left_word)},
            "field": {"field": right, "word": list(right_word)},
            "coefficient_jets": [
                {"word": list(jet), "coefficient": _fraction(value)}
                for jet, value in sorted(profile.items())
            ],
        }
        for (left, left_word, right, right_word), profile in sorted(table.items())
    ]


@lru_cache(maxsize=1)
def exact_data() -> dict[str, Any]:
    records: dict[str, Any] = {}
    serialized: dict[str, Any] = {}
    for name, vector in stabilizer_vectors().items():
        action = stabilizer_action(vector)
        equation_action = density_dual_action(action)
        moment = equation_field_moment_map(action)
        pullback = symmetrized_hessian_pullback(moment)
        source = polarized_euler_source(action)
        defect = {
            key: pullback.get(key, 0) - source.get(key, 0)
            for key in set(pullback) | set(source)
            if pullback.get(key, 0) != source.get(key, 0)
        }
        if defect:
            raise AssertionError(f"{name} equation-field factorization defect: {next(iter(defect.items()))}")
        records[name] = {
            "field_action_terms": len(action),
            "field_action_sha256": _linear_digest(action),
            "equation_action_terms": len(equation_action),
            "equation_action_sha256": _linear_digest(equation_action),
            "equation_field_moment_terms": len(moment),
            "equation_field_moment_sha256": _table_digest(moment),
            "symmetrized_hessian_pullback_terms": len(pullback),
            "euler_source_terms": len(source),
            "hessian_pullback_defect_terms": 0,
        }
        serialized[name] = _serialize_moment(moment)
    return {"records": records, "moments": serialized}


def _generated(data: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema": "pure-weyl-relative-five-current-de-rham-q2-operations-v1",
        "result_id": f"{RESULT_ID}_OPERATIONS",
        "q2_sign_convention": "q2(e,v)=-M_X(e,v), so d_H C_X+q2(Eu,v)+q2(u,Ev)=0",
        "equation_field_moment_operations": data["moments"],
        "carrier_row_audit": data["carrier_row_audit"],
        "zero_on_added_rows": "all q2 operations with P_0,P_1,P_2,D_2,D_3,D_4 inputs are zero",
    }


def _carrier_row_audit(carrier: dict[str, Any]) -> dict[str, Any]:
    layout_path = ROOT / carrier["generated_layout"]["path"]
    if _sha(layout_path) != carrier["generated_layout"]["sha256"]:
        raise AssertionError("pinned de Rham carrier layout drifted")
    rows = _load(layout_path)["rows"]
    role_counts: dict[str, int] = defaultdict(int)
    records = []
    for row in rows:
        key = (row["chain"], row["form_degree"])
        role = {
            ("primal", 3): "field_field_current_output",
            ("primal", 4): "equation_field_moment_output",
            ("cotangent", 1): "field_field_current_cyclic_input",
            ("cotangent", 0): "equation_field_moment_cyclic_input",
        }.get(key, "zero_q2_row")
        role_counts[role] += 1
        records.append({"row": row["index"], "row_id": row["row_id"], "q2_role": role})
    expected = {
        "field_field_current_output": 20,
        "equation_field_moment_output": 5,
        "field_field_current_cyclic_input": 20,
        "equation_field_moment_cyclic_input": 5,
        "zero_q2_row": 110,
    }
    if len(rows) != 160 or dict(role_counts) != expected:
        raise AssertionError(f"carrier q2 row census changed: {dict(role_counts)}")
    return {"row_count": 160, "active_orbit_rows": 50, "zero_q2_rows": 110, "role_counts": expected, "records": records}


def build() -> dict[str, Any]:
    dependencies = {name: _load(path) for name, path in DEPENDENCIES.items()}
    if not dependencies["de_rham_carrier"]["classification"]["unary_cyclicity_exact"]:
        raise AssertionError("cyclic de Rham unary carrier is unavailable")
    if not dependencies["five_current"]["classification"]["all_five_off_shell_divergence_identities_exact"]:
        raise AssertionError("five-current theorem is unavailable")
    if not dependencies["cyclic_current"]["classification"]["arity_two_current_cone_cyclicity_exact"]:
        raise AssertionError("cyclic current orbit is unavailable")
    data = dict(exact_data())
    data["carrier_row_audit"] = _carrier_row_audit(dependencies["de_rham_carrier"])
    records = deepcopy(data["records"])
    for name, record in records.items():
        current = dependencies["cyclic_current"]["cyclic_completion"]["generator_records"][name]
        record["field_field_current_monomials"] = current["factorized_current_monomials"]
        record["field_field_current_sha256"] = current["current_sha256"]
    generated = _generated(data)
    generated_sha = hashlib.sha256((json.dumps(generated, indent=2, sort_keys=True) + "\n").encode()).hexdigest()
    return {
        "schema": "pure-weyl-relative-five-current-de-rham-q2-v1",
        "result_id": RESULT_ID,
        "result_state": "ACTION_DERIVED_CURRENT_INTERFACE_Q2_EXACT_FULL_RELATIVE_MORPHISM_OPEN",
        "lifecycle_status": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "scope": {
            "theory": "Einstein-Maxwell source relative to Weyl-Maxwell target",
            "background": "compact magnetic Plebanski-Hacyan product",
            "boundaries": "local coefficient jets on M=R x S1 x S2; no harmonic or Green reduction",
            "charge_sector": "H,P_x,J_1,J_2,J_3",
            "carrier": "14 relative physical fields, their 14 Hessian equations, and the 160-row five-current de Rham/cotangent carrier",
            "degree": "physical field-equation interface plus carrier degrees -2 through 3",
            "parity": "canonical cyclic odd pairing",
            "ell": "not harmonic-reduced", "m": "not harmonic-reduced", "k": "not harmonic-reduced", "omega": "not harmonic-reduced",
        },
        "dependencies": {name: _artifact(path, dependencies[name]) for name, path in DEPENDENCIES.items()},
        "operations": {
            "field_field_to_primal_three_form": "q2(u,v)=C_X(u,v)",
            "equation_field_to_primal_four_form": "q2(e,v)=-M_X(e,v), M_X(e,v)=1/2(v L_E e-e L_F v)",
            "equation_action": "L_E=-L_F^sharp for the coordinate-density field/equation pairing",
            "cyclic_completion": "adjoin every rotation of the two lowered tensors against D_1 and D_0; all other operation orbits vanish",
            "base_identity": "d_H C_X(u,v)=M_X(Eu,v)+M_X(Ev,u)",
            "all_row_argument": "q1 and q2 are cyclic and the odd pairing is nondegenerate, so every cyclic rotation of the base identity vanishes; rows outside the two operation orbits vanish termwise",
            "carrier_row_audit": data["carrier_row_audit"],
            "generator_records": records,
        },
        "generated_operations": {
            "path": str(GENERATED.relative_to(ROOT)),
            "sha256": generated_sha,
            "portable_tables": "all equation-field moment-map coefficients; field-field currents are reconstructed by the pinned five-current producer",
        },
        "classification": {
            "density_dual_equation_action_exact": True,
            "action_derived_equation_field_operation_exact": True,
            "all_five_hessian_pullback_factorizations_exact": True,
            "current_interface_q1q2_identity_exact": True,
            "current_interface_cyclic_completion_exact": True,
            "all_160_carrier_rows_audited": True,
            "added_potential_and_reducibility_q2_rows_zero": True,
            "finite_order_support_local": True,
            "full_relative_238_row_arity_two_morphism_constructed": False,
            "direct_f2_obstruction_repaired": False,
            "causal_green_homotopy_certified": False,
            "arity_three_authorized": False,
            "quantum_claim": False,
        },
        "next_gate": "ATTACH_THE_EXACT_CURRENT_INTERFACE_Q2_TO_THE_78_ROW_RELATIVE_MAPPING_COFIBER_AND_SOLVE_OR_CERTIFY_THE_REMAINING_CROSS_INCIDENCE",
        "provenance": {
            "source_manifest": {
                str(path.relative_to(ROOT)): _sha(path)
                for path in (Path(__file__).resolve(), VERIFIER, TESTS, SCHEMA)
            },
            "verification_commands": [
                "PYTHONPATH=. python3 -m d_quotient_classical.relative.einstein_weyl_relative_five_current_de_rham_q2 --check --guards",
                "PYTHONPATH=. python3 -m d_quotient_classical.relative.verify_einstein_weyl_relative_five_current_de_rham_q2",
                "python3 -m unittest d_quotient_classical.relative.tests.test_einstein_weyl_relative_five_current_de_rham_q2",
                "npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true -s d_quotient_classical/schema/relative-five-current-de-rham-q2-v1.schema.json -d d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_FIVE_CURRENT_DE_RHAM_Q2_V1.json",
            ],
        },
        "claim_boundary": (
            "This LOCAL-ALGEBRAIC theorem certifies the complete cyclic q2 operation orbit on the 14+14 physical Hessian interface and all 160 rows of the selected five-current de Rham carrier. The equation-field operation is derived from the stabilizer action and the density-dual equation action, and its Hessian pullback reproduces the complete Euler source for all five generators with zero PBW defect. It does not yet attach that interface to every ghost, identity and antifield row of the 78-row relative mapping cofiber, repair the pre-existing direct f2 obstruction, construct a causal Green homotopy, authorize arity three, or make a quantum claim."
        ),
    }


def validate(value: dict[str, Any]) -> None:
    schema = _load(SCHEMA)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)


def _render(value: object) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def _report() -> str:
    return r"""# Five-current de Rham arity-two interface

The action-derived current operation now extends across the equation row of
the selected support-local de Rham carrier.  If (L_F) is any of the five
stabilizer actions, its equation-density action is

\[
L_E=-L_F^\sharp,
\]

and the required equation-field operation is the moment-map expression

\[
M_X(e,v)=\frac12\bigl(vL_Ee-eL_Fv\bigr).
\]

Exact PBW substitution of the relative Hessian gives, for every stabilizer,

\[
d_H C_X(u,v)=M_X(Eu,v)+M_X(Ev,u).
\]

Thus the sign convention (q_2(e,v)=-M_X(e,v)) makes the field-field
arity-two identity vanish.  The field-field current tensor and the
equation-field moment tensor are completed by all of their cyclic rotations
against the de Rham cotangent rows.  Since the unary differential and both
lowered tensors are cyclic and the pairing is nondegenerate, the remaining
row identities are the cyclic rotations of the displayed identity; the 110
new potential/reducibility rows outside these two orbits have zero (q_2).

This closes the 188-row physical-current interface only.  The existing
78-row relative mapping cofiber has not yet been coupled to it through all
ghost, identity and antifield rows, so the full 238-row relative morphism and
the old direct-(f_2) obstruction remain open.
"""


def _guards(value: dict[str, Any]) -> None:
    for key in (
        "full_relative_238_row_arity_two_morphism_constructed",
        "direct_f2_obstruction_repaired",
        "causal_green_homotopy_certified",
        "arity_three_authorized",
        "quantum_claim",
    ):
        mutant = deepcopy(value)
        mutant["classification"][key] = True
        try:
            validate(mutant)
        except Exception:
            continue
        raise AssertionError(f"mutation guard accepted classification.{key}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()
    value = build()
    data = dict(exact_data())
    data["carrier_row_audit"] = _carrier_row_audit(_load(DEPENDENCIES["de_rham_carrier"]))
    generated = _generated(data)
    validate(value)
    if args.write:
        GENERATED.parent.mkdir(parents=True, exist_ok=True)
        GENERATED.write_text(_render(generated))
        OUTPUT.write_text(_render(value))
        REPORT.write_text(_report())
    if args.check:
        if GENERATED.read_text() != _render(generated) or OUTPUT.read_text() != _render(value) or REPORT.read_text() != _report():
            raise AssertionError("five-current de Rham q2 outputs drifted")
    if args.guards:
        _guards(value)
    print(f"{RESULT_ID}: PASS")


if __name__ == "__main__":
    main()
