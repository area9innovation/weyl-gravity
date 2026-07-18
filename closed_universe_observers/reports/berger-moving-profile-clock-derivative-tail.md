# Berger moving-profile clock-derivative tail

The calculation differentiates the physical detector one-form at fixed Berger
spatial point before changing to rod coordinates.  It combines the resulting
first and second amplitude-derivative Sobolev norms with an operator-valued
clock integration-by-parts estimate.  The derivative norms are approximately
`1.33e10` and `1.47e12`; the small clock frequency controls their chain-rule
coefficients.  The resulting tail upper is approximately `196` above retained
`two_j=1024`, and retained `two_j=3835` is the first integer cutoff for which
this bound is below one for both polarizations.

This certifies the physical omitted-mode bound, not a full Green image.  The
complete retained projection through `3835`, massive image, response, recoil,
and tangent-cone restriction remain open.
