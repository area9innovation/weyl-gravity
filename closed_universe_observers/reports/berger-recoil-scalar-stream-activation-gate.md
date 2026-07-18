# Berger recoil-scalar stream activation gate

Dependency tags: `LOCAL-ALGEBRAIC`, `LORENTZIAN-CAUSAL`.

The analytic stopping envelope is complete: the absolute-`g^3` operator,
exact switches, finite Maxwell and massive kernels, selected exact-`T` clock
transform, and four symbolic detector-tail radii are certified.
The coupling-stripped successor also fixes `tilde_u_b` as the Cauchy datum,
so each recoil channel carries the explicit monomial `g_b g_c^2`.

The complete symbolic preparation and recoil word is also certified.  All
eight `(a,b,c)` channels and four `(a,b)` aggregates carry exact typed block
compositions and the Peter–Weyl reconstruction weight.  This closes the
symbolic word, not an executable stream.

The readiness audit finds four missing execution capabilities: the detector
coefficient provider, nested time-convolution backend, shell interval
evaluator, and tail-aware aggregate stop loop.  The remaining sequence is:

1. Implement and validate the callable finite-shell interval backend.
2. Only then declare numerical positive masses, nonzero couplings, and an
   interval, nonzero, or sign stopping goal.
3. Run the four response-specific streams and close them with the certified
   tail radii.

No numerical mass or coupling is inferred, and symbolic tail bounds or
operator words are not reported as evaluated recoil coefficients.
