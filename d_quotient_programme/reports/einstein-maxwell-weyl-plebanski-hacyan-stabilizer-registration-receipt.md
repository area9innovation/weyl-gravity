# Plebański–Hacyan stabilizer descent registration receipt

The programme imports
`bridge/certificates/einstein_maxwell_weyl_plebanski_hacyan_stabilizer.json`
at commit `607be99928ca94515af4b8d96e0faff2229329d7`, SHA-256
`212d231aa60f390f4d785a95466156a7851e4c8a531fd2dbaf60c1c50f09d2cf`.

The registered G2 result corrects the residual authority boundary for the
fixed-flux compactified Plebański–Hacyan fixture.  Its connected automorphism
algebra has five generators, not the vacuum-cylinder `SO(4,2)` algebra.  The
five-generator action preserves the generic axial and polar Einstein and
extra primary modules and their direct Lee–Wald forms.

Explicit nonzero moment-map matrix elements show that these generators are
not universal presymplectic-radical directions on the full generic phase
space.  The programme therefore registers them as global symmetries and
records an absolute gauge/CE quotient as `NOT_AUTHORIZED` until a common
moment-map/Taub-zero derived sector is constructed.

Verification:

```text
python3 -m bridge.einstein_sector.einstein_maxwell_weyl_plebanski_hacyan_stabilizer --verify bridge/certificates/einstein_maxwell_weyl_plebanski_hacyan_stabilizer.json
python3 -m bridge.einstein_sector.verify_einstein_maxwell_weyl_plebanski_hacyan_stabilizer
python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_plebanski_hacyan_stabilizer
python3 d_quotient_programme/verify_programme_status.py --check --guards
```

Tier 0 completed in `0.07` seconds and the scoped Tier-1 rail in `1.15`
seconds, both `PASS`.  Programme regeneration completed in `0.89` seconds and
the status-plus-mutation-guard check completed in `1.36` seconds, both `PASS`.
No upstream content-addressed operator or current was changed, so Tier 2 was
not required.  Tier 3 was not run because no release, shared-core, causal, or
quantum lifecycle state is promoted.
