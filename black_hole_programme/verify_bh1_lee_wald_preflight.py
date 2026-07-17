"""Structurally independent verifier for BH1_LEE_WALD_PREFLIGHT.

Independence from the producer stack (`weyl_geometry.py` + `lee_wald.py`):

- curvature comes from the verifier-side pipeline in
  `verify_bh0_background.py` (Schouten/Kulkarni--Nomizu route);
- the Iyer--Wald theta and Q assembly below is separate code;
- the GR normalization controls (Schwarzschild and Schwarzschild--de
  Sitter must give exactly 16 pi delta m) are re-run here, so a silent
  convention drift in either stack is caught.

The obstruction algebra (dF, kernel, Euler identity, pairings) is
recomputed from the certified charge expressions by plain calculus.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import jsonschema
import sympy as sp

import verify_bh0_background as vb

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
CERTIFICATE = HERE / "certificates" / "BH1_LEE_WALD_PREFLIGHT.json"
SCHEMA = HERE / "schema" / "bh1-lee-wald-preflight-v1.schema.json"

N = 4


class BH1VerifyError(AssertionError):
    pass


def _check(cond: bool, msg: str) -> None:
    if not cond:
        raise BH1VerifyError(msg)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _surface_F(coords, g, E_up_fn, psym, r, th, ph):
    """Independent assembly of Int_{S_r} (delta Q - i_chi theta), chi = d_t."""
    ginv, Gam, Ric, Rsc, C = vb.curvature(coords, g)

    class Geo:
        pass

    geo = Geo()
    geo.coords, geo.g, geo.ginv, geo.Gamma = coords, g, ginv, Gam
    geo.Weyl = C
    E = E_up_fn(geo)
    sqrtg = sp.sqrt(-g.det())
    dg = sp.Matrix(N, N, lambda i, j: sp.diff(g[i, j], psym))

    def covdg(e, b, c):
        s = sp.diff(dg[b, c], coords[e])
        for h in range(N):
            s -= Gam[h][e][b] * dg[h, c] + Gam[h][e][c] * dg[b, h]
        return s

    def covE(e, a, b, c, d):
        s = sp.diff(E[a][b][c][d], coords[e])
        for h in range(N):
            s += (Gam[a][e][h] * E[h][b][c][d] + Gam[b][e][h] * E[a][h][c][d]
                  + Gam[c][e][h] * E[a][b][h][d] + Gam[d][e][h] * E[a][b][c][h])
        return s

    theta_r = sp.Integer(0)
    for b in range(N):
        for c in range(N):
            for dd in range(N):
                if E[1][b][c][dd] != 0:
                    theta_r += 2 * E[1][b][c][dd] * covdg(dd, b, c)
                if dg[b, c] != 0:
                    theta_r -= 2 * dg[b, c] * covE(dd, 1, b, c, dd)
    chi_low = [g[d, 0] for d in range(N)]

    def nabla_chi(cc, dd):
        s = sp.diff(chi_low[dd], coords[cc])
        for h in range(N):
            s -= Gam[h][cc][dd] * chi_low[h]
        return s

    Q_tr = sp.Integer(0)
    for cc in range(N):
        for dd in range(N):
            if E[0][1][cc][dd] != 0:
                Q_tr -= E[0][1][cc][dd] * nabla_chi(cc, dd)
            if chi_low[dd] != 0:
                Q_tr += 2 * chi_low[dd] * covE(cc, 0, 1, cc, dd)
    q_form = sp.cancel(sp.together(2 * sqrtg * Q_tr))
    itheta = sp.cancel(sp.together(-sqrtg * theta_r))
    integrand = sp.cancel(sp.together(sp.diff(q_form, psym) - itheta))
    return sp.simplify(
        sp.integrate(sp.integrate(integrand, (th, 0, sp.pi)), (ph, 0, 2 * sp.pi))
    )


def _E_gr(geo):
    gi = geo.ginv
    return [[[[sp.cancel((gi[a, c] * gi[b, d] - gi[a, d] * gi[b, c]) / 2)
               for d in range(N)] for c in range(N)] for b in range(N)] for a in range(N)]


def _E_weyl(alpha):
    def make(geo):
        gi = geo.ginv
        C = geo.Weyl
        out = [[[[sp.Integer(0)] * N for _ in range(N)] for _ in range(N)] for _ in range(N)]
        for a in range(N):
            for b in range(N):
                for c in range(N):
                    for d in range(N):
                        s = sp.Integer(0)
                        for p in range(N):
                            for q in range(N):
                                for u in range(N):
                                    for v in range(N):
                                        w = gi[a, p] * gi[b, q] * gi[c, u] * gi[d, v]
                                        if w != 0:
                                            s += w * C[p][q][u][v]
                        out[a][b][c][d] = sp.cancel(2 * alpha * s)
        return out

    return make


def verify_certificate() -> None:
    payload = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator(schema).validate(payload)
    _check(payload["schema_sha256"] == _sha256(SCHEMA), "schema hash mismatch")
    prov = payload["provenance"]
    for key in ("machinery", "engine"):
        _check(
            prov[f"{key}_sha256"] == _sha256(ROOT / prov[f"{key}_path"]),
            f"{key} hash mismatch",
        )
    _check(
        prov["bh0_certificate_sha256"] == _sha256(ROOT / prov["bh0_certificate"]),
        "BH-0 certificate hash mismatch",
    )

    t, ph = sp.symbols("t phi")
    r, th = sp.symbols("r theta", positive=True)
    beta, gam, k, alpha = sp.symbols("beta gamma k alpha")
    m = sp.Symbol("m", positive=True)
    coords = [t, r, th, ph]
    SYM = {"beta": beta, "gamma": gam, "k": k, "alpha": alpha, "pi": sp.pi, "r": r}

    def _sym(s):
        return sp.sympify(s, locals=dict(SYM))

    def diag(B):
        return sp.diag(-B, 1 / B, r**2, r**2 * sp.sin(th) ** 2)

    # GR normalization controls, independent pipeline
    F = _surface_F(coords, diag(1 - 2 * m / r), _E_gr, m, r, th, ph)
    _check(sp.simplify(F - 16 * sp.pi) == 0, f"GR Schwarzschild control: {F}")
    F = _surface_F(coords, diag(1 - 2 * m / r - k * r**2), _E_gr, m, r, th, ph)
    _check(sp.simplify(F - 16 * sp.pi) == 0, f"GR S-dS control: {F}")

    # Weyl charges on the MK family, independent pipeline
    MK = 1 - 3 * beta * gam - beta * (2 - 3 * beta * gam) / r + gam * r - k * r**2
    stored = {
        beta: _sym(payload["bare_charges"]["F_beta"]),
        gam: _sym(payload["bare_charges"]["F_gamma"]),
        k: _sym(payload["bare_charges"]["F_k"]),
    }
    for psym, expect in stored.items():
        Fp = _surface_F(coords, diag(MK), _E_weyl(alpha), psym, r, th, ph)
        _check(r not in Fp.free_symbols, f"charge {psym} r-dependent: {Fp}")
        _check(sp.simplify(Fp - expect) == 0, f"charge {psym} mismatch: {Fp} vs {expect}")

    # obstruction algebra from the stored charges
    ps = [beta, gam, k]
    Fvec = [stored[beta], stored[gam], stored[k]]
    dF = {
        (i, j): sp.simplify(sp.diff(Fvec[j], ps[i]) - sp.diff(Fvec[i], ps[j]))
        for i in range(3)
        for j in range(i + 1, 3)
    }
    _check(
        sp.simplify(dF[(0, 1)] - _sym(payload["integrability_obstruction"]["dF_beta_gamma"])) == 0
        and sp.simplify(dF[(0, 2)] - _sym(payload["integrability_obstruction"]["dF_beta_k"])) == 0
        and sp.simplify(dF[(1, 2)] - _sym(payload["integrability_obstruction"]["dF_gamma_k"])) == 0,
        "stored dF mismatch",
    )
    _check(any(v != 0 for v in dF.values()), "dF unexpectedly zero")
    gen_c = [-3 * beta**2, 6 * beta * gam - 2, gam]
    gen_l = [-beta, gam, 2 * k]

    def iota(V):
        out = []
        for j in range(3):
            s = sp.Integer(0)
            for i in range(3):
                if i < j:
                    s += V[i] * dF[(i, j)]
                elif i > j:
                    s -= V[i] * dF[(j, i)]
            out.append(sp.simplify(s))
        return out

    _check(all(e == 0 for e in iota(gen_c)), "gen_c not in ker dF")
    _check(
        all(sp.simplify(a - b) == 0 for a, b in zip(iota(gen_l), Fvec)),
        "Euler identity fails",
    )
    _check(sp.simplify(sum(f * v for f, v in zip(Fvec, gen_c))) == 0, "F(gen_c) != 0")
    _check(sp.simplify(sum(f * v for f, v in zip(Fvec, gen_l))) == 0, "F(gen_lambda) != 0")
    # kernel is exactly 1-dimensional: the 3x3 antisymmetric matrix has rank 2
    M = sp.zeros(3, 3)
    for (i, j), val in dF.items():
        M[i, j] = val
        M[j, i] = -val
    _check(M.rank() == 2, "dF does not have rank 2")

    # fixture and subfamily values
    fx = {beta: sp.Rational(3, 2), gam: sp.Rational(12, 19), k: sp.Rational(1, 19)}
    hf = payload["horizon_fixture_charges"]
    for name, psym in (("F_beta", beta), ("F_gamma", gam), ("F_k", k)):
        _check(
            sp.simplify(stored[psym].subs(fx) - _sym(hf[name])) == 0,
            f"fixture {name} mismatch",
        )
    obs = payload["einstein_subfamily_observations"]
    _check(
        sp.simplify(stored[k].subs({gam: 0}) - _sym(obs["k_pairing_at_schwarzschild"])) == 0,
        "k pairing at Schwarzschild mismatch",
    )
    _check(
        sp.simplify(stored[gam].subs({gam: 0}) - _sym(obs["extra_branch_variation_charged"])) == 0,
        "extra-branch variation charge mismatch",
    )
    _check(
        sp.simplify(stored[beta].subs({gam: 0, k: 0})) == 0,
        "Schwarzschild mass charge not zero",
    )

    # nontriviality witness is genuinely r-dependent
    _check(
        r in _sym(payload["bare_charges"]["nontriviality_witness"]).free_symbols,
        "stored nontriviality witness is r-independent",
    )

    print("BH1_LEE_WALD_PREFLIGHT: all independent checks passed")


if __name__ == "__main__":
    verify_certificate()
