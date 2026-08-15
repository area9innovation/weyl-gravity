# BT exponential action tail and current-spike gate

**Certificate:** `REVERSE_PHYSICS_BT_EUCLIDEAN_ACTION_EXPONENTIAL_CURRENT_SPIKE_GATE_V1`

**Dependency tags:** `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`

## Result

The actual positive BT Gibbs measure has a volume-uniform exponential moment
for its nonlinear action, not merely the previously proved first moment.  At
the tuned coupling \(\lambda=2/5\),

\[
 \mu_{2/5}(A\geq50N)\leq e^{-17N/5}.
\]

This controls the bulk-action morphology exponentially in the full lattice
volume.  A pointwise consequence for the canonical current is

\[
 \mu_{2/5}\!\left(\max_{\{x,y\}}|J_{xy}|\geq360N\right)
 \leq e^{-17N/5}.
\]

Thus a single superextensive current spike cannot be the likely mechanism
behind a failure of the desired low-momentum estimate.  The unresolved sector
contains bounded and moderate local currents whose phases may add coherently.

## From the affine virial theorem to an exponential moment

The predecessor proved, on every finite eight-regular periodic lattice,

\[
 D(\psi)=\psi\mathbin\cdot\nabla A(\psi)
 \geq2A(\psi)-\frac{488}{5}N.
\]

Fix \(\psi\), put \(f(t)=A(t\psi)\), and differentiate:

\[
 f'(t)=\frac{D(t\psi)}t.
\]

Consequently

\[
 \frac{d}{dt}\frac{f(t)}{t^2}
 \geq-\frac{488N}{5t^3}.
\]

Integrating from one to \(t\geq1\) gives the outward radial estimate

\[
 A(t\psi)\geq t^2A(\psi)-\frac{244}{5}N(t^2-1).
\]

Let \(Z(\lambda)\) be the normalized finite-volume partition integral on the
\((N-1)\)-dimensional mean-zero carrier.  For

