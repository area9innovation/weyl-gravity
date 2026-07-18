# Berger finite detector coefficient provider

Dependency tags: `LOCAL-ALGEBRAIC`, `LORENTZIAN-CAUSAL`.

The public `detector_profile_coefficient_interval` callable now exposes the
existing validated advanced-Maxwell detector polynomial coefficients for D0
and D1 through `two_j=4`.  It returns exact rational real and imaginary
enclosures together with the mode’s uniform entire-series remainder.
Serialized omissions inside the validated index domain are returned as exact
structural zeros.

The provider rejects `two_j>=5`, missing spatial coframe labels and unknown
blocks.  It does not yet supply an all-shell detector profile, the massive
advanced image, the positive-energy Cauchy coefficients, or any nested recoil
channel.  The complete detector-provider readiness row therefore remains
`OBSTRUCTED`.
