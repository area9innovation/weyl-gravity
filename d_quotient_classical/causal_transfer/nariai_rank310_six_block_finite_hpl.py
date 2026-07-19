#!/usr/bin/env python3
"""Exact six-block finite HPL theorem for the rank-310 Nariai carrier."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

import d_quotient_classical.causal_transfer.nariai_parent_detour_mapping_cone_repair as repair
import d_quotient_classical.causal_transfer.nariai_transverse_rank310_dual_sdr as dual


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "d_quotient_classical/causal_transfer"
OUTPUT = ROOT / "d_quotient_classical/certificates/NARIAI_RANK310_SIX_BLOCK_FINITE_HPL_V1.json"
REPORT = ROOT / "d_quotient_classical/reports/nariai-rank310-six-block-finite-hpl.md"
SCHEMA = ROOT / "d_quotient_classical/schema/nariai-rank310-six-block-finite-hpl-v1.schema.json"
VERIFIER = HERE / "verify_nariai_rank310_six_block_finite_hpl.py"
TESTS = HERE / "tests/test_nariai_rank310_six_block_finite_hpl.py"
CORE = HERE / "nariai_parent_detour_mapping_cone_repair.py"

DEPENDENCIES = {
    "base_rank310_SDR": ROOT / "d_quotient_classical/certificates/NARIAI_PARENT_DETOUR_MAPPING_CONE_REPAIR_V1.json",
    "four_block_HPL": ROOT / "d_quotient_classical/certificates/NARIAI_RANK310_FINITE_HPL_INCIDENCE_THEOREM_V1.json",
    "finite_KS_incidence_obstruction": ROOT / "d_quotient_classical/certificates/NARIAI_KS_FOUR_BLOCK_INCIDENCE_OBSTRUCTION_V1.json",
}

O = repair.O
Matrix = repair.Matrix


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise ValueError(f"dependency is not an object: {path}")
    return value


def _ref(path: Path, value: dict[str, Any]) -> dict[str, str]:
    return {"artifact_id": str(value["result_id"]), "path": str(path.relative_to(ROOT)), "sha256": _sha(path)}


def _word(*names: str) -> O:
    return O._from_dict({tuple(names): 1})


FINITE_ADJOINT = {
    **dual.ADJOINT,
    "gD": "gsharpD",
    "gsharpD": "gD",
    "kD": "ksharpD",
    "ksharpD": "kD",
    "MD": "MD",
    "BD": "BD",
    "L0D": "L0sharpD",
    "L0sharpD": "L0D",
}


def _finite_replace_once(value: O) -> tuple[O, bool]:
    rules = {
        ("gD", "J"): O.zero(),
        ("J", "gD"): _word("L0D", "p0").scale(-1),
        ("p0", "L0D"): O.zero(),
        ("Jsharp", "gsharpD"): O.zero(),
        ("gsharpD", "Jsharp"): _word("p0sharp", "L0sharpD").scale(-1),
        ("L0sharpD", "p0sharp"): O.zero(),
        # This is precisely the finite Maurer--Cartan/gauge identity
        # (B+BD)(k+kD)=0 after subtracting Bk=0.
        ("B", "kD"): (_word("BD", "k") + _word("BD", "kD")).scale(-1),
        ("ksharpD", "B"): (_word("ksharp", "BD") + _word("ksharpD", "BD")).scale(-1),
    }
    for word, coefficient in value.terms:
        for old, replacement in rules.items():
            for index in range(len(word) - len(old) + 1):
                if word[index : index + len(old)] != old:
                    continue
                rest = value + O._from_dict({word: -coefficient})
                prefix = O._from_dict({word[:index]: coefficient})
                suffix = O._from_dict({word[index + len(old) :]: 1})
                return rest + prefix * replacement * suffix, True
    return value, False


def reduce_finite(value: O) -> O:
    for _ in range(800):
        changed, did_change = repair._replace_once(value)
        if did_change:
            value = changed
            continue
        changed, did_change = _finite_replace_once(value)
        if did_change:
            value = changed
            continue
        return value
    raise AssertionError(f"finite six-block reduction did not terminate: {value.display()}")


def matrix_defects(value: Matrix) -> list[dict[str, Any]]:
    output = []
    for row, entries in enumerate(value):
        for column, entry in enumerate(entries):
            reduced = reduce_finite(entry)
            if reduced != O.zero():
                output.append({"row": row, "column": column, "value": reduced.display()})
    return output


def operator_adjoint(value: O) -> O:
    return O._from_dict(
        {tuple(FINITE_ADJOINT[name] for name in reversed(word)): coefficient for word, coefficient in value.terms}
    )


def matrix_adjoint(value: Matrix) -> Matrix:
    return [[operator_adjoint(value[column][row]) for column in range(len(value))] for row in range(len(value[0]))]


def exact_fixture() -> dict[str, Any]:
    base = dual.abstract_fixture()["base"]
    add, multiply, scale = repair._add, repair._multiply, repair._scale
    delta = repair._zero(10, 10)
    delta[1][0] = O.atom("gD")
    delta[3][0] = O.atom("kD")
    delta[6][2] = O.atom("MD", repair.C)
    delta[7][3] = O.atom("BD")
    delta[9][5] = O.atom("gsharpD")
    delta[9][7] = O.atom("ksharpD")

    identity = repair._identity(10)
    metric_identity = repair._identity(4)
    q_new = add(base["q"], delta)
    h_delta = multiply(base["homotopy"], delta)
    delta_h = multiply(delta, base["homotopy"])
    inclusion = multiply(add(identity, scale(h_delta, -1)), base["inclusion"])
    projection = multiply(base["projection"], add(identity, scale(delta_h, -1)))
    homotopy = add(base["homotopy"], scale(multiply(h_delta, base["homotopy"]), -1))
    metric_q = multiply(multiply(projection, q_new), inclusion)

    degree_sign = repair._degree_sign(repair.BLOCK_DEGREES)
    checks = {
        "H_Delta_squared": multiply(h_delta, h_delta),
        "Delta_H_squared": multiply(delta_h, delta_h),
        "Q_new_squared": multiply(q_new, q_new),
        "projection_inclusion": add(multiply(projection, inclusion), scale(metric_identity, -1)),
        "inclusion_chain": add(multiply(q_new, inclusion), scale(multiply(inclusion, metric_q), -1)),
        "projection_chain": add(multiply(projection, q_new), scale(multiply(metric_q, projection), -1)),
        "retract": add(
            add(identity, scale(multiply(inclusion, projection), -1)),
            scale(add(multiply(q_new, homotopy), multiply(homotopy, q_new)), -1),
        ),
        "homotopy_squared": multiply(homotopy, homotopy),
        "homotopy_inclusion": multiply(homotopy, inclusion),
        "projection_homotopy": multiply(projection, homotopy),
        "Q_new_odd_cyclic": add(
            multiply(matrix_adjoint(q_new), base["pairing"]),
            multiply(multiply(degree_sign, base["pairing"]), q_new),
        ),
        "homotopy_odd_cyclic": add(
            multiply(matrix_adjoint(homotopy), base["pairing"]),
            scale(multiply(multiply(degree_sign, base["pairing"]), homotopy), -1),
        ),
        "metric_pairing_pullback": add(
            multiply(multiply(matrix_adjoint(inclusion), base["pairing"]), inclusion),
            scale(base["metric_pairing"], -1),
        ),
        "projection_is_inclusion_adjoint": add(
            scale(multiply(multiply(base["metric_pairing"], matrix_adjoint(inclusion)), base["pairing"]), -1),
            scale(projection, -1),
        ),
    }
    defects = {name: matrix_defects(matrix) for name, matrix in checks.items()}
    failed = {name: value for name, value in defects.items() if value}
    if failed:
        raise AssertionError(f"six-block finite HPL identity failed: {failed}")

    correction = matrix_defects(multiply(multiply(multiply(multiply(base["projection"], delta), base["homotopy"]), delta), base["inclusion"]))
    expected_correction = [
        {"row": 1, "column": 0, "value": "-1 kD L0D"},
        {"row": 3, "column": 2, "value": "-1 L0sharpD ksharpD"},
    ]
    if correction != expected_correction:
        raise AssertionError(f"six-block metric cross correction drifted: {correction}")
    metric_entries = matrix_defects(metric_q)
    expected_metric = [
        {"row": 1, "column": 0, "value": "K + kD L0 + kD L0D"},
        {"row": 2, "column": 1, "value": "B + BD"},
        {"row": 3, "column": 2, "value": "Ksharp + L0sharp ksharpD + L0sharpD ksharpD"},
    ]
    if metric_entries != expected_metric:
        raise AssertionError(f"transferred metric differential drifted: {metric_entries}")

    return {
        "coefficient_algebra": "noncommutative exact finite-difference operator algebra",
        "block_count": 10,
        "delta_nonzero_blocks": matrix_defects(delta),
        "H_delta_nonzero_blocks": matrix_defects(h_delta),
        "delta_H_nonzero_blocks": matrix_defects(delta_h),
        "identity_defect_counts": {name: 0 for name in checks},
        "inverse_series_length": 2,
        "metric_quadratic_cross_corrections": correction,
        "transferred_metric_differential": metric_entries,
        "finite_relations": [
            "gD J=0",
            "J gD=-L0D p0",
            "p0 L0D=0",
            "Jsharp gsharpD=0",
            "gsharpD Jsharp=-p0sharp L0sharpD",
            "L0sharpD p0sharp=0",
            "(B+BD)(k+kD)=0",
            "(ksharp+ksharpD)(B+BD)=0",
        ],
    }


def build() -> dict[str, Any]:
    records = {name: _load(path) for name, path in DEPENDENCIES.items()}
    if not records["base_rank310_SDR"]["flags"]["SUPPORT_LOCAL_AUTOMORPHISM_SDR"]:
        raise ValueError("base rank-310 SDR drifted")
    if not records["four_block_HPL"]["flags"]["FINITE_SUPPORT_LOCAL_HPL_DENOMINATOR"]:
        raise ValueError("four-block HPL theorem drifted")
    if not records["finite_KS_incidence_obstruction"]["flags"]["CANONICAL_KS_SIX_BLOCK_PREFLIGHT_REQUIRED"]:
        raise ValueError("six-block activation gate drifted")
    fixture = exact_fixture()
    sources = {str(path.relative_to(ROOT)): _sha(path) for path in (Path(__file__).resolve(), VERIFIER, TESTS, SCHEMA, CORE)}
    return {
        "schema": "pure-weyl-nariai-rank310-six-block-finite-hpl-v1",
        "result_id": "NARIAI_RANK310_SIX_BLOCK_FINITE_HPL_V1",
        "result_state": "SIX_BLOCK_FINITE_HPL_TERMINATES_WITH_EXACT_METRIC_CROSS_CORRECTIONS",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "dependency_refs": {name: _ref(DEPENDENCIES[name], records[name]) for name in DEPENDENCIES},
        "theorem": {
            "statement": "For an exact cyclic rank-310 differential whose finite difference from the unit-Nariai split presentation occupies g,k,M,B and the two cyclic-dual blocks, both HPL resolvents terminate after one correction. The resulting cyclic support-local SDR is exact and the retained metric differential contains two forced quadratic gauge/splitting cross terms.",
            "finite_formulas": "I1=(1-H Delta)I0, p1=p0(1-Delta H), H1=H0-H0 Delta H0, qmet1=p1 Q1 I1",
            "scope": "exact finite operator algebra once the six geometric difference blocks obey the displayed complement and gauge identities",
        },
        "exact_fixture": fixture,
        "analytic_consequence": {
            "nonlocal_HPL_inverse_required": False,
            "convergence_condition_required": False,
            "quadratic_metric_cross_terms_may_be_dropped": False,
            "remaining_input": "bind all six finite difference operators to the exact Kantowski-Sachs common-slab geometry and verify the metric biwave endpoint hypotheses",
        },
        "exact_checks": {
            "six_block_Q_squared": True,
            "both_HPL_resolvents_terminate": True,
            "all_chain_retract_and_side_identities": True,
            "cyclicity_and_pairing_pullback": True,
            "two_metric_quadratic_cross_terms_retained": True,
        },
        "flags": {
            "NARIAI_RANK310_SIX_BLOCK_FINITE_HPL_V1": True,
            "SIX_BLOCK_FINITE_SUPPORT_LOCAL_HPL": True,
            "KS_SIX_BLOCK_GEOMETRIC_COEFFICIENT_BINDING": False,
            "TRANSVERSE_KS_COMMON_SLAB_CAUSAL_TRANSFER": False,
            "TRANSVERSE_KS_GLOBAL_SMOOTH_CYLINDER_FAMILY": False,
            "HADAMARD_STATE": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "NARIAI_KS_SIX_BLOCK_GEOMETRIC_BINDING_AND_COMMON_SLAB_ENDPOINT",
        "provenance": {
            "source_manifest": sources,
            "verification_commands": [
                "PYTHONPATH=. python3 d_quotient_classical/causal_transfer/nariai_rank310_six_block_finite_hpl.py --check --guards",
                "PYTHONPATH=. python3 d_quotient_classical/causal_transfer/verify_nariai_rank310_six_block_finite_hpl.py",
                "python3 -m unittest d_quotient_classical.causal_transfer.tests.test_nariai_rank310_six_block_finite_hpl",
                "npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true -s d_quotient_classical/schema/nariai-rank310-six-block-finite-hpl-v1.schema.json -d d_quotient_classical/certificates/NARIAI_RANK310_SIX_BLOCK_FINITE_HPL_V1.json"
            ]
        },
        "claim_boundary": "This exact theorem closes the algebraic HPL problem for the six-block finite incidence and proves that the quadratic metric cross terms cannot be discarded. It does not yet bind those abstract differences to the coefficient-complete Kantowski-Sachs geometry, verify the endpoint Volterra hypotheses there, promote a common-slab or whole-cylinder causal theorem, or establish Hadamard or quantum claims."
    }


def validate(value: dict[str, Any]) -> None:
    if not all(value["exact_checks"].values()):
        raise ValueError("an exact six-block check dropped")
    for flag in (
        "KS_SIX_BLOCK_GEOMETRIC_COEFFICIENT_BINDING",
        "TRANSVERSE_KS_COMMON_SLAB_CAUSAL_TRANSFER",
        "TRANSVERSE_KS_GLOBAL_SMOOTH_CYLINDER_FAMILY",
        "HADAMARD_STATE",
        "QUANTUM_CLAIM",
    ):
        if value["flags"][flag] is not False:
            raise ValueError("claim boundary crossed")
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)


def _render(value: object) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def _report() -> str:
    return r"""# Six-block finite HPL theorem for the rank-310 carrier

