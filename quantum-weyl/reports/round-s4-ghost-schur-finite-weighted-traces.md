# Round-S4 ghost Schur finite weighted traces

Dependency tag: `EUCLIDEAN-SPECTRAL`.

## Why this is the correct next finite calculation

The generic Schur receipts fix the full classical symbol through the residue
order, the three Wodzicki residues and the scale response. They cannot fix a
reference finite weighted trace. If `T` is any finite-rank smoothing
operator, then `K` and `K+T` have the same homogeneous symbols and Wodzicki
residues, while

```text
R_Q(K+T)-R_Q(K) = Tr(T).
```

The quadratic row changes by `Tr(KT+TK+T^2)`. Thus the missing generic input
is the full primed Green/resolvent kernel, or equivalently the complete
spectral measure—not another local symbol coefficient.

The round unit four-sphere supplies that spectrum and therefore gives a
useful exact benchmark without impersonating the generic result.
The weight-change normalization follows
[Paycha](https://arxiv.org/abs/math-ph/0503033); the sphere zeta-continuation
framework is cross-checked against
[Spreafico--Zerbini](https://arxiv.org/abs/math-ph/0610046).

## Spectral carrier and zero modes

For scalar harmonics,

```text
lambda_ell = ell(ell+3),
d_ell      = (2ell+3)(ell+2)(ell+1)/6.
```

On `R=12`, the normalized Schur factor is

```text
S_L = (Delta_0-4)/(Delta_0-6),
K   = S_L-I = 2/(Delta_0-6).
```

The carrier is `ell>=2`. The constant scalar has zero gradient and is absent
from the longitudinal carrier. The five `ell=1` harmonics are the certified
proper-conformal-Killing ghost zero modes and are deleted. This exclusion is
essential: `S_L(ell=1)=0`.

## Exact finite rows

Let

```text
q = 7/2,
a = sqrt(33)/2,
psi_+ = psi(q-a)+psi(q+a),
psi1_- = psi1(q-a)-psi1(q+a).
```

For `B=Delta_0-6`, define

```text
Z_B(s) = sum_(ell>=2) d_ell [lambda_ell-6]^(-s).
```

Exact asymptotic subtraction gives

```text
FP Z_B(1) = -1/9 -(4/3) psi_+,
FP Z_B(2) = -(1/6) psi_+ +(4/(3sqrt(33))) psi1_-.
```

The declared reference weight is `Q=Delta_0` on this carrier, at
`mu_0=1` in inverse unit-sphere-radius units. The
same-order weighted-trace change is

```text
R_Delta(K)-R_B(K) = -2,
R_Delta(K^2)-R_B(K^2) = 0.
```

Therefore

```text
R_Delta(K)
  = -20/9 -(8/3) psi_+
  = -3.096757614428635415834712409685232152637...,

FP R_Delta(K^2)
  = -(2/3) psi_+ +(16/(3sqrt(33))) psi1_-
  = 2.759102873212810620143872890124473280663...,

R_Delta(K) -(1/2)FP R_Delta(K^2)
  = -4.476309051035040725906648854747468792968....
```

The last line is the finite low-order part of the modified-determinant split.
The convergent `det_3` tail is not evaluated in this certificate.

## Claim boundary

This closes the two reference finite rows on one fully declared Euclidean
background. It does not compute their generic-background values, a generic
multiplicative anomaly, the full round-sphere `det_3` tail, the physical
fourth-order Hessian, complete `Gamma_1/Q_1`, or any Lorentzian quantum
statement.

## Replay

```bash
PYTHONPATH=quantum-weyl python3 -m \
  spectral.euclidean.round_s4_ghost_schur_finite_weighted_traces \
  --emit --check
PYTHONPATH=quantum-weyl python3 -m \
  spectral.euclidean.verify_round_s4_ghost_schur_finite_weighted_traces
PYTHONPATH=quantum-weyl pytest -q \
  quantum-weyl/spectral/euclidean/tests/test_round_s4_ghost_schur_finite_weighted_traces.py
```
