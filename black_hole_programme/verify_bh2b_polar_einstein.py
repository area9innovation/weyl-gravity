"""Structurally independent verifier for BH2B_POLAR_EINSTEIN.

Re-runs the entire fail-closed polar Einstein-branch analysis (RW-gauge
delta-Ric rows, H2 = H0, two-dimensional reduction with consistency,
horizon benchmark in both conventions) on the verifier-side
Schouten/Kulkarni--Nomizu pipeline (VbGeo), which shares no curvature code
with the producer engine.  Every claim is re-asserted by
`bh2b_polar_einstein.run_analysis`.  Additionally cross-checks the recorded
system matrix M against the recomputed one.

Also validates the certificate against its schema and provenance hashes.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import jsonschema
import sympy as sp

from bh2b_polar_einstein import run_analysis
from verify_bh2a_axial_operator import VbGeo

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
CERTIFICATE = HERE / "certificates" / "BH2B_POLAR_EINSTEIN.json"
SCHEMA = HERE / "schema" / "bh2b-polar-einstein-v1.schema.json"


class PolarEinsteinVerifyError(AssertionError):
    pass


def _check(cond: bool, msg: str) -> None:
    if not cond:
        raise PolarEinsteinVerifyError(msg)


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
    r = sp.Symbol("r", positive=True)
    w = sp.Symbol("omega")
    m = sp.Symbol("m", positive=True)
    loc = {"r": r, "omega": w, "m": m, "I": sp.I,
           "K": sp.Function("K"), "H1": sp.Function("H1")}
    for i in range(2):
        for j in range(2):
            rec = sp.sympify(payload["reduction"]["M"][i][j], locals=loc)
            _check(sp.cancel(sp.together(rec - res["M"][i, j])) == 0,
                   f"recorded M[{i}][{j}] mismatch")
    rec_h0 = sp.sympify(payload["reduction"]["H0_algebraic"], locals=loc)
    _check(sp.cancel(sp.together(rec_h0 - res["H0"])) == 0, "recorded H0 mismatch")
    print("BH2B_POLAR_EINSTEIN: all independent checks passed")
    print("stage_seconds:", res["stage_seconds"])


if __name__ == "__main__":
    verify_certificate()
