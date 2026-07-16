# Weyl--Maxwell restriction on the axial Einstein--Maxwell `ell=2` sector

## Result

`EINSTEIN_MAXWELL_WEYL_AXIAL_SYMPLECTIC_RESTRICTION` evaluates the literal
Weyl--Maxwell Lee--Wald current on the certified axial `ell=2,m=0`
Einstein--Maxwell tangent at arbitrary periodic `S1` momentum `k`.

For the plane-wave representative `(H,Q)` the sphere-integrated coordinate
currents are

```text
omega_EM^t
 = 8 i pi omega (3 H^2+Q^2)(k^2-omega^2)/5,

omega_WM^t
 =-8 i pi omega (k^2-omega^2)
   [9 H^2 k^2-9 H^2 omega^2+51 H^2-Q^2]/5.
```

The two physical axial branches at `lambda=6` obey

```text
mu_+=omega_+^2-k^2=6+2 sqrt(3),   Q/H=+sqrt(3),
mu_-=omega_-^2-k^2=6-2 sqrt(3),   Q/H=-sqrt(3).
```

Their exact Weyl--Maxwell/Einstein--Maxwell restriction factors are

```text
r_+=1+3 sqrt(3),
r_-=1-3 sqrt(3).
```

Both are nonzero, but `r_+>0` and `r_-<0`.  Conservation and the distinct
branch frequencies make the two branches symplectically orthogonal at fixed
`k`.  Thus the restricted axial `ell=2` form is nondegenerate with one
positive and one negative branch weight relative to the positive
Einstein--Maxwell branch form.

This already refutes a single nonzero normalization

```text
Omega_WM|_EM = c Omega_EM
```

on the identity tangent inclusion: the two ordinary branches require
different factors, of opposite sign.

## Direct controls

The slow coordinate rail uses

```text
P^abcd=(alpha_B/4)C^abcd,

Theta_C2^mu
 =2 sqrt(-g)[P^(mu a b nu)nabla_nu(delta g_ab)
              -nabla_nu(P^(mu a b nu))delta g_ab].
```

It retains `delta(nabla P)` even though `nabla Cbar=0`.  It also retains the
full metric variation of the Maxwell potential at nonzero background flux.
The following controls pass exactly:

- the background Bach tensor is `diag(1,-1,1,1)/6` in the orthonormal frame;
- the curvature-momentum Einstein current agrees pointwise with the
  independent Einstein--Maxwell Lee--Wald implementation;
- the flat TT Weyl current vanishes on the Einstein root;
- a pure Weyl variation has zero pointwise pairing with the axial tangent;
- the paired product current is independent of `t` and `x`.

## Interpretation and boundary

The flat zero-restriction theorem is not background-independent: curvature
and magnetic flux activate a nonzero Weyl--Maxwell pairing on this product.
But this does not recover Einstein gravity with one action normalization.  An
ordinary Einstein--Maxwell branch already has the opposite relative sign.

The waves remain exact linear solutions and the quotient-injectivity theorem
shows that target Weyl gauge does not remove them.  What changes is their
symplectic weighting inside Weyl--Maxwell theory.

This theorem is `LOCAL-ALGEBRAIC` and `REDUCED-MODE`, scoped to axial
`ell=2`.  Arbitrary `ell`, polar and global blocks, nonlinear closure, the
extra fourth-order phase space, final `SO(4,2)` reduction, scattering, and
quantum theory remain open.

## Verification

Fast rail:

```text
python3 -m bridge.einstein_sector.einstein_maxwell_weyl_axial_symplectic_restriction --verify bridge/certificates/einstein_maxwell_weyl_axial_symplectic_restriction.json
python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_axial_symplectic_restriction.py
python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_axial_symplectic_restriction
```

Slow direct-current rail:

```text
python3 -m bridge.einstein_sector.weyl_maxwell_axial_lee_wald_fixture --verify bridge/certificates/weyl_maxwell_axial_lee_wald_fixture.json
```

The slow rail passed in `72.42 s`.  It is kept out of the fast unit suite; the
fixture is content-addressed by the theorem certificate.  Tier 3 was not run
because this is a scoped `ell=2` theorem, not a freeze, release, shared-core
promotion, or complete phase-space theorem.
