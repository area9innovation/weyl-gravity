# Berger 108-row scalar q1 first-jet replay obstruction

The complete scalar 108-row unary has now been composed in the truncated coefficient ring
`Q(sqrt(10))[epsilon_R_squared,kappa]/(epsilon_R_squared^2,kappa^2)` from the pinned base,
memory, emitter, shifted-background and local rod-Hessian overlays.

The replay first found and repaired an interface error in the emitter overlay: covariant
form-valued Euler components had been written directly into density-valued BV cotangent
rows.  Hamiltonian raising through the frozen odd pairing requires `+eta_1` on the Maxwell
antifield equations and `-eta_2` on the emitter antifield equations.  Before this repair,
the zeroth-order unary had 24 nilpotency terms and 102 cyclicity terms.  After it, every
bidegree coefficient is exactly cyclic and the zeroth-order square vanishes.

Two further normalization errors have now been repaired.  Variation with respect to the
covariant symmetric metric component gives `sqrt(-gHat) T^{ab}/2`, not the full stress,
and `q2(Phi2,-)` fixes one ordered input slot rather than summing both symmetric
placements.  The former spatial witness cancels after these repairs.

The full nilpotency result is nevertheless fail-closed.  The `(0,0)`, `(0,1)` and `(1,1)`
coefficients of `q1^2` vanish.  The `epsilon_R_squared` coefficient still has 355 exact PBW
keys, 150 matrix positions and 30,326 coefficient monomials.  Its exhaustive finite Berger
specialization now leaves 374 defects on 54 matrix positions.  A minimal exact witness
occurs at output row 27, Weyl-ghost input row 4, identity input PBW word and target time
mode `-2`.  The coefficient of

```text
x0*x3*cos(sqrt(10)/12)*sin(sqrt(10)/12)^3*detector_time_phase^4
```

is the nonzero rational number `-49/20`.  It decomposes entirely into the two shifted-base
compositions: `q00_base q10_shifted` contributes `49/20`, while
`q10_shifted q00_base` contributes `-49/10`.  The local rod Hessian contributes zero in
the sigma column.  Rescaling the linear radial metric column by each of
`-1,-1/2,0,1/2,1,2` leaves the selected coefficient unchanged.

This localizes the obstruction to the missing second jet of the clock canonical
transformation, or an equivalent action-derived radial/temporal clock-source completion.
The existing rod payload is only linearly clock-dressed.  The complete scalar first-jet
unary gate is therefore `OBSTRUCTED` at pure `epsilon_R_squared` on the current correction
class.  The mixed `epsilon_R_squared*kappa` coefficient itself passes.

This prevents activation of the nonlinear team’s requested apparatus `q2/q3`,
`K_Berger`-equivariance and observer-morphism-stability step.  It also keeps the detector
response on the second-order tangent cone and the physical-branch bridge inactive.  The
next gate is an action-derived export of the second clock-map jet and its cotangent lift,
followed by replay of the displayed Weyl witness.  No finite-parameter causal or quantum
claim is made.
