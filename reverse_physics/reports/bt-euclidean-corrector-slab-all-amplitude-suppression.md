# BT corrector-slab all-large-amplitude suppression

**Certificate:** `REVERSE_PHYSICS_BT_EUCLIDEAN_CORRECTOR_SLAB_ALL_AMPLITUDE_SUPPRESSION_V1`

**Dependency tags:** `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`

## Result

The amplitude cutoff in the preceding signed-octave theorem is removable for
the scaled slab family.  Let

\[
 \eta_b=(\log b)n_L
\]

with the same rowwise-zero exponent pattern and positive-radius cylinder as
before.  At coupling \(\lambda=2/5\), the normalized Gibbs probability of the
entire uncountable large-contrast union satisfies

\[
 \mu_{2/5}\!\left(\bigcup_{b\leq 1/2\ \mathrm{or}\ b\geq2}
 C_b(1/800)\right)
 \leq 3208\exp[-c_*L^3],
\]

where

\[
 c_*=\frac{5042236776703616766188323}
 {15165964910254000109529600}
 \simeq0.3324705554.
\]

Thus arbitrarily large positive or negative slab amplitudes do not create an
entropy escape.  The slowest-decaying part remains the first signed octave;
larger contrasts become rapidly more expensive.

## Exact second octave

The first theorem covered
\([2,4]\cup[1/4,1/2]\).  The next signed octave needs only two rational bins
per orientation:

\[
 [4,6],\ [6,8],\qquad
 [1/8,3/16],\ [3/16,1/4].
\]

Independent relaxation of the amplitude and every cylinder edge leaves all
discarded Laurent-coefficient lower endpoints nonnegative.  The worst bin is
\([4,6]\), with residual-square gap

\[
 g_2=
 \frac{477200043180364512192613499}
 {3808294587860368619520000}
 \simeq125.3054437.
\]

This is already much larger than the first-octave gap
\(g_*\simeq0.4255623\).

## Every outer octave

For a symbolic parameter \(B\geq8\), the certificate reconstructs all 17
translation coefficients simultaneously on each of

\[
 b\in[B,2B],
 \qquad
 b\in[1/(2B),1/B].
\]

The coefficients are Laurent polynomials in \(B\).  Every choice made by
interval multiplication is itself certified: after clearing negative powers,
the difference between the selected endpoint and every alternative endpoint
is expanded in \(t=B-8\), and every rational coefficient is nonnegative.  The
same shifted-coefficient test proves the sign of all 12 discarded coefficients.

Only two linear coefficients can be negative.  If \(\alpha(B)\) is the common
floor of their positive-square partners, \(\beta(B)\) bounds their magnitudes,
and \(C(B)\) is the constant floor, exact square completion gives

\[
 C(B)-\frac{\beta(B)^2}{2\alpha(B)}
 \geq \frac9{10}B^4.
\]

The certificate proves this by expanding

\[
 2\alpha(B)\left(C(B)-\frac9{10}B^4\right)-\beta(B)^2
\]

after clearing its negative powers.  All 13 coefficients in \(B-8\) are
nonnegative and the constant coefficient is strictly positive.  This is an
exact statement for every real \(B\geq8\), not a finite scan.

## Countable amplitude entropy

On each positive octave use

\[
 c_j=B(1+j/400),\qquad j=0,\ldots,400,
\]

and use the reciprocal centers on the negative octave.  The closest center
has logarithmic error at most \(1/800\), so 802 representative cylinders of
radius \(1/400\) cover the continuum family of adaptive radius \(1/800\).

For \(B=2^m\), \(m\geq3\), the outer contribution at \(\lambda=2/5\) is at
most

\[
 802\exp\!\left[-\frac{45}{64}16^mL^3\right].
\]

Consecutive terms have ratio below \(1/2\), already by the elementary bound
\(e^x\geq1+x\).  Hence the complete outer series is at most

\[
 1604e^{-2880L^3}.
\]

Adding the first octave and second octave yields the stated prefactor 3208
with the first-octave exponent \(c_*\).

## Meaning and remaining barrier

The amplitude direction is no longer the barrier for this dangerous slab
family.  If a large corrector background is known to contain a slab-like
region, no choice of its contrast can evade the Gibbs cost by moving to a
larger amplitude.

What remains is a morphology problem.  A general background with a large
lowest-momentum corrector need not resemble this slab.  The next theorem must
show that it either contains many separated slab-like blocks, has extensive
bulk weighted-gradient/action cost, or concentrates its current in isolated
spikes.  The latter two alternatives need their own probability bounds, and
the extracted blocks must admit compatible simultaneous translations.

No corrector hyperuniformity theorem, current-susceptibility estimate,
interacting \(H^{-1}\) bound, continuum limit, Born rule, Krein reconstruction,
or `LORENTZIAN-CAUSAL` statement is established.

## Verification

```bash
ulimit -v 500000; python3 reverse_physics/bt_euclidean_corrector_slab_all_amplitude_suppression.py --check
ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_corrector_slab_all_amplitude_suppression.py
ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_corrector_slab_all_amplitude_suppression
```

## Verification receipt

- Tier 0 passed: the changed Python and structured-data files parse, and the
  scoped diff check is clean.  Python ran under a 500 MB virtual-memory cap.
- The deterministic producer drift check passed in 0.18 s with 27 MB maximum
  resident memory.
- The non-importing independent verifier passed in 0.22 s with 36 MB maximum
  resident memory.  It
  separately reconstructs the four finite bins and the complete 508-branch
  symbolic Laurent interval ledger.
- Thirteen direct and adversarial mutation tests passed in 1.12 s with 41 MB
  maximum resident memory.
- The amplitude-band and cylinder predecessor verifiers passed in 0.55 s and
  0.10 s respectively.
- The planning import read 1636 nodes with zero invalid items and zero
  malformed events in 7.15 s under a 300 MiB Go memory limit.
- The 2.29 s advisory Science Forge shadow rail failed closed on the
  pre-existing Forge binary/stdlib mismatch (`E9118`) and reported corpus
  baseline drift (1750 certificates versus 976).  Its advisory wrapper exited
  zero; the bridge audit itself is recorded as failed, not passed.
- Paper 21 integration is deferred rather than silently taking ownership of an
  independent foundations-authority transition.  Its pre-existing claim map is
  stale: the generator check exited 1 in 0.08 s, and the independent verifier
  exited 1 in 0.10 s on `authority hash drift: explorer_snapshot`.  This
  theorem is therefore published through its certificate and research report,
  without claiming a clean paper rail.
- Tier 3 is not required because this is a working `EUCLIDEAN-SPECTRAL`
  checkpoint, not the interacting \(H^{-1}\) lifecycle promotion, a freeze,
  or a shared-core algebra change.
