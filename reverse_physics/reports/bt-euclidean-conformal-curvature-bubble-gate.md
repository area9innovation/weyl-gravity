# BT conformal-curvature bubble gate

**Certificate:**
`REVERSE_PHYSICS_BT_EUCLIDEAN_CONFORMAL_CURVATURE_BUBBLE_GATE_V1`

**Dependency tags:** `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`,
`REDUCED-MODE`

## Result

The four-dimensional continuum BT action has an exact geometric identity.  If
(g=\Omega^2\delta), (R=\Delta\Omega/\Omega), and
(A=\frac12\int R^2dx), then

\[
 \operatorname{Scal}_g=-6\Omega^{-2}R,
 \qquad
 \int \operatorname{Scal}_g^2d\operatorname{vol}_g=72A.
\]

Thus the BT functional is scalar-curvature-squared restricted to conformally
flat metrics.  It is not the Weyl-tensor-squared action.

This identification exposes a genuine nonperturbative mechanism.  The
stereographic round four-sphere is an exact finite-action critical bubble on
\(\mathbb R^4\).  Adding a positive constant floor gives a smooth family whose
action approaches the bubble action while its Euler-gradient quotient tends
to zero.  Finite-volume uniqueness therefore does not by itself imply the
compactness needed for a uniform estimate: critical points can escape through
scale and the boundary of positive-field space.

The calculation does **not** yet break the torus barrier.  Matching the bubble
transition radius to a torus of side (L) makes the quotient scale as
(L^{-4}), exactly the free lowest-mode scale, with a nonzero formal normalized
coefficient.  Periodic gluing contributes at that same order.  A controlled
periodic construction or a compactness theorem is still required.

## Exact conformal identity

For a conformal change (g=\Omega^2\delta) in four dimensions,

\[
 \operatorname{Scal}_g=-6\Omega^{-3}\Delta\Omega,
 \qquad d\operatorname{vol}_g=\Omega^4dx.
\]

Since (R=\Delta\Omega/\Omega=\Delta\psi+|\nabla\psi|^2), the powers of
\(\Omega\) cancel:

\[
 \int \operatorname{Scal}_g^2d\operatorname{vol}_g
 =36\int R^2dx=72A.
\]

The Euler gradient of (A) in the flat (L^2(d x)) metric on
\(\psi=\log\Omega\) is

\[
 E=\Delta R-2\operatorname{div}(R\nabla\psi)
  =\operatorname{div}\!\left[\Omega^2\nabla(R/\Omega^2)\right].
\]

This weighted-current form is the continuum version of the lattice
conductance/corrector gate.

## Exact round-sphere critical bubble

For every \(\rho>0\), put

\[
 \Omega_\rho(x)=\frac{2\rho}{|x|^2+\rho^2}.
\]

Radial differentiation in four dimensions gives

\[
 \Delta\Omega_\rho=-2\Omega_\rho^3,
 \qquad
 R_\rho=-2\Omega_\rho^2
       =-\frac{8\rho^2}{(|x|^2+\rho^2)^2}.
\]

Hence (R_\rho/\Omega_\rho^2=-2), (E=0), and the conformal metric has
constant scalar curvature (12).  Exact radial integration gives

\[
 \int_{\mathbb R^4}R_\rho^2dx=\frac{32\pi^2}{3},
 \qquad
 A[\Omega_\rho]=\frac{16\pi^2}{3},
\]

independent of \(\rho\).  This is the stereographic round (S^4).  It is a
noncompact critical family, not a positive periodic field on a finite torus.

## Positive-floor approach to the bubble

Set

\[
 B=\frac{\rho}{|x|^2+\rho^2},\qquad
 \Omega=a+B,\qquad
 t=1+\frac{|x|^2}{\rho^2},\qquad
 \epsilon=a\rho,
\]

with (a,\rho>0).  Since (\Delta B=-8B^3), direct calculation yields

\[
 R=-\frac{8\rho^{-2}}{t^2(1+\epsilon t)},
 \qquad
 \frac{R}{\Omega^2}=-\frac8{(1+\epsilon t)^3},
\]

and

