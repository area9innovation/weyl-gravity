# Outgoing S common-remainder report

Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`.

The practical infinity adapter had already established an all-order,
parameter-uniform XI3 solution at `r=32`, but its rectangular output did not
carry the shared frequency generator required by the partial-jet transport.
This package makes that missing representation explicit.

On the first pilot child, the old XI3 hull is transformed by the exact
old-to-factor matrix and normalized to the unit quotient line
`S=i XI3/(2 omega)`. The finite exact factor head is evaluated in the same
`IvTaylor4` generator (`7315`) used by the selected outgoing R column. The
validated all-order hull minus the finite-head hull is attached as one common
remainder. Runtime gates independently require:

- the transformed all-order hull is contained by the reissued common model;
- all five exact Taylor coefficient matrices are unchanged;
- the base and tangent hulls remain finite;
- the partial dual has state `(Y,Z)+epsilon(X,0)`.

The result is intentionally fail-closed downstream. It establishes the
correlated endpoint S remainder only. Inward transport, a joint outgoing
three-frame, analytic `K_plus`, `T_plus`, Stokes conservation and flux remain
open.
