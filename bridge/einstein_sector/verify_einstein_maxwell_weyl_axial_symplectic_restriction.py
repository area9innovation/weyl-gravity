#!/usr/bin/env python3
"""Independent verifier for the axial ell=2 symplectic restriction."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import jsonschema
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_symplectic_restriction.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_axial_symplectic_restriction.schema.json"


def verify_certificate() -> dict[str, object]:
    payload = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator(schema).validate(payload)
    assert payload["schema_sha256"] == hashlib.sha256(SCHEMA.read_bytes()).hexdigest()
    for record in payload["provenance"]["inputs"].values():
        path = ROOT / record["path"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == record["sha256"]
    for record in payload["provenance"]["direct_implementation"].values():
        path = ROOT / record["path"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == record["sha256"]

    k, omega, h, q = sp.symbols("k omega H Q", real=True)
    local = {"k": k, "omega": omega, "H": h, "Q": q, "I": sp.I, "pi": sp.pi}
    currents = payload["restriction"]["off_shell_integrated_coordinate_currents"]
    einstein = sp.sympify(currents["einstein_maxwell"], locals=local)
    weyl = sp.sympify(currents["weyl_maxwell"], locals=local)
    for row, sign in zip(payload["restriction"]["on_shell_branches"], (1, -1), strict=True):
        mass = 6 + sign * 2 * sp.sqrt(3)
        branch = {q: sign * sp.sqrt(3) * h}
        e_branch = sp.factor(sp.expand(einstein.subs(branch)).subs(k**2, omega**2 - mass))
        w_branch = sp.factor(sp.expand(weyl.subs(branch)).subs(k**2, omega**2 - mass))
        ratio = sp.simplify(w_branch / e_branch)
        assert sp.simplify(ratio - (1 + sign * 3 * sp.sqrt(3))) == 0
        assert sp.simplify(sp.sympify(row["restriction_over_einstein"]) - ratio) == 0
    assert payload["restriction"]["signature_relative_to_positive_einstein_branch_form"] == {"positive": 1, "negative": 1, "zero": 0}
    assert payload["classification"]["axial_ell2_restriction_nondegenerate"] is True
    assert payload["classification"]["single_universal_proportionality_to_einstein_form"] is False
    assert payload["classification"]["relative_branch_form_indefinite"] is True
    assert payload["classification"]["target_weyl_gauge_removes_einstein_class"] is False
    assert payload["classification"]["all_axial_ell_ge2_restriction_computed"] is False
    return payload


if __name__ == "__main__":
    verify_certificate()
    print("EINSTEIN_MAXWELL_WEYL_AXIAL_SYMPLECTIC_RESTRICTION independent verification: PASS")
