#!/usr/bin/env python3
"""Certify the associative coefficient-jet PBW backend and Nariai inputs."""

from __future__ import annotations

import argparse
from functools import lru_cache
import hashlib
from itertools import combinations
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp

from covariant_completion.curved_operator.adjoint_tractor_bgg_curved_pbw import (
    FibrePBW,
)
from d_quotient_classical.causal_transfer.coefficient_jet_pbw import (
    CoefficientJetPBW,
    JetLinearizedOperator,
    jet_add,
    jet_scale,
    parallel_zero_variation,
)
from d_quotient_classical.causal_transfer.first_variation_pbw import (
    FirstVariationPBW,
)
from d_quotient_classical.causal_transfer.nariai_automorphism_prolongation_first_two_rows import (
    fixture as nariai_fixture,
)


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
OUTPUT = ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_COEFFICIENT_JET_PBW_REQUIREMENTS_V1.json"
REPORT = ROOT / "d_quotient_classical/reports/nariai-transverse-coefficient-jet-pbw-requirements.md"
SCHEMA = ROOT / "d_quotient_classical/schema/nariai-transverse-coefficient-jet-pbw-requirements-v1.schema.json"
VERIFIER = HERE / "verify_nariai_transverse_coefficient_jet_pbw_requirements.py"
TESTS = HERE / "tests/test_nariai_transverse_coefficient_jet_pbw_requirements.py"
BACKEND_TESTS = HERE / "tests/test_coefficient_jet_pbw.py"
BACKEND = HERE / "coefficient_jet_pbw.py"
OLD_GATE = ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_LINEARIZED_PBW_ASSOCIATIVITY_GATE_V1.json"
JET_DATA = ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_JET_AWARE_MIDDLE_SCHUR_VARIATION_V1.json"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _table_digest(table: dict[tuple[int, ...], sp.Matrix]) -> str:
    text = "\n".join(
        f"{word}:{sp.srepr(sp.ImmutableSparseMatrix(matrix))}"
        for word, matrix in sorted(table.items())
    )
    return hashlib.sha256(text.encode()).hexdigest()


def _count(table: dict[tuple[int, ...], sp.Matrix]) -> int:
    return sum(value != 0 for matrix in table.values() for value in matrix)


class _FlatLine:
    @staticmethod
    def covector_commutator(_left: int, _right: int) -> sp.Matrix:
        return sp.zeros(1)


def _scalar_table(values: dict[tuple[int, ...], sp.Expr]):
    return {word: sp.Matrix([[value]]) for word, value in values.items()}


def _flat_backend() -> CoefficientJetPBW:
    zero = tuple(tuple(sp.zeros(1) for _ in range(4)) for _ in range(4))
    base = FibrePBW(zero, _FlatLine(), "coefficient-jet-proof-fixture")
    return CoefficientJetPBW(
        FirstVariationPBW(
            base,
            zero,
            zero,
            lambda _word: sp.Integer(0),
            "coefficient-jet-proof-fixture",
        )
    )


def _exponential_jet(coefficient: sp.Expr):
    def provider(word: tuple[int, ...]):
        if any(axis != 0 for axis in word):
            return {}
        return _scalar_table({(): coefficient})

    return provider


def _direct_compose(outer, inner, x: sp.Symbol):
    result: dict[int, sp.Expr] = {}
    for outer_order, outer_coefficient in outer.items():
        for inner_order, inner_coefficient in inner.items():
            for coefficient_order in range(outer_order + 1):
                order = outer_order - coefficient_order + inner_order
                value = (
                    sp.binomial(outer_order, coefficient_order)
                    * outer_coefficient
                    * sp.diff(inner_coefficient, x, coefficient_order)
                )
                result[order] = sp.expand(result.get(order, 0) + value)
    return {order: value for order, value in result.items() if value != 0}


