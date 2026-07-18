# Round-S4 negative scalar phase locality

Dependency tags: `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`.

The scalar ghost factor `Delta_0-4` has one negative level-zero harmonic,
with eigenvalue `-4` and degeneracy one. For the effective-action exponent
`-1/2`, upper and lower spectral cuts give phases `-i pi/2` and `+i pi/2`.
Their jump is `-i pi`.

On the chamber where this eigenvalue remains negative, that discrete branch
phase is constant. It therefore has zero local BRST/Weyl variation and cannot
change the principal-symbol local `b4` density. Its magnitude and the overall
partition-function branch remain global determinant data; an eigenvalue
crossing would require a new analysis. No global branch is selected here.

## Verification

```bash
PYTHONPATH=quantum-weyl python3 -m spectral.euclidean.round_s4_negative_scalar_phase --check
PYTHONPATH=quantum-weyl python3 -m spectral.euclidean.verify_round_s4_negative_scalar_phase
PYTHONPATH=quantum-weyl python3 -m unittest spectral.euclidean.tests.test_round_s4_negative_scalar_phase
```
