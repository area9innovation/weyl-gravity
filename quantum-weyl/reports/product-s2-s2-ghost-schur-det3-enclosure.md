# Product \(S^2\times S^2\) ghost Schur \(\det_3\) enclosure

## Computed coefficient

**Dependency tag:** `EUCLIDEAN-SPECTRAL`.

On the regular complement of the exact `S2(1) x S2(2)` Schur spectrum,

\[
\log\det{}_3(I+K)
=\sum_{\ell,m}^{\rm regular}(2\ell+1)(2m+1)
\left[\log(1+K_{\ell m})-K_{\ell m}+\frac12K_{\ell m}^2\right]
\]

is now rigorously enclosed. The certificate proves

```text
0.32630391405410603404...
  < log det_3(I+K) <
0.32630396588976784255...
```

so the common certified prefix is `0.3263039`.

## Error architecture

The calculation uses the rectangular cutoff `0 <= ell,m <= 2400`.

- The 54 modes with `K>1/100` are enclosed by exact rational alternating
  Taylor sums through order 100.
- The remaining 5,764,744 modes use an even order-eight Taylor lower sum,
  an ordinary positive binary64 sum, and the exact truncation bound
  `943/4800000000000`. A standard `gamma_N` summation estimate, combined
  with a forty-operation per-term bound and the condition number of the
  alternating polynomial on `K<=1/100`, gives an exact absolute roundoff
  bound below `1.283e-12`; the declared `10^-10` cushion is therefore
  independently ample.
- With `x=ell+1/2`, `y=m+1/2` and `q=x^2+2y^2`, the exterior double tail is
  bounded using

  \[
  K\leq\frac4{3(\lambda-4)},\qquad
  0<\log(1+K)-K+\frac12K^2\leq\frac13K^3,
  \]

  plus independent one-dimensional bounds on the two exterior strips. The
  corner may be overcounted, preserving the upper bound.

An independent verifier computes the finite sum directly, using `log1p` on
the 54 large modes and a different order-twelve stable series elsewhere. It
rederives the rational exterior bound and verifies that the direct value lies
strictly inside the stored interval.

## Coupled priming and claim boundary

The six matched vector-zero/Schur-pole modes do not belong to the regular
Schur `det_3`. Their finite coupled correction remains separately recorded as

\[
3^{-6}=\frac1{729}.
\]

This certificate does not yet compute the weighted rows `R(K)` or
`FP R(K^2)`, the minimal-vector determinant, or the full coupled ghost
determinant. It is background-specific and does not supply generic form
factors, remaining BV rows, complete `Gamma1/Q1`, or a Lorentzian theorem.

## Receipts

```bash
PYTHONPATH=quantum-weyl python3 -m \
  spectral.euclidean.product_s2_s2_ghost_schur_det3_enclosure --check
PYTHONPATH=quantum-weyl python3 -m \
  spectral.euclidean.verify_product_s2_s2_ghost_schur_det3_enclosure
PYTHONPATH=quantum-weyl python3 -m unittest \
  quantum-weyl/spectral/euclidean/tests/test_product_s2_s2_ghost_schur_det3_enclosure.py
```

Observed scoped timings on the recorded workspace were:

| Rail | Elapsed | Result |
| --- | ---: | --- |
| producer/check | 6.07 s | pass |
| independent verifier | 12.70 s | pass |
| five-test unit slice | 18.94 s | pass |
| frontier, atlas and Paper 12 consumers | 2.89 s | pass |

Tier 0 also included Python compilation, JSON/schema parsing, TeX compilation,
`git diff --check`, and inspection of the exact scoped diff. The two Paper 12
documents compiled cleanly after two and three passes respectively.

Tier 3 is not required: this is a content-addressed special-background
spectral leaf, not a shared-core algebra change, theorem freeze, lifecycle
promotion, release, or full-QME claim. The affected producer, independent
consumer, direct tests, frontier/atlas consumers and Paper 12 publication
chain are the relevant certificate chain.
