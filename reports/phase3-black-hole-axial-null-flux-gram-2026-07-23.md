# Phase 3 axial null-endpoint flux Grams

Date: 23 July 2026

## Result

For strict four-dimensional pure Weyl gravity linearized about Schwarzschild
with \(M=1\), axial \(\ell=2\), and positive-frequency support
\(\omega\in(1/2,3/4)\), the previously constructed exact wave-packet traces
at \(\mathscr I^-\) and \(\mathscr I^+\) now carry exact action-derived
Lee--Wald flux forms.

In the matching trace bases

\[
 \mathscr I^-:\ (\mathrm{XI0},\mathrm{XI1},\mathrm{EI0}),\qquad
 \mathscr I^+:\ (\mathrm{XI2},\mathrm{XI3},\mathrm{EI2}),
\]

and after dividing by \(\pi\alpha_{\rm W}\), the Stokes-oriented past Gram is

\[
G_-=
\begin{pmatrix}
 \frac{576}{5\omega} & \frac{96i}{5} & \frac{384\omega}{5}\\
 -\frac{96i}{5} &-\frac{144\omega}{5}&-\frac{192i\omega^2}{5}\\
 \frac{384\omega}{5}&\frac{192i\omega^2}{5}&0
\end{pmatrix},
\]

whereas the future Gram is

\[
G_+=
\begin{pmatrix}
\frac{384(-512\omega^6+640\omega^4-278\omega^2+39)}{5\omega}
&
\frac{12288i\omega^4-3072\omega^3-9984i\omega^2}{5}
+192\omega+384i
&
\frac{-1536i\omega^2+384\omega+768i}{5}
\\
\frac{-12288i\omega^4-3072\omega^3+9984i\omega^2}{5}
+192\omega-384i
&
-\frac{768\omega^3}{5}+48\omega
&
\frac{96\omega}{5}
\\
\frac{1536i\omega^2+384\omega-768i}{5}
&
\frac{96\omega}{5}
&
0
\end{pmatrix}.
\]

Both matrices are Hermitian and

\[
 \det G_-=\frac{14155776}{125}\omega^3,\qquad
 \det G_+=\frac{3538944}{125}\omega.
\]

They therefore have rank three and zero radical throughout the closed pilot
interval.  Exact LDL pivots at \(\omega=1/2\) have signs
\((+,-,-)\) at both endpoints.  Since neither determinant vanishes, the
inertia is constant:

\[
\boxed{\operatorname{inertia}(G_-)
=\operatorname{inertia}(G_+)=(1,2,0)}
\qquad(\alpha_{\rm W}>0).
\]

Changing the overall sign of the action reverses the positive and negative
counts.

## Why the formal matrices define exact wave-packet flux

The frozen current is the action-derived `LinearizedTheta` representative,
with no boundary counterterm or radial/corner improvement added.  It is
written in Schwarzschild \(t\) coordinates, so the pullback from ingoing
Eddington--Finkelstein variables includes

\[
h_{1,t}=h_{1,\mathrm{EF}}+B^{-1}h_{0,v},
\qquad
\partial_r|_t=\partial_r|_v+\frac{i\omega}{B}
\]

on the positive-frequency slot, with the conjugate sign on the Hermitian
slot.  This differentiated reconstruction is essential.

The exact current contains radial derivatives through order three and its
coefficients grow no faster than \(r^0\).  The largest formal metric head is
\(O(r^2)\); the first omitted term is uniformly \(O(r^{-4})\).  Hence every
formal/exact cross-current error is \(O(r^{-2})\), and every
remainder/remainder error is \(O(r^{-8})\), up to harmless logarithms.  The
certified Volterra envelope supplies uniform frequency derivatives through
order three and cross-rate decay \(p\geq5\).

On the smooth compactly supported frequency core, Plancherel diagonalizes
the time-integrated finite-radius current.  Dominated convergence gives the
matching endpoint limit, while cross-rate terms vanish by the
Riemann--Lebesgue lemma.  Because every matrix entry is bounded on the compact
frequency interval, the form extends continuously to
\(L^2([1/2,3/4];\mathbb C^3)\).

The sign at \(\mathscr I^-\) deserves care.  The coordinate \(F^r\) points
toward increasing \(r\), but the past null boundary has the opposite Stokes
orientation.  Thus \(G_-\) is minus the coordinate-radial Gram, whereas
\(G_+\) equals it.  This is why the two endpoint inertias agree.

## Interpretation

The endpoint spaces are not radical: all three matching trace directions at
each null infinity carry nonzero, nondegenerate flux data.  The form is
indefinite at both endpoints.  This is an endpoint theorem, not yet a
scattering theorem.  In particular it does not say whether any selected
\(\mathscr I^+\) direction is reached by horizon-regular data.

## Does not establish

- a horizon-to-infinity connection or scattering matrix;
- population of an endpoint direction by regular horizon data;
- stability, quasinormal-mode exclusion, or time-domain decay;
- a positive CPT metric, particle norm, or unitarity theorem;
- the polar sector, other angular modes, or frequencies outside the pilot
  interval;
- invariance under unrestricted radial or corner improvements of the
  presymplectic potential.

## Verification

```bash
python3 -m black_hole_programme.phase3.axial_null_flux_gram.produce --check
python3 -m black_hole_programme.phase3.axial_null_flux_gram.verify
python3 -m black_hole_programme.phase3.axial_null_flux_gram.mutations
python3 -m unittest black_hole_programme.phase3.axial_null_flux_gram.tests.test_null_flux_gram
```

The complete literal-current replay is deliberately separate because it is
the expensive rail:

```bash
python3 -m black_hole_programme.phase3.axial_null_flux_gram.formal_gram --check --jobs 4
```

The machine-readable result is
`black_hole_programme/phase3/axial_null_flux_gram/certificate.json`.
