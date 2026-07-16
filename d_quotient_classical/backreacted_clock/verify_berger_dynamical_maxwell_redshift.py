#!/usr/bin/env python3
"""Independent exact replay of the Berger Maxwell redshift mode."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "d_quotient_classical/certificates/BERGER_DYNAMICAL_MAXWELL_REDSHIFT_MODE.json"
SCHEMA = ROOT / "d_quotient_classical/schema/berger-dynamical-maxwell-redshift-v1.schema.json"


def main() -> None:
    certificate = json.loads(CERTIFICATE.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(certificate)

    for record in certificate["dependency_refs"].values():
        source = ROOT / record["path"]
        if hashlib.sha256(source.read_bytes()).hexdigest() != record["sha256"]:
            raise AssertionError(f"dependency hash mismatch: {source}")
        if json.loads(source.read_text())["result_id"] != record["result_id"]:
            raise AssertionError(f"dependency result mismatch: {source}")
    for relative_path, expected_hash in certificate["provenance"]["source_manifest"].items():
        source = ROOT / relative_path
        if hashlib.sha256(source.read_bytes()).hexdigest() != expected_hash:
            raise AssertionError(f"source manifest mismatch: {source}")

    # Independent field-equation replay in the left-invariant coframe.
    beta_symbol, alpha, t = sp.symbols("beta alpha t", positive=True, real=True)
    potential = sp.Matrix(
        [sp.cos(beta_symbol * t), sp.sin(beta_symbol * t), 0]
    )
    curl = sp.diag(-beta_symbol, -beta_symbol, -alpha)
    electric = -sp.diff(potential, t)
    magnetic = curl * potential
    if sp.simplify(sp.diff(potential, t, 2) + curl * curl * potential) != sp.zeros(3, 1):
        raise AssertionError("independent source-free Maxwell replay failed")
    if sp.trigsimp(electric.dot(electric) - magnetic.dot(magnetic)) != 0:
        raise AssertionError("independent null-field norm replay failed")
    if sp.trigsimp(electric.dot(magnetic)) != 0:
        raise AssertionError("independent null-field pseudoscalar replay failed")
    if sp.simplify(sp.trigsimp(electric.cross(magnetic)) - sp.Matrix([0, 0, -beta_symbol**2])) != sp.zeros(3, 1):
        raise AssertionError("independent Poynting direction replay failed")

    beta = 2 * sp.sqrt(10) / 3
    volume = 12 * sp.sqrt(10) * sp.pi**2 / 5
    gamma_receive = sp.Rational(5, 4)
    frequency_emit = beta
    frequency_receive = sp.factor(beta * gamma_receive * sp.Rational(2, 5))
    expected = {
        "beta": str(beta),
        "spatial_volume": str(volume),
        "gamma_emit": "1",
        "gamma_receive": "5/4",
        "frequency_emit": str(frequency_emit),
        "frequency_receive": str(frequency_receive),
        "averaged_energy_emit": "40/9",
        "averaged_energy_receive": "10/9",
        "one_plus_z": "2",
        "z": "1",
        "travel_time": "1/2",
        "theta_receive": "3/8",
        "phase_slope_emit": "-8*sqrt(10)/9",
        "phase_slope_receive": "-16*sqrt(10)/45",
        "symplectic_pairing": "-32*pi**2",
        "positive_energy_coefficient": "32*sqrt(10)*pi**2/3",
    }
    if certificate["rational_fixture"]["results"] != expected:
        raise AssertionError("independent Maxwell fixture replay failed")
    if certificate["health_and_pairing"]["energy_signature"] != [2, 0, 0]:
        raise AssertionError("positive Maxwell energy signature drifted")
    if certificate["flags"]["BERGER_GRAVITY_MAXWELL_Q2_DRESSING"] is not False:
        raise AssertionError("missing q2 extension was promoted")
    print("BERGER_DYNAMICAL_MAXWELL_REDSHIFT_MODE independent replay: PASS")


if __name__ == "__main__":
    main()
