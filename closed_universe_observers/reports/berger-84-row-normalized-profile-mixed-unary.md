# Berger 84-row normalized-profile mixed unary gate

Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`, `LORENTZIAN-CAUSAL`.

## Result

The normalized detector-density obstruction is closed by a covariant rule
that uses exactly the clock and the three rods already assigned to each
detector.  On the clock slice `Sigma_tau={Theta=tau}`, define

```text
Pi_g = g^{-1} - (g^{-1}dTheta)(g^{-1}dTheta)/g^{-1}(dTheta,dTheta),
G_a^{IJ} = Pi_g(dR_aI,dR_aJ),
J_a = sqrt(det G_a),
chi_a = f_a(Theta) rho_a(R_a) J_a.
```

Here `rho_a` is a fixed normalized smooth bump in the oriented rod chart and
`f_a` is centered at the certified clock label.  The coarea identity gives

```text
J_a dSigma_g=d^3R_a,
integral_Sigma chi_a dSigma_g=f_a(Theta),
chi_a dvol_g=f_a rho_a dTheta d^3R_a/sqrt(U),
U=-g^{-1}(dTheta,dTheta).
```

Thus the metric dependence is no longer arbitrary:

```text
sigma_a=delta_r log chi_a=1/2 tr(G_a^{-1} delta_r G_a).
```

Both certified event rod Jacobians are the identity in order `(e3,e1,e2)`.
For `g_r=gHat+r Phi2`, exact first variation therefore gives

```text
sigma_a=-1/2(Phi2_11+Phi2_22+Phi2_33),
d1+sigma_a=-Phi2_00/2.
```

This agrees independently with the variation of the coarea factor
`U^(-1/2)`.

## Mixed unary and Green coefficient

The true mixed readout coefficient is

```text
delta Btilde_a A
 = chi_a[delta C(F,P_a)+(d1+sigma_a) C_gHat(F,P_a)],
Q11(p_a_plus,A)=-delta Btilde_a,
Q11(A_plus,p_a)=+(delta Btilde_a)^sharp.
```

These are exactly four nonzero operator blocks on carrier rows
`A=55..58`, `A_plus=59..62`, `p_a=72,73`, and `p_a_plus=82,83`; all other
`Q11` carrier blocks vanish.  The two Maxwell gauge paths vanish by `d^2=0`
and formal adjunction, and the two odd-cyclicity pairs cancel exactly.  Thus
the all-84-row mixed nilpotency and cyclicity defect counts are zero.  There
are no cross-channel profile terms.  Three independent exact two-channel
Hessian fixtures verify the
bivariate inverse coefficient

```text
E11 = E00 K10 E00 K01 E00
    + E00 K01 E00 K10 E00
    - E00 K11 E00.
```

Deleting its direct `K11` term produces nonzero left- and right-inverse
defects.

## Boundary

This is a coefficientwise first-jet result over the already certified
Schur--Laurent formal causal witness.  It does not establish a finite-
parameter Green operator or finite-
`r` Green hyperbolicity.  Apparatus `q2,q3`, `K_Berger` equivariance, the
observer morphism, deformed response rank, emitter recoil, and every quantum
claim remain open.
