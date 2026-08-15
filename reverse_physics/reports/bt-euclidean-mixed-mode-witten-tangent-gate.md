# BT mixed-mode Witten-tangent gate

**Certificate:**
`REVERSE_PHYSICS_BT_EUCLIDEAN_MIXED_MODE_WITTEN_TANGENT_GATE_V1`

**Dependency tags:** `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`,
`REDUCED-MODE`

## Result

The mixed harmonic that lowers the deterministic BT action-gradient quotient
does not directly produce a low-Rayleigh one-form in the Witten source
sector.

For its canonical tangent lift, the exact free lattice Witten quotient is

\[
 \boxed{
 \mathcal R_q={\omega_L^2\over\lambda^2}
              {1+5x\over1+x},
 \qquad
 x={q^2\lambda^2\over4N\omega_L^2}.}
\]

It is strictly larger than the unmixed source value whenever \(q\ne0\).
The field-space derivative and transverse bilaplacian terms therefore absorb
the deterministic flattening in this architecture.

The first interacting term has the same sign in the exact continuum
two-mode reduction. If \(b\) is the mixed-path parameter, then

\[
 \boxed{
 \lambda^2\mathcal R_b(\lambda)
 =1+4\big((b-1)^2+1\big)\lambda^2+O(\lambda^4).}
\]

At the deterministic optimum \(b=5/3\), the correction is \(52/9>0\).
Thus the newly found resonance is not, by itself, a full-Witten obstruction.
This remains a `REDUCED-MODE` result: other background-dependent one-forms,
the full interacting Gibbs expectation, and the actual \(H^{-1}\) moment are
still open.

## Exact free lattice theorem

On the periodic four-dimensional lattice let

\[
 h_x=\cos(\theta x_1)+\cos(\theta x_2),
 \qquad
 m_x=\cos(\theta x_1)\cos(\theta x_2),
 \qquad \theta={2\pi\over L}.
\]

For nonaliased modes,

\[
 \|h\|^2=N,
 \qquad \|m\|^2={N\over4},
 \qquad (-\Delta)h=\omega_Lh,
 \qquad (-\Delta)m=2\omega_Lm.
\]

Under the free bilaplacian Gibbs law

\[
 d\mu_0\propto
 \exp\left[-{\|\Delta\psi\|^2\over2\lambda^2}\right]d\psi,
\]

define the normalized source amplitude

\[
 a(\psi)={\langle h,\psi\rangle\over N},
 \qquad
 \mathbb E_0a^2={\lambda^2\over N\omega_L^2},
\]

and the mixed tangent one-form

\[
                         v_q(\psi)=h+q\,a(\psi)m.
\]

Its source overlap never changes:

\[
                         \langle v_q,h\rangle=N.
\]

The field-space derivative is the rank-one tensor

\[
 Dv_q={q\over N}m\otimes h,
 \qquad
 \|Dv_q\|_{\rm HS}^2={q^2\over4}.
\]

The free one-form Hessian gives one further \(q^2\) after averaging the
mixed amplitude. Consequently,

\[
 \mathbb E_0\|v_q\|^2
 =N+{q^2\lambda^2\over4\omega_L^2},
\]

and

\[
 \mathcal Q_1(v_q)
 ={N\omega_L^2\over\lambda^2}+{5q^2\over4}.
\]

Dividing these expressions proves the boxed theorem. The strict inequality
is not a pointwise-Hessian statement: it uses the complete Witten derivative
term and the free Gibbs variance of the amplitude.

For an exact rational check, use \(L=4\), \(N=256\),
\(\omega_4=2\), \(\lambda=2/5\), and the deterministic tangent
\(q=2(5/3)=10/3\). Then

\[
 x={1\over2304},
 \qquad
 {\mathcal R_q\over\omega_4^2/\lambda^2}
 ={2309\over2305}>1.
\]

The independent verifier reconstructs the norm, derivative cost, transverse
Hessian cost, and quotient from the mode data rather than importing the
producer fixture.

## Exact two-mode interacting reduction

On the continuum \(2\pi\)-torus take

\[
 \psi=a f+d m,
 \qquad
 f=\cos x+\cos y,
 \qquad
 m=\cos x\cos y.
\]

The predecessor's exact residual norm gives the reduced action

\[
 A(a,d)={a^2+d^2\over2}-a^2d+{5\over8}a^4
        +{5\over4}a^2d^2+{5\over32}d^4.
\]

The induced flat field metric is

\[
                    \|\delta\psi\|^2=(\delta a)^2+{(\delta d)^2\over4}.
\]

For the path \(d=ba^2\), the canonical tangent is

\[
 v_b=f+2ba\,m,
 \qquad
 \|v_b\|^2=1+b^2a^2,
 \qquad
 \|Dv_b\|_{\rm HS}^2=b^2.
\]

Now rescale \(a=\lambda x\), \(d=\lambda y\). The quadratic action makes
\(x,y\) independent standard Gaussians. The cubic and quartic weights are

\[
 A_3=-x^2y,
 \qquad
 A_4={5\over8}x^4+{5\over4}x^2y^2+{5\over32}y^4.
\]

Expanding \(e^{-\lambda A_3-\lambda^2A_4}\) with exact Gaussian moments,
including normalization, gives

\[
 \mathbb E[v_b^T(\nabla^2A)v_b]
 =1+4(b^2-2b+2)\lambda^2+O(\lambda^4).
\]

The order-\(\lambda^2\) derivative cost in the Witten numerator cancels
the corresponding one-form norm correction in the denominator. What remains
is exactly

\[
 4(b^2-2b+2)=4\big((b-1)^2+1\big)\geq4.
\]

The coefficient is minimized at \(b=1\), not at the deterministic-gradient
value \(5/3\). At \(5/3\) it is \(52/9\). An independent polynomial engine
differentiates the reduced action and evaluates every Gaussian moment over
the rationals at four values of \(b\).

## Meaning for the remaining barrier

The deterministic calculation and the Witten calculation answer different
questions. Allowing the mixed harmonic makes the action gradient slightly
flatter along a configuration path. A Witten trial one-form must also change
as the configuration changes, and that bending has a field-space derivative
cost. The mixed harmonic also lies at twice the graph-Laplacian eigenvalue.
Together, those terms more than repay the deterministic gain for the
canonical tangent.

This retires the simplest route from the mixed resonance to a Gibbs
counterexample. A genuine negative branch now needs an essentially different
one-form: for example, a background-dependent \(Q\)-sector corrector whose
connection cost is reduced by conditional averaging. The positive branch is
still the signed conditional mixed-Hessian or heat-bath response estimate.

## Boundary

This theorem covers one canonical family of source-overlapping one-forms and
an exact two-mode weak-coupling reduction. It is not a lower bound for the
full interacting Witten cyclic sector, does not rule out every low-Rayleigh
sequence, and proves neither boundedness nor divergence of the interacting
\(H^{-1}\) moment. It establishes no tightness, continuum identification,
continuum OS theorem, Born rule, Krein reconstruction, or
`LORENTZIAN-CAUSAL` claim.

## Verification

Run sequentially under the 500 MB cap:

```bash
ulimit -v 500000; python3 reverse_physics/bt_euclidean_mixed_mode_witten_tangent_gate.py --check
ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_mixed_mode_witten_tangent_gate.py
ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_mixed_mode_witten_tangent_gate
```
