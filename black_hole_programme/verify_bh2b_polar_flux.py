"""Structurally independent verifier for BH2B_POLAR_FLUX.

Re-runs the ENTIRE fail-closed polar flux analysis (machinery controls,
general polar bilinear, off-shell 4-alpha identity, Einstein-block
reduction and null theorem, conformal-gauge degeneracy control) on the
verifier-side Schouten/Kulkarni--Nomizu pipeline (VbGeo), which shares no
curvature code with the producer engine.  Every claim is re-asserted by
`bh2b_polar_flux.run_flux_analysis`; additionally the recorded bilinear
and Einstein-block coefficients are cross-checked against the recomputed
ones.

Also validates the certificate against its schema and provenance hashes.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import jsonschema
import sympy as sp

from bh2b_polar_flux import run_flux_analysis
from verify_bh2a_axial_operator import VbGeo

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
CERTIFICATE = HERE / "certificates" / "BH2B_POLAR_FLUX.json"
SCHEMA = HERE / "schema" / "bh2b-polar-flux-v1.schema.json"


class PolarFluxVerifyError(AssertionError):
    pass


def _check(cond: bool, msg: str) -> None:
    if not cond:
        raise PolarFluxVerifyError(msg)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_certificate() -> None:
    payload = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator(schema).validate(payload)
    _check(payload["schema_sha256"] == _sha256(SCHEMA), "schema hash mismatch")
    prov = payload["provenance"]
    for key, path_key in [("engine_sha256", "engine_path"),
                          ("theta_sha256", "theta_path"),
                          ("bach_sha256", "bach_path")]:
        _check(prov[key] == _sha256(ROOT / prov[path_key]), f"{path_key} hash mismatch")
    for key in ("bh1b_certificate", "bh2b_einstein_certificate"):
        _check(prov[key + "_sha256"] == _sha256(ROOT / prov[key]),
               f"{key} hash mismatch")

    res = run_flux_analysis(VbGeo)

    # cross-check recorded objects against the independent recomputation
    t = sp.Symbol("t")
    r = sp.Symbol("r", positive=True)
    m = sp.Symbol("m", positive=True)
    alpha = sp.Symbol("alpha")
    w1, w2 = sp.symbols("omega1 omega2")
    loc = {"t": t, "r": r, "m": m, "alpha": alpha, "I": sp.I, "pi": sp.pi,
           "omega1": w1, "omega2": w2}
    for nm in ("H0", "H1", "H2", "K"):
        for tag in ("a", "b"):
            loc[nm + tag] = sp.Function(nm + tag)
    for key, rec_expr in [("Ft", payload["bilinear"]["Ft"]),
                          ("Fr", payload["bilinear"]["Fr"])]:
        rec = sp.sympify(rec_expr, locals=loc)
        _check(sp.cancel(sp.together(rec - res[key])) == 0,
               f"recorded {key} bilinear mismatch")
    for key, rec_expr in payload["einstein_block"]["coefficients"].items():
        rec = sp.sympify(rec_expr, locals=loc)
        got = sp.sympify(res["einstein_block"][key], locals=loc)
        _check(sp.cancel(sp.together(rec - got)) == 0,
               f"recorded Einstein-block coefficient {key} mismatch")
    print("BH2B_POLAR_FLUX: all independent checks passed")
    print("stage_seconds:", res["stage_seconds"])


if __name__ == "__main__":
    verify_certificate()
