# Einstein--Maxwell compact-product L-infinity export

The exact action-derived minimal BV Taylor coefficients through arity three
are exported on the 38-row Diff x U(1) carrier at the rational magnetic
Plebanski--Hacyan product.  The physical Euler rows come from differentiating
the covariant Einstein--Maxwell action.  Ghost, gauge and cotangent rows come
from the same covariant BV master vertices, using
`lambda_cov=lambda+i_c A`.

All 38 unary, binary and ternary rows pass the coefficientwise identities
`q1^2=0`, `[q1,q2]=0`, and the complete arity-three coefficient of `Q^2=0`.
The executable records include sparse coefficient jets through order two;
this is what permits an independent consumer to replay derivatives of the
coordinate-dependent product coefficients.

The independent consumer replays unary pairing adjointness, higher input
Koszul symmetry, the ordered first-slot output--input cyclic transpose for
`q1`, `q2`, and `q3`, and all three coefficients of `Q^2` from JSON alone.
The transpose check includes formal integration by parts against the product
measure and is streamed by output row.  It verifies the exported cyclic
coderivation; it does not independently derive the exported coefficients
from the Einstein--Maxwell action.

Claim boundary: this is a LOCAL-ALGEBRAIC, REDUCED-MODE same-background
Taylor package.  It does not establish the Einstein--Weyl relative morphism,
a causal theorem, a particle-branch projector, an observable, or a quantum
claim.
