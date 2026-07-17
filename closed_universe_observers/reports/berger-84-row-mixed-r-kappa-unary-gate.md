# Berger 84-row mixed-axis unary gate

Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`, `LORENTZIAN-CAUSAL`.

## Result

The mixed-axis preflight contained one incorrect bidegree assignment.  The
memory kinetic action is

```text
sum_a integral dvol_g p_a T(g) m_a,
```

with no factor of `kappa`.  Therefore the `Phi2` variation of `T` is a
`Q10` coefficient at bidegree `(r,kappa)=(1,0)`, not part of `Q11`.  The
readout variation of `kappa p_a B_a(g) A` is the actual `(1,1)` block.

For `dTheta=(3/4)e^0`, `X=-9/16`, and `n0=(4/3)e0`, exact differentiation on
the canonical physical `Phi2` gives

```text
delta n^0 = 0,
delta n^i = -(4/3) Phi2_0i,
delta T = -(4/3) sum_i Phi2_0i e_i.
```

The zero-frequency transport correction vanishes.  The positive-frequency
sector has eleven nonzero spatial derivative coefficients, and the negative
sector is its exact conjugate.  Starting with the physical-volume adjoint and
conjugating to the frozen `dvol_gHat` pairing cancels the `n0(d1)` term:

```text
delta(T_raw*)   = -delta T-div_gHat(delta n)-n0(d1),
delta(T_sharp) = -delta T-div_gHat(delta n),
d1=1/2 tr_gHat(Phi2).
```

The formal same-sided inverse correction is also exact:

```text
H10=-H00 deltaT H00,
J10=-J00 deltaT_sharp J00.
```

Both left and right first-order inverse defects vanish.  This repairs the
previously omitted memory portion of the separate `r` axis.  It remains a
formal coefficientwise causal statement, not finite-`r` Green hyperbolicity.

## First mixed obstruction

For `P_a=dTheta wedge dR_aI(a)` write

```text
C_g(F,P)=1/2 F_mn P_ab g^{ma}g^{nb}.
```

The inverse-metric variation is fixed exactly, but the handoff defines `chi_a`
only by saying that a normalized transverse detector density is included in
it.  It supplies neither its normalization measure nor
`sigma_a=delta_r log chi_a`.  Consequently

```text
delta Btilde_a A
 = chi_a [delta C(F,P_a)+(d1+sigma_a) C_gHat(F,P_a)]
```

is not determined.  Choosing `sigma_a=0` or a nonzero support-local `s_a`
obeys every currently exported field while changing the mixed block by
`chi_a s_a C_gHat(F,P_a)` independently in both channels.  The certificate
therefore returns a normalized input obstruction.  It does not invent a
detector profile, and it does not promote mixed nilpotency, cyclicity, the
mixed Green coefficient, apparatus interactions, the observer morphism, or
any quantum claim.
