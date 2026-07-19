# Berger recoil real-shell extraction

The direct Berger carrier now has an exact complex-to-real shell map.  In the
repository's normalized symmetric-power convention,

```text
conjugate(D[r,c]) = (-1)^(r-c) D[two_j-r,two_j-c].
```

The induced anti-linear row reversal intertwines every finite de Rham and
Laplacian block.  Real entire finite-mode Green functions, real switch
operations and the Lorentzian Hermitian form pairing therefore imply

```text
I_abc[two_j,two_j-k] = conjugate(I_abc[two_j,k]).
```

The extractor folds each column pair to twice the real interval of one
representative.  It does not add independently rounded imaginary boxes.
For even shells, the central self-partner is real and is counted once.

Exact representation, de Rham and Laplacian audits have zero defects through
`two_j=6`.  All 24 pairs in the existing `two_j=5` feedback fixture also have
exactly conjugate serialized rectangles, and the eight bare channel sums are
exported as real intervals.

This closes the carrier-language mismatch only.  The exported values still
use the validation mass domain and partition count two.  No `two_j=6`
feedback evaluation, physical masses or couplings, tail closure, four recoil
records, tangent-cone restriction, quotient descent, Bridge 3 activation,
nonlinear observer theorem or quantum claim follows.
