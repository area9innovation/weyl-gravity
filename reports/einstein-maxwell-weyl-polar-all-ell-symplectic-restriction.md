# Weyl--Maxwell restriction on every regular polar Einstein--Maxwell wave

## Result

`EINSTEIN_MAXWELL_WEYL_POLAR_ALL_ELL_SYMPLECTIC_RESTRICTION` computes the
literal Weyl--Maxwell Lee--Wald restriction on every standard polar harmonic
with `lambda=ell(ell+1)`, `ell>=2`, all spherical `m`, arbitrary periodic
momentum, and both physical master branches.

For `mu=omega^2-k^2`, harmonic norm `N_lambda`, and polar master vector
`v=(K,U)`, use

```text
omega_P^t=-i omega N_lambda v_1^T G_P(lambda,mu) v_2.
```

The exact matrices are

```text
G_EM,P = [[1,-2],[-2,2 lambda]],

G_WM,P = [[4(mu-lambda), 5lambda-4mu],
          [5lambda-4mu, 4(mu-lambda)]].
```

The off-diagonal entry was obtained with independent `(K1,U1)` and `(K2,U2)`
amplitudes. The direct calculation used arbitrary `Y(theta)`, not a finite
harmonic interpolation. A reusable normal-form engine reduces the current by
the spherical ODE and solves a pole-vanishing quadratic primitive in
`z=cos(theta)`. Its exact remainder and the direct `ell=2` normalization
remainder both vanish.

## Branch theorem and parity comparison

The polar master branches are

```text
mu_+ = lambda+sqrt(2lambda),  (K,U)=(1,-1/sqrt(2lambda)),
mu_- = lambda-sqrt(2lambda),  (K,U)=(1,+1/sqrt(2lambda)).
```

Their exact Weyl--Maxwell/Einstein--Maxwell factors are

```text
r_+ = 1+(3/2)sqrt(2lambda),
r_- = 1-(3/2)sqrt(2lambda).
```

These are exactly the previously certified axial factors. Thus parity
isospectrality extends to the on-shell relative restriction weights, although
the axial and polar off-shell matrices and reconstruction maps are different.

Writing `a=sqrt(2lambda)>2`, the positive Einstein weights and target weights
factor as

```text
E_+ = 2(a+2)/a,       W_+ =  (a+2)(3a+2)/a,
E_- = 2(a-2)/a,       W_- = -(a-2)(3a-2)/a.
```

Consequently every polar `ell>=2` block has rank two and relative signature
`(1,1)`. The target form restricted along the linear tangent inclusion is
nondegenerate but indefinite. The inclusion is not a symplectic embedding of
the Einstein--Maxwell form.

## The `mu=0` locus

The standard polar reconstruction contains `1/mu`, so the direct fixture is
declared only for `mu!=0`. This does not leave a hidden solution: the
independent full coefficient audit has minor

```text
lambda^3(lambda-2)/8,
```

which is nonzero for `lambda>=6`. Therefore the gauge-fixed `mu=0` polar
solution is only the zero field.

## Claim boundary and next gate

This is a `LOCAL-ALGEBRAIC`/`REDUCED-MODE` theorem before the final residual
`SO(4,2)` quotient. It does not compute the physical `ell=1`, homogeneous
`ell=0`, axial-twist, extra fourth-order, nonlinear, causal, scattering, or
quantum sectors.

The nearest next step is to combine the axial and polar results into one
standard radiative-wave restriction theorem, then calculate the exceptional
and global blocks using their certified quotient representatives.

## Verification

Fast Tier 1:

```text
python3 -m bridge.einstein_sector.einstein_maxwell_weyl_polar_all_ell_symplectic_restriction --verify bridge/certificates/einstein_maxwell_weyl_polar_all_ell_symplectic_restriction.json
python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_polar_all_ell_symplectic_restriction.py
python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_polar_all_ell_symplectic_restriction bridge.einstein_sector.tests.test_quadratic_harmonic_density
```

Slow direct-current rail:

```text
python3 -m bridge.einstein_sector.weyl_maxwell_polar_arbitrary_lambda_fixture --verify bridge/certificates/weyl_maxwell_polar_arbitrary_lambda_fixture.json
```

The initial slow build passed in `321.21 s`; the strengthened replay requiring
every primitive coefficient to vanish at both poles passed in `367.47 s`.
Tier 2 was not required because all shared inputs and engines are imported by
content hash; Tier 3 was not required because no freeze or shared core algebra
was changed.
