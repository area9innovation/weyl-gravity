# Product \(S^2\times S^2\) ghost Schur weighted-row preflight

## Result

**Dependency tag:** `EUCLIDEAN-SPECTRAL`.

The two weighted rows needed beside the already enclosed regular
\(\det_3(I+K)\) now have an exact meromorphic/trace-class decomposition. On
the regular complement, with \(a=\ell(\ell+1)\), \(b=2m(m+1)\) and
\(\lambda=a+b\), the first three homogeneous pieces are

\[
K_1=\frac{2(a+2b)}{3\lambda^2},\qquad
K_2=\frac{4(a+4b)}{3\lambda^3},\qquad
K_3=\frac{8(a+8b)}{3\lambda^4}.
\]

Thus \(K-K_1-K_2-K_3\) and
\(K^2-K_1^2-2K_1K_2\) are directly summable. The corresponding product-heat
blocks independently replay

\[
\operatorname*{Res}R_\Delta(K)=\frac{19}{9},\qquad
\operatorname*{Res}R_\Delta(K^2)=\frac{14}{27},
\]

including exact subtraction of the three exceptional families from every
low-order block.

Three small-time splits give stable numerical candidates

```text
R_Delta(K)       = -2.240660268...
FP R_Delta(K^2)  =  1.966971853...
R_Delta(K) - 1/2 FP R_Delta(K^2) = -3.224146194...
```

The direct trace-class sums use the rectangle `0 <= ell,m <= 2400`. Exact
exterior estimates bound their omitted tails below `2.85e-13` and `3.41e-13`;
a binary64 `gamma_N` estimate is below the declared `2e-9` cushion. An
independent verifier recomputes a smaller rectangle and proves consistency
using its own exact exterior bounds.

## Fail-closed boundary

These displayed intervals are numerical validation intervals, not rigorous
coefficient enclosures. The small-time product heat expansions are generated
to finite order and agree across three choices of split, but a uniform
Euler--Maclaurin remainder bound has not yet been proved. Therefore

```text
PRODUCT_HEAT_EULER_MACLAURIN_REMAINDER_RIGOROUSLY_BOUNDED = false
PRODUCT_WEIGHTED_R_K_COMPUTED = false
PRODUCT_FINITE_PART_R_K2_COMPUTED = false
```

The next analytic gate is precisely that uniform remainder theorem. This
preflight is not the full coupled ghost determinant, a generic-background
form factor, complete `Gamma1/Q1`, or a Lorentzian result.

## Receipts

```bash
PYTHONPATH=quantum-weyl python3 -m \
  spectral.euclidean.product_s2_s2_ghost_schur_weighted_rows_preflight --check
PYTHONPATH=quantum-weyl python3 -m \
  spectral.euclidean.verify_product_s2_s2_ghost_schur_weighted_rows_preflight
PYTHONPATH=quantum-weyl python3 -m unittest \
  quantum-weyl/spectral/euclidean/tests/test_product_s2_s2_ghost_schur_weighted_rows_preflight.py
```

Observed scoped timings on the recorded workspace were:

| Rail | Elapsed | Result |
| --- | ---: | --- |
| producer/check | 19.49 s | pass |
| independent verifier | 0.18 s | pass |
| five-test unit slice | 19.07 s | pass |

Tier 3 is not required: this is a background-specific spectral leaf and does
not promote a lifecycle state, freeze a theorem, or change shared core
algebra. The scoped producer, independent consumer, schema, certificate and
five tests are the affected chain.
