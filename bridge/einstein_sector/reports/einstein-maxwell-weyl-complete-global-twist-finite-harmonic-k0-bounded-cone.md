# Complete finite-harmonic global/twist bounded cone at rest

For an arbitrary finite set of generic `ell>=2` wave blocks at `k=0`, the
complete standard-global bounded second-order cone is

```text
wave=0:  a=b=Q_e=B=0; c,d,W_x,A arbitrary,
wave!=0: a=b=d=Q_e=B=0; c,W_x,A arbitrary; total mu_H=mu_J_i=0.
```

The new step is finite additivity.  Writing `u_wave=sum_ell u_ell`, bilinearity
gives `D2E[A,u_wave]=sum_ell D2E[A,u_ell]`.  Each summand has zero same-shell
projection and bounded inverses in its neighboring angular outputs.  Even if
two summands reach the same output carrier, the sum of their corrections
solves the summed source because the second-order operator is linear.  No
blockwise moment-map condition is needed for this mixed column.

The wave--wave source, including all cross-`ell` products, is independently
solved by the finite-harmonic theorem on the total compact stabilizer zero
cone.  The global pivots and transport theorems then assemble exactly as in
the one-fixed-`ell` successor.

Infinite harmonic completion, exceptional wave inputs, nonzero momentum,
causal propagation and higher lifecycles remain fail-closed.
