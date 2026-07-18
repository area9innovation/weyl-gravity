"""Independent verifier for BH2A_CROSS_FLUX.

Validates the schema and evidence hashes, checks the stored fixture data
for internal consistency (null-control smallness, imaginary extra norm
with the certified sign, nonzero cross pairing), and re-runs the full
pipeline at a THIRD frequency (omega = 1/2) with the same fail-closed
gates — an independent fixture the producer never touched.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import jsonschema
import sympy as sp

from axial_flux_modes import run_pipeline

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
CERTIFICATE = HERE / "certificates" / "BH2A_CROSS_FLUX.json"
SCHEMA = HERE / "schema" / "bh2a-cross-flux-v1.schema.json"


class CrossFluxVerifyError(AssertionError):
    pass


def _check(cond: bool, msg: str) -> None:
    if not cond:
        raise CrossFluxVerifyError(msg)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_certificate() -> None:
    payload = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator(schema).validate(payload)
    _check(payload["schema_sha256"] == _sha256(SCHEMA), "schema hash mismatch")
    prov = payload["provenance"]
    _check(prov["pipeline_sha256"] == _sha256(ROOT / prov["pipeline_path"]),
           "pipeline hash mismatch")
    for key in ("flux", "reach"):
        _check(prov[f"{key}_certificate_sha256"] == _sha256(ROOT / prov[f"{key}_certificate"]),
               f"{key} certificate hash mismatch")

    # stored-fixture internal consistency
    for fx in payload["fixtures"]:
        ees = [complex(s) for s in fx["ee_over_pi_alpha_float"]]
        ctls = [complex(s) for s in fx["control_over_pi_alpha_float"]]
        crs = [complex(s) for s in fx["cross_over_pi_alpha_float"]]
        for e in ees:
            _check(abs(e.real) < 1e-9 * abs(e), "stored ee not imaginary")
            _check(e.imag < 0, "stored ee sign mismatch")
        for c, e in zip(ctls, ees):
            _check(abs(c) < 1e-12 * abs(e), "stored control too large")
        _check(abs(ees[0] - ees[1]) < 0.02 * abs(ees[0]), "stored ee not stable")
        for c in crs:
            _check(abs(c) > abs(ees[0]) / 10, "stored cross too small")
    print("[stored] fixture consistency verified", flush=True)

    # independent third-frequency run with the same gates
    alpha = sp.Symbol("alpha")
    out = run_pipeline(sp.Rational(1, 2), NORD=16)
    ctrl = [sp.simplify(vv / (sp.pi * alpha)) for vv in out["control"]]
    cross = [sp.simplify(vv / (sp.pi * alpha)) for vv in out["cross"]]
    ee = [sp.simplify(vv / (sp.pi * alpha)) for vv in out["ee"]]
    for e in ee:
        _check(sp.re(e) == 0, "third-frequency ee not exactly imaginary")
        _check(sp.im(e) < 0, "third-frequency ee sign differs")
    for c, e in zip(ctrl, ee):
        _check(sp.Abs(c) ** 2 * sp.Integer(10) ** 24 < sp.Abs(e) ** 2,
               "third-frequency null control fails")
    _check(sp.Abs(ee[0] - ee[1]) ** 2 * sp.Integer(2500) < sp.Abs(ee[0]) ** 2,
           "third-frequency ee not stable")
    for c in cross:
        _check(sp.Abs(c) ** 2 * sp.Integer(100) > sp.Abs(ee[0]) ** 2,
               "third-frequency cross too small")
    print("[independent] third-frequency fixture (omega = 1/2) passes all gates", flush=True)
    print("BH2A_CROSS_FLUX: all independent checks passed")


if __name__ == "__main__":
    verify_certificate()
