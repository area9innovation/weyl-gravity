"""Structurally independent verifier for BH4_HAWKING_MONODROMY.

Re-runs the entire fail-closed analysis (surface gravity, first-law
consistency, all four horizon spectra re-derived from scratch, monodromy
universality) on the verifier-side Schouten/Kulkarni--Nomizu pipeline
(VbGeo).  Cross-checks the recorded spectra and temperature strings.

Also validates the certificate against its schema and provenance hashes.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import jsonschema

from bh4_hawking_monodromy import run_analysis
from verify_bh2a_axial_operator import VbGeo

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
CERTIFICATE = HERE / "certificates" / "BH4_HAWKING_MONODROMY.json"
SCHEMA = HERE / "schema" / "bh4-hawking-monodromy-v1.schema.json"


class HawkingVerifyError(AssertionError):
    pass


def _check(cond: bool, msg: str) -> None:
    if not cond:
        raise HawkingVerifyError(msg)


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
                "polar_einstein_certificate", "axial_cross_certificate",
                "polar_cross_certificate", "bh1a_certificate"):
        _check(prov[key + "_sha256"] == _sha256(ROOT / prov[key]),
               f"{key} hash mismatch")
    res = run_analysis(VbGeo)
    _check(payload["temperature"]["kappa"] == res["kappa"], "kappa mismatch")
    _check(payload["temperature"]["T_H"] == res["T_H"], "T_H mismatch")
    for fam, exps in payload["spectra"].items():
        _check(sorted(exps) == sorted(res["spectra"][fam]),
               f"spectrum mismatch for {fam}")
    print("BH4_HAWKING_MONODROMY: all independent checks passed")
    print("stage_seconds:", res["stage_seconds"])


if __name__ == "__main__":
    verify_certificate()
