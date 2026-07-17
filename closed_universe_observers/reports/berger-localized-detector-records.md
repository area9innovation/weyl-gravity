# Hardened Berger detector-record preflight

## Result

The detector layer now certifies the objects needed before computing a
retarded response.  It does not call an unevaluated Green function a click.

First, each detector carries three standard-sign probe rod scalars with

\[
S_R=-\frac12\sum_{I=1}^3\int
\sqrt{-\widehat g}\,\widehat g^{ab}\partial_aR^I\partial_bR^I.
\]

On the detector clock slice their Cauchy data are `R^I=x^I` and
`n(R^I)=0`.  The normally hyperbolic scalar Cauchy theorem supplies local
solutions.  Both relational Jacobians are exactly `I_4`, so continuity gives
open neighborhoods on which

\[
d\Theta\wedge dR^1\wedge dR^2\wedge dR^3\ne0.
\]

Each compact smearing support is selected inside the intersection of such a
neighborhood and its nominal detector ball.  Continuity certifies some
nonzero support there, not nondegeneracy throughout the full declared
numerical-radius ball.  This is a local probe-rod theorem, not a backreacting
global material coordinate system.

## Smearings and independence

The detector centers lie on one no-wrap Hopf chart:

\[
(\tau_0,L_0)=(3/16,1/4),\qquad
(\tau_1,L_1)=(3/8,1/2),\qquad \Theta=(3/4)t.
\]

For an emitter center at `(Theta,L)=(0,0)`, both exact null-incidence
residuals `tau_a-(3/4)L_a` vanish.  Moreover

\[
0<L_a<\frac94<2\pi c=\frac{3\sqrt{10}\pi}{10},
\]

so the central Hopf rays are below the half-fibre cut locus.  This proves
central no-wrap incidence only; full compact-support incidence remains part
of the response calculation.

At each center define a smooth compact spacetime smearing inside the local
rod neighborhood,

\[
Q_a[F]=\int \rho_a(\Theta,R)
 \langle F,P_a\rangle_{\widehat g}\,d\operatorname{vol}_{\widehat g},
\]

with `P_0=dTheta wedge dR1` and `P_1=dTheta wedge dR2`.  Compact Maxwell test
fields `H_a` are chosen inside the detector windows and normalized by
`Q_a[H_a]=1`.  Cross pairings vanish because the spacetime supports are
disjoint.  The derived matrix is

\[
(Q_a[H_b])=I_2.
\]

The earlier label-based `probe_supports` input has been removed.  Five
mutations now destroy, separately, rod nondegeneracy, clock-label separation,
null incidence, no-wrap geometry, and smearing independence.

## Persistent probe records

Each smearing drives a first-order memory register with response action

\[
S_{\rm mem}=\sum_a\int p_a
  \bigl(\partial_\Theta m_a-q_a(\Theta;F)\bigr)d\Theta.
\]

Here `q_a(Theta;F)` is the clock-time drive whose integral is `Q_a[F]`.
Thus `partial_Theta m_a=q_a(Theta;F)` and `partial_Theta p_a=0`.  On the
probe branch `p_a=0`, the Maxwell field receives no detector force.  Starting
from zero memory, `m_a=Q_a[F]` after the detector window and remains constant.
These are persistent probe records; apparatus recoil and backreaction remain
open.

## Correct next gate

The next object is not a pointwise Green-kernel value and not two nonzero
numbers from one pulse.  Predeclare two compact conserved emitter currents
and compute the smeared transfer matrix

\[
M_{ab}=Q_a[dG_{\rm ret}J_b].
\]

Promotion requires a nonzero exact determinant or rank-two minor, full
source-support-to-window causal/no-wrap witnesses, and the same matrix in the
memory registers.  Detector locations, polarizations, sources, and
normalizations may not be selected after seeing the responses.

The new gate is
`BERGER_SMEARED_RETARDED_TWO_SOURCE_TWO_DETECTOR_TRANSFER`.

## Dependency and claim boundary

Every classical dependency is replayed from snapshot
`fc7a680d32d23d516a1c29c54ae1e0734d532a75`; current files are checked
separately through required compatibility flags.  A later compatible claim
boundary update therefore does not make this certificate stale.

The probe smearings are Diff-covariant, Weyl invariant through `gHat`, and
Maxwell-gauge invariant because they depend on `F`.  Raw-`D` and
`K_Berger` descent remain open because the rod-memory sector is not in the
imported phase space or interacting complex.  No quantum claim is made.

Verification:

```bash
python3 closed_universe_observers/generate_berger_detector_records.py --check
python3 closed_universe_observers/verify_berger_detector_records.py
python3 -m pytest -q closed_universe_observers/tests/test_berger_detector_records.py
```
