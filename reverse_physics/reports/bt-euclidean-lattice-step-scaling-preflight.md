# Bateman--Turok Euclidean sampler and step-scaling preflight

## Result

The finite positive Bateman--Turok lattice now has two genuinely different
sampling implementations.  The original chain is zero-mode-projected hybrid
Monte Carlo.  The new chain is local random-scan Metropolis, whose acceptance
decision uses a separately derived local action difference rather than the HMC
force.  An independent verifier checks that local formula against a full action
recomputation.

The independent-sampler gate passes only coarsely.  At λ=0.4, the two
algorithms agree on four observables at both (L=4) and (L=6) within a
predeclared four-standard-error threshold.  The largest discrepancy is 3.04
standard errors, so the result does not pass a two-standard-error precision
gate.  The two-volume interaction proxy is consequently inconclusive.

Certificate:
`REVERSE_PHYSICS_BT_EUCLIDEAN_STEP_SCALING_PREFLIGHT_V1`.

Dependency tags: `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`.
Lifecycle: `CLASSIFIED`.

## Independent local update

Write

\[
 r_x=\sum_{y\sim x}e^{\lambda(\phi_y-\phi_x)}-q,
 \qquad S=\frac1{2\lambda^2}\sum_x r_x^2,
\]

where (q=2d).  A proposal (phi_k\mapsto\phi_k+\delta) changes only
(r_k) and the residuals at sites joined to (k).  If an edge from (i) to
(k) has multiplicity (m_{ik}), then

\[
 r'_k=(r_k+q)e^{-\lambda\delta}-q,
 \qquad
 r'_i=r_i+m_{ik}e^{\lambda(\phi_k-\phi_i)}
                 (e^{\lambda\delta}-1).
\]

The Metropolis code computes (ΔS) from these affected residuals only.  The
proposal is symmetric, and recentering the field after each sweep changes only
the exact constant-shift zero mode.  The production artifact records a maximum
local-versus-global action-difference residual of
(5.20\times10^{-16}).  The independent verifier builds its own periodic graph
and checks the same identity without importing the producer.

## Observable scheme

For each lattice axis define the lowest nonzero complex Fourier mode

\[
 z_\mu=V^{-1/2}\sum_x\phi_x e^{-2\pi i x_\mu/L}.
\]

The block statistics pool axes and configurations to obtain
(M_2=\langle|z_\mu|^2\rangle) and
(M_4=\langle|z_\mu|^4\rangle).  The declared dimensionless proxy is

\[
 u_L=2-\frac{M_4}{M_2^2}.
\]

It vanishes for a centered complex Gaussian mode.  This makes (u_L) a useful
finite-volume interaction diagnostic, but not yet a renormalized continuum
coupling.  Its uncertainty is obtained by deleting one of twenty stored blocks
at a time and recomputing the nonlinear ratio.

## Free calibration

The independent local chain was first run at λ=0 on (4^4).  Its acceptance
was 0.7095.  The exact mean-zero Gaussian targets are action density
(255/512), lowest-mode (M_2=1/4), and (u_4=0).

| observable | Metropolis estimate | target | deviation |
|---|---:|---:|---:|
| action density | (0.49798\pm0.00138) | (0.49805) | (-0.05\sigma) |
| lowest-mode (M_2) | (0.2336\pm0.0127) | (0.25) | (-1.29\sigma) |
| (u_4) | (-0.1315\pm0.0674) | (0) | (-1.95\sigma) |

This calibration and the local action identity support the implementation.
They do not determine the interacting autocorrelation time.

## Interacting comparison

All production chains used λ=0.4 and periodic four-dimensional lattices.
The local chains retained 1,600 samples at (L=4) and 2,000 at (L=6), with
four sweeps between samples.  HMC retained 600 samples at each volume, with
two trajectories between samples.  All chains used twenty blocks.

| (L) | sampler | acceptance | action density | field variance | (M_2) | (u_L) |
|---:|---|---:|---:|---:|---:|---:|
| 4 | Metropolis | 0.707 | (0.49284\pm0.00163) | (0.02741\pm0.00025) | (0.2418\pm0.0073) | (0.0507\pm0.0491) |
| 4 | HMC | 0.874 | (0.49381\pm0.00459) | (0.02785\pm0.00022) | (0.2505\pm0.0055) | (0.0276\pm0.0430) |
| 6 | Metropolis | 0.707 | (0.49475\pm0.00063) | (0.03123\pm0.00037) | (0.8368\pm0.0564) | (0.2437\pm0.0661) |
| 6 | HMC | 0.915 | (0.49966\pm0.00149) | (0.03222\pm0.00029) | (0.9589\pm0.0458) | (0.0527\pm0.0519) |

