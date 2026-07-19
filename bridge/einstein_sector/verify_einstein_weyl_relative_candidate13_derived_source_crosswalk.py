"""Independent verifier for the candidate-13 relative derived-source crosswalk."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/EINSTEIN_WEYL_RELATIVE_CANDIDATE13_DERIVED_SOURCE_CROSSWALK_V1.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify() -> None:
    payload = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    schema_path = ROOT / payload["schema_path"]
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(payload)
    assert payload["schema_sha256"] == sha(schema_path)
    records = {}
    for name, item in payload["provenance"]["inputs"].items():
        path = ROOT / item["path"]
        assert item["sha256"] == sha(path)
        records[name] = json.loads(path.read_text(encoding="utf-8"))
    triangle = records["linear_triangle"]
    assert triangle["claim_status"] == "CERTIFIED_OFF_SHELL_LINEAR_TRIANGLE"
    assert triangle["acceptance_flags"]["SUPPORT_LOCAL_MAPPING_COFIBER"]
    assert records["branch_dictionary"]["classification"]["same_background_only"]
    receiver = records["current_cofiber_receiver"]
    assert receiver["classification"]["charge_projected_arity_two_descent_exact"]
    assert not receiver["classification"]["full_relative_arity_two_morphism_constructed"]
    assert not records["full_domain_f2_obstruction"]["classification"]["frozen_unary_full_domain_f2_exists"]
    assert records["candidate13_cone"]["classification"]["complete_candidate13_bounded_tangent_cone_formula_certified"]
    assert records["bounded_zero_block"]["classification"]["bounded_zero_frequency_necessity_and_sufficiency_certified"]
    assert records["pressure_obstruction"]["classification"]["candidate13_bounded_pressure_functional_nonzero"]
    assert payload["quadratic_receiver"]["zero_block_map"]["components"] == ["mu_H", "mu_Px", "mu_J1", "mu_J2", "mu_J3"]
    assert payload["quadratic_receiver"]["relative_resonance_map"]["components"] == "R_13,1,...,R_13,18"
    assert "R_c=" in payload["quadratic_receiver"]["bounded_pressure_map"]["components"]
    assert payload["derived_source_pullback"]["BOUNDED_OR_FINITE_QUASIPERIODIC"]["status"] == "CERTIFIED"
    assert payload["derived_source_pullback"]["CAUSAL_RETARDED"]["status"] == "NO_CERTIFIED_MAP"
    flags = payload["classification"]
    assert flags["candidate13_five_plus_pressure_plus_eighteen_quadratic_receiver_typed"]
    assert flags["bounded_derived_source_pullback_certified"]
    assert flags["bounded_derived_source_known_necessary_ledger_certified"]
    assert flags["full_domain_f2_obstruction_preserved"]
    assert not flags["support_local_BV_derived_subcomplex_constructed"]
    assert not flags["full_relative_arity_two_morphism_constructed"]
    assert not flags["arity_three_authorized"]
    print("EINSTEIN_WEYL_RELATIVE_CANDIDATE13_DERIVED_SOURCE_CROSSWALK_V1 verifier: PASS")


if __name__ == "__main__":
    verify()
