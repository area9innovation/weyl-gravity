from __future__ import annotations

import json

from closed_universe_observers import generate_berger_global_detector_rods as result
from closed_universe_observers import verify_berger_global_detector_rods as verifier


def test_global_rods_replay_exactly() -> None:
    payload = result.build()
    assert payload["exact_checks"]["all_pass"] is True
    assert payload["exact_checks"]["wave_residuals"] == ["0"] * 6
    assert payload["exact_checks"]["linear_spatial_eigenvalue"] == "29/18"
    assert payload["exact_checks"]["event_relational_jacobians"] == [[
        ["1", "0", "0", "0"], ["0", "1", "0", "0"], ["0", "0", "1", "0"], ["0", "0", "0", "1"]
    ]] * 2


def test_detector_indexing_corrects_carrier_arity() -> None:
    payload = result.build()
    correction = payload["allocation_correction"]
    assert correction["new_detector_indexed_rod_count"] == 6
    assert correction["corrected_proposed_total_rows"] == 84
    assert correction["mutation_rejected"] is True
    assert len(correction["new_degree_zero_rows"]) == 10
    assert len(correction["new_degree_one_rows"]) == 10


def test_compact_nonlinear_gate_remains_fail_closed() -> None:
    payload = result.build()
    assert "T_rod^{ab}/2" in payload["global_source_export"]["retained_metric_source"]
    assert payload["flags"]["GLOBAL_COMPACT_ROD_CONFIGURATION_EXPORTED"] is True
    assert payload["flags"]["GLOBAL_COMPACT_ROD_Q0_FORMULA_EXPORTED"] is True
    assert payload["flags"]["COMPACT_TAUB_PROJECTION_COMPUTED"] is False
    assert payload["flags"]["PERTURBATIVE_BACKREACTED_ROD_BRANCH_CERTIFIED"] is False
    assert payload["nonlinear_import_contract"]["status"] == "OPEN"


def test_persisted_certificate_and_independent_verifier() -> None:
    assert json.loads(result.CERTIFICATE.read_text()) == result.build()
    assert verifier.main() == 0
