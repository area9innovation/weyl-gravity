# Asymptotic Bach boundary-counterterm/corner close-out

## Disposition

The existing-field local counterterm route is exactly obstructed.

The full tensor curvature-squared potential is

\[
P^{abcd}=\frac{\alpha_B}{4}C^{abcd},\qquad
\Theta^a=2\sqrt{-g}
\left(P^{abcd}\nabla_d\delta g_{bc}
-(\nabla_dP^{abcd})\delta g_{bc}\right).
\]

On flat Einstein Jacobi fields, the identity

\[
C^2=E_4+2R_{ab}R^{ab}-\frac23R^2
\]

makes its horizontal presymplectic class zero.  Every finite-order local
Lee--Wald/JKM ambiguity made from the existing metric and boundary jets has
the form

\[
L\mapsto L+dB,\qquad
\Theta\mapsto\Theta+\delta B+dY.
\]

The \(B\) term does not change the symplectic current, and the \(Y\) term
changes only its horizontal representative.  Therefore no such counterterm
can turn the fixed-boundary Einstein-radiative restriction into a
nondegenerate form.  The nonexactness check is coefficient-free: the
one-polarization news density

\[
f\,\partial_u g-g\,\partial_u f
\]

has nonzero Euler derivatives, whereas the sign-mutated exact derivative
\(\partial_u(fg)\) is rejected by the independent rail.

The reduced raw calculation remains consistent with this theorem.  Its
\(p=0\) self-divergence is a retarded-time corner derivative, while the
fixed-boundary \(p=1\) self-form is radical.  A whole-\(\mathscr I\)
cancellation is not promoted to a finite cut form.

## Minimal escape from the obstruction

The first local extension outside the exhausted ambiguity class is the
independent auxiliary Schouten tensor

\[
s_{ab}=\alpha_B P_{ab}.
\]

Modulo the Euler density,

\[
L_{\rm aux}
=s^{ab}G_{ab}
-\frac1{\alpha_B}(s_{ab}s^{ab}-s^2)
\]

is exactly equivalent to the \(C^2\) bulk density.  Its curvature momentum is
\(A_{ab}=s_{ab}-\tfrac12g_{ab}s\), with boundary potential

\[
\Theta^\mu_{\rm aux}
=\sqrt{-g}
\left(A^{ab}\delta\Gamma^\mu{}_{ab}
-A^{\mu b}\delta\Gamma^a{}_{ab}\right).
\]

The tracefree normal-jet principal block on

```text
(nabla_n h_plus,nabla_n h_cross,s_plus,s_cross)
```

has determinant one and rank four.  This proves that
\(s_{AB}^{\rm TF}=A_{AB}^{\rm TF}\) supplies the minimal two dual tensor
components.  It does not yet prove a finite cut symplectic form or a
gauge-descended boundary phase space.

## Claim boundary

This closes only the local existing-field counterterm/corner route.  The
following belong to the successor edge-pair work item:

- coupled Bondi/polyhomogeneous recursion and weights for
  \((h_{ab},s_{ab})\);
- the boundary ghost, antifield, constraint and BFV complex;
- finite-cut renormalization and nondegeneracy after gauge descent;
- \(\mathscr I^-/i^0/\mathscr I^+\) corner matching;
- differentiable \(P_0\) and \(D_M\) charges and fluxes.

\(H_{\rm ESU}\) remains not applicable on one fixed Minkowski patch, and no
map to radial-quantization \(D\) is asserted.  No causal, particle,
scattering, stability, positivity, unitarity or quantum conclusion follows.

## Evidence

- `ASYMPTOTIC_BACH_RAW_FLUX_CORNER_OBSTRUCTION`;
- `ASYMPTOTIC_BACH_LOCAL_COUNTERTERM_COHOMOLOGY_OBSTRUCTION_V1`;
- `ASYMPTOTIC_BACH_AUXILIARY_SCHOUTEN_EDGE_PAIR_PREFLIGHT_V1`;
- their independent verifiers, mutation controls, tier receipts and
  fail-closed atlas fragments.

CLOSE-OUT: OBSTRUCTED — the complete existing-field local JKM counterterm class cannot yield a nondegenerate fixed-boundary Einstein-radiative form, and the minimal required Schouten auxiliary edge variable is certified
EVIDENCE: ASYMPTOTIC_BACH_LOCAL_COUNTERTERM_COHOMOLOGY_OBSTRUCTION_V1