\[
 E=\frac{192\epsilon\rho^{-4}
 (1+2\epsilon t-\epsilon t^2)}
 {t^3(1+\epsilon t)^3}.
\]

After angular integration, (dx=\pi^2\rho^4(t-1)dt), so

\[
 \|R\|_2^2=64\pi^2\int_1^\infty
 \frac{t-1}{t^4(1+\epsilon t)^2}\,dt
 \longrightarrow\frac{32\pi^2}{3},
\]

while

\[
 \frac{\rho^2}{a^2}\|E\|_2^2
 \longrightarrow\frac{9216\pi^2}{5}.
\]

The constants use the exact integrals

\[
 \int_1^\infty\frac{t-1}{t^4}dt=\frac16,
 \qquad
 \int_1^\infty\frac{t-1}{t^6}dt=\frac1{20}.
\]

The gradient limit is not a formal interchange over an unbounded interval.
For (0<\epsilon\leq1), split the integral at (t=1/\epsilon).  Below the
split its dimensionless integrand is bounded by (16t^{-3}) and converges
pointwise.  Above the split, its integral is at most
(\frac83\epsilon^2).  Dominated convergence on the first part and the tail
bound prove the displayed limit.  The residual integrand is directly bounded
by ((t-1)t^{-4}).

Consequently

\[
 \frac{\|E\|_2^2}{\|R\|_2^2}
 =\frac{864}{5}\left(\frac a\rho\right)^2(1+o(1)).
\]

This is a precise critical-at-infinity sequence on \(\mathbb R^4\).  The
independent verifier reconstructs the residual and weighted divergence by a
separate radial-calculus implementation and checks two exact rational points.

## Why this does not yet make a torus counterexample

The floor and bubble are comparable at radius
(R_{\rm tr}\sim\sqrt{\rho/a}).  If this is matched to a box scale (L), then
(a/\rho=L^{-2}), and formally

\[
 \frac{\|E\|_2^2}{\|R\|_2^2}
 \sim\frac{864}{5L^4}.
\]

The free lowest-mode coefficient is
((2\pi/L)^4=16\pi^4L^{-4}), giving the formal ratio

\[
                         \frac{54}{5\pi^4}.
\]

That number is informative but not certified as a torus quotient.  The
periodic correction lives where the floor and bubble meet, precisely the
region that contributes at order (L^{-4}).  A naive minimum-image profile
also has a seam and is not admissible.  Boundary topology therefore affects
the leading coefficient rather than a negligible remainder.

## Consequence for the research programme

The earlier finite-graph theorem remains intact: every finite connected graph
has one critical orbit and contractible action sublevels.  The new result says
why that fact is insufficient for a growing-volume estimate.  The sequence can
leave every compact part of the gauge-fixed positive-field space while
retaining finite action and approaching a noncompact critical geometry.

The next deterministic gate is now concrete: construct a smooth periodic
Green-function bubble and compute its complete (L^{-4}) coefficient, or prove
a quantitative compactness theorem modulo the one-bubble profile.  Only after
that calculation should a candidate be inserted into the full Witten
one-form Rayleigh quotient.  Deterministic gradient geometry alone does not
control the actual Gibbs (H^{-1}) moment.

## Boundaries

This result does not establish a periodic low-gradient sequence, failure of a
positive volume-uniform torus constant, Witten or Poincare failure, an actual
Gibbs moment bound or divergence, tightness, continuum identification, a Born
rule, Krein reconstruction, or anything `LORENTZIAN-CAUSAL`.

## Verification

```bash
ulimit -v 500000; python3 reverse_physics/bt_euclidean_conformal_curvature_bubble_gate.py --check
ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_conformal_curvature_bubble_gate.py
ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_conformal_curvature_bubble_gate
```

The measured scoped times were (0.05), (0.14), and (0.17) seconds,
respectively.  The repository-wide planning conformance command refused after
9.7 seconds on ten pre-existing `forge-requests` lifecycle states; the new
sequence-45 event itself validated.  The advisory Science Forge shadow run was
not counted as a pass: it was stopped after more than 75 seconds when unrelated
indexing subprocesses aborted under the memory ceiling before producing an
audit disposition.
