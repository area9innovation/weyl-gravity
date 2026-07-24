# Outgoing S+ step-size ladder

This package tests one correlated outgoing `S+` panel from the certified
checkpoint at `r=8143/256` with widths `1/128`, `1/64`, and `1/32`.

Every case preserves generator `7315`, the exact internal tangent
normalization by `512`, direct/partial-dual coefficient equality, interval
overlap, finite tails, and finite widths.  Finiteness is not identified with
operational usefulness: the certificate separately requires tail below
`1e-3`, base width below `1e-2`, and normalized tangent width below `1`.
Only the `1/128` step satisfies those bounds.  The cases are independent and
do not constitute multipanel transport.

Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`.

Nothing here establishes arrival at `r=31`, a joint `(E,R,S)` frame,
`K_plus`, `T_plus`, Stokes conservation, scattering, or flux.
