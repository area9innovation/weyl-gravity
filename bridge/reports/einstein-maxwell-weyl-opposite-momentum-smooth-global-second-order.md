# Paired opposite-momentum smooth-global second-order cone

Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`.

## Theorem

Fix one generic input `ell>=2` and one nonzero allowed `|k|`.  Include all
`m`, both parities, all Einstein and extra primaries, and both momentum signs.
Every finite real tangent satisfying

```text
mu_H=mu_Px=mu_J1=mu_J2=mu_J3=0
```

admits a second-order Weyl--Maxwell correction that is smooth and periodic in
space and finite exponential-polynomial in time.  Relative standing-wave
phases are arbitrary.

## Channel proof

- At `(Omega,K)=(0,0)`, the complete physical adjoint pairings are the five
  stabilizer moment maps, which vanish on the declared cone.
- Every nonzero `L=0` Fourier block is exact modulo
  `Diff x Weyl x U(1)`, including the static `K=+/-2k` phase channel.
- Direct `L=1` exceptional replays expose only the shells `4` and `4/3`.
  Static nonzero momentum is off shell; resonant forcing has a secular inverse.
- For `L>=2`, the static extra factor is strictly negative and the Einstein
  factor strictly positive.  All nonzero resonances reduce through the
  certified fibrewise Smith factors to the scalar secular-inverse lemma.
- The angular product contains only `L=0,...,2ell`, so these cases exhaust the
  quadratic source.

This proves existence constructively, block by block.  It does not assert
that the correction remains bounded.  The exact resonance divisor is
nonempty for every `ell`, so bounded or finite-quasiperiodic extension still
requires a separate resonant source projection.

## Open boundary

The theorem does not combine distinct `|k|` fibres, add homogeneous/twist/
Wilson-line/charge or physical `ell=1` input modes, establish an all-orders
solution, perform the final residual quotient, or make a causal or quantum
claim.
