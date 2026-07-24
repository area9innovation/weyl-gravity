# Common-affine Evans chunk v2

This package resumes the certified 512-panel projective Evans boundary at
panel 16 and requests panels 16--31.  Each ordered batch uses the existing
moving-phase/direct-`q` endpoint transports and one panel-local omega
generator shared by the horizon export, outgoing export, and
`Delta=q_H-q_out+2*I*omega`.

The run checkpoints after each four-panel batch and stops at the first
non-passing endpoint, chart, self-map, or mismatch gate.

Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`.
