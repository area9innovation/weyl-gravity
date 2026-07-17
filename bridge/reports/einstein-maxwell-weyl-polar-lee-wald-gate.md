# Polar Weyl--Maxwell Lee--Wald gate

Result: `GENERIC_POLAR_DIRECT_LEE_WALD_EXTRA_BLOCK_CERTIFIED`.

The certified polar action Hessian was converted to its exact local Green
current on `(A_t,B,C_t,U)`.  The action current is one half of that current
because the stored Hessian represents `2 delta S`.  An independent coordinate
Lee--Wald engine then recomputed every nonzero bilinear entry separately at
`ell=2,3,4`.  The three exact matrices agree with the action current after the
scalar harmonic norms `4 pi/(2 ell+1)` are restored.  The lambda-degree-two
natural-operator bound promotes the match to every physical `ell>=2`.

The entrywise route is load-bearing.  Sphere integration must be applied only
after a left/right amplitude coefficient is isolated.  Feeding one unsplit
amplitude polynomial to the symbolic spherical normalizer can change the
expression through unsafe trigonometric simplification and is explicitly not
used as evidence.

On the extra shell

```text
p=omega_e^2-k^2-lambda+2/3,
```

two polynomial representatives have independence minor

```text
-3 omega_e (6 k^2+3 lambda-2)^2.
```

Their direct positive-frequency Hermitian-current Gram matrix has determinant

```text
9 lambda^2 (lambda-2) (9 lambda-2)
  (3 k^2+3 lambda-2) (6 k^2+3 lambda-2)^2.
```

It is positive definite for every physical `lambda=ell(ell+1)>=6` and every
allowed compact momentum, including `k=0`.  Thus the polar extra block has
inertia `(2,0)`.  Its mixed current with the complete Einstein `q`-primary
summand vanishes exactly modulo `p` and `q`; the Einstein block has inertia
`(1,1)`, so the complete local-gauge-reduced polar target has inertia `(3,1)`.

This certifies a nonradical classical compact extra-mode block and conserved
stationary coefficient extractors before the final residual quotient.  It is
not a residual-survival theorem, a causal or scattering result, a quantum
norm, or a ghost theorem.

## Verification

Fast rails:

```text
python3 -m bridge.einstein_sector.einstein_maxwell_weyl_polar_lee_wald_gate --verify bridge/certificates/einstein_maxwell_weyl_polar_lee_wald_gate.json
python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_polar_lee_wald_gate.py
python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_polar_lee_wald_gate
```

Exhaustive sparse coordinate rail:

```text
python3 -m bridge.einstein_sector.einstein_maxwell_weyl_polar_lee_wald_gate --recompute-direct
```

The exhaustive rail completed the three samples in approximately 409 seconds
in the producing session.  It is separated from the fast commit rail because
full coordinate curvature linearization dominates its runtime.