def _direct_delta_jet_table(operator, jet_order, x, epsilon):
    result = {}
    for order, coefficient in operator.items():
        value = sp.diff(
            sp.diff(coefficient, epsilon).subs(epsilon, 0), x, jet_order
        ).subs(x, 0)
        if value != 0:
            result[(0,) * order] = sp.Matrix([[sp.expand(value)]])
    return result


def _positive_subwords(words: set[tuple[int, ...]], maximum: int):
    result: set[tuple[int, ...]] = set()
    for word in words:
        positions = tuple(range(len(word)))
        for size in range(1, min(maximum, len(word)) + 1):
            for selected in combinations(positions, size):
                result.add(tuple(word[index] for index in selected))
    return sorted(result, key=lambda word: (len(word), word))


@lru_cache(maxsize=1)
def exact_data() -> dict[str, Any]:
    algebra = _flat_backend()
    a = parallel_zero_variation(_scalar_table({(0, 0): 1, (): 2}), "A")
    b = JetLinearizedOperator(
        _scalar_table({(0,): 3, (): 5}), _exponential_jet(7), "B"
    )
    c = JetLinearizedOperator(
        _scalar_table({(0,): 11, (): 13}), _exponential_jet(17), "C"
    )
    left = algebra.compose(algebra.compose(a, b, "AB"), c, "(AB)C")
    right = algebra.compose(a, algebra.compose(b, c, "BC"), "A(BC)")
    associator = jet_add(left, jet_scale(right, -1), name="associator")

    x, epsilon = sp.symbols("x epsilon")
    direct_a = {2: sp.Integer(1), 0: sp.Integer(2)}
    direct_b = {1: sp.Integer(3), 0: 5 + epsilon * 7 * sp.exp(x)}
    direct_c = {1: sp.Integer(11), 0: 13 + epsilon * 17 * sp.exp(x)}
    direct_left = _direct_compose(_direct_compose(direct_a, direct_b, x), direct_c, x)
    direct_right = _direct_compose(direct_a, _direct_compose(direct_b, direct_c, x), x)
    direct_defect = {
        order: sp.expand(direct_left.get(order, 0) - direct_right.get(order, 0))
        for order in set(direct_left) | set(direct_right)
    }
    direct_defect = {order: value for order, value in direct_defect.items() if value != 0}

    jet_rows = []
    for order in range(4):
        backend = left.delta((0,) * order)
        direct = _direct_delta_jet_table(direct_left, order, x, epsilon)
        if backend != direct:
            raise AssertionError(f"coefficient-jet/direct mismatch at order {order}")
        defect = associator.delta((0,) * order)
        if defect:
            raise AssertionError(f"coefficient-jet associator at order {order}")
        jet_rows.append(
            {
                "jet_word": [0] * order,
                "nonzero_coefficients": _count(backend),
                "sha256": _table_digest(backend),
            }
        )
    if associator.base or direct_defect:
        raise AssertionError("base or direct associator did not vanish")

    nariai = nariai_fixture()
    middle_words = set(nariai["middle"]["yang_mills_middle"])
    l0_required = [[axis] for axis in range(4)]
    l1_required = [list(word) for word in _positive_subwords(middle_words, 2)]
    if len(l1_required) != 14:
        raise AssertionError(f"Nariai L1 coefficient-jet count drifted: {len(l1_required)}")
    jet_payload = json.loads(JET_DATA.read_text())
    variations = jet_payload["exact_data"]["operator_variations"]

    return {
        "backend_theorem": {
            "base_coefficients": "parallel normal-form coefficients",
            "varied_coefficients": "lazy ordered covariant coefficient jets",
            "composition": "covariant Leibniz distribution followed by base PBW normal ordering plus varied-curvature PBW terms",
            "point_value_only_missing_jets_raise": "MissingCoefficientJet",
            "direct_polynomial_fixture_associator_zero": True,
            "backend_associator_zero": True,
            "direct_and_backend_coefficient_jets_agree": True,
            "checked_output_coefficient_jet_orders": jet_rows,
        },
        "nariai_replay_requirements": {
            "typed_triple": "M_parent o L1_corrected o (K p0)",
            "available_curvature_jet_order": 3,
            "maximum_curvature_jet_order_for_typed_triple": 3,
            "curvature_jet_input_sufficient": True,
            "corrected_L0_positive_coefficient_jet_words_required_for_first_square": l0_required,
            "corrected_L1_positive_coefficient_jet_words_required_for_associativity": l1_required,
            "each_requested_jet_is": "the complete varied normal-form coefficient table, including coefficient slots whose value happens to vanish at the normalization point",
            "available_corrected_L0_data": {
                "jet_words": [[]],
                "nonzero_point_coefficients": variations["corrected_L0"]["nonzero_coefficients"],
            },
            "available_corrected_L1_data": {
                "jet_words": [[]],
                "nonzero_point_coefficients": variations["corrected_L1"]["nonzero_coefficients"],
            },
            "positive_order_corrected_splitting_jets_available": False,
            "point_values_determine_positive_jets": False,
            "normalized_nonuniqueness_witness": {
                "functions": ["a", "a+x"],
                "same_value_at_x0": "a",
                "first_derivative_difference_at_x0": "1",
            },
            "authoritative_derivation_required": "full perturbed covariant HPL/BGG splitting or an equivalent natural operator formula; scalar interpolation of the point matrices is forbidden",
        },
        "disposition": {
            "associative_coefficient_jet_backend_available": True,
            "old_point_value_backend_superseded": True,
            "nariai_associative_replay_runnable": False,
            "rank_310_transverse_SDR_decided": False,
            "next_gate": "derive corrected L0/L1 covariant coefficient jets from the perturbed BGG/HPL construction, then replay first square, parent identity, shifted chain, and compressed Schur",
        },
    }


