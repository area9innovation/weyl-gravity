# Berger complex-clock local anomaly complex

## Result

On the regular formal polar chart `rho != 0`, the actual positive-Berger
two-scalar clock theory has

```text
H^{1,4}_even(s|d) = 0
H^{1,4}_odd(s|d)  = 0
```

with dependency tag `LOCAL-ALGEBRAIC`.  The action-derived covariant BV export
contains the complete minimal and nonminimal rows.  With
`tau=-log(rho/f)` and `g_hat=(rho/f)^2 g`, the four generators
`(tau, omega, omega_star, tau_hat_star)` form an exact quartet, including all
finite jets.  The quotient therefore reduces to the four-dimensional Diff BV
complex of `g_hat` and the nonchiral phase scalar `theta`; its ghost-one local
anomaly space vanishes on the declared regular Euler--Lagrange chart.

The phase-shift current is the only additional antifield-number-one
characteristic class introduced by the clock.  Its possible ghost-number-one
lift requires a scalar pure-ghost-number-two cocycle.  The independent exact
Chevalley--Eilenberg control has ranks `rank(d1)=6`, `rank(d2)=9` in the
15-dimensional two-cochain space, hence `H2(so(3,1)_C,Q)=0`; the current does
not create an antifield-dependent anomaly.

The familiar representatives `omega C2`, `omega E4`, `omega CdualC`, and
`omega BoxR` are all exact in this changed theory.  More generally,
`omega I_hat(g_hat,theta)` has primitive `tau I_hat` with its universal Diff
completion.

## Strict-versus-coupled action complexes

There is still no BV action-complex restriction from strict pure Weyl gravity
to this Berger solution.  The constant-term functional separates the two
complexes:

```text
epsilon_0 Q_target = 0
epsilon_0 j Q_source(gstar_00) = 961/1920
```

This proves nonexistence for every unit-preserving local-analytic background-
jet morphism regular at zero fluctuation, even when arbitrary field/antifield
mixing is allowed.  No `961/1920` term was subtracted.  The zero anomaly
quotient is a result about the actual matter-coupled theory, not a repaired
pullback of the strict theory.

## Claim boundary

No gravity-clock anomaly coefficient was computed, and its QME was not
restored.  Raw `D` is affine rather than a linear symmetry of the fixed clock
background; `K_Berger` is a rigid background symmetry, not a local gauge
ghost.  Its quantum Cartan disposition remains open.  Maxwell, global
`rho=0` strata, Lorentzian products, Hadamard states, positivity, particles,
scattering, and unitarity are outside this certificate.

Proof digest: `51c0607f6c9f5e596b2d5b46b92da9a073530e14e06100ac4511067a89464353`.

EVIDENCE: quantum-weyl/anomalies/certificates/BERGER_COMPLEX_CLOCK_LOCAL_ANOMALY_COMPLEX_V1.json

CLOSE-OUT: DONE — the actual positive-Berger complex-clock local anomaly
complex is classified on the declared regular formal polar chart; the strict
action-complex map remains obstructed by the exact `961/1920` separator.
