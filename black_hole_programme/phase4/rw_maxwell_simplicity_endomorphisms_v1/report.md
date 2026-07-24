# Exact RW/Maxwell simplicity and endomorphism report

## Established

For `ell>=2` and real `omega>0`, the spin-two Regge--Wheeler and spin-one
Maxwell modules are simple over `C(r)[D]`, and each has rational endomorphism
ring `C`. The same-sign spin-two Riccati reduction gives exact
algebraically-special controls. A separate opposite-sign audit excludes the
selected-frame events `i/4`, `i/2`, and `i` as reducibility points.

The axial `ell=2` Bach cocycle is also nonsplit at every positive real
frequency. The earlier witness proportional to `omega^2-3` was nonoptimal:
the fixed exact minors

```text
det M[0,1,2]       = 3456 omega^10
det [M|rhs][0,1,2,5] = -645120 i omega^9
```

give ranks three and four for every `omega!=0`.

Combining these results with the certified nonsplit self-extension and the
characteristic-zero involution lemma proves that only `+I` and `-I` are
rational local dynamically compatible involutions on the axial spin-two Bach
block for real `omega>0`. Neither can make its hyperbolic form positive.

## Proof boundary

The exact machine rail checks the finite residual identities, indicial
polynomials, symmetric-square kernel equations, rank minors, and
algebraically-special controls. Exhaustiveness uses the stated local
regular-singular and infinity-balance lemmas.

## Not established

- behavior at the algebraically special points and a complete classification
  of the complex-frequency reducibility locus;
- all-`ell` Bach lifting or nonsplitting;
- absence of nonlocal or scattering-dependent positive metrics;
- a QNM Smith type, Fredholm overlap, Green-resolvent pole, or ringdown term;
- any quantum statement.
