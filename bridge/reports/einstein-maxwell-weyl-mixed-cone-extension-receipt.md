# Mixed-cone extension verification receipt

Date: 2026-07-17.

Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`.

## Scope

This receipt covers four new content-addressed results:

1. the complete generic `k=0` common stabilizer-zero density cone;
2. a two-parameter axial `ell=2,m=0` face with a complete second-order
   correction;
3. the fixed-`(ell,|k|)` paired opposite-momentum cone and its standing-wave
   face;
4. standard physical-`ell=1`, homogeneous, twist, and electric-charge moment
   maps.

No shared operator, existing certificate, schema, or frozen paper theorem was
changed.  All mathematical inputs are imported by content hash.

## Tier 0

Python byte-compilation of the eight generators/verifiers: PASS, 0.03 s.

JSON parsing of four certificates and four schemas: PASS, 0.02 s.

The scoped `git diff --check` command is recorded below after the final note
integration.

## Tier 1

Generator replay:

```text
python3 -m bridge.einstein_sector.einstein_maxwell_weyl_k0_moment_map_cone --verify bridge/certificates/einstein_maxwell_weyl_k0_moment_map_cone.json
PASS, 0.65 s

python3 -m bridge.einstein_sector.einstein_maxwell_weyl_ell2_neutral_face_second_order --verify bridge/certificates/einstein_maxwell_weyl_ell2_neutral_face_second_order.json
PASS, 26.29 s

python3 -m bridge.einstein_sector.einstein_maxwell_weyl_opposite_momentum_cone --verify bridge/certificates/einstein_maxwell_weyl_opposite_momentum_cone.json
PASS, 0.67 s

python3 -m bridge.einstein_sector.einstein_maxwell_weyl_exceptional_global_moment_maps --verify bridge/certificates/einstein_maxwell_weyl_exceptional_global_moment_maps.json
PASS, 0.31 s
```

Separately implemented verifiers: PASS at 0.51 s, 0.44 s, 0.43 s, and
0.38 s respectively.

Combined 12-test scoped unit suite: PASS, 27.83 s wall time
(`Ran 12 tests in 27.325s`).

## Higher tiers

Tier 2 was satisfied by replaying every direct consumer introduced here and
checking the unchanged, content-addressed input certificates by SHA-256.  No
transitive producer was modified, so rebuilding the imported four-dimensional
curvature, Lee--Wald, or Noether chains was not required.

Tier 3 was not run.  The change introduces scoped new `CLASSIFIED` results but
does not alter shared core algebra, freeze or retag an existing paper theorem,
or prepare a repository release.  Paper 91 remains unchanged and
theorem-frozen in its narrower scope.

## Fail-closed boundaries

The certificates explicitly leave false:

* full second-order classification of the complete `k=0` density cone;
* phase-sensitive quadratic-source classification for standing waves;
* exceptional fourth-order Weyl target modes;
* all-orders integration and any stabilizer quotient;
* Lorentzian-causal, scattering, particle, or quantum claims.
