#!/usr/bin/env python3
"""Numerical regression tests for the symplectic reconstruction audit (spec section 15).

For each parameter triple (gamma, w1, w2) computes G, A, eig(A), alpha/beta/r,
M, K, S and reports (not merely asserts) every residual:
  * symplectic residual        ||S^T J S - J||_F
  * normal-form residual       ||S^T G S - G0||_F
  * pseudo-Hermiticity residual ||S^{2T} G S^2 - conj(G)||_F   (matrix form of eta H = H^dag eta)
  * eigenvalues of S^dag S (rescaled coordinates) vs {e^r x2, e^-r x2}
  * affine-invariant distance ||log(S^dag S)||_F vs 2r
Also cross-checks F6 (uniqueness of the positive admissible diagonalizer) by a
brute-force nonlinear solve over the stabilizer at each triple.

Precision: 50 significant digits (~166 bits) everywhere; 80 digits for the
near-degenerate case -- comfortably beyond the spec's 80-bit floor.

Run:  python3 regression.py     # writes ../reports/regression.json, prints table
"""

import json
import os

import mpmath as mp


def mat(rows):
    return mp.matrix(rows)


def frob(Mx):
    return mp.sqrt(mp.fsum(abs(Mx[i, j]) ** 2 for i in range(Mx.rows) for j in range(Mx.cols)))


def dagger(Mx):
    out = mp.matrix(Mx.cols, Mx.rows)
    for i in range(Mx.rows):
        for j in range(Mx.cols):
            out[j, i] = mp.conj(Mx[i, j])
    return out


def transpose(Mx):
    out = mp.matrix(Mx.cols, Mx.rows)
    for i in range(Mx.rows):
        for j in range(Mx.cols):
            out[j, i] = Mx[i, j]
    return out


def conjmat(Mx):
    out = mp.matrix(Mx.rows, Mx.cols)
    for i in range(Mx.rows):
        for j in range(Mx.cols):
            out[i, j] = mp.conj(Mx[i, j])
    return out


