# Short Phase-2 plan (adopted 2026-07-22)

Status: adopted plan with adjustments; supersedes the first draft of this
note.  Source: Paper 15 limitations list, external-interest review of the
Phase-1 synthesis, and coordinating review.  Design rule: every principal
experiment must be valuable under either outcome.

Launch refinement: three short-lived read-only subagents independently
audited the CPT, Schwarzschild and sign-family inputs before work items were
written.  They found three load-bearing scope corrections:

- BRST compatibility is a chain-map/intertwining and cohomology-descent gate,
  not `Q^dagger eta = eta Q` with positive `eta`; the latter would force every
  nilpotent `Q` to vanish.
- the axial `ell=2` Schwarzschild result already covers every real nonzero
  frequency, so the new headline begins at generic `ell>=2`; polar and the
  full boundary topology remain independently gated;
- the first comparable sign family is the stationary compact dyonic
  `k1=0` coupling--background family.  Pure-magnetic off-wall branches do not
  preserve the same global stationary positive-frequency policy.

The implementation graph is split at these boundaries so a polar, boundary,
BRST or parity shortfall cannot erase an independently completed theorem.

## P2-A  Structured CPT feasibility (pilot, first gate)

A structured pseudo-Hermitian/CPT **preflight**, not a Mannheim
construction claim: solving $H^\dagger\eta=\eta H$ with $\eta>0$ does not
by itself construct a $C$ operator.  A genuine CPT result must also
produce the involution and its compatibility with $P$, $T$, the spatial
symmetries, the real-field structure, and BRST reduction.

Structural requirements on $\eta$, fixed before calculation (otherwise
every real diagonalizable finite matrix admits a manufactured positive
metric):

- $\eta$ belongs to the invariant commutant algebra;
- rational or polynomial in certified invariant operators;
- nonsingular across the parameter family;
- respects momentum and frequency decomposition;
- descends positively to $H^0(Q)$;
- compatible with the causal covariance.

For a nontrivial BRST complex, require an explicit `C` chain map or graded
intertwiner (normally `[C,Q]=0`) and positivity on a declared representative
of $H^0(Q)$.  Exact states are removed cohomologically; $Q$ is not required
to be self-adjoint in a positive metric.

Test blocks:

- compact Weyl–Maxwell Einstein and additional blocks;
- the reduced cylinder carrier;
- the counterflow quartet as an **exact negative control**: if
  $\eta>0$ and $H^\dagger\eta=\eta H$ then $\eta^{1/2}H\eta^{-1/2}$ is
  Hermitian with real spectrum, and the complex Hamiltonian–Hopf quartet
  makes such an $\eta$ impossible.  (This no-go remark is being added to
  Paper 15 directly.)

Deliverable: a symmetry-compatible $C/\eta$ construction or an exact
infeasibility certificate.  The secular-log connection to the
equal-frequency Pais–Uhlenbeck Jordan mechanism is an **analogy** to be
examined, not an identification.

## P2-B  Schwarzschild asymptotic phase diagram (headline)

The existing axial $\ell=2$ result is already symbolic in every real
$\omega\ne0$.  Phase 2 therefore starts at generic angular momentum and is
staged so the project does not hinge on a full scattering theory:

1. **General asymptotic-coefficient theorem.**  For real $\omega\neq0$,
   $\ell\ge2$, both parities: reconstruction, current powers, leading
   Lee–Wald coefficients $A_\ell(\omega)$, and a certified classification
   of their exceptional real zero sets.
2. **Boundary-topology theorem.**  Decide whether those asymptotics
   define finite flux, wave-packet norm, or another physically justified
   asymptotic phase space.
3. **Full phase space and scattering** — only if gates 1–2 warrant it.

An explicit $A_\ell(\omega)$ with a certified zero-set classification is
already a substantial standalone result (the Lorentzian counterpart of
the Euclidean/AdS Einstein-selection arguments).

## P2-C  Background robustness of the sign result

Use the stationary compact dyonic $k_1=0$ family at fixed magnetic Chern
number.  With

\[
 \beta=\frac{\kappa N^2}{4q_{\min}^2},\qquad
 k_2=\frac1{\beta(1+\tau^2)},\qquad
 P=\frac{2q_{\min}}{N\kappa(1+\tau^2)},\qquad E=\tau P,
\]
\[
 \alpha_B=\frac{3N^2}{4q_{\min}^2}(1+\tau^2).
\]

This is explicitly a coupling--background family, not an open family within
one fixed $\alpha_B$ theory.  It preserves the compact Cauchy surface and
global $H=\partial_t$.  First decide whether the electric background preserves
parity only after a discrete duality/charge action; otherwise use a combined
mixed-parity carrier.  Then compute the family map

  (background parameters) ↦ (inertia h_E, inertia h_A, rad Ω).

Output: either an open robustness region or exact signature walls with a
mechanism explaining them.  Either is the citable form of the Result
card A surprise.

## P2-D  Optional Lorentzian quantum theorem (stretch, not closure)

One BRST-compatible Hadamard construction or scoped no-go on one
complete causal BV complex.  High value, but Phase 2 does not wait for
it: run the pseudo-Hermitian pilot first — it determines which
covariance and adjoint structure the Hadamard construction should
respect.

## P2-E  Mandatory theory-admission gate

No new changed theory without: causal completeness; stable reduced
dynamics; acceptable charge interpretation; nonlinear preservation; a
predeclared operational observable.

## Not prioritized

- full arbitrary-support bounded nonlinear cone;
- more isolated counterflow blocks;
- another changed action;
- a standard-matter anomaly census (ordinary-matter route structurally
  unpromising);
- cubic normal forms of the quartet, unless needed to interpret a nearby
  signature wall.  A quartet figure is communication, not research.

## Immediate Paper 15 additions (pre-Phase-2)

1. Counterflow quartet lies in the broken-PT regime and admits no
   positive pseudo-Hermitian metric (spectral no-go, not a norm choice).
2. Result A's sign pattern is adjoint-dependent evidence motivating —
   not proving — the CPT alternative.
3. The local anomaly coefficients are unchanged by similarity
   transformations within the same local operator and regulator class;
   they are not claimed invariant under a genuinely different complex
   contour and measure, which requires its own regulator/QAP analysis.

## Closure rule

Short Phase 2 closes with: an exact structured-CPT feasibility
classification; a general real-frequency Schwarzschild asymptotic phase
diagram; a compact-background sign-robustness theorem; an updated
Paper 15.  The Hadamard result is a high-value bonus.

Impact estimates: CPT pilot alone ≈ 6–6.5/10; general Schwarzschild
theorem or exceptional-frequency classification ≈ 8/10; Schwarzschild +
sign-family mechanism + CPT classification ≈ 8–8.5/10.
