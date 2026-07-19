from __future__ import annotations

import json

from closed_universe_observers import generate_berger_global_rod_q1_solvability as result
from closed_universe_observers import verify_berger_global_rod_q1_solvability as verifier


def test_complete_global_rod_source_sector_is_exact() -> None:
    payload = result.build()
    assert payload["exact_blocks"]["zero"]["operator_rank"] == 70
    assert payload["exact_blocks"]["zero"]["augmented_ranks"] == [70, 70, 70]
    assert payload["exact_blocks"]["positive"]["operator_rank"] == 68
    assert payload["exact_blocks"]["positive"]["augmented_ranks"] == [68, 68, 68]
    assert all(block["primitive_residual_nonzero_count"] == 0 for block in payload["exact_blocks"].values())
    assert all(block["full_stress_mutation_residual_nonzero_count"] > 0 for block in payload["exact_blocks"].values())
    assert "T_rod^{ab}/2" in payload["second_order_equation"]["source_convention"]


def test_result_is_second_order_and_fail_closed_beyond_it() -> None:
    payload = result.build()
    flags = payload["flags"]
    assert flags["GLOBAL_ROD_SOURCE_COKERNEL_PROJECTION_ZERO"] is True
    assert flags["GLOBAL_ROD_BACKREACTION_SOLVABLE_THROUGH_ORDER_EPSILON_R_SQUARED"] is True
    assert flags["ACTION_EULER_HALF_STRESS_NORMALIZATION_CERTIFIED"] is True
    assert flags["FULL_NONLINEAR_BACKREACTED_ROD_BRANCH_CERTIFIED"] is False
    assert flags["84_ROW_INTERACTING_COMPLEX_CERTIFIED"] is False
    assert flags["84_ROW_CAUSAL_GREEN_HOMOTOPY_CERTIFIED"] is False


def test_persisted_certificate_and_independent_replay() -> None:
    assert json.loads(result.CERTIFICATE.read_text()) == result.build()
    assert verifier.main() == 0
