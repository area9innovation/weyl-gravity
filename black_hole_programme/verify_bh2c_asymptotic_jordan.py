"""Structurally independent verifier for BH2C_ASYMPTOTIC_JORDAN.

Re-runs the entire fail-closed asymptotic formal analysis (axial symbolic
resonance consistency, polar symbolic mu=0 jet count, polar fixture
mu=-2omega jet counts) on the verifier-side Schouten/Kulkarni--Nomizu
pipeline (VbGeo) and cross-checks the recorded tables.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import jsonschema

from bh2c_asymptotic_jordan import run_analysis
from verify_bh2a_axial_operator import VbGeo

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
CERTIFICATE = HERE / "certificates" / "BH2C_ASYMPTOTIC_JORDAN.json"
SCHEMA = HERE / "schema" / "bh2c-asymptotic-jordan-v1.schema.json"


class AsymptoticJordanVerifyError(AssertionError):
    pass


def _check(cond: bool, msg: str) -> None:
    if not cond:
        raise AsymptoticJordanVerifyError(msg)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_certificate() -> None:
    payload = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator(schema).validate(payload)
    _check(payload["schema_sha256"] == _sha256(SCHEMA), "schema hash mismatch")
    prov = payload["provenance"]
    _check(prov["engine_sha256"] == _sha256(ROOT / prov["engine_path"]),
           "engine hash mismatch")
    for key in ("axial_disposition_certificate", "polar_disposition_certificate"):
        _check(prov[key + "_sha256"] == _sha256(ROOT / prov[key]),
               f"{key} hash mismatch")
    res = run_analysis(VbGeo)
    _check(payload["axial"] == res["axial"], "axial tables mismatch")
    _check(payload["polar"] == res["polar"], "polar tables mismatch")
    print("BH2C_ASYMPTOTIC_JORDAN: all independent checks passed")
    print("stage_seconds:", res["stage_seconds"])


if __name__ == "__main__":
    verify_certificate()
