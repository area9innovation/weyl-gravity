"""Structurally independent verifier for BH2A_COMPOSED_REPAIR.

Re-runs the entire fail-closed analysis (3-function rows, two-level
cascade with the source-compatibility identity, RW-gauge single-ODE
particular with zero cokernel, structured three-row receipt, and the
constant-flux windows with exact values) on the verifier-side
Schouten/Kulkarni--Nomizu pipeline (VbGeo) and validates the recorded
certificate.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import jsonschema
from bh2a_composed_repair import run_analysis
from verify_bh2a_axial_operator import VbGeo

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
CERTIFICATE = HERE / "certificates" / "BH2A_COMPOSED_REPAIR.json"
SCHEMA = HERE / "schema" / "bh2a-composed-repair-v1.schema.json"


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
    for key, path in (("engine_sha256", prov["engine_path"]),
                      ("pipeline_sha256", prov["pipeline_path"]),
                      ("flux_matrix_certificate_sha256",
                       prov["flux_matrix_certificate"])):
        _check(prov[key] == _sha256(ROOT / path), f"{key} mismatch")
    sup = payload["supersedes"]
    _check(sup["certificate_sha256"] == _sha256(ROOT / sup["certificate"]),
           "superseded certificate hash mismatch")
    res = run_analysis(VbGeo)
    _check(payload["fixtures"] == res["fixtures"], "fixture values mismatch")
    print("BH2A_COMPOSED_REPAIR: all independent checks passed")
    print("stage_seconds:", res["stage_seconds"])


if __name__ == "__main__":
    verify_certificate()