At (L=4), the largest cross-sampler deviation is 1.33 standard errors.  At
(L=6), the action density differs by 3.04 standard errors, (u_L) by 2.27,
the field variance by 2.10, and (M_2) by 1.68.  All lie below the coarse
four-standard-error gate, but the result is not precision agreement.

## What the two-volume change says

The two algorithms give

\[
 \Delta u_{4\to6}^{\rm HMC}=0.0251\pm0.0675,
 \qquad
 \Delta u_{4\to6}^{\rm Metro}=0.1930\pm0.0824.
\]

The changes differ by 1.58 combined standard errors, so the algorithms do not
contradict each other.  HMC is compatible with no change, however, while the
local estimate is only (2.34\sigma) from zero.  A nonzero finite-size step is
therefore not resolved by both algorithms.

The main obstacle has shifted.  We no longer depend on one sampling algorithm;
the barrier is precision in a tail-sensitive fourth moment and slow mixing of
the lowest mode.  Spending immediately on (L=8) would enlarge that ambiguity
instead of answering it.

## Next falsifiable gate

Run at least four independent seeds for each algorithm at (L=6), retain raw
per-measurement (|z|^2) and (|z|^4), and estimate integrated autocorrelation
times.  Require action density, field variance, (M_2), and (u_L) to agree
within two combined standard errors before adding (L=8).  If local critical
slowing dominates, add a Fourier-accelerated or multiscale sampler as a third
rail rather than merely lengthening one chain.

Only after that gate passes should the programme tune a matched finite-volume
coupling at several bare λ values and attempt continuum step scaling.

## Boundaries

This result does not establish a continuum or infinite-volume limit, a beta
function, an interacting fixed point, reflection positivity, or analytic
continuation.  It does not identify (u_L) with a Lorentzian (q_8) or
(q_{10}) detector observable.  It supplies no full BT projector theorem and
no Weyl-gravity lattice measure.  In particular, it establishes nothing tagged
`LORENTZIAN-CAUSAL`.

## Verification receipt

The production runs were sequential under `ulimit -v 500000`, Python 3.12.13,
and single-thread numerical-library settings.  The complete first production
pass took 101.96 seconds and peaked at 18,844 KiB RSS.  The extended local
chains took 68.79 seconds and peaked at 17,668 KiB; the free calibration took
7.05 seconds and peaked at 17,480 KiB.  The observation JSON retains twenty
block sufficient-statistic rows per chain, fixed seeds, configurations, and
the measured run times.

The fast certificate producer reads those observations rather than rerunning
the chains.  The independent verifier redoes the local identity, all pooled
moments, delete-one-block errors, cross-sampler scores, and boundary checks.
The scoped unit suite includes direct free/nonlinear action-difference tests, a
small smoke experiment, deterministic certificate reconstruction, and six
certificate mutations.  Tier 3 is not applicable: this is a `CLASSIFIED`
finite-volume preflight with no theorem, freeze, or lifecycle promotion.

| tier | command or rail | result | elapsed | peak RSS |
|---|---|---:|---:|---:|
| 0/1 | preflight producer `--check` | PASS, 16/16 | 0.02 s | 16,468 KiB |
| 1 | independent verifier | PASS, 14/14 | 0.06 s | 24,600 KiB |
| 1 | scoped smoke/unit/mutation suite | PASS, 11 tests including 6 mutations | 0.10 s | 25,332 KiB |
| 2 | affected IR-trilemma producer/verifier/tests | PASS, hash-only refresh; 10/10, 12/12, 9 tests | 0.21 s tests | below 25 MiB |
| paper | Paper V, two `pdflatex -halt-on-error` passes | PASS, 86 pages; six pre-existing overfull boxes | 0.54 s first pass | 50,644 KiB |
| planning | sanitized `sfc conform planning` | new work and event nodes pass; aggregate REFUSED on 10 pre-existing request states | 8.3 s | not recorded |
| advisory | Paper V prose heuristic | NON-CERTIFYING: existing parenthetical/abstract findings | 1.3 s | not recorded |

The complete classical or quantum certificate suite was not run.  No classical
input, shared operator, schema used by another chain, lifecycle state, paper
theorem, or release changed, so Tier 3 was unnecessary under the repository
test policy.  The unrelated programme-introduction verifier also has existing
corpus/README failures and is not evidence for this claim.

CLOSE-OUT: DONE -- sampler monoculture is removed and the two-volume proxy is
measured, but the precision step-scaling gate remains inconclusive.

EVIDENCE:
`reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_STEP_SCALING_PREFLIGHT_V1.json`