The exact finite Kantowski--Sachs presentation must allow the six differences

\[
 \Delta g,\quad \Delta k,\quad \Delta M,\quad \Delta B,
 \quad \Delta g^\sharp,\quad \Delta k^\sharp.
\]

In the split rank-310 block incidence one still has

\[
 (H\Delta)^2=(\Delta H)^2=0.
\]

The only additional Maurer--Cartan relation is the finite gauge identity

\[
 (B+\Delta B)(k+\Delta k)=0
\]

and its formal dual.  Therefore

\[
 I_1=(1-H\Delta)I_0,
 \quad p_1=p_0(1-\Delta H),
 \quad H_1=H_0-H_0\Delta H_0
\]

give an exact finite-order support-local cyclic SDR.  Every chain, retract,
side-condition, cyclicity and pairing defect vanishes in the exact
noncommutative operator algebra.

Unlike the four-block formal calculation, the retained metric differential
has two forced quadratic terms:

\[
 (p\Delta H\Delta I)_{10}=-\Delta k\,\Delta L_0,
 \qquad
 (p\Delta H\Delta I)_{32}=-\Delta L_0^\sharp\Delta k^\sharp.
\]

The remaining task is geometric, not homological: bind the six differences
and these two cross terms to the exact common-slab Kantowski--Sachs operators,
then verify the metric endpoint's typed biwave hypotheses.
"""


def _guards(value: dict[str, Any]) -> None:
    for flag in (
        "KS_SIX_BLOCK_GEOMETRIC_COEFFICIENT_BINDING",
        "TRANSVERSE_KS_COMMON_SLAB_CAUSAL_TRANSFER",
        "TRANSVERSE_KS_GLOBAL_SMOOTH_CYLINDER_FAMILY",
        "HADAMARD_STATE",
        "QUANTUM_CLAIM",
    ):
        mutant = deepcopy(value)
        mutant["flags"][flag] = True
        try:
            validate(mutant)
        except Exception:
            continue
        raise AssertionError(f"mutation guard accepted: {flag}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()
    value = build()
    validate(value)
    if args.write:
        OUTPUT.write_text(_render(value))
        REPORT.write_text(_report())
    if args.check:
        if OUTPUT.read_text() != _render(value) or REPORT.read_text() != _report():
            raise AssertionError("six-block HPL outputs drifted")
    if args.guards:
        _guards(value)
    print("NARIAI_RANK310_SIX_BLOCK_FINITE_HPL_V1: PASS")


if __name__ == "__main__":
    main()
