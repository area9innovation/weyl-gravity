# BT two-scale round-tower obstruction

**Certificate:**
REVERSE_PHYSICS_BT_EUCLIDEAN_TWO_SCALE_ROUND_TOWER_OBSTRUCTION_V1

**Dependency tags:** LOCAL-ALGEBRAIC, EUCLIDEAN-SPECTRAL,
REDUCED-MODE

## Result

The canonical same-center tower made from two round conformal bubbles cannot
collapse the normalized BT Euler-gradient quotient. Its Euler cost diverges
as the inverse square of the scale ratio.

On \(\mathbb R^4\), put \(t=r^2\) and

\[
 \Omega_\varepsilon(t)
 =\frac{2\varepsilon}{t+\varepsilon^2}+\frac2{t+1},
 \qquad 0<\varepsilon<1.
\]

The two summands are round bubbles of radii \(\varepsilon\) and one. For

\[
 R_\varepsilon=\frac{\Delta\Omega_\varepsilon}{\Omega_\varepsilon},
 \qquad
 q_\varepsilon=\frac{R_\varepsilon}{\Omega_\varepsilon^2},
 \qquad
 E_\varepsilon=\operatorname{div}
   (\Omega_\varepsilon^2\nabla q_\varepsilon),
\]

exact radial analysis gives

\[
 \|E_\varepsilon\|_2^2
 =\frac{9216\pi^2}{5}\varepsilon^{-2}
  +o(\varepsilon^{-2}),
\]

while

\[
 \|R_\varepsilon\|_2^2\longrightarrow\frac{64\pi^2}{3}.
\]

Therefore

\[
 \boxed{
 \frac{\|E_\varepsilon\|_2^2}{\|R_\varepsilon\|_2^2}
 =\frac{432}{5}\varepsilon^{-2}+o(\varepsilon^{-2})
 \longrightarrow\infty.}
\]

The exact round bubble is critical by itself. Adding a much larger round
bubble looks like a small constant perturbation in the inner core, but the
fourth-order Euler operator magnifies that perturbation into a power-cost
neck.

## Exact radial algebra

For a radial function of \(t=r^2\),

\[
 \Delta f=4t f''+8f',\qquad
 E=\frac4t\frac{d}{dt}\left(t^2\Omega^2q'\right).
\]

Write

\[
 a=\varepsilon(t+1),\qquad b=t+\varepsilon^2.
\]

The numerator arising from the two bubble Laplacians contains

\[
 a^3+b^3=(a+b)(a^2-ab+b^2).
\]

Since \(a+b=(1+\varepsilon)(t+\varepsilon)\), cancellation gives

\[
 q_\varepsilon(t)=
 -2\frac{d(t^2+\varepsilon^2)+ct}
 {(1+\varepsilon)^2(t+\varepsilon)^2},
\]

where

\[
 d=\varepsilon^2-\varepsilon+1,\qquad
 c=4\varepsilon^2-\varepsilon^3-\varepsilon.
\]

One differentiation collapses further:

\[
 q_\varepsilon'(t)=
 -6\frac{\varepsilon(1-\varepsilon)^2(t-\varepsilon)}
 {(1+\varepsilon)^2(t+\varepsilon)^3}.
\]

These are exact rational identities, not formal series.

## Inner-scale profile

Set

\[
 t=\varepsilon^2u.
\]

At fixed \(u\),

\[
 \Omega_\varepsilon(\varepsilon^2u)
 =\frac2\varepsilon\left[\frac1{1+u}
 +\varepsilon+O(\varepsilon^3u)\right],
\]

and the exact formula for \(q\) gives

\[
 q_\varepsilon(\varepsilon^2u)
 =-2+6\varepsilon(1+u)
 +O(\varepsilon^2(1+u)^2).
\]

Substitution into the radial Euler operator yields the limiting profile

\[
 \varepsilon^3E_\varepsilon(\varepsilon^2u)
 \longrightarrow\frac{192}{(1+u)^3}.
\]

The four-dimensional radial measure is

\[
 2\pi^2r^3\,dr=\pi^2t\,dt.
\]

Hence the inner contribution to
\(\varepsilon^2\|E_\varepsilon\|_2^2\) tends to

\[
 \pi^2\,192^2
 \int_0^\infty\frac{u\,du}{(1+u)^6}
 =\pi^2\,192^2\frac1{20}
 =\frac{9216\pi^2}{5}.
\]

The exact rational formula supplies an integrable majorant after splitting
the \(u\)-axis at fixed large radius; the transition and outer regions vanish
after multiplication by \(\varepsilon^2\).

## Residual energy

At the inner scale,

\[
 R_\varepsilon(\varepsilon^2u)
 \sim-\frac8{\varepsilon^2(1+u)^2}.
\]

Therefore its residual energy tends to

\[
 64\pi^2\int_0^\infty\frac{u\,du}{(1+u)^4}
 =\frac{32\pi^2}{3}.
\]

At fixed outer scale the inner bubble disappears and the radius-one bubble
contributes the same value. The transition cross terms vanish, giving
\(64\pi^2/3\) in total.

## Meaning for the barrier

Three standard concentration mechanisms now fail:

- fixed finite repaired bubble splitting;
- a synchronized repaired gas with count proportional to volume;
- the canonical two-round-bubble same-center tower.

The tower result is deliberately scoped to the exact radial \(\mathbb R^4\)
family. A periodized tower could add bounded gluing terms, which cannot cancel
the displayed \(\varepsilon^{-2}\) coefficient, but that gluing statement is
not proved here. Arbitrary non-round towers and neck profiles also remain
open.

The main analytic target is still the connection-corrected Witten/Schur
estimate or a controlled low-Rayleigh sequence.

## Boundaries

No periodized-tower theorem, arbitrary tower classification, all-field
gradient bound, Witten/Poincare theorem, interacting Gibbs \(H^{-1}\)
estimate, continuum measure, Born rule, Krein reconstruction, or
LORENTZIAN-CAUSAL statement is established.

## Verification

~~~bash
ulimit -v 500000; python3 reverse_physics/bt_euclidean_two_scale_round_tower_obstruction.py --check
ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_two_scale_round_tower_obstruction.py
ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_two_scale_round_tower_obstruction
~~~

The producer check, independent verifier, and ten focused tests passed in
0.04, 0.10, and 0.12 seconds, using at most 20,512, 29,544, and 30,572 KiB.
The two direct predecessor verifiers passed in 0.10 seconds each. The planning
import folded 1,657 nodes with no invalid item or malformed event in 6.95
seconds under a 300 MiB Go limit. Tier 3 was not run because this is a radial
family obstruction, not an all-field Witten/\(H^{-1}\) promotion, freeze, or
release.
