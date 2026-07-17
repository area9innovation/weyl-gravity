# Polar ungauged equation/Noether lift registration receipt

The programme imports
`bridge/certificates/einstein_maxwell_weyl_polar_ungauged_noether_lift.json`
at commit `427e479db7b3d7bd15a01ca8e0940c27bb21ed4f`, SHA-256
`1247963ba92efc60b7d6744140c6412e3667bb03010c2251db752d23d7707d34`.

The registered G2 result lifts the polar Einstein-to-Weyl equation square to
the complete eight-field generic harmonic coefficient complex.  Source Diff
and target Diff×Weyl contractions, source Bianchi rows, target Noether rows,
the equation/identity chain map, formal adjointness, and the off-shell local
Green identity are exact and retain `k=0` and `omega=0`.

This is deliberately not registered as a strict short exact sequence or
cyclic BV morphism.  The equation/identity map is not degreewise injective,
the final residual quotient is open, and the quantum classical-import gate
remains fail-closed.

Verification:

```text
python3 -m bridge.einstein_sector.einstein_maxwell_weyl_polar_ungauged_noether_lift --verify bridge/certificates/einstein_maxwell_weyl_polar_ungauged_noether_lift.json
python3 -m bridge.einstein_sector.verify_einstein_maxwell_weyl_polar_ungauged_noether_lift
python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_polar_ungauged_noether_lift
python3 d_quotient_programme/verify_programme_status.py --check --guards
```

Tier 0 completed in `0.04` seconds and the scoped Tier-1 rail in `9.54`
seconds, both `PASS`.  Programme regeneration completed in `0.59` seconds and
the status-plus-mutation-guard check completed in `0.74` seconds, both `PASS`.
No upstream content-addressed input changed.  Tier 3 was not run because no
paper theorem freeze, release, shared core algebra, or causal/quantum lifecycle
state is promoted.
