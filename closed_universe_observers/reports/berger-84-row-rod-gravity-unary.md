# Berger 84-row rod--gravity unary first jet

The six global detector rods are not inert coefficients.  Their backgrounds
transform under diffeomorphisms, so the rod wave equations alone cannot be
adjoined to the BV complex.  This certificate supplies the missing blocks at
the covariant first-jet level.

## Clock dressing and gauge block

The clock contraction already removes temporal diffeomorphisms from the
dressed metric.  The compatible rod coordinate is

```text
rhat_aI = delta R_aI - Theta e0(Rbar_aI).
```

Its cotangent lift shifts `Theta_plus` by
`sum e0(Rbar_aI) rhat_aI_plus`, so the 84-row pairing is unchanged.  The
remaining gauge action is the honest spatial block

```text
Gamma_R(xi)_aI = sum_i xi^i e_i(Rbar_aI).
```

The generator exports every nonzero coefficient.  At each detector event its
three-by-three block, in base ghost order `(e1,e2,e3)`, is

```text
[0 0 1]
[1 0 0]
[0 1 0]
```

and therefore has determinant one.  The antifield block is the negative
formal transpose required by the frozen odd pairing.

## Hessian, principal-order correction, and formal causal witness

The mixed blocks are obtained from the standard-sign scalar action.  Their
covariant formulas are exported before transport through the clock dressing;
exact rational action specializations verify commuting mixed and metric
second variations.  The shifted base block is the pinned support-local
`q2_64(Phi2,-)` tensor.

The physical real `Phi2` is now assembled rather than left behind two
indirection layers.  Its machine-readable tensor uses the ten metric
components, ten declared spatial harmonics, and temporal frequencies
`0,+sqrt(58)/3,-sqrt(58)/3`; the negative block is the exact conjugate of the
positive block.  Sparse coefficient vectors and three spatial derivative
matrices make the field directly usable by the mixed calculation.

The original causal rationale incorrectly classified `q2(Phi2,-)` as order
two.  The pinned pure-Weyl payload has 53,468 metric--metric terms and 7,488
terms with four derivatives on one argument.  The corrected certificate
contracts the physical zero-frequency `Phi2` exactly and obtains the nonzero
coefficient `623/81` multiplying `e3^4 h_hat_00` in the
`h_hat_00`-antifield equation.  Thus this block is constructively a
fourth-order diagonal principal deformation, rather than merely being
classified that way fail-closed.
The rod off-diagonal blocks remain strictly subprincipal, but the gravity
principal symbol is not claimed to remain unchanged.

The Laurent inverse is checked explicitly, not inferred from the diagonal
alone.  In gravity--rod block form the specialized operator is

```text
P(r) = [ A0+r A1   r B ]
       [ r C       r D ].
```

Writing `E=A1-B D^-1 C` and
`S^-1=A0^-1-r A0^-1 E A0^-1`, its inverse through order `r` is

```text
G11 =  S^-1
G12 = -S^-1 B D^-1
G21 = -D^-1 C S^-1
G22 =  r^-1 D^-1 + D^-1 C S^-1 B D^-1.
```

Both multiplication orders have zero coefficients at Laurent powers
`r^-1`, `r^0`, and `r^1` in exact noncommuting rational-matrix fixtures.
Deleting the Schur feedback `B D^-1 C` produces a nonzero first-order defect.
Here `A1` includes the fourth-order principal deformation.  The formula is a
formal coefficientwise inverse: each coefficient composes same-sided pinned
Green operators with local differential insertions, so causal support is
preserved term by term.  It does not establish existence, uniqueness, or
Green hyperbolicity for a finite nonzero `r` operator.

The canonical rod pairing makes the Green operator Laurent-singular as
`r -> 0`; this is recorded rather than hidden.  This certificate computes the
rod--gravity part of the `r` axis, but it originally assigned the backreacted
memory transport to the mixed coefficient.  That assignment is corrected
here: because `p*T(g_r)*m` has no `kappa`, `delta_r T` belongs to `Q10`.
It is not computed in this artifact, so the full 84-row `r` axis is not claimed
here.  The later mixed-axis gate computes that missing transport coefficient.

## Mixed-order preflight

The next coefficient is frozen as

```text
Q=Q00+r Q10+kappa Q01+r*kappa Q11+O(r^2,kappa^2),
[Q00,Q11]+[Q10,Q01]=0.
```

Unary identities use the four displayed bidegrees.  Causal identities use a
coefficient window in `K((r))[[kappa]]`, retaining Laurent powers
`r^-1,r^0,r^1` and memory powers through `kappa^2`; this is not represented by
the inconsistent quotient `r^2=0` after adjoining `r^-1`.

The `Q10` shifted transport adjoint must be recomputed:

```text
T_r* = -T_r - div_g_r(n_Theta(g_r)).
```

The stationary identity `T0*=-T0` cannot be reused.  The physical density
ratio and every `B_a`/`T` cotangent block must first be expanded and then
transported to the frozen 84-row pairing.  The transport variation belongs to
`Q10`; only the shifted background `B_a^(0)` and its adjoint belong to `Q11`.
`B_a^(1)` and `B_a^(2)` remain the later apparatus `q2` and `q3` calculation.
The mixed profile coefficient itself,
`K_Berger` equivariance, observer morphism, deformed rank two, and every
quantum claim remain open.
