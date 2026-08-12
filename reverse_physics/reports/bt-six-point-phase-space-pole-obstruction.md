# BT six-point physical phase-space pole obstruction

Certificate: `REVERSE_PHYSICS_BT_SIX_POINT_PHASE_SPACE_POLE_OBSTRUCTION_V1`

Dependencies: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`. Lifecycle:
`COEFFICIENT_COMPUTED`.

## Result

The complete six-point local BT tree density is strictly positive on the
regular physical phase space, but its ordinary exclusive phase-space integral
does not exist. A positive transverse double pole occurs at an exact interior
physical point. Consequently no principal-value sign cancellation can repair
the tree integral; a detector resolution, distributional completion, or
inclusive real--virtual prescription is mandatory.

Let (y_A=1/s_A) for the ten unordered three-particle channels. The universal
coefficient formula gives

\[
 D=2\sum_S c_S^2
  =\left(\sum_A y_A\right)^2+\frac18\sum_A y_A^2.
\]

If only (s_B\) tends to zero, then

\[
 D=\frac{9}{8s_B^2}+O(s_B^{-1}).
\]

This leading coefficient is positive and universal.

On the exact five-coordinate chart, take

\[
 (a,b,t,u,v)=(2,-2,3/5,1/2,1/3).
\]

All outgoing energies are ((6/5,1,1)). Exactly one channel, mask (11),
vanishes; the other nine are nonzero. On the transverse (t)-line,

\[
 s_{11}(t)=-\frac{36(5t-3)(13t+5)}{625(1+t^2)},\qquad
 \partial_t s_{11}\big|_{t=3/5}=-\frac{1152}{425}.
\]

The full chart still has rank five, with nonzero minor
(-8957952/112890625). Therefore the phase-space measure is locally smooth
and nonvanishing, while

\[
 D=\frac{180625}{1179648}\frac1{(t-3/5)^2}
   +O((t-3/5)^{-1}).
\]

The integral over every neighborhood crossing this hypersurface diverges
positively. This is not a failure of the local sign theorem; it is the precise
reason that local positivity is not yet a physical normalized probability.

The result does not select a regulator or finite part, compute detector
resolution, combine real and virtual terms, prove KLN cancellation, construct
Eq. (19), treat loops, lift to metric BV--BRST, or establish anything
`LORENTZIAN-CAUSAL`.

CLOSE-OUT: DONE -- a unique transverse physical channel gives an exact positive double-pole obstruction to the ordinary exclusive integral.
EVIDENCE: reverse_physics/certificates/REVERSE_PHYSICS_BT_SIX_POINT_PHASE_SPACE_POLE_OBSTRUCTION_V1.json