\[
 0\leq\theta<\lambda^{-2},\qquad
 \lambda'=\frac{\lambda}{\sqrt{1-\theta\lambda^2}},
 \qquad t=\frac{\lambda'}\lambda,
\]

the exponential moment is the partition-function ratio

\[
 \mathbb E_{\mu_\lambda}e^{\theta A}
 =\frac{Z(\lambda')}{Z(\lambda)}.
\]

Changing variables \(\psi=t\phi\) and applying the radial estimate proves

\[
 \boxed{\quad
 \mathbb E_{\mu_\lambda}e^{\theta A}
 \leq
 \exp\!\left[\frac{244}{5}\theta N\right]
 (1-\theta\lambda^2)^{-(N-1)/2}.
 \quad}
\]

This is an estimate for the actual normalized interacting Gibbs measure.

At \(\lambda=2/5\), choose \(\theta=25/8\), so
\(1-\theta\lambda^2=1/2\).  Chernoff's inequality and the certified rational
bound \(\log2<7/10\) give

\[
 \begin{aligned}
 \mu_{2/5}(A\geq50N)
 &\leq
 \exp\left[-\frac{25}{8}\left(50-\frac{244}{5}\right)N
       +\frac{N-1}{2}\log2\right]\\
 &\leq e^{-17N/5}.
 \end{aligned}
\]

## Current morphology consequences

For a positive directed edge ratio
\(w_{xy}=e^{\psi_y-\psi_x}\), the residual identity

\[
 r_x+8=\sum_{z\sim x}w_{xz}
\]

implies

\[
 w_{xy}\leq |r_x|+8,
 \qquad
 w_{yx}\leq |r_y|+8.
\]

The canonical current therefore obeys the all-field inequality

\[
 |J_{xy}|
 \leq |r_x|(|r_x|+8)+|r_y|(|r_y|+8).
\]

On \(A<50N\), every residual is below \(10\sqrt N\), so

\[
 |J_{xy}|<200N+160\sqrt N\leq360N.
\]

Summing the same edge inequality gives

\[
 \sum_{\{x,y\}}|J_{xy}|
 \leq16A+64\sqrt{2NA}<1440N.
\]

Hence, for every threshold \(h>0\), fewer than \(1440N/h\) edges can satisfy
\(|J_{xy}|\geq h\) on the good-action event.  This is a deterministic
bulk/spike decomposition, but it does not yet control phase coherence of the
remaining edges.

## A compact slice-valid current motif

The morphology cannot be reduced to macroscopic slabs.  On any \(L^4\) torus
with \(L\geq5\), let \(\Omega=2^n\), with the only nonzero exponents

\[
 n_{(0,0,0,0)}=-1,\quad n_{(0,1,0,0)}=1,
 \quad n_{(1,0,0,0)}=1,\quad n_{(1,2,0,0)}=-1.
\]

Each active time row sums to zero.  The logarithmic field therefore has zero
mean and is orthogonal to the cosine and sine phases of every nonzero axial
time momentum.  Exact enumeration gives

\[
 A=\frac{2085}{16},
 \qquad
 \sum_xJ_{x,0}=\frac{339}{16}.
\]

The values are unchanged between the independently enumerated \(5^4\),
\(7^4\), and producer \(8^4\) tori because the motif and its interaction
neighborhood do not wrap into themselves.  Thus compact finite-action
current carriers genuinely exist in the exact full-phase background slice.

This does not prove extensive current susceptibility.  It identifies the
minimal adversarial block that a decorrelation or lower-susceptibility theorem
must handle.

## Boundary and next calculation

The exponential moment is under the full mean-zero Gibbs measure.  The live
score theorem uses a zero-fiber observable under the integrated
cosine--sine background marginal.  Transferring a suitable local moment to
that marginal remains a separate gate.

The next calculation is an observable-weighted block decomposition on
\(A<50N\).  It must decide whether translated compact motifs decorrelate
enough to provide the missing momentum factor, or instead retain an extensive
zero-momentum susceptibility.  Only a result transferred to the actual mode
moment can prove or obstruct interacting \(H^{-1}\).

No current-susceptibility theorem, interacting \(H^{-1}\) result, continuum
limit, Born rule, Krein reconstruction, or `LORENTZIAN-CAUSAL` statement is
claimed.

## Verification

```bash
ulimit -v 500000; python3 reverse_physics/bt_euclidean_action_exponential_current_spike_gate.py --check
ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_action_exponential_current_spike_gate.py
ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_action_exponential_current_spike_gate
```

## Verification receipt

- Tier 0 passed: the three Python files compile, the schema, certificate and
  planning event parse, and the scoped diff check is clean.  Python ran under
  a 500 MB virtual-memory cap.
- The deterministic producer drift check passed in 0.11 s with 22 MB maximum
  resident memory.
- The non-importing independent verifier passed in 0.14 s with 31 MB maximum
  resident memory.  It separately enumerates the compact motif on \(5^4\) and
  \(7^4\) tori.
- Thirteen direct and adversarial mutation tests passed in 0.49 s with 32 MB
  maximum resident memory.
- The affine-virial, weighted-current, and all-amplitude-slab predecessor
  verifiers passed in 0.12 s, 0.13 s, and 0.27 s respectively.
- The planning import read 1637 nodes with zero invalid items and zero
  malformed events in 9.07 s under a 300 MiB Go memory limit.
- The 2.67 s advisory Science Forge shadow rail failed closed on the
  pre-existing Forge binary/stdlib mismatch (`E9118`) and reported corpus
  baseline drift (1751 certificates versus 976).  Its advisory wrapper exited
  zero; the bridge audit itself is recorded as failed, not passed.
- Paper 21 is not updated at this checkpoint because its independent
  foundations authority/claim-map rail was already stale at the unchanged
  parent (`authority hash drift: explorer_snapshot`).  Taking ownership of
  that substantial overlapping transition would violate the shared-master
  boundary; the theorem is published through this certificate and report.
- Tier 3 is not run because this is a working `EUCLIDEAN-SPECTRAL` estimate,
  not the interacting \(H^{-1}\) lifecycle promotion, a freeze, or a shared
  core-algebra change.
