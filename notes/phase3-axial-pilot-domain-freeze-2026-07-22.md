# Phase 3 axial pilot — frozen domain

This file fixes the first global-connection pilot domain before endpoint
matching or numerical connection data are available.

## Real-frequency channel interval

- parity: axial;
- angular number: \(\ell=2\);
- mass convention: \(M=1\), with
  \(\widehat r=r/M\) and \(\widehat\omega=M\omega\);
- real-frequency interval:
  \[
  I_{\rm pilot}=\left[\frac12,\frac34\right].
  \]

The interval contains the legacy value \(\widehat\omega=3/5\), but the pilot
is an open-interval/compact-cover calculation rather than a replay of that
fixture.  Threshold \(\widehat\omega=0\), negative frequencies, algebraically
special points outside the interval, and all other \(\ell\) remain separate.

## First spectral-search box

If the global connection determinant is defined and analytic on the required
closure, the first validated upper-half-plane search uses

\[
B_{\rm pilot}=\left\{\widehat\omega\in\mathbb C:
\frac12\leq\Re\widehat\omega\leq\frac34,
\quad
\frac1{32}\leq\Im\widehat\omega\leq\frac14
\right\}.
\]

A pole or zero on the boundary prevents an argument-principle count and must
be reported as a boundary obstruction or handled by a separately frozen
subdivision.  A zero count in this box is not a stability theorem and says
nothing about \(0<\Im\widehat\omega<1/32\), other real parts, or large
frequency.

## Quantities not frozen here

Radial truncation radii, endpoint-series depths, precision and interval
subdivision are selected by the validated-error proof, not by a desired
physical outcome.  Every such choice must be recorded in the certificate and
shown stable under a stricter independent replay.
