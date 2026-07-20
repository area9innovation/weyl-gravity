# Candidate 17/20 singular radial contraction

## Result

For either singular component, scale the arbitrary third-transvectant-kernel
parity factor by `t` and transfer the released positive and negative node
occupations into the common-square factor. This preserves fixed total
occupations, the bilinear resonance equation, node-phase reduction and
reality.

If the initial point is rotation-zero, the exact residual along this path is

```text
mu_rotation(t) = (1-t^2) delta mu_square,
delta = omega_plus N_plus - omega_minus N_minus.
```

Consequently:

- on candidate 20's exact `delta=0` balance divisor, every rotation-zero
  point of both singular components contracts to the connected
  double-singular hub;
- the complete fixed-occupation singular rotation-zero union is therefore
  connected on that divisor;
- off balance, the same radial contraction works on the phase-real
  common-square sublocus, where `mu_square=0`;
- the displayed residual is an obstruction to this canonical contraction,
  not a no-go theorem for every possible nonradial path.

Candidate 17 never reaches `delta=0` on its nonzero active cone. Candidate 20
does, by the previously certified positive combination of `R2` and `R4`.

## Claim boundary

The complete singular union is classified only on the candidate-20 balance
divisor. Candidate 17 and candidate-20 off balance still require either a
nonradial contraction or an invariant separating a component from the hub.
Occupation gluing, the full smooth-plus-singular carrier and all later
physical descents remain open.

## Verification

```text
python3 -m bridge.einstein_sector.einstein_maxwell_weyl_same_sign_candidate17_20_singular_radial_contraction --check
python3 -m bridge.einstein_sector.verify_einstein_maxwell_weyl_same_sign_candidate17_20_singular_radial_contraction
python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_same_sign_candidate17_20_singular_radial_contraction
```
