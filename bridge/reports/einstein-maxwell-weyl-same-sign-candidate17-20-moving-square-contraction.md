# Candidate-17/20 moving-square contraction

## Result

The normalized Cartan-square moment map is not confined to the phase-real
zero locus.  Its complete image is a closed three-ball.  In a phase gauge
`z=x+i y`, with `x dot y=0`, put `u=2|x||y|`.  After normalizing the
spin-two square,

```text
|mu_square| = F(u) = 3u/(2+u^2),
F'(u) = 3(2-u^2)/(2+u^2)^2 > 0.
```

The moment direction is the oriented line `x cross y`, and `SO(3)` acts
transitively on its unit sphere.  The radius formula and these direction
orbits prove that the complete normalized moment image is the closed
three-ball.

Thus every scalar contraction of an initial square moment through
`r in [0,1]` is realized by a continuous moving square direction.

For uniform scaling of the arbitrary `K` factor, let `s=t^2`,

```text
alpha = omega_plus*A_plus - omega_minus*A_minus,
delta = omega_plus*N_plus - omega_minus*N_minus,
c(s) = s*alpha + (1-s)*delta.
```

Initial rotation zero gives `M_K=-alpha*mu_0`.  Choosing

```text
mu_square(s) = r(s)*mu_0,
r(s) = s*alpha/c(s),
dr/ds = alpha*delta/c(s)^2,
```

cancels the rotational moment exactly.  If `alpha*delta>0`, then `c(s)`
never vanishes and `r(s)` runs continuously from zero to one.  Every point
in that sign-compatible stratum therefore contracts to the connected
double-singular hub.

If `alpha*delta<0`, the coefficient vanishes at the unique interior point

```text
s_0 = -delta/(alpha-delta),
```

while the scaled kernel moment remains nonzero when `mu_0` is nonzero.  No
motion of the square direction can repair that zero.  At `alpha=0`,
`delta!=0`, a nonvertex non-phase-real starting direction instead has an
endpoint-continuity obstruction.

## Candidatewise consequence

- Candidate 17 has `delta<0`.  Its complete `alpha<0` singular stratum
  contracts; the `alpha>0`, non-phase-real stratum hits the coefficient-zero
  obstruction.
- Candidate 20 remains complete on `delta=0`.  Off balance, the full
  `alpha*delta>0` stratum contracts.
- Phase-real directions and square vertices retain the earlier contraction.

## Boundary

This is a complete classification of the uniform `K`-factor scaling,
occupation-transfer, arbitrary-moving-square ansatz.  It is not a no-go for
independent node scaling, deformation of the `K` factor inside
`T3(f,g)=0`, or other nonradial paths.  Candidate-17 and candidate-20
off-balance complete connectedness, occupation gluing, final residual
descent, all-orders integration, causal transport, observables and quantum
states remain open.

CLOSE-OUT: SHORTFALL — the enlarged moving-square ansatz is completely disposed, but nonuniform K-factor deformations remain open.
EVIDENCE: bridge/certificates/einstein_maxwell_weyl_same_sign_candidate17_20_moving_square_contraction.json
