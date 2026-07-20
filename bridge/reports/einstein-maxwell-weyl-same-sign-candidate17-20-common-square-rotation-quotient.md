# Candidate 17/20 common-square rotation quotient

## Result

The one-parity common-square singular carrier is completely reduced at fixed
positive active occupations after the two free node phases.

Writing

```text
delta = omega_plus N_plus - omega_minus N_minus,
```

the lifted rotational moment map is a positive normalization times `delta`
and the Cartan-square moment map on `CP2`.

- If `delta != 0`, its zero set is the phase-real `RP2`, and the `SO(3)`
  quotient is one point.
- If `delta = 0`, the rotation equation vanishes on all of `CP2`; its
  `SO(3)` quotient is a closed interval parameterized by
  `eta=|z^T z|/(z^dagger z)`.

Candidate 17 has `delta<0` on both active circuit rays, while every inactive
ray adds another strictly negative term. Its quotient is therefore always
one point on the complete nonzero active cone.

Candidate 20 has `delta<0` on `R2` and `delta>0` on `R4`. The positive
combination `t20 R2+R4`, with `t20=-delta_R4/delta_R2`, lies on an exact
balance divisor. Candidate 20 therefore has a point quotient off balance and
an interval quotient on balance.

## Exact geometric check

The binary square

```text
[a,b,c] -> [a^2,ab,(ac+2b^2)/3,bc,c^2]
```

is checked against all three `sl2` generators. In the equivalent Cartesian
model

```text
S(z)=z z^T-(z^T z/3)I,
```

the identity

```text
[S,S^dagger]=(z^dagger z)(z z^dagger-conjugate(z) z^T)
```

shows directly that the moment map vanishes precisely on phase-real
projective directions.

## Claim boundary

This does not classify the complete two-parity singular union
`(S_plus x K_minus) union (K_plus x S_minus)`. It also does not glue
occupation strata or perform final residual, causal, observational or quantum
descent.

## Verification

```text
python3 -m bridge.einstein_sector.einstein_maxwell_weyl_same_sign_candidate17_20_common_square_rotation_quotient --check
python3 -m bridge.einstein_sector.verify_einstein_maxwell_weyl_same_sign_candidate17_20_common_square_rotation_quotient
python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_same_sign_candidate17_20_common_square_rotation_quotient
```
