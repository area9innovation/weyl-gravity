# Phase 3 outgoing partial-jet frame completion

Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`.

The exact outgoing trace frame is now typed in the order

\[
(E,R,S)
=
\left(
2EI2,\;
XI2-\frac{i(16\omega^2-4i\omega-5)}{\omega}XI3,\;
\frac{i}{2\omega}XI3
\right).
\]

The six-state factor order is
`(metric_RW_tau_tangent, carrier_RW_base, Lx_spin_one)`.  All three lines use
the physical outgoing phase `exp(-2 i omega rstar)`; the formal endpoint rail
keeps `exp(-2 i omega r) r^(-4 i omega)` symbolic and uses the bounded
real-axis conjugator `(1-2/r)^(4 i omega)`.

The quotient audit gives `pi_x(R)=0` and `pi_x(S)=1`.  The rescaled Einstein
line has the same unit scalar amplitude as `R`, so `E` is its epsilon-copy
and reuses the certified all-order scalar Jost remainder.  The `XI2` and
`XI3` recurrences are log-free and set the free `EI2` coefficient to zero.
Consequently the canonical *formal* endpoint tau recurrence has

\[
K_+^{\mathrm{formal}}=0.
\]

The remaining failure is precise.  The practical infinity certificate proves
an all-order six-state existence enclosure for `XI3` at `r=32`, but that
box does not export a common omega generator or dual-tau coefficient.  It
therefore cannot certify the normalized `S` column in the same correlated
`IvTaylor4_omega tensor dual_tau` algebra as `R`.

Accordingly analytic `K_+`, the complete correlated outgoing frame, `T_+`,
reflection, Stokes conservation, scattering, and flux remain fail closed.
The next gate is to reissue the phase-factored `XI3/S` remainder in the
common omega/dual-tau algebra.

CLOSE-OUT: SHORTFALL — formal E/R/S and canonical formal K+ are exact, but the correlated all-order S remainder needed for analytic K+ and T+ is missing
EVIDENCE: black_hole_programme/phase3/axial_partial_jet_outgoing_frame_completion_v1/certificate.json
MISSING-DEP: correlated phase-factored XI3/S remainder in IvTaylor4_omega tensor dual_tau
