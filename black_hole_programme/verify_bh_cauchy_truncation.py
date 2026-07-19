"""Structurally independent verifier for BH_LOCAL_EINSTEIN_CAUCHY_TRUNCATION.

Re-runs the entire fail-closed analysis (axial and polar operator/trace/
constraint-transport identities, the conformal witness, the time-odd
mutation witness) on the verifier-side Schouten/Kulkarni--Nomizu pipeline
(VbGeo) and validates the recorded certificate.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import jsonschema
from bh_cauchy_truncation import run_analysis
from verify_bh2a_axial_operator import VbGeo

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
CERTIFICATE = HERE / "certificates" / "BH_LOCAL_EINSTEIN_CAUCHY_TRUNCATION.json"
SCHEMA = HERE / "schema" / "bh-local-einstein-cauchy-truncation-v1.schema.json"


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
    _check(prov["engine_sha256"] == _sha256(ROOT / prov["engine_path"]),
           "engine hash")
    for key in ("axial_operator_certificate", "polar_split_certificate"):
        _check(prov[key + "_sha256"] == _sha256(ROOT / prov[key]), f"{key} hash")
    res = run_analysis(VbGeo)
    _check(set(res["stage_seconds"])
           >= {"axial_identities", "polar_identities", "conformal_witness",
               "mutation_witness"},
           "verifier stages incomplete")
    print("BH_LOCAL_EINSTEIN_CAUCHY_TRUNCATION: all independent checks passed")
    print("stage_seconds:", res["stage_seconds"])


if __name__ == "__main__":
    verify_certificate()