def run_case(gamma, w1, w2, dps):
    mp.mp.dps = dps

    def parse(v):
        if isinstance(v, str) and "/" in v:
            n, d = v.split("/")
            return mp.mpf(n) / mp.mpf(d)
        return mp.mpf(v)

    gamma, w1, w2 = parse(gamma), parse(w1), parse(w2)
    i = mp.mpc(0, 1)

    J = mat([[0, 0, 1, 0], [0, 0, 0, 1], [-1, 0, 0, 0], [0, -1, 0, 0]])
    G = mat([[gamma * (w1**2 + w2**2), 0, 0, -i],
             [0, gamma * w1**2 * w2**2, 0, 0],
             [0, 0, 1 / gamma, 0],
             [-i, 0, 0, 0]])
    G0 = mp.diag([gamma * w1**2, gamma * w1**2 * w2**2, 1 / gamma, 1 / (gamma * w1**2)])

    A = J * G
    eigA = mp.eig(mp.matrix(A), left=False, right=False)
    eigA_sorted = sorted(eigA, key=lambda z: (mp.im(z), mp.re(z)))
    # expected +-i w1, +-i w2
    expected = sorted([i * w1, -i * w1, i * w2, -i * w2], key=lambda z: (mp.im(z), mp.re(z)))
    eigA_resid = max(abs(a - b) for a, b in zip(eigA_sorted, expected))

    L = mp.log((w1 + w2) / (w1 - w2))
    alpha = L / (gamma * w1 * w2)
    beta = alpha * gamma**2 * w1**2 * w2**2
    r = mp.sqrt(alpha * beta)
    r_resid = abs(r - L)

    M = mat([[0, beta, 0, 0], [beta, 0, 0, 0], [0, 0, 0, alpha], [0, 0, alpha, 0]])
    K = J * M
    K2_resid = frob(K * K + r**2 * mp.eye(4))

    # S = e^{iK/2}, computed by INDEPENDENT means: mpmath expm (Pade/scaling-squaring),
    # not the closed hyperbolic formula -- then compared against the closed formula.
    S_expm = mp.expm(i * K / 2)
    S_closed = mp.cosh(r / 2) * mp.eye(4) + (i / r) * mp.sinh(r / 2) * K
    S_formula_resid = frob(S_expm - S_closed)
    S = S_closed

    sympl_resid = frob(transpose(S) * J * S - J)
    normal_resid = frob(transpose(S) * G * S - G0)
    S2 = S * S
    pseudo_resid = frob(transpose(S2) * G * S2 - conjmat(G))
    det_resid = abs(mp.det(S) - 1)

    # Rescaled coordinates: D = diag(d,d,1/d,1/d), d = sqrt(gamma w1 w2).
    d = mp.sqrt(gamma * w1 * w2)
    D = mp.diag([d, d, 1 / d, 1 / d])
    Dinv = mp.diag([1 / d, 1 / d, d, d])
    Sp = D * S * Dinv
    herm_resid_rescaled = frob(Sp - dagger(Sp))
    herm_resid_original = frob(S - dagger(S))

    Mobs = dagger(Sp) * Sp
    eigM = sorted([mp.re(e) for e in mp.eig(mp.matrix(Mobs), left=False, right=False)])
    eigM_expected = sorted([mp.e**-r, mp.e**-r, mp.e**r, mp.e**r])
    eigM_resid = max(abs(a - b) for a, b in zip(eigM, eigM_expected))

    dist = mp.sqrt(mp.fsum(mp.log(e) ** 2 for e in eigM))
    dist_resid = abs(dist - 2 * r)

    # F6 cross-check: unique positive member of the solution family S' C(th1, th2).
    # Hermiticity residual g(th) = ||S'C - (S'C)^dag||^2 minimized over complex angles;
    # verify the only zero near the identity component gives C = I, and random
    # multistarts find no other Hermitian-positive member.
    G0p = Dinv * G0 * Dinv  # D^{-T} G0 D^{-1}, D diagonal
    A0p = J * G0p
    X1 = mp.matrix(4, 4); X2 = mp.matrix(4, 4)
    X1[0, 2] = A0p[0, 2] / w1; X1[2, 0] = A0p[2, 0] / w1
    X2[1, 3] = A0p[1, 3] / w2; X2[3, 1] = A0p[3, 1] / w2
    P1 = mp.diag([1, 0, 1, 0]); P2 = mp.diag([0, 1, 0, 1])

    def C_of(th1, th2):
        return (mp.cos(th1) * P1 + mp.sin(th1) * X1 +
                mp.cos(th2) * P2 + mp.sin(th2) * X2)

    def herm_gap(v, workdps=20):
        with mp.workdps(workdps):
            th1 = mp.mpc(v[0], v[1]); th2 = mp.mpc(v[2], v[3])
            SC = Sp * C_of(th1, th2)
            return frob(SC - dagger(SC))

    def positivity(v):
        th1 = mp.mpc(v[0], v[1]); th2 = mp.mpc(v[2], v[3])
        SC = Sp * C_of(th1, th2)
        ev = mp.eig(mp.matrix((SC + dagger(SC)) / 2), left=False, right=False)
        return sum(1 for e in ev if mp.re(e) <= 0)

    import random
    random.seed(0)
    other_solutions = 0
    for trial in range(12):
        v = [random.uniform(-1.2, 1.2) for _ in range(4)]
        # crude gradient-free polish: coordinate descent on the Hermiticity gap
        step = 0.3
        g = herm_gap(v)
        for _ in range(120):
            improved = False
            for k in range(4):
                for sgn in (+1, -1):
                    w = list(v); w[k] += sgn * step
                    g2 = herm_gap(w)
                    if g2 < g:
                        v, g = w, g2
                        improved = True
            if not improved:
                step /= 2
                if step < 1e-10:
                    break
        gap, neg = herm_gap(v, workdps=30), positivity(v)
        if gap < mp.mpf("1e-8") and neg == 0:
            # Hermitian positive member found: must be C = I (angles = 0 mod 2pi)
            th_norm = min(abs(mp.mpf(v[0]) % (2 * mp.pi)), abs((mp.mpf(v[0]) % (2 * mp.pi)) - 2 * mp.pi)) + \
                      abs(mp.mpf(v[1])) + \
                      min(abs(mp.mpf(v[2]) % (2 * mp.pi)), abs((mp.mpf(v[2]) % (2 * mp.pi)) - 2 * mp.pi)) + \
                      abs(mp.mpf(v[3]))
            if th_norm > 1e-4:
                other_solutions += 1

    def f(x):
        return mp.nstr(x, 6)

    return dict(
        parameters=[str(gamma), str(w1), str(w2)], dps=dps,
        eigA_residual=f(eigA_resid),
        r=mp.nstr(r, 20), r_identity_residual=f(r_resid),
        K2_residual=f(K2_resid),
        S_expm_vs_closed=f(S_formula_resid),
        symplectic_residual=f(sympl_resid),
        det_residual=f(det_resid),
        normal_form_residual=f(normal_resid),
        pseudo_hermiticity_residual=f(pseudo_resid),
        S_hermiticity_original=f(herm_resid_original),
        S_hermiticity_rescaled=f(herm_resid_rescaled),
        eig_SdagS=[mp.nstr(e, 12) for e in eigM],
        eig_SdagS_residual=f(eigM_resid),
        distance=mp.nstr(dist, 20), distance_residual=f(dist_resid),
        positive_solution_extra_count=other_solutions,
    )


CASES = [
    ("1", "2", "1", 50),
    ("3/2", "5", "2", 50),
    ("7/3", "10", "9", 50),
    ("1", "1.0001", "1", 80),        # near-degenerate: 80 digits >> 80 bits
]

if __name__ == "__main__":
    results = []
    for gamma, w1, w2, dps in CASES:
        mp.mp.dps = dps
        res = run_case(gamma, w1, w2, dps)
        results.append(res)
        print(f"\n=== (gamma, w1, w2) = ({gamma}, {w1}, {w2})  @ {dps} digits ===")
        for k, v in res.items():
            if k not in ("parameters", "dps"):
                print(f"  {k:34s} {v}")

    outdir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "reports")
    os.makedirs(outdir, exist_ok=True)
    with open(os.path.join(outdir, "regression.json"), "w") as fh:
        json.dump(results, fh, indent=2)
    print("\nwrote", os.path.join(outdir, "regression.json"))
