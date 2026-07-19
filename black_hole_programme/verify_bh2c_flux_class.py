"""Structurally independent verifier for BH2C_FLUX_CLASS.

Re-runs the entire fail-closed analysis (F^v bilinear, carrier and
homogeneous asymptotics, log-tail dichotomy, flux power table) on the
verifier-side Schouten/Kulkarni--Nomizu pipeline (VbGeo) and cross-checks
the recorded table.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import jsonschema
from bh2c_flux_class import run_analysis
from verify_bh2a_axial_operator import VbGeo

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
CERTIFICATE = HERE / "certificates" / "BH2C_FLUX_CLASS.json"
SCHEMA = HERE / "schema" / "bh2c-flux-class-v1.schema.json"


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
    _check(prov["engine_sha256"] == _sha256(ROOT / prov["engine_path"]), "engine hash")
    for key in ("jordan_certificate", "metric_leading_certificate"):
        _check(prov[key + "_sha256"] == _sha256(ROOT / prov[key]), f"{key} hash")
    res = run_analysis(VbGeo)
    _check(payload["flux_table"] == res["table"], "flux table mismatch")
    print("BH2C_FLUX_CLASS: all independent checks passed")
    print("stage_seconds:", res["stage_seconds"])


if __name__ == "__main__":
    verify_certificate()
