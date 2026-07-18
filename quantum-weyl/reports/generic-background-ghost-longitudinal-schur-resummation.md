# Generic ghost longitudinal Schur resummation

Dependency tags: `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`.

## Result

The three previously separate longitudinal carriers are not independent
analytic kernels.  On the primed nonzero-mode domain, write

```text
F = -Box I + Ric,
W = -2 Ric,
A = F + W,
H = A + (1/2) d delta,
H0 = F + (1/2) d delta.
```

The Hodge Ward identities

```text
F d = d Delta0,
delta F = Delta0 delta,
delta d = Delta0
```

give the normalized scalar Schur operator

```text
S_L(W) = (2/3) I + (1/3) delta (F+W)^-1 d.
```

For one common determinant-class relative prescription, the matrix
determinant lemma yields

```text
Det_rel(H,H0)
  = Det_rel(F+W,F) Det_F(S_L(W),I).
```

Thus the pure-vector determinant and every longitudinal insertion combine
into one minimal-vector relative determinant and one scalar order-zero Schur
relative determinant.  Three dedicated `D_W=delta W d` evaluations are no
longer the correct architecture.

## Exact trace-log expansion

Define

```text
B_n = Delta0^-1 delta W (G_F W)^(n-1) d Delta0^-1.
```

Then

```text
S_L = I + sum_(n>=1) (-1)^n B_n/3,
```

and through cubic order

```text
W^1: -(1/3) Tr(B1)

W^2: +(1/3) Tr(B2)
     -(1/18) Tr(B1^2)

W^3: -(1/3) Tr(B3)
     +(1/9) Tr(B1 B2)
     -(1/81) Tr(B1^3).
```

The first three rows reproduce exactly the formerly open
`N1_LONGITUDINAL_SCALAR`, `N2_VECTOR_LONGITUDINAL`, and
`N2_LONGITUDINAL_LONGITUDINAL` carriers.  The cubic longitudinal weights are
therefore fixed to `(-1/3,1/9,-1/81)`.

## Einstein regression

For `Ric=(R/4)g`, hence `W=-(R/2)I`, the minimal-vector longitudinal ratio is

```text
(Delta0-R/2)/Delta0,
```

while the normalized Schur factor is

```text
(Delta0-R/3)/(Delta0-R/2).
```

Their product is `(Delta0-R/3)/Delta0`, reproducing the accepted scalar ghost
factor `Delta0-R/3` without fitting a background coefficient.

## Regularization boundary

The finite-dimensional determinant identity and formal trace-log series are
exact.  However, `S_L-I` starts at pseudodifferential order `-2` in four
dimensions, which does not by itself put it in ordinary trace class.  A
regularized relative determinant or equivalent common trace regulator is
therefore required on a generic background.  If the operators become
determinant class on a more restrictive domain, the ordinary Fredholm formula
applies.  For separately zeta-regularized factors, multiplicativity can also
acquire a local multiplicative anomaly.  That local term is not evaluated
here.  It cannot change the conclusion that the nonlocal longitudinal
trace-log towers are one Schur series, but it can shift local counterterm
coordinates and must be retained in any coefficient calculation.

Consequently this result does **not** compute the generic longitudinal form
factors, all five ghost functions, the physical fourth-order Hessian,
complete `Gamma1` or `Q1`, residual transfer, or a Lorentzian QME.

## Independent checks

The producer uses an exact noncommuting `4 x 4` vector/`2 x 2` scalar fixture.
The verifier uses a distinct `5 x 5` vector/`3 x 3` scalar fixture and checks:

- all three Hodge Ward identities;
- the finite determinant identity;
- equality of the direct nonminimal trace log with the vector plus Schur
  series through cubic order;
- the Einstein specialization;
- dependency hashes and the strict schema;
- rejection of the mutation `1/9 -> 1/8` in the mixed cubic term;
- fail-closed zeta, form-factor, `Gamma1/Q1`, transfer, and Lorentzian flags.

Replay with:

```bash
PYTHONPATH=quantum-weyl python3 -m \
  spectral.euclidean.generic_background_ghost_longitudinal_schur_resummation --check
PYTHONPATH=quantum-weyl python3 -m \
  spectral.euclidean.verify_generic_background_ghost_longitudinal_schur_resummation
PYTHONPATH=quantum-weyl pytest -q \
  quantum-weyl/spectral/euclidean/tests/test_generic_background_ghost_longitudinal_schur_resummation.py
```

The next coefficient-bearing gate is the normalized Schur relative
determinant kernel, together with the same-gauge generic physical fourth-order
Hessian kernel.
