# BT cubic-current free-chaos obstruction

**Certificate:** `REVERSE_PHYSICS_BT_EUCLIDEAN_CUBIC_CURRENT_CHAOS_OBSTRUCTION_V1`

**Dependency tags:** `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`

## Result

The proposed order-by-order route to the BT current-susceptibility estimate is
obstructed.  The cubic homogeneous part of the canonical current does not
carry the extra low-momentum factor required by a bound of order
\(N\omega_p\).  On every \(L^4\) torus with \(5\mid L\), exact packing and a
third-Hermite-chaos projection prove

\[
 \mathbb E_0|\widehat J^{(3)}_0(p)|^2
 \geq \frac{1083}{3349609375}\lambda^6N.
\]

At \(\lambda=2/5\) and the lowest axial momentum this implies

\[
 \frac{\mathbb E_0|\widehat J^{(3)}_0(p_L)|^2}
 {N\omega_{p_L}}
 \geq \frac{4332}{129241943359375}L^2.
\]

This is an exact obstruction to demanding hyperuniformity from each
homogeneous current term separately.  It is not an obstruction to the full
interacting theory: cross-order terms and corrections from the interacting
measure may cancel this free cubic contribution.

## Exact cubic current

Set \(\psi=\epsilon f\).  With

\[
 \ell_x=\Delta f_x,\qquad
 q_x=\frac12\sum_{y\sim x}(f_y-f_x)^2,\qquad
 c_x=\frac16\sum_{y\sim x}(f_y-f_x)^3,
\]

and \(\delta_x=f_{x+e_0}-f_x\), expansion of the canonical axial current gives

\[
 J_x^{(3)}=c_x-c_{x+e_0}
 +\delta_x(q_x+q_{x+e_0})
 +\frac{\delta_x^2}{2}(\ell_x-\ell_{x+e_0}).
\]

All coefficients in the certificate are obtained with exact rational
arithmetic.

## Compact witness

Use the four nonzero values

\[
 f_{(0,0,0,0)}=-1,\quad f_{(0,1,0,0)}=1,\quad
 f_{(1,0,0,0)}=1,\quad f_{(1,2,0,0)}=-1.
\]

Every active time row sums to zero.  The motif is therefore in the exact
orthogonal complement of both phases of every nonzero axial time mode.  Direct
enumeration on the \(5^4\) and \(7^4\) tori gives

\[
 \sum_x(\Delta f_x)^2=350,
 \qquad \sum_xJ_x^{(3)}=38,
\]

and the time-row profile \((44,-3,0,\ldots,0,-3)\).  Its Fourier polynomial is

\[
 P(e^{ip})=44-3e^{ip}-3e^{-ip}=44-6\cos p\geq38.
\]

The current therefore remains uniformly visible at every axial momentum,
including the lowest nonzero one.

## Packing and the variance lower bound

For \(L=5m\), translate the motif independently by multiples of five in all
four directions.  There are \(M=(L/5)^4=N/625\) translations.  Their
Laplacian supports are disjoint, so after division by \(\sqrt{350}\) they are
orthonormal in the free bilaplacian action inner product.  They also remain in
the full-phase background slice.

Under the free Gaussian measure their coordinates are independent centered
Gaussians of variance \(\lambda^2\).  Projecting the cubic current onto the
orthogonal third Hermite polynomial of each coordinate gives a rigorous lower
bound: other chaos components cannot reduce its squared norm.  The exact
coefficient is

\[
 \frac{6\,38^2}{625\,350^3}
 =\frac{1083}{3349609375}.
\]

Using \(\pi<22/7\) gives
\(\omega_{p_L}=4\sin^2(\pi/L)<1936/(49L^2)\), which yields the displayed
quadratic divergence after normalization by \(N\omega_{p_L}\).

## Meaning and boundary

In ordinary language, isolated weak nonlinear current blocks can add up like
ordinary independent noise.  The target theorem needs them to cancel more
strongly at long wavelengths.  That stronger cancellation is absent from the
cubic current alone, so it must come—if it exists—from the exact Ward identity
that combines all perturbative orders and the change of measure.

The next exact calculation is therefore the complete order-\(\lambda^6\)
background-marginal score variance, including current cross terms, the action
density, and determinant/normalization corrections in one common Hermite
basis.  A surviving extensive component would perturbatively obstruct this
susceptibility route; exact cancellation would identify the missing positive
mechanism.  Either result would still require a volume-uniform bridge to the
fixed-coupling interacting measure.

No complete perturbative susceptibility, nonperturbative current bound,
interacting \(H^{-1}\) theorem, continuum limit, Born rule, Krein
reconstruction, or `LORENTZIAN-CAUSAL` statement is claimed.

## Verification

```bash
ulimit -v 500000; python3 reverse_physics/bt_euclidean_cubic_current_chaos_obstruction.py --check
ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_cubic_current_chaos_obstruction.py
ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_cubic_current_chaos_obstruction
```

## Verification receipt

- Tier 0 passed: the three Python files compile, the schema, certificate, and
  sequence-35 planning event parse, and the scoped diff check is clean.  Python
  ran under a 500 MB virtual-memory cap.
- The deterministic producer drift check passed in 0.20 s with 22 MB maximum
  resident memory.
- The non-importing independent verifier passed in 0.21 s with 31 MB maximum
  resident memory.  It separately reconstructs the cubic current on the
  \(5^4\) and \(7^4\) tori.
- Fifteen direct and adversarial mutation tests passed in 0.98 s with 32 MB
  maximum resident memory.
- The weighted-current V2 and exponential-action predecessor verifiers passed
  in 0.13 s and 0.15 s respectively.
- The append-only planning import read 1,638 nodes with zero invalid items and
  zero malformed events in 7.88 s under a 300 MiB Go memory limit.
- The 2.45 s advisory Science Forge shadow rail failed closed on the
  pre-existing Forge binary/standard-library mismatch (`E9118`) and reported
  corpus baseline drift (1,752 certificates versus 976).  Its advisory wrapper
  exited zero; the bridge audit itself is recorded as failed, not passed.
- Paper 21 is not updated at this checkpoint because its independent
  foundations authority/claim-map rail was already stale at the unchanged
  parent (`authority hash drift: explorer_snapshot`).  Taking ownership of
  that substantial overlapping transition would violate the shared-master
  boundary; this result is published through the certificate and report.
- Tier 3 was not run because this is a working `EUCLIDEAN-SPECTRAL` method
  obstruction, not an interacting \(H^{-1}\) lifecycle promotion, a freeze,
  or a shared core-algebra change.
