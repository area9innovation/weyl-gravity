# Affine midpoint-recentered projective transport

Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`.

The phase-factored endpoint initializer is propagated by an order-14
midpoint Taylor reference, recentered every `1/20` in radius.  One shared
frequency-panel radius drives simultaneous majorants for `q`,
`eta=d_tau q`, and `xi=d_omega q`.

The q remainder is controlled with the backward scalar logarithmic norm,
not the absolute norm of the linearized Riccati coefficient.  Every proposed
majorant is checked with outward-rounded `arb` self-map inequalities.

All 16 panels reach `r=32`, including certified eta and xi remainder balls.
The xi balls are broad, reflecting the already broad certified endpoint
frequency sensitivity, but remain valid.

Continued inward, the q remainder eventually loses its scalar Riccati
self-map.  The exact panel radii and widths are recorded in
`affine-run.json`.  This does not establish a two-sided Evans boundary,
root count, QNM, Smith selector, or EP2.
