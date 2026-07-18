# Berger recoil-scalar stream activation gate

Dependency tags: `LOCAL-ALGEBRAIC`, `LORENTZIAN-CAUSAL`.

The analytic stopping envelope is complete: the absolute-`g^3` operator,
exact switches, finite Maxwell and massive kernels, selected exact-`T` clock
transform, and four symbolic detector-tail radii are certified.
The coupling-stripped successor also fixes `tilde_u_b` as the Cauchy datum,
so each recoil channel carries the explicit monomial `g_b g_c^2`.

The four scalar streams are not active.  The detector-selected preparations
are still operator-defined.  Their harmonic coefficients and advanced
massive Green images are explicitly unevaluated, so the repository does not
yet contain a complete per-shell scalar integrand.

The corrected sequence is:

1. Serialize the complete per-shell preparation and recoil contraction with
   `m_0,m_1>0` symbolic and the coupling monomials factored.
2. Separately declare numerical masses, nonzero couplings, and an interval,
   nonzero, or sign stopping goal.
3. Run the four response-specific streams and close them with the certified
   tail radii.

No numerical mass or coupling is inferred, and symbolic tail bounds are not
reported as evaluated recoil coefficients.
