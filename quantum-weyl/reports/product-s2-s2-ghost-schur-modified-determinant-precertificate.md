# Product \(S^2\times S^2\) Schur modified determinant certificate

**Dependency tag:** `EUCLIDEAN-SPECTRAL`.

The rigorous regular-complement rows assemble as

\[
\log\det_{3,R_\Delta}(I+K)
=\log\det_3(I+K)+R_\Delta(K)-\frac12\operatorname{FP}R_\Delta(K^2),
\]

with enclosure

```text
-2.8978422820931000571... < log det_(3,R_Delta)(I+K)
                             < -2.8978422264095807335...
```

The six matched vector-zero/Schur-pole directions contribute the finite
factor `3^-6`, never a separately primed Schur determinant. Directed interval
evaluation of `-6 log(3)` therefore gives the coupled Schur-factor enclosure

```text
-9.4895160141017582055... < coupled Schur log
                             < -9.4895159584182388819...
```

The historical 830-test run exposed stale Cartan, relative, Lorentzian and
transfer receipts and correctly blocked promotion. After those receipts were
reconciled, a fresh 850-test Tier-3 run passed in 648.160 test seconds and
650.86 wall seconds with zero failures and zero errors. This promotes the
selected special-background Schur factor to `COEFFICIENT_COMPUTED`. The full
vector-plus-Schur flag remains the responsibility of the downstream
minimal-vector assembly.

The regenerated endpoints use exact-binary-to-decimal outward rounding rather
than nearest-decimal display. The printed intervals therefore retain the
direction of the internal MPF interval proof.

Receipts:

```bash
PYTHONPATH=quantum-weyl python3 -m \
  spectral.euclidean.product_s2_s2_ghost_schur_modified_determinant_precertificate --check
PYTHONPATH=quantum-weyl python3 -m \
  spectral.euclidean.verify_product_s2_s2_ghost_schur_modified_determinant_precertificate
PYTHONPATH=quantum-weyl python3 -m unittest \
  quantum-weyl/spectral/euclidean/tests/test_product_s2_s2_ghost_schur_modified_determinant_precertificate.py
```

The algebraic assembly inherits the exact passing Tier-3 receipt from its
weighted-row dependency. The focused producer, independent verifier, strict
schema and tests remain the direct affected chain. The compatibility filename
retains `precertificate` so existing content-addressed consumers do not break;
the machine lifecycle and result state are authoritative.
