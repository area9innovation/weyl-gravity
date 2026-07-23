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

## Uniform endpoint Hilbert-space control

The matrices above define indefinite flux forms on an auxiliary positive
Hilbert topology.  With

\[
 \|a\|_{L^2}^2=\int_{1/2}^{3/4}a(\omega)^\dagger a(\omega)\,d\omega,
\]

the normalized current form is

\[
 [a,b]_\pm=\int_{1/2}^{3/4}
 a(\omega)^\dagger G_\pm(\omega)b(\omega)\,d\omega.
\]

This distinction matters: the positive \(L^2\) norm defines the completion;
the action-derived flux is the indefinite form being classified.

An exact Sturm audit of the Frobenius-square functions gives

\[
\begin{array}{c|cc}
 &\displaystyle\max\|G_\pm\|_F^2&
 \displaystyle\max\|G_\pm^{-1}\|_F^2\\ \hline
\mathscr I^-&1429056/25&7025/65536\\
\mathscr I^+&10389888/25&19825/65536 .
\end{array}
\]

For \(G_-\), both norm functions are strictly decreasing.  For \(G_+\),
each has exactly one interior critical point, and exact derivative signs
show that point is a minimum.  Thus the displayed maxima are certified
endpoint values, not sampled estimates.  Since
\(\|A\|_2\leq\|A\|_F\), a common explicit estimate is

\[
\boxed{
 \|a\|_{L^2}\leq\|G_\pm a\|_{L^2}
 \leq645\,\|a\|_{L^2}.
}
\]

The endpoint forms are therefore bounded and uniformly nondegenerate on the
whole closed interval.  Spectral calculus supplies the continuous
fundamental symmetry \(J_\pm=\operatorname{sign}(G_\pm)\) and the positive
Krein majorant defined by \(|G_\pm|\), uniformly equivalent to the auxiliary
\(L^2\) topology.  This canonical majorant is not a CPT metric, positive
energy, or particle norm.

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

The incoming/outgoing convention absorbs this past-boundary sign.  Once a
global map \(a_{\rm out}=T a_{\rm in}\) exists, the required conservation
identity is

\[
 T^\dagger J_{\rm out}T=J_{\rm in}.
\]

If horizon channels were absent, its null-infinity restriction would be
\(T^\dagger G_+T=G_-\).  No such \(T\) is constructed here.  Consequently,
the negative indices are not removable by changing the declared orientation,
but they are still only endpoint indices.

## Presymplectic-improvement scope

For the standard ambiguity

\[
 \theta\longmapsto\theta+\delta Y+dZ,
\]

\(\delta Y\) drops out by \(\delta^2=0\), and angular exact terms integrate
to zero.  There is also a scoped endpoint statement: a stationary, globally
defined, local finite-tangential-jet \(dZ\) with a finite trace-only pullback
changes the integrated current only by cut terms.  On the
\(C_c^\infty\) frequency core the inverse Fourier traces are Schwartz, so
those corners vanish; continuity then preserves the conclusion on the
declared \(L^2\) completion.

This does **not** establish unrestricted representative invariance.  A
complete audit still requires a typed improvement basis modulo \(d\) and
\(\delta\), radial and subleading pullbacks on all six endpoint jets,
uniform corner bounds, and the resulting additive matrices
\(\Delta G_{\pm,A}\).  Nonlocal, soft, explicit-time, nondecaying, and
radial/subleading improvements remain open.

## Interpretation

The endpoint spaces are not radical: all three matching trace directions at
each null infinity carry nonzero, nondegenerate flux data.  The form is
indefinite at both endpoints.  This is an endpoint theorem, not yet a
scattering theorem.  In particular it does not say whether any selected
\(\mathscr I^+\) direction is reached by horizon-regular data.

The mature comparison is Einstein scattering on Schwarzschild, where
finite-energy initial data and radiation states are related by Hilbert-space
isomorphisms.  The present theorem constructs only the endpoint side for the
axial Bach system.  Flat-space conformal-higher-spin scattering separately
shows that admissible conformal-gravity states need not be limited to
Einstein gravitons; it does not supply the Schwarzschild Bach connection.
These comparisons sharpen, rather than close, the missing global map.

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

EVIDENCE: `black_hole_programme/phase3/axial_null_flux_gram/receipt.json` records the exact producer, independent verifier, mutation, deep literal-current, schema, atlas, and test gates.

CLOSE-OUT: DONE — exact action-derived axial null-endpoint wave-packet flux Grams, trace-limit theorem, rank, radical and inertia are certified on the declared pilot interval.
