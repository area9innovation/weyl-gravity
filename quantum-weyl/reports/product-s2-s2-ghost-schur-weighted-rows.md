# Product \(S^2\times S^2\) ghost Schur weighted rows

## Rigorous enclosures derived; lifecycle promotion blocked

**Dependency tag:** `EUCLIDEAN-SPECTRAL`.

The two weighted rows accompanying the regular Schur \(\det_3\) are now
rigorously enclosed:

```text
-2.240660269017... < R_Delta(K)
                       < -2.240660266450...

 1.966971851698... < FP R_Delta(K^2)
                       <  1.966971854262...

-3.224146196148... < R_Delta(K) - 1/2 FP R_Delta(K^2)
                       < -3.224146192299...
```

The first two interval widths are below \(2.57\times10^{-9}\). The scoped
mathematics therefore derives rigorous special-background enclosures, but the
standard `COEFFICIENT_COMPUTED` flags remain false because the required Tier-3
promotion suite did not pass.

## Uniform heat proof

For the sphere moment heat sums

\[
H_p(t)=\sum_{\ell\ge0}(2\ell+1)[\ell(\ell+1)]^p
e^{-t\ell(\ell+1)},
\]

the order-18 Euler--Maclaurin remainder is bounded through the
periodic-Bernoulli estimate

\[
\frac{2\zeta(2r)}{(2\pi)^{2r}}<\frac4{6^{2r}}.
\]

After shifting \(x\mapsto x+1/2\), every required derivative is a polynomial
times a Gaussian. Its absolute integral is bounded termwise using
\(\sqrt\pi<1773/1000\). The full Euler--Maclaurin polynomial through power 35
is retained, so there is no unrecorded Taylor truncation. Multiplying the left
moment with the radius-two right moment gives exact rational error bounds:

```text
R_Delta(K) meromorphic block error       < 2.16e-12
FP R_Delta(K^2) meromorphic block error  < 8.34e-13
```

The upper-incomplete spectral sums are evaluated by directed interval
arithmetic. Their rectangle `0 <= ell,m <= 80` has a separate rational tail
bound obtained by splitting the exponential equally and using
`H(c) <= 2/c`; both row errors are below `1e-40`.

## Direct trace-class proof

The positive trace-class remainders retain the preflight rectangle
`0 <= ell,m <= 2400` and exact exterior bounds. Their binary64 proof now uses
an explicit 200-operation budget per term and a conditioning reserve of 16,
covering the smallest regular denominator `1-4/lambda=1/3`. The positive
computed sum bootstraps an exact sum envelope of 2, yielding an absolute
rounding bound below `1.3e-9`.

## Claim boundary and next gate

This derives the two weighted-row enclosures only on the declared Euclidean
product background. The unrelated stale receipt chain has now been reconciled,
and the full 850-test quantum Tier-3 suite passes. The weighted rows are
therefore promoted to `COEFFICIENT_COMPUTED`; the dependent minimal-vector and
coupled Schur total is promoted under the same content-addressed receipt.
Nothing here supplies
generic-background form factors, complete
`Gamma1/Q1`, a restored QME, or a Lorentzian causal/Hadamard theorem.

## Receipts

```bash
PYTHONPATH=quantum-weyl python3 -m \
  spectral.euclidean.product_s2_s2_ghost_schur_weighted_rows --check
PYTHONPATH=quantum-weyl python3 -m \
  spectral.euclidean.verify_product_s2_s2_ghost_schur_weighted_rows
PYTHONPATH=quantum-weyl python3 -m unittest \
  quantum-weyl/spectral/euclidean/tests/test_product_s2_s2_ghost_schur_weighted_rows.py
```

Interval endpoints are serialized from their exact binary MPF rationals with
decimal `ROUND_FLOOR`/`ROUND_CEILING`; the tests explicitly prove that the
printed lower and upper endpoints enclose the internal directed interval.
Observed scoped timings for the regenerated affected chain were:

| Rail | Elapsed | Result |
| --- | ---: | --- |
| producer/emit | 16.71 s | pass |
| independent verifier | 0.08 s | pass |
| 17-test weighted/assembly/minimal-vector chain | 37.69 s | pass |
| historical full quantum Tier 3 (`830` tests) | 629.08 s | fail: 20 failures, 12 errors |
| promotion full quantum Tier 3 (`850` tests) | 650.86 s wall / 648.160 s tests | pass |

Tier 3 was required because this result promotes two rows from `NOT_COMPUTED`.
The historical failed run remains documented rather than reinterpreted as a
pass. After the Cartan, relative, Lorentzian and transfer receipts were
reconciled, the fresh 850-test run passed with zero failures and zero errors.
The certificate records that exact command, evidence commits and timings and
sets only the two special-background weighted-row flags true.
