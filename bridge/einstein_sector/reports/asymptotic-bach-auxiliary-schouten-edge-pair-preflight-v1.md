# Asymptotic Bach auxiliary-Schouten edge-pair preflight

## Exact first-order extension

The local-counterterm theorem proves that the fixed-boundary metric carrier
has zero horizontal presymplectic class.  The next local possibility is
therefore an independent tensor momentum, not another JKM coefficient.

Modulo the four-dimensional Euler density,

\[
\frac{\alpha_B}{8}C^2
=\frac{\alpha_B}{4}
\left(R_{ab}R^{ab}-\frac13R^2\right).
\]

Introduce the symmetric auxiliary Schouten tensor

\[
s_{ab}
=\frac{\alpha_B}{2}
\left(R_{ab}-\frac16g_{ab}R\right)
=\alpha_B P_{ab}.
\]

The exact Legendre transform is

\[
L_{\rm aux}
=s^{ab}G_{ab}
-\frac1{\alpha_B}\left(s_{ab}s^{ab}-s^2\right).
\]

Eliminating \(s_{ab}\) reproduces the curvature-squared density above.  The
curvature momentum entering the boundary term is the trace reversal

\[
A_{ab}=s_{ab}-\frac12g_{ab}s.
\]

Its tensor Lee--Wald potential is

\[
\Theta^\mu_{\rm aux}
=\sqrt{-g}
\left(
A^{ab}\delta\Gamma^\mu{}_{ab}
-A^{\mu b}\delta\Gamma^a{}_{ab}
\right).
\]

At the flat background \(\bar s=0=\bar A\), the bilinear current is the cross
current

\[
\omega^\mu_{\rm aux}
=\delta A_1^{ab}\delta\Gamma^\mu_{2\,ab}
-\delta A_1^{\mu b}\delta\Gamma^a_{2\,ab}
-(1\leftrightarrow2).
\]

This supplies the full-tensor version of the source--response pairing that
the reduced \(p=0/p=1\) calculation suggested.

## Minimality and branch meaning

At each cut point the radiative metric has two tracefree tensor normal-jet
components.  The metric-only class has rank zero.  The tracefree auxiliary
tensor \(s_{AB}^{\rm TF}=A_{AB}^{\rm TF}\) supplies exactly two dual components in the
principal flux symbol.  In the basis

```text
(nabla_n h_plus,nabla_n h_cross,s_plus,s_cross)
```

the algebraic cut matrix is

\[
\begin{pmatrix}
0&I_2\\
-I_2&0
\end{pmatrix},
\qquad
\det=1,\quad \operatorname{rank}=4.
\]

Thus \(s_{AB}^{\rm TF}\) is a minimal-rank full-tensor candidate edge
variable at principal normal-jet level.  This is not yet a cut symplectic
form: the Bondi recursion, tangential terms and gauge quotient must still
turn the normal-jet block into a well-defined form on boundary solutions.
The auxiliary variable also gives the correct branch dictionary:

- on the flat Einstein image, \(\delta R_{ab}=0\), hence \(s_{ab}=0\);
- additional Bach data have \(s_{ab}\ne0\);
- the metric \(1/r\) coefficient alone cannot distinguish a \(p=0\)
  recursion contribution from a leading \(p=1\) contribution.

The last point is why treating two falloff labels as independent canonical
coordinates is insufficient without the Schouten/Bach defect variable.

## Gauge action

The auxiliary tensor is invariant under linearized diffeomorphisms on flat
space.  Under a linear Weyl ghost,

\[
\delta_\sigma s_{ab}
=-\alpha_B\partial_a\partial_b\sigma,
\qquad
\delta_\sigma A_{ab}
=\alpha_B\left(
-\partial_a\partial_b\sigma
+\frac12\eta_{ab}\Box\sigma
\right).
\]

This transformation must be part of the eventual boundary ghost complex; the
prequotient rank is not yet a gauge-descended BFV theorem.

## Fail-closed boundary

The following remain open:

- Bondi weights and recursion for \((h_{ab},s_{ab})\);
- finite-cut renormalization of the tensor \(p=0/p=1\) pairing;
- boundary-preserving ghost falloffs, antifields and BFV constraints;
- nondegeneracy after the exact boundary quotient;
- \(\mathscr I^-/i^0/\mathscr I^+\) corner matching;
- differentiable \(P_0\) and \(D_M\) charges.

This is a `LOCAL-ALGEBRAIC` preflight, not a causal, particle, scattering,
stability, positivity, unitarity or quantum theorem.

CLOSE-OUT: SHORTFALL — the minimal full-tensor auxiliary edge variable and prequotient current are certified, but Bondi renormalization, BV-BFV descent, corner matching and charges remain open
EVIDENCE: ASYMPTOTIC_BACH_AUXILIARY_SCHOUTEN_EDGE_PAIR_PREFLIGHT_V1
