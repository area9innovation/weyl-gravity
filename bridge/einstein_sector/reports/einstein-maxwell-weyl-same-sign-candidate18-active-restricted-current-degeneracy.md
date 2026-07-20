# Candidate 18: smooth bounded active-current radicals

## Result

Candidate 18's active `L=3` resonance variety is an affine spectator space
times two rank-one binary-quartic cones.  Its active positive `p_extra(n=1)`
current and negative `q_minus(n=2)` current reduce, after the exact parity
factorization, to

```text
G_positive = [[w_x/12+w_y/4, -w_x/12+w_y/4],
              [-w_x/12+w_y/4, w_x/12+w_y/4]],
G_negative_absolute = 6 h_minus I.
```

Both `w_x` and `w_y` are strictly positive by exact rational interval
certificates.  The two internal eigenlines `z=(1,1)` and `z=(1,-1)` have
positive eigenvalues `w_y/2` and `w_x/6`.  Scaling the negative node by
`t^2=eigenvalue/(6 h_minus)` cancels the current on every transverse angular
variation.

With the common angular carrier `e0=(0,0,1,0,0)`, both rank-one factors are
nonzero proportional pairs and hence smooth.  Every `r` orthogonal to `e0`
gives

```text
delta f = z tensor r,
delta g = t z tensor r,
```

so each family has a four-complex-dimensional fixed-norm projective current
radical.

The active occupation ratio crosses one between exact scalar rays `R1` and
`R3`.  The positive mixture `R3+s18 R1` makes the `p_extra(n=1)` and
`q_minus(n=2)` absolute-current occupations equal.  Choosing `m=0`
spectators kills all rotation moments; the scalar cone kills the time and
circle moments.  The exact bounded fibre-product theorem therefore places
both smooth radical families inside the bounded second-order tangent cone.

## Interpretation and boundary

Candidate 18 is not a global symplectic orbifold on its active bounded
variety.  This completes the existence-level active-current audit for
candidates 17, 18 and 20: all three contain smooth bounded projective current
radicals, although their algebraic mechanisms differ.

This does not classify any complete degeneracy divisor, presymplectic
quotient, connected component, occupation gluing, final residual descent,
all-orders extension, or causal/observational/quantum map.
