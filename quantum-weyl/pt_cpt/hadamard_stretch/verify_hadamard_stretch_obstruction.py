#!/usr/bin/env python3
"""Independent semantic verifier for the Phase-2 Hadamard obstruction."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CERT = Path(__file__).parent / "certificates" / "PHASE2_BRST_HADAMARD_STRETCH_OBSTRUCTION_V1.json"

EXPECTED_SOURCES = {
    "gauge_fixed_unary_pairing": "6e3baf6ecfab2c2854ccfbfb5c69122fe0bbe621ddcf8ab2a5651e3decf113e0",
    "causal_green_homotopy": "e92642b3225ab87b6058987f73f9ade3909646f2d0d3b95cc45cc9c5712b9c3b",
    "graded_state_contract_and_real_structure": "99768cf1e444ef3525f19621702ee64a68aea83f83349a1c5d6223d9c959ca35",
    "hadamard_lift_preflight": "59d52928eb3e0063a4b0464b4592d4bd7d5d43e06860ee96999b6094a12b9723",
    "zero_frequency_readiness": "204b207b31b5df145e036f44762310af211a8353c721be4cb34aa7ac85e9cbfc",
    "stationary_generator_import_readiness": "cf3499a76ea0367db9d886f6b91c3de1ee392c4c1a376eb60d3060b8e37ca7de",
    "phase2_cpt_disposition": "516415604952c1f835ea0d46095d8fa82b07fe36de3dc33d641e34f0b938223c",
}


def validate(payload: dict) -> None:
    assert payload["result_state"] == "COMPLETE_CAUSAL_BV_SELECTED_ZERO_FREQUENCY_CARRIER_EXACTLY_NOT_IDENTIFIED"
    selected = payload["selected_complex"]
    assert selected["selection_count"] == 1
    assert selected["row_count"] == 54
    assert selected["complete_causal_status"] == "CERTIFIED"
    assert "not substituted" in selected["reduced_26_role"]

    obstruction = payload["first_exact_obstruction"]
    assert obstruction["type"] == "MISSING_COMPLETE_STATIONARY_CAUCHY_CARRIER"
    assert obstruction["missing_artifacts"] == ["A104", "q_Cauchy_104", "G_Cauchy_104", "real_structure_104"]
    assert obstruction["unknown_coordinates_in_current_A104"] == 288
    witness = obstruction["exact_witness"]
    assert witness["completion_A_endpoint_zero_eigenspace_dimension"] - witness["completion_B_endpoint_zero_eigenspace_dimension"] == witness["difference"] == 24

    flags = payload["claim_flags"]
    assert flags["COMPLETE_54_ROW_CAUSAL_BV_COMPLEX_IMPORTED"] is True
    for forbidden in [
        "P2A_FULL_BV_C_OPERATOR_CERTIFIED",
        "BERGER_RETAINED_26_ZERO_FREQUENCY_SPECTRAL_LEDGER",
        "BERGER_54_ROW_BRST_HADAMARD",
        "BERGER_PHYSICAL_OBSERVABLE_POSITIVITY",
        "LORENTZIAN_QME_RESTORED",
        "QUANTUM_CLAIM",
    ]:
        assert flags[forbidden] is False
    assert payload["dependency_tags"] == ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL", "REDUCED-MODE"]
    assert all(payload["exact_checks"].values())

    for role, expected in EXPECTED_SOURCES.items():
        ref = payload["source_refs"][role]
        assert ref["sha256"] == expected
        actual = hashlib.sha256((ROOT / ref["path"]).read_bytes()).hexdigest()
        assert actual == expected


def main() -> None:
    validate(json.loads(CERT.read_text()))
    print("PASS: independent full-BV Hadamard obstruction replay")


if __name__ == "__main__":
    main()
