# Berger Maxwell stress residual projection

## Binary verdict

**OBSTRUCTION in the stationary homogeneous Hopf-flux channel.**

The Maxwell normalization is frozen as

\[
S_M=-\frac14\int\sqrt{-\hat g}F_{ab}F^{ab},
\]

and the gravity equation is extended from
`alpha_B B-T_clock=0` to `alpha_B B-T_clock-T_Maxwell=0`.
With the repository symmetric-component convention, the same-input Taylor
block is

\[
q_2(A,A)_{h^+_{ab}}=2(2-\delta_{ab})T^{ab}[A].
\]

For both real phases `A_c` and `A_s`, `beta=2*sqrt(10)/3` and the only
nonzero retained source rows are

- `h_hat_star_00 = 80/9`;
- `h_hat_star_03 = -160/9`;
- `h_hat_star_33 = 80/9`.

The phase cross-source vanishes, so for a real mode
`A=x A_c+y A_s` the source is `(x^2+y^2) S_Maxwell`.  It is stationary,
homogeneous, tracefree, has total `D`-weight zero, and carries positive
energy with Hopf momentum flux along `s=-e3`.

## Projection and exactness

On these ten metric-antifield rows, the certified `pi_cl` block is exactly
the identity.  The retained Noether operator annihilates the source, so it
is `q1` closed.

The diagonal energy-pressure part is exact.  In row order
`(00,01,02,03,11,12,13,22,23,33)`, one primitive is

```text
['-5120/567', '0', '0', '0', '10880/651', '0', '0', '10880/651', '0', '14080/1953']
```

and its residual is exactly zero.  By contrast, the constant retained
Hessian has rank `7`, while adjoining the full Maxwell source raises the
rank to `8`.  The normalized left-null witness has only

```text
w(h_hat_star_03)=-9/160
```

and satisfies `w^T H=0`, `w^T S_Maxwell=1`.  This is an exact obstruction
witness, not a numerical rank diagnosis.

## Physical interpretation

The obstruction is the homogeneous time-Hopf momentum/shift source.  The
stationary homogeneous gravity block can absorb the diagonal energy and
pressure, but it cannot absorb the unbalanced null momentum flux.  A
backreacted configuration therefore needs either a counter-propagating or
otherwise momentum-balancing sector, or a genuinely nonhomogeneous gravity
response.

This block couples neither certified radiative Einstein-like nor extra-Weyl
branch: its only nontrivial class is a weight-zero constraint/flux channel,
while the diagonal metric response is exact.  The positive Maxwell
two-plane remains signature `[2,0,0]`; an obstruction source is not a new
kinetic direction, so no negative physical direction has been introduced.

## REDUCED-MODE limitation

The verdict holds only for constant components in the stationary
`SU(2)_L x U(1)_R`, `D`-weight-zero retained metric block at the rational
Berger fixture.  It does not exclude a nonhomogeneous or support-local
primitive and is not a radiative scattering or Lorentzian quantum theorem.

Machine-readable result:
`d_quotient_classical/certificates/BERGER_MAXWELL_STRESS_RESIDUAL_PROJECTION.json`.
