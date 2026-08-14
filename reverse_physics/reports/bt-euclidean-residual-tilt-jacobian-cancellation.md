# BT residual-tilt Jacobian cancellation

Certificate:
REVERSE_PHYSICS_BT_EUCLIDEAN_RESIDUAL_TILT_JACOBIAN_CANCELLATION_V1

Dependency tags: LOCAL-ALGEBRAIC, EUCLIDEAN-SPECTRAL

Lifecycle: EXACT_REDUCTION_PROVED

## Result

The reciprocal spanning-tree coarea Jacobian in the residual-boundary form of
the BT measure cancels exactly under the natural boundary map induced by a
multiplicative field tilt. It therefore supplies no additional confinement of
the tilted lowest Fourier mode. The remaining normalized marginal is exactly
the original action-weighted orthogonal-fiber integral in the flat mean-zero
log-field chart.

This is a reduction of the live problem, not the missing moment estimate.

## General cancellation theorem

Let

\[
 H=\{\psi\in\mathbb R^N:\sum_x\psi_x=0\}
\]

and let \(R:H\to\partial\mathcal C_G\) be the residual diffeomorphism from
the predecessor certificate. Write its surface Jacobian as
\(\mathcal J_H(\psi)\). For \(h\in H\), translation by \(th\) induces

\[
 \tau_{t,h}(\psi)=\psi+th,\qquad
 T_{t,h}=R\circ\tau_{t,h}\circ R^{-1}.
\]

Translation on \(H\) has determinant one. The chain rule therefore gives

\[
 \operatorname{Jac}_{\partial\mathcal C_G}T_{t,h}(R(\psi))
 =\frac{\mathcal J_H(\psi+th)}{\mathcal J_H(\psi)}.
\]

The pushed BT surface density is

\[
 \rho(R(\psi))=Z^{-1}\frac{e^{-S(\psi)}}{\mathcal J_H(\psi)}.
\]

Consequently its pullback Radon--Nikodym ratio is

\[
 \boxed{
 \frac{\rho(T_{t,h}R(\psi))
       \operatorname{Jac}_{\partial\mathcal C_G}T_{t,h}(R(\psi))}
      {\rho(R(\psi))}
 =e^{-S(\psi+th)+S(\psi)}.}
\]

Both occurrences of \(\mathcal J_H\) cancel. Thus the previously certified
log-convexity and vacuum minimum of the tree Jacobian do not become a second
confining potential for this tilt.

## Exact marginal after cancellation

For a unit vector \(h\in H\), write

\[
                 \psi=\eta+s h,qquad \eta\in H\cap h^\perp.
\]

The normalized marginal is

\[
 m_h(s)=Z^{-1}\int_{H\cap h^\perp}e^{-S(\eta+s h)}\,d\eta.
\]

There is no coarea or tree factor in this expression. The next theorem must
control the ratio of these action-weighted fiber integrals uniformly in
lattice volume, or exhibit a controlled diverging sequence for the actual
marginal.

## Exact four-cycle fixture

On the four-cycle use

\[
 \Omega=(1,2,1,1/2),\qquad h=(1,-1,0,0),\qquad t=\log2.
\]

The tilted field is \(\Omega'=(2,1,1,1/2)\); both products equal one. Exact
rational calculation gives

\[
 \begin{array}{c|cc}
 &\Omega&\Omega'\\ \hline
 r&(1/2,-1,1/2,2)&(-5/4,1,-1/2,4)\\
 A=\|r\|_2^2/2&11/4&301/32\\
 \tau&5&9/2\\
 \mathcal J_H&85/2&153/4.
 \end{array}
\]

Hence

\[
 \frac{\mathcal J_H(\psi+th)}{\mathcal J_H(\psi)}=\frac9{10},
 \qquad
 \frac{\mathcal J_H(\psi)}{\mathcal J_H(\psi+th)}=\frac{10}9,
\]

and their product is exactly one. At \(\lambda=2/5\), the action gap and
Boltzmann exponent gap are

\[
 A'-A=\frac{213}{32},\qquad
 \frac{A'-A}{\lambda^2}=\frac{5325}{128}.
\]

The surface density ratio contains the factor \(10/9\), while the transformed
surface element contains \(9/10\). The weighted pullback ratio is therefore
only \(e^{-5325/128}\), exactly as in the flat chart.

## Foundations consequence

The dependency cut has three distinct layers:

1. The chart chain rule, four-cycle tree sums, and rational cancellation are
   finite exact algebra.
2. The surface change-of-variables interpretation is finite-dimensional
   analysis.
3. The all-volume conditional-fiber estimate is an unsupplied continuum
   input.

The result is classified as USED_BY_DISPLAYED_PROOF. It proves no weakest
base or reverse-mathematical equivalence.

## Next gate and boundaries

Work in the flat mean-zero log-field chart. For a normalized lowest axial
mode, derive a direct action-difference or conditional-fiber inequality for
\(S(\eta+s h)\). Do not count the tree Jacobian as additional confinement.
Only after a one-mode result should the calculation proceed to dyadic Fourier
shells.

This certificate does not establish a conditional-fiber ratio bound, a
normalized lowest-mode moment, the interacting \(H^{-1}\) estimate,
tightness, a continuum measure, a Born rule, a Krein reconstruction, or
anything LORENTZIAN-CAUSAL.

## Verification

Run sequentially:

    ulimit -v 500000; python3 reverse_physics/bt_euclidean_residual_tilt_jacobian_cancellation.py --check
    ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_residual_tilt_jacobian_cancellation.py
    ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_residual_tilt_jacobian_cancellation
