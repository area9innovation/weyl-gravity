#!/usr/bin/env python3
"""Independent verifier for the Weyl--Maxwell symplectic preflight."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import jsonschema
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_weyl_symplectic_preflight.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_symplectic_preflight.schema.json"


def verify_certificate() -> dict[str, object]:
    payload = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator(schema).validate(payload)
    assert payload["schema_sha256"] == hashlib.sha256(SCHEMA.read_bytes()).hexdigest()
    for record in payload["provenance"]["inputs"].values():
        path = ROOT / record["path"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == record["sha256"]

    # Re-derive the pure-Weyl kernel equations without importing the generator.
    sigma, sigma_tt, sigma_xx, laplacian = sp.symbols("sigma sigma_tt sigma_xx Delta_S2_sigma")
    box_sigma = -sigma_tt + sigma_xx + laplacian
    rows = {
        "tt": sp.expand(-sigma_tt - box_sigma),
        "xx": sp.expand(-sigma_xx + box_sigma),
        "sphere_trace": sp.expand(-laplacian + 2 * box_sigma + 2 * sigma),
    }
    stored_rows = payload["quotient_injectivity_theorem"]["independent_component_equations"]
    for name, expression in rows.items():
        assert sp.expand(sp.sympify(stored_rows[name]) - expression) == 0
    reduced = sp.expand(rows["sphere_trace"].subs({sigma_tt: laplacian, sigma_xx: -laplacian}))
    assert reduced == 2 * sigma - 3 * laplacian
    assert sp.expand(sp.sympify(payload["quotient_injectivity_theorem"]["elimination"]) - reduced) == 0
    ell = sp.symbols("ell", integer=True, nonnegative=True)
    coefficient = sp.factor(reduced.subs(laplacian, -ell * (ell + 1) * sigma) / sigma)
    assert sp.simplify(coefficient - (3 * ell * (ell + 1) + 2)) == 0
    assert payload["quotient_injectivity_theorem"]["status"] == "CERTIFIED"
    assert payload["classification"]["induced_linear_tangent_quotient_map_injective"] is True
    assert payload["classification"]["weyl_maxwell_symplectic_restriction_computed"] is False
    assert payload["classification"]["nonlinear_solution_space_embedding_certified"] is False
    assert "TARGET_GAUGE" not in payload["comparison_contract"]["admissible_verdicts"]
    return payload


if __name__ == "__main__":
    verify_certificate()
    print("EINSTEIN_MAXWELL_WEYL_SYMPLECTIC_PREFLIGHT independent verification: PASS")