def build() -> dict[str, Any]:
    data = exact_data()
    dependencies = {}
    for key, path, result_id in (
        ("old_associativity_gate", OLD_GATE, "NARIAI_TRANSVERSE_LINEARIZED_PBW_ASSOCIATIVITY_GATE_V1"),
        ("point_and_curvature_jet_data", JET_DATA, "NARIAI_TRANSVERSE_JET_AWARE_MIDDLE_SCHUR_VARIATION_V1"),
    ):
        payload = json.loads(path.read_text())
        if payload["result_id"] != result_id:
            raise AssertionError(f"dependency drifted: {key}")
        dependencies[key] = {
            "path": str(path.relative_to(ROOT)),
            "result_id": result_id,
            "sha256": _sha(path),
        }
    sources = (Path(__file__).resolve(), VERIFIER, TESTS, BACKEND_TESTS, SCHEMA, BACKEND)
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "schema": "nariai-transverse-coefficient-jet-pbw-requirements-v1",
        "schema_version": "1.0.0",
        "result_id": "NARIAI_TRANSVERSE_COEFFICIENT_JET_PBW_REQUIREMENTS_V1",
        "result_state": "ASSOCIATIVE_COEFFICIENT_JET_BACKEND_EXACT_NARIAI_SPLITTING_JETS_MISSING",
        "lifecycle_state": "CERTIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "dependency_refs": dependencies,
        "exact_data": data,
        "exact_checks": {
            "direct_fixture_associative": data["backend_theorem"]["direct_polynomial_fixture_associator_zero"],
            "backend_fixture_associative": data["backend_theorem"]["backend_associator_zero"],
            "direct_backend_match": data["backend_theorem"]["direct_and_backend_coefficient_jets_agree"],
            "nariai_curvature_jets_sufficient": data["nariai_replay_requirements"]["curvature_jet_input_sufficient"],
            "nariai_splitting_jets_missing": not data["nariai_replay_requirements"]["positive_order_corrected_splitting_jets_available"],
            "rank_310_not_overclaimed": not data["disposition"]["rank_310_transverse_SDR_decided"],
        },
        "flags": {
            "COEFFICIENT_JET_PBW_BACKEND_ASSOCIATIVE_ON_DIRECT_FIXTURE": True,
            "NARIAI_TRANSVERSE_CURVATURE_JETS_SUFFICIENT_FOR_TYPED_TRIPLE": True,
            "NARIAI_TRANSVERSE_CORRECTED_SPLITTING_COEFFICIENT_JETS": False,
            "NARIAI_TRANSVERSE_ASSOCIATIVE_PBW_REPLAY": False,
            "TRANSVERSE_COMPLETE_RANK_310_SDR_FIRST_VARIATION": False,
            "TRANSVERSE_CAUSAL_TRANSFER": False,
        },
        "next_gate": "NARIAI_TRANSVERSE_CORRECTED_BGG_SPLITTING_COEFFICIENT_JETS",
        "claim_boundary": "This certificate supplies and directly checks an associative first-variation PBW composition for nonparallel operator coefficients, and proves that the existing Nariai curvature jets reach the order needed by the M-L1-K triple. It also proves that the repository exports only point values, not the required positive-order covariant coefficient jets, of the corrected L0/L1 splittings. Point values cannot determine those jets. Therefore no transverse first-square, shifted-chain, Schur, rank-310 SDR, or causal theorem is promoted. The missing jets must be derived from a full perturbed BGG/HPL or equivalent natural operator construction, not fitted.",
        "source_manifest": {
            str(path.relative_to(ROOT)): _sha(path) for path in sources
        },
        "verification_commands": [
            "python3 -m d_quotient_classical.causal_transfer.nariai_transverse_coefficient_jet_pbw_requirements --check",
            "python3 d_quotient_classical/causal_transfer/verify_nariai_transverse_coefficient_jet_pbw_requirements.py",
            "python3 -m unittest d_quotient_classical.causal_transfer.tests.test_coefficient_jet_pbw d_quotient_classical.causal_transfer.tests.test_nariai_transverse_coefficient_jet_pbw_requirements",
            "npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true -s d_quotient_classical/schema/nariai-transverse-coefficient-jet-pbw-requirements-v1.schema.json -d d_quotient_classical/certificates/NARIAI_TRANSVERSE_COEFFICIENT_JET_PBW_REQUIREMENTS_V1.json",
        ],
    }


