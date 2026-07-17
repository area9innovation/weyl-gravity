from __future__ import annotations

from copy import deepcopy
import json

from jsonschema import Draft202012Validator, ValidationError
import sympy as sp

from closed_universe_observers.generate_berger_84_row_rod_gravity_unary import (
    CERTIFICATE,
    SCHEMA,
    _action_hessian_specializations,
    _operator_order_audit,
    build,
    rod_gravity_laurent_inverse_audit,
)
from closed_universe_observers.verify_berger_84_row_rod_gravity_unary import (
    _independent_gamma,
    _independent_hessian,
    _independent_laurent_inverse,
    _semantic_boundary,
    verify,
)


def test_clock_dressed_gamma_has_two_rank_three_event_blocks() -> None:
    value = build()
    _independent_gamma(value)
    blocks = value["rod_gauge_blocks"]["event_blocks"]
    expected = [["0", "0", "1"], ["1", "0", "0"], ["0", "1", "0"]]
    assert len(blocks) == 2
    assert all(block["matrix_base_ghost_order_e1_e2_e3"] == expected for block in blocks)
    assert all(block["rank"] == 3 and block["determinant"] == "1" for block in blocks)
    assert value["rod_gauge_blocks"]["raw_temporal_nonzero_count"] == 6


def test_gamma_cotangent_block_is_negative_transpose() -> None:
    gauge = build()["rod_gauge_blocks"]
    assert gauge["gamma_entry_count"] == len(gauge["gamma_entries"])
    assert len(gauge["gamma_sharp_q1_entries"]) == gauge["gamma_entry_count"]
    for forward, adjoint in zip(gauge["gamma_entries"], gauge["gamma_sharp_q1_entries"]):
        assert adjoint["output_index"] == forward["input_index"] + 49
        assert adjoint["input_index"] == forward["output_index"] + 10
        assert sp.simplify(sp.sympify(adjoint["coefficient"]) + sp.sympify(forward["coefficient"])) == 0


def test_action_hessian_specializations_are_exact_and_nontrivial() -> None:
    audit = _action_hessian_specializations()
    assert audit["coefficient_field"] == "Q"
    assert audit["mixed_partial_defect_count"] == 0
    assert audit["metric_hessian_symmetry_defect_count"] == 0
    assert audit["nonzero_mixed_fixture_count"] > 0
    _independent_hessian(build())


def test_coupled_cross_blocks_are_strictly_subprincipal() -> None:
    audit = _operator_order_audit()
    assert audit["principal_part_defect_count"] == 0
    assert all(row["order"] < row["comparison_order"] for row in audit["cross_block_orders"])


def test_coupled_laurent_inverse_requires_schur_feedback() -> None:
    audit = rod_gravity_laurent_inverse_audit()
    assert audit["left_inverse_defect_count_through_r"] == 0
    assert audit["right_inverse_defect_count_through_r"] == 0
    mutant = rod_gravity_laurent_inverse_audit(delete_schur_feedback=True)
    assert mutant["left_inverse_defect_count_through_r"] + mutant["right_inverse_defect_count_through_r"] > 0
    assert _independent_laurent_inverse() == (0, 0)
    assert sum(_independent_laurent_inverse(delete_feedback=True)) > 0


def test_mutations_are_computed_and_scope_is_fail_closed() -> None:
    value = build()
    _semantic_boundary(value)
    assert all(row["detected"] and row["defect_count"] > 0 for row in value["mutation_results"])
    assert value["coefficient_scope"]["q1_certified_bidegrees_r_kappa"] == [[0, 0], [1, 0], [0, 1]]
    assert not value["flags"]["84_ROW_Q1_CERTIFIED"]
    mutant = deepcopy(value)
    mutant["flags"]["MIXED_EPSILON_R2_KAPPA_UNARY_CERTIFIED"] = True
    try:
        _semantic_boundary(mutant)
    except ValueError:
        pass
    else:
        raise AssertionError("mixed-jet overclaim mutation was accepted")


def test_strict_schema_and_persisted_certificate() -> None:
    value = build()
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    assert json.loads(CERTIFICATE.read_text()) == value
    mutant = deepcopy(value)
    mutant["unexpected"] = True
    try:
        Draft202012Validator(schema).validate(mutant)
    except ValidationError:
        pass
    else:
        raise AssertionError("strict schema accepted an unexpected field")


def test_independent_verifier() -> None:
    assert verify() == build()
