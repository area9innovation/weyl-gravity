# BT heat-bath influence symbol gate

Certificate:
REVERSE_PHYSICS_BT_EUCLIDEAN_HEAT_BATH_INFLUENCE_SYMBOL_GATE_V1

Dependency tags:
LOCAL-ALGEBRAIC, EUCLIDEAN-SPECTRAL, REDUCED-MODE

## Result

The new quotient-site Poincare bound cannot be globalized by a standard
absolute Dobrushin influence argument.  That route already fails in the free
Gaussian BT theory:

\[
 \sum_{y\ne o}\left|\frac{K_{oy}}{K_{oo}}\right|
 =\frac{184}{72}=\frac{23}{9}>1,
 \qquad K=(-\Delta)^2.
\]

This is not failure of heat-bath or local-to-global methods.  The signed
continuous-time heat-bath Markov drift has Fourier symbol

\[
                        -\frac{\omega(p)^2}{72},
\]

so its positive relaxation rate is \(\omega(p)^2/72\).  The lowest rate is of
order \(L^{-4}\), exactly the bilaplacian slow scale
expected from the free continuum covariance.  Entrywise absolute values erase
that cancellation.

For the interacting measure, differentiation of the quotient-site
conditional mean gives an exact covariance identity.  The local
\(C_P\leq1/2\) theorem bounds it by a conditional mixed-Hessian square.  That
signed finite-range composite, rather than an absolute influence matrix, is
the next calculation.

## Mean-zero quotient-site geometry

On

\[
 H=\{\psi:\sum_x\psi_x=0\},
 \qquad h_o=\delta_o-N^{-1}\mathbf1,
\]

use the orthogonal split
\(H=\operatorname{span}(h_o)\oplus h_o^\perp\).  Shift invariance gives

\[
 A(\eta+s h_o)=A(\eta+s\delta_o).
\]

Thus the quotient-site conditional law is exactly the one-site exponential
fiber already certified, while remaining inside the normalized mean-zero
carrier.

## Exact free response

Let

\[
 L_G=8I-\operatorname{Adj},\qquad K=L_G^2.
\]

The free action is \(\frac12\langle\psi,K\psi\rangle\).  Since
\(K\mathbf1=0\),

\[
 \langle h_o,Kh_o\rangle=K_{oo}=8^2+8=72.
\]

For \(\eta\in h_o^\perp\), the conditional mean coordinate is

\[
 m_o(\eta)=-\frac{\langle h_o,K\eta\rangle}{72}.
\]

Summing continuous-time quotient-site updates over all sites gives Markov
drift (-K/72).  Equivalently, the positive mean-relaxation operator is

\[
 \mathcal R_{\rm HB}=\frac K{72}
\]

on \(H\).  The corresponding simultaneous conditional-mean response is

\[
 T_{\rm HB}=I-\frac K{72},
 \qquad
 \widehat T_{\rm HB}(p)=1-\frac{\omega(p)^2}{72},
\]

where

\[
 \omega(p)=8-2\sum_{\mu=1}^4\cos p_\mu.
\]

For the lowest axial momentum,

\[
 \omega_L=4\sin^2(\pi/L),
 \qquad
 \gamma_L=\frac{\omega_L^2}{72}
 =\frac29\sin^4(\pi/L)
 \sim\frac{2\pi^4}{9L^4}.
\]

This is the correct signed slow scale.  It is not yet an interacting spectral
gap.

## Why absolute influence fails

The origin row of \(K\) has:

- diagonal \(72\);
- eight nearest-neighbor entries \(-16\), total absolute weight \(128\);
- axial distance-two path weight with total \(8\);
- twenty-four mixed distance-two entries \(2\), total absolute weight \(48\).

Hence the off-diagonal absolute sum is \(184\).  The failure is visible
without an inequality: at checkerboard momentum,

\[
 \omega(\pi,\pi,\pi,\pi)=16,
 \qquad
 \widehat T_{\rm HB}=-\frac{23}{9}.
\]

The exact \(4^4\) fixture independently enumerates the 256-site torus.  Its
lowest real cosine has bilaplacian eigenvalue \(4\), giving heat-bath rate
\(1/18\), while the checkerboard has eigenvalue \(256\) and response
\(-23/9\).

The simultaneous response is not itself the continuous-time Markov
semigroup.  Its high-frequency magnitude greater than one therefore does not
mean the continuous-time heat-bath dynamics is unstable.  It means that
entrywise absolute contraction and simultaneous Jacobi iteration are the
wrong proof architectures.

## Exact interacting response gate

For \(\eta\in h_o^\perp\), write

\[
 q_\eta(s)=Z_\eta^{-1}e^{-S(\eta+s h_o)}\,ds,
 \qquad
 m_o(\eta)=\mathbb E_{q_\eta}s.
\]

For \(k\in h_o^\perp\), differentiating the normalized conditional integral
gives

\[
 D_km_o(\eta)
 =-\operatorname{Cov}_{q_\eta}(s,D_kS).
\]

Apply the certified one-dimensional Poincare inequality first to \(s\) and
then to \(D_kS\):

\[
 \operatorname{Var}_{q_\eta}(s)\leq\frac12,
 \qquad
 \operatorname{Var}_{q_\eta}(D_kS)
 \leq\frac12\,
 \mathbb E_{q_\eta}\!\left[
   \bigl(\operatorname{Hess}S[h_o,k]\bigr)^2
 \right].
\]

Therefore

\[
 \boxed{
 |D_km_o(\eta)|
 \leq\frac12
 \left(
 \mathbb E_{q_\eta}
 [(\operatorname{Hess}S[h_o,k])^2]
 \right)^{1/2}.}
\]

This reduction is exact, but the mixed-Hessian expectation has not been
bounded with the signed Fourier structure needed at low momentum.

## Meaning and next calculation

In ordinary language, each local conditional distribution is well controlled,
but the sites pull on one another with positive and negative signs.  If those
signs are discarded, the apparent influence is more than twice too large.
Keeping the signs recovers the bilaplacian \(L^{-4}\) scale in the free theory.

The next calculation is to expand
\(\operatorname{Hess}S[h_o,k]\) as its exact finite-range residual/edge
composite, condition it along the \(h_o\) fiber, and Fourier transform the
signed response.  The vacuum term must reproduce \(\omega(p)^2/72\).  The
decision is whether the nonlinear remainder is relatively controlled at that
scale or produces a low-frequency countersequence.

## Boundary

This certificate does not obstruct every influence or heat-bath method.  It
does not establish an interacting signed influence bound, global Poincare
inequality, Witten coercivity, normalized lowest-mode estimate, interacting
\(H^{-1}\) moment, tightness, or a continuum measure.  It does not change the
finite-volume ordinary-OS obstruction and has no Born, Krein, or
LORENTZIAN-CAUSAL consequence.

Paper 21 is not changed at this method checkpoint because the global
interacting-moment and reconstruction lifecycle states remain open.

## Reproducibility

Run under the 500 MB Python cap:

    ulimit -v 500000; python3 reverse_physics/bt_euclidean_heat_bath_influence_symbol_gate.py --check
    ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_heat_bath_influence_symbol_gate.py
    ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_heat_bath_influence_symbol_gate

The verifier applies the graph Laplacian twice to independent delta, cosine,
and checkerboard fields rather than importing the producer's path-count row.
Tier 0 also compiles Python, validates JSON/schema, checks both predecessor
hashes, runs the scoped diff check, and inspects staged paths.  Tier 2 uses the
unchanged content-addressed inputs by hash.  Tier 3 is not triggered because
this is a method gate, not a global theorem promotion, freeze, shared-core
change, or release.
