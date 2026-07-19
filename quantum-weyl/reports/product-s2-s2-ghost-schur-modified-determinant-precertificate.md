# Product \(S^2\times S^2\) Schur modified determinant precertificate

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

This is an assembly precertificate, not a lifecycle promotion. Its weighted
row dependency remains `PRECERTIFICATE_TIER3_FAILED_NO_PROMOTION` after the
830-test exhaustive run exposed 20 failures and 12 errors in stale Cartan,
relative, Lorentzian and transfer receipts. The minimal-vector determinant is
also still absent, so the full coupled vector ghost determinant flag remains
false.

Receipts:

```bash
PYTHONPATH=quantum-weyl python3 -m \
  spectral.euclidean.product_s2_s2_ghost_schur_modified_determinant_precertificate --check
PYTHONPATH=quantum-weyl python3 -m \
  spectral.euclidean.verify_product_s2_s2_ghost_schur_modified_determinant_precertificate
PYTHONPATH=quantum-weyl python3 -m unittest \
  quantum-weyl/spectral/euclidean/tests/test_product_s2_s2_ghost_schur_modified_determinant_precertificate.py
```

Tier 3 is not rerun by this algebraic assembly: it introduces no new
lifecycle promotion and inherits the explicit failed gate from its weighted
row dependency. The focused producer, independent verifier, strict schema and
four tests are the affected chain.
