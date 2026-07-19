"""Structurally independent verifier for BH2B_POLAR_REACH.

Re-runs the ENTIRE fail-closed polar-reach analysis (Bianchi cascade,
constrained carrier, operator rows, exact trace/divergence identities,
conformal gauge generator, traceless-slice residue spectrum, residual-gauge
exponents and images, analytic-family fixtures) on the verifier-side
Schouten/Kulkarni--Nomizu curvature pipeline (the VbGeo adapter of
`verify_bh2a_axial_operator`), which shares no curvature code with the
producer engine `weyl_geometry.Geometry`.  Every claim is re-asserted by
`bh2b_polar_reach.run_analysis`; a single failure raises.

Also validates the certificate against its schema and checks all content
hashes recorded in the provenance block.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import jsonschema

from bh2b_polar_reach import run_analysis
from verify_bh2a_axial_operator import VbGeo

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
CERTIFICATE = HERE / "certificates" / "BH2B_POLAR_REACH.json"
SCHEMA = HERE / "schema" / "bh2b-polar-reach-v1.schema.json"


class PolarReachVerifyError(AssertionError):
    pass


def _check(cond: bool, msg: str) -> None:
    if not cond:
        raise PolarReachVerifyError(msg)


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
    _check(
        prov["bh2b_split_certificate_sha256"] == _sha256(ROOT / prov["bh2b_split_certificate"]),
        "BH-2B stage-1 certificate hash mismatch",
    )
    res = run_analysis(VbGeo)
    _check("slice_residue" in res["stage_seconds"], "analysis incomplete")
    print("BH2B_POLAR_REACH: all independent checks passed")
    print("stage_seconds:", res["stage_seconds"])


if __name__ == "__main__":
    verify_certificate()
