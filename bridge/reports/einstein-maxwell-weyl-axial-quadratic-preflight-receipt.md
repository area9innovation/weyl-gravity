# Axial quadratic-channel preflight receipt

Date: 2026-07-16

Dependency boundary: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`.

Established:

- the compact fixed-bundle constant-lapse target adjoint witness is extracted
  independently of a named source fixture;
- the generic axial extra-shell detector/reconstruction pair defines a
  basis-independent rank-two idempotent projector;
- an exact squarefree-radical enumeration finds no parity-compatible
  Einstein-axial by Einstein-polar resonance with an axial extra shell in the
  declared finite window;
- the selected lowest `ell=2,k=0` sum-frequency output block has a displayed
  exact inverse, so every source vector in that block is removable.

Not established:

- the explicit mixed axial-polar full-tensor value of `D^2E_WM`;
- absence of resonance outside the finite window;
- general nonlinear closure of the Einstein sector;
- residual, causal, asymptotic, scattering, or quantum descent.

Verification receipt:

```text
python3 -m compileall -q <three generators and three test modules>
python3 -m unittest \
  bridge.einstein_sector.tests.test_einstein_maxwell_weyl_target_adjoint_witness \
  bridge.einstein_sector.tests.test_einstein_maxwell_weyl_axial_extra_projector \
  bridge.einstein_sector.tests.test_einstein_maxwell_weyl_axial_quadratic_channel_preflight

10 tests, PASS, 2026-07-16, elapsed 9.16 seconds.

python3 -m bridge.einstein_sector.einstein_maxwell_weyl_target_adjoint_witness --verify \
  bridge/certificates/einstein_maxwell_weyl_target_adjoint_witness.json
python3 -m bridge.einstein_sector.einstein_maxwell_weyl_axial_extra_projector --verify \
  bridge/certificates/einstein_maxwell_weyl_axial_extra_projector.json
python3 -m bridge.einstein_sector.einstein_maxwell_weyl_axial_quadratic_channel_preflight --verify \
  bridge/certificates/einstein_maxwell_weyl_axial_quadratic_channel_preflight.json

PASS, combined elapsed approximately 6.2 seconds.
```

Tier 0 and Tier 1 are required and were run. Tier 2 was not run because no
existing mathematical input, shared operator, schema, or generated artifact
was changed; all new certificates import content-addressed inputs. Tier 3 was
not run because this does not promote a freeze, release, causal claim, or
paper theorem.
