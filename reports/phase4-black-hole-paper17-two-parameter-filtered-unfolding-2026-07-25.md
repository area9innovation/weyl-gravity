# Paper 17 two-parameter filtration-protected EP2 phase diagram

## Result

Paper 17 now embeds the physical Einstein--Weyl mass deformation in a
two-parameter local unfolding.  In the normalized critical frame,

\[
T(z;m,\epsilon)=
\begin{pmatrix}
z&-1\\
c_n\epsilon&z-\nu_nm
\end{pmatrix}
+\text{higher order},
\]

where the mass parameter \(m\) preserves the Einstein submodule and a
declared transverse parameter \(\epsilon\) breaks it.  The coefficient
\(c_n\ne0\) belongs to that chosen transverse direction; no physical
numerical value of \(c_n\) is claimed.

For the reduced Evans determinant \(F\), both coefficients are intrinsic:

\[
\nu_n=-\frac{2F_{\omega m}}{F_{\omega\omega}},
\qquad
c_n=\frac{2F_\epsilon}{F_{\omega\omega}}.
\]

The ratios are unchanged by multiplying \(F\) by an analytic unit.
At operator level,

\[
c_n=
\frac{\langle W_0,BV_0\rangle}{
\left\langle W_0,\mathbb L_n'V_1+
\tfrac12\mathbb L_n''V_0\right\rangle}.
\]

This is the Lidskii reverse-coupling coefficient.  It complements the
forward extension overlap \(\beta_n\); the physical mass direction has
zero reverse coupling because it preserves the Einstein submodule.

The spectral discriminant is

\[
\Delta^2=\nu_n^2m^2-4c_n\epsilon+\cdots.
\]

This gives:

- linear analytic splitting on the physical axis \(\epsilon=0\);
- square-root splitting on a generic transverse path;
- the exceptional parabola
  \(\epsilon_{\rm EP}=\nu_n^2m^2/(4c_n)+O(m^3)\);
- branch exchange only when the discriminant is encircled.

The exceptional parabola is a complex-analytic curve.  A real slice
contains a real exceptional curve only when its coefficient respects that
slice's reality structure.  Also, two notions of transversality are kept
separate: the QNM divisors intersect transversely in \((\omega,m)\), while
the physical mass axis is tangent to the exceptional curve in
\((m,\epsilon)\).

## Gap-controlled confluence

The right and left modes have biorthogonal pairing \(\pm\Delta\), so

\[
\|P_\pm\|\asymp|\Delta|^{-1}.
\]

The normalized difference has the path-independent critical limit

\[
\frac{\Delta}{2}(P_+-P_-)\longrightarrow
N=
\begin{pmatrix}0&1\\0&0\end{pmatrix}.
\]

For a uniformly positive separated-branch metric,

\[
\operatorname{cond}H\asymp|\Delta|^{-2}.
\]

The earlier \(m^{-1}\) projector and \(m^{-2}\) metric laws are therefore
the physical-axis specialization.  A generic mixing axis instead gives
\(\epsilon^{-1/2}\) and \(\epsilon^{-1}\).

## Certification threshold

A lower-left numerical or gauge error must satisfy

\[
|c_n\epsilon_{\rm err}|\ll|\nu_n^2m^2|
\]

to recover the physical QNM velocity.  For
\(\epsilon_{\rm err}=O(m^p)\):

- \(p<2\): generic mixing dominates;
- \(p=2\): splitting remains linear but its coefficient changes;
- \(p>2\): the physical coefficient is recovered;
- exact filtration: \(\epsilon_{\rm err}=0\).

The natural crossover variable is

\[
\chi=\frac{4c_n\epsilon}{\nu_n^2m^2}.
\]

The mutation suite verifies the discriminant, exceptional curve, gap
normalization, and rejects an incorrect first-order error tolerance.

## Centered resolvent crossover

The correct centered frequency is

\[
\zeta=z-\frac{\nu_nm}{2},
\qquad
\det T=\zeta^2-\frac{\Delta^2}{4}.
\]

For \(|\zeta|\gg|\Delta|\), the upper-right response is

\[
(T^{-1})_{12}
=\zeta^{-2}
\left[1+O\!\left(\Delta^2/\zeta^2\right)\right].
\]

For \(|\zeta|\lesssim|\Delta|\), the two simple poles must be resolved.
Using raw \(z\) without centering is insufficient near the exceptional
parabola because the common pole location can move while the gap vanishes.

## Claim boundary

Established:

- the exact leading two-parameter normal form and discriminant;
- invariant determinant-derivative formulas for \((\nu_n,c_n)\);
- the Lidskii root-chain formula for reverse coupling;
- physical linear versus generic square-root splitting;
- exceptional parabola and branch monodromy;
- gap-controlled projector and positive-metric laws;
- path-independent nilpotent recovery;
- the \(o(m^2)\) filtration-error requirement;
- the centered local resolvent crossover.

Not established:

- a physical or numerical value of \(c_n\);
- that every perturbation breaks the filtration;
- a global retarded contour deformation;
- a complete overtone tower;
- time-domain stability or a quantum positivity statement.

CLOSE-OUT: DONE — the filtration-protected EP2 is promoted to an exact
two-parameter local phase diagram with fail-closed mutation controls.
EVIDENCE: reports/PAPER17_TWO_PARAMETER_UNFOLDING_TIER_RECEIPT.json
