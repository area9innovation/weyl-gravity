# Balanced mixed second-order extension registration receipt

The programme imports
`bridge/certificates/einstein_maxwell_weyl_balanced_ell0_second_order.json`
at commit `6e271cd3d8ebdaaa64bc761d22439dcb52743ab1`, SHA-256
`bd036062558db94db7f352215e35d07606c40e82e9368fdf98492b80506d15d8`.

The registered G1 theorem supplies the first complete mixed Einstein--extra
second-order extension in the compact programme.  The declared `k=0,m=0`
tangent balances the positive Einstein-minus and negative extra Taub charges.
All five stabilizer moment maps vanish.  Its homogeneous zero-frequency source
cancels exactly, and every remaining `ell=0,2,4` frequency channel has an exact
correction with zero operator remainder.

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

The final exhaustive unreduced tensor replay passed in `478.87` seconds.  The
scoped fast verification and seven-test rail passed in under ten seconds.
Deterministic programme regeneration completed in `0.68` seconds and the
status-plus-mutation-guard check completed in `1.05` seconds, both `PASS`.
