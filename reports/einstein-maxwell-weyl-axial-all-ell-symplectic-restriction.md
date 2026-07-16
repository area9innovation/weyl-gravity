# Weyl--Maxwell restriction on every regular axial Einstein--Maxwell wave

## Result

`EINSTEIN_MAXWELL_WEYL_AXIAL_ALL_ELL_SYMPLECTIC_RESTRICTION` computes the
literal Weyl--Maxwell Lee--Wald current on the complete standard axial
Einstein--Maxwell tangent block with

```text
lambda=ell(ell+1),  ell>=2,
```

all spherical `m`, arbitrary periodic `S1` momentum, and both physical master
branches.  This is a `LOCAL-ALGEBRAIC`/`REDUCED-MODE` theorem before the final
residual `SO(4,2)` quotient.

With `mu=omega^2-k^2`, harmonic norm
`N_lambda=integral_(S2)Y^2 dOmega`, and curl-potential vector `v=(H,Q)`, the
integrated currents use the convention

```text
omega^t=-i omega mu N_lambda v_1^T G(lambda,mu) v_2.
```

The exact off-shell coefficient matrices are

```text
G_EM,A = diag(lambda, 2),
G_WM,A = diag(lambda(3 mu-3 lambda+1), 2).
```

The second formula was not inferred from finitely many harmonics.  The direct
coordinate current was computed with an arbitrary function `Y(theta)`, reduced
by

```text
Y''+cot(theta)Y'+lambda Y=0,
```

and reduced modulo the certified primitive

```text
-H1 H2 [(1+3 mu) sin(theta) Y Y'
         +(3/2) cos(theta) (Y')^2].
```

Regularity makes this primitive vanish at both poles.  The resulting formula
reproduces the earlier direct `ell=2` fixture exactly.

## Physical branches

The certified axial master branches obey

```text
mu_+ = lambda+sqrt(2 lambda),  Q/H=+sqrt(lambda/2),
mu_- = lambda-sqrt(2 lambda),  Q/H=-sqrt(lambda/2).
```

Their Weyl--Maxwell weights relative to the positive Einstein--Maxwell branch
form are

```text
r_+ = 1+(3/2)sqrt(2 lambda),
r_- = 1-(3/2)sqrt(2 lambda).
```

For every `ell>=2`, `lambda>=6`; hence `r_+>0` and
`r_-<=1-3sqrt(3)<0`.  Neither factor vanishes, so each axial block has rank two
and relative signature `(1,1)`. The target form restricted along the identity
tangent inclusion is therefore nondegenerate on the complete regular axial
wave sector, but the inclusion is not a symplectic embedding of the
Einstein--Maxwell form: the pullback is neither equal to it nor one universal
scalar rescaling of it.

This sharpens the interpretation.  The ordinary axial graviton/photon-like
modes have not disappeared: they remain nonnull tangent directions, and the
preflight quotient theorem says target Weyl gauge does not remove them.  What
changes is their canonical weight.  One master branch has the opposite sign
from its Einstein--Maxwell norm throughout the entire `ell>=2` tower.

## The `ell=1` consistency degeneration

Formally setting `lambda=2` gives `mu_+=4` and `mu_-=0`.  The minus curl
current therefore vanishes through the common prefactor `mu`.  For nonzero
periodic momentum this agrees with the independently certified `ell=1` gauge
branch.  It is not a computation of the physical `ell=1` quotient or of the
`n=0` global twist: the twist uses a different representative and remains a
separate restriction block.

## Claim boundary and next gate

This theorem does not compute the polar, homogeneous, physical `ell=1`, or
global twist restrictions; the extra fourth-order Weyl--Maxwell phase space;
nonlinear closure; the final residual quotient; causal scattering; or quantum
theory.  The nearest gate is the polar all-`ell` restriction, followed by the
exceptional/global blocks using their already certified quotient
representatives.

## Verification receipts

Fast Tier 1:

```text
python3 -m bridge.einstein_sector.einstein_maxwell_weyl_axial_all_ell_symplectic_restriction --verify bridge/certificates/einstein_maxwell_weyl_axial_all_ell_symplectic_restriction.json
python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_axial_all_ell_symplectic_restriction.py
python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_axial_all_ell_symplectic_restriction
```

Slow direct-current rail:

```text
python3 -m bridge.einstein_sector.weyl_maxwell_axial_arbitrary_lambda_fixture --verify bridge/certificates/weyl_maxwell_axial_arbitrary_lambda_fixture.json
```

The slow rail recomputes the generic coordinate current, the harmonic-ODE and
total-derivative witness, and the old `ell=2` normalization control.  It passed
in `76.89 s`.  Tier 2 was not run because no shared mathematical input,
operator, schema, or upstream certificate changed; all inputs are checked by
content hash.  Tier 3 was not required because this is a scoped theorem
promotion rather than a classical/quantum freeze or shared-core change.