def report(payload: dict[str, Any]) -> str:
    data = payload["exact_data"]
    requirements = data["nariai_replay_requirements"]
    return f"""# Transverse coefficient-jet PBW requirements

The replacement PBW backend retains ordered covariant jets of every varied
normal-form coefficient.  On an independently evaluated scalar differential
operator fixture, both parenthesizations agree through coefficient-jet order
three, and every output coefficient agrees with direct symbolic
differentiation.  Point-only inputs now fail closed rather than silently
setting positive-order coefficient jets to zero.

For the Nariai triple `M_parent o L1_corrected o (K p0)`, the existing exact
curvature tower through order
`{requirements['available_curvature_jet_order']}` is sufficient.  The actual
remaining input is smaller and more precise: four positive-order coefficient
jet tables for `L0_corrected`, and fourteen for `L1_corrected`.  The current
export contains only their values at the normalization point
(`{requirements['available_corrected_L0_data']['nonzero_point_coefficients']}`
and `{requirements['available_corrected_L1_data']['nonzero_point_coefficients']}`
nonzero coefficients respectively).

Those values do not determine the missing jets: `a` and `a+x` agree at the
point but have normalized first-derivative difference one.  Consequently the
associative Nariai replay remains open.  Its next input must be derived from a
full perturbed covariant HPL/BGG splitting or an equivalent natural operator
formula; interpolating the point matrices is not admissible.
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = build()
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(payload)
    if args.write:
        OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
        REPORT.write_text(report(payload))
    if args.check and json.loads(OUTPUT.read_text()) != payload:
        raise AssertionError("coefficient-jet requirements artifact is stale")
    print("NARIAI_TRANSVERSE_COEFFICIENT_JET_PBW_REQUIREMENTS_V1: PASS")


if __name__ == "__main__":
    main()
