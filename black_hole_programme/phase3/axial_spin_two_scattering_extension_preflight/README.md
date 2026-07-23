# Axial repeated spin-two scattering-extension preflight

This package extracts the exact local off-diagonal extension between the two
certified spin-two Regge--Wheeler factors.  It then separates three statements
which must not be conflated:

1. the local rational extension matrix is exact and nonzero;
2. its filtered scattering class is `[c]` in `O/(A_in_2)`, up to a unit;
3. evaluating `[c]` at a damped simple QNM requires normalized QNM and adjoint
   QNM germs plus a boundary-convergent Fredholm pairing.

For a simple zero, `[A_in_2']` is already a unit in the quotient.  Thus the
existence of an unspecified `q` with
`c=q*A_in_2' mod A_in_2` is tautological; only a prescribed or certified
nonzero `q` would select a Smith case.  No such value is claimed here.

The time convention is `exp(+I*omega*t)`, so damped QNMs lie in
`Im(omega)>0`.

Verification:

```bash
PYTHONPATH=. python3 -m \
  black_hole_programme.phase3.axial_spin_two_scattering_extension_preflight.verify
PYTHONPATH=. python3 -m unittest -v \
  black_hole_programme.phase3.axial_spin_two_scattering_extension_preflight.test_preflight
```
