# BT mixed-mode sharp-gradient obstruction

**Certificate:**
`REVERSE_PHYSICS_BT_EUCLIDEAN_MIXED_MODE_SHARP_GRADIENT_OBSTRUCTION_V1`

**Dependency tags:** `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`,
`REDUCED-MODE`

## Result

The sharp free coefficient retained by every coordinate-separable BT field
does not extend to arbitrary mixed-coordinate fields.

On the continuum torus, a lowest-mode pair and its forced mixed harmonic give
an exact field with

\[
                         \|E\|_2^2<\|R\|_2^2.
\]

More importantly for the regulator, on every periodic four-dimensional
\(L^4\) lattice with \(L\geq8\), there are positive fields satisfying

\[
             \|\nabla A\|_2^2<\omega_L^2\|r\|_2^2,
 \qquad \omega_L=4\sin^2(\pi/L).
\]

Thus the coefficient-one extension of the separable theorem is obstructed on
an unbounded family of actual lattice volumes. This does **not** show that the
best coefficient tends to zero. A smaller positive volume-uniform coefficient,
the full Witten estimate, and the interacting \(H^{-1}\) moment all remain
open.

## Continuum resonance

On the \(2\pi\)-periodic torus take

\[
 \psi=a(\cos x+\cos y)+d\cos x\cos y,
 \qquad
 R=\Delta\psi+|\nabla\psi|^2,
 \qquad
 E=\Delta R-2\operatorname{div}(R\nabla\psi).
\]

Exact Fourier algebra gives

\[
 \|R\|_2^2={1\over16}\left(
 20a^4+40a^2d^2-32a^2d+16a^2+5d^4+16d^2\right)
\]

and

\[
\begin{split}
 \|E\|_2^2={1\over4}\big(&36a^6+238a^4d^2-112a^4d+36a^4
 +144a^2d^4-116a^2d^3\\
 &+124a^2d^2-48a^2d+4a^2+9d^6+36d^4+16d^2\big).
\end{split}
\]

Set \(d=ba^2\). The first nonzero difference from the sharp separable
coefficient is

\[
 \|E\|_2^2-\|R\|_2^2
 =a^4\left(3b^2-10b+{31\over4}\right)+O(a^6).
\]

Completing the square exposes the resonance:

\[
 3b^2-10b+{31\over4}
 =3\left(b-{5\over3}\right)^2-{7\over12}.
\]

The mixed mode \(b=5/3\) therefore lowers the quotient at second order.
This is the complete quadratic harmonic correction: a general second-order
profile \(g\) has coefficient

\[
 {31\over4}-40\langle g,\cos x\cos y\rangle
 +\left\langle g,(-\Delta)^2\big((-\Delta)^2-1\big)g\right\rangle.
\]

All unforced modes add nonnegative terms. The unique forced high-mode
minimizer, modulo constants and lowest-mode reparametrizations, is
\(g=(5/3)\cos x\cos y\).

An exact finite-amplitude fixture is

\[
 a={1\over12},\qquad d={1\over90}.
\]

For it,

\[
 \|R\|_2^2={5858509\over839808000},\qquad
 \|E\|_2^2={26307248191\over3779136000000},
\]

and hence

\[
 \|E\|_2^2-\|R\|_2^2
 =-{56042309\over3779136000000}<0.
\]

## Every lattice volume from eight onward

Let \(\theta=2\pi/L\), \(c_L=\cos\theta\), and use the lattice family

\[
 \psi_x=a(\cos\theta x_1+\cos\theta x_2)
       +ba^2\cos\theta x_1\cos\theta x_2.
\]

Expanding the exact exponential residual and its exact log-field action
gradient gives

\[
 \|\nabla A\|_2^2-\omega_L^2\|r\|_2^2
 =a^4\omega_L^4 C_L(b)+O(a^5),
\]

where

\[
 C_L(b)=3b^2-10b+c_L^4-{5\over4}c_L^2
        -{3\over2}c_L+{19\over2}.
\]

Again \(b=5/3\) is optimal, and

\[
 C_L(5/3)={p(c_L)\over12},
 \qquad
 p(c)=12c^4-15c^2-18c+14.
\]

For \(L\geq8\), one has \(c_L\in[\sqrt2/2,1)\). On this interval,

\[
 p'(c)=6(c-1)(8c^2+8c+3)<0,
\]

while

\[
 p(\sqrt2/2)={19\over2}-9\sqrt2<0.
\]

Thus \(C_L(5/3)<0\) for every \(L\geq8\). Analyticity then supplies a
nonzero sufficiently small \(a\) at each such volume for which the strict
coefficient-one inequality fails.

The independent verifier derives the formal coefficient directly from the
nearest-neighbour exponential series in a Laurent cyclic-shift variable. It
does not import the producer's formula.

## Exact rational \(8^4\) fixture

The certificate also stores an integer-valued positive \(8\times8\) table
\(\Omega_{x_1x_2}\), extended constantly in \(x_3,x_4\). Since only ratios
of \(\Omega\) enter, multiplying the table by its inverse geometric mean
puts it on the mean-zero log-field carrier without changing any quantity
below. Its residual and full four-dimensional log-field action gradient are
rational. Exact enumeration proves

\[
 {\|\nabla A\|_2^2\over\|r\|_2^2}
 <{35\over102}.
\]

The Pell approximant

\[
 {577\over408}>\sqrt2,
 \qquad 577^2-2\,408^2=1,
\]

gives

\[
 {35\over102}<6-4\sqrt2=(2-\sqrt2)^2=\omega_8^2.
\]

This independently verifies a strict finite-amplitude lattice obstruction
using only rational arithmetic and a one-unit Pell identity.

## Meaning for the reconstruction programme

The preceding separable theorem was not misleading: independent coordinate
profiles really do retain the free coefficient. The new calculation locates
the first mechanism that they exclude. Two lowest modes generate a mixed
harmonic, and that harmonic cancels a small part of the Euler gradient.

In ordinary language, the landscape is slightly flatter in a diagonal
two-coordinate direction than it is along any product of one-coordinate
directions. It is not flat: the certified quotient is close to one, and no
sequence tending to zero has been found.

The deterministic fork is now narrower. A proof of full coercivity must allow
a renormalized constant below one; attempting to extend the sharp separable
constant is impossible. The more relevant next calculation is to insert this
forced harmonic into the connection-corrected Witten cyclic sector. If the
connection term absorbs it, the resonance is only deterministic. If it
creates a normalized low-Rayleigh direction with lowest-mode overlap, it can
become a genuine obstruction to the Gibbs moment route.

## Boundary

This result does not establish collapse of the full gradient quotient, failure
of every positive volume-uniform deterministic coefficient, a Poincare or
Witten theorem, boundedness or divergence of the actual interacting
\(H^{-1}\) moment, tightness, continuum identification, or a continuum OS
theorem. It supplies no Born rule, Krein reconstruction, or
`LORENTZIAN-CAUSAL` claim.

## Verification

Run sequentially under the 500 MB cap:

```bash
ulimit -v 500000; python3 reverse_physics/bt_euclidean_mixed_mode_sharp_gradient_obstruction.py --check
ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_mixed_mode_sharp_gradient_obstruction.py
ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_mixed_mode_sharp_gradient_obstruction
```
