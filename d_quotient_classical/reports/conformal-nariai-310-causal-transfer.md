# Conformal Nariai 310-row causal transfer

Let `g_phi=exp(2 phi)g_N` with

```text
sup |exp(phi)-1| < 1/9.
```

This is an open bounded-smooth conformal class.  It stays inside the explicit
radius-`1/4` Bach-flat ADM neighborhood: the largest spatial deviation is
`19/81<1/4`.  Every member is Bach-flat and non-conformally-flat, and has
exactly the Nariai causal relation.

The finite Diff--Weyl BV transformation includes the essential affine term
`omega_phi=omega-xi(phi)` and its forced cotangent shear.  Transporting the
gauge fermion, generalized auxiliaries, normal-tractor rows and cyclic duals
gives

```text
Q_phi=U_phi Q_N U_phi^-1,
I_phi=U_310 I_N U_met^-1,
P_phi=U_met P_N U_310^-1,
H_phi=U_310 H_N U_310^-1.
```

Consequently all SDR identities and side conditions hold.  The causal
homotopies are

```text
Lambda_310,phi,+/-=U_310 Lambda_310,N,+/- U_310^-1
                   =H_phi+I_phi Lambda_met,phi,+/- P_phi,
```

with exact metric descent, same-sided support and cyclic adjoint reversal.
The nonconstant consumer `Omega=1+1/(10(1+t^2))` lies strictly inside the
class.

This closes the metric/all-row theorem along the conformal Nariai orbit.  It
does not cover Bach-flat deformations transverse to that orbit.
