# The spectral theorem actually used by the explicit energy operator

## Result

`FOUNDATIONAL_EXPLICIT_ENERGY_SPECTRAL_FRAGMENT_ZF_V1` completes the Phase B
spectral audit with dependency tags `LOCAL-ALGEBRAIC` and `REDUCED-MODE`.
The central result is negative and useful: the displayed construction uses no
abstract spectral theorem.  Its physical representation labels every mode by
an integer energy before the operator is defined.

```text
finite cutoff                 PRA  USED_BY_DISPLAYED_PROOF
maximal diagonal D             ZF  USED_BY_DISPLAYED_PROOF
Fock occupation energy         ZF  USED_BY_DISPLAYED_PROOF
abstract compact eigenbasis    --  NOT_USED_BY_DISPLAYED_PROOF
general PVM theorem            --  NOT_USED_BY_DISPLAYED_PROOF
```

Here PRA means Primitive Recursive Arithmetic.  The completed carriers use ZF
without Countable Choice, continuing the preceding explicit-Krein result.  ZF
is sufficient but not the weakest foundation claimed.

## Direct coordinate proof

On the already-defined mode index `I`,

```text
(Dx)_i = energy(i) x_i,
Dom(D) = {x in ell^2(I): sum_i energy(i)^2 |x_i|^2 < infinity}.
```

Symmetry is coordinatewise.  Conversely, if `y` lies in the adjoint domain,
testing the adjoint functional on each coordinate vector fixes
`(D*y)_i=energy(i)y_i`; the representing vector belongs to `ell^2(I)`, which
is exactly the weighted domain condition.  Hence `Dom(D*)=Dom(D)` and `D*=D`.
Because the fundamental symmetry `J` is bounded, diagonal and commutes with
`D`, also `D^sharp=J D* J=D`.

This is an `AVOIDED_BY_REFORMULATION` result.  The supplied coordinate basis
replaces eigenvector selection, basis extension, compact self-adjoint
diagonalization, and construction of a projection-valued measure from an
abstract operator.

## What spectral fragments remain available

If a later argument needs projections, they are already coordinate filters:

```text
(E(S)x)_i = 1_{energy(i) in S} x_i.
```

Likewise `(f(D)x)_i=f(energy(i))x_i`.  This gives polynomial and bounded
continuous functional calculus directly.  The resolvent is compact by the
finite-rank energy truncations: beyond energy `N`, the norm of `(D-i)^-1` is
at most `1/(N+1)`.  These facts are available, but the source self-adjointness
and block-finiteness conclusions do not depend on them.

That distinction matters.  “Spectral theorem” can mean finite exact
diagonalization, polynomial spectral mapping, bounded continuous functional
calculus, compact self-adjoint decomposition, or a general PVM theorem.  The
repository's explicit energy construction uses only the first and the direct
diagonal-domain argument.

## Fock lift

In the normalized occupation basis,

```text
dGamma(D)|m> = (sum_i m(i) energy(i)) |m>.
```

A fixed total energy `E` has particle number at most `E/2`, only uses
one-particle levels from 2 through `E`, and has finitely many partitions and
occupations.  Thus each fixed-energy eigenspace is finite without selecting an
eigenbasis: the occupation basis was already supplied.

The independent integer checker reconstructs the matter dimensions

```text
E=0..4: 1, 0, 10, 40, 137
E=12:   2783317
```

and checks 3,740 cutoff coordinates, projection Boolean laws, polynomial
spectral mapping, `D`--`J` commutation, and the exact resolvent-tail inequality.

## Boundary

This audit does not classify spectral measures for Euclidean BV Hessians,
background-dependent pseudodifferential operators, Green operators,
interacting Hamiltonians, determinants, zeta functions, or traces.  It proves
no reverse-mathematical necessity or independence result and remains not the
weakest-base theorem.

It is not a `LORENTZIAN-CAUSAL` result.  In particular, explicit reduced-mode
diagonalization supplies no Lorentzian propagator, Hadamard state, causal
product, or quantum-master-equation theorem.

## Next gate

The next low-hanging cell is the separable observable-algebra/state chain.
The availability of direct functional calculus must not be promoted to a
positive functional, GNS representation, selected physical state, local
normality, dynamics, or a Born rule.
