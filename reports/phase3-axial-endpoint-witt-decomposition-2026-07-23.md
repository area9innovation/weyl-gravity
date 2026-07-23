# Phase 3 axial endpoint Witt decomposition

Date: 23 July 2026

## Result

The exact axial \(\ell=2\) endpoint flux Grams admit explicit
Witt-adapted bases for every

\[
\omega\in[1/2,3/4].
\]

The calculation uses the dimensionless Hermitian form
\(iF^r/(\pi\alpha_{\rm W})\), with the Stokes endpoint orientation
applied.  For \(\alpha_{\rm W}>0\), each endpoint splits as

\[
(\mathbb C^{1,1})\ \widehat\oplus\ (\mathbb C^{0,1}),
\]

so its full inertia is \((1,2,0)\) and its radical is zero.

## Past null endpoint

The source coordinate order is

\[
(XI0,XI1,EI0),
\]

and the oriented form is the negative of the coordinate Gram.  Define

\[
E=EI0,\qquad X=XI0,\qquad
Y=-\omega^2XI0-2i\omega XI1+EI0.
\]

In the ordered basis \((E,X,Y)\), the exact Gram is

\[
\begin{pmatrix}
0 & 384\omega/5 & 0\\
384\omega/5 & 576/(5\omega) & 0\\
0 & 0 & -384\omega^3/5
\end{pmatrix}.
\]

Thus \(E\) is null,

\[
\langle E,X\rangle=\frac{384\omega}{5},
\qquad
\det G_{\langle E,X\rangle}
=-\frac{147456\omega^2}{25}<0,
\]

and \(Y\) is orthogonal to \(E,X\), with

\[
\langle Y,Y\rangle=-\frac{384\omega^3}{5}<0.
\]

The shifted partner

\[
X_{\rm null}=X-\frac{3}{4\omega^2}E
\]

is also null and retains the same nonzero pairing with \(E\), making the
Witt plane explicit.

The change-of-basis determinant is \(-2i\omega\), hence is nonzero
uniformly on the pilot interval.

## Future null endpoint

The source coordinate order is

\[
(XI2,XI3,EI2),
\]

and the coordinate Gram already has the future endpoint orientation.  Define

\[
E=EI2,\qquad X=XI3,\qquad
Y=i\omega XI2+4(4\omega^2-i\omega-2)XI3.
\]

In the ordered basis \((E,X,Y)\), the exact Gram is

\[
\begin{pmatrix}
0 & 96\omega/5 & 0\\
96\omega/5 & -48\omega(16\omega^2-5)/5 & 0\\
0 & 0 & -384\omega/5
\end{pmatrix}.
\]

Consequently,

\[
\langle E,X\rangle=\frac{96\omega}{5},
\qquad
\det G_{\langle E,X\rangle}
=-\frac{9216\omega^2}{25}<0,
\]

while \(Y\perp E,X\) and

\[
\langle Y,Y\rangle=-\frac{384\omega}{5}<0.
\]

Here the second null vector is

\[
X_{\rm null}=X+\frac{16\omega^2-5}{4}E.
\]

The change-of-basis determinant is \(-i\omega\), also uniformly nonzero.

## Interpretation and boundary

The decomposition exposes the exact anatomy behind the previously certified
endpoint inertia: a null-paired hyperbolic plane plus an independent negative
line.  It is basis-explicit and uniform on the closed pilot interval.

It does **not** identify the algebraic vector \(Y\) with a spectral
derivative or radial Jordan partner.  It does not produce a
time-translation Jordan chain, a scalar or matrix repeated-factor
representation of the Bach operator, or a horizon-to-infinity scattering
state.  Those questions require separate operator and global-connection
data; matching endpoint algebra is not evidence of their origin.

## Verification

```bash
python3 -m black_hole_programme.phase3.axial_endpoint_witt_decomposition.verify
python3 -m unittest -v \
  black_hole_programme.phase3.axial_endpoint_witt_decomposition.tests.test_witt
```

The verifier imports and hashes the frozen formal Gram file, reconstructs
both oriented Hermitian forms, performs both exact basis changes over
\(\mathbb Q(i,\omega)\), and checks all nullity, cross-pairing,
orthogonality, determinant, sign, radical, inertia and claim-boundary
statements.  Mutation tests reject orientation, basis, coefficient, sign,
interval, inertia, provenance and overpromotion errors.
