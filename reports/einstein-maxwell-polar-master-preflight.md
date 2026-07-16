# Compact Einstein--Maxwell polar master preflight

Date: 2026-07-16

## Result

`COMPACT_EM_POLAR_MASTER_PREFLIGHT` fixes the generic `ell>=2` polar Fourier
matrix on the compact Einstein--Maxwell product, reduces it to two master
variables, proves axial--polar isospectrality at that matrix level, and checks
one exact full-tensor `ell=2` plus-branch solution. It is a
`G1_POLAR_ELL_GE2_MATRIX_PREFLIGHT` result tagged `LOCAL-ALGEBRAIC` and
`REDUCED-MODE`.

This is deliberately not the full polar theorem. An arbitrary-eigenvalue
full-tensor derivation, the exceptional `ell=0,1` blocks, and covariant
symplectic matching remain open.

## Volume-density correction

The axial tensor helper could use the background density because axial metric
perturbations are trace-free at first order. That shortcut is invalid in the
polar block, where the sphere-trace coefficient `K` changes
`sqrt(-det(g))`. The Maxwell equation used here is therefore

```text
M^nu=(1/sqrt(-g)) partial_mu(sqrt(-g) F^(mu nu)),
```

with the perturbed determinant retained through first order. Its axial
angular row is

```text
(A-C)/2 + K + (omega^2-k^2-lambda) U = 0.
```

Dropping the determinant variation creates an artificial inconsistency. The
exact fixture uses the oriented sphere chart `0<theta<pi`, where the smooth
density is `sin(theta)`; the polar axes follow by smooth continuation. This
also prevents a symbolic `Abs(sin(theta))` from masquerading as a physical
pole-supported residual.

## Gauge-fixed Fourier matrix

In standard polar Regge--Wheeler gauge for `ell>=2`, the retained coefficients
are

```text
h_AB=(A,B,C)Y,  h_ab=K g_ab Y,  a_a=U X_a.
```

The exact coefficient rows are recorded in the machine certificate in the
order

```text
E00, E01, E11, E0a, E1a, sphere trace, sphere tracefree, Maxwell axial.
```

The constraint rows give

```text
A=C,
omega(A+K-2U)+kB=0,
k(A-K+2U)+omega B=0.
```

Writing `R=K-2U` and `s=omega^2-k^2`, their solution is

```text
A=C=-(omega^2+k^2)R/s,
B=2k omega R/s.
```

The remaining equations are the two-master system with matrix

```text
K_polar=[[lambda,-2lambda],[-1,lambda]].
```

Consequently

```text
omega_+^2=k_n^2+lambda+sqrt(2lambda),
omega_-^2=k_n^2+lambda-sqrt(2lambda),
```

exactly matching the certified axial eigenvalues. The reconstruction maps
are different, so this is isospectrality, not an identification of parity
sectors.

## Tensor fixture and reduced current

For `ell=2`, `k=0`, and the plus branch, the certificate substitutes

```text
omega^2=6+2sqrt(3), K=1, U=-sqrt(3)/6, A=C=-(1+sqrt(3)/3), B=0
```

into the full linearized Einstein--Maxwell tensors. Every Einstein component
and every Maxwell density component vanishes exactly.

The master matrix is symmetrized by `W=diag(1,2lambda)`, yielding the local
conserved candidate

```text
j^A(u,v)=u^T W partial^A v-(partial^A u)^T W v.
```

Its normalization and sign have not yet been matched to the covariant
Einstein--Maxwell presymplectic current.

## Interpretation and next gate

The generic radiative polar block has the same two real dispersion branches
as the axial block. Thus the compact pre-quotient linear theory visibly
contains both parities of the familiar helicity-two/photon-coupled modes.
The residual-cohomology question is a later global quotient and does not
erase these local solutions.

The next promotion requires a full arbitrary-`lambda` tensor identity rather
than interpolation from checked harmonics, followed by separate `ell=0` and
`ell=1` analyses. Only then should the axial and polar currents be matched to
the covariant symplectic form and used to normalize the full adjoint/Taub
coefficient table.

## Verification

The generator performs the exact algebraic reduction and the full `ell=2`
tensor fixture. An independent verifier reconstructs the matrix,
constraints, characteristic polynomial, symmetrizer, provenance, and
fail-closed scope. Eight scoped tests cover the schema and theorem boundary.
Generator verification passed in `15.38 s`, the independent verifier in
`0.59 s`, and the eight-test suite in `15.73 s`. Tier 2 is unnecessary because
the two imported certificates are unchanged content-addressed inputs. Tier 3
criteria are not met because this result is explicitly a preflight and does
not promote the full polar or full-adjoint theorem.
