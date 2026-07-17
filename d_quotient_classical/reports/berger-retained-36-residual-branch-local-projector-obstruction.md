# Berger retained-36 residual branch projector audit

## Binary verdict

The requested `BERGER_RETAINED_36_RESIDUAL_BRANCH_BASIS_V2` cannot be
issued as a support-local same-bundle Einstein-like/extra-Weyl projector on
the retained 36-row carrier.  This package therefore issues the normalized
obstruction branch of the handoff.

The exact metric endpoint is

```text
A10 = Box_2^2 + V_2,   ord(V_2) <= 2.
```

All 92 nonzero entries of the degree-two symbol of `V_2` are nondivisible by
the scalar wave polynomial.  At matrix entry `(0,0)` and at the frozen Berger
fixture, the first exact witness is

```text
(71 p1^2 + 71 p2^2 + 9 p3^2)/80.
```

Its remainder modulo `-p0^2+p1^2+p2^2+p3^2` is unchanged, and the functional
`(80/71) coefficient_of(p1^2)` evaluates to one.  Thus the canonical rough
tensor-wave equation module is not an exact left or right factor of the
Berger endpoint.  It cannot serve as the image of the requested local,
q1-intertwining complementary projector.

## Scope

This is not a global no-go for every imaginable branch definition.  A
mixed-bundle Einstein-defect or curvature mapping cylinder, a higher-rank
filtered carrier, or a clearly labeled reduced-mode/nonlocal decomposition
remains possible.  The exact symbol lower bound is four additional BV rows:
two real helicity-two configuration directions and their two cyclic duals.
The smallest natural support-local covariant candidate is an STF2 variable
and its dual, adding ten rows and producing a rank-46 retained carrier; that
candidate remains to be constructed.

Paper 11 is unaffected.  Its proper interpretation is that the interaction
survives on the retained cyclic causal complex, while the canonical local
Einstein/extra-Weyl split is obstructed on the 36-row carrier.  The
topological odd direction remains in the separate deformation/vertex basis.
