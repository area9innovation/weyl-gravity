#!/usr/bin/env python3
"""Independent verifier for the charged-time event-map contract."""

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp

ROOT = Path(__file__).resolve().parents[1]
CERT = ROOT / "closed_universe_observers/certificates/COUNTERFLOW_CHARGED_TIME_RELATIONAL_OBSERVABLE_PREFLIGHT_V1.json"
SCHEMA = ROOT / "closed_universe_observers/schema/counterflow-charged-time-relational-observable-preflight-v1.schema.json"


def verify() -> dict:
    value = json.loads(CERT.read_text()); schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema); Draft202012Validator(schema).validate(value)
    for ref in value["dependency_refs"].values():
        if hashlib.sha256((ROOT / ref["path"]).read_bytes()).hexdigest() != ref["sha256"]: raise ValueError("dependency drift")
    psi, charge, tau = sp.symbols("psi Q tau")
    omega = sp.Rational(3, 4); f = sp.Function("F")(tau - psi)
    bracket = lambda a, b: sp.diff(a, psi)*sp.diff(b, charge)-sp.diff(a, charge)*sp.diff(b, psi)
    if bracket(psi, charge) != 1 or bracket(psi, omega*charge) != omega: raise ValueError("Darboux replay")
    if sp.simplify(bracket(f, charge)+sp.diff(f,tau)) != 0: raise ValueError("R covariance")
    if sp.simplify(bracket(f, omega*charge)+omega*sp.diff(f,tau)) != 0: raise ValueError("D covariance")
    inertia = 12*sp.pi**2*sp.sqrt(10)/5
    if sp.simplify(-omega*inertia + 9*sp.pi**2*sp.sqrt(10)/5) != 0: raise ValueError("monotonic bound")
    if value["physical_instantiation_gate"]["status"] != "NO_CERTIFIED_MAP" or value["flags"]["PHYSICAL_REDSHIFT_CERTIFIED"]: raise ValueError("promotion")
    if not all(row["detected"] for row in value["mutation_results"]): raise ValueError("mutation")
    return value


if __name__ == "__main__": verify(); print("COUNTERFLOW_CHARGED_TIME_RELATIONAL_OBSERVABLE_PREFLIGHT_V1 independent verification: PASS")
