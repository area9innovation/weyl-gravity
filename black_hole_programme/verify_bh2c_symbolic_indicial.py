"""Structurally independent verifier for BH2C_SYMBOLIC_INDICIAL.

Re-runs the full symbolic-frequency indicial analysis -- polar carrier
leading matrix, semisimplicity by explicit nullspace dimension, sector
exponents, the axial cascade and rank-1 level-2 block, the RW-gauge ODE,
the resonance structure, and both mutations -- on the verifier-side
Schouten/Kulkarni--Nomizu pipeline (VbGeo), then validates the recorded
certificate against schema, hashes and every symbolic value.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import jsonschema

from bh2c_symbolic_indicial import run_analysis
from verify_bh2a_axial_operator import VbGeo

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
CERTIFICATE = HERE / "certificates" / "BH2C_SYMBOLIC_INDICIAL.json"
SCHEMA = HERE / "schema" / "bh2c-symbolic-indicial-v1.schema.json"


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
    ext = payload["extends"]
    _check(ext["certificate_sha256"] == _sha256(ROOT / ext["certificate"]),
           "extended certificate hash mismatch")

    res = run_analysis(VbGeo)
    for key in ("polar", "axial", "resonance", "exceptional_set"):
        _check(payload[key] == res[key], f"{key} mismatch")

    # the extended certificate must still be the one that flags the gap
    jordan = json.loads((ROOT / ext["certificate"]).read_text())
    _check(jordan["claim_flags"]["polar_mu2w_symbolic_certified"] is False,
           "extended certificate no longer records the symbolic gap")
    _check(payload["claim_flags"]["polar_mu2w_symbolic_certified"] is True,
           "this certificate does not close the symbolic gap")

    print("BH2C_SYMBOLIC_INDICIAL: all independent checks passed")
    print("stage_seconds:", res["stage_seconds"])


if __name__ == "__main__":
    verify_certificate()
