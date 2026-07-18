# Generic-background ghost Schur Wodzicki residue

Status: `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`.

This certificate closes the canonical local-residue part of the normalized
longitudinal ghost Schur determinant.  Write

```text
S_L = I + K,
K = -(1/3) B1 + (1/3) B2 + O(Psi^-6).
```

In four dimensions, only `B1` and `B2` can contribute to a Wodzicki
residue.  Cyclicity reduces the first row to

```text
Wres(B1) = Wres((delta W d) Delta_0^-2).
```

For the positive scalar Laplacian, the mixed heat kernel gives

```text
Tr((delta W d) exp(-t Delta_0))
 = (4 pi t)^-2 integral W^mn
   [g_mn/(2t) - Ric_mn/6 + g_mn R/12 + O(t)].
```

The order-two heat/residue normalization therefore yields

```text
Wres(B1) = (4 pi)^-2 integral
  [-W.Ric/3 + (tr W)R/6].
```

The second row needs only its principal symbol:

```text
sigma_-4(B2) = <xi,W^2 xi>/|xi|^6,
Wres(B2) = (4 pi)^-2 integral tr(W^2)/2.
```

With `W=-2 Ric`, the exact result is

```text
Wres(K) = (4 pi)^-2 integral [R^2 + 4 Ric^2]/9.
```

Combining it with the previously certified

```text
Wres(K^2) = (4 pi)^-2 integral [R^2 + 2 Ric^2]/27
```

gives

```text
Wres(log S_L)
 = (4 pi)^-2 integral [5 R^2 + 22 Ric^2]/54.
```

The exact Einstein specialization supplies a separate check.  There

```text
S_L = (Delta_0-R/3)/(Delta_0-R/2),
K = (R/6)(Delta_0-R/2)^-1,
```

and the standard scalar heat coefficient gives `Wres(K)=2R^2/9`, exactly the
restriction of the generic formula.

A second check takes a covariantly constant isotropic endomorphism `W=w I`.
Then `B1=w Delta_0^-1`, whose scalar residue is `wR/3`; the general `B1`
formula gives `-wR/3+4wR/6=wR/3` exactly.

The independent verifier reconstructs the coefficients from the mixed heat
kernel and sphere second moment without calling the producer.  It also
mutates the `-Ric/6` coincidence coefficient and requires the Einstein check
to fail.

This does not compute the renormalized finite value `R(K)`, the finite part of
`R(K^2)`, a reference-specific pole or scale coefficient, or a zeta
multiplicative anomaly.  It also does not supply the physical fourth-order
Hessian, complete `Gamma1/Q1`, residual transfer, or any Lorentzian or state
claim.

Replay:

```bash
PYTHONPATH=quantum-weyl python3 -m \
  spectral.euclidean.generic_background_ghost_schur_wodzicki_residue \
  --emit --check
PYTHONPATH=quantum-weyl python3 -m \
  spectral.euclidean.verify_generic_background_ghost_schur_wodzicki_residue
PYTHONPATH=quantum-weyl pytest -q \
  quantum-weyl/spectral/euclidean/tests/test_generic_background_ghost_schur_wodzicki_residue.py
```
