# Phase-3 axial QNM high-overtone cocycle audit

**Date:** 24 July 2026

**Repository HEAD inspected:** `3a875d09a0326f82958009efda8776414cd47485`

**Dependency tags:** `LOCAL-ALGEBRAIC`, `REDUCED-MODE`
**Status:** `READ_ONLY_ANALYTICAL_SHORTFALL`

## Scope and inputs

This read-only audit asks whether the exact reduced projective cocycle already
supports a controlled high-damping theorem for the repeated axial spin-two
QNM selector

\[
\beta_n
=
B_n+\int_{\Gamma_n}{\cal I}_{\rm red}(r,\omega_n)y_n(r)^2\,dr_*.
\]

The authoritative inputs were:

- `black_hole_programme/phase3/axial_qnm_projective_cocycle_v1/certificate.json`,
  SHA-256
  `3f7c2fff23a70ab8c1f6e922d6799b168ca328f0fa9e68be8a0e8881f80310bb`;
- `black_hole_programme/phase3/axial_qnm_local_smith_dichotomy/certificate.json`,
  SHA-256
  `bbc34d5865a95c9fa8b74157d0ef6abcac8271cca067983e7b23e5850f16da41`.

The exact local inputs are

\[
{\cal I}_{\rm red}
=
\frac{i(r-2)(2r\omega^2+3\omega^2+12)}
{5r^4\omega},
\qquad
D=\frac{r-2}{r}\partial_r,
\]

and

\[
L=D^2+U,
\qquad
U=\omega^2-\frac{6(r-2)(r-1)}{r^4}.
\]

No QNM, Stokes multiplier, Fredholm pairing or off-real-axis numerical solve
was imported or computed.

## Exact \(r=0\) projective term

The reduced cocycle has the exact Laurent expansion

\[
\boxed{
{\cal I}_{\rm red}
=
-\frac{6i}{5}\left(\omega+\frac4\omega\right)r^{-4}
+\frac{i}{5}\left(-\omega+\frac{12}{\omega}\right)r^{-3}
+\frac{2i\omega}{5}r^{-2}.}
\]

The coefficient of \(r^{-4}\) is the resonant local projective residue.  The
certified leading action of the symmetric-square operator is

\[
{\cal K}_U(r^m)
\sim
-8(m-6)(m-2)(m+2)r^{m-6}.
\]

Producing \(r^{-4}\) requires \(m=2\), where the leading factor vanishes.
Consequently this coefficient is not removable by the local rational leading
map.  It is nonzero at large \(\lvert\omega\rvert\); its only finite zeros are
\(\omega=\pm2i\).  This local residue does not by itself decide any QNM
period.

## High-damping balance and Bessel model

Choose a branch of \(\sqrt{\omega}\) and set

\[
r=\frac{\rho}{\sqrt{\omega}}.
\]

This is the natural balance because

\[
U=\omega^2-\frac{12}{r^4}+\frac{18}{r^3}-\frac6{r^2}.
\]

After division by \(\omega^2\), the scalar equation is exactly

\[
\begin{aligned}
0={}&
\left(
4\rho^{-2}\partial_\rho^2
-4\rho^{-3}\partial_\rho
+1-12\rho^{-4}
\right)y\\
&+\omega^{-1/2}
\left(
-4\rho^{-1}\partial_\rho^2
+2\rho^{-2}\partial_\rho
+18\rho^{-3}
\right)y\\
&+\omega^{-1}
\left(
\partial_\rho^2-6\rho^{-2}
\right)y.
\end{aligned}
\]

Near \(r=0\),

\[
r_*-r_{*,0}=-\frac{r^2}{4}+O(r^3).
\]

With

\[
z=-\frac{\rho^2}{4}
\simeq
\omega(r_*-r_{*,0}),
\]

the leading equation becomes

\[
\boxed{
\frac{d^2y}{dz^2}
+\left(1-\frac{3}{4z^2}\right)y=0.}
\]

It is the order-one Bessel model.  Its two leading turning points are

\[
z=\pm\frac{\sqrt3}{2}.
\]

This identifies the correct \(r\sim\lvert\omega\rvert^{-1/2}\) turning
region, but does not supply the physical QNM Stokes combination.

## Exact scaled cocycle density

The tortoise Jacobian cancels the factor \(r-2\):

\[
\boxed{
{\cal I}_{\rm red}\,dr_*
=
\frac{i(2r\omega^2+3\omega^2+12)}
{5r^3\omega}\,dr.}
\]

On the inner scale,

\[
\boxed{
{\cal I}_{\rm red}\,dr_*
=
\frac{3i}{5}\omega^2\rho^{-3}\,d\rho
+\frac{2i}{5}\omega^{3/2}\rho^{-2}\,d\rho
+\frac{12i}{5}\rho^{-3}\,d\rho.}
\]

Equivalently, the leading Bessel-coordinate density is

\[
\boxed{
{\cal I}_{\rm red}\,dr_*
\sim
-\frac{3i}{40}\omega^2z^{-2}\,dz.}
\]

If a QNM solution admitted a uniformly controlled local normalization

