# Channel-factorized fundamental-symmetry pullback test

This package separates an exact finite-dimensional theorem from the present
physical-data availability.

For Hermitian forms
\[
G=G_-,\qquad K_H=A^\dagger H_{\mathcal H^+}A,\qquad
K_+=G-K_H,\qquad L_H=G^{-1}K_H,
\]
with \(A=T_-^{-1}\), the theorem states that a common incoming fundamental
symmetry inducing positive, channel-separated horizon and outgoing metrics
exists exactly when \(L_H\) is diagonalizable and
\(\operatorname{spec}L_H\subset(0,1)\).  The statement assumes the incoming,
horizon, and outgoing forms are nondegenerate and that \(T_-\) and \(T_+\)
are invertible, so the two channel pullbacks are genuine congruences.

The physical audit is fail closed.  The incoming Gram and future-horizon Gram
are exact, and the outgoing cell certifies \(T_+\in GL(3,\mathbb C)\).
However, the committed transport-free authority explicitly records that the
full typed entries of \(T_-\) are unavailable.  Its determinant, existence,
and invertibility do not determine \(K_H\).  Consequently the physical
generalized eigenvalues are not yet defined by certified data.

Run:

```bash
python3 -m black_hole_programme.phase4.channel_factorized_c_pullback_test_v1.produce
python3 -m black_hole_programme.phase4.channel_factorized_c_pullback_test_v1.verify
python3 -m unittest -v black_hole_programme.phase4.channel_factorized_c_pullback_test_v1.test_pullback
```

Dependency tags: `REDUCED-MODE`, `LORENTZIAN-CAUSAL`.
