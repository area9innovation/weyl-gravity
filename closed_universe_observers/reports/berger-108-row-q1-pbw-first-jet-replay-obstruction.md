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

The full nilpotency result is nevertheless fail-closed.  The `(0,0)`, `(0,1)` and `(1,1)`
coefficients of `q1^2` vanish.  The `epsilon_R_squared` coefficient has 355 exact PBW keys,
150 matrix positions and 30,326 coefficient monomials.  It remains nonzero after the
certified finite Berger background specialization.  A minimal exact witness occurs at
output row 27, input row 0, identity input PBW word and target time mode zero.  Its `x0*x1`
coefficient is

```text
-27*s^4/40 + 27*s^2/32 - 2921/480,
s = sin(sqrt(10)/12).
```

Because `0 < s^2 < 10/144 = 5/72`, this coefficient is strictly smaller than
`(27/32)(5/72)-2921/480 < 0`.  The complete scalar first-jet unary gate is therefore
`OBSTRUCTED` at pure `epsilon_R_squared` on the current correction class.  The mixed
`epsilon_R_squared*kappa` coefficient itself passes.

This prevents activation of the nonlinear team’s requested apparatus `q2/q3`,
`K_Berger`-equivariance and observer-morphism-stability step.  It also keeps the detector
response on the second-order tangent cone and the physical-branch bridge inactive.  The
next gate is a localized repair of the shifted-gravity/rod-memory first-jet composition,
followed by replay of the displayed witness.  No finite-parameter causal or quantum claim
is made.
