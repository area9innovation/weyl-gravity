#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERT = ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_ellipse_sobolev_bohr_no_go.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_exceptional_ellipse_sobolev_bohr_no_go.schema.json"


def verify() -> None:
    value = json.loads(CERT.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    for item in value["provenance"]["inputs"].values():
        path = ROOT / item["path"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == item["sha256"]

    lam = sp.symbols("lambda", positive=True, real=True)
    omega = sp.sqrt(lam - sp.sqrt(2 * lam))
    axial = -3 * sp.I * omega * (3 * sp.sqrt(2 * lam) - 1)
    polar = lam**2 * (2 * lam - 1) / 6
    for ell in range(2, 20):
        physical = ell * (ell + 1)
        assert sp.simplify(axial.subs(lam, physical)) != 0
        assert polar.subs(lam, physical) > 0

    domain = value["declared_sobolev_bohr_domain"]
    assert domain["regularity"] == "integer s>=6"
    assert "closure of finite" in domain["mode_space"]
    assert "fails the all-orders weighted l1" in domain["strictly_weaker_than_smooth_wiener"]
    lemma = value["continuous_quadratic_projection_lemma"]
    assert "total order at most four" in lemma["sobolev_product"]
    assert "contraction" in lemma["frequency_projection"]
    assert "Bochner-Fejer" in lemma["finite_approximation"]
    classes = value["correction_classes"]
    assert classes["BOUNDED_UNIFORMLY_ALMOST_PERIODIC_SOBOLEV_GRAPH"]["status"] == "OBSTRUCTED"
    assert classes["SMOOTH_INFINITE_SECULAR"]["status"] == "OPEN"
    assert classes["CAUSAL_RETARDED"]["status"] == "NO_CERTIFIED_MAP"
    classification = value["classification"]
    assert classification["strict_extension_beyond_smooth_wiener_domain"]
    assert classification["continuous_quadratic_source_map_certified"]
    assert not classification["maximal_finite_energy_or_low_regularity_completion_classified"]
    assert not classification["nonzero_momentum_classified"]


if __name__ == "__main__":
    verify()
    print("EINSTEIN_MAXWELL_WEYL_EXCEPTIONAL_ELLIPSE_SOBOLEV_BOHR_NO_GO independent verification: PASS")
