# C2a analytic bridge: Bach reducibility, Taub charge, and the cylinder current

## Purpose and scope

This note records the analytic statement that turns the exceptional
`ell=|omega|=1` scalar block into a linearization-stability problem.  The
selected component normalization is checked independently by
`symbolic/verify_conformal_taub_charge.py`.  The result is a necessary
integrability constraint on linearized oscillator representatives.  It is
not yet a construction of the full compact-cylinder BRST cohomology, a
classification of all charge-neutral composites, or a quartic transition
operator.

The general mechanism is the one studied for compact Cauchy surfaces and
higher-curvature gravities by Altas and Tekin,
[arXiv:1705.10234](https://arxiv.org/abs/1705.10234): background
reducibilities make the linearized constraint map non-surjective, and the
second-order source must obey a quadratic integral constraint.

## Mixed second-order Bach equation

Use the action-normalized Euler tensor of

```text
S_red[g] = integral sqrt(-g) (R_mn R^mn-R^2/3).
```

Write it as `E^mn`; it is proportional to the Bach tensor, is covariantly
conserved, and is traceless.  For a two-parameter family

```text
g(a,b)=gbar+a h1+b h2+a b k12+O(a^2,b^2),
```

the mixed field equation is

```text
E^(1)[k12]+E^(2)[h1,h2]=0.
```

A cylinder Diff x Weyl reducibility is a pair `(xi,sigma)` satisfying

```text
L_xi gbar+2 sigma gbar=0.
```

Equivalently, `xi` is a conformal Killing field and
`sigma=-(1/4) div(xi)` in four dimensions.  Since `E` is traceless, the Weyl
part adds no independent bulk charge.  With future normal `n_m`, define

```text
Q_xi[h1,h2]
  = integral_S3 sqrt(gamma) n_m xi_n E^(2)mn[h1,h2].
```

Contracting the mixed field equation with `xi` converts the `E^(1)[k12]`
term into the associated linearized conserved surface charge.  The spatial
slice is compact and has no boundary, so that term vanishes.  Consequently

```text
Q_xi[h1,h2]=0
```

is necessary for `h1,h2` to be tangent to a common two-parameter family of
exact Bach-flat metrics.  A nonzero value is a linearization-stability
constraint, not a divergent exchange amplitude.  Vanishing is necessary;
the present argument does not assert sufficiency.

## The fifteen cylinder reducibilities

Under `SO(4)=SU(2)_L x SU(2)_R`, the conformal Killing algebra decomposes as

```text
frequency 0:  (0,0)       time translation         multiplicity 1
frequency 0:  (1,0)       left rotations           multiplicity 3
frequency 0:  (0,1)       right rotations          multiplicity 3
frequency +1: (1/2,1/2)   proper conformal          multiplicity 4
frequency -1: (1/2,1/2)   proper conformal          multiplicity 4.
```

Thus `1+3+3+4+4=15`.  In intrinsic cylinder notation, if `Y_A`, `A=1,...,4`,
are the `ell=1` scalar harmonics satisfying

```text
D_i D_j Y_A=-gamma_ij Y_A,
```

the eight proper conformal parameters have time dependence
`exp(-i s time)`, `s=+/-1`, and are precisely the null parameters of the
scalar Diff x Weyl generator.  The companion executable constructs this
sector explicitly.  C2a now also constructs the seven Killing parameters and
verifies the complete 15-generator algebra; the nonlinear charge kernels
remain incomplete.

## Exact current-to-charge map in the exceptional block

In the scalar component basis `(h00,h0i,hij_trace)`, the signed-frequency
proper-CK parameter is

```text
r_s=(i s,1,1)^T,                 G_s r_s=0.
```

Let `p_s` be the one-dimensional transverse quotient representative and
`B_s` the ordinary two-column gauge orbit.  Direct exact algebra gives

```text
d_omega(G_s r_s)=2 p_s+B_s(-2 i s,1)^T.
```

The metric probe associated with the normal charge is

```text
k_s=2 n_(m xi_n)=-i s d_omega(G_s r_s).
```

For the cubic action trilinear form `V3`, its third variation against `k_s`
is twice the mixed Euler/Bach charge:

```text
V3(h1,h2,k_s)=2 Q_s[h1,h2].
```

The curved-cylinder current calculation separately evaluates the slice
coefficient `C_s=V3(h1,h2,p_s)` and both ordinary-gauge columns.  Each gauge
coefficient integrates to zero.  Therefore

```text
2 Q_s=-i s [2 C_s+0],
```

or

```text
Q_s=-i s C_s.
```

This equality uses the action, component, frequency, and normal conventions
shown above; it is not inferred only from the scalar Hessian value
`kappa_t=0`.

For the selected forward chiral seeds the exact mixed bilinears are

```text
Q_xi-[E_+^dagger,A_+]=-sqrt(5)/(5 pi),
Q_xi+[L_-^dagger,A_-]= sqrt(10)/(5 pi).
```

They are nonzero.  The independently assembled reverse entries give the
ordinary coefficient-kernel dagger relation, and the parity partners furnish
another nonzero magnetic orbit rather than cancelling these components.  A
physical-adjoint statement awaits the globally reduced pairing.

## Consequence and remaining fork

These selected mixed `EA` and `LA` entries imply that generic superpositions
of the corresponding oscillator modes carry a proper-conformal Taub charge.
They do not imply that either basis mode is individually nonintegrable.  C2b
reconstructs every magnetic component in the two multiplicity-one mixed
blocks and exhibits an exact cancellation among their quadratic values.  The
test vector is a point on the seeded Taub-constraint zero locus, not a common
kernel of the charge matrices or a result about the complete constraint locus.  The
entries are not a computation of `Q[A_3,A_3]`, nor do they alone decide the
charge of the complete parity-projected `AA` or `EL` state: that requires the
remaining mode blocks and every term in the global charge action.  The
calculation also does not yet distinguish among:

1. exclusion of the charged pair from the nonlinear tangent cone;
2. charge-neutral superpositions or dressed composites;
3. enlargement by a collective background coordinate; or
4. cancellation in the full local-plus-global BRST complex.

Classically, the expected local structure is a moment-map reduction

```text
P_phys = mu^(-1)(0)/SO(4,2),
```

with fifteen quadratic components `mu_A`.  C2f-N/A/M now match the finite
oscillator kernels to the symplectic generators and construct the complete
moment-map jet through source energy four.  The expected all-level zero set is nonlinear rather than the
oscillator Fock space used by P4 staging.  Its quantum realization
requires the global reducibility ghosts and a BFV/BRST construction; simply
deleting one oscillator mode or projecting a Hessian by hand would not be a
derivation.

The low-energy collection through source energy four is now supplied by
`notes/conformal-moment-map-energy4.md`.  The next acceptance target is the
extension of this energy-graded action far enough to compute a complete
global-BRST kernel and image, followed by the charge-constrained energy-six
state space and its induced pairing.  The defining collection is

```text
(Q_A)_ij=integral_S3 sqrt(gamma) n_m xi_(A)n E^(2)mn[u_i,u_j],
A=1,...,15,
```

Until that cohomological step closes, no `1/kappa_t`, reduced `t` exchange, physical
energy-six effective Hamiltonian, or metric obstruction is defined.

The exact seeded-block reconstruction is in
`notes/conformal-taub-multiplets.md` and
`symbolic/verify_conformal_taub_multiplets.py`.
