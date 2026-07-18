"""Independent verifier for BH2B_POLAR_SPLIT (verifier-side pipeline)."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import jsonschema
import sympy as sp

from linearized_bach import LinearizedBach
from verify_bh2a_axial_operator import VbGeo

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
CERTIFICATE = HERE / "certificates" / "BH2B_POLAR_SPLIT.json"
SCHEMA = HERE / "schema" / "bh2b-polar-split-v1.schema.json"


def _check(cond, msg):
    if not cond:
        raise AssertionError(msg)


def _sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_certificate() -> None:
    payload = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator(schema).validate(payload)
    _check(payload["schema_sha256"] == _sha256(SCHEMA), "schema hash mismatch")
    prov = payload["provenance"]
    _check(prov["machinery_sha256"] == _sha256(HERE / "linearized_bach.py"), "machinery hash")
    _check(prov["engine_sha256"] == _sha256(ROOT / prov["engine_path"]), "engine hash")
    _check(prov["bh2a_certificate_sha256"] == _sha256(ROOT / prov["bh2a_certificate"]),
           "bh2a certificate hash")

    t, ph = sp.symbols("t phi")
    r = sp.Symbol("r", positive=True)
    x = sp.Symbol("x")
    m = sp.Symbol("m", positive=True)
    coords = [t, r, x, ph]
    B0 = 1 - 2 * m / r
    g0 = sp.diag(-B0, 1 / B0, r**2 / (1 - x**2), r**2 * (1 - x**2))
    geo0 = VbGeo(coords, g0)
    gi = geo0.ginv
    cancel = lambda e: sp.cancel(sp.together(e))  # noqa: E731
    P2 = (3 * x**2 - 1) / 2
    H0 = sp.Function("H0")(t, r)
    H1 = sp.Function("H1")(t, r)
    H2 = sp.Function("H2")(t, r)
    K = sp.Function("K")(t, r)
    h = sp.zeros(4, 4)
    h[0, 0] = B0 * H0 * P2
    h[0, 1] = h[1, 0] = H1 * P2
    h[1, 1] = H2 / B0 * P2
    h[2, 2] = g0[2, 2] * K * P2
    h[3, 3] = g0[3, 3] * K * P2
    lb = LinearizedBach(geo0)
    dB = lb.build(h)
    X = lb.dRic
    dRsc = lb.dRsc
    _check(sp.simplify(dRsc) != 0, "polar delta R zero")
    G = geo0.Gamma
    DX = [[[cancel(geo0.covd2(X, e, a, b)) for b in range(4)] for a in range(4)]
          for e in range(4)]

    def covd2X2(e, f, a, b):
        s = sp.diff(DX[f][a][b], coords[e])
        for hh in range(4):
            s -= (G[hh][e][f] * DX[hh][a][b] + G[hh][e][a] * DX[f][hh][b]
                  + G[hh][e][b] * DX[f][a][hh])
        return s

    boxX = sp.Matrix(4, 4, lambda a, b: cancel(
        sum(gi[e, f] * covd2X2(e, f, a, b) for e in range(4) for f in range(4)
            if gi[e, f] != 0)))
    Xup = sp.Matrix(4, 4, lambda c, d: cancel(
        sum(gi[c, e] * gi[d, f] * X[e, f] for e in range(4) for f in range(4))))
    CX = sp.Matrix(4, 4, lambda a, b: cancel(sp.together(
        sum(geo0.Weyl[a][c][b][d] * Xup[c, d] for c in range(4) for d in range(4)
            if Xup[c, d] != 0))))
    dR1 = [sp.diff(dRsc, coords[e]) for e in range(4)]
    DDR = sp.Matrix(4, 4, lambda a, b: cancel(
        sp.diff(dR1[a], coords[b]) - sum(G[hh][a][b] * dR1[hh] for hh in range(4))))
    boxR = cancel(sum(gi[e, f] * DDR[e, f] for e in range(4) for f in range(4)))
    for a in range(4):
        for b in range(a, 4):
            v = sp.simplify(sp.expand(cancel(sp.together(
                dB[a, b] - boxX[a, b] / 2 - CX[a, b]
                + DDR[a, b] / 6 + g0[a, b] * boxR / 12))))
            _check(v == 0, f"identity fails at ({a},{b})")
    print("BH2B_POLAR_SPLIT: all independent checks passed")


if __name__ == "__main__":
    verify_certificate()
