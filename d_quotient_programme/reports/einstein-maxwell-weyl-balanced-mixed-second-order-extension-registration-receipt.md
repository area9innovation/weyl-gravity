# Balanced mixed second-order extension registration receipt

The programme imports
`bridge/certificates/einstein_maxwell_weyl_balanced_ell0_second_order.json`
at commit `74eaf0893a5c9c9659b14b7190870b0c57034eec`, SHA-256
`236c308cec85b4edde24f0acd4fe4c2133c58516426041eab2d9ffb01be28d59`.

The registered G1 theorem supplies the first complete mixed Einstein--extra
second-order extension in the compact programme.  The declared `k=0,m=0`
tangent balances the positive Einstein-minus and negative extra Taub charges.
All five stabilizer moment maps vanish.  Its homogeneous zero-frequency source
cancels exactly, and every remaining `ell=0,2,4` frequency channel has an exact
correction with zero operator remainder.  The four solved action equations
stacked with the four target Noether identities have determinant `-4` in the
eight ungauged polar equations at `k=0`, so dependent-row completion survives
every frequency and angular specialization.  The exact real-channel factors
and fixed-charge/reality audit also pass.

The companion cone theorem also proves that a single fixed nonzero-momentum
travelling block cannot balance both `H` and `P_x` nontrivially.  Neither result
classifies cancellations across distinct momenta.

This registration certifies one formal second-order jet.  It does not assert
general mixed nonlinear closure, all-orders integrability, an exact family, a
stabilizer quotient, causal evolution, or quantum physics.

Verification:

```text
python3 -m bridge.einstein_sector.einstein_maxwell_weyl_mixed_moment_map_zero_locus --verify bridge/certificates/einstein_maxwell_weyl_mixed_moment_map_zero_locus.json
python3 -m bridge.einstein_sector.verify_einstein_maxwell_weyl_mixed_moment_map_zero_locus
python3 -m bridge.einstein_sector.einstein_maxwell_weyl_balanced_ell0_second_order --verify bridge/certificates/einstein_maxwell_weyl_balanced_ell0_second_order.json
python3 -m bridge.einstein_sector.verify_einstein_maxwell_weyl_balanced_ell0_second_order
python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_mixed_moment_map_zero_locus bridge.einstein_sector.tests.test_einstein_maxwell_weyl_balanced_ell0_second_order
python3 d_quotient_programme/verify_programme_status.py --check --guards
```

The final exhaustive source-and-channel replay passed in `468.66` seconds.
The scoped fast verification and test rail passed in under ten seconds.
Deterministic programme regeneration completed in `0.59` seconds and the
status-plus-mutation-guard check completed in `0.81` seconds, both `PASS`.
