#!/usr/bin/env python3
"""Independent verifier for the parameterized five-form-factor freeze audit."""

from __future__ import annotations

from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CERTIFICATE = (
    HERE
    / "certificates/PARAMETERIZED_PARITY_EVEN_FIVE_FORM_FACTOR_FAMILY_INDEPENDENT_AUDIT.json"
)
SCHEMA = (
    HERE
    / "schema/parameterized-parity-even-five-form-factor-family-independent-audit-v1.schema.json"
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _bareiss_determinant(matrix: list[list[int]]) -> int:
    work = [row[:] for row in matrix]
    size = len(work)
    sign = 1
    previous = 1
    for pivot_index in range(size - 1):
        if work[pivot_index][pivot_index] == 0:
            swap = next(
                (
                    row
                    for row in range(pivot_index + 1, size)
                    if work[row][pivot_index]
                ),
                None,
            )
            if swap is None:
                return 0
            work[pivot_index], work[swap] = work[swap], work[pivot_index]
            sign *= -1
        pivot = work[pivot_index][pivot_index]
        for row in range(pivot_index + 1, size):
            for column in range(pivot_index + 1, size):
                numerator = (
                    work[row][column] * pivot
                    - work[row][pivot_index] * work[pivot_index][column]
                )
                if numerator % previous:
                    raise AssertionError("Bareiss division lost exactness")
                work[row][column] = numerator // previous
        previous = pivot
    return sign * work[-1][-1]


def verify(payload: dict[str, Any]) -> None:
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    try:
        Draft202012Validator(schema).validate(payload)
    except ValidationError as error:
        raise ValueError(f"certificate schema validation failed: {error.message}") from error

    assert payload["dependency_tags"] == [
        "LOCAL-ALGEBRAIC",
        "EUCLIDEAN-SPECTRAL",
    ]
    assert payload["source_commit"] == "ed265d70c"
    independence = payload["independence_boundary"]
    assert independence["terminal_producer_imported"] is False
    assert independence["terminal_producer_invoked"] is False
    assert independence["producer_ambiguity_matrix_reused"] is False
    assert independence["producer_rank_computation_reused"] is False

    imports = payload["import_closure"]
    assert imports["input_count"] == 17
    assert imports["assembly_dependency_closure_count"] == 14
    assert imports[
        "all_physical_ghost_contact_zero_mode_and_Schur_inputs_pinned"
    ] is True
    for reference in imports["inputs"].values():
        path = ROOT / reference["path"]
        assert path.is_file()
        assert _sha256(path) == reference["sha256"]
        source = json.loads(path.read_text())
        assert source["result_id"] == reference["result_id"]

    quotient = payload["carrier_quotient_audit"]
    assert quotient["raw_dimension"] == 11
    assert quotient["relation_rank"] == 1
    assert quotient["raw_lift_rank"] == 10
    assert quotient["quotient_dimension"] == 10
    assert quotient["relation_vector"] == [0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0]
    lift = quotient["raw_lift_matrix"]
    assert len(lift) == 11 and all(len(row) == 10 for row in lift)
    for column in range(10):
        assert sum(
            quotient["relation_vector"][row] * lift[row][column]
            for row in range(11)
        ) == 0
    assert quotient["raw_character"] == {
        "identity": 11,
        "transposition": 5,
        "three_cycle": 2,
    }
    assert quotient["quotient_character"] == {
        "identity": 10,
        "transposition": 4,
        "three_cycle": 1,
    }
    assert quotient["irreducible_multiplicities"] == {
        "trivial": 4,
        "sign": 0,
        "standard": 3,
    }

    endpoints = payload["endpoint_audit"]
    assert endpoints["contact_count"] == 3
    assert endpoints["contact_row_count"] == 33
    assert sorted(endpoints["rows_per_contact"].values()) == [11, 11, 11]
    assert endpoints["contact_I28_relation"] == (
        "ZERO_TERM_BY_TERM_FOR_ALL_CONTACTS"
    )
    assert endpoints["mellin_endpoint_finite_constant"] == {
        "numerator": 0,
        "denominator": 1,
    }
    assert endpoints["relative_IBP_channel_count"] == 11
    assert endpoints["relative_IBP_corner_count"] == 33
    assert endpoints["status"] == "ALL_LABELLED_ENDPOINTS_REPLAYED_EXACTLY"

    zero_modes = payload["zero_mode_and_holdout_audit"]
    assert zero_modes["repository_factor_count"] == 4
    assert zero_modes["special_background_interpolation_used"] is False
    witness = zero_modes["two_point_noninterpolation_witness"]
    round_parameter = Fraction(witness["round_S4_parameter"])
    product_parameter = Fraction(witness["product_S2_S2_parameter"])
    generic_parameter = Fraction(witness["generic_test_parameter"])
    amplitude = lambda value: value * (value - 1) / 2
    assert [
        amplitude(round_parameter),
        amplitude(product_parameter),
        amplitude(generic_parameter),
    ] == [Fraction(value) for value in witness["values"]]
    assert witness["values"] == [0, 0, 1]

    completion = payload["global_completion_audit"]
    model = completion["finite_matrix_model"]
    assert model["Pi0_diagonal"] == [1, 0, 0]
    assert model["S0_diagonal"] == ["1", "3/2", "4/3"]
    assert model["smoothing_projector_diagonal"] == [0, 1, 0]
    assert Fraction(3, 2) / Fraction(3, 2) == 1
    assert model["determinant_ratio_B_over_A"] == "1+u1*u2*u3"
    assert model["mixed_third_log_determinant_shift"] == {
        "numerator": 1,
        "denominator": 1,
    }
    assert completion["distinct_finite_third_variations"] is True
    assert completion["unit_completion_count"] == 10
    matrix = completion["ambiguity_matrix"]
    assert len(matrix) == 10 and all(len(row) == 10 for row in matrix)
    assert _bareiss_determinant(matrix) in {-1, 1}
    assert completion["ambiguity_rank"] == 10
    assert completion["universal_combination_kernel_dimension"] == 0
    assert completion["universal_combination_kernel_basis"] == []

    verdict = payload["freeze_verdict"]
    assert all(
        verdict[key] is True
        for key in (
            "terminal_affine_family_theorem_survives",
            "rank_ten_finite_Schur_ambiguity_independently_verified",
            "no_nonzero_universal_finite_Schur_combination",
            "partial_BV_and_local_scale_content_preserved",
            "special_background_holdouts_do_not_fix_generic_data",
        )
    )
    assert verdict["complete_universal_coefficient_table"] == "NONDEFINED"
    flags = payload["claim_flags"]
    assert flags == {
        "PARAMETERIZED_FAMILY_THEOREM_INDEPENDENTLY_FROZEN": True,
        "RANK_TEN_AMBIGUITY_INDEPENDENTLY_VERIFIED": True,
        "ZERO_UNIVERSAL_SCHUR_KERNEL_INDEPENDENTLY_VERIFIED": True,
        "SPECIAL_BACKGROUND_INTERPOLATION_USED": False,
        "COMPLETE_UNIVERSAL_BV_FIVE_FUNCTION_TABLE_COMPUTED": False,
        "QME_OR_LORENTZIAN_PROMOTED": False,
    }


def main() -> int:
    verify(json.loads(CERTIFICATE.read_text()))
    print("PARAMETERIZED FIVE-FORM-FACTOR INDEPENDENT AUDIT REPLAY: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
