"""Structurally independent verifier for BH2B_POLAR_CROSS_FLUX.

Re-runs the entire fail-closed polar cross-flux pipeline (carrier
machinery, mode construction, delta Ric[h] = psi composition with all-row
verification, Einstein/gauge controls, EF bilinear, fixture flux matrix
with all asserts) on the verifier-side Schouten/Kulkarni--Nomizu pipeline
(VbGeo).  Cross-checks the recorded rho = 1/4 flux matrix entry-by-entry
against the recomputed one (exact equality).

Also validates the certificate against its schema and provenance hashes.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import sympy as sp

import jsonschema

from bh2b_polar_cross_flux import run_pipeline
from verify_bh2a_axial_operator import VbGeo

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
CERTIFICATE = HERE / "certificates" / "BH2B_POLAR_CROSS_FLUX.json"
SCHEMA = HERE / "schema" / "bh2b-polar-cross-flux-v1.schema.json"


class PolarCrossFluxVerifyError(AssertionError):
    pass


def _check(cond: bool, msg: str) -> None:
    if not cond:
        raise PolarCrossFluxVerifyError(msg)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_certificate() -> None:
    payload = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator(schema).validate(payload)
    _check(payload["schema_sha256"] == _sha256(SCHEMA), "schema hash mismatch")
    prov = payload["provenance"]
    for key, path_key in [("engine_sha256", "engine_path"),
                          ("theta_sha256", "theta_path")]:
        _check(prov[key] == _sha256(ROOT / prov[path_key]), f"{path_key} hash mismatch")
    for key in ("bh2b_reach_certificate", "bh2b_einstein_certificate",
                "bh2b_flux_certificate"):
        _check(prov[key + "_sha256"] == _sha256(ROOT / prov[key]),
               f"{key} hash mismatch")
    res = run_pipeline(VbGeo, sp.Rational(3, 5),
                       [sp.Rational(1, 4), sp.Rational(1, 2)])
    alpha = sp.Symbol("alpha", positive=True)
    loc = {"alpha": alpha, "I": sp.I, "pi": sp.pi}
    for key, rec_expr in payload["fixtures"]["flux_matrix_rho_1_4"].items():
        rec = sp.sympify(rec_expr, locals=loc)
        got = sp.sympify(res["matrix"][key], locals=loc)
        _check(sp.simplify(rec - got) == 0,
               f"recorded flux matrix entry {key} mismatch")
    print("BH2B_POLAR_CROSS_FLUX: all independent checks passed")
    print("stage_seconds:", res["stage_seconds"])


if __name__ == "__main__":
    verify_certificate()