\[
y_n=A_n\left(Y_0+O(\omega_n^{-1/2})\right),
\]

this density would suggest a conditional form

\[
\beta_n
=
A_n^2\omega_n^2
\left(C_0+O(\omega_n^{-1/2})\right).
\]

Neither the existence nor the nonvanishing of \(C_0\) follows from the
present artifacts.

## Concomitant cancellation obstruction

The reduced representative differs from the original cocycle by a rational
projective gauge.  Its reducing function behaves at \(r=0\) as

\[
q_{\rm red}
=
-\frac{3i}{20\omega r^2}
-\frac{i}{5\omega r}
+O(\omega^{-1}).
\]

Thus \(q_{\rm red}=O(1)\) on the turning scale
\(r=\rho/\sqrt{\omega}\), and its boundary concomitant has the same
\(O(\omega^2)\) size as the leading reduced-cocycle integral.

For \(Z=y^2\), the exact Lagrange identity is

\[
\int_\Gamma Z\,{\cal K}_Uq\,dr_*
=
\left[
Z D^2q-(DZ)(Dq)+(D^2Z)q+4UZq
\right]_{\partial\Gamma}
-\int_\Gamma q\,{\cal K}_UZ\,dr_*.
\]

Since \({\cal K}_U(y^2)=0\), a rational change of representative changes the
bulk period entirely through the displayed endpoint or patch term.
Therefore the apparent \(O(\omega^2)\) local contribution can cancel against
the required normalization concomitant.

There is also a nested scale in the unreduced companion frame: its moving
apparent divisor

\[
r=\frac{2i}{\omega}
\]

lies at \(r=O(\omega^{-1})\), inside the
\(r=O(\omega^{-1/2})\) turning region.  A uniform calculation must either
resolve that coalescing divisor explicitly or use the reduced cocycle while
retaining its full patch concomitant.  Dropping the endpoint term is not a
gauge-invariant high-overtone approximation.

## Missing global data

The repository does not presently contain the objects needed to turn the
local balance into a controlled QNM theorem:

1. a declared rapid-decay or monodromy contour and consistent branches of
   \(r_*\), \(\sqrt{\omega}\) and the Bessel coordinate;
2. Bessel-to-horizon and Bessel-to-infinity Stokes matrices in the certified
   factor-frame normalization;
3. the endpoint-normalization term \(B_n\) and its transformation under
   \(q_{\rm red}\);
4. uniform error bounds through the complex turning region and bounds on all
   remaining contour legs;
5. a proof that the leading Stokes sum and endpoint concomitant do not
   cancel;
6. certified high-overtone scalar QNM disks, simplicity and absence of a
   coincident spin-one zero.

The existing exact rational nonsplitting theorem guarantees that the local
differential class is nonzero generically.  It does not imply nonvanishing of
its pairing with any particular rapid-decay QNM cycle.

## Smallest falsifiable augmented-monodromy successor

The smallest controlled successor should remain a local asymptotic pilot,
not claim an EP2 tower:

1. **Certify the inner normal form.** Independently derive the scaled Bessel
   operator, the exact scaled cocycle density, the resonant \(r^{-4}\)
   projective coefficient and the projective concomitant from both the
   original and reduced companion gauges.
2. **Freeze a typed contour.** Declare one pair of anti-Stokes rays, all
   branch conventions and a Bessel-normalized leading solution \(Y_0\).
   Compute
   \[
   C_0
   =
   B_0-\frac{3i}{40}
   \int_{\Gamma_0}z^{-2}Y_0(z)^2\,dz
   +C_{\rm patch},
   \]
   including every endpoint and patch contribution.
3. **Run an independent full-system rail.** Integrate the unreduced repeated
   spin-two \(4\times4\) system at a declared sequence
   \(\omega,2\omega,4\omega\) along the same scaled contour.
4. **Test the asymptotic law.** Compare the appropriately normalized
   off-diagonal transfer with \(C_0\) and require a certified
   \(O(\lvert\omega\rvert^{-1/2})\) contraction rate.
5. **Fail closed.** Refuse promotion if the original and reduced gauges
   disagree after concomitant transport, the remainder does not contract, or
   the enclosure of \(C_0\) contains zero.

Only after this local pilot passes should its augmented monodromy be joined
to certified high-overtone QNM quantization.  That later join would still
need a noncancellation proof before establishing
\(\beta_n\neq0\), a Smith branch, an EP2, a double pole or generalized
ringdown.

## Claim boundary

This audit establishes exact local asymptotic formulas and identifies the
specific gauge-concomitant obstruction to reading a QNM theorem from them.
It does **not** establish:

- a value or nonzero theorem for any \(\beta_n\);
- the existence, location or simplicity of a physical QNM;
- a QNM Smith type or exceptional point;
- an inverse-connection or Green-resolvent double pole;
- a generalized ringdown term or an infinite EP2 tower;
- a time-domain or `LORENTZIAN-CAUSAL` theorem.

`CLOSE-OUT: SHORTFALL — exact local high-damping anatomy obtained, but the
global Stokes normalization, endpoint concomitant and noncancellation
estimate required for a QNM period are missing.`
