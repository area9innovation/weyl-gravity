# The `two_j<=138` exact-T input-tail obstruction

The exact-`T` functional calculus fixes the temporal approximation problem, but it does
not make the detector profile band-limited.  The first omitted form shell can
be tested without extending the whole rail: its Clebsch--Gordan recurrence
uses the already certified scalar shell `two_j=138` and one new scalar neighbor
at `two_j=140`.

For detector `D0`, form `two_j=139`, representation column `69`, charge
`q=-1/2`, the microphase-dressed spatial input has a selected coefficient
whose absolute value is greater than `0.827`.  The corresponding dressed
coderivative coefficient is greater than `0.862`.  Both bounds are far above
the finite temporal rail's propagated error.

Thus `two_j<=138` is not a uniformly small input-tail cutoff.  This result is
a lower-bound obstruction from one omitted shell; it neither bounds the full
infinite tail from above nor evaluates the exact-`T` cosine on that shell.  The next route must widen the adaptive harmonic
rail or certify a physical-space Green construction before retesting the
infinite tail.
