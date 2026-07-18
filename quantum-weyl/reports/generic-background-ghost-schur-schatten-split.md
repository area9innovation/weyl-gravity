# Generic ghost Schur Schatten split and critical residue

Dependency tags: `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`.

## Result

Write the normalized longitudinal scalar Schur factor as

```text
S_L = I + K,
K = -(1/3) delta (F+W)^-1 W d Delta0^-1,
W = -2 Ric.
```

On a closed compact four-manifold, with the primed zero-mode complement and
elliptic inverses fixed, `K` is a classical scalar pseudodifferential operator
of order `-2`. Its singular values obey

```text
s_j(K) = O(j^-1/2).
```

Consequently `K` belongs to every Schatten ideal `S_p` with `p>2`, in
particular `S_3`. It is not generically trace class merely from this order.
The powers have the sharp dispositions

```text
K^2 : order -4, critical weak trace class in dimension four;
K^3 : order -6, ordinary trace class.
```

The canonical third modified Fredholm determinant is therefore defined:

```text
det_3(I+K) = det[(I+K) exp(-K+K^2/2)].
```

For sufficiently small norm its logarithm is

```text
log det_3(I+K)
  = sum_(m>=3) (-1)^(m+1) Tr(K^m)/m.
```

Thus a local trace prescription `R` enters only through

```text
log Det_(3,R)(I+K)
  = R(K) - (1/2) R(K^2) + log det_3(I+K).
```

This identifies the exact analytic division of labor. The tail is a genuine
modified Fredholm determinant. The first two trace rows still require a
common regulator, and a separately factorized zeta prescription can carry a
local multiplicative anomaly.

## Curvature expansion

With

```text
K1 = -B1/3,
K2 =  B2/3,
K3 = -B3/3,
```

the split reproduces the certified Schur series through cubic order:

```text
W^1: -(1/3) R(B1)

W^2: +(1/3) R(B2)
     -(1/18) R(B1^2)

W^3: -(1/3) R(B3)
     +(1/9) R(B1 B2)
     -(1/81) Tr(B1^3).
```

Only the last cubic row is already in the canonical `det_3` tail. The
`R(B3)` and `R(B1 B2)` rows remain part of the regulated trace extension.
The split therefore does not silently promote the complete cubic form
factor.

## Critical local residue

The principal symbol is

```text
sigma_-2(K) = -(1/3) <xi,W xi> / |xi|^4.
```

Since `K^2` has critical order `-4`, only the square of this principal symbol
contributes to its Wodzicki residue. Using

```text
Vol(S^3) = 2 pi^2,
E[n_i n_j n_k n_l]
  = (delta_ij delta_kl + delta_ik delta_jl + delta_il delta_jk)/24,
```

gives, in the certificate's residue convention,

```text
Wres(K^2)
  = (4 pi)^-2 integral [(tr W)^2 + 2 tr(W^2)] / 108
  = (4 pi)^-2 integral [R^2 + 2 Ric_mn Ric^mn] / 27.
```

On the declared scalar-flat carrier this reduces to

```text
Wres(K^2)
  = (4 pi)^-2 integral [2 Ric_mn Ric^mn] / 27.
```

This is the first local coefficient extracted directly from the normalized
Schur factor. It is a residue, not yet the coefficient of a particular zeta
pole or scale logarithm. That conversion depends on the order of the chosen
reference operator and the trace normalization and remains fail-closed.

## What remains

The exact missing analytic rows are now:

- the regulated value and local residue of `R(K)`;
- the finite part of `R(K^2)`;
- any multiplicative anomaly of the selected factorized zeta prescription;
- the same-gauge generic physical fourth-order Hessian kernel.

The result does not compute the complete Schur determinant, the five
repository form-factor functions, `Gamma1`, `Q1`, residual transfer, or a
Lorentzian QME.

## Verification

The producer symbolically contracts a generic symmetric four-dimensional
endomorphism against the fourth sphere moment. The independent verifier uses
a different fixed endomorphism and integrates its degree-four polynomial
monomial by monomial. It also checks on an unrelated noncommuting `4 x 4`
fixture that

```text
log det(I+tK) - t Tr(K) + (t^2/2) Tr(K^2)
```

has precisely the `det_3` coefficients through `t^6`. Mutating the residue
denominator from `108` to `109` is rejected.

Replay with:

```bash
PYTHONPATH=quantum-weyl python3 -m \
  spectral.euclidean.generic_background_ghost_schur_schatten_split --check
PYTHONPATH=quantum-weyl python3 -m \
  spectral.euclidean.verify_generic_background_ghost_schur_schatten_split
PYTHONPATH=quantum-weyl pytest -q \
  quantum-weyl/spectral/euclidean/tests/test_generic_background_ghost_schur_schatten_split.py
```

The next coefficient-bearing gate is the common-regulator computation of
`R(K)` and the finite part of `R(K^2)`, followed by combination with the
generic physical fourth-order Hessian kernel.
