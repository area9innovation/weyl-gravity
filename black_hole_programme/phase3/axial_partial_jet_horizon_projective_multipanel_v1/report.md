# Projective and midpoint/Lohner horizon transport shortfall

Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`

Status:
`CERTIFIED_PROJECTIVE_THROUGHPUT_AND_PIVOT_SHORTFALL`.

## Full complex-pivot chart

The mixed base/tangent column was normalized by its first regular spin-one
component. A correlated complex dual scalar carried the removed amplitude,
while a direct twelve-state realization was transformed by the same chart.

With 64 panels per geometric shell, this rail completed five panels. At
shell 0, panel 5, the structured complex inverse refused:

\[
\begin{aligned}
h\|\widehat{\mathcal B}\|_\infty&=0.08740073002218199,\\
\text{operator tail}&=2.8063072926175013\times10^{-24},\\
\Re p&\in[0.3938702815041292,1.6061297155150525],\\
\Im p&\in[-0.002368228549123645,0.0023682196089283582].
\end{aligned}
\]

The refusal code is `IVTAY_KRAWCZYK_UNCERTIFIED`. The interval evaluation of
\(|p|^2\) spans zero because dependency between the real and imaginary
models was discarded by the generic inversion enclosure. This is not
evidence of an actual pivot zero.

## Midpoint/Lohner alternate

The single permitted alternate removes only the exact Taylor centre of the
complex pivot. No interval division is required; all residual frequency
dependence stays in the affine state, and the complex dual amplitude is
tracked separately.

The compiled rail exceeded its bounded 240-second runtime without flushing a
completed-panel diagnostic. The materialized run log contains exactly
`TIMEOUT_240_SECONDS`. The attempt is therefore classified as a throughput
shortfall. It is not assigned an inferred terminal panel.

## Boundary

No bounded matching-radius column was obtained and \(K_H\) was not
extracted. A successor would need a faster validated nonlinear chart kernel
or a checkpointed/chunked midpoint implementation before further transport
is scientifically meaningful.

Nothing here establishes \(T_+\), H4, scattering, or bounded global
transport.
