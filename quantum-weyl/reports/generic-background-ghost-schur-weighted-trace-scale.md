# Generic-background ghost Schur weighted-trace scale

Dependency tags: `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`.

## Declared regulator

On the primed scalar ghost space choose the positive elliptic weight

```text
Q = Delta_0 + Pi_0,     ord(Q)=2,
Q_mu = Q / mu^2.
```

The smoothing projector only makes the weight invertible; it changes no
Wodzicki residue.  Define

```text
R_mu(A) = FP_[z=0] TR'[A (Q/mu^2)^(-z)].
```

For any classical pseudodifferential `A`, the weighted-trace Laurent row is

```text
TR'(A Q^(-z)) = Wres(A)/(2z) + R_Q(A) + O(z).
```

Because `(Q/mu^2)^(-z)=mu^(2z) Q^(-z)`, exact multiplication of the Laurent
series gives

```text
R_(exp(t)mu)(A) - R_mu(A) = t Wres(A).
```

The order two of the weight and the square on the dimensionful scale are both
load-bearing.  The independent verifier mutates `mu^2` to `mu` and rejects
the resulting factor of one half.

## Pole and scale rows

The already certified residues therefore imply

```text
Res_[z=0] TR'(K Q^(-z))
  = (4 pi)^-2 integral [R^2+4 Ric^2]/18,

Res_[z=0] TR'(K^2 Q^(-z))
  = (4 pi)^-2 integral [R^2+2 Ric^2]/54.
```

For the renormalized Schur split

```text
log Det_(3,R_mu)(I+K)
  = R_mu(K) - (1/2)R_mu(K^2) + log det_3(I+K),
```

the canonical tail is scale independent and

```text
d/dlog(mu) log Det_(3,R_mu)(S_L)
  = Wres(log S_L)
  = (4 pi)^-2 integral [5 R^2+22 Ric^2]/54.
```

Equivalently,

```text
log Det_(3,R_mu1)(S_L) - log Det_(3,R_mu0)(S_L)
  = log(mu1/mu0) Wres(log S_L).
```

This is the reference-specific scale conversion that was previously open.
It fixes neither `R_mu0(K)` nor the finite part of `R_mu0(K^2)`.  Those are
global, weight-dependent constants at the reference scale.  A local
multiplicative anomaly can also remain if the determinant is separately
factorized instead of regulated through this common Schur weight.

## Verification

```bash
PYTHONPATH=quantum-weyl python3 -m \
  spectral.euclidean.generic_background_ghost_schur_weighted_trace_scale \
  --emit --check
PYTHONPATH=quantum-weyl python3 -m \
  spectral.euclidean.verify_generic_background_ghost_schur_weighted_trace_scale
PYTHONPATH=quantum-weyl pytest -q \
  quantum-weyl/spectral/euclidean/tests/test_generic_background_ghost_schur_weighted_trace_scale.py
```

The next coefficient gate is the reference-scale finite pair
`R_mu0(K), FP R_mu0(K^2)` and the local multiplicative term for any selected
factorized zeta prescription, followed by combination with the same-gauge
generic physical fourth-order Hessian.
