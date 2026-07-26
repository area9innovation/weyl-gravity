"""Scoped tests for the Paper 18 successor certificate and stdlib rail."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys

import jsonschema


ROOT = Path(__file__).resolve().parents[2]
PKG = ROOT / "black_hole_programme"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def test_promotion_certificate_is_current_and_schema_valid() -> None:
    producer = load_module("paper18_promotion", PKG / "paper18_static_first_law_promotion.py")
    actual = json.loads(
        (PKG / "certificates" / "PAPER18_STATIC_FIRST_LAW_PROMOTION.json").read_text(encoding="utf-8")
    )
    schema = json.loads(
        (PKG / "schema" / "paper18-static-first-law-promotion-v1.schema.json").read_text(encoding="utf-8")
    )
    jsonschema.Draft202012Validator(schema).validate(actual)
    assert actual == producer.build()
    assert actual["declaration"]["historical_certificates_unchanged"]
    assert not actual["claim_flags"]["physical_process_first_law_certified"]
    assert not actual["claim_flags"]["radiative_flux_certified"]


def test_standard_library_algebra_rail() -> None:
    verifier = load_module(
        "paper18_stdlib",
        ROOT / "paper" / "verify_18_static_weyl_thermodynamics_stdlib.py",
    )
    checks = verifier.verify()
    assert len(checks) >= 20
    assert "first-law quotient (beta)" in checks
    assert "mutation control rejects H+beta" in checks
