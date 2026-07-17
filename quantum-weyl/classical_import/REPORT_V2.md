# Executable antifield/Koszul--Tate export contract v2

The historical v1 handoff remains a valid metadata and proof-artifact
preflight. It deliberately treats expression records as opaque. Version 2 is
the executable receiving gate required before the production minimal-BV
quotient.

The v2 payload supplies the complete minimal field, ghost, and antifield
dictionary; a finite atom inventory under declared dimension, derivative,
form, parity, and antifield-number bounds; and exact rational canonical
superpolynomials for `delta`, `gamma`, every positive-filtration component,
and total `Q`. Every polynomial is explicitly ordered, so Grassmann signs and
odd nilpotence are evaluated by the consumer rather than trusted from a
producer receipt.

The quantum consumer independently verifies

```text
Q = delta + gamma + Q_gt0
delta^2 = 0
delta gamma + gamma delta = 0
Q^2 = 0
```

on every exported atom. It then closes the admitted monomials under the
filtration components, constructs exact sparse blocks, and passes them through
the existing `FilteredLocalComplex` and AFN0-view APIs. The nontrivial
synthetic fixture has six base generators, three derived Euler/Noether atoms,
16 closed canonical monomials, eight filtered spaces, and four AFN0 spaces.

Mutation tests reject opaque expressions, floats, incomplete generator roles,
noncanonical super-ordering, odd squares, a forged total `Q`, a broken
`delta`--`gamma` sign, grading drift, atom-order drift, unsafe paths, stale
hashes, and working-tree/commit divergence.

## Slow-run policy

The inexpensive arrival gate always runs. The production minimal-BV quotient
runs only when a scope, generator, atom, differential, dependency, or AFN0
basis-manifest hash changes. The full repository suite is reserved for shared
canonical-algebra or cohomology-engine changes and theorem promotion.

## Boundary

This is a receiving contract with a synthetic regression fixture. The actual
covariant classical antifield export remains absent. No minimal-BV quotient,
anomaly coefficient, Slavnov breaking, QME, Lorentzian, or quantum statement
has been computed.
