# Conformal `AA <-> EL` exchange rail

## Status

`symbolic/verify_conformal_quartic_exchange.py` is a fail-closed staging
certificate.  It reduces the exchange problem to three finite scalar-type
cylinder blocks and fixes all basis, Gram, gauge, Ward, and sign conventions.
The exact companion rail `verify_conformal_quartic_hessian.py` now supplies
all three covariant action Hessians, and
`verify_conformal_quartic_currents.py` supplies the directed raw-chiral cubic
current probes.  These data still do **not** define an exchange number: the
stationary-action/Born map is open, parity and reverse normalization must be
assembled explicitly, and the t channel is a Hessian-null generalized
conformal-Killing block with a provisional nonzero oscillator current.

Consequently the staging module continues to fail closed.  It produces no
effective Hamiltonian or obstruction until the compact-`S^3` BRST/Taub audit
determines the physical state space and every remaining archive rail closes.

## Exact channel reduction

For the chiral seed used by the contact calculation,

```text
A3+ : (3/2,1/2),  A3- : (1/2,3/2),
E2+ : (2,0),      L4- : (0,2),
```

the three pairings have unique common internal irreps:

| channel | minus-frequency pair | plus-frequency pair | frequency | internal irrep |
|---|---|---|---:|---|
| `s` | `A3+ A3-` | `E2+ L4-` | `(-6,+6)` | `(2,2)` |
| `t` | `E2+ A3+` | `L4- A3-` | `(-1,+1)` | `(1/2,1/2)` |
| `u` | `E2+ A3-` | `L4- A3+` | `(-1,+1)` | `(3/2,3/2)` |

All are scalar-type `SO(4)` representations `(j,j)`.  Thus the complete
metric exchange in each current channel lies in a small scalar harmonic
block; no TT-only propagator is relevant.

## Scalar metric basis and Gram signs

For a unit scalar harmonic `Y` with

\[
-\nabla^2Y=\lambda Y,
\qquad
\lambda=\ell(\ell+2),
\]

use

\[
h_{00}=x_0Y,
\quad
h_{0i}=x_1\nabla_iY,
\quad
h_{ij}=x_2\gamma_{ij}Y+x_3Q_{ij}[Y],
\]

where

\[
Q_{ij}=\nabla_i\nabla_jY+\frac{\lambda}{3}\gamma_{ij}Y.
\]

For `ell=1`, `Q` vanishes and `x3` is omitted.  In this unnormalized
component basis the spacetime field Gram matrix is

\[
G=\operatorname{diag}
\left(1,-2\lambda,3,\frac23\lambda(\lambda-3)\right).
\]

The negative `h0i` entry is important when converting a current covector to
component coefficients:

\[
j^{\rm component}=G^{-1}j_{\rm covector}.
\]

This is a field-component Gram sign, not the physical conformal Krein form.
The exact channel Grams are

```text
s: diag(1,-48,3,336)
t: diag(1,-6,3)
u: diag(1,-30,3,120).
```

## Diffeomorphism plus Weyl gauge

For parameters

\[
\xi_0=aY,
\qquad
\xi_i=b\nabla_iY,
\qquad
\sigma=cY,
\]

the script constructs the exact coefficient matrix of

\[
\delta h_{\mu\nu}
=\nabla_\mu\xi_\nu+\nabla_\nu\xi_\mu+2\sigma g_{\mu\nu}.
\]

The gauge slice is the scalar-harmonic projection of

\[
F_\mu=\nabla^\nu h_{\mu\nu}-\frac14\nabla_\mu h=0,
\qquad h=0.
\]

At `ell=omega=1`, one parameter combination `(a,b,c)=(i,1,1)` is a
conformal-Killing reducibility and one projected de-Donder row is dependent.
The code removes exactly one generator column and one constraint row.  The
reduced gauge orbit and slice then both have rank two, and their product is
nonsingular.  In the `s` and `u` blocks both have rank three.

The exchange rail also constructs an independent Gram-orthogonal slice,

\[
C_+'=B_-^TG,
\qquad
C_-'=B_+^TG.
\]

It is transverse in all three blocks.  Every archived exchange is solved in
both this slice and conformal de Donder plus trace gauge; disagreement is a
hard failure.

Consequently every channel has a one-dimensional gauge quotient.  This does
not by itself imply an invertible propagator: the quadratic form can still
vanish on that quotient.  The exact Ward covector bases printed by the script
are

```text
s minus: (-1/28,-3i/7,-1/28,1)
s plus : (-1/28, 3i/7,-1/28,1)

t minus: (1, 2i,1)
t plus : (1,-2i,1)

u minus: (1/4, i/2,1/4,1)
u plus : (1/4,-i/2,1/4,1).
```

