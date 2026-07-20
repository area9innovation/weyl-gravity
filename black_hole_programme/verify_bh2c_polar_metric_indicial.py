"""Structurally independent verifier for BH2C_POLAR_METRIC_INDICIAL.

Re-runs the metric-side indicial analysis -- leading matrix, fixture
cross-check, Jordan staircase, and BOTH controls (the positive control
that the extraction reproduces certified sigma0 in the semisimple sector,
and the negative control that it fails to in the Jordan sector) -- on the
verifier-side Schouten/Kulkarni--Nomizu pipeline (VbGeo), then validates
the recorded certificate.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import jsonschema

from bh2c_polar_metric_indicial import run_analysis
from verify_bh2a_axial_operator import VbGeo

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
CERTIFICATE = HERE / "certificates" / "BH2C_POLAR_METRIC_INDICIAL.json"
SCHEMA = HERE / "schema" / "bh2c-polar-metric-indicial-v1.schema.json"


def _check(cond, msg):
    if not cond:
        raise AssertionError(msg)


def _sha256(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def verify_certificate():
    payload = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator(schema).validate(payload)
    _check(payload["schema_sha256"] == _sha256(SCHEMA), "schema hash mismatch")
    prov = payload["provenance"]
    _check(prov["reach_sha256"] == _sha256(ROOT / prov["reach_path"]),
           "reach hash mismatch")
    _check(prov["certified_sigma0_source_sha256"]
           == _sha256(ROOT / prov["certified_sigma0_source"]),
           "certified sigma0 source hash mismatch")
    comp = payload["companion"]
    _check(comp["certificate_sha256"] == _sha256(ROOT / comp["certificate"]),
           "companion certificate hash mismatch")

    res = run_analysis(VbGeo)
    _check(payload["sectors"] == res["sectors"], "sector data mismatch")
    _check(payload["established"]["charpoly"] == res["charpoly"],
           "charpoly mismatch")
    _check(payload["established"]["semisimple_sector"]
           == res["positive_control"], "positive control mismatch")
    _check(payload["obstruction"]["evidence"] == res["negative_control"],
           "negative control mismatch")
    # the obstruction must remain an obstruction
    _check(payload["claim_flags"]["mu0_exponents_certified"] is False,
           "mu0 exponents must not be claimed")
    _check(payload["claim_flags"]["shearing_analysis_performed"] is False,
           "shearing analysis was not performed")
    print("BH2C_POLAR_METRIC_INDICIAL: all independent checks passed")
    print("stage_seconds:", res["stage_seconds"])


if __name__ == "__main__":
    verify_certificate()
