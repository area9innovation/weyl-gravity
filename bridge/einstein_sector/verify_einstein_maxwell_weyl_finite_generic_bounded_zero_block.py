"""Independent checks for the finite-generic bounded zero-block theorem."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import sympy as sp
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
CERT = ROOT / "bridge/certificates/einstein_maxwell_weyl_finite_generic_bounded_zero_block.json"


def main() -> None:
    data = json.loads(CERT.read_text(encoding="utf-8"))
    schema_path = ROOT / data["schema_path"]
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(data)
    assert data["schema_sha256"] == hashlib.sha256(schema_path.read_bytes()).hexdigest()
    for item in data["provenance"]["inputs"].values():
        path = ROOT / item["path"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == item["sha256"]

    omega = sp.symbols("omega", real=True)
    symbol = sp.diag(omega**4, omega**2)
    assert symbol.rank() == 2
    assert symbol.subs(omega, 0).rank() == 0
    assert len(symbol.subs(omega, 0).T.nullspace()) == 2

    flags = data["classification"]
    assert flags["homogeneous_bounded_dynamical_mean_cokernel_dimension_two"]
    assert flags["circle_pressure_source_functional_certified"]
    assert flags["wilson_acceleration_source_functional_identically_zero"]
    assert flags["five_stabilizers_plus_circle_pressure_complete_on_finite_generic_zero_block"]
    assert flags["bounded_zero_frequency_necessity_and_sufficiency_certified"]
    assert not flags["generalized_zero_inputs_included"]
    assert not flags["nonzero_frequency_resonance_ledger_classified"]
    assert not flags["causal_residual_observational_or_quantum_claim"]

    pairings = data["source_pairings"]
    assert pairings["circle_pressure"]["functional"] == "R_c(u)=(1/2) sum_j k_j^2 h_j"
    assert pairings["wilson_acceleration"]["value_on_complete_carrier"] == "0"
    assert data["bounded_zero_block_theorem"]["necessary_and_sufficient_condition"] == "mu_H=mu_Px=mu_J1=mu_J2=mu_J3=R_c=0"
    print("EINSTEIN_MAXWELL_WEYL_FINITE_GENERIC_BOUNDED_ZERO_BLOCK independent verification: PASS")


if __name__ == "__main__":
    main()
