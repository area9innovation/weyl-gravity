# Einstein--Maxwell radiative symplectic matching

## Result

`COMPACT_EM_RADIATIVE_SYMPLECTIC_MATCHING` fixes the covariant normalization
of the complete radiative Einstein--Maxwell master system on
`R_t x S1_L x S2`.  It covers every Fourier momentum and spherical `m`, all
`ell>=2`, and the physical `ell=1` quotient.  Homogeneous `ell=0` global data,
the axial `ell=1` twist pair, and the pullback of the Weyl--Maxwell form are
kept as separate gates.

For

```text
N_lm = int_(S2) conjugate(Y_lm) Y_lm dOmega,
lambda = ell(ell+1),
```

the exact rest-frame transverse-coefficient and polar-master Hessians are

```text
W_A = (N_lm/2) [[lambda,0],[0,2]],
G_P = (N_lm/2) [[1,-2],[-2,2lambda]].
```

The axial coefficients are curls of the certified scalar potentials,
`(h_A,q_A)=epsilon_A^B partial_B(H,Q)`.  Pulling `W_A` back through that curl,
integrating by parts on the periodic cylinder, and using the master equation
gives

```text
G_A = (N_lm/2) W_A M_A
    = (N_lm/2) [[lambda^2,2lambda],[2lambda,2lambda]].
```

This distinction is essential at `ell=1`: unlike `W_A`, `G_A` sees the
massless gauge kernel.  The polar matrix supersedes the earlier diagonal
conserved symmetrizer as the action-normalized current.  That diagonal matrix
remains a valid algebraic symmetrizer; it was not the pullback of the
covariant action pairing.

## Exact second variation

The slow exact rail expands

```text
S = int sqrt(-g)[(R-2Lambda)/(2kappa)-F^2/4],
kappa=1, Lambda=1/2, radius(S2)=1, P=1,
```

to second order for an arbitrary smooth axisymmetric function `Y(theta)`.
After integrating the `q_i ddot(q_j)` terms by parts, it obtains the local
velocity Hessians

```text
H_A = [[sin(theta)(Y')^2/2, 0],
       [0, sin(theta)Y^2]],

H_P = [[ sin(theta)Y^2/2, -sin(theta)Y^2],
       [-sin(theta)Y^2,    sin(theta)(Y')^2]].
```

These are arbitrary-function identities, not fixed-`ell` interpolation.
Using only

```text
int |D Y_lm|^2 dOmega = lambda N_lm
```

gives the displayed all-`lambda` coefficient and polar matrices.  `SO(3)`
equivariance extends the axisymmetric computation to every `m`.  Local `1+1`
covariance fixes the same normalization for every `S1` momentum.  The axial
curl pullback then gives `G_A=W_A M_A` without assuming a global Lorentz boost
of the cylinder.  The compact Cauchy pairing is obtained by integrating the
corresponding Wronskian over `S1`.

The matrices symmetrize the certified master operators exactly:

```text
G_A M_A = M_A^T G_A,
G_P M_P = M_P^T G_P.
```

Before the common factor, `G_A` has leading minor `lambda^2` and determinant
`2lambda^2(lambda-2)`; `G_P` has leading minor `1` and determinant
`2(lambda-2)`.  Both are positive definite for every `ell>=2`.

## Covariant-current and bundle statement

The Lee--Wald current is the antisymmetrized field-space variation of the
Einstein--Maxwell presymplectic potential.  Its quadratic-action canonical
current differs from the current obtained after the displayed integrations
by parts only by a spacetime-exact improvement.  Since the Cauchy surface is
the closed manifold `S1 x S2`, the integrated improvement vanishes.  The
master Wronskians therefore equal the integrated covariant
Einstein--Maxwell presymplectic form.

The magnetic background connection itself is patchwise, but the difference
of two connections on the fixed bundle `P_N` is a global one-form.  Hence an
allowed `delta A`, the Maxwell presymplectic potential, and its current agree
on chart overlaps.  No Cech corner term appears.  A uniform magnetic-charge
variation is excluded because it changes `c1(P_N)`.

## The `ell=1` quotient and corrected normalization

At `lambda=2`,

```text
G_P = [[1,-2],[-2,4]]
```

before the common factor.  It has rank one and kernel `(K,U)=(2,1)`, exactly
the smooth residual polar diffeomorphism.  With

```text
Psi=U-K/2
```

and representative `(K,U)=(0,Psi)`, the bracket weight is `4`, hence the
normalized quotient weight is `2 N_1m`.  The physical axial `ell=1` vector
is governed instead by

```text
G_A = [[4,4],[4,4]].
```

Its kernel `(H,Q)=(1,-1)` is the massless combined `Diff x U(1)` branch; the
physical vector `(1,1)` is positive.  Its raw weight should not be compared
to the polar `Psi` weight because the axial curl potentials and polar master
use different fixed reconstruction conventions.  The polar result replaces
the provisional phrase "2 for Psi" in the exceptional-complex certificate,
which inherited a non-action-normalized diagonal current; it does not change
that certificate's gauge quotient or spectrum.

## Interpretation

The usual photon/graviton-like harmonic waves are present before the final
residual quotient as positive, nondegenerate directions of the covariant
Einstein--Maxwell phase space.  The polar zero branch at `ell=1` vanishes for
the ordinary reason: it is a presymplectic gauge kernel.  A later vanishing of
one-particle residual cohomology on the closed cylinder is therefore a claim
about the subsequent global conformal quotient, not about the absence of
local gravitational radiation.

## Claim boundary and next gate

This is a `LOCAL-ALGEBRAIC` / `REDUCED-MODE` result.  It is not a
`LORENTZIAN-CAUSAL` or scattering theorem.  It does not yet determine the
global zero-mode phase space or whether the Weyl--Maxwell Lee--Wald form pulls
back to a nonzero multiple of the Einstein--Maxwell form.

The next work should be split in the same way:

1. compute the `ell=0` radion/circumference/electric-charge and axial `ell=1`
   twist global presymplectic pairs;
2. independently compute the Weyl--Maxwell pullback, including any exact
   improvement or corner term.

## Verification receipt

The final exhaustive arbitrary-function action check passed in `53.80 s`.  It is a
separate slow rail because repeating it in every unit test would exceed the
target fast feedback loop.  The generator verification, independent
verifier, and eight scoped tests form the fast Tier-1 rail.  Tier 3 was not
run: no freeze, tag, shared core-algebra change, release, or paper-theorem
promotion is made by this report.

```text
python3 -m bridge.einstein_sector.einstein_maxwell_radiative_symplectic_action_check --verify
python3 -m bridge.einstein_sector.einstein_maxwell_radiative_symplectic_matching --verify bridge/certificates/einstein_maxwell_radiative_symplectic_matching.json
python3 bridge/einstein_sector/verify_einstein_maxwell_radiative_symplectic_matching.py
python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_radiative_symplectic_matching
```
