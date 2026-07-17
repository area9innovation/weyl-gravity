# Minimal-BV antifield V2 receiver obstruction

The classical adapted-coordinate filtration passes `delta^2=0`,
`delta gamma+gamma delta=0`, `Q=delta+gamma`, and `Q^2=0`.  The current
quantum V2 receiver then stops with:

```text
filtered adapter closure did not stabilize
```

The exact witness is not a classical defect.  With
`Lie_omega=L_xi omega`, the Weyl-covariant row for `Lie_g` contains
`-2 g Lie_omega`.  Componentwise free-algebra closure therefore contains

```text
g, g Lie_omega, g Lie_omega^2, ...
```

The receiver declares a finite ghost-number and engineering-dimension scope,
but `_dry_run_adapter` does not use either bound.  The safe repair is to
project generated monomials to the declared filtered window, or to add
generalized-connection/quotient relations to the schema.  Collapsing a full
BRST variation into one opaque atom is explicitly rejected.

No official V2 export or minimal-BV cohomology promotion is made here.
