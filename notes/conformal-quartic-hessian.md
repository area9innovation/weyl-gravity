# P4 Hessian certificate: scalar exchange quotients

`symbolic/verify_conformal_quartic_hessian.py` computes the exact two-wave
coefficient of

\[
\sqrt{-g}\left(R_{\mu\nu}R^{\mu\nu}-\frac13R^2\right)
\]

on `R x S^3` in the scalar-type `s`, `t`, and `u` exchange blocks isolated by
the energy-six `AA <-> EL` staging rail.  This is an exact stationary-mode
**covariant action Hessian**.  It is not silently identified with a
time-ordered Born denominator or cylinder effective Hamiltonian.

## Quotient convention

In each channel the conformal-de-Donder/trace slice is one dimensional.  If
`p_+` and `p_-` span the ket and bra slices while `q_+` and `q_-` span the
Ward-current covectors, the reconstructed covariant Hessian is

\[
K=\kappa\,q_+q_-^T.
\]

For nonzero `kappa`, two independently constructed bordered gauges reproduce
`1/kappa` exactly for unit Ward currents.  The component basis is

\[
h_{00}=x_0Y,\qquad h_{0i}=x_1\nabla_iY,\qquad
h_{ij}=x_2\gamma_{ij}Y+x_3Q_{ij}[Y],
\]

with `x_3` absent at `ell=1`.

## Exact results

### s channel

\[
p_-=(-12,3i,-4,1)^T,\qquad
p_+=(-12,-3i,-4,1)^T,
\]

\[
\mathcal D_s(t)=
\frac{54720t^5-2400t}{\pi^2(1+t^2)^5},\qquad
p_-^TK_sp_+=10752,
\]

\[
\boxed{\kappa_s=131712}.
\]

In the declared component basis,

\[
K_s=
\begin{pmatrix}
168&2016i&168&-4704\\
-2016i&24192&-2016i&56448i\\
168&2016i&168&-4704\\
-4704&-56448i&-4704&131712
\end{pmatrix}.
\]

The exact run used 161.12 seconds in the recorded environment.

### t channel

\[
p_-=(3,-i,1)^T,\qquad p_+=(3,i,1)^T,
\]

\[
\mathcal D_t(t)=
\frac{12t(1-t^2)}{\pi^2(1+t^2)^2},\qquad
p_-^TK_tp_+=0,
\]

\[
\boxed{\kappa_t=0},\qquad K_t=0.
\]

The local density is not zero; it integrates to a boundary zero.  Both
bordered matrices are singular.  Consequently the t block is **not** an
ordinary propagating quotient and no expression containing `1/kappa_t` is
admissible.  The subsequently computed raw chiral cubic currents do **not**
vanish on its transverse slice, although every direct pure-gauge probe does.
The block therefore cannot enter an ordinary exchange archive.  Its quotient
is the frequency derivative of a conformal-Killing reducibility, so a global
BRST/Taub/linearization-stability audit must decide whether the proposed
external oscillator block is excluded, dressed, or completed before any
physical exchange is defined.  The regression-enabled Hessian run used 59.74
seconds and 75,160 KB.

### u channel

\[
p_-=(30,-2i,10,1)^T,\qquad
p_+=(30,2i,10,1)^T,
\]

\[
\mathcal D_u(t)=
\frac{10944t^5-24480t^3+52512t}{\pi^2(1+t^2)^4},\qquad
p_-^TK_up_+=96000,
\]

\[
\boxed{\kappa_u=960}.
\]

\[
K_u=
\begin{pmatrix}
60&120i&60&240\\
-120i&240&-120i&-480i\\
60&120i&60&240\\
240&480i&240&960
\end{pmatrix}.
\]

The exact run used 174.82 seconds in the recorded environment.

## Acceptance boundary

The script regression-fixes every density, slice coefficient, and `kappa`,
checks scalar-harmonic and tensor-component norms, reconstructs the complete
covariant Hessian, and verifies its diffeomorphism/Weyl kernels.  For `s` and
`u`, conformal-de-Donder and Gram-orthogonal bordered solves agree exactly.

The following are deliberately not inferred:

1. the cubic currents;
2. t-channel global-constraint reduction (the raw oscillator current is
   known to be nonzero);
3. the stationary-action to time-ordered Born normalization;
4. reducible external-state subtractions;
5. a complete energy-six effective Hamiltonian or metric obstruction.

`--require-born-map` therefore fails closed.
