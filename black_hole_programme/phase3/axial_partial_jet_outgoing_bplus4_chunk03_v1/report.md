# Bplus4 maximal-step runtime refusal

Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`

Status: `BPLUS4_MAXIMAL_STEP_RUNTIME_REFUSED`.

The third successor attempt resumed the certified chunk-02 payload at
\(r=979/32\). It tested a \(7/32\), order-168 primary panel before the
declared \(5/32\), order-120 pre-tail fallback.

The generated source compiled successfully. Its bounded execution reached
the 42-second runtime cap without flushing a terminal model record. Because
the selected branch and direct boundary comparison were not emitted, neither
is inferred from the timeout.

No successor checkpoint exists. The last usable state remains the chunk-02
checkpoint with payload
`047f7f3118a0ed49790d54c6d8b0549186224836c17f56ec03cd65114ed4b7ff`.

CLOSE-OUT: SHORTFALL — the first genuine gate is throughput. Nothing here
establishes continuation beyond \(r=979/32\), the full \(r=4\) frame,
\(T_+\), Stokes, scattering, reflection, or flux.
