"""Structurally independent verifier for BH2_OMEGA_ZERO.

Re-runs the entire fail-closed omega = 0 classification (axial and polar
carrier systems, RW control, polar-Einstein degeneration) on the
verifier-side Schouten/Kulkarni--Nomizu pipeline (VbGeo) and cross-checks
the recorded classification tables.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import jsonschema

from bh2_omega_zero import run_analysis
from verify_bh2a_axial_operator import VbGeo

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
CERTIFICATE = HERE / "certificates" / "BH2_OMEGA_ZERO.json"
SCHEMA = HERE / "schema" / "bh2-omega-zero-v1.schema.json"


class OmegaZeroVerifyError(AssertionError):
    pass


def _check(cond: bool, msg: str) -> None:
    if not cond:
        raise OmegaZeroVerifyError(msg)


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
    for key in ("axial_reach_certificate", "polar_reach_certificate",
                "polar_einstein_certificate"):
        _check(prov[key + "_sha256"] == _sha256(ROOT / prov[key]),
               f"{key} hash mismatch")
    res = run_analysis(VbGeo)
    _check(payload["classification"] == res["results"],
           "classification tables mismatch")
    print("BH2_OMEGA_ZERO: all independent checks passed")
    print("stage_seconds:", res["stage_seconds"])


if __name__ == "__main__":
    verify_certificate()
