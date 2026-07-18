# Round-S4 ghost Schur zeta factorization

Dependency tags: `EUCLIDEAN-SPECTRAL`.

On the primed scalar harmonic carrier `ell >= 2`, set

```text
Q = Delta_0
A = Delta_0 - 4
B = Delta_0 - 6
S_L = A B^-1.
```

All four operators commute on round unit `S4`.  The same-order
zeta/weighted determinant comparison therefore gives

```text
m_Q(A,B)
  = log det_zeta(A) - log det_zeta(B) - tr^Q log(A B^-1)
  = -(1/4)(4^2-6^2) Wres(Q^-2).
```

The scalar heat coefficient fixes

```text
Wres(Q^-2)
  = 2 Res_(s=2) zeta_Q(s)
  = 2 Vol(S4)/(4 pi)^2
  = 1/3,
```

so the exact local factorization defect is

```text
m_Q(A,B) = 5/3.
```

Combining it with the already certified weighted modified determinant gives

```text
log det_zeta(Delta_0-4) - log det_zeta(Delta_0-6)
  = -2.311478818948744960808728888139320253915499526632223505...
```

An independent Hurwitz-zeta continuation of both shifted spectra reproduces
the value.  The absent constant-gradient row and the five `ell=1`
conformal-Killing ghost zero modes remain deleted.

This closes only the declared round-`S4` zeta factorization.  On a generic
background `[Q,S_L(W)]` need not vanish.  Its local factorization defect needs
the order-minus-three and order-minus-four BCH symbols of
`log(Q S_L)-log Q-log S_L` for a frozen factorization and cuts.  The generic
finite weighted rows are a separate global gate requiring a full primed
Green kernel or spectral measure.  Neither gate supplies the physical
fourth-order Hessian, complete `Gamma1/Q1`, or any Lorentzian result.

Machine certificate:
[`ROUND_S4_GHOST_SCHUR_ZETA_FACTORIZATION.json`](../spectral/euclidean/certificates/ROUND_S4_GHOST_SCHUR_ZETA_FACTORIZATION.json).
