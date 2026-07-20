# Candidate-17/20 independent-node-scaling contraction

## Result

The remaining strict opposite-sign wall can be classified exactly when the
two directions of the arbitrary third-transvectant-kernel factor are held
fixed but their amplitudes are scaled independently.

Put

```text
a = omega_minus*B_minus > 0,
b = omega_plus*B_plus > 0,
(x,y) in [0,1]^2,
c(x,y) = delta+a*x-b*y,
M_K(x,y) = -x*U+y*V.
```

Here `x,y` are squared amplitude fractions and
`U=a*mu_f`, `V=b*mu_g` are the fixed weighted node moments.  Exact
occupation transfer preserves both node norms and `T3(f,g)=0`.  The
rotational equation is

```text
M_K(x,y)+c(x,y)*mu_square=0.
```

At the initial point `(1,1)`, `c=alpha`; at the hub endpoint `(0,0)`,
`c=delta`.  Therefore `alpha*delta<0` forces every path to cross `c=0`.
At that crossing the square contribution vanishes, so the kernel moment must
also vanish.  Define the bottleneck incidence

```text
I = {(x,y) in [0,1]^2 : c(x,y)=0, M_K(x,y)=0}.
```

Then a fixed-direction independent-node-scaling contraction exists if and
only if `I` is nonempty.

Necessity is the intermediate-value argument.  Sufficiency is constructive:

1. Move linearly from `(1,1)` to an incidence point.  Both `c` and `M_K`
   scale by the same factor, so the initial square direction cancels them.
2. Hold the incidence point fixed.  Since `c=M_K=0`, move the square moment
   through its certified closed ball to a phase-real value.
3. Move linearly to `(0,0)`.  The kernel moment remains zero and the
   phase-real square direction cancels the remaining coefficient.

The endpoint lies in the connected double-singular hub.

## Exact incidence table

If `U,V` are both nonzero, incidence is possible only when they lie on the
same positive ray.  Writing `V=kappa*U`, `kappa>0`, the sole candidate is

```text
y_* = -delta/(a*kappa-b),
x_* = kappa*y_*.
```

It exists precisely when the denominator is nonzero and both coordinates
belong to `[0,1]`.  If the moment vectors are not positively collinear,
incidence is impossible.

The two one-zero cases are also exact:

```text
U=0, V!=0:  (x_*,y_*)=(-delta/a,0),
U!=0, V=0:  (x_*,y_*)=(0,delta/b),
```

subject in each case to the displayed coordinate lying in `[0,1]`.

Thus generic fixed directions remain obstructed, while an explicit
positive-collinearity locus contracts.  Candidate 17 and candidate 20 are
kept separate; the statement is applied to each candidate's own strict
opposite-sign stratum.

## Boundary

This is a complete classification only of fixed `K` directions with
independent nonnegative node scaling, occupation transfer and an arbitrary
moving common-square direction.  Deformation of the `K` directions inside
`T3(f,g)=0` can change the incidence and remains open.  No complete
off-balance connectedness or disconnection, occupation gluing, final
residual descent, all-orders extension, causal transport, observation or
quantum claim follows.

CLOSE-OUT: SHORTFALL — the fixed-direction ansatz is complete; the genuine
next gate is deformation of the kernel directions.

EVIDENCE:
`bridge/certificates/einstein_maxwell_weyl_same_sign_candidate17_20_independent_node_scaling_contraction.json`
