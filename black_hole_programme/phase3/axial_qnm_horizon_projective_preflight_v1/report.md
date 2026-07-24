# QNM-band horizon projective preflight

Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`.

The moving horizon phase is correctly removed and its intrinsic exponent
derivative is exactly zero.  A QNM-band scalar Frobenius recurrence supplies
phase-reduced `q`, `eta`, and `xi` seeds on all 16 panels.

The subsequent geometric affine transport does not reach `r=32`.  The first
failure is uniformly `REFERENCE_Q_MAJORANT_DISCRIMINANT`: the absolute
Cauchy bound used for the midpoint reference becomes noncontractive before
the affine projective remainder itself fails.  Exact rational refusal radii
are stored in `horizon-run.json`.

Because no horizon line reaches the common matching radius, the code does
not assemble `Delta`, `Delta_tau`, or `Delta_omega`.  No Evans, QNM, Smith,
or EP2 claim is made.
