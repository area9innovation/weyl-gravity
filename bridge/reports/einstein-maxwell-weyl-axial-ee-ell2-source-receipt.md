# Mixed EE axial ell=2 source receipt

Date: 2026-07-16

Dependency boundary: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`.

The direct coordinate expansion of `3 B_ab-T_ab` and `div(F)^b` was run for
the explicit axisymmetric `ell=2,k=0` axial and polar Einstein-Maxwell minus-
branch representatives. The positive-frequency mixed source was projected
onto all four independent gauge-fixed axial `ell=2` rows. The two `t` rows
vanish, the two `x` rows are nonzero, and the full certified target Hessian
was inverted exactly. The displayed second-order correction has zero four-row
operator remainder. The dependent angular rows follow the imported Noether
identities but were not directly replayed in this certificate.

This does not compute even-parity quadratic outputs, conjugate/difference-
frequency outputs, or the complete second-order correction for a real tangent.

Verification receipt:

```text
/usr/bin/time -f 'elapsed=%e' \
  python3 -m bridge.einstein_sector.einstein_maxwell_weyl_axial_ee_ell2_source --write
PASS, initial x-row replay elapsed=179.93 seconds; final internally consistent
four-row replay elapsed=224.02 seconds

python3 -m bridge.einstein_sector.einstein_maxwell_weyl_axial_ee_ell2_source \
  --verify bridge/certificates/einstein_maxwell_weyl_axial_ee_ell2_source.json
python3 -m unittest \
  bridge.einstein_sector.tests.test_einstein_maxwell_weyl_axial_ee_ell2_source
3 tests, PASS, elapsed below 1 second
```

The final `--write` run is the exhaustive four-row tensor replay and generated
the committed coordinate source. Tier 0 and Tier 1 were run. Tier 2 consists
of the affected preflight/operator inputs, which are imported by content hash
and replayed algebraically. Tier 3 was not run because no freeze, release,
causal claim, or complete nonlinear theorem is promoted.
