# Conformal C0: direct free pairing before the interaction test

Status: C0a is exact and machine-verified by
`symbolic/verify_conformal_free_pairing.py`. C0b is the next active
calculation. This note is a research ledger, not a programme-overview
update and not yet a manuscript claim.

## Decision

The conformal theory must be defined directly at the pure-Weyl point. It
will not be defined as a limit of the split Hilbert space or split
positive metric. Mannheim likewise stresses that the equal-frequency
`1/k^4` theory is non-diagonalizable and that its state-space structure
cannot be inferred by a regular limit of the unequal-frequency theory:
[arXiv:2109.12743](https://arxiv.org/abs/2109.12743).

The direct arena is the Einstein cylinder `S^3 x R`, conformally related
to Minkowski space. AdS is a later boundary-condition and partially
massless benchmark, not the first test of the flat conformal Jordan
point.

## C0a: results now checked exactly

### Auxiliary elimination

For

```text
S_aux = int sqrt(-g) [f^{mn} G_mn - 1/4 (f_mn f^{mn} - f^2)],
```

the algebraic equation gives

```text
f = 2 R/3,
f_mn = 2 R_mn - g_mn R/3,
```

and substitution gives exactly

```text
R_mn R^{mn} - R^2/3.
```

This is the pure-Weyl action modulo the four-dimensional Euler density
and an overall normalization.

### TT Jordan pairing

After an irrelevant overall rescaling, the flat TT quadratic action is

```text
L_TT = -f Box h - f^2/2.
```

Its Hessian and inverse are

```text
K(z) = [[0,-z],[-z,-1]],
K(z)^(-1) = [[1/z^2,-1/z],[-1/z,0]].
```

Thus `Box f=0`, `Box h=-f`, the `hh` propagator has a double pole, the
cross propagator has a simple pole, and `ff` vanishes. Direct evaluation
of the covariant symplectic current on an Einstein root `E` and a Jordan
partner `L` gives

```text
<E,E> = 0,
<E,L> = <L,E> = 1.
```

The remaining `<L,L>` entry is removed by `L -> L+cE`, leaving the
canonical nondegenerate Gram matrix

```text
J1 = [[0,1],[1,0]].
```

Every nondegenerate Hermitian form preserved by the rank-two Jordan
Hamiltonian has negative determinant. Indefiniteness is therefore forced
by the Jordan block; it is not an optional bad normalization.

### Full flat physical algebra already in the literature

Kubo and Kuntz already carried out the flat diffeomorphism-plus-Weyl BRST
reduction and LSZ construction for pure conformal gravity:
[arXiv:2202.08298](https://arxiv.org/abs/2202.08298). Their physical
oscillators obey, for each TT helicity,

```text
[a_h, a_H^dagger] = 1,
[a_h, a_h^dagger] = [a_H, a_H^dagger] = 0,
```

and the Hamiltonian maps the generalized state into the null energy
eigenstate. This is precisely the `J1=sigma_x` block derived above. They
also find two ordinary helicity-1 modes with diagonal nonzero norm.

At fixed null momentum the resulting free physical form can be written

```text
J_phys = sigma_x (+) sigma_x (+) s I_2,
```

where `s=+1` in their displayed action convention. Paper IV reaches the
opposite vector sign by continuing the overall Weyl-action sign fixed in
the regular split phase. Reversing that overall sign changes the full
signature from `(4,2)` to `(2,4)` while leaving each TT Jordan block
indefinite. The relative normalization under the full conformal group
still has to be checked explicitly.

Kubo--Kuntz therefore prevents us from claiming a new flat BRST state
count or a new discovery of the cross commutator. The open question is
different: whether Mannheim's proposed left-right/CPT completion, rather
than the conventional indefinite completeness relation used there, is
preserved by the actual interaction.

### No elementary local O(1,1) import

Solving `X^T K(z)+K(z)X=0` for a constant two-field generator gives only
`X=0`. The cross kinetic term alone admits opposite scaling of `h` and
`f`, but the algebraic `f^2` term breaks it. Removing that term requires

```text
h_tilde = h + (1/(2 Box)) f.
```

No finite-derivative polynomial shift can do this. The transformation is
singular on the massless/Jordan shell. This rules out the elementary
local Bateman--Turok `O(1,1)` presentation, not every possible nonlinear
or doubled construction. Bateman--Turok's mechanism and its assumptions
are described in [arXiv:2607.00096](https://arxiv.org/abs/2607.00096).

### Conditional two-particle prediction

The symmetric bosonic lift of `J1` on `(EE, EL_s, LL)` is

```text
J2 = [[0,0,1],
      [0,1,0],
      [1,0,0]].
```

If the complete degenerate transition block is `J2`-self-adjoint and the
Einstein selection theorem gives

```text
T_EE,EE = T_EL,EE = T_EE,EL = 0,
```

then exact linear algebra forces

```text
T_LL,LL = T_EL,LL = T_LL,EL = 0.
```

Equivalently, the canonically normalized TT amplitudes `LLLL` and `ELLL`
must vanish. These are conditional regression identities, not yet a
unitarity theorem: vector and BRST channels sharing the same cylinder
energy must be included before applying them.

### Coupling convention

If the action is written `S=-alpha_g int C^2`, canonical normalization
gives cubic coupling `alpha_g^(-1/2)` and quartic coupling
`alpha_g^(-1)`. If instead one writes `S=(const/g_W^2) int C^2`, as in
Kubo--Kuntz, then `g_W` itself is the weak coupling. Future formulas must
state which convention is being used.

## C0b: next exact deliverable

The next step is not to reconstruct the flat BRST complex from scratch.
It is to reconcile three existing descriptions in one convention:

1. Paper IV's reduced TT/vector/scalar phase-space decomposition;
2. Kubo--Kuntz's physical BRST oscillators and Jordan Hamiltonian;
3. Metsaev's ordinary-derivative tensor--vector formulation and explicit
   conformal boosts: [arXiv:0707.4437](https://arxiv.org/abs/0707.4437).

The target is a cylinder-harmonic theorem with these acceptance tests:

- the scalar/Weyl direction is BRST-exact or presymplectically null;
- the physical tower contains two TT Jordan chains and two ordinary
  vector modes;
- the reduced symplectic form is nondegenerate on all six modes;
- all `SO(4,2)` generators preserve the same form;
- conformal boosts determine whether the vector normalization is tied to
  the TT cross pairing;
- the result is compared explicitly with Mannheim's left-right pairing
  and Kubo--Kuntz's conventional completeness relation.

This is an infinite conformal module/harmonic-tower problem, not merely a
`6 x 6` matrix at one momentum: conformal boosts change momentum in flat
space and cylinder energy in radial quantization.

## C1 after C0b: test cubic blocks before four-point blocks

The exact Einstein subsector plausibly gives `A(E^n)=0` and
`A(L E^(n-1))=0`, but it does not remove `ELL`, `LLL`, or interactions
containing vector modes. The first interaction test must therefore be a
scan of the lowest degenerate cubic cylinder blocks, followed by

```text
V3^sharp = V3
```

on the complete physical cohomology block. Only if cubic order is
protected should the project assemble the second-order quartic-contact
plus cubic-exchange Hamiltonian.

Split-theory divided differences remain useful as independent TT
regression checks. They will not define conformal states: they do not
generate the ordinary vector sector, the scalar quotient changes rank,
and internal propagator limits can be nonuniform.

No second oppositely oriented Jordan copy is assumed. Such a copy must be
identified inside the actual conformal module; adding it by hand would
enlarge the theory.
