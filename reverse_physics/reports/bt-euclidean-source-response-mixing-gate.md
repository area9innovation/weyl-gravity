# BT source-response mixing gate

Certificate:
`REVERSE_PHYSICS_BT_EUCLIDEAN_SOURCE_RESPONSE_MIXING_GATE_V1`

Dependency tags: `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`, `REDUCED-MODE`

Lifecycle:
`SOURCE_RESPONSE_KERNEL_PROVED_LOCAL_ONLY_L8_DIAGNOSTIC_REJECTED`

## Result

The physical scalar response is now measured with a Markov move that directly
updates the slow Fourier coordinate.  The move is exactly reversible for the
finite positive BT Gibbs law.  It exposes a large mixing failure in the
local-only diagnostic at (L=8): the two chains agree on action density but
their lowest-mode second moments differ by (6.37) combined block standard
errors.

The local-only value must therefore not be interpreted as generated infrared
tension.  With the complete-mode update, the (L=6) and (L=8) observations
are both within two block errors of the free bilaplacian normalization
(omega_L^2M_2=1).  This supports keeping the full (1/omega_L^2) target in
the Witten/conditional-center analysis.  It is not an equilibration theorem,
a scaling law, or the missing volume-uniform estimate.

## The actual source response

For a mean-zero source (J), define

\[
 Z[J]=\int_H
 \exp\left[-A(\psi)/\lambda^2+\langle J,\psi\rangle\right]d\psi.
\]

Finite-volume coercivity permits differentiation under the integral, giving

\[
 D_J\log Z[J][h]=\mathbb E_J\langle h,\psi\rangle,
\]

and

\[
 \boxed{
 D_J^2\log Z[J][h,k]
 =\operatorname{Cov}_J(\langle h,\psi\rangle,
                         \langle k,\psi\rangle).}
\]

This is the response that the twist functional could not access: the exact
gauge Ward identity makes longitudinal twist response zero, while a scalar
source is not gauge removable.

In the certified flat Schrödinger-potential coordinates, the same observable
is

\[
 F_h(u)=\langle h,\psi(u)\rangle,
 \qquad
 d_uF_h=L_\psi^{-T}h=-\operatorname{diag}(\Omega^2)\phi,
 \qquad B\phi=h.
\]

The pullback-metric connection makes this covector parallel.  Consequently
the electrical Green function is the correct coordinate representation of
the source differential, but it does not itself supply the missing covariance
upper bound.  That bound remains the full Witten inverse or conditional-center
problem.

## Exact complete-mode update

Choose uniformly one of the complete lowest cosine or sine phases (h), draw
(delta) symmetrically from ([-w,w]), and propose

\[
                         \phi'=\phi+\delta h.
\]

Every phase has zero site sum, so the proposal stays on the mean-zero carrier.
The implementation recomputes every residual and the full nonlinear action,
then accepts with

