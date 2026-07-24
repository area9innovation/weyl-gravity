# Outgoing S+ continuation to r=31

This package resumes the certified correlated outgoing `S+` checkpoint at
`r=8143/256`.  It uses 103 inward panels of width `1/128`, selected by the
validated step ladder, followed by one exact `1/256` panel to reach `r=31`.
The schedule is split into one 32-panel and four 16-panel checkpoints plus
the final eight-panel chunk.  A 180-second monolithic attempt and the
original second 32-panel attempt are retained as throughput failures, not
transport refusals.

The tangent remains divided by 512 throughout transport.  Every panel
requires generator 7315, exact direct/partial-dual Taylor coefficient
equality, interval overlap, a finite tail, and finite base/tangent widths.

Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`.

Arrival at `r=31` co-locates the `S+` checkpoint with the existing `R+`
checkpoint.  This package does not itself assemble the joint `(E,R,S)`
frame or establish `K_plus`, `T_plus`, Stokes conservation, scattering, or
flux.
