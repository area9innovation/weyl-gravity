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

## Hessian and causal witness

The mixed blocks are obtained from the standard-sign scalar action.  Their
covariant formulas are exported before transport through the clock dressing;
exact rational action specializations verify commuting mixed and metric
second variations.  The shifted base block is the pinned support-local
`q2_64(Phi2,-)` tensor.

The extended witness has diagonal principal pieces: the certified gravity
biwave, Maxwell wave, six scalar rod waves, and the certified memory
transport.  All new cross terms are lower order.  Thus the coupled wave
operator has same-sided advanced and retarded Green operators for fixed
nonzero `r=epsilon_R^2`, and `Lambda=W G_P` gives the chain contraction on the
certified axial first jet.

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
Because each term composes same-sided base and rod Green operators with local
cross blocks, advanced/retarded support is preserved at this axial first jet.

The canonical rod pairing makes the Green operator Laurent-singular as
`r -> 0`; this is recorded rather than hidden.  The mixed
`epsilon_R^2*kappa` corrections to `B_a`, `T`, and their adjoints are not yet
present, so the unqualified full-84 flags remain false.

Accordingly, the result certifies the full 84-row differential, unary
cyclicity, and causal chain contraction only on the three separate axial
bidegrees `(0,0)`, `(epsilon_R^2,0)`, and `(0,kappa)`.  It is not an
all-orders 84-row theorem and does not cover the mixed axis, apparatus
`q2/q3`, `K_Berger` equivariance, the observer morphism, or a quantum theory.
