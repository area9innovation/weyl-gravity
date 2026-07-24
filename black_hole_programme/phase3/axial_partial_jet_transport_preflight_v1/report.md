# Bounded partial-jet microfactor preflight

Dependency boundary: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`.

The exact partial-jet crosswalk was reissued in the arithmetic actually
needed by a correlated transport successor:

\[
\mathrm{IvTaylor4}_\omega\otimes
\mathbb{Q}[\tau]/(\tau^2).
\]

One q00-child radial microfactor was attempted at shell 0, panel 0. Frequency
dependence uses the shared generator 7315 on
\([1/2,4097/8192]\); radial uncertainty is retained as an outward interval
remainder. The code constructs both the dual-\(\tau\) \(8\times8\) route and
the direct \(12\times12\) six-state reference route from the hashed exact
crosswalk.

The run stops fail-closed at the analytic-tail gate. The direct coefficient
hull has

\[
\|A\|_\infty\le 5.27857793478263\times10^{13},
\qquad
h\|A\|_\infty=49160.58792530214.
\]

The current geometric tail bound therefore returns its typed
noncontractive value `-1`. No padded enclosure is emitted, and the
coefficient/difference comparison is correctly left unevaluated.

This diagnoses a more immediate issue than loss of \(\tau\)-correlation:
the rail Taylor-expands the unfactored moving Frobenius phase.  Frequency
derivatives of \(\rho^{\lambda_H(\omega)}\) contain powers of
\(\log\rho\), so a supremum-norm Taylor majorant is not expected to contract
as \(\rho\to0\).  The correct successor keeps the complete moving phase
symbolic and applies the mixed Taylor/dual arithmetic only to the reduced
Frobenius amplitude.  The present refusal does not establish physical
singularity, rank loss, H4 failure, or failure of that reduced transport.

No \(T_+\), endpoint, scattering, or global boundedness claim is made.

CLOSE-OUT: DONE — mixed omega/dual-tau arithmetic exercised on one bounded microfactor; current factor-gauge tail enclosure refuses fail-closed.

EVIDENCE: `black_hole_programme/phase3/axial_partial_jet_transport_preflight_v1/certificate.json`
