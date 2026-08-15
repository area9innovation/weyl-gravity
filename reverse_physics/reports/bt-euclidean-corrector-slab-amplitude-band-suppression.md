# BT corrector-slab amplitude-band suppression

**Certificate:** `REVERSE_PHYSICS_BT_EUCLIDEAN_CORRECTOR_SLAB_AMPLITUDE_BAND_SUPPRESSION_V1`

**Dependency tags:** `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`

## Result

The positive-radius slab theorem is not restricted to the single field
$\Omega=2^n$.  It controls a continuum of slab contrasts in one signed octave.

For the same rowwise-zero slab pattern $n_L$, set

\[
 \eta_b=(\log b)n_L,
 \qquad
 b\in[2,4]\cup[1/4,1/2].
\]

The first interval covers positive amplitudes between $\log2$ and $\log4$;
the second covers their sign reversals.  Every $\eta_b$ remains in the exact
mean-zero, lowest-cosine--sine orthogonal background slice.

On the six-row buffer, allow an arbitrary time-only row field and a
perturbation of sup norm at most $1/400$.  Its directed edge multipliers lie
in

\[
 \left[\frac{199}{200},\frac{200}{199}\right].
\]

The certificate partitions $[2,4]$ into 128 rational bins of width $1/64$ and
$[1/4,1/2]$ into 128 rational bins of width $1/512$.  In each bin it relaxes
the amplitude and every perturbation edge independently, then reconstructs
the complete seventeen-term Laurent enclosure for the four changed residual
rows.

After separating the two possibly negative linear terms, every other
discarded coefficient has a nonnegative lower endpoint.  If $\alpha$ is the
smaller positive quadratic coefficient, $\beta$ bounds the magnitude of the
two negative linear coefficients, and $c_0$ is the constant lower endpoint,
two square completions give

\[
 D_b\geq c_0-\frac{\beta^2}{2\alpha}.
\]

All 256 exact bin gaps are positive.  Their common lower bound is

\[
 g_*=
 \frac{5042236776703616766188323}
      {11848410086135937585570000}
 >0.4255.
\]

Consequently every radius-$1/400$ cylinder centered at any fixed amplitude in
the signed octave has

\[
 A(\psi+\eta_b)-A(\psi)\geq\frac{g_*}{8}L^3.
\]

## Controlling the uncountable amplitude union

A bound for each fixed $b$ is not automatically a probability bound for the
uncountable union.  Here the amplitude entropy is finite-dimensional and can
be removed explicitly.

Use the rational net

\[
 b_j=2+\frac{j}{200},\qquad j=0,\ldots,400,
\]

together with the reciprocal net $b_j^{-1}$.  There are 802 centers.  Every
$b\in[2,4]$ lies within $1/400$ of some $b_j$, and

\[
 |\log b-\log b_j|\leq\frac12|b-b_j|\leq\frac1{800}.
\]

The reciprocal interval obeys the same logarithmic estimate after replacing
$b$ by $1/b$.  Therefore every radius-$1/800$ cylinder around an arbitrary
amplitude is contained in one of the 802 certified radius-$1/400$ cylinders.
The union bound and the translation theorem give

\[
 \mu_\lambda\left(
   \bigcup_{b\in[2,4]\cup[1/4,1/2]}C_b(1/800)
 \right)
 \leq
 802\exp\left[-\frac{g_*}{8\lambda^2}L^3\right].
\]

At $\lambda=2/5$,

\[
 \mu_{2/5}\left(\bigcup_b C_b(1/800)\right)
 \leq802\exp[-c_*L^3],
 \qquad
 c_*=
 \frac{5042236776703616766188323}
      {15165964910254000109529600}
 >0.3324.
\]

This is an actual normalized Gibbs probability estimate for a continuum of
amplitudes, not a collection of point-density comparisons.

## Meaning and remaining barrier

The previous theorem could have failed as soon as the slab amplitude changed.
It does not: amplitude entropy over a full signed octave costs only the fixed
prefactor 802, while the action suppression remains exponential in $L^3$.

The global corrector theorem is nevertheless still open.  An arbitrary large
corrector need not have this slab morphology.  The missing deterministic step
must separate at least three possibilities: a slab-like region at some
amplitude, an extensive bulk-gradient/action cost, or isolated high-current
spikes.  It must then make simultaneous block translations compatible before
summing probabilities.

Amplitudes outside the certified octave, the weighted-potential mass estimate,
Gibbs corrector hyperuniformity, current susceptibility, interacting
$H^{-1}$ moment, and continuum limit remain open.  No Born, Krein, or
`LORENTZIAN-CAUSAL` conclusion is made.

## Verification

```bash
ulimit -v 500000; python3 reverse_physics/bt_euclidean_corrector_slab_amplitude_band_suppression.py --check
ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_corrector_slab_amplitude_band_suppression.py
ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_corrector_slab_amplitude_band_suppression
```

## Verification receipt

- Tier 0 passed: the changed Python files compile, the structured data parse,
  and the scoped diff has no whitespace errors.  Python ran under the 500 MB
  virtual-memory cap.
- The deterministic producer drift check passed in 0.57 s.  The independent
  verifier replayed all 256 amplitude bins without importing the producer and
  passed in 0.61 s.  Peak scoped Python RSS was below 31 MB.
- Twelve focused and adversarial tests passed in 4.40 s and reject mutations of either amplitude
  partition, the uniform gap, finite-net count, probability exponent, input
  hashes, dependency tags, and the open global-corrector gates.
- The planning import read 1635 nodes with zero invalid items and zero
  malformed events in 10.46 s.
- The 3.65 s advisory Science Forge shadow rail failed closed on the
  pre-existing Forge binary/stdlib mismatch (`E9118`) and reported corpus
  baseline drift (1749 certificates versus 976).  Its advisory wrapper exited
  zero; the bridge audit itself is recorded as failed, not passed.
- Paper 21 integration is deferred rather than generated from inconsistent
  inputs: the newly landed strict-auxiliary commit changed the explorer
  authority without regenerating Paper 21, so its pre-existing generator and
  verifier currently fail on `explorer_snapshot` hash drift.  This checkpoint
  does not take ownership of that independent foundations integration.
- Tier 2 is limited to the two direct predecessor verifiers because the shared
  action operator and predecessor bytes are unchanged.  Both passed
  sequentially in 0.24 s.
- Tier 3 is not required unless this working result is promoted to the global
  $H^{-1}$ theorem, a freeze, or a release.  This certificate deliberately
  leaves those lifecycle gates open.
