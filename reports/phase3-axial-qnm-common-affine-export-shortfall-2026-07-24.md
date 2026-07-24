# Phase 3 common affine endpoint export shortfall

Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`.

The existing horizon and outgoing endpoint artifacts serialize midpoint
values and total panel remainder radii. They do not serialize:

- a common \(\omega\)-generator identity;
- the centered polynomial basis and coefficients;
- residual radii after subtracting those polynomials;
- an explicit phase-convention field tied to that generator.

Those fields are necessary to retain the cancellation in

\[
\Delta=q_H-q_++2i\omega
\]

without treating the same frequency dependence as three independent
uncertainties.

A bounded singleton-frequency experiment was attempted instead of launching
another long transport. On panel zero the centered horizon Frobenius seed has
zero frequency radius, and its first Taylor reference step passes. The
existing affine remainder rail nevertheless fails immediately with
`HORIZON_Q_REMAINDER_SELF_MAP` at
\(r=2+2^{-22}\), step \(2^{-26}\). This is the first exact implementation
obstruction to the common centered rerun.

The boundary-nonvanishing gate was therefore not rerun. Argument-principle,
K0, interval-Newton, QNM and EP2 gates remain not run.
