# BT additive flow-rate obstruction

**Certificate:**
REVERSE_PHYSICS_BT_EUCLIDEAN_ADDITIVE_FLOW_RATE_OBSTRUCTION_V1

**Dependency tags:** LOCAL-ALGEBRAIC, EUCLIDEAN-SPECTRAL,
REDUCED-MODE

## Result

The certified additive contraction proves that every finite-volume BT action
sublevel retracts to the vacuum.  It does not have a field-uniform
exponential decay rate, even at fixed volume.

On an axial six-cycle, replicated over the other three coordinates of the
\(6^4\) torus, put

\[
 \Omega_m=(x,x^{-3},x^{-3},x^{-3},x,x^7),
 \qquad x=2^m.
\]

The product of the six entries is one, so this is already in geometric-mean
gauge.  Its residual is

\[
 r=(R,S,0,S,R,T),
\]

where

\[
 R=x^6+x^{-4}-2,\qquad
 S=x^4-1,\qquad
 T=2x^{-6}-2.
\]

For the unnormalized additive vector field \(X=P_H\Omega^{-1}\), the exact
action dissipation is

\[
 -X\cdot\nabla A=D:=\sum_i\frac{r_i^2}{\Omega_i}.
\]

The leading Laurent terms are

\[
 \|r\|^2\sim2x^{12},\qquad D\sim4x^{11}.
\]

Since \(A=\|r\|^2/2\),

\[
 \boxed{\frac{-X\cdot\nabla A}{A}\sim\frac4x\longrightarrow0.}
\]

The bounded normalized flow
\(X_1=P_H\pi\), with
\(\pi_i=\Omega_i^{-1}/W\), is even slower.  Since

\[
 W=\sum_i\Omega_i^{-1}\sim3x^3,
\]

its relative decay obeys

\[
 \boxed{\frac{-X_1\cdot\nabla A}{A}
 \sim\frac4{3x^4}\longrightarrow0.}
\]

Thus the global homotopy cannot be promoted directly to a uniform
quantitative Lyapunov or Poincaré estimate.

## This is not an almost-stationary field

The producer also differentiates the actual action in the ordinary Euclidean
log-field metric.  Its squared gradient has leading term

\[
 \|\nabla A\|^2\sim6x^{24},
\]

and therefore

\[
 \boxed{\frac{\|\nabla A\|^2}{\|r\|^2}
 \sim3x^{12}\longrightarrow\infty.}
\]

The same configurations that move slowly under the specially chosen additive
homotopy become increasingly steep for the actual Euclidean gradient flow.
They are not a low-Rayleigh or almost-stationary sequence for the Witten
problem.

This distinction matters.  Recent work relating global gradient-flow
optimization to Poincaré inequalities assumes quantitative control of the
actual gradient flow and a low-temperature regime whose inverse temperature
scales at least with dimension; see Chen and Sridharan,
[*Optimization, Isoperimetric Inequalities, and Sampling via Lyapunov
Potentials*](https://proceedings.mlr.press/v291/chen25g.html) (COLT 2025).
The BT additive homotopy is a different vector field, its uniform relative
rate fails by the exact family above, and the physical
\(\lambda=2/5\) inverse temperature does not grow like the
\(N-1\)-dimensional carrier.  That theorem is therefore not imported as a BT
Poincaré result.

## Meaning for the continuum programme

In normal language: we know a road from every field configuration to the
vacuum, but this family shows that traffic on that particular road can become
arbitrarily slow.  This says nothing bad about the slope of the actual BT
landscape—the slope becomes enormous here.  Contractibility is topological
information; a spectral gap needs a quantitative metric estimate.

The surviving deterministic question is the one already isolated by the
unique-critical-point certificate:

\[
 \gamma_L=\inf_{\psi\ne0}
 \frac{\|\nabla A(\psi)\|^2}
      {\omega_L^2\|r(\psi)\|^2}.
\]

A positive volume-uniform lower bound for \(\gamma_L\), or a genuine
collapsing sequence, would decide the actual-gradient fork.  Even a positive
answer would still need a separate Gibbs/Witten bridge before it could bound
the lowest Fourier mode.  The direct formulations remain the
connection-corrected Witten form and the translation-invariant conditional
current susceptibility.

No normalized lowest-mode theorem, interacting \(H^{-1}\) estimate,
continuum measure, Born rule, Krein reconstruction, or
LORENTZIAN-CAUSAL statement is established.

## Verification

Run sequentially:

    ulimit -v 500000; python3 reverse_physics/bt_euclidean_additive_flow_rate_obstruction.py --check
    ulimit -v 500000; mise x python@3.12 -- python3 reverse_physics/verify_bt_euclidean_additive_flow_rate_obstruction.py
    ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_additive_flow_rate_obstruction

## Verification receipt

- Tier 0 and scoped Tier 1 results are recorded in the machine certificate
  committed with this report.  The planning import accepted 1,688 nodes with
  zero invalid items and zero malformed events in 6.53 s.
- The producer uses exact integer Laurent arithmetic.  The independent
  verifier instead constructs the residual and full Jacobian directly in
  SymPy, differentiates the action, checks the stored rational fixtures, and
  evaluates all three limits symbolically.  The producer passed in 0.04 s at
  20,816 KB peak RSS, the verifier in 0.74 s at 73,776 KB, and seven tests in
  0.04 s at 21,356 KB.  The verifier's first 0.63 s invocation used structural
  rather than algebraic expression comparison; it was corrected and rerun
  from the start, and that failed invocation is not counted as a pass.
- The 2.96 s advisory Science Forge wrapper exited zero, but its external
  bridge audit failed closed because that Python lacks SymPy; its census also
  reported baseline drift (1,849 certificates versus 976).  Those findings
  are failures/drift, not evidence for this result.
- Tier 2 uses content hashes for the unchanged additive-contraction and
  unique-critical-point certificates.
- Tier 3 is not required: this is a proof-route obstruction, not an
  \(H^{-1}\), continuum, reconstruction, freeze, release, or shared-core
  lifecycle promotion.
- Paper 21 is not changed because the continuum estimate and lifecycle state
  remain open.
