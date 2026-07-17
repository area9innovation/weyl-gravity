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

The inexpensive arrival gate always runs. Generated monomials are projected
to the declared ghost, antifield, form, engineering-dimension, and derivative
window before finite block assembly, while the generator identities are
checked on the untruncated exact rows. The production minimal-BV quotient
runs only when a scope, generator, atom, differential, dependency, or AFN0
basis-manifest hash changes. The full repository suite is reserved for shared
canonical-algebra or cohomology-engine changes and theorem promotion.

## Boundary

This file describes a receiving contract with a synthetic regression fixture;
the separate import receipt is authoritative for export availability. The
contract itself computes no minimal-BV quotient, anomaly coefficient, Slavnov
breaking, QME, Lorentzian, or quantum statement.

## Accepted classical export

The separate receipt
[`CLASSICAL_MINIMAL_BV_ANTIFIELD_IMPORT_V2.json`](certificates/CLASSICAL_MINIMAL_BV_ANTIFIELD_IMPORT_V2.json)
accepts the unchanged classical foundation at commit
`3e15eafa5e0bb8cbc3eb1d2ad79a669c54ce9cca`. It independently replays six
minimal generators, eighteen covariant atoms, the exact filtration identities,
and the pinned dependency/proof artifacts. The finite scope contains 28
monomials in twelve filtered spaces; seven generated monomials outside the
declared window are recorded and projected. The next gate is the actual
minimal-BV relative-cohomology quotient.
