# Product \(S^2\times S^2\) ghost minimal-vector carrier

**Dependency tags:** `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`.

The missing minimal-vector block is now reduced to two scalar product-zeta
carriers with a precise polarization and zero-mode policy.

For every active first-factor harmonic there are exact and coexact one-forms,
both with

\[
F=\lambda,\qquad A=\lambda-2.
\]

The two second-factor polarizations instead have \(A=\lambda-4\). Hence on
the regular complement the minimal-vector ratio is

\[
\prod_{i\in\mathrm{active}}
\left(\frac{\lambda-2k_i}{\lambda}\right)^2.
\]

The square must not be applied to the exceptional factor. At `(1,0)` and
`(0,1)`, the exact zero pairs with the Schur pole and contributes `1/3`, while
the coexact zero is a genuine Killing mode and is primed out. There are six
matched exact directions and six coexact Killing zeros.

The remaining infinite calculation is exactly

```text
2 * [modified determinant of J1=-2/lambda on ell>0, excluding (1,0)]
+
2 * [modified determinant of J2=-4/lambda on m>0, excluding (0,1)].
```

The required active heat carriers are `[H1-1]H2` and `H1[H2-1]`. The local
comparison between the weighted and separately zeta-regularized ratios is
also fixed. Since each scalar polarization has
`Wres(F^-2)=1`, the two-polarization total defect is

\[
2(-2^2/4)+2(-4^2/4)=-10.
\]

This certificate does not yet evaluate either infinite modified determinant.
It therefore does not complete the coupled ghost factor or promote any QME,
Lorentzian, Hadamard, or state-space claim.

Receipts:

```bash
PYTHONPATH=quantum-weyl python3 -m \
  spectral.euclidean.product_s2_s2_ghost_minimal_vector_carrier --check
PYTHONPATH=quantum-weyl python3 -m \
  spectral.euclidean.verify_product_s2_s2_ghost_minimal_vector_carrier
PYTHONPATH=quantum-weyl python3 -m unittest \
  quantum-weyl/spectral/euclidean/tests/test_product_s2_s2_ghost_minimal_vector_carrier.py
```

Tier 3 is not triggered: this is a mode-carrier and local-defect result with
the infinite determinant and all lifecycle promotions left false. The scoped
producer, independent verifier, strict schema and five tests are the affected
chain.