\[
             \min\{1,\exp[-S(\phi')+S(\phi)]\}.
\]

The proposal density is symmetric.  Ordinary Metropolis detailed balance
therefore proves exact finite-volume invariance of the BT law.  This is not an
approximate force or a perturbative mode update.

On the axial four-cycle, take

\[
 \Omega=(1,2,1,1/2),\qquad
 e^{\delta h}=(1,2,1,1/2).
\]

Both vectors have product one, and the proposed field is
(Omega'=(1,4,1,1/4)).  Exact residuals are

\[
 r=(1/2,-1,1/2,2),
 \qquad
 r'=(9/4,-3/2,9/4,6).
\]

The actions per transverse line are (11/4) and (387/16).  Repetition over
the (4^3) transverse sites gives the exact full-lattice action difference

\[
                             \Delta A=1372.
\]

The independent verifier reconstructs this fixture directly from neighbor
ratios rather than using the producer's residual helper.

## Source-response preflight

For every axis, the measured complex mode is

\[
 z_\mu=N^{-1/2}\sum_x\phi_xe^{-2\pi i x_\mu/L},
 \qquad M_2=\mathbb E|z_\mu|^2,
 \qquad \omega_L=4\sin^2(\pi/L).
\]

The free bilaplacian law has (M_2=1/\omega_L^2).  Each row below uses one
fixed seed and ten stored blocks.

| (L) | kernel | samples | (M_2) | (omega_L^2M_2) | action density |
|---:|:---|---:|---:|---:|---:|
| 6 | local + complete mode | 100 | (0.8578\pm0.0774) | (0.8578\pm0.0774) | (0.49387\pm0.00257) |
| 8 | local only | 100 | (1.1663\pm0.0934) | (0.4002\pm0.0321) | (0.49365\pm0.00145) |
| 8 | local + complete mode | 100 | (3.0506\pm0.2804) | (1.0468\pm0.0962) | (0.49737\pm0.00118) |

At (L=8), the action densities differ by only (1.99) combined block
errors, while (M_2) differs by (6.37).  A bulk observable can therefore
look equilibrated even when the slow source coordinate is not.  The complete
mode acceptance rates are (0.748) at (L=6) and (0.792) at (L=8).

The augmented values being close to one is supporting evidence only.  A
single seed, block errors without a certified integrated autocorrelation
analysis, and one augmented architecture cannot establish equilibrium or
distinguish a small anomalous correction from exact bilaplacian scaling.

## Research consequence

The source calculation rules out a tempting false turn.  The positive
expected-Hessian coefficient and the under-mixed local (L=8) chain could
have been read as evidence for an ordinary (1/\omega_L) propagator.  The
corrected diagnostic does not support that inference.  The live analytic
target remains the harder bilaplacian-scale statement:

\[
 \operatorname{Var}\langle h,\phi\rangle
 \lesssim {\|h\|^2\over\omega_L^2},
\]

equivalently the normalized lowest-mode bound already declared by the Witten
and conditional-center certificates.

The next numerical gate is at least four independent seeds plus a genuinely
global second sampler or an autocorrelation-certified background/mode update.
The next analytic gate is not another sampler: prove conditional marginal-
score or full-Witten coercivity at the (omega_L^2) scale, or construct an
actual normalized low-Rayleigh or diverging-moment sequence.

## Boundary

This checkpoint does not establish equilibration of the augmented chain, a
source-susceptibility scaling theorem, a normalized lowest-mode or interacting
(H^{-1}) bound or divergence, tightness, or a continuum Euclidean measure.
It does not change the finite-volume ordinary-OS obstruction and has no Born,
Krein, gravitational, or `LORENTZIAN-CAUSAL` consequence.  Paper 21 is not
changed because no theorem or lifecycle state is promoted.

## Verification

Run under the 500 MB Python cap:

```bash
ulimit -v 500000; python3 reverse_physics/bt_euclidean_source_response_mixing_gate.py --check
ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_source_response_mixing_gate.py
ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_source_response_mixing_gate
ulimit -v 500000; python3 reverse_physics/bt_euclidean_source_response_experiment.py --smoke
```

The three stored production runs completed in 31.54 seconds at 25,444 KiB
peak RSS.  The producer passed 17/17 checks in 0.04 seconds at 21,096 KiB;
the non-importing verifier passed 9/9 in 0.11 seconds at 29,628 KiB; ten
focused and adversarial tests passed in 0.25 seconds at 31,504 KiB; and the
bounded sampler smoke passed in 0.13 seconds at 21,784 KiB.

The planning importer accepted 1,683 nodes with zero invalid items and zero
malformed events in 17.25 seconds at 279,400 KiB under
`GOMEMLIMIT=300MiB` and `GOGC=50`.  The advisory Science Forge wrapper exited
zero in 4.85 seconds at 336,688 KiB, but its bridge audit failed closed because
the external `bp2transformer` verifier lacks `sympy`; it also reported corpus
drift, 1,836 certificates versus baseline 976.  These are failures and drift,
not scientific passes.

Tier 2 checks the unchanged Witten/electrical, canonical-score, and
twist-obstruction inputs by content hash.  Tier 3 is not run because this is a
finite-volume kernel theorem and a numerical mixing preflight, not an
(H^{-1}), reconstruction, freeze, release, shared-core, or Lorentzian
lifecycle promotion.
