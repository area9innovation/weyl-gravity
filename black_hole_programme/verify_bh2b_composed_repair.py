"""Structurally independent verifier for BH2B_COMPOSED_REPAIR.

Re-runs the complete fail-closed analysis -- horizon exact-constant
windows at both fixtures (controls identically zero, physical pairs
constant with exact rho^0 values, exact Hermiticity/positivity), the
off-shell drift mutation, and the infinity vv/vr audit with the unique
Einstein combination and recomputed table classes -- on the verifier-side
Schouten/Kulkarni--Nomizu pipeline (VbGeo) and validates the recorded
certificate against schema, hashes, and fixture values.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import jsonschema

from bh2b_composed_repair import run_analysis
from verify_bh2a_axial_operator import VbGeo

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
CERTIFICATE = HERE / "certificates" / "BH2B_COMPOSED_REPAIR.json"
SCHEMA = HERE / "schema" / "bh2b-composed-repair-v1.schema.json"


def _check(cond, msg):
    if not cond:
        raise AssertionError(msg)


def _sha256(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def verify_certificate():
    payload = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator(schema).validate(payload)
    _check(payload["schema_sha256"] == _sha256(SCHEMA),
           "schema hash mismatch")
    prov = payload["provenance"]
    for key, path in (("pipeline_sha256", prov["pipeline_path"]),
                      ("reach_sha256", prov["reach_path"])):
        _check(prov[key] == _sha256(ROOT / path), f"{key} mismatch")
    sup = payload["supersedes"]
    for tag in ("cross_flux", "flux_class"):
        _check(sup[f"{tag}_certificate_sha256"]
               == _sha256(ROOT / sup[f"{tag}_certificate"]),
               f"superseded {tag} certificate hash mismatch")
    res = run_analysis(VbGeo)
    _check(payload["fixtures"] == res["fixtures"],
           "fixture values mismatch")
    _check(payload["audit"] == res["audit"], "audit results mismatch")
    print("BH2B_COMPOSED_REPAIR: all independent checks passed")
    print("stage_seconds:", res["stage_seconds"])


if __name__ == "__main__":
    verify_certificate()
