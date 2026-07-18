# Berger high-order profile-moment rail

Dependency tags: `LOCAL-ALGEBRAIC`, `LORENTZIAN-CAUSAL`.

The adaptive Clebsch--Gordan route needs radial flat-bump moments and clock
expectations of `sec(lambda s)^(2k)` beyond the earlier `k<=6` window.  This
certificate extends both normalized families through `k=50` with directed
interval arithmetic and 4096-cell dyadic Darboux sums.

The radial integrands use their exact unimodality polynomial.  The clock
integrands are decreasing throughout the rail because
`k lambda^2/cos(lambda)<1`.  For `k=0,...,6`, the new coarser enclosures
contain the existing 32768-cell certified intervals, so the successor does
not silently replace the stronger low-order values.

This is a validated input rail, not a high-mode Fourier evaluation.  The
diagonal scalar recurrence, its binomial truncation remainder, clock/Green
composition, infinite tail, full images, recoil, tangent-cone restriction,
and physical-branch interpretation remain open.
