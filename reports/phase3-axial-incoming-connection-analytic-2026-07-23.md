# Phase 3 analytic axial incoming-connection theorem

Date: 23 July 2026

## Result

For the strict pure-Weyl axial \(\ell=2\) system on Schwarzschild with

\[
\omega\in[1/2,3/4],
\]

the exact horizon-regular frame and the exact
\(\mathscr I^-\) incoming frame each contain one Jost line for all three
diagonal factors of the certified triangular module:

\[
\text{spin-two RW},\qquad
\text{spin-two RW},\qquad
\text{spin-one RW}.
\]

The resulting three-by-three incoming connection block obeys

\[
\boxed{
\det T_-(\omega)=
-\frac{(2\omega-i)(4\omega-i)^2}{4(\omega-i)}
A_{{\rm in},2}(\omega)^2A_{{\rm in},1}(\omega)
\ne0.
}
\]

Therefore

\[
\boxed{T_-(\omega)\in GL(3,\mathbb C)}
\]

throughout the real pilot interval.  This conclusion uses exact factor
reduction and the real-potential Wronskian, not interval radial transport.

## Exact endpoint assignments

Let

\[
\mathcal A(y)=2P+2rP'-2i\omega rQ.
\]

For a carrier state this is the leading amplitude of the spin-one master
\(y=r^2(r-2)Z\), where \(Z=L_{\rm RW}P\).

At the future horizon,

\[
\mathcal A(XH0a)=4\omega^2-3i\omega+4,
\]

\[
\mathcal A(XH0b)=4(\omega-i)(2\omega-i).
\]

The second expression has no real zero.  Hence the regular carrier plane has
the factor-adapted basis

\[
RH=XH0a-
\frac{4\omega^2-3i\omega+4}
{4(\omega-i)(2\omega-i)}XH0b,
\qquad
SH=XH0b.
\]

The quotient kills \(RH\), so \(RH\) is the carrier spin-two line, while
\(SH\) projects onto the spin-one horizon-ingoing line.  Their scalar
horizon amplitudes are

\[
h_{RH}=\frac{i\omega(4\omega-i)}{2(\omega-i)},
\qquad
h_{SH}=4(\omega-i)(2\omega-i).
\]

The third line is the Einstein-kernel mode \(EH0\).  Under

\[
\Psi=\frac{(1-2/r)H_1+H_0}{r},
\]

its horizon amplitude is

\[
h_{EH}=-\frac{i\omega(4\omega-i)}{4(\omega-i)}.
\]

At \(\mathscr I^-\),

\[
\mathcal A(XI0)=2,\qquad
\mathcal A(XI1)=-2i\omega.
\]

Thus

\[
RI=XI0-\frac{i}{\omega}XI1,\qquad SI=XI1
\]

are respectively the carrier spin-two and spin-one incoming lines.  Their
incoming amplitudes are

\[
i_{RI}=1,\qquad i_{SI}=-2i\omega.
\]

The Einstein-kernel line \(EI0\) has

\[
i_{EI}=-i\omega.
\]

Both changes from the repository endpoint frames to these factor-adapted
frames are triangular with determinant one.

## Wronskian nonvanishing

The diagonal potentials are

\[
V_2=\frac{6(r-2)(r-1)}{r^4},
\qquad
V_1=\frac{6(r-2)}{r^3}.
\]

They are real, nonnegative and short-range on the exterior.  Indeed, with
\(dr_*=dr/f\),

\[
\int_{2}^{\infty}\frac{V_2}{f}\,dr=\frac94,
\qquad
\int_{2}^{\infty}\frac{V_1}{f}\,dr=3.
\]

Normalize each horizon-ingoing Jost solution to unit amplitude.  At infinity
write

\[
u_H=
A_{{\rm in},s}e^{+i\omega r_*}
+A_{{\rm out},s}e^{-i\omega r_*}.
\]

Conservation of the scalar Wronskian gives

\[
|A_{{\rm in},s}|^2-|A_{{\rm out},s}|^2=1,
\]

so \(A_{{\rm in},s}\) cannot vanish for real nonzero frequency.  Multiplying
the three exact endpoint normalization ratios yields

\[
C(\omega)=
-\frac{(2\omega-i)(4\omega-i)^2}{4(\omega-i)}.
\]

Its modulus is manifestly nonzero:

\[
|C(\omega)|^2=
\frac{(4\omega^2+1)(16\omega^2+1)^2}
{16(\omega^2+1)}.
\]

Triangularity then proves the determinant formula and invertibility of
\(T_-\).

## Scope boundary

This theorem classifies only the incoming block \(T_-\).  It does not say
that either reflection amplitude is nonzero, and therefore does not fix the
rank of the outgoing \(\mathscr I^+\) block \(T_+\).  It also does not exclude
upper-half-plane poles, prove stability, construct a CPT metric, establish a
positive total flux, or define a unitary scattering theory.

The result is nevertheless global in the radial direction: it proves that
the three horizon-regular factor channels have nonzero incoming Jost
coefficients, without numerically transporting a correlated three-plane
across the exterior.

## Verification

```bash
python3 -m black_hole_programme.phase3.axial_incoming_connection_analytic.verify
python3 -m unittest -v \
  black_hole_programme.phase3.axial_incoming_connection_analytic.tests.test_connection
```

The verifier imports all three source certificates by content hash,
reconstructs the quotient amplitudes from the frozen endpoint heads, checks
the factor-basis changes and normalization ratios, verifies the two exact
real short-range potentials and their \(L^1(dr_*)\) integrals, derives the
determinant prefactor, and rejects outgoing, reflection, stability and
quantum overpromotions.