## Exact covariant quadratic Hessians

`symbolic/verify_conformal_quartic_hessian.py` evaluates the complete
two-wave curved-cylinder reduced-Weyl action in normalized scalar harmonics.
It gives

\[
\boxed{
\kappa_s=131712,
\qquad
\kappa_t=0,
\qquad
\kappa_u=960.}
\]

The corresponding gauge-slice action coefficients are

\[
B_s=10752,
\qquad B_t=0,
\qquad B_u=96000,
\]

with the different numbers arising from the explicit slice/Ward-vector
contractions.  For `s` and `u`, both conformal-de-Donder/Weyl and
Gram-orthogonal bordered solves reproduce `1/kappa` exactly.

The `t` result is qualitatively different.  Its local radial density is

\[
\mathcal D_t(t)
=\frac{12t(1-t^2)}{\pi^2(1+t^2)^2},
\]

which is nonzero but integrates to zero after the stereographic measure is
included.  Thus the whole scalar quotient is Hessian-null and both bordered
matrices are singular.  This is not a zero or infinite propagator value: the
ordinary inverse does not exist.  The block may enter the exchange archive
only after the compact-cylinder global constraint problem is solved.  The
raw chiral cubic calculation now shows that both slice currents are nonzero,
while all four independently inserted pure-gauge generators integrate to
zero.  Thus simple local BRST-current decoupling fails at the oscillator
level.  No `1/kappa_t` may be formed.

The exceptional quotient has been identified exactly.  At `ell=omega=1`
the full gauge generator has the conformal-Killing reducibilities

\[
G_+(i,1,1)^T=0,\qquad G_-(-i,1,1)^T=0,
\]

and its transverse representatives are the frequency derivatives of those
reducibilities modulo ordinary gauge.  It is therefore a generalized
conformal-Killing/Taub zero mode.  Before calling the energy-six block
physical, one must determine whether global conformal-charge constraints
exclude it or require a charge-neutral/dressed/singlet completion.

These are covariant stationary-mode action coefficients.  Their use as
time-ordered Born denominators requires a separate normalization/prescription
theorem and is a mandatory archive rail.

## Conditional one-line exchange

Let `q-` and `q+` denote the corresponding Ward bases.  Completeness of the
gauge quotient forces exact currents and the covariant quadratic Hessian to
factor as

\[
j_-=a_-q_- ,
\qquad
j_+=a_+q_+ ,
\qquad
K=\kappa\,q_+q_-^T.
\]

When \(\kappa\ne0\), the gauge-bordered inverse and the one-dimensional
quotient agree:

\[
\boxed{
X_{\rm channel}
=j_-^T K_{\rm bordered}^{-1}j_+
=\frac{a_-a_+}{\kappa}.}
\]

For channels whose reduced Hessian is invertible, the parent P4 convention is

\[
V_{\rm eff}=C_{\rm contact}
-\sum_{\text{resolved non-null channels}}X_{\rm channel}.
\]

Synthetic exact fixtures verify the bordered solve and this sign in the
non-null `s` and `u` channels.  They are visibly synthetic and contain no
Weyl vertex data.  The `t` regression instead verifies that its zero Hessian
is rejected as an ordinary propagator.  A t contribution, if any, can be
defined only by the subsequent global reduction; it is not part of the
ordinary inverse-Hessian sum.

## Data still required

The current contact-only source in the `(AA,EL)` block is

\[
\frac{1099}{21600\pi^2}
\begin{pmatrix}0&1\\-1&0\end{pmatrix}.
\]

It is only an exchange-cancellation target.  To evaluate the exchange, an
independent generator must provide for each of `s,t,u`:

1. the complete minus- and plus-frequency cubic current covectors;
2. agreement with the exact covariant quadratic Hessians displayed above;
3. exact diffeomorphism and Weyl Ward identities;
4. the bordered solve, which the rail repeats in its independent
   Gram-orthogonal internal gauge;
5. for `t`, the full compact-`S^3` BRST/Taub/linearization-stability reduction;
   the provisional raw oscillator currents are nonzero and no Hessian inverse
   exists;
6. proof that lapse, shift, trace, scalar-derived tensor, constraints and
   auxiliary components are complete;
7. the parity partner and all normalization factors;
8. independently generated reverse currents satisfying the physical adjoint;
9. the stationary covariant-action to time-ordered Born/effective-Hamiltonian
   mapping.

The archive loader rejects floats, a wrong Gram convention, missing channels,
or any incomplete acceptance rail.  Once supplied, it prints the resolved
non-null one-line subtractions, records the separately certified global
reduction of the Hessian-null t block without forming an inverse, and checks
the independently assembled reverse sum before the parent P4 rail combines
it with the contact coefficient.
