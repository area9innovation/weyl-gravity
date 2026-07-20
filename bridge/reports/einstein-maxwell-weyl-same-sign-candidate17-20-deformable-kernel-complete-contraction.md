# Candidate-17/20 complete deformable-kernel contraction

## Result

Every fixed-positive-occupation rotation-zero point in the complete
candidate-17 and candidate-20 singular unions contracts to the connected
double-singular hub.

The strict opposite-sign wall is crossed by a constructive three-part path.
The previous component-incidence theorem remains the invariant explanation;
the new result proves that every admissible component meets its incidence.

## Exact spin-two moment damping

In the normalized magnetic basis \(m=-2,\ldots,2\), let

```text
W = diag(1,1/4,1/6,1/4,1)
Theta(f) = R conjugate(f)
R = anti_diag(1,-1,1,-1,1).
```

For the normalized generators, whose spectrum in every spatial direction is
`{-1,-1/2,0,1/2,1}`,

```text
Theta J_a Theta^-1 = -J_a,
(W J_a R)^T = -W J_a R.
```

Thus the normalized moment satisfies `||m(f)||<=||f||_W^2`, time reversal
changes its sign, and the cross moment between `f` and `Theta f` vanishes.
Use a node phase to arrange

```text
sigma = <f,Theta f>_W in [0,1].
```

Then

```text
f_theta =
  [cos(theta) f + sin(theta) Theta f]
  /sqrt(1+sigma sin(2 theta)),

m(f_theta) =
  cos(2 theta)/(1+sigma sin(2 theta)) m(f).
```

The scalar multiplier decreases monotonically from one to zero for
`0<=theta<=pi/4`. The endpoint is phase-real and has zero rotation moment.

## Convex one-node deletion

Write

```text
c = delta+a*x-b*y,
M_K = -a*m(F)+b*m(G),
alpha = delta+a-b.
```

### Negative delta, positive alpha

Scale only the positive node:

```text
F fixed,
G_t=sqrt(t)G,
c(t)=(1-t)(delta+a)+t alpha > 0.
```

The moment is affine. Initial admissibility and the unit moment bound give

```text
||M(0)|| <= ||M(1)||+b||m(G)||
          <= alpha+b
           = delta+a
           = c(0).
```

Convexity of the norm therefore proves `||M(t)||<=c(t)` on the whole
segment. At `G=0`, the equation `T3(F,0)=0` is automatic. Apply the
time-reversal homotopy to `F`, then scale the phase-real survivor through

```text
||F||_W^2=-delta/a
```

and onward to the hub.

### Positive delta, negative alpha

Scale only the negative node:

```text
G fixed,
F_t=sqrt(t)F,
-c(t)=(1-t)(b-delta)+t(-alpha) > 0.
```

Now

```text
||M(0)|| <= ||M(1)||+a||m(F)||
          <= -alpha+a
           = b-delta
           = -c(0).
```

The same convexity argument applies. With `F=0`, damp the moment of `G` and
scale the phase-real survivor through

```text
||G||_W^2=delta/b.
```

In both cases the required common-square moment stays in its certified unit
ball. After the survivor reaches zero moment, the wall is crossed with
`M_K=0` and a fixed phase-real square direction.

## Complete assembly

- Candidate 17 has `delta<0` everywhere. Its `alpha<=0` strata were already
  contracted by the repaired moving-square theorem; the new path covers
  `alpha>0`.
- Candidate 20 on `delta=0` was already covered by the balanced radial
  theorem.
- Candidate 20 off balance has `alpha*delta>0` and `alpha=0` covered by the
  moving-square theorem; the new path covers `alpha*delta<0`.

Therefore both complete singular components on both candidates contract to
their connected hub at every fixed positive active occupation.

## Boundary

This closes fixed-occupation singular rotation-zero topology. It does not
identify candidates 17 and 20, glue distinct total-occupation strata,
construct a global Hausdorff quotient outside this carrier, perform final
residual descent, prove an all-orders solution, or establish causal,
observational or quantum claims.

EVIDENCE:
`bridge/certificates/einstein_maxwell_weyl_same_sign_candidate17_20_deformable_kernel_complete_contraction.json`
