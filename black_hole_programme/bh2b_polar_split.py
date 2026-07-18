"""BH-2B stage 1: general branch-split identity including the polar sector.

Fail-closed builder for
`black_hole_programme/certificates/BH2B_POLAR_SPLIT.json`.

Verdict: BH2B_GENERAL_BRANCH_SPLIT_IDENTITY_CLASSIFIED.

Exact result (Schwarzschild, symbolic m, polar l=2 RW-gauge perturbation
with four radial functions H0, H1, H2, K; rational chart x = cos theta):

    delta B_ab = (1/2) Box (delta Ric)_ab + C_acbd (delta Ric)^{cd}
                 - (1/6) nabla_a nabla_b (delta R)
                 - (1/12) g_ab Box (delta R),

componentwise, with universal constants (1/2, 1, -1/6, -1/12).  The
certified axial identity (BH2A_AXIAL_OPERATOR) is the delta R = 0 special
case.  Consequences: the Einstein branch (delta Ric = 0) injects exactly
into the Bach kernel in the polar sector as well, and the polar extra
branch is governed by the second-order trace-coupled Lichnerowicz system
on (psi_ab, delta R) = (delta Ric_ab, delta R).

NOT claimed: the Zerilli reduction benchmark, polar horizon reach and
asymptotics, polar flux blocks, causal disposition of the polar extra
branch, general l, or any stability/ringdown statement.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path

import sympy as sp

from linearized_bach import LinearizedBach
from weyl_geometry import Geometry

ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
DEFAULT_OUTPUT = HERE / "certificates" / "BH2B_POLAR_SPLIT.json"
SCHEMA_PATH = HERE / "schema" / "bh2b-polar-split-v1.schema.json"
BH2A_CERT = HERE / "certificates" / "BH2A_AXIAL_OPERATOR.json"

SCHEMA_NAME = "pure-weyl-bh2b-polar-split-v1"
RESULT_ID = "PURE_WEYL_BH2B_POLAR_SPLIT"
RESULT_TOKEN = "BH2B_GENERAL_BRANCH_SPLIT_IDENTITY_CLASSIFIED"


class PolarSplitError(RuntimeError):
    pass


def _require(cond: bool, msg: str) -> None:
    if not cond:
        raise PolarSplitError(msg)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_certificate() -> dict:
    t0_all = time.time()
    t, ph = sp.symbols("t phi")
    r = sp.Symbol("r", positive=True)
    x = sp.Symbol("x")
    m = sp.Symbol("m", positive=True)
    coords = [t, r, x, ph]
    B0 = 1 - 2 * m / r
    g0 = sp.diag(-B0, 1 / B0, r**2 / (1 - x**2), r**2 * (1 - x**2))
    geo0 = Geometry(coords, g0)
    gi = geo0.ginv
    cancel = lambda e: sp.cancel(sp.together(e))  # noqa: E731
    receipts = {}

    t0 = time.time()
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
    _require(sp.simplify(dRsc) != 0, "polar delta R unexpectedly zero")
    receipts["polar_rows"] = round(time.time() - t0, 1)

    t0 = time.time()
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
    receipts["basis"] = round(time.time() - t0, 1)

    t0 = time.time()
    for a in range(4):
        for b in range(a, 4):
            v = sp.simplify(sp.expand(cancel(sp.together(
                dB[a, b] - boxX[a, b] / 2 - CX[a, b]
                + DDR[a, b] / 6 + g0[a, b] * boxR / 12))))
            _require(v == 0, f"general split identity fails at ({a},{b})")
    receipts["identity"] = round(time.time() - t0, 1)
    receipts["total"] = round(time.time() - t0_all, 1)

    certificate = {
        "schema": SCHEMA_NAME,
        "schema_path": str(SCHEMA_PATH.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA_PATH),
        "result_id": RESULT_ID,
        "result_token": RESULT_TOKEN,
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "declaration": {
            "theory": "pure-Weyl gravity L = alpha C_abcd C^abcd",
            "background_family": "Schwarzschild (symbolic m)",
            "conformal_frame": "working gauge; rational chart x = cos theta",
            "generator": "none; operator-level identity",
            "phase_space": "polar l = 2 RW-gauge perturbations (H0, H1, H2, K)",
            "horizon_condition": "none imposed",
            "infinity_condition": "none imposed",
            "lifecycle": "CLASSIFIED",
        },
        "identity": {
            "statement": "delta B_ab = (1/2) Box(delta Ric)_ab + C_acbd (delta Ric)^{cd} - (1/6) nabla_a nabla_b(delta R) - (1/12) g_ab Box(delta R), componentwise on the Ricci-flat background",
            "constants": {"box_ric": "1/2", "weyl_coupling": "1", "grad_grad_R": "-1/6", "g_box_R": "-1/12"},
            "axial_consistency": "the certified axial identity (BH2A_AXIAL_OPERATOR) is the delta R = 0 special case",
            "consequence": "the Einstein branch injects exactly into the Bach kernel in the polar sector; the polar extra branch is the second-order trace-coupled Lichnerowicz system on (delta Ric_ab, delta R)",
        },
        "claim_flags": {
            "polar_rows_certified": True,
            "general_split_identity_certified": True,
            "axial_special_case_consistent": True,
            "zerilli_benchmark_certified": False,
            "polar_horizon_reach_certified": False,
            "polar_flux_blocks_certified": False,
            "polar_causal_disposition_decided": False,
            "general_l_certified": False,
            "stability_or_ringdown_certified": False,
        },
        "missing_objects": [
            "Zerilli master-equation reproduction (polar literature anchor)",
            "polar extra-carrier horizon reach and asymptotics",
            "polar flux blocks and Lee-Wald signs",
            "polar causal disposition; general l",
            "any stability or ringdown statement",
        ],
        "stage_seconds": receipts,
        "provenance": {
            "generator_path": "black_hole_programme/bh2b_polar_split.py",
            "machinery_path": "black_hole_programme/linearized_bach.py",
            "machinery_sha256": _sha256(HERE / "linearized_bach.py"),
            "engine_path": "black_hole_programme/weyl_geometry.py",
            "engine_sha256": _sha256(HERE / "weyl_geometry.py"),
            "bh2a_certificate": str(BH2A_CERT.relative_to(ROOT)),
            "bh2a_certificate_sha256": _sha256(BH2A_CERT),
        },
        "verification_command": "python3 black_hole_programme/verify_bh2b_polar_split.py",
    }
    return certificate


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    certificate = build_certificate()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(certificate, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
