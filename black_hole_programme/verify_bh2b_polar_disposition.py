"""Structurally independent verifier for BH2B_POLAR_DISPOSITION.

Re-runs the entire fail-closed polar disposition analysis (carrier sliced
rows, asymptotic dispersion and sigma spectra, Einstein K-scalar control,
conformal-gauge scalar control) on the verifier-side
Schouten/Kulkarni--Nomizu pipeline (VbGeo).  Every claim is re-asserted by
`bh2b_polar_disposition.run_analysis`.

Also validates the certificate against its schema and provenance hashes.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import jsonschema

from bh2b_polar_disposition import run_analysis
from verify_bh2a_axial_operator import VbGeo

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
CERTIFICATE = HERE / "certificates" / "BH2B_POLAR_DISPOSITION.json"
SCHEMA = HERE / "schema" / "bh2b-polar-disposition-v1.schema.json"


class PolarDispositionVerifyError(AssertionError):
    pass


def _check(cond: bool, msg: str) -> None:
    if not cond:
        raise PolarDispositionVerifyError(msg)


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
    for key in ("bh2b_reach_certificate", "bh2b_flux_certificate",
                "bh2b_cross_flux_certificate", "bh2b_einstein_certificate"):
        _check(prov[key + "_sha256"] == _sha256(ROOT / prov[key]),
               f"{key} hash mismatch")
    res = run_analysis(VbGeo)
    _check(payload["asymptotics"]["sigma_ef"] == res["sigma"],
           "recorded sigma spectra mismatch")
    print("BH2B_POLAR_DISPOSITION: all independent checks passed")
    print("stage_seconds:", res["stage_seconds"])


if __name__ == "__main__":
    verify_certificate()
