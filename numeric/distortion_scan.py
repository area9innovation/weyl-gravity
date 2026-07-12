#!/usr/bin/env python3
"""Numerical test of the minimum-distortion conjecture (direction A).

Conjecture: over the solution coset S = S_+ C(th1, th2), C in SO(2,C)^2,
    F(S) = || log(S^dag S) ||_F^2  >=  4 r^2 = F(S_+),
with equality characterized (candidate: C unitary).

This script:
  1. evaluates F on random complex angles (broad scan);
  2. runs local minimization from many starts;
  3. checks the equality set: F on real angles, imaginary angles, axes;
  4. reports the log-eigenvalue pairs (x1, x2) of S^dag S to test the
     stronger conjecture x1, x2 >= r separately.
Everything in float; exactness not needed for a truth test.
"""

import numpy as np
from scipy.optimize import minimize

def build(gamma, w1, w2):
    t = w1 / w2
    r = np.log((w1 + w2) / (w1 - w2))
    c, s = np.cosh(r / 2), np.sinh(r / 2)
    B = np.zeros((4, 4), dtype=complex)
    B[0, 3] = 1j; B[1, 2] = 1j; B[2, 1] = -1j; B[3, 0] = -1j
    Sp = c * np.eye(4) + s * B
    P1 = np.diag([1, 0, 1, 0]).astype(complex)
    P2 = np.diag([0, 1, 0, 1]).astype(complex)
    X1 = np.zeros((4, 4), dtype=complex); X1[0, 2] = w2;    X1[2, 0] = -1 / w2
    X2 = np.zeros((4, 4), dtype=complex); X2[1, 3] = 1 / w1; X2[3, 1] = -w1
    return r, Sp, P1, P2, X1, X2

def C_of(th1, th2, P1, P2, X1, X2):
    return (np.cos(th1) * P1 + np.sin(th1) * X1 +
            np.cos(th2) * P2 + np.sin(th2) * X2)

def F_and_logs(Sp, C):
    S = Sp @ C
    P = S.conj().T @ S
    ev = np.linalg.eigvalsh(P)
    logs = np.log(ev)
    return float(np.sum(logs ** 2)), np.sort(logs)

def run(gamma, w1, w2, n_scan=20000, n_opt=60, seed=0):
    rng = np.random.default_rng(seed)
    r, Sp, P1, P2, X1, X2 = build(gamma, w1, w2)
    F0 = 4 * r ** 2

    def F(v):
        th1 = v[0] + 1j * v[1]; th2 = v[2] + 1j * v[3]
        return F_and_logs(Sp, C_of(th1, th2, P1, P2, X1, X2))[0]

    # broad scan
    best_scan = np.inf; best_v = None
    for _ in range(n_scan):
        v = rng.uniform(-2.5, 2.5, 4)
        f = F(v)
        if f < best_scan:
            best_scan, best_v = f, v.copy()

    # local minimization from many starts (incl. best scan point and origin-ish)
    best_opt = np.inf; best_vo = None
    starts = [best_v, np.zeros(4)] + [rng.uniform(-2, 2, 4) for _ in range(n_opt)]
    for v0 in starts:
        res = minimize(F, v0, method="Nelder-Mead",
                       options=dict(xatol=1e-12, fatol=1e-14, maxiter=8000))
        if res.fun < best_opt:
            best_opt, best_vo = res.fun, res.x

    # equality-set probes
    f_real = F([0.7, 0, -1.1, 0])                # real angles (non-unitary in coords)
    f_realb = F([0.3, 0, 0.4, 0])
    f_imag = F([0, 0.5, 0, 0])                    # hyperbolic
    f_pi = F([np.pi, 0, np.pi, 0])                # C = -I

    # stronger conjecture: x-pairs at random points
    xmin_minus_r = []
    for _ in range(4000):
        v = rng.uniform(-2, 2, 4)
        th1 = v[0] + 1j * v[1]; th2 = v[2] + 1j * v[3]
        _, logs = F_and_logs(Sp, C_of(th1, th2, P1, P2, X1, X2))
        x1, x2 = logs[3], logs[2]     # two largest (pairs are +-)
        xmin_minus_r.append(min(x1, x2) - r)
    xmin_minus_r = np.array(xmin_minus_r)

    print(f"(gamma,w1,w2)=({gamma},{w1},{w2})  r={r:.6f}  F0=4r^2={F0:.8f}")
    print(f"  scan min F  = {best_scan:.8f}   (>= F0? {best_scan >= F0 - 1e-9})")
    print(f"  opt  min F  = {best_opt:.10f}  gap to F0 = {best_opt - F0:+.3e}  at v={np.round(best_vo,6)}")
    print(f"  F(real th)  = {f_real:.8f}, {f_realb:.8f}   (equality would mean real angles suffice)")
    print(f"  F(imag th)  = {f_imag:.8f}   F(C=-I) = {f_pi:.8f}")
    print(f"  stronger conj min(x_i) - r : min over samples = {xmin_minus_r.min():+.6f} "
          f"(negative => some x_i < r occurs)")
    return best_opt, F0

if __name__ == "__main__":
    for params in [(1.0, 2.0, 1.0), (1.5, 5.0, 2.0), (1.0, 1.05, 1.0), (0.7, 10.0, 9.5)]:
        run(*params)
        print()
