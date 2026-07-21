from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CERT = ROOT / "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_REPAIRED_Q70_LOW_J_STABILIZER_HEALTH_V1.json"
PAYLOAD = ROOT / "d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_REPAIRED_Q70_LOW_J_STABILIZER_HEALTH_PAYLOAD_V1.json"


def _load() -> tuple[dict, dict]:
    return json.loads(CERT.read_text()), json.loads(PAYLOAD.read_text())


def test_low_j_artifact_and_exceptional_census_are_current() -> None:
    certificate, payload = _load()
    assert certificate["payload_ref"]["sha256"] == hashlib.sha256(PAYLOAD.read_bytes()).hexdigest()
    assert payload["representation_census"]["exceptional_two_j"] == [0, 2]
    assert payload["terminal_verdict"]["stabilizer_dimension_accounted"] == 4
    disposition = payload["representation_census"]["absent_tensor_harmonic_disposition"]
    assert (disposition["j0_field_rows_retained"], disposition["j1_field_rows_retained"]) == (10, 30)


def test_zero_frequency_pairing_and_charge_distinctions_are_fail_closed() -> None:
    _, payload = _load()
    for key in ("j0", "j1"):
        zero = payload["exceptional_blocks"][key]["zero_frequency_full_complex"]
        assert zero["cohomology_dimensions_Hminus1_H0_H1_H2"] == [1, 1, 1, 1]
        assert zero["pairing_rank"] == 4
        assert zero["pairing_radical_dimension"] == 0
        assert zero["ordinary_inertia"] == "NOT_APPLICABLE_TO_GRADED_PAIRING"
    charges = payload["charge_actions"]
    assert charges["repaired_diagonal_U1"]["physical_cohomology"] == "ZERO"
    assert charges["repaired_diagonal_U1"]["local_Gauss_charge"] == "ZERO"
    assert charges["nonzero_characteristic_modes"]["unrestricted_vs_fixed_charge"] == "IDENTICAL"


def test_physical_instabilities_have_exact_pairing_and_jordan_dispositions() -> None:
    _, payload = _load()
    j0 = payload["exceptional_blocks"]["j0"]["spectrum"]
    assert j0["unstable_sector"]["classification"] == "GENUINE_REAL_EXPONENTIAL_PHYSICAL_DIRECTION"
    assert j0["unstable_sector"]["energy"]["inertia_positive_negative_zero"] == [3, 3, 0]
    j1 = payload["exceptional_blocks"]["j1"]["spectrum"]
    assert [entry["two_copy_inertia_positive_negative_zero"] for entry in j1["unstable_sectors"]] == [[4, 4, 0], [8, 12, 0]]
    for spectrum in (j0, j1):
        assert all(audit["pairing_radical_dimension"] == 0 for audit in spectrum["nonzero_factor_audits"])
        assert all(audit["Jordan_status"] == "SEMISIMPLE_NO_POLYNOMIAL_TIME_PARTNER" for audit in spectrum["nonzero_factor_audits"])


def test_forbidden_low_j_mutations_are_recorded() -> None:
    _, payload = _load()
    assert payload["mutations"]["isolated_k0_at_j1"] == "REJECTED_BY_NONZERO_E1_E2_LADDER_BOUNDARY"
    assert payload["mutations"]["generic_rank_substitution"] == "REJECTED_BY_EXACT_NULLITY_ONE_AT_TWO_J_0_AND_2"
    assert payload["mutations"]["charged_R_rel_called_spatial_gauge"] == "REJECTED_BY_IMPORTED_CHARGE_CURRENT_AND_SEPARATE_CARRIER"
