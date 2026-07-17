# Weyl--Maxwell moment-map/Taub bridge registration receipt

The programme imports
`bridge/certificates/einstein_maxwell_weyl_moment_map_taub_bridge.json` at
commit `d67b2b252436720a7b19ac9583a68fa55176fcf0`, SHA-256
`4cbf20f26e3d87d981e5949b4d0727a0c8e936dba8f64503a19615fa18346e26`.

The registered G2 theorem identifies the compact stabilizer moment maps with
the corresponding quadratic Taub pairings.  Its normalization agrees exactly
with three independent direct tensor fixtures.  The positive axial and polar
extra-current blocks then make the time-translation Taub charge negative
definite on the complete real generic pure-extra sector.  Consequently no
nonzero tangent in that sector extends to second order at fixed bundle
topology.

This is a linearization-instability theorem, not deletion of the certified
linear modes.  Mixed Einstein--extra cancellations, exceptional and global
blocks, charge-varying families, an absolute stabilizer quotient, cyclic BV
enhancement, causal propagation, and quantum interpretation remain open.

Verification:

```text
python3 -m bridge.einstein_sector.einstein_maxwell_weyl_moment_map_taub_bridge --verify bridge/certificates/einstein_maxwell_weyl_moment_map_taub_bridge.json
python3 -m bridge.einstein_sector.verify_einstein_maxwell_weyl_moment_map_taub_bridge
python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_moment_map_taub_bridge
python3 d_quotient_programme/verify_programme_status.py --check --guards
```

The producing bridge Tier 0 and Tier 1 rails passed in `0.09` and `2.90`
seconds.  Deterministic programme regeneration completed in `0.60` seconds;
the status and mutation-guard check completed in `0.82` seconds.  No
content-addressed upstream mathematical input changed, so Tier 2 was not
required.  Tier 3 was not run because this registration does not promote a
release, shared-core, causal, or quantum lifecycle state.
