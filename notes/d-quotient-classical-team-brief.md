# Classical team brief: is \(D\) gauge or charged?

## Commission

Answer one question:

\[
\boxed{
\text{Is }D\text{ genuinely gauge after adding clocks, interactions, quantization, or boundaries?}
}
\]

Here \(D\) is cylinder-time translation/dilatation in the residual conformal
algebra.  Your task is **not** to extend the existing closed-cylinder theorem.
Construct the strongest classical counterexample to quotienting by \(D\), then
report exactly where that counterexample survives or fails.

The certified vacuum-cylinder Cartan calculation is a baseline under its stated
hypotheses, not a premise to export to other phase spaces.  In particular, do
not infer that a residual transformation is proper gauge from its occurrence in
a BRST complex.  Decide proper gauge versus physical symmetry from the
presymplectic degeneracy and the renormalized covariant phase-space charge.

The centered classes \([W_+^2]\) and \([W_-^2]\) are deformation/vertex
classes.  They are not one-particle graviton states.

## Programme atlas and tangent-cone deliverables (2026-07-18)

The classical fragment of the programme residual atlas is generated at
`d_quotient_classical/atlas/classical-causal-atlas-fragment.json`.  Its
producer, independent verifier, tests, strict shared-schema validation and
human crosswalk report are part of the same handoff.  The fragment covers the
vacuum cylinder, Berger clock, conformal Nariai orbit, the transverse Nariai
tangent and the relative-open Bach-flat parent class.  It uses only
`CERTIFIED`, `OBSTRUCTED`, `OPEN`, `NOT_APPLICABLE` and `NO_CERTIFIED_MAP`,
and it never imports a mode across backgrounds or carriers without an
explicit crosswalk.  In particular, the Berger carrier remains unsplit and
the broad Bach-flat theorem remains a parent theorem rather than a class-wide
metric theorem.

The abstract second deliverable is certified by
`FINITE_HARMONIC_SECOND_ORDER_TANGENT_CONE_THEOREM_V1`.  After complete
harmonic closure, Noether-row reduction and removal of gauge-null directions,
the second-order tangent cone in correction class \(\mathcal C\) is

\[
\mathcal Z_2^{\mathcal C}
=\{u\in\ker q_1:\mu_X(u)=0,\ R_j^{\mathcal C}(u)=0\}.
\]

The correction class is part of the theorem, not metadata: a resonant Fourier
obstruction can persist for bounded/quasiperiodic corrections while
disappearing after a smooth secular \(t e^{i\omega t}\) correction or a
compatible retarded integral.  Stabilizer moment-map conditions remain
separate and do not disappear merely because the correction space is enlarged.

The transverse Nariai connection/curvature-jet gate is now scoped exactly.
The fixed-frame Levi--Civita variation is nonzero and
\((\nabla_0\delta C)_{0202}=-\sqrt2\).  The old locally symmetric PBW backend
therefore cannot produce the true middle/Schur derivative: it omits the
Leibniz terms in which an outer derivative hits the varied curvature.  Its
frozen-parallel response is retained as a checked diagnostic, including exact
normal-tractor-square agreement, but is marked `OBSTRUCTED` rather than
promoted.

The complete jet-aware gate is now certified.  An exact bivariate Taylor-jet
recurrence derives every coordinate covariant curvature jet requested through
order three, reproduces the earlier moving-frame first jet, and closes the
corrected BGG first square and parent Yang--Mills identity.  The exact
shifted-chain variation retains 207 coefficients.  The endpoint gauge defect
contains zeroth- and second-order words, so a purely algebraic Schur
correction cannot suffice.

The complete first-order differential screen is now solved as well.  For each
of the nine output rows the exact coefficient map has shape `60 x 45` and
rank 45; every augmented system has rank 45 and no free parameter.  Hence a
unique 59-coefficient local first-order Schur correction kills the complete
endpoint gauge defect.  This is a gauge-repair theorem, not yet an action or
cyclic theorem.

The post-delivery shifted-chain audit rules out the simplest continuation.
If only the Φ row is corrected by an arbitrary local operator of order at
most one, its coefficient map has shape `225 x 45` and rank 45, but 38 of the
60 output rows have augmented rank 46.  A normalized two-term left-null
witness in row zero annihilates the complete ansatz and evaluates to one on
the target.  This obstructs a first-order Φ-only repair, not the coupled SDR.

The next smallest coupled continuation is rigid as well.  With an algebraic
variation of the incidence row and an arbitrary order-at-most-one variation
of $L_1$, homogeneous preservation of the complete first BGG square gives a
`60 x 60` coefficient map per output row with determinant $-2^{-36}$.  Hence
the only allowed pair is zero and it cannot act on the shifted-chain defect.
This supersedes coefficient-layer-only sensitivity tests, which did not impose
the full differential first square.

Adding every normalized algebraic $L_0$ direction still does not close the
chain.  The condition $p_0\delta L_0=0$ gives a 44-dimensional family.  The
unique induced incidence/$L_1$ corrections preserve the complete first BGG
square for every basis element, but their shifted-chain response map has rank
44 and augmented rank 45.  A normalized five-term algebraic left-null witness
detects the remaining obstruction.  Importantly, the earlier Phi-only witness
is reachable in this enlarged family and is explicitly superseded rather than
mistaken for a global no-go.

The remaining five-term quotient is formally sensitive to variations of the
first BGG/gauge row: 23 of 180 complete order-at-most-one basis directions
hit it after the unique induced incidence/$L_1$ correction and the
$\delta(Kp_0)$ term are included.  This is not an admissible repair.  The
authoritative action-derived transverse `first_BGG` variation in the jet
certificate has zero coefficients, so every sensitive formal direction would
change the target metric BV differential rather than strictify its parent
comparison.

The complete existing-row Phi continuation is now exhausted through the first
order capable of generating every target derivative order.  Allowing all 135
local Phi coefficients through differential order two gives a `525 x 135`
map of rank 130 and kernel dimension five.  Twenty-nine target rows are
consistent, while 31 have augmented rank 131; the normalized row-zero
two-term witness survives.  Thus neither a Phi-only continuation nor a change
of the fixed metric gauge generator is the missing repair.

That coupled gate is now closed by differentiating the universal ten-block
mapping-cone SDR rather than fitting a larger local row ansatz.  All twenty-one
split/original chain, retract, side-condition, cyclicity and conjugation
identities vanish through first order, with the newly derived
`g_dot=-r0 L0_dot p0` satisfying every complement and gauge-reconstruction
relation.  The action-derived metric gauge generator remains fixed.  The
atlas is fail-closed: the complete rank-310 algebraic SDR variation is now
`CERTIFIED`, while transverse metric and rank-310 causal homotopies remain
`OPEN`.

## Generator correction (2026-07-17; authoritative)

The exact co-rotating audit `BERGER_GENERATOR_CONJUGATION_AUDIT` supersedes
the geometric interpretation of every legacy artifact named `D_CARTAN` or
`LOCAL_D_ACTION` in the Berger branch.  With

\[
R(T_1,T_2)=(-T_2,T_1),\qquad K=D-\omega R,
\]

the frozen all-row rule \(e_0I_{54}\) represents \(K\), not raw \(D\).  In
co-rotating variables,

\[
U^{-1}DT=\partial_t\psi+\omega R\psi+\omega R(\rho,0),
\qquad U^{-1}KT=\partial_t\psi.
\]

Therefore the existing unary-through-ternary coefficients prove a
\(K\)-Cartan theorem.  Raw \(D\) has a nonzero zeroth Taylor component, and
an affine \(D\)-Cartan homotopy remains open.  The fixed-coupling charge
theorem is unchanged: it is still the raw-cylinder statement
\(Q_R>0\) but \(dQ_R|_{\mathcal Z}=0\), with linear presymplectic nullity of
\(D\) as its corollary.  Read every older `D-Cartan` sentence below under
this correction until the legacy artifact family is migrated.

## Shared relative-complex assignment

Use the canonical Einstein--Weyl spine in
[`universe-building-roadmap.md`](universe-building-roadmap.md).  The classical
team owns `RELATIVE_RESIDUAL_AND_OBSERVABLE_FUNCTOR_V1`; it does not own a
second construction of the linear Einstein inclusion.

The Berger disposition of Bridge 1 is now frozen, but its activation gate is
not satisfied: atlas row
`classical.berger.crosswalk.retained36_to_einstein_extra` remains
`NO_CERTIFIED_MAP`.  `BERGER_BRIDGE1_ADMISSIBLE_CARRIER_DISPOSITION_V1`
selects the unsplit retained 36-row cyclic causal complex as the authoritative
same-background carrier: the rank-36 projector and the contractible rank-46
graph anchor are obstructed, while none of the remaining relative-cofiber,
noncontractible mixed-bundle, all-mode `REDUCED-MODE`, or port alternatives
currently supplies a Berger branch crosswalk.  No row-name or cross-background
identification is allowed.  The active queue therefore advances to the
compact-product off-shell noncyclic three-form Einstein--Weyl relative
triangle, while a genuinely noncontractible Berger carrier remains open.
The Bach-flat rank-310-to-metric causal rail is closed; only the categorically
different bare-parent-to-metric crosswalk remains fail-closed.

Three same-background handoffs follow the transverse replay; the first now
has its fail-closed disposition and the second is active:

1. **Disposed, not activated.**  On Berger, retain the unsplit 36-row carrier
   and the exact normalized rank-36/rank-46 obstructions.  Reopen the local
   branch map only for a genuinely noncontractible mixed-bundle/cofiber
   construction; a row-name or contractible-graph split is forbidden.
2. **Complete.** For the compact product background,
   `EINSTEIN_WEYL_RELATIVE_LINEAR_TRIANGLE_V1` certifies the off-shell
   **noncyclic three-form** Einstein--Weyl relative triangle. The stronger
   `EINSTEIN_WEYL_GENERIC_CYCLIC_MAP_INERTIA_OBSTRUCTION_V1` certificate shows
   that the Einstein form has inertia `(2,0)` while the Weyl form on the
   complete `q`-primary image has inertia `(1,1)` in both generic parities.
   Therefore no real-structure-preserving, product-equivariant corrected map,
   chain homotopy or exact current improvement can make the standard pairings
   cyclic. The Einstein, pulled-back Weyl and relative forms are exported
   separately.
   An explicitly pairing-changed theorem is a different open route. This is
   Bridge 2 and must not import Berger or vacuum carriers without an explicit
   crosswalk.  `EINSTEIN_WEYL_COMPACT_PRODUCT_COVARIANT_CHAIN_MAP_V1` now
   reconstructs the generic, exceptional and homogeneous coefficient maps as
   one natural support-local minimal four-dimensional chain morphism, with no
   harmonic projector or inverse differential operator.  In the oriented
   fixed-Chern-class `N=2` sector, the source and target endpoint maps are the
   identity on the five connected product Killing reducibilities plus constant
   `U(1)`, the dual map is also the identity, and the disconnected
   `H^1(S1 x S2;Z)=Z` winding lattice maps identically.  This activates
   compact-product Bridge 1 only at the linear algebraic/cofiber level.  The
   nonzero-`k` exceptional solution cofiber and its
   action pairing are now exact: each parity has the standard Einstein image
   at `omega^2-k^2=4` and one nonradical extra class at
   `omega^2-k^2=4/3`, represented polynomially without a differential
   inverse.  `EINSTEIN_WEYL_COMPACT_PRODUCT_CHAIN_MAP_PBW_V1` now serializes
   this same support-local map as a strict row-ID-keyed 38-to-40-row PBW
   operator with coefficient jets through order four.  The frozen target-q1
   replay exposed the legacy covariant-equation versus BV-cotangent sign on
   the Maxwell Euler row.  Refitting the complete 41-parameter invariant
   family gives rank (26=operatorname{rank}[A|b]); its simplest normalized
   representative reverses exactly the four derivative-Maxwell coefficients
   and the associated identity term.  After that typed adapter, every one of
   the 40 coefficientwise chain defects vanishes, including a mutation test
   that restores the rejected sign.  Its lifecycle is now
   `EXACT_PBW_CHAIN_MAP_TARGET_Q1_REPLAYED`.
3. **Both interaction payloads delivered; direct relative solve disposed.**
   `EINSTEIN_MAXWELL_PRODUCT_LINFINITY_THROUGH_ARITY_THREE_V1` now exports the
   complete same-background 38-row minimal Einstein--Maxwell
   \(q_1,q_2,q_3\), action, row layout and cyclic pairing. Its executable
   coordinate-PBW tables include sparse rational coefficient jets through
   order two, so an independent consumer replays \(q_1^2\), the arity-two
   identity and the complete arity-three identity instead of trusting opaque
   hashes. The consumer independently verifies unary pairing adjointness and
   higher input Koszul symmetry; it explicitly does not claim a second
   derivation of the master-action cotangent lift.
   `WEYL_MAXWELL_PRODUCT_LINFINITY_THROUGH_ARITY_THREE_V1` now supplies the
   corresponding action-derived 40-row Weyl--Maxwell package with fourth-order
   coefficient jets.  Its independent consumer replays 1,835,845 ternary terms,
   1,437,607 ordered cyclic transposes and every unary, arity-two and
   arity-three defect row exactly over \(\mathbb Q\).  The V2 receiver imports
   both packages and is now
   `INPUTS_IMPORTED_RELATIVE_MORPHISM_SOLVE_READY`.  This is an input theorem,
   not itself a relative \(L_\infty\) morphism.  The strict \(\Delta_2\) has
   since been computed and its frozen full-domain \(f_2\) extension obstructed
   by the relative Taub class below.  The arity-three defect, induced
   cohomology map and separate even/odd deformation verdict are therefore not
   authorized on that direct carrier.  Neither payload may be inferred from
   the other theory by matching branch labels.  The nonlinear comparison must
   retain all three action forms rather than silently replacing them by a
   standard-pairing cyclic map.
   The receiver contract is now V2 and executable: opaque artifact hashes plus
   self-declared acceptance booleans are rejected.  Each theory must export a
   complete indexed BV row layout, the action and master terms, nondegenerate
   cyclic pairing, and rational sparse multilinear PBW tables for
   \(q_1,q_2,q_3\).  The receiver checks artifact scope and hashes, row and dual
   bounds, arities, term counts, derivative orders, duplicate support and
   pairing rank before import.  Both action-derived tables now pass that
   contract; their import still does not itself prove a relative
   \(L_\infty\) theorem.

### Queued nonlinear-team handoffs (2026-07-18)

The nonlinear team has requested three classical inputs.  They form one
dependency chain, not three interchangeable branch-labelled calculations:

1. **Berger same-background branch carrier — blocked, fail-closed.**  The
   desired Einstein-like/extra-Weyl/Maxwell map on the retained 36-row Berger
   carrier is still `NO_CERTIFIED_MAP`.  The certified support-local projector
   obstruction rules out the requested split on that carrier.  Reopen this
   handoff only through one of the admissible Bridge-1 alternatives: a relative
   cofiber, a larger noncontractible mixed-bundle carrier, an explicitly
   nonlocal all-mode `REDUCED-MODE` map, or a port to a background with a
   certified split.  Matching branch names across backgrounds is forbidden.
   A successful handoff must export exact inclusions/projections or cofiber
   maps, pairing, parity, real structure, Berger-generator weights and the
   Maxwell carrier.  Otherwise the normalized local-projector obstruction is
   the authoritative binary result.
2. **Compact-product direct relative morphism — obstructed at arity two.**
   The support-local off-shell noncyclic Einstein--Weyl linear triangle
   is certified, while a standard-pairing cyclic correction is obstructed by
   the fixed inertia mismatch.  The requested cyclic triangle therefore must
   either declare and justify a changed relative pairing or return the existing
   normalized obstruction; it may not silently relabel the noncyclic triangle
   as cyclic.  Independently, the frozen direct full-domain morphism has a
   nonzero relative constant-lapse Taub class at arity two, so no \(f_2\)
   valued in the declared smooth periodic fixed-bundle target domain exists.
   Arity three is not authorized on that carrier.  Reopen only after declaring
   a Taub-zero derived source sector, relative cofiber/mapping cone, larger
   charge carrier, modified unary/endpoint map, or different background.
3. **Same-background interaction payloads — complete.**  The complete
   Einstein--Maxwell and Weyl--Maxwell \((q_1,q_2,q_3)\) payloads are delivered,
   action-derived and independently replayed in the strict executable V2 PBW
   contract.  Their direct full-domain \(f_2\) gate is now obstructed; the
   nonlinear team should consume the obstruction and help choose a Taub-zero
   derived source or charge-carrying cofiber before any arity-three morphism
   defect or even/odd deformation verdict is attempted.

`EINSTEIN_WEYL_RELATIVE_ARITY_TWO_DEFECT_V1` evaluates the strict
\(\Delta_2=q_{2,W}(f_1,f_1)-f_1q_{2,E}\) operator.  It has 50,854 exact
rational coefficients in 15 target rows, maximum total derivative order four,
and an independent rowwise replay.  The Maxwell equation rows and U(1)
identity remain strict; the nonzero terms lie in the metric equations,
diffeomorphism identities and Weyl-trace identity.

[`EINSTEIN_WEYL_RELATIVE_F2_TAUB_OBSTRUCTION_V1`](../d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_F2_TAUB_OBSTRUCTION_V1.json)
now supplies the normalized obstruction; its human-readable derivation is in
[`einstein-weyl-relative-f2-taub-obstruction.md`](../d_quotient_classical/reports/einstein-weyl-relative-f2-taub-obstruction.md).
On the certified axial \(\ell=2,m=0,k=0\) plus mode, the complete
PBW defect evaluates locally to \(-3/2\) times the independently derived
Chevreton tensor.  Globally, the exact radiative-current restriction and the
moment-map--Taub identity give

\[
\left\langle\zeta_H,\frac12\Delta_2(u,u)\right\rangle
=\mu_W-\mu_E=-\frac{54}{5}(1+\sqrt3)\ne0.
\]

The target constant-lapse class annihilates every \(q_{1,W}\)-exact smooth
periodic fixed-bundle correction, including smooth secular corrections.
Therefore no \(f_2\), support-local or otherwise, extends the frozen unary map
on the full declared carrier.  This does not obstruct a Taub-zero restriction,
relative cofiber/mapping cone, larger charge fibre, modified unary/endpoint
map, or another background.

The active architecture gate is now `choose relative Taub-zero restriction or
charge-carrying cofiber -> rebuild the arity-two map -> only then authorize
arity three`.  The Berger
branch-carrier rail remains independent and fail-closed throughout.

### Post-obstruction carrier decision (2026-07-19)

`EINSTEIN_WEYL_RELATIVE_CHARGE_KOSZUL_RECEIVER_PREFLIGHT_V1` resolves the
architectural fork at `REDUCED-MODE` scope.  A plain “Taub-zero subcomplex” is
not legitimate: the relative moment map is homogeneous quadratic, so its
zero locus has the full radiative unary tangent and must be represented as a
derived zero locus.  Retain the certified support-local noncyclic unary
mapping cofiber and adjoin the relative stabilizer-charge fibre through

\[
\mathcal O(\operatorname{Sol}_{\rm std})\otimes
\Lambda(\kappa_H,\kappa_{P_x},\kappa_{J_1},\kappa_{J_2},\kappa_{J_3}),
\qquad d_K\kappa_X=\mu_{{\rm rel},X}.
\]

The five-generator Koszul differential squares to zero on all 32 exterior
monomials.  The sixth common endpoint is constant (U(1)) reducibility;
because (d\lambda=0), it has zero fundamental vector field and is not a
sixth Taub charge.  On the standard radiative branches,

\[
\mu_{{\rm rel},X}=(w_\pm-1)\mu_{{\rm EM},X},\qquad
w_\pm=1\pm\frac32\sqrt{2\ell(\ell+1)}.
\]

The quadratic function and its action-derived Taylor coefficient are kept
distinct:

\[
B_X(u,v)=\left\langle\zeta_X,\frac12\Delta_2(u,v)\right\rangle,
\qquad q^{\rm charge}_{2,X}(u,v)=2B_X(u,v).
\]

This selects the carrier without repairing the morphism.  The next exact
gate is the complete off-shell five-charge polarization of the PBW defect,
including any required exceptional/global rows, or a typed obstruction to
that lift.  Support-local BV/Koszul completion, (f_2), arity three, causal
Green data, observables and quantum transfer remain fail-closed.

`EINSTEIN_WEYL_RELATIVE_STANDARD_RADIATIVE_CHARGE_Q2_V1` now supplies the
first exact arity-two operation on this receiver.  For every standard
radiative Einstein branch, both parities, every (ell\ge2), and every compact
momentum,

\[
q^{\rm charge}_{2,X}(u,v)
=\langle\zeta_X,\Delta_2(u,v)\rangle,
\qquad X\in\{H,P_x,J_1,J_2,J_3\}.
\]

The export contains the axial and polar Einstein coefficient matrices, the
all-(ell) angular weight, the rotation action, selection rules, and the
relative branch coefficients

\[
r_\pm=\pm\frac32\sqrt{2\ell(\ell+1)}.
\]

On the certified plus witness,
(q^{\rm charge}_{2,H}(u,u)=-108(1+\sqrt3)/5), exactly twice the Taub
quadratic value.  This bracket records the obstruction; it is not an
(f_2) primitive.  The remaining extension is exceptional/global source
cohomology followed by a genuinely local current-density lift if the
programme still requires support-local BV data.

`EINSTEIN_WEYL_RELATIVE_COMPLETE_STANDARD_FIVE_CHARGE_Q2_V1` closes the
first of those two gaps.  The complete standard source cohomology is the
certified orthogonal sum of generic radiation, physical (ell=1) radiation,
the homogeneous generalized block, and the axial twist.  Their relative
pairing operators determine the five charge Hessians without a new fit:

\[
R_{\ell=1}^{\rm phys}-1=3I,
\qquad
q^{\rm charge}_{2,H}|_{\rm hom}=-3b_1b_2,
\qquad
q^{\rm charge}_{2,H}|_{\rm twist}=6B_1\!\cdot B_2,
\]

with

\[
q^{\rm charge}_{2,J}|_{\rm twist}
=-6(A_1\!\times B_2+A_2\!\times B_1).
\]

All cross-block coefficients vanish by the certified action-current
orthogonality, and the output cokernel is exactly
(H,P_x,J_1,J_2,J_3).  This remains a global `REDUCED-MODE` operation on
standard source cohomology.  Target-only extra Weyl modes are not inputs;
the off-shell local-current/BV lift, direct (f_2), arity three and causal
transport remain fail-closed.

`EINSTEIN_WEYL_RELATIVE_FINITE_CHARGE_SUPPORT_LOCAL_LIFT_OBSTRUCTION_V1`
now fixes the category boundary.  No nonzero finite-order support-local
operation can land directly in the constant five-dimensional charge fibre:
compact inputs give compact output, whereas a nonzero constant section on
the connected noncompact cylinder has full support.  Compactly supported jet
realization then forces such an operator to vanish, contradicting the exact
nonzero (H) witness.

The next local carrier is therefore not another finite charge row.  It is the
horizontal equation cone

\[
\Omega_H^3(M;\mathfrak g_{\rm stab}^*)
\xrightarrow{d_H}
\Omega_H^4(M;\mathfrak g_{\rm stab}^*),
\]

with cyclic dual rows, followed by Cauchy-slice integration only after
globalization.  `EINSTEIN_WEYL_RELATIVE_POLARIZED_NOETHER_CURRENT_SEED_V1`
now exports the finite-order support-local three-current at coefficient level:

\[
j_X(u,v)=\frac12\bigl(
\omega_{\rm rel}(u,{\cal L}_Xv)+
\omega_{\rm rel}(v,{\cal L}_Xu)\bigr),
\qquad
\omega_{\rm rel}=\omega_{\rm WM}-\omega_{\rm EM}.
\]

The metric lift is the tensor Lie derivative and the Maxwell lift is the
fixed-bundle Cartan action \(\iota_Xda={\cal L}_Xa-d(\iota_Xa)\).  All four
vector-density components are available, the polarization is symmetric, and
an exact spatial fixture gives \(j_D^x=3x/8\), so the exported local carrier is
nonzero.  The full off-shell divergence replay, cyclic dual rows and equality
of the integrated current with every block of the complete five-charge
operation remain open; the seed does not repair \(f_2\) or authorize arity
three.

The underlying action-derived Lee--Wald engine is now component-complete.
`weyl_maxwell_current_component` and
`einstein_maxwell_current_component` evaluate every vector-density component,
while the established time-component functions remain exact wrappers.  This
closes the API prerequisite for the relative current cone without promoting
its still-unchecked off-shell divergence or cyclic BV rows.  The active local
gate was `CERTIFY_OFF_SHELL_DIVERGENCE_CONE_AND_CYCLIC_DUAL_ROWS`.

`EINSTEIN_WEYL_RELATIVE_HESSIAN_GREEN_CURRENT_CONE_V1` now closes the
equation-level half of that gate without repeatedly rebuilding curved
coordinates.  It imports the complete action-derived fourteen-field source
and target Hessians and applies the ordered multivariate Lagrange identity to
every coefficient-jet monomial.  The antisymmetrized relative Green current
has component term counts

\[
(922,922,928,932),
\]

maximum total derivative order three, and the coefficientwise identity

\[
d_H B_E(u,v)=\langle u,E_{\rm rel}v\rangle
-\langle E_{\rm rel}^{\sharp}u,v\rangle
\]

has zero defect on the complete PBW table after the required
\(\sin\theta\) densitization.  The same coefficient-jet replay verifies
formal self-adjointness directly.

`EINSTEIN_WEYL_RELATIVE_FIVE_STABILIZER_CURRENT_CONE_V1` now precomposes the
entire connected stabilizer basis

\[
H=\partial_t,\quad P_x=\partial_x,\quad J_1,J_2,J_3\in\mathfrak{so}(3)
\]

using the tensor Lie derivative and the fixed-bundle Maxwell Cartan lift.
All five vectors preserve the product metric and magnetic two-form.  Every
polarized current is symmetric, and every complete coefficient-jet divergence
equals its action-Euler source with zero defect.

`EINSTEIN_WEYL_RELATIVE_GREEN_LEE_WALD_IMPROVEMENT_V1` now closes the local
representative comparison.  A sparse first-field-jet derivation reconstructs
the action Lee--Wald current and independently reconstructs the symbolic
coordinate-density Hessian whose ordered Green current agrees exactly with
the frozen PBW table.  Their nonzero difference is horizontally closed, and
an exact rational solve in the seven-function Laurent--trigonometric product
basis exports

\[
\omega_{\rm LW}^{\mu}-\omega_G^{\mu}
=\partial_\nu U^{\mu\nu},
\qquad U^{\mu\nu}=-U^{\nu\mu},
\]

with 2,478 finite-order PBW terms and zero symbolic replay defect.  An
independent coordinate-curvature-momentum fixture also matches the sparse
Lee--Wald coefficient.

`EINSTEIN_WEYL_RELATIVE_CYCLIC_FIVE_CURRENT_CONE_V1` now closes the cyclic
row half of the successor gate.  The minimal local receiver has degree ranks

\[
(5,20,20,5),
\]

consisting of five dual-divergence rows, twenty dual-current rows, twenty
current rows and five divergence rows.  Horizontal divergence and negative
gradient are exact formal-adjoint unary blocks under the canonical odd
pairing.  The five symmetric field--field current operations are retained
coefficientwise; their two mixed operations are the forced finite-order
formal adjoints, so the lowered cubic tensors are cyclic without a fitted
pairing or sign.

`EINSTEIN_WEYL_RELATIVE_GLOBAL_FIVE_CHARGE_REPLAY_V1` closes the global
receiver without overpromoting the Laurent coordinate primitive.  The
Lee--Wald current and a covariantly integrated Green current are global; their
difference is a closed vertical-degree-two, horizontal-degree-three form.
Exactness of the positive-contact row of the global variational bicomplex for
the affine metric/connection field bundle supplies a smooth global
superpotential.  Its integral vanishes on the closed slice by Stokes.  The
moment-map identity then replays the generic radiative, physical \(\ell=1\),
homogeneous and twist blocks into exactly

\[
(H,P_x,J_1,J_2,J_3),
\]

with every certified cross-block term zero and no constant-\(U(1)\) output.
The particular 2,478-term Laurent representative remains only a local exact
witness; its polar-chart smoothness is not asserted.  The direct support-local
map into constant charge rows remains obstructed, and no \(f_2\) repair or
arity-three promotion follows.

`EINSTEIN_WEYL_RELATIVE_CURRENT_COFIBER_ASSEMBLY_V1` now performs the typed
post-replay assembly.  The 78-row support-local unary mapping cofiber and the
50-row cyclic five-current cone form a 128-row block-diagonal complex.  The
local current operation, its exact divergence, closed-slice integral and the
five-generator Koszul differential form the complete homotopy-moment-map
receiver for the stabilizer-charge projection.  This is not the missing
relative \(f_2\): if \(f'_2=(a,b)\) takes values in the enlarged direct sum,
projection onto the original Weyl target gives the unchanged equation
\([q_{1,W},a]=-\Delta_2\), where the constant-lapse Taub witness remains
nonzero.  The current cone records and globalizes the obstruction but cannot
cancel it without a nonzero typed cross-incidence or a genuinely derived
source pullback.  Direct \(f_2\) and arity three remain fail-closed.  The
classical lane therefore advances to the linear relative observable pullback;
any nonlinear repair is a separate architecture gate.

The transverse replay now has an associative coefficient-jet PBW algebra,
independently matched to direct symbolic differential-operator composition.
The finite covariant HPL series and unique normalized degree-one correction
derive all four required `L0_corrected` jets and fourteen `L1_corrected` jets,
recover the old point values, and close `d_aut L0=L1 K` on every requested
ordered jet.  With those jets, the parent Yang--Mills identity, both
parenthesizations of `M_parent/L1_corrected/Kp0`, and the shifted-chain
identity also close exactly.  The authoritative `Phi` differs from the old
point-only intermediate, so the old 207-coefficient shifted defect is rejected
as a backend artifact.  The Hom-adjoint and compressed-Schur gate is now exact
as well: the adjoint is taken on the primitive covariant HPL factors before
normal ordering, and the calculation exercises the nonzero curvature jet tower
through order five.  No interpolation is used.  The upper relative-saddle,
action endpoint and complete ten-block rank-310 first-variation SDR gates now
close exactly.  The global four-row metric Green homotopy also has an exact
formal first variation.  The global all-row gate is now closed without
misusing the one-point coefficient table: the cyclic basic perturbation lemma
applied to the natural global `Qdot_310` gives
`Idot=-H Qdot I`, `pdot=-p Qdot H`, `Hdot=-H Qdot H`, and
`qdot=p Qdot I`.  These formulas reproduce the certified pointwise geometric
representative exactly and transfer the same-sided Duhamel homotopy to all 310
rows through formal first order.  The exact nonzero-`epsilon` global family is
not claimed.  The active queue may now advance to the three same-background
relative/interaction handoffs below.

For every declared background, charge fibre, boundary condition, and quotient:

1. import the Einstein team's map/cofiber certificate by content hash;
2. test whether the full residual action, especially \(D\), is equivariant on
   the map and descends to the cofiber;
3. determine whether taking the Taub-zero or charge-zero derived sector
   commutes with forming the relative cofiber;
4. construct the contravariant observable map
   \(\iota^*: \operatorname{Obs}(\mathcal E_{\rm Weyl})\to
   \operatorname{Obs}(\mathcal E_{\rm Einstein})\);
5. identify relational or curvature observables that annihilate the Einstein
   image and therefore detect the relative sector; and
6. place the Berger clock/redshift observable in this diagram, including any
   failure caused by global winding, boundary dressing, or charge variation.

Return exact defects rather than forcing equivariance.  A solution-level
comparison is not an observable map, and `D_GAUGE` in one derived sector is
not evidence that the cofiber construction commutes with that quotient.

`RELATIVE_RESIDUAL_AND_OBSERVABLE_FUNCTOR_V1` now closes the linear version
of this handoff.  Dualizing the complete finite-order all-row inclusion gives
the contravariant support-local chain map

\[
\iota^*: \operatorname{Obs}_{\rm loc}(\mathcal C_{WM})
\longrightarrow \operatorname{Obs}_{\rm loc}(\mathcal C_{EM}),
\qquad O_f\longmapsto O_{\iota^\sharp f}.
\]

It is equivariant under the certified product residual group, including
\(H=\partial_t\), and the global endpoint cofiber is zero.  On solution
cohomology, inverse action-current Gram matrices give exact coefficient
detectors for the generic axial, generic polar and both exceptional
\(\ell=1\) extra cofibers; orthogonality makes their pullback zero and
nondegeneracy makes them separating.  These detectors are `REDUCED-MODE`
stationary coefficients, not support-local Peierls or relational observables.
They exhibit a nonzero pre-residual kernel, not a quasi-isomorphism.  Full
\(SO(4,2)\), final residual descent, the nonlinear relative morphism, causal
Green transport, and a Berger cross-background observable map remain false
or `NO_CERTIFIED_MAP`.  The block-diagonal charge derived sector does not
commute with the full arity-two morphism because the direct Taub obstruction
survives.  The classical lane now returns to the independent curved
parent-to-metric C-G2 bridge.

Use the shared row format:

| Setting | Map \(\iota\) | Cofiber | Relative pairing | \(\mathfrak O_2\) | Residual action | Observable map | Quantum lift |
|---|---|---|---|---|---|---|---|
| Explicit background/sector/boundaries | imported status + hash | imported status | imported or checked | imported status | computed verdict | computed verdict | `NOT_APPLICABLE` |

## Live Berger nonlinear handoff (2026-07-17)

### Coupled Maxwell cyclicity repair gate

The independent retained-​36 replay has replaced the earlier broad cyclicity
failure by a sharply localized repair problem.  All 953 exact defects contain
two Maxwell legs: 800 lie in the physical `hAA` orbit, 138 in its
diffeomorphism-ghost/potential-antifield completion, and 15 in the Maxwell
ghost-density orbit.  Multiplying every Maxwell-output component of the
transferred (q_2) by two preserves ([q_1,q_2]=0) and removes the first 938
defects.  Pairing-sign changes do not help, while the tested scaling that also
removes the last 15 creates 108 chain defects and is rejected.

That completion is now constructed.  It is the common factor-two
Maxwell-output normalization followed by the \(q_1\)-coboundary of the local
BV-canonical cotangent lift of

\[
c_M\longmapsto c_M-2\,\iota_cA.
\]

The shear has 24 generator coefficients and a 160-coefficient full
coboundary (120 after retention).  The repaired tensors contain 1,890 full
and 1,474 retained PBW coefficients, with both \([q_1,q_2]=0\) and cyclicity
replaying exactly in the independent exact backend. The quantum acceptance
rail now pins the committed hashes and returns
`ACCEPTED_COUPLED_Q2_CYCLIC_REPAIR`, so mixed \(q_3\) is unblocked; the
nonlinear observer vertex remains a separate construction.

The mixed \(q_3\) gate is now complete in the nonlinear typed presentation.
The arity-two factor two belongs to the Maxwell Darboux block, not to a bare
output rescaling: with

\[
S=\operatorname{diag}(I_{54},2I_{10}),\qquad
\Omega_{\rm typed}=\Omega_{\rm legacy}S,\qquad
q_{2,{\rm typed}}=S^{-1}q_{2,{\rm legacy}},
\]

the lowered cubic tensor is unchanged, while coderivation composition is
well typed.  The action-derived and finitely BV-canonically transformed
mixed operation has 59,598 exact PBW coefficients on 21 nonzero output rows.
The certificate `BERGER_SUPPORT_LOCAL_COUPLED_MAXWELL_Q3` proves raw quartic
action cyclicity with the Maxwell weight two, graded symmetry, frozen
\(K_{\rm Berger}\)-equivariance, and the mixed part of

\[
q_1q_3+q_2(q_2,\cdot)+\text{graded unshuffles}=0
\]

on all 64 rows.  It is a full four-dimensional `LOCAL-ALGEBRAIC` export, not
a reduced-mode fit.

The retained transfer is now exact on an explicit typed carrier.
BERGER_PORTABLE_COUPLED_64_TYPED_PAIRING_36_SDR exports both odd pairings,
both unary differentials, the typing scales, and the complete cyclic
support-local \(64\to36\) contraction.  In this carrier,
BERGER_RETAINED_MIXED_ELL3_TRANSFER proves

\[
\ell_{3,\mathrm{mixed}}
=\pi q_{3,\mathrm{mixed}}(\iota,\iota,\iota)
\]

coefficientwise.  The retained mixed contact contains 25,950 exact PBW
coefficients in 18 nonzero rows, while each of the three possible relative
homotopy-exchange sectors vanishes exactly.  The retained mixed arity-three
exchange lemma is concrete: the only nonzero raw exchange has 342 terms, all
in full contractible output row 38, which the retained projection
annihilates; the other two exchange compositions vanish before projection.
The retained mixed arity-three
identity then closes on all 36 rows, with 1,474 retained mixed
\(\ell_2\)-coefficients.  A separate verifier reconstructs the contact
pullback, evaluates every graded exchange unshuffle, and replays all 36
identity rows.  Independent quantum-side acceptance, QME restoration, and
every quantum claim remain separate fail-closed gates.

The coupled Cartan gate is now also closed through arity three.
BERGER_COUPLED_K_CARTAN_THROUGH_ARITY_THREE combines the certified 64-row
gravity--clock--Maxwell causal homotopy, the typed cyclic \(64\to36\) SDR,
the action-derived coupled \(q_2,q_3\), and the explicit retained mixed
\(\ell_2,\ell_3\).  For \(K_{\rm Berger}=D-\omega R\), the arity-two source
closes by \([K,q_2]=0\); at arity three the two Jacobi channels cancel with
normalized coefficients \(-\tfrac12+\tfrac12=0\), while \([K,q_3]=0\).
Cyclic Reynolds completion therefore constructs the coupled primitives
through arity three with two-sided causal-hull support.  Finite cyclic HPL
transfers the theorem to the retained 36-row carrier, where the explicit
Maxwell-mixed operation agrees with the 1,474-term \(\ell_2\) and
25,950-term contact \(\ell_3\) exports.  Raw affine \(D\), arity four,
Hadamard products, QME restoration, and every quantum claim remain false.

The separate extended apparatus unary audit is now exact. On the detector
chart the three declared standard-sign rods have
\(T^R_{\hat a\hat b}=\operatorname{diag}(3/2,-1/2,-1/2,-1/2)\). Because the
probe preflight excluded this stress, the unchanged Berger background is off
shell at nonzero rod coupling and cannot support an uncurved nilpotent
apparatus \(q_1\). `BERGER_EXTENDED_ROD_MEMORY_MAXWELL_UNARY_GATE` also proves
the universal finite triangular retarded inverse for the memory--Maxwell
Hessian. Completion now requires a backreacted rod background and explicit
content-addressed detector profile operators; it is not blocked by the
abstract memory Green algebra.  The superseding implementation target is the
observer team's independent 84-row unary/pairing/Green construction.  The
classical team must not reconstruct or silently replace that 84-row export.

The authoritative 54-row support-local classical Taylor data are now complete
through arity three at the frozen rational Berger fixture.  The certificate
`BERGER_SUPPORT_LOCAL_Q3` contains 5,812,130 exact
\(\mathbb Q(\sqrt{10})\)-valued PBW terms on twelve nonzero rows and proves,
coefficientwise,

\[
q_1q_3+q_2(q_2,\cdot)+\text{graded unshuffles}=0,
\]

together with graded symmetry, quartic action cyclicity, and the local
\(D\)-derivation identity with \(L_D^{(3)}=0\).  The portable export is a
strict-JSON manifest plus deterministic gzip-compressed strict-JSON row
chunks; it is a full four-dimensional `LOCAL-ALGEBRAIC` result, not a
reduced-mode fit.

That gate is now passed by `BERGER_ARITY_THREE_D_CARTAN_FULL_4D`.  On the
complete arbitrary-input 54-row four-dimensional Berger BV complex it
constructs a cyclic arity-three Cartan primitive and proves

\[
[q_1,\iota_D^{(3)}]
=-[q_3,\iota_D^{(1)}]-[q_2,\iota_D^{(2)}]+L_D^{(3)},
\qquad L_D^{(3)}=0.
\]

The primitive has two-sided causal-hull support; it is not claimed to be
separately retarded or advanced.  Under the authoritative generator audit this
closes the classical \(K_{\rm Berger}=D-\omega R\) Cartan recurrence through
arity three, not raw affine \(D\) and not to all orders.  It does not
promote a quantum, QME, anomaly-cancellation, or Hadamard claim.  Before a
paper theorem is frozen, the current certificate, manifest, schemas, receipt,
and independent verifier must be committed together and replayed from the
recorded hashes.

## Residual branch-projector handoff (2026-07-17; authoritative)

The requested
`BERGER_RETAINED_36_RESIDUAL_BRANCH_BASIS_V2` has been decided by the
obstruction branch of its binary handoff.  The retained metric endpoint has
the exact form

\[
A_{10}=\Box_2^2+V_2,\qquad \operatorname{ord}V_2\leq2,
\]

and all 92 nonzero entries of \(\sigma_2(V_2)\) fail divisibility by the
canonical scalar-wave polynomial.  At the frozen Berger fixture the first
normalized witness is

\[
\frac{71p_1^2+71p_2^2+9p_3^2}{80},
\]

with \((80/71)\) times its \(p_1^2\) coefficient equal to one.  Therefore the
canonical rough-tensor-wave equation module is not an exact same-bundle factor
of the Berger endpoint and cannot be the image of the requested support-local,
\(q_1\)-intertwining complementary Einstein-like projector on the retained
36-row carrier.  The exact certificate is
`BERGER_RETAINED_36_RESIDUAL_BRANCH_LOCAL_PROJECTOR_OBSTRUCTION_V1`.

The natural rank-46 STF2 graph carrier has now also been decided negatively at
the first nonzero filtered page.  The exact physical helicity module is the
rank-two projective image of the TT idempotent.  At
\(\zeta=(1,1,0,0)\), after allowing every principal gauge change, Hessian
boundary and physical-equation representative, the permitted correction
space has rank four.  Adjoining the \(V_2\) image of
\(h_{22}-h_{33}\) raises it to five.  The normalized left-null witness

\[
\ell=(-5/31,10/31,0,0,25/31,0,\ldots,0)
\]

annihilates all permitted corrections and evaluates to \((1,0)\) on the two
physical columns.  Hence the physical projective module does not descend to a
closed filtered subcomplex, and the contractible rank-46 graph cannot supply
the requested support-local branch projector.  This exact verdict is
`BERGER_RETAINED_46_STF2_SUBPRINCIPAL_BRANCH_ANCHOR_OR_OBSTRUCTION_V1`.

This remains scoped: it does not rule out a mixed-bundle curvature mapping
cylinder, a noncontractible filtered carrier with a larger leading
cohomology module, or an explicitly nonlocal `REDUCED-MODE` splitting.  At
the standard fibre any repair needs at least one additional equation
cohomology direction and its cyclic-dual field direction; the global
covariant bundle rank is not certified by this pointwise lower bound.

The category boundary is fixed.  Einstein-like and extra-Weyl are dynamical
gravity branches; the odd topological direction remains in the separate
deformation/vertex basis with its Euler--Lagrange and transgression witnesses.
The quantum team must absorb the obstruction and must not compute a branch
mixing table from a reduced-mode substitute.  Paper XI remains valid on the
unsplit retained cyclic causal complex; its theorem does not depend on this
projector verdict.

## Paper IX writing commission

**Primary owner:** classical team.  **Scientific co-lead:** nonlinear team.
The classical team owns the manuscript and its single editorial source; the
nonlinear team supplies and signs off the interaction/Cartan sections and the
final interpretation.

### Working title and question

Use the conservative working title

> **A backreacting phase clock with fixed momentum in pure-Weyl gravity:
> fixed-coupling rigidity and causal BV Cartan analysis of the helical
> stabilizer**

and organize the paper around one question:

\[
\boxed{\text{Can a healthy clock have nonzero but fixed momentum, and what
Cartan theorem holds for its background stabilizer?}}
\]

The paper should answer: **raw \(D\) is linearly presymplectically null on the
declared fixed-coupling sector, while \(K=D-\omega R\) has the certified
Cartan contraction through arity three**.  It must not turn those scoped
theorems into a claim about
generic spacetimes or the complete nonlinear or quantum theory.

### The theorem spine

Build the readable argument around five linked results:

1. the exact non-conformally-flat Berger family with two standard-sign
   rotating conformal scalars, positive potential, timelike clock phase, and
   the declared energy inequalities;
2. the covariant phase-space identity
   \(\Omega_{\rm total}(\delta,\mathcal L_D)=\omega\delta Q_R\), followed by
   the fixed-coupling lapse constraint and compact-averaging proof that
   \(\delta Q_R=0\) for every smooth linearized tangent;
3. the complete cyclic 54-row gauge-fixed BV complex and its causal Green
   homotopy, with the distinction between support-local operations and
   two-sided causal cyclic completion stated explicitly;
4. the action-derived support-local \(q_2\) and \(q_3\), including the exact
   \(L_\infty\) identities and cubic/quartic cyclicity;
5. the cyclic causal Cartan contraction through arity three, showing that the
   interacting classical quotient has no obstruction through this order.

Relational redshift may appear as a clearly labelled certified fixture or
application.  Do not make localized emitter/receiver propagation,
backreaction, or a general observational redshift theorem part of the main
claim unless those additional gates close before theorem freeze.

### Required paper structure

Write a short main paper with this order:

1. physical question and exact claim boundary;
2. Berger universe, matter clock, and admissible parameter interval;
3. charge theorem: nonzero clock momentum versus vanishing tangent charge;
4. gauge explanation and relational evolution;
5. 54-row causal BV construction;
6. interaction tensors \(q_2,q_3\) and their exact identities;
7. Cartan recurrence through arity three;
8. what survives, what fails, and what remains open;
9. reproducibility and certificate map.

Put row tables, PBW payload details, hashes, resource measurements, exhaustive
sign tables, and replay commands in a computational supplement.  The main
paper should explain why each calculation matters rather than narrating the
software pipeline.

### Division of work

- **Classical team:** sections 1--5 and 8--9; charge conventions, clock health,
  phase-space scope, relational interpretation, evidence table, and final TeX
  integration.
- **Nonlinear team:** sections 6--7; independently import the frozen classical
  hashes, explain the arity-two and arity-three recurrences, and verify every
  interaction claim in the abstract and conclusion.
- **Quantum team:** one claim-boundary review only.  Confirm that no classical
  result is described as a QME, Hadamard, anomaly, or quantum-unitarity
  theorem.
- **Einstein team:** optional internal referee.  Check that the paper does not
  identify the Berger quotient with an asymptotically flat Einstein radiative
  phase space or claim black-hole/scattering consequences.

### Freeze and stopping rule

Writing starts now.  Promote the paper to `THEOREM_FROZEN` only when:

- all theorem certificates and their independent verifiers pass from a clean
  committed tree;
- the paper-to-certificate claim table has no missing or broadened dependency;
- the nonlinear team signs off the arity-three Cartan interpretation;
- every limitation below appears in the abstract, theorem statement, and
  conclusion where relevant.

The paper stops at: one compact Berger family, fixed couplings, classical
theory, the declared smooth phase space, and interaction order three.  It does
not wait for arity four, a Hadamard state, the QME, anomaly coefficients,
particles, asymptotic scattering, black holes, or a GUT.  Those are later
papers and must not be imported as motivation-shaped conclusions.

## Binary charge test

For every setting, specify the field space, equations, allowed variations,
boundary conditions, corner conditions, presymplectic potential, and finite
counterterm convention.  Then compute

\[
\delta H_D=\Omega_\Sigma(\delta\phi,\mathcal L_D\phi)
\]

including every surface and corner contribution.  Check integrability of
\(\delta H_D\), flux dependence, conservation, and the reference normalization
of \(H_D\).  Classify the result as exactly one of:

1. **proper gauge:** the \(D\)-vector is a presymplectic degeneracy and the
   normalized charge vanishes on the reduced phase space;
2. **physical symmetry:** \(D\) has a nonzero integrable charge, nonzero flux,
   or a nontrivial boundary Hamiltonian;
3. **sector-dependent:** it is gauge only after explicit boundary, zero-charge,
   or superselection restrictions;
4. **not Hamiltonian:** the charge variation is nonintegrable or the proposed
   phase space is not preserved, which itself obstructs the quotient.

Do not call a field-independent constant “zero” without declaring the reference
choice.  Do not call a transformation gauge if it changes allowed boundary
data, carries flux, or is generated by a nonzero boundary charge.

## Work package C-D1: compute the \(D\) charge

Compute \(H_D\) in this order:

1. compact vacuum cylinder;
2. cylinder plus a conformally coupled scalar;
3. cylinder plus Yang--Mills;
4. weakly perturbed conformally flat backgrounds;
5. Lorentzian dS and AdS with declared boundary conditions;
6. asymptotically flat spacetimes at \(\mathscr I^-\) and \(\mathscr I^+\).

For matter systems, separate gravitational, matter, improvement, ghost, and
boundary pieces before summing them.  The strongest counterexample is a smooth,
admissible solution and tangent variation for which the intended \(D\) action
preserves the phase space but \(\delta H_D\neq0\).  If no such example exists,
provide the identity forcing each candidate contribution to vanish.

For noncompact or bounded settings, first identify which asymptotic generator,
if any, is the image of cylinder \(D\).  Do not assume that the conformal
compactification map turns a cylinder gauge generator into proper gauge at the
physical boundary.

## Work package C-D2: recompute the residual complexes

Compute cohomology and the induced pairing for at least four choices:

\[
\mathfrak{so}(4,2),\qquad
D\text{ retained as a global symmetry},\qquad
\mathfrak g_{H=0},\qquad
\text{local gauge transformations only}.
\]

The requested “\(\mathfrak{so}(4,2)\setminus\langle D\rangle\)” comparison
must be implemented as a mathematically defined relative/equivariant complex
or an explicitly closed gauge subalgebra.  Do not silently treat set subtraction
as a Lie algebra.  Likewise, prove whether the zero-charge transformations
\(\mathfrak g_{H=0}\) close under the bracket on the chosen sector; allow for a
field-dependent algebroid if that is what the charge algebra gives.

For every quotient report:

- the cochain complex and differential;
- exact cohomology dimensions by degree, \(D\)-weight, and particle number;
- whether helicity-\(\pm2\) one-particle classes return;
- the norms and full Gram matrices of surviving classes;
- whether the conventional ghost branch and Einstein graviton appear
  separately;
- the fate, mixing, and interpretation of \([W_+^2]\) and \([W_-^2]\);
- cocycle representatives and exact trivialization witnesses.

Use exact rational or algebraic arithmetic for ranks, canonical forms,
cocycles, and pairings.  Generate the ansatz; do not hard-code the expected
basis.

## Work package C-D3: add a relational clock

### Current one-scalar resolution

The first candidate is now certified as obstructed on the exact vacuum
cylinder. For one real conformally coupled scalar the Weyl-invariant
homogeneous variable \(\chi=aT\) obeys \(\ddot\chi+\chi=0\), supplies exact
local clock charts, and has positive improved charge
\(H_D^T=(\dot\chi^2+\chi^2)/2\). Its improved stress is nonzero on every clock
orbit, whereas the exact cylinder Bach tensor vanishes. Hence no nonzero
homogeneous scalar clock is a coupled background there. At the only
compatible background \(\bar T=0\), the linearized scalar gauge incidence
vanishes and cannot fix \(D\).

The replacement gate is `BACKREACTED_OR_COMPOSITE_CLOCK_MODEL`: use a
genuinely backreacted scalar geometry, a Weyl-invariant composite/two-field
clock, or separately declared reference matter. Do not reuse the obstructed
background in downstream work.

### Neutral two-field replacement

This gate is now passed on the exact homogeneous sector by
`NEUTRAL_CONFORMAL_CLOCK_PAIR`. Two conformal scalars with internal signature
`(+,-)` have conserved
\(H_D=(I_1-I_2)\) and Wronskian \(W\). On \(H_D=0\), their improved stresses
cancel componentwise; on \(W\ne0\), their projective angle is an everywhere
monotone compact-\(D\) clock and the raw Diff \(\times\) Weyl incidence has
full rank. The scoped verdict is `D_GAUGE` on
`compact_neutral_clock_pair_homogeneous`.

The replacement uses opposite-sign reference matter. Its local health audit
is now complete and obstructs an unrestricted promotion: after Weyl reduction
the ratio mode retains a derivative term with sign-changing coefficient, and
every neutral winding orbit crosses four kinetic degeneracies. The homogeneous
clock theorem remains valid, but `FULL_NEUTRAL_CLOCK_PAIR_BV_COMPLETION` fails
as a globally regular positive clock.

The complete standard positive-sign one-field stealth alternative is now
classified, including inhomogeneous configurations. Every nowhere-zero clock
candidate has reciprocal
\(T^{-1}=A\cos t+B\sin t+C\cdot n\); every nontrivial denominator has a zero,
and every time-dependent gradient fails the everywhere-timelike test. The next
clock gate is `POSITIVE_ENERGY_NONCONFORMALLY_FLAT_BACH_SOURCED_CLOCK`.
That gate is now passed by an exact Berger-cylinder family. Two standard-sign
conformal scalars of constant modulus rotate with phase \(\theta=\omega t\),
source the nonzero Bach tensor, have a positive quartic potential, satisfy the
dominant energy inequalities, and give full raw Diff \(\times\) Weyl incidence
on

\[
\frac{5-\sqrt{21}}2<q=\frac{c^2}{a^2}<\frac14.
\]

This proves a credible healthy clock *background*.  Its fixed-coupling
linearized charge gate is now closed.  The minimal temporal/Weyl clock sector
also contracts support-locally and cyclically on all eight field/ghost and
minimal-dual rows, leaving a 26-row dressed-metric/spatial-diffeomorphism
complex. The complete retained operator is now certified coefficientwise.
The nonzero-Weyl Berger Bach variation has been expanded at every differential
order in the invariant-frame PBW algebra; together with the matter Hessian it
obeys the exact spatial Noether identities, formal self-adjointness, cyclicity,
and \(q_1^2=0\) on all 26 rows. The twenty nonminimal rows, the selected
gauge-fermion shear, the complete gauge-fixed 54-row unary differential, and
its cyclic 54-to-26 contraction are also exact. The helical \(D\)-action is
the invariant time derivative on every row and commutes coefficientwise with
\(q_1\) and every contraction map. Causal Green homotopies, the full
four-dimensional \(q_2\), and nonlinear stability remain separate.
Generalized non-Noetherian or higher-derivative scalar actions remain
separate theories with independent health and BV gates.

The first reduced charge seed is also exact. If
\(R(T_1,T_2)=(-T_2,T_1)\), then

\[
\mathcal L_D(T_1,T_2)=\omega R(T_1,T_2),
\qquad
Q_R=16\pi^2\alpha_Bq\sqrt{1-4q}>0.
\]

Thus the phase has genuine conserved matter momentum.  The pure-Weyl and
improved scalar currents combine on the background to give the exact decision
identity below; \(Q_R\ne0\) alone is not the verdict.

The action and tangent conventions are now frozen. In the producer curvature
convention,

\[
\delta\int\sqrt{-g}\,C^2
=4\int\sqrt{-g}\,B_{\mu\nu}\delta g^{\mu\nu},
\]

so the coefficient producing \(\alpha_BB=T\) is \(\alpha_B/8\). At fixed
\(\alpha_B\lambda\), the stationary relation forces \(\delta q=0\); the open
\(q\) interval labels different coupling products, not perturbations within
one theory. The helical current calculation gives the exact decision identity

\[
\Omega_{\rm total}(\delta,\mathcal L_D)=\omega\,\delta Q_R.
\]

The tangent gate is now decided by varying the exact lapse before fixing it.
In conformal gauge for the common spatial scale, the full time-dependent
biaxial reduced action gives

\[
\boxed{
\delta E_N=-\frac{\alpha_Bq^{3/2}}2\frac{\delta Q_R}{Q_R}.
}
\]

The coefficient is nonzero on the complete positive branch, so every
homogeneous fixed-coupling solution tangent has \(\delta Q_R=0\).  This also
settles the inhomogeneous question without a harmonic cutoff: compact
\(SU(2)_L\times U(1)_R\) averaging preserves the linearized equations and the
invariant functional \(\delta Q_R\). Any charged tangent would therefore
average to a forbidden charged homogeneous tangent. Consequently

\[
\Omega_{\rm total}(\delta,\mathcal L_D)=0
\]

for every smooth fixed-coupling linearized tangent, and the scoped verdict is
`D_GAUGE`.  The nonzero background momentum is fixed by the compact lapse
constraint; its pullback differential vanishes.
`BERGER_RETAINED_MINIMAL_OPERATOR` is now complete. The retained companion
`T=alpha_B Box_1 F_spatial` makes the ghost and identity endpoints Green
hyperbolic as compositions of normally hyperbolic vector operators. Its
rank-eight metric symbol is a presentation effect, not a principal no-go:
support-locally reattaching the eight certified clock rows restores temporal
diffeomorphism and Weyl incidence, and the normalized full companion obeys

\[
JH_4+K_1T=(\zeta^2)^2I_{10},\qquad
TK_1=(\zeta^2)^2I_5.
\]

The first curved \(W_{34}\) candidate nevertheless mixed coordinate
conventions: it retained the dressed unary differential and companion but
used an untransported identity middle map. The exact compatibility audit
records the resulting rank-eight dressed subblock and rejects only that
candidate. The coherent repair is now certified. With \(F\) the local
raw-to-dressed clock shear, the corrected middle map is

\[
J_{\rm dressed}=FJ_{\rm raw}F^\sharp,
\qquad
J_{\rm raw}=\frac4{\alpha_B}R_{\rm raise},
\]

and \(q,W,P\), antifields, the companion, and the pairing are transported
together. In raw coordinates the exact principal blocks are
\(I_5,I_{10},I_{10},I_5\); the two clock rows form a triangular algebraic
extension rather than an additional wave sector. This closes
`BERGER_RAW_CLOCK_REATTACHED_WITNESS_TRANSPORT`, but not Green inversion.

The follow-up \(10+2\) block audit finds an exact \(I_2\) clock diagonal.
Eliminating it directly produces a nonzero order-six Schur correction, so the
clock pair must not simply be discarded analytically. Its top symbol is only
rank one and has an exact \(\zeta^2\) factor; it vanishes on the null cone.
Thus the narrowed analytic object is a rank-one wave-divisible extension of
the fourth-order metric block, not a new physical characteristic sector.

The extension is now constructed coefficientwise. The exact curved identity

\[
C_R=-\Box_0F_2,
\qquad
F_2=\frac16(\Box_0\operatorname{tr}-\operatorname{div}\operatorname{div})
\]

allows one scalar prolongation variable \(y=F_2h\). The prolonged 13-row
operator has maximum order four and support-local triangular maps satisfy

\[
E_{13}L_{13}U_{13}^{-1}=L_{12}\oplus I_1.
\]

Within the fixed \(K_{12}\), ghost operator and \(I_2\) clock diagonal, the
metric-to-clock incidence cannot be erased: chain commutation leaves the
nonzero invariant defect \(K_{\rm clock}(P_{\rm ghost}-I_5)\). Thus further
middle-block tuning is closed in that architecture; the causal inverse must
use the exposed scalar-wave extension.

The extension is now cyclic and all-row at the analytic level. The original
34-row BV complex and its cohomology remain unchanged, with degree ranks
\([5,12,12,5]\). The propagation realization adds \(y\) in degree zero and
its pairing-dual \(y^*\) in degree one, giving \([5,13,13,5]\). Exact
solution and source graph SDRs, the formal-adjoint 13-row antifield operator,
and a nondegenerate 36-row cyclic pairing are exported. The future causal
operators must satisfy \(G_{13,+}^\sharp=G_{13,-}\), and their zero-mode
policy is causal Cauchy evolution without a spatial projector.

Consumer contracts must distinguish the authoritative BV ranks from these
analytic realization ranks. In particular, a contract hard-coded only to
\([5,12,12,5]\) does not yet describe the one-pair wave prolongation.

The all-row analytic bookkeeping is now finished. Exact chain maps prove

\[
\Lambda_{54,\pm}
=S_{\rm cl}+\iota_{\rm cl}\Lambda_{26,\pm}\pi_{\rm cl},
\]

so 28 clock/nonminimal/gauge-fixing rows introduce no independent causal
obstruction. The immediate gate is therefore
`BERGER_RAW_ENDPOINT_EXTENSION_GREEN_OPERATORS`: construct advanced/retarded
operators for the exact 13-row scalar-wave/metric extension. Transport
through the certified clock SDR then
gives `BERGER_26_ROW_CAUSAL_GREEN_HOMOTOPY`, and the formula above lifts it
support-locally and cyclically to all 54 rows. The total causal flag remains
false until that endpoint theorem passes.

The endpoint consumer now receives the complete minimal records

\[
W_{34},\qquad P_{34},\qquad \operatorname{pairing}_{34},
\]

in the authoritative 34-row coordinate layout.  The export states and
verifies coefficientwise

\[
P_{34}=q_{34}W_{34}+W_{34}q_{34},
\]

together with cyclicity and nondegeneracy of the pairing.  The independent
quantum-side adapter returns `ADMISSIBLE_EXACT_CURVED_WITNESS` for this
candidate while correctly leaving Green execution unauthorized. A nonzero
defect from any later candidate test rejects the submitted candidate only.
It is not a global nonexistence theorem for all local curved witnesses,
mixed-order witnesses, or Green realizations.

### Active nonlinear support-local export

The nonlinear team additionally requires one authoritative classical export
before its actual theorem or obstruction can be promoted. This is a separate
work package from any homogeneous clock certificate. Its required contents
and current disposition are:

1. the complete support-local \(q_1\) (**complete**) and \(q_2\) (**complete on the rational Berger fixture**);
2. the local \(D\)-action on the same declared complex (**complete on all 54 rows**);
3. the contraction data
   \((\pi_{\rm cl},\iota_{\rm cl},s_{\rm cl})\) (**complete on all 54 rows**);
4. the cyclic pairing, with conventions and formal adjoints pinned (**complete through arity two**);
5. a typed row layout, support/order metadata, hashes, and fail-closed guards.

The separate authoritative
\((W_{34},P_{34},\operatorname{pairing}_{34})\) causal handoff described
above is now complete. The 54-row nonlinear export remains logically
distinct and does not silently substitute for those minimal curved-witness
records.

The handoff gate `CLASSICAL_SUPPORT_LOCAL_Q1_Q2_EXPORT` is now passed by
`BERGER_SUPPORT_LOCAL_Q2`. This is not a reduced harmonic matrix: it is the
arbitrary-input four-dimensional local operation on the complete 54-row
gauge-fixed complex at the exact rational Berger background. Its separate PBW
payload contains 150305 terms over \(\mathbb Q(\sqrt{10})\), on 39 nonzero
output rows, through maximum total jet order six.

For cross-team use, the unary operator must be exported under the semantic
name `classical_unary_q1` (equivalently \(\ell^{\rm cl}_1\)). The existing
`q1_blocks` key is a stable historical certificate field, not the quantum
\(\hbar Q_1\). The export must also distinguish its two audit layers: the
producer derives the Bach PBW expansion from the action, while the independent
consumer verifies the frozen coefficients and their algebraic BV identities
without independently rederiving the action Hessian.

The combined minimal unary item is now complete:

```text
BERGER_COMBINED_MINIMAL_CONTRACTION_ALL_34_ROWS = true
```

The portable certificate exports `classical_unary_q1` and the exact
\((\iota_{\rm cl},\pi_{\rm cl},S_{\rm cl})\) on all thirty-four minimal rows.
The twenty nonminimal antighost--multiplier rows are now complete as an
unfixed direct sum. They give an exact pointwise cyclic 54-to-26 contraction,
and the exact curved five-direction companion is derived coefficientwise from
one source. The gauge-fermion canonical transform is now applied
coefficientwise: the full 54-row gauge-fixed `classical_unary_q1`, cyclic
pairing, and transformed contraction are portable and exact. The complete
support-local four-dimensional \(\ell^{\rm cl}_2\), including its
antifield/Koszul--Tate and ghost-antifield rows, is now exact. The raw 34-row
presentation satisfies the coefficientwise arity-two \(L_\infty\) identity;
the clock dressing and gauge-fermion shear transport it canonically to all 54
rows. The canonical Euler densities include both the \(\sqrt{-g}\) factor and
nonlinear index raising; omitting those terms gives the right Hessian but
fails the antifield identity. The final payload also passes an independent
frozen-coefficient and Draft-2020-12 schema audit. The Cartan dependency is
now explicitly split. The full four-dimensional unary equation

\[
q_1\iota_D^{(1)}+\iota_D^{(1)}q_1=D.
\]

is exactly obstructed on the bare 26-row complex: at
\(\zeta=(1,1,0,0)\), its Douglis symbol cohomology has dimensions
\((0,6,6,0)\), while \(\sigma(D)=1\). The D-equivariant SDR carries this
obstruction to the bare 54-row complex. Therefore the arity-two source and
homotopy remain machine-blocked there. The next gate is a residual/BFV or
causal Cartan extension. These routes are now explicitly split, with the
causal route selected first. The conditional transfer theorem proves that a
(D)-equivariant retained causal homotopy supplies
(iota^{(1)}_{D,\pm}=\Lambda_{26,\pm}D_{26}), makes the arity-two source
(q_1)-closed, and gives a raw causal primitive. The retained 26-row Green
homotopy is therefore the next gate. Cyclic completion of the binary
primitive, Hadamard data, and the residual/BFV alternative remain separate
and false.

### Reduced-mode arity-two fixture

`BERGER_RATIONAL_FIXTURE_Q2_D_BLOCK` now provides a separate, deliberately
small nonlinear handoff. The exact stationary homogeneous Berger action is
differentiated in the normalized coordinate \(c=c_0(1+u)\), after dividing
the action density by the constant \(c_0\), to produce a rational six-row Koszul--Tate
block: three field variations and three equation rows. Its Hessian is
`classical_unary_q1`, its symmetric third derivative is
`classical_binary_q2`, and the canonical field--equation pairing fixes
cyclicity. Every row has homogeneous \(D\)-weight zero, so the exported local
\(D\)-action is the zero matrix on this centered block.

The certificate proves \([q_1,D]=0\), the arity-two \(q^2\) identity,
cyclicity, and closure exactly. It is immediately ingestible by ND2, but its
scope is only `REDUCED-MODE`. It neither satisfies
the full four-dimensional nonlinear theorem nor tests a nonzero-weight
\(D\)-obstruction. It remains a regression fixture downstream of the new
54-row support-local export.

The first nonzero-weight extension has now been decided as a scoped no-go.
For the rational Berger cubic tensor the square map
\(Q(x)=q_2(x,x)\) is anisotropic over both \(\mathbb R\) and \(\mathbb C\).
Therefore a finite, pairing-nondegenerate, q2-closed homogeneous block
containing any field mode of weight \(w\ne0\) would have to contain the
unbounded sequence \(w,-2w,4w,-8w,\ldots\). The attempted
\((-1,0,+1)\) block fails first at \(E_{u,+2}\), with normalized leakage
witness \((80/27,0,0)\). This rules out finite nonzero-weight truncations; it
does not rule out the infinite all-weight complex and is not a Cartan
cohomology obstruction.

The infinite all-weight homogeneous complex now closes the corresponding
positive gate. Retaining every \(k\in\mathbb Z\) makes q2 a weight-convolution
operation. The linear homotopy \(\iota_D^{(1)}E_k=kH^{-1}E_k\) has a
generically nonzero arity-two Cartan source, and an explicit first-order,
graded-cyclic \(\iota_D^{(2)}\) contracts it exactly. Thus nonzero weights have
now genuinely been tested: finite cyclic truncations fail, while the infinite
homogeneous lattice admits the arity-two contraction. This remains
`REDUCED-MODE`; extending the formulas to the full four-dimensional 54-row
complex is the next gate.

The all-row unary ingredients needed by that extension are already frozen in
`BERGER_54_ROW_LOCAL_D_ACTION`: the invariant time derivative acts locally on
all 54 rows, commutes coefficientwise with `classical_unary_q1`, intertwines
the contraction, and preserves the cyclic pairing. Together with the new
support-local \(q_2\), this proves the arity-two \(D\)-derivation identity
termwise because \([e_0,e_i]=0\). What remains is the nonlinear Cartan
homotopy itself, not another unary \(D\)-construction. Independently,
`BERGER_54_ROW_CAUSAL_HOMOTOPY_REDUCTION` reduces the complete causal theorem
exactly to the retained 26-row mixed-order metric endpoint.

Begin with a conformally coupled scalar \(T\).  Define a domain on which it is a
valid clock and construct complete observables

\[
\mathcal O_A(\tau)=\text{``the value of }A\text{ when }T=\tau\text{.''}
\]

Verify rather than assert:

- gauge invariance of \(\mathcal O_A(\tau)\);
- nontrivial \(\tau\)-evolution and its reduced Poisson brackets;
- monotonicity, turning points, Gribov/multiple-crossing issues, and the domain
  of the clock chart;
- the total \(D\) charge, including the scalar improvement and boundary terms;
- whether clock gauge fixing converts a first-class constraint into a physical
  Hamiltonian without changing the status of total \(D\).

The critic wins this rail if every legitimate clock sector necessarily gives
total \(D\) a nonzero charge.  The construction survives if explicit
relational observables evolve nontrivially while total \(D\) remains a
zero-charge presymplectic degeneracy.

## Work package C-D4: perturb the background

Let the differential, residual action, contraction, and background depend on a
deformation parameter \(\epsilon\).  Determine:

- whether a deformed residual strong deformation retract exists;
- whether the homological perturbation series converges, terminates by a
  filtration, or fails;
- an explicit bound such as \(\|h\,\Delta Q\|<1\), or the exact algebraic
  replacement used to define the stability radius;
- which identities require an exact Killing or conformal Killing generator;
- whether the causal complex survives after the finite residual cohomology
  calculation fails;
- the first obstruction class and the lowest order in \(\epsilon\) at which it
  appears.

The output must be a quantitative stability/no-go radius in a declared norm or
filtered category.  “Generic backgrounds are harder” is not a result.

## Generalization programme

Begin this rail after the current paper-improvement investigation and its
immediate certificate repairs are frozen.

Promote results one level at a time and record the level in every new
certificate:

```text
G0  exact fixture or finite reduced-mode block
G1  complete invariant/harmonic sector on one background
G2  full linearized complex on one background
G3  open background class with uniform hypotheses
G4  nonlinear stability on that class
G5  boundary/quantum completion
```

A covariant formula is not automatically a `G3` theorem.  Promotion requires
uniform operator domains, support conditions, charges, and verification
hypotheses.

### Work package C-G1: extract the causal-transfer theorem — certified

Separate the cylinder construction into an abstract theorem whose declared
inputs are a cyclic local gauge/detour complex, Green-hyperbolic endpoints or
companions, a support-preserving SDR, and finite-order cyclic shears.  Prove
the transport formulas for retarded/advanced homotopies, support, and cyclic
adjoints.  Re-run the cylinder as a consumer of this theorem.

`ABSTRACT_CYCLIC_CAUSAL_TRANSFER` now certifies this conditional theorem,
including endpoint-companion construction, finite direct sums,
support-local cyclic shears, and complete 54- and 64-row Berger replays.  The
result is `G2`: endpoint Green hyperbolicity is a hypothesis, and timelike
boundaries, pseudodifferential projectors, Hadamard products, interactions,
and quantum claims are not included.  Its next generality gate is C-G5 or the
uniform background class C-G2, not another cylinder replay.

### Work package C-G2: conformally flat background class

`CONFORMALLY_RELATED_CYCLIC_CAUSAL_TRANSFER_V1` now certifies the first G3
open class: the fixed cylinder manifold with metrics
\(g_\varphi=e^{2\varphi}g_0\), where \(\varphi\in C_b^\infty\) lies in a
declared open bounded-smooth neighbourhood.  The exact finite BV map includes
the affine Diff--Weyl ghost term \(\omega_\varphi=\omega-\xi(\varphi)\) and
its cotangent shear.  Conjugation transports the differential, gauge fermion,
Green homotopies, causal support, cyclic adjoint and current pairing.  An
independent consumer replays the nonconstant factor
\(1+1/(10(1+t^2))\).

This does **not** cover arbitrary locally conformally flat topology, timelike
boundaries, chart patching, or the original untransported coordinate gauge.
`CONFORMALLY_EINSTEIN_TRACTOR_CURVATURE_OBSTRUCTION_V1` closes the first
curvature gate: unit Nariai is globally hyperbolic, Einstein and Bach-flat,
but its normalized Weyl witness \((3/2)C_{2323}=1\) prevents the flat cylinder
tractor connection from being related to it by the same invertible zero-order
conjugation, even locally.  This is only a `LOCAL-ALGEBRAIC` obstruction; it
does not exclude curved differential HPL corrections or an independently
constructed Nariai Green homotopy.

The remaining C-G2 alternatives are therefore a curved Bach-flat HPL
correction/obstruction or a local-patching theorem within the conformally
flat category.

`CONFORMALLY_EINSTEIN_YANG_MILLS_DETOUR_CORRECTION_V1` resolves the first
half of the curved repair.  The flat parent middle must be replaced by
\(M^D=\delta^Dd^D-F\!\cdot\); exact rational matrix replay verifies
\(M^Dd^D=\varepsilon(\delta^DF)\) and
\(\delta^DM^D=-\iota(\delta^DF)\), while omitting the curvature action leaves
rank-two defects on both sides.  Bach-flatness makes the Nariai normal tractor
connection Yang--Mills, so the corrected formally self-adjoint parent complex
exists.  The next unresolved gate is its actual curved differential BGG/HPL
compression to the metric Bach complex; no Nariai Green claim has yet been
made.

`NARIAI_POINTWISE_BGG_CURVATURE_COMPRESSION_OBSTRUCTION_V1` now evaluates the
first downstairs candidate exactly.  Inserting the Nariai Weyl tensor into
the standard and adjoint tractor representations gives a rank-54 parent
curvature action.  The raw pointwise term
\(Q_F=-p_1(F\!\cdot)i_1\) has rank nine, but
\(JQ_F-Q_F^TJ\) has rank two and normalized witness
\((JQ_F-Q_F^TJ)_{1,4}=1\).  Thus pointwise compression alone is excluded;
the next calculation must include the first derivative-dependent BGG
splitting correction.  This is not a no-go for the full Bach-flat detour
compression.

`NARIAI_FIRST_BGG_ZEROTH_ORDER_STRICTIFICATION_OBSTRUCTION_V1` now screens
the complete zeroth-order strict-chain repair.  The current certificate
explicitly supersedes hash
`c4738c825fd1814962d4970e62341f0399fafb08331fe9b57bc25958b1fadbcc`,
which used the wrong temporal Schouten sign.  The corrected convention is
essential away from the conformally flat cylinder: the Nariai Schouten
components are \((-1/6,+1/6,+1/6,+1/6)\), form slots carry the covector
curvature action, and the standard-tractor middle slot carries the dual vector
action.  For arbitrary bundle maps
\(\Delta L_0:H_0\to C_0\) and \(\Delta L_1:H_1\to C_1\), the three
transverse derivative axes have rank nine and uniquely fix each row of
\(\Delta L_1\).  The remaining axes consistently give \(\Delta L_0=0\),
but a rank-four algebraic residual with twelve entries survives; its
coefficient \((4,1)=2/3\) gives normalized witness one.  The harmonic
normalization defects remain zero.  Hence no zeroth-order correction can
strictify the first Nariai BGG square with the conformal-Killing operator
fixed.  This is not a full curved BGG no-go: genuinely derivative-dependent
splitting corrections,
homotopy-coherent transfer of the Yang--Mills detour middle, and an
independent Nariai Green construction remain open.

`NARIAI_CURVATURE_INCIDENCE_FIRST_SQUARE_V1` now identifies that entire
residue geometrically.  Reconstructing the Nariai normal tractor curvature
independently gives the exact coefficient identity
\[
d^D(L_0+\Delta L_0)-(L_1+\Delta L_1)K=I_\Omega,
\qquad (I_\Omega\xi)_a=\Omega_{ab}\xi^b.
\]
Both sides have rank four and twelve nonzero entries, all in the Lorentz
generator slot, and their difference is zero.  The reconstructed
\(\operatorname{ad}(\Omega)\) also equals the PBW normal-tractor square
exactly, excluding an accidental convention match.  Reversing the incidence
sign leaves twelve defects.  The former residual is therefore the canonical
curved-connection Lie-derivative incidence, not unexplained cone cohomology.
This is a positive homotopy-coherent first-square theorem, not a strict-square
promotion.  The next gate is its cyclic mapping-cone completion on the dual
equation and identity rows, followed by recompression of the Yang--Mills
middle.

`NARIAI_CURVATURE_INCIDENCE_SHIFTED_CHAIN_V1` continues the incidence through
the parent middle.  With
\[
\Phi_0=I_\Omega,
\qquad
\Phi_1=M^D L_1^{\rm corr},
\]
the exact PBW relation is
\[
M^D\Phi_0+\Phi_1K=0.
\]
Each nonzero term contains 154 coefficients through order two; their sum is
zero.  Moreover the factorized relative saddle
\(S=A^\sharp M^D A\), \(A=(L_1^{\rm corr},1)\), annihilates
\((K,I_\Omega)^T\) in both displayed equation blocks.  This supplies the
complete local algebra for the incidence saddle.

The post-delivery cyclic audit found a verifier boundary rather than a parent
no-go.  Applying the generic PBW adjoint routine to the already normal-ordered
component middle leaves a rank-60 algebraic replay defect with 60 diagonal
entries and normalized witness one.  The factorized operator
\(M^D=(d^D)^\sharp d^D-F\!\cdot\) remains formally self-adjoint by
construction, and its factor-ordered saddle identities pass.  The failing
path has discarded the Hom-bundle covariance carried by the `(01)` and `(23)`
cross-form coefficient tensors during normal ordering.  Therefore
`PARENT_FORMAL_SELF_ADJOINTNESS_NO_GO` remains false.  The next gate is a
Hom-bundle-covariance-aware PBW adjoint/associativity replay (or an independent
variational coefficient-table checker), followed by the odd cotangent cone
and mapping-cylinder SDR.  The following certificate takes and completes the
independent-checker alternative; repairing the generic normalizer is no longer
on the critical path.

`NARIAI_CURVATURE_INCIDENCE_CYCLIC_MAPPING_CYLINDER_V1` closes that verifier
gate by taking the allowed independent route rather than modifying the shared
normalizer.  Its eight blocks are
\[
(\epsilon,\chi,h,a,h^\sharp,a^\sharp,
  \epsilon^\sharp,\chi^\sharp),
\]
with split differential equal to the corrected Yang--Mills parent plus the
contractible pair \(\chi\mapsto h\) and its cotangent dual.  The finite-order
canonical shear
\[
b=a+L_1^{\rm corr}h
\]
and the forced cotangent shift produce the graph-coordinate differential.
The portable formal matrices independently verify both squares, odd
cyclicity before and after the shear, its two-sided inverse, the inclusion and
projection chain identities, \(PI=1\),
\(IP-1=QH+HQ\), and cyclicity of \(H\).  No inverse Laplacian, inverse curl,
projector or Green atom occurs.  The cone therefore deformation-retracts to
the parent without duplicating cohomology.

The endpoint ghost embedding is now exact and geometric:
\[
\xi\longmapsto (L_0\xi,K\xi),
\qquad
Q\xi=(K\xi,I_\Omega\xi).
\]
This promotes the parent-relative cyclic incidence cone, while leaving the
generic post-normal-order PBW adjoint routine unrepaired.  That routine is no
longer a blocker because the independent factorized variational checker
covers the theorem.  The remaining C-G2 problem is genuinely analytic and
comparative again, but the first strict comparison is now closed by the
following theorem.

`NARIAI_STRICT_METRIC_GRAPH_CHAIN_MAP_OBSTRUCTION_V1` proves that the
canonical ghost embedding cannot extend to a field-only strict graph

\[
h\longmapsto(h,Rh)
\]

for any finite-order differential operator \(R:H_1\to C_1\).  The chain
square would force \(RK=I_\Omega\).  In the global unit-Nariai chart,
\(\partial_\chi\) is Killing, so \(K\partial_\chi=0\), while at the certified
homogeneous basepoint

\[
(I_\Omega\partial_\chi)_4=\frac23.
\]

Thus \(RK\partial_\chi=0\) contradicts the nonzero incidence.  This is an
all-order kernel witness, not a bounded ansatz: exact curved-PBW screens at
orders zero through four merely reproduce its rank-four signature.  It rules
out only the canonical ghost map plus identity metric component and a
field-only graph.  Relative equation-level, homotopy-coherent and enlarged
mapping-cylinder comparisons remain open.  With the action-derived Bach
endpoint below now available, the active gate is
`C_G2_NARIAI_RELATIVE_CYCLIC_PAIRING_AND_EQUATION_CONE`; only after that cone
closes may a Nariai Green transfer be promoted.

`NARIAI_ACTION_DERIVED_BACH_ENDPOINT_V1` replaces that provisional endpoint
interpretation with the actual Hessian.  Directly varying

\[
B_{ab}=\nabla^c\nabla^dC_{acbd}+\frac12R^{cd}C_{acbd}
\]

on unit Nariai, including all four connection variations against the nonzero
parallel background Weyl tensor, yields the complete trace-free operator at
orders zero, two and four.  Its tensor symmetry, trace, divergence and gauge
defects vanish exactly.  In the repository action normalization,

\[
B_{\rm parent,comp}+Q_{\rm unique}=-2B_{\rm action}
\]

coefficientwise, with zero defect, and an independent product-scaling family
checks the algebraic coefficient.  Thus the old certificate showing that
\(Q_{\rm unique}\) alone is noncyclic remains only a diagnostic of the
provisional coefficientwise Hom-bundle adjoint; it is not an endpoint no-go.
The strict field graph is still excluded by the Killing-field theorem.

`NARIAI_METRIC_BACH_CYCLIC_BV_COMPLEX_V1` now closes the endpoint pairing
layer.  The Bach output is already in evaluation-dual coordinates, so the
tensor Gram is not applied a second time: the field/equation pairing is
(I_9), while the ghost/identity pairing is
(\operatorname{diag}(-1,1,1,1)).  The typed adjoint (K^\sharp) is derived
from these pairings.  The identities

\[
B_{\rm action}K=0,
\qquad
K^\sharp B_{\rm action}=0
\]

are exact, and the four-row complex
(H_0\to H_1\to H_1^*\to H_0^*) is nilpotent and odd cyclic.  An independent
consumer reconstructs both Noether identities from the serialized Bach and
BGG tables, including the tensor divergence.  Formal self-adjointness of the
middle row is the second-variation theorem for the Weyl-squared action at the
Bach-flat solution; the deficient generic normal-order adjoint is not used as
authority.

`NARIAI_PARENT_REDUCIBILITY_MISMATCH_V1` then rejects the proposed
equation-only comparison before another cone search.  Unit Nariai has six
explicit independent global product Killing fields, hence

\[
\dim H^{-1}_{\rm metric}\geq6.
\]

For the current Yang--Mills parent, a ghost cocycle is a parallel normal
adjoint tractor.  Its value must lie in the common kernel of the six curvature
blocks.  The stacked (90\times15) matrix has exact rank fourteen, so

\[
\dim H^{-1}_{\rm parent}\leq1.
\]

The certified incidence cylinder retracts to this parent and has the same
ghost cohomology.  Thus its cone with the metric complex cannot be acyclic,
and adding only contractible equation/identity rows cannot repair the gap.
The normalized deficit is at least (6-1=5).  This is the geometric
distinction between parallel adjoint tractors and infinitesimal Cartan
automorphisms.  The active gate is now
`C_G2_NARIAI_CURVATURE_CORRECTED_AUTOMORPHISM_PROLONGATION`, beginning with
the local equation

\[
\nabla^D s+i_{p(s)}\Omega=0.
\]

Only after that corrected ghost complex reproduces the metric reducibilities
should equation/identity rows, an SDR or Green transfer be attempted.

`NARIAI_AUTOMORPHISM_PROLONGATION_FIRST_TWO_ROWS_V1` now performs that repair.
With

\[
d_{\rm aut}=d^D-I_\Omega p_0,
\qquad
\Phi=M^DL_1^{\rm corr},
\]

the exact support-local sequence is

\[
C_0\xrightarrow{(d_{\rm aut},Kp_0)^T}
C_1\oplus H_1
\xrightarrow{(M^D,-\Phi)}C_1^*.
\]

The two defining identities,

\[
d_{\rm aut}L_0^{\rm corr}=L_1^{\rm corr}K,
\qquad
M^Dd_{\rm aut}=\Phi Kp_0,
\]

vanish coefficientwise.  Since \(p_0L_0^{\rm corr}=1\), the metric graph
\(\xi\mapsto L_0^{\rm corr}\xi\),
\(h\mapsto(L_1^{\rm corr}h,h)\) is strict through the gauge and constraint
rows, and every metric Killing field becomes a closed prolonged ghost.  The
next gate is `C_G2_NARIAI_AUTOMORPHISM_CYCLIC_BACH_EXTENSION`: add the action
Bach equation and the forced cotangent/identity rows, then test the complete
cyclic complex and its metric graph.  No SDR or Green claim precedes that
test.

`NARIAI_AUTOMORPHISM_CYCLIC_BACH_EXTENSION_V1` now closes this gate.  The
canonical completion is the odd-cotangent saddle of the constraint complex,
with multiplier \(\lambda\in C_1\) and quadratic action

\[
S^{(2)}_{\rm aut}
=
\frac12\langle h,B_{\rm action}h\rangle
+\langle\lambda,M^Da-\Phi h\rangle.
\]

In the ordered carrier

\[
\epsilon; (a,h,\lambda);
(a^\sharp,h^\sharp,\lambda^\sharp);
\epsilon^\sharp,
\]

the total rank is \(288\).  Nilpotency reduces exactly to
\(M^Dd_{\rm aut}=\Phi Kp_0\), \(B_{\rm action}Kp_0=0\), and their formal
adjoints.  The fibre pairings force every cotangent row, while the graph

\[
(L_0^{\rm corr};\ L_1^{\rm corr},1,0;\ 0,1,0;\ p_0^\sharp)
\]

is an isometric strict embedding of the four-row metric Bach complex.  The
next gate is `C_G2_NARIAI_AUTOMORPHISM_SUPPORT_LOCAL_SDR`: construct or
obstruct a finite-order projection and homotopy for the complement.  Green
transfer remains downstream of that gate.

`NARIAI_AUTOMORPHISM_CYCLIC_BACH_SDR_SYMBOL_OBSTRUCTION_V1` now gives the
negative verdict for this carrier.  Use the explicit Rees weights

\[
(0,1,1,1,3,5,5,6)
\]

on the eight prolonged blocks and \((0,1,5,6)\) on the embedded metric
complex.  At the timelike covector \((1,0,0,0)\), the metric ranks are
\((4,5,4)\), so its symbol complex is exact.  The parent middle has rank \(45\)
on \(C_1[60]\).  Since the multiplier \(\lambda\) has no incoming arrow and

\[
\lambda\longmapsto
(M_2\lambda,-L_{1,2}^\sharp M_2\lambda),
\]

its 15-dimensional kernel survives as degree-zero symbol cohomology.  A
finite-order filtered SDR would induce an associated-graded quasi-isomorphism,
contradicting this mismatch.  The conclusion is scoped: the cyclic Bach
complex remains exact as a BV differential, but it is too small for the
desired retract.  The next gate is
`C_G2_NARIAI_PARENT_DETOUR_MAPPING_CONE_REPAIR`, which must add the parent
detour/cotangent cone rather than trying to invert the bare multiplier saddle.

`NARIAI_PARENT_DETOUR_MAPPING_CONE_REPAIR_V1` now closes that repair.  The
economical rank-310 carrier adds the eleven-dimensional pointwise complement
of (p_0:C_0\to H_0) and its cyclic dual.  With

\[
x=a-d_{\rm aut}J_0s-L_1h,
\qquad
y=\lambda-\frac12\Phi h,
\]

the complex splits into the metric Bach complex, the algebraic complement
pair, and the parent saddle

\[
\begin{pmatrix}-M^D/2&1\\1&0\end{pmatrix},
\qquad
\begin{pmatrix}0&1\\1&M^D/2\end{pmatrix}
\]

as its finite-order local inverse.  Exact coefficient replay gives
(gJ_0=1), (J_0g=1-L_0p_0),
(d_{\rm aut}J_0g+L_1Kp_0=d_{\rm aut}), and

\[
-\frac12L_1^\sharp M^DL_1-\frac12Q_{\rm unique}=B_{\rm action}.
\]

The ten-block inclusion, projection and cyclic homotopy obey
(PI=1) and (1-IP=QH+HQ), both before and after the certified BV-canonical
triangular transform.  No rank-minimality claim is made.  The next gate is
`C_G2_NARIAI_REPAIRED_PARENT_GREEN_TRANSFER`: combine the parent causal input
with a coefficient-complete metric endpoint witness.  The SDR retracts onto
the metric complex, not the bare parent, so its direction must not be silently
reversed.

The first analytic half is now frozen in
`NARIAI_YANG_MILLS_PARENT_GREEN_HOMOTOPY_V1`.  Flatness is not required.  On
global unit Nariai the normal adjoint-tractor connection is Yang--Mills, and
the backward witness

\[
W_{\rm parent}=(\delta^D,1,d^D)
\]

gives

\[
QW+WQ=
\operatorname{diag}
\bigl(
\delta^Dd^D,
d^D\delta^D+M^D,
M^D+d^D\delta^D,
\delta^Dd^D
\bigr).
\]

Every block has principal symbol
(-g^{ab}\zeta_a\zeta_bI); tractor curvature and spacetime Ricci commutators
are lower order.  Global hyperbolicity therefore supplies unique
(G_{{\rm parent},\pm}), and
(\Lambda_{{\rm parent},\pm}=W_{\rm parent}G_{{\rm parent},\pm}) obeys the
same-sided causal homotopy identity.  Adjoint reversal uses the
pairing-derived degree-sign involution, not a uniform scalar sign.  The active
gate remains the second half: insert this causal input into the repaired
rank-310 cone and verify the all-row homotopy and metric descent.

`NARIAI_REPAIRED_PARENT_GREEN_WITNESS_PREFLIGHT_V1` now fixes the leading
metric normalization.  If (G_H) is the trace-free tensor Gram and

\[
T_{\rm pr}=\Box\operatorname{div}
-\frac13d\operatorname{div}^2,
\]

then, in the certified H0/H1 coordinates,

\[
T_{\rm pr}K=(\zeta^2)^2I_4,
\qquad
B_{\rm action}+\frac12G_HKT_{\rm pr}
=\frac12(\zeta^2)^2G_H.
\]

Thus both ghost and fibre-identified field blocks have scalar biwave leading
symbols.  The candidate (p_0\delta^DL_1) is not the missing companion: its
cubic symbol vanishes exactly by the Bianchi identity.  The active subgate is
now `C_G2_NARIAI_LOWER_ORDER_BIWAVE_FACTOR_COMPLETION`: derive the curved
lower-order companion and an exact normally-hyperbolic factorization or
equivalent Green system before promoting either the metric or rank-310 causal
flag.

`NARIAI_METRIC_BIWAVE_GREEN_HOMOTOPY_V1` closes the lower-order metric gate.
The only Einstein-background first-order correction is fixed uniquely:

\[
T=T_{\rm pr}+\frac13\operatorname{div}.
\]

It yields

\[
TK=(\Box+1)(\Box+\tfrac13)I_4,
\]

and, after the action fibre identification,

\[
G_H^{-1}B_{\rm action}+\frac12KT
=\frac12(\Box I_9+A)(\Box I_9+B).
\]

The parallel endomorphisms (A,B) commute, are (G_H)-self-adjoint, and have
curvature-channel multiplicities (4+1+4).  All primal factors and their formal
duals are normally hyperbolic.  Their same-sided Green compositions give the
complete four-row metric homotopy with causal support and complementary-degree
adjoint reversal.  The known generic PBW adjoint backend is not used as upper
row coefficient authority; the invariant action-pairing adjoint theorem is.
`NARIAI_REPAIRED_310_ALL_ROW_GREEN_TRANSFER_V1` closes the remaining
homological gate.  In both split and original coordinates,

\[
\Lambda_{310,\pm}=H+I\Lambda_{{\rm met},\pm}P
\]

satisfies

\[
Q\Lambda_{310,\pm}+\Lambda_{310,\pm}Q=1,
\qquad
P\Lambda_{310,\pm}I=\Lambda_{{\rm met},\pm}.
\]

The exact replay includes `H^2=HI=PH=0`, all ten BV blocks, causal support,
the original-coordinate conjugation, and complementary-degree adjoint
reversal.  Thus the single-background Nariai `G2` causal theorem is complete.

`BACH_FLAT_PARENT_GREEN_STABILITY_V1` then promotes the parent analytic input
to a relative-open `G3` class.  In four dimensions `Bach(g)=0` is the
Yang--Mills condition for the normal tractor connection, so the universal
detour witness is degreewise normally hyperbolic on every globally hyperbolic
Bach-flat representative.  The declared ADM ball around Nariai has radius
`1/4`, a common reference causal-speed bound below `2`, and contains the exact
nonconstant consumer

\[
g_\Omega=\left(1+\frac1{10(1+t^2)}\right)^2g_N,
\]

which is Bach-flat and non-conformally-flat.  The class is open relative to
the Bach-flat solution locus, not in the space of all metrics.  The next gate
has now narrowed further.  `BACH_FLAT_RANK310_NATURAL_SDR_V1` uses a global
ADM orthonormal-coframe/density transport and the universal normal-BGG,
Yang--Mills detour and Noether identities to bind the complete six-block
finite HPL construction on every member of the class.  The resulting
rank-310 inclusion, projection and homotopy are finite-order, support-local
and cyclic, and retract to the action-derived metric Bach complex.  The
remaining issue is only the non-Einstein metric endpoint's Green homotopy;
neither the parent theorem nor the parent/metric SDR is still open.

`CONFORMAL_NARIAI_310_CAUSAL_TRANSFER_V1` closes the metric half on the full
bounded-smooth conformal orbit

\[
g_\varphi=e^{2\varphi}g_N,
\qquad
\sup|e^\varphi-1|<\frac19.
\]

This class stays inside the radius-`1/4` parent ball because its largest
spatial ADM deviation is `19/81`.  The finite BV map includes
`omega_phi=omega-xi(phi)`, its forced cotangent shear, the conformal tractor
splitting, and the transported gauge fermion.  Conjugation transports the
metric and rank-310 differentials, `I,P,H`, both causal homotopies, cyclic
adjoints, support, and exact metric descent.  Thus the remaining class-wide
problem is strictly transverse: deform inside the Bach-flat locus away from
the global conformal orbit and compute the first SDR obstruction or a new
support-local correction.

`TYPED_BIWAVE_VOLTERRA_GREEN_THEOREM_V1` now separates the reusable analytic
input from both the Berger and Nariai fixtures. For `A=P2 P1+V`, with two
not-necessarily-commuting normally hyperbolic factors and `ord(V)<=2`, it
constructs separate solution- and source-space Volterra resolvents on every
finite slab, proves factorial estimates, both inverse identities, causal
globalization and adjoint reversal against `A^sharp`. Smooth time dependence
is allowed, but the exact wave-energy graph bound for `V` is an explicit
hypothesis. This theorem does not supply the transverse metric/parent SDR.
The active gate remains the first transverse Bach-flat SDR defect, now with a
precise analytic acceptance criterion if the corrected metric endpoint has
this lower-order biwave form.

`NARIAI_TRANSVERSE_LINEARIZED_EINSTEIN_WITNESS_V1` supplies the missing
transverse input.  In the Kantowski--Sachs sector,
`delta a=-(1/3)sinh(2t)` and `delta b=sinh(t)` solve the complete linearized
Einstein ODE at fixed cosmological constant and hence are linearized
Bach-flat.  The tangent is not in the infinitesimal Diff--Weyl orbit: the
background Weyl contraction on one-forms has rank four, the tangent remains
Cotton-flat, and its nonconstant scalar variation is
`delta(C_abcd C^abcd)=-32 sinh(t)`.  At `t=asinh(1)` the normalized tractor
Weyl-slot drift is `delta C_0202=-1`.  This proves that coefficient-frozen
Nariai maps do not extend unchanged, but it is not yet an obstruction to
curvature-corrected maps.  The next gate is now the actual first variation of
the rank-310 chain-map, retract and cyclicity identities along this witness.

That first variation is now closed in the outer incidence rows.
`NARIAI_TRANSVERSE_CURVATURE_INCIDENCE_VARIATION_V1` reconstructs the
Ricci-free moving-frame curvature variation, obtains the exact rank-four
normal-tractor incidence `dot(I_Omega)`, and proves that the automorphism row
must acquire `-dot(I_Omega)p0`.  Both maps have twelve nonzero entries and the
normalization `-(1/2)dot(I_Omega)[4,1]=1`; cyclicity fixes the formal-adjoint
dual row.  `NARIAI_TRANSVERSE_ALGEBRAIC_BGG_PAIRING_VARIATION_V1` now makes
that dual coefficientwise explicit.  In the moving orthonormal
conformal-tractor/covariant-PBW frame, the representation-theoretic Kostant
maps, harmonic projections, and four fibre pairings have zero variation; the
fixed-Λ Einstein tangent also has zero moving-frame Schouten variation.  The
remaining BGG variation is therefore not algebraic and not a pairing
normalization: it is the Levi--Civita connection/PBW variation and its
middle/Schur propagation.  The jet-aware parent calculation now closes the
BGG first square and Yang--Mills identity with complete first-jet coverage.
The exact bivariate coordinate recurrence supplies every mixed spatial jet
requested through order three, but the subsequent composition audit finds a
more basic backend failure.  The typed
\(M^D\circ L_1^{\rm corr}\circ Kp_0\) associator vanishes at the base point
and has 209 first-variation coefficients in the current linearized PBW
backend.  Since the shifted chain follows abstractly from the parent identity,
the first square and \(p_0L_0=1\) in an associative differential-operator
  algebra, the reported 207-coefficient defect is not an authoritative operator
obstruction.  The Phi/L0/K screens remain exact regression calculations only
relative to that superseded target.  The coefficient-jet-aware associative
replay has since closed the parent identity, associator and shifted chain.  The
factorized Hom-adjoint middle and cyclic compressed Schur have also closed with
fifth-order curvature-jet coverage.  The upper relative-saddle identity
`Schur (K p0)+L1_corrected^sharp M_parent (I_Omega p0)=0` now has zero base and
first-variation defects as well.  The relative-incidence rows are therefore
complete.  The action endpoint gate is now complete as well.  Direct
differentiation of the Bach formula proves that the transverse action Hessian
has no varying order above two, and its 115 order-two coefficients agree
exactly with the correctly scaled parent target.  The parent artifact formerly
displayed the factor `-1/2` while serializing the unscaled endpoint; it now
stores both tables separately.  Missing derivatives of the explicit varied
Weyl coefficient can affect only orders zero and one, so the frozen lower table
is not used.  Instead the complete `60 x 45` rank-45 differentiated-Noether
solve determines the unique lower action completion; action cyclicity is a
separate consistency check rather than an input to uniqueness.  The complete
rank-310 first variation now follows without a new ansatz: differentiating the
universal ten-block SDR gives twenty-one zero matrix defects in both split and
original coordinates, including all side conditions and cyclic adjoints.  No
row is dropped, and all varied maps remain finite-order and support-local.
The transverse metric causal first variation is exact globally at formal
order one.  The tangent is generated on every fixed compact time slab by an
exact Kantowski--Sachs Einstein family, and the finite Duhamel formula
`Gdot_+/-=-G0_+/- Pdot G0_+/-` satisfies both inverse identities, the
differentiated chain homotopy and same-sided support.  The full 310-row
variation is globalized by the normalized cyclic basic perturbation lemma,
not by treating the Taylor/PBW normalization table as a global field.  Its
four HPL formulas obey the complete SDR identities, agree with the pointwise
geometric representative, and transfer the advanced/retarded homotopy through
formal first order.  This closes the transverse tangent causal gate at its
honest formal scope.  A single smooth exact nonzero-`epsilon` family over the
entire cylinder remains unclaimed.

### Programme residual-atlas and tangent-cone handoff (2026-07-18)

After the current transverse-causal gate, this lane must emit the classical
causal/gauge/carrier fragment of the shared generated residual atlas.  Use the
Einstein team's authoritative schema when it lands; do not create a competing
programme schema.  Seed vacuum cylinder, Berger clock, conformal Nariai, and
the open Bach-flat parent class at exactly their certified scopes.  Every
record must declare theory, background, boundaries, charge sector, carrier,
degree, parity, `(ell,m,k,omega)`, causal maps, support class, and an explicit
carrier crosswalk or `NO_CERTIFIED_MAP`.  The only allowed lifecycle values
are `CERTIFIED`, `OBSTRUCTED`, `OPEN`, `NOT_APPLICABLE`, and
`NO_CERTIFIED_MAP`.  The centered classes `[W_+^2]` and `[W_-^2]` are
deformation/vertex classes, never one-particle modes.

The analytic reduction lemma is now certified by
`FINITE_HARMONIC_SECOND_ORDER_TANGENT_CONE_THEOREM_V1`.  For the shared
finite-harmonic second-order tangent cone,

\[
\mathcal Z_2^{\mathcal C}
=\{u:\mu_X(u)=0,\ R_j^{\mathcal C}(u)=0\}.
\]

the theorem requires complete harmonic output closure, removes gauge and
Noether rows before forming the adjoint cokernel, identifies the certified
stabilizer subspace with `mu_X`, and uses a complementary basis for
`R_j^C`.  Its adversarial resonance fixture has one persistent moment-map
row and one category-sensitive row: the latter obstructs bounded finite
Fourier corrections but is killed by `t exp(i omega t)` in the smooth-
secular category and by the retarded integral for compatible compact
sources.  The theorem is abstract and does not upgrade any background.  Its
next gate is atlas instantiation, with a distinct correction-category record
rather than one ambiguous second-order status.

### Work package C-G3: clock-family stability

Replace the single Berger fixture by an audit of the full squashing interval,
nearby fixed couplings and scalar potentials, first inhomogeneous clock
perturbations, and nearby coupled backgrounds.  Use an exact
implicit-function, bifurcation, or obstruction calculation to decide whether
clock monotonicity, energy positivity, (delta Q_R=0), and the BV contraction
hold on an open family or only on an isolated branch.

### Work package C-G4: complete Berger relational observables

After the 54-row causal clock data freeze, construct one complete observable

\[
\mathcal O_A(\tau)=A\text{ evaluated when the Berger phase equals }\tau.
\]

Prove its gauge invariance, causal dependence, clock-chart domain, treatment
of repeated phase crossings, reduced Poisson brackets, nontrivial
\(\tau\)-evolution, and compatibility with the induced pairing. Reconcile the
evolution explicitly with the fixed-coupling identity
\(\Omega(\delta,\mathcal L_D)=0\); do not treat the name “clock” as a
relational-observable construction.

The first scoped C-G4 milestone is now complete in
`BERGER_RETARDED_RELATIONAL_MAXWELL_OBSERVABLE`.  A compact spacetime Maxwell
source prepares the certified two-phase mode before emission, so the exact
\(1+z=2\) clock-slice reading is an actual retarded signal rather than a
characteristic preflight.  The observable is Maxwell-gauge, Weyl,
diffeomorphism and raw-\(D\) invariant, has retarded causal dependence, and is
single-valued on the lifted phase clock labelled by
\(\widetilde\tau=\tau+2\pi n\).  Its exact reduced block satisfies

\[
\{x,y\}=-\frac1{32\pi^2},\qquad
\partial_{\widetilde\tau}Q=-\frac{8\sqrt{10}}9P,qquad
\partial_{\widetilde\tau}P=\frac{8\sqrt{10}}9Q.
\]

Thus fixed-\(\widetilde\tau\) observables are raw-\(D\) invariant while the
family evolves nontrivially with the clock reading.  This is an exact `G0`
spatially averaged probe-mode theorem, not a complete harmonic sector or a
fully backreacted signal.  The localized rod/memory observer morphism stops
fail-closed at the first missing mixed coefficient
\(\epsilon_R^2\kappa\): shifted detector profiles, clock transport and their
cyclic adjoints are not present in the certified 84-row axial first-jet
complex.  The observer team owns that mixed-order completion.

### Work package C-G5: one nearby detour-system pilot

After C-G1 is certified, apply the abstract transfer theorem to one conformal
spin-three, conformal gravitino, or finite mixed-field detour system on a
declared Bach-flat Lorentzian background. Choose the smallest system with an
explicit tractor parent and formal pairing. Return transferred Green
homotopies or the first normalized curvature/support obstruction. Do not
begin a higher-spin tower.

### External bridge C-X: meet adjacent work in its own observables

For each promoted theorem, choose one primary adjacent result and provide:

1. a convention dictionary for fields, couplings, charges, boundaries, and
   inner products;
2. an exact reproduction of one published benchmark in its original regime;
3. the new consequence of the present BV/Taub analysis stated in that
   literature's language;
4. a sentence identifying what the adjacent result does **not** claim.

Prioritize Fischer--Marsden--Moncrief/Taub linearization stability,
Lü--Pope critical gravity, and the detour/BGG literature.  Useful bridge
questions include whether critical/log modes satisfy the Taub constraints,
whether zero energy means gauge or merely null pairing, and whether the
abstract causal-transfer theorem supplies a missing Green-complex result.
Do not ask adjacent authors to adopt the (D)-quotient vocabulary before the
translation has been made.

Use the adjacent-work portfolio and outward-facing acceptance criteria in
[`universe-building-roadmap.md`](universe-building-roadmap.md), and prepare any external
contact with [`adjacency-bridge-note-template.md`](adjacency-bridge-note-template.md).

## Common background matrix

Complete every cell established by your work; write `OPEN`, `NOT TESTED`, or
`NOT APPLICABLE` rather than extrapolating.

| Setting | \(D\) charge | Cartan contraction | Causal homotopy | One-particle sector | Pairing | Einstein sector |
|---|---|---|---|---|---|---|
| Vacuum cylinder | known target; re-audit charge | known target | proved baseline | zero in stated absolute residual complex | \(I_2\) on centered degree-four classes | proper solution sector |
| Positive Berger clock | zero on the declared smooth fixed-coupling linearized phase space | complete 54-row causal cyclic \(K_{\rm Berger}\)-Cartan contraction through arity three; repaired coupled Maxwell \(q_2\), mixed \(q_3\), retained transfer and coupled Cartan are exact | complete advanced/retarded 54-row chain contractions plus a compact neutral retarded Maxwell signal; independent 84-row observer construction open | no Paper-IX one-particle claim; the Maxwell signal is a classical sourced solution, not a cohomology class | gravity--clock and typed gravity--clock--Maxwell cyclic pairings complete on their declared carriers | certified non-Einstein Weyl--matter control branch; canonical support-local Einstein-like/extra-Weyl projector obstructed on retained 36 rows |
| Cylinder + scalar clock | open | open | open | open | open | open |
| Cylinder + Yang--Mills | open | open | open | open | open | open |
| Weakly deformed background | open | open | open | open | open | open |
| Lorentzian dS/AdS | boundary-dependent | open | open | open | open | selected-sector question open |
| Asymptotically flat | physical charge expected; compute | likely unavailable; do not assume | open | expected nonzero; compute | open | decisive |

## Priority and stop/go decisions

1. Treat the Paper IX clean-tree freeze and its classical/nonlinear/quantum
   scoped signoffs as complete.  Do not reopen the certified \(q_2,q_3\),
   Green, or arity-three \(K_{\rm Berger}\)-Cartan calculations.  Raw affine
   \(D\), arity four, Hadamard and quantum gates remain outside that theorem.
2. Treat the repaired coupled Maxwell \(q_2\), mixed \(q_3\), retained
   \(\ell_3\), and coupled arity-three Cartan calculation as complete on their
   declared full and retained carriers.  Preserve the historical 1,234/953
   defect atlas as a negative control.
3. The observer team owns the independent backreacted 84-row
   unary/pairing/Green construction.  It must supply the on-shell rod
   background and explicit local detector operators \(B_a,B_a^*\); the
   classical team must not substitute the obsolete 78-row target or import
   the memory--Maxwell inverse before the observer unary complex closes.
4. The retained-36 branch-basis gate is closed by the normalized canonical
   local-projector obstruction.  The quantum team must import that verdict and
   keep the branch-space \(\ell_3\) mixing table false.  Paper XI proceeds on
   the unsplit retained cyclic causal complex.
5. Treat the scoped rod-free C-G4 milestone as complete: the retarded
   clock-slice Maxwell observable, winding-labelled periodic clock, reduced
   bracket and nontrivial \(\widetilde\tau\)-evolution are exact.  Keep the
   localized apparatus observable false until the observer team supplies the
   mixed \(\epsilon_R^2\kappa\) coefficients.
6. The rank-46 STF2 graph prolongation is an exact cyclic carrier with a
   contractible complement, but its requested physical branch projector is
   now closed by the normalized subprincipal filtered obstruction.  The
   nonlinear/quantum branch-space mixing table remains false; use the unsplit
   retained cyclic causal complex.  Any future local repair must be a
   noncontractible filtered or mixed-bundle enlargement, not another
   contractible STF2 graph and not a reduced-mode projector.  Do not identify
   Berger labels automatically with the actual Einstein--Maxwell image on the
   Pleba\'nski--Hacyan background.
7. `EINSTEIN_WEYL_RELATIVE_LINEAR_TRIANGLE_V1` is now imported by committed
   content hash.  Its support-local cofiber, `H_product` equivariance,
   fixed-`N=2` endpoint maps and three distinct action forms certify residual
   equivariance and cofiber compatibility.  The relative observable functor
   remains a preflight until an actual observable pullback is constructed; it
   must not reconstruct the Einstein map or silently impose a cyclic pairing.
8. C-G1 is certified as `ABSTRACT_CYCLIC_CAUSAL_TRANSFER`, including both SDR
   lift and descent.  C-G5 now has a second non-cylinder `G2` consumer: the
   doubled adjoint-tractor mixed detour on Minkowski.  Preserve both as
   regression inputs.  The remaining causal generality gate is C-G2: state
   and verify uniform hypotheses on an open background class.  The connected
   branch-projector request is now separately closed by item 6's obstruction.
   C-G2 has reached G3 on the global conformal orbit of the cylinder with a
   transported gauge fermion.  The same zero-order conjugation is now exactly
   obstructed on unit Nariai by nonzero tractor curvature.  The differential
   translation residue has now been identified exactly as the canonical
   curvature incidence, and the shifted chain plus factorized saddle now
   close exactly.  The cyclic parent-relative mapping cylinder and SDR are
   now certified through an independent factorized variational checker.  Its
   canonical strict metric graph is now excluded at every finite differential
   order by the `partial_chi` Killing-kernel witness.  The parent-relative
   cylinder is also excluded as a metric quasi-isomorphism by a reducibility
   mismatch of at least five noncontractible directions.  The later
   curvature-corrected automorphism/parent-detour construction is the
   admissible replacement: its rank-288 carrier is symbolically obstructed,
   while the rank-310 repair, metric endpoint, all-row causal transfer and
   metric descent are exact on unit and conformal Nariai.  The active gate is
   transverse Bach-flat continuation of that rank-310 metric/parent SDR, not
   another map from the rejected eight-block cylinder.  The exact
   Kantowski--Sachs Einstein continuation of the certified transverse tangent
   is now globally obstructed: for every nonzero `0<|epsilon|<1` the sphere
   radius reaches zero with divergent Weyl curvature at finite proper time.
   Its slabwise family and formal causal variation remain exact.  This
   historical next-target statement is now discharged by the relative-open
   non-Einstein Bach-flat metric/rank-310 Volterra theorem described below;
   it does not cure the singular Einstein branch on the whole cylinder.
   The rank-310 HPL denominator is no longer part of the four-block risk: that
   formal transverse incidence obeys
   `Delta^2=(H Delta)^2=(Delta H)^2=0`, so both normalized resolvents terminate
   after one correction and the complete cyclic SDR identities hold
   coefficientwise in `Q[epsilon]`.  The exact Kantowski--Sachs family does
   not retain only those four blocks: after the declared tracefree output
   transport, a conformal-Killing symbol channel changes first at order
   `epsilon^2`, forcing `k=Kp0` and `ksharp` into the finite incidence.  The
   six-block HPL calculation is now exact: both resolvents terminate after one
   correction, all cyclic SDR identities close, and the metric endpoint
   acquires the two required quadratic terms `-kD L0D` and
   `-L0sharpD ksharpD`.  The geometric binding is now complete in invariant
   operator form: after an explicit fibre/density transport, the natural
   normal-BGG splittings, Yang--Mills detour middle, action Bach Hessian and
   adjoints populate exactly those six blocks, while the curved triangular
   graph conjugation retains the automorphism and first-splitting rows.  A
   component-expanded PBW table remains an optional regression artifact, not
   missing theorem data.  The domain is the certified common causal slab:
   after the regular change
   `b=1+epsilon y`, smooth ODE dependence gives, for every finite `T`, a
   uniformly globally hyperbolic small-parameter family on `(-T,T)` with one
   wider reference cone.  The metric endpoint is now exact on that whole
   Einstein slab family: the invariant identity
   `B_action+K T/2=L_E(L_E-2/3)/2`, with
   `L_E=Box+2 Cdot-2/3`, gives two normally hyperbolic factors without any
   parallel-Weyl assumption.  The finite cyclic SDR therefore transports the
   metric homotopy to exact advanced/retarded homotopies on all 310 rows, with
   metric descent.  C-G2 is closed on every declared common slab.  The nonzero
   family still has no whole-cylinder extension.  The formerly open
   non-Einstein Bach-flat endpoint is now closed independently: the bare
   covariant companion has scalar biwave leading symbol and no covariant
   order-three remainder, so the typed Volterra theorem applies to all four
   metric degrees with an order-at-most-two remainder.  The natural cyclic
   SDR then gives `Lambda_310,+/-=H+I Lambda_metric,+/- pi` on all 310 rows
   throughout the certified radius-`1/4` Bach-flat ADM class.  Exact
   same-bundle factorization is neither used nor claimed.  The bare
   normal-tractor parent still has no pure parent-to-metric SDR, and Hadamard
   and quantum promotions remain false.
9. The classical `CLASSICAL_MINIMAL_BV_ANTIFIELD_EXPORT_V2` is now official:
   all six minimal roles, the Bach Euler coordinate, both Noether rows,
   Lie/Weyl covariance, and the four filtration identities replay. Quantum
   repaired `_dry_run_adapter` by enforcing the declared graded window and
   independently accepted the unchanged export. The former
   `g (Lie_omega)^n` finite-closure obstruction remains a historical
   regression receipt. The next quantum gate is the minimal-BV `H^{0,4}` and
   `H^{1,4}` quotient; neither that quotient nor a QME claim follows from
   import alone.
10. Continue the deformation, Yang--Mills and boundary rails as independent
   generality tests, not prerequisites for the Berger relational-observable
   or causal-transfer gates.

The physical activation sequence and reassignment triggers are recorded in
[`universe-building-roadmap.md`](universe-building-roadmap.md).  The
`BERGER_Q2_EXPORTED`, the scoped C-G4 trigger, and the rank-46 carrier trigger
have fired.  The rank-46 projector handoff is closed by its normalized
subprincipal obstruction, and the Bach-flat four-row/rank-310 causal
generality rail is now closed on the certified relative ADM class.  The
first Bridge~1 category audit is now closed by
`CANDIDATE13_REDUCED_SOURCE_SUPPORT_LOCAL_UPGRADE_OBSTRUCTION_V1`.  The exact
candidate-13 bounded-origin and nontrivial smooth pullbacks remain valid
`REDUCED-MODE` theorems, but their declared zero- and finite-frequency
receivers cannot themselves be promoted to a support-local causal/BV
differential: nonzero global-mode
projectors enlarge support.  This does not obstruct the certified unary
support-local relative triangle, nor does it prove that every local relative
carrier is impossible.  The next admissible Bridge~1 construction must be a
genuinely new local equation-level cofiber or a larger noncontractible
mixed-bundle carrier; otherwise the candidate remains reduced-mode only.
Do not infer a local upgrade from matching mode labels or from the
finite-harmonic tangent-cone theorem.  The bare normal-tractor-parent-to-metric
crosswalk also remains fail-closed, while the observer team owns localized
apparatus completion.

The first admissible larger carrier is now selected at unary level by
`EINSTEIN_WEYL_RELATIVE_FIVE_CURRENT_DE_RHAM_CARRIER_V1`.  For every connected
stabilizer it completes the old current/divergence rows to the shifted de Rham
chain and its cyclic cotangent chain.  The five-copy complex has 160 rows and
degree ranks `(5,25,50,50,25,5)`; all 320 unary incidences, 160 odd-pairing
terms and the injective 50-row legacy row-layout embedding are portable and
exact.  The latter is deliberately not a unary-subcomplex embedding, because
the cotangent resolution continues the old terminal dual-current rows.  Its middle
equation is `d_H B_X+j_X/2=0`.  Since the product cylinder has one-dimensional
third de Rham cohomology, this is a local derived presentation of the five
zero-charge conditions without a Fourier projector.  It is intentionally
noncontractible.

`EINSTEIN_WEYL_RELATIVE_FIVE_CURRENT_DE_RHAM_Q2_V1` now closes the next scoped
arity-two gate.  For the 14 physical relative fields and their 14 Hessian
equations, the equation-density stabilizer action is derived as
`L_E=-L_F^sharp`, and the forced moment operation
`M_X(e,v)=1/2(v L_E e-e L_F v)` satisfies
`d_H C_X(u,v)=M_X(Eu,v)+M_X(Ev,u)` with zero exact PBW defect for all five
stabilizers.  Completing the two lowered tensors by cyclic rotation audits all
160 carrier rows; the 110 added potential/reducibility rows outside those
orbits have zero `q2`.  This is a 188-row physical-current interface theorem,
not yet the complete 238-row relative morphism.  The active gate is therefore
the remaining cross-incidence with the 78-row mapping cofiber.  Causal Green
data, the direct relative `f2`, candidate-13's eighteen spectral resonance
rows, arity three and quantum transfer remain fail-closed.

The first complete-carrier gate is now decided negatively and more sharply
than any coefficient search.  The 78-row mapping cofiber has padded degree
ranks `(5,20,28,19,6,0)`, while the self-dual 160-row current carrier has
degree ranks `(5,25,50,50,25,5)`.  Their fixed 238-row direct sum therefore
has ranks `(10,45,78,69,31,5)`.  A nondegenerate odd BV pairing of degree one
would pair degree `d` with degree `1-d`, but the three rank deficits are
`5`, `14` and `9`.  Consequently
`EINSTEIN_WEYL_RELATIVE_238_ROW_CYCLIC_RANK_OBSTRUCTION_V1` rules out every
cyclic `q1/q2` completion on those fixed rows, independently of coefficients
or cross-incidence.  An add-only repair needs at least 28 new rows—one
rank-minimal profile adds 9 in degree 1, 14 in degree 2 and 5 in degree 3—but
this is necessary rather than sufficient.  Noncyclic or presymplectic
238-row complexes, regradings or quotients, and larger mixed-bundle cyclic
carriers remain open.  The active bridge is therefore the bundle-type and
incidence classification of a cyclic enlargement of at least 28 rows; no
full `q2` solve should start before that carrier exists.

The canonical carrier classification is now complete at unary order.
`EINSTEIN_WEYL_RELATIVE_316_ROW_COTANGENT_COMPLETION_V1` selects

\[
\mathcal C_{316}=\mathcal C_{160,\mathrm{current}}\oplus
T^*[1]\operatorname{Cone}(\iota).
\]

The full 78-row cotangent addition has degree profile
`(6,19,28,20,5)` in degrees `-1,...,3`; the completed ranks are
`(10,51,97,97,51,10)`.  The exact factorized unary operator is
`q_current direct_sum q_C direct_sum (-q_C^sharp)`, so square-zero,
nondegeneracy, odd cyclicity and support locality follow without asking the
obstructed Einstein-to-Weyl inclusion to preserve the standard action forms.
This is deliberately a carrier-and-pairing change: it neither refutes the
generic inertia obstruction nor identifies the new cotangent pairing with the
Lee--Wald/current pairing.  The formal adjoint remains factorized rather than
PBW-expanded.  The active gate is now the complete `q2` extension or its first
normalized obstruction on these 316 rows; action-current comparison and
causal propagation remain later gates.

That first arity-two gate is now an exact scoped obstruction.
`EINSTEIN_WEYL_RELATIVE_316_BLOCK_DIAGONAL_Q2_OBSTRUCTION_V1` projects any
candidate full-domain `q2` through the block-diagonal unary carrier to the
Weyl target.  Current-valued and cotangent-valued outputs vanish under this
projection, leaving precisely the old direct-`f2` equation.  Its normalized
Taub witness remains `-54*(1+sqrt(3))/5`, so no complete full-domain relative
`q2` exists while the 316-row unary operator stays block diagonal.  The unary
cyclic carrier and scoped 188-row physical/current interface are not demoted.
The derived Taub-zero architecture is now placed at the correct Taylor
degree by
`EINSTEIN_WEYL_RELATIVE_DERIVED_TAUB_ZERO_PULLBACK_PREFLIGHT_V1`.
The relative moment map obeys
`mu_rel(0)=0=d mu_rel|_0`, so its derived zero locus does not restrict the
unary tangent complex and does not require a nonzero unary cross-incidence.
Its first canonical local equation is the arity-two current equation
`d_H B_X+j_X(u,u)/2=0` for the five stabilizers.  The 160-row current
resolution, 188-row q1/q2 interface and 316-row cyclic unary ambient carrier
already provide the typed ingredients.  The finite obstruction-module gate
is now closed by `EINSTEIN_WEYL_RELATIVE_REDUCED_TAUB_FACTORIZATION_V1`.
On `B_standard=Sym^2(H^0(q1_EM)_standard)` in the finite-harmonic
smooth-secular target category, the complete five-dimensional cokernel makes
`chi_X([S])=(1/2)<zeta_X,S>` an isomorphism and the global current replay gives
`chi([Delta2])=mu_rel,pol`.  Thus `D=A M_pol` with normalized
quotient-coordinate matrix `I5`, and `ker(D)=ker(M_pol)`, including all
cross-block pairs.  This is an abstract quotient-coordinate theorem, not a
serialized all-mode PBW source-pair matrix; the stricter bounded category
retains additional polynomial and resonant obstruction functionals.  The
support-local lift has now been typed by
`EINSTEIN_WEYL_RELATIVE_SHIFTED_CURRENT_CONE_PREFLIGHT_V1` as a degree-zero
chain map `A:K_P->C_W`.  The derived source must use `K_P[1]` inside the
mapping cone before cyclic completion.  Thus the relevant candidate is
`T*[1](Cone(iota) direct_sum K_P[1])`, still 316 rows but with degree ranks
`(5,25,56,72,72,56,25,5)` in degrees `-3,...,4`; it is not the existing
block-diagonal 316-row carrier.  No coefficient of `A` has been solved.  The
portable-current input is now closed by
`EINSTEIN_WEYL_RELATIVE_FULL_FIVE_CURRENT_PBW_EXPORT_V1`: all five
field-field currents are bound to the 14 source fields and 20 primal
three-form rows in a strict exact payload with 30,494 canonical symmetric
terms, 60,890 terms after expansion and 239 deduplicated coefficient
profiles.  The coefficient jets are complete only through order one.
`EINSTEIN_WEYL_RELATIVE_ORDER_ZERO_LIFT_OBSTRUCTION_V1` now exhausts the
unrestricted algebraic ansatz: the 480-by-310 rational top-descent system has
rank 305, and its five-dimensional kernel consists only of the Maxwell de
Rham tails.  Hence every metric output of `A^1` vanishes, while `Delta2`
contains a normalized fourth-order `g_00_star` witness; the strict incidence
`Delta2=A^1 C` with `f2=0` has no order-zero solution.  This is not a global
no-go.  Positive-order postcomposition first requires higher current
coefficient jets.  The endpoint normalization is now frozen by
`EINSTEIN_WEYL_RELATIVE_ENDPOINT_NORMALIZATION_V1`:
`A^2(P_X^4)=X^mu c_mu_star`, with positive orientation sign and no U(1) or
Weyl-identity component.  The active exact gate is the complete order-one
invariant top descent with that endpoint fixed.
`EINSTEIN_WEYL_RELATIVE_ORDER_ONE_INVARIANT_ANSATZ_V1` classifies the complete
`SO(2)` ansatz: 364 `A^1` coefficients through order one and 42 derivative
coefficients for `A^2`, hence 406 free coefficients after endpoint fixing.
The coefficient-depth prerequisite is now closed rather than assumed.
`EINSTEIN_WEYL_RELATIVE_HESSIAN_SECOND_CURRENT_INPUT_V1` rebuilds the
authoritative action coefficients deeply enough to expose 278 raw target
fifth jets and 36 raw source third jets; exact densitization and relative
subtraction prove that the corresponding unavailable relative odd-depth jets
vanish.  `EINSTEIN_WEYL_RELATIVE_FULL_FIVE_CURRENT_SECOND_JET_EXPORT_V1`
then streams the complete current through coefficient-jet order two into
twenty deterministic content-addressed chunks.  They contain 36,539 canonical
symmetric terms and 72,953 ordered terms, with independent chunkwise
coefficient replay and exact agreement with all 30,494 V1 terms.  Peak
generation RSS is 184,756 KiB, so the export does not materialize the complete
current table at once.

`EINSTEIN_WEYL_RELATIVE_ORDER_ONE_CHAIN_OBSTRUCTION_V1` now closes the exact
406-parameter solve negatively.  Globalizing the `80+284+42` primitive
isotropy bases with the four transitive stabilizer actions gives 822 nonzero
coefficient equations.  The rational matrix has rank 398 and augmented rank
399.  A two-row left-null witness compares `c_1_star partial_t` and
`c_0_star partial_x` on `P_H_3_t_theta_phi`: the unknown coefficients cancel
while the fixed endpoint evaluates to one.  Thus this complete invariant
order-one chain map is obstructed before the fifteen-row `f2` incidence can
be tested.  The next choices are order two, another current representative,
or a larger relative carrier.  None is silently promoted, and no causal or
quantum consequence is inferred.

The next-order screen is now exact rather than speculative.
`EINSTEIN_WEYL_RELATIVE_ORDER_TWO_OBSTRUCTION_SENSITIVITY_V1` derives the
coefficient descent caused by second jets of the transitive stabilizer
`J_2`.  The complete invariant homogeneous order-two `A1` symbol space has
dimension 626.  Its induced map to the one-dimensional order-one obstruction
quotient has rank one: two explicit `SO(2)`-invariant symbols have normalized
evaluations `-1` and `+1`.  Thus the two-row witness is not rigid under the
next differential order.  This authorizes the complete endpoint-normalized
order-two solve and rules out promoting the order-one result into an
all-finite-order no-go.  It does not prove that the remaining chain equations
are simultaneously consistent, does not activate `f2`, and does not yet
require a carrier enlargement or current change.

That unrestricted screen is now refined by the legal top-descent gate.
`EINSTEIN_WEYL_RELATIVE_ORDER_TWO_TOP_DESCENT_OBSTRUCTION_V1` constructs the
complete invariant top-symbol system with 626 `A1` and 86 `A2` coefficients.
Its `1056 x 712` sparse rational matrix has 2,484 nonzero entries, rank 516
and kernel dimension 196.  Appending the old obstruction-sensitivity row does
not increase the rank.  A four-row rowspace certificate,
with coefficients `(-1,-1,-1/2,+1/2)`, proves that the sensitivity vanishes
on every legal top-descent symbol.  Combining this identity with the
normalized order-one left-null evaluation proves that no endpoint-normalized
invariant chain map exists through differential order two.  The result is
scoped: order three, another endpoint/current incidence and larger relative
carriers remain open, and `f2` is still not activated.

The cubic prolongation has now been closed as a separate exact gate.
`EINSTEIN_WEYL_RELATIVE_ORDER_THREE_DESCENT_OBSTRUCTION_V1` finds invariant
order-three dimensions 1,108 for `A1` and 144 for `A2`.  All third jets of
the transitive stabilizer fields and all second source-action jets vanish at
the base point, so the direct cubic sensitivity is zero.  The only indirect
route is the relaxed quadratic equation
`L2 x2 = -y2 D3 x3`; its right-hand functional is coefficientwise zero on
all 5,600 raw cubic `A1` coefficients, even before isotropy and the cubic
top equation are imposed.  The normalized defect therefore survives every
legal correction through differential order three.  This is not an
all-finite-order no-go and says nothing about order four, a changed
endpoint/current incidence, or a larger carrier.  The next gate is a
proof-first Spencer/filtered-cohomology analysis, not a blind quartic search.

That proof-first gate now has an invariant disposition.
`EINSTEIN_WEYL_RELATIVE_ALL_ORDER_ENDPOINT_PAIRING_OBSTRUCTION_V1` pairs the
proposed equation `q_W A1 = A2 d_H` with an exact target reducibility
`zeta_Y`.  Formal adjunction and compact support force
`d g(X,Y)=0` for every current label `X` and reducibility `Y` if the frozen
diffeomorphism-only endpoint `A2(P_X^4)=X^mu c_mu_star` extends to a chain
map.  This fails for `X=Y=J_1`, since
`g(J_1,J_1)=sin(theta)^2`.  The conclusion is independent of the order of
`A1`: the fixed endpoint family is obstructed at every finite differential
order, rather than by extrapolation from orders one through three.

The same theorem locates the smallest repair.  The rotational stabilizers are
fixed-bundle Maxwell reducibilities only together with their correlated
zero-mean functions `lambda_X`, satisfying `d lambda_X+i_X F=0`.  Replacing
the endpoint by
`A2_comp(P_X^4)=X^mu c_mu_star+lambda_X lambda_cov_star` uses an existing row
and gives the constant exact Gram matrix `diag(-1,1,1,1,1)`.  It neither adds
an independent constant `U(1)` current nor enlarges the carrier.  This removes
the pairing obstruction only; the corrected chain map and `f2` remain open.

The compensated unary gate is now disposed exactly.
`EINSTEIN_WEYL_RELATIVE_COMPENSATED_ENDPOINT_CHAIN_OBSTRUCTION_V1`
restricts the corrected endpoint equation to the translation-invariant
\((t,x)\) zero mode and the `P_H_3_t_theta_phi` current component.  The
lowest coefficient matrix has rank \(3\) and augmented rank \(4\), with a
two-row left-null witness evaluating to \(-1\).  Equivalently, the remaining
normal form is

\[
\xi\notin(\tau,\xi^2)\subset\mathbb Q[\tau,\xi].
\]

This is a filtration theorem, so every finite-order product-equivariant
support-local unary lift on the existing symmetric equation carrier is
obstructed; it is not an extrapolation from the order-one through order-three
screens.  The unique minimal \(GL(4)\)-covariant tensor-symbol repair is an
added \(\Lambda^2(T^*M)\) equation module.  Its flat \(B_{01}\) component
gives

\[
u=w=0,\qquad v=b=\frac12.
\]

Only this symbol-level repair is classified.  Its cyclic dual completion and
full chain map remain absent, so relative `q2/f2` is still inactive and no
causal, observable, nonlinear, particle or quantum promotion follows.

The accepted retained-26 bikernel request is now at a typed support gate.
`BERGER_26_ROW_SMOOTH_BIKERNEL_HOMOTOPY_SUPPORT_GATE_V1` extends
\(\Lambda_{26,+}\) and \(\Lambda_{26,-}\) continuously in one kernel
variable to the standard past-compact, future-compact and time-compact smooth
LF classes.  The \(q_{26}\)-homotopy identity, same-sided support,
smoothness and graded cyclic adjoint reversal persist there.

There is no continuous extension of the certified factorization
\(\Lambda_{26,\pm}=W_{26}G_{26,\pm}\) to the full smooth compact-open
Fréchet space.  Moving a temporal cutoff on a nonzero homogeneous solution
to past or future infinity gives compact sources tending locally to zero
whose Green images tend locally to the nonzero solution.

The imported Ward artifact exports only that
\(C_{26}=[H_{26,+},q_{26}]\) is smooth.  It provides no one-sided support
profile, harmonic support or serialized smooth remainder.  Therefore
\(C_{26}\) is known to lie only in the full smooth class, where the
factorized extension is obstructed; its membership in every positive
one-sided domain remains undecided.  The active typed need is:

```text
C26_BIKERNEL_SUPPORT_PROFILE_OR_SERIALIZED_SMOOTH_REMAINDER
```

No Ward correction, BRST Hadamard covariance, positivity or quantum claim is
made by this support theorem.

The accepted same-background Wess--Zumino compensator request is now closed
for the vacuum-cylinder raw-\(D_{\rm compact}\) row.
`WESS_ZUMINO_D_CARTAN_CONTRACTION_V1` works on the unit conformal cylinder in
the declared closed-universe derived sector `P_der`.  The compensator is the
formal local Wess--Zumino field, not the Berger clock, and the generator is
raw \(D_{\rm compact}=\partial_t\), not \(K_{\rm Berger}\).  Its Weyl
component is zero, so the tau-adic augmentation ideal is \(D\)-stable.

In dressed variables the exact quartet is

\[
Q_0\tau=\omega,\qquad
Q_0\omega=0,\qquad
Q_0\omega^*=\widehat\tau^*,\qquad
Q_0\widehat\tau^*=0.
\]

With \(N\) the quartet number and
\(s(\omega)=\tau,\ s(\widehat\tau^*)=\omega^*\), the support-local homotopy
\(S=N^{-1}s\) on \(N>0\) satisfies

\[
Q_0S+SQ_0=1-\iota\pi,\qquad
[Q_0,\iota_{D,0}]_+=\mathcal L_{D,0}.
\]

The inclusion, augmentation projection, all side conditions, raw-\(D\)
equivariance, canonical odd pairing and opposite-weight cyclicity are exact.
Nonzero-weight Cartan fixtures at weights \(-2\) and \(3\) prevent the result
from being a weight-zero tautology.

The generator boundary is sharp.  For any raw generator with Weyl component
\(\sigma_D\),

\[
\pi(\mathcal L_D\tau)-\mathcal L_D(\pi\tau)=\sigma_D.
\]

Hence the same projection is exactly obstructed for Minkowski dilation
\(D_M\), where \(\sigma_D=-1\).  That row would require an explicitly
translated compensator-background orbit or another affine \(D\)-stable
target carrier.  The classical export supplies no complete renormalized
\(Q_1,\iota_{D,1},\mathcal L_{D,1}\), renormalized products or
local-insertion-to-Cartan map, so it does not classify the quantum Cartan
defect or authorize residual quantum transfer.

Escalate immediately if \(D\) is charged on the intended compact phase space,
if the clock necessarily charges it, or if the alternative quotient restores a
negative-norm one-particle class.  A counterexample is a successful result, not
a failed task.

## Required handoff

### Current eight-hour assignment (2026-07-17)

The rank-46 support-local projector rail is closed by its certified
subprincipal obstruction.  C-G2 certifies the global conformal-cylinder orbit
and the unit/conformal-Nariai rank-310 metric theorem.  The historical
eight-block normal-tractor curvature cylinder is not the metric bridge: the
exact reducibility mismatch requires at least five noncontractible new
directions.  The curvature-corrected rank-310 parent-detour mapping cone is
the selected replacement and already has a cyclic support-local SDR and
advanced/retarded all-row contraction with exact metric descent at unit and
conformal Nariai.  On the exact transverse Kantowski--Sachs Einstein branch,
every finite common slab now has both the certified four-row metric biwave
homotopy and its exact cyclic support-local transfer to all 310 rows.  The
   next optional regression is a component-expanded PBW spot check.  The
   non-Einstein Bach-flat metric endpoint and rank-310 causal bridge are now
   closed on the full certified relative ADM class by the lower-order biwave
   Volterra theorem plus the natural cyclic SDR.  The remaining crosswalk is
   narrower: no pure normal-tractor-parent-to-metric SDR is inferred.  The
branch still develops finite-time Weyl-curvature blow-up for every nonzero small parameter,
so no whole-cylinder promotion follows.  This scoped obstruction does not
demote the formal rank-310 variation and does not cover all Bach-flat
deformations.  Fixed
untransported gauges, undeclared timelike boundaries and Hadamard claims
remain false.
The full queue and
morning handoff are authoritative in
[`universe-building-roadmap.md`](universe-building-roadmap.md#coordinated-eight-hour-work-queue--2026-07-17).

### Sharp cyclic Green-homotopy transfer theorem (2026-07-20)

`GREEN_HYPERBOLIC_CYCLIC_TRANSFER_THEOREM_V1` closes the proof-first bridge
gate without changing any background producer.  For a differential cyclic
contraction `(i,p,h)`,

\[
\Lambda_{C,\pm}=h+i\Lambda_{E,\pm}p,\qquad
\Delta_C=i\Delta_Ep.
\]

The second identity promotes the causal quasi-isomorphism only as the
composition

\[
[\Delta_C]=[i_{\rm sc}][\Delta_E][p_{\rm c}]
\]

on the declared compact and spacelike-compact support complexes.  Pairing
adjointness gives the exact representative identity

\[
\langle f,\Delta_Cg\rangle_C
=\langle pf,\Delta_Epg\rangle_E.
\]

The certificate now distinguishes load-bearing hypotheses from convenient
normalizations.  Seven exact rational counterexamples isolate failures of
the chain maps, deformation identity, retraction, support locality,
inclusion/projection adjointness, endpoint adjoint reversal and fixed-sign
intertwining.  The side conditions \(h^2=hi=ph=0\) normalize a strong
retract but are not used in the one-step lifted chain identity.

Three independent rails are present: a six-dimensional exact toy, the
content-addressed 386-row unit conformal-cylinder carrier, and the curved
310-row unit-Nariai carrier with its 26-row metric endpoint.  The latter two
are hash-consumed without rerunning their producers and are never identified
across backgrounds.  The result is `LORENTZIAN-CAUSAL` only conditional on
their imported endpoint data.  It does not transfer wavefront sets, construct
a Hadamard two-point function, select a complex structure, prove positivity,
or establish a particle or quantum claim.

### Weak-background causal stability versus residual \(D\) (2026-07-20)

`WEAK_BACKGROUND_CAUSAL_VS_D_STABILITY_V1` separates two statements that had
previously been distributed across several background certificates.

The complete cyclic causal complex persists on the bounded-smooth global
conformal-cylinder orbit, throughout the radius-`1/4` relative ADM
neighbourhood of unit Nariai inside the smooth Bach-flat locus, and on every
common finite slab of the exact small Kantowski--Sachs Einstein family.  The
mechanisms are respectively pointwise BV-canonical conjugation, the
biwave--Volterra metric theorem plus the natural cyclic rank-310 SDR, and the
finite six-block HPL with a common wider causal cone.

Residual \(D\)-Cartan persistence is narrower.  It requires a declared
conformal-Killing family, the Cartan and equivariance identities on the same
target carrier, and an invertible nonzero-weight operator on the contracted
complement.  The finite-carrier gap condition is

\[
\left\|L_{D,0}^{-1}(L_{D,\epsilon}-L_{D,0})\right\|<1.
\]

The same conformally flat cylinder class already separates the verdicts.  For
\(D=\partial_t\) and a spatial conformal factor
\(\Omega_{\rm sp}=1+z/10\), the fixed tau-adic target remains
\(D\)-equivariant.  For

\[
\Omega_{\rm tm}=1+\frac1{10(1+t^2)}
\]

the causal complex still transports exactly, but the fixed augmentation has

\[
\pi{\cal L}_D\tau-{\cal L}_D\pi\tau
=D\log\Omega_{\rm tm},\qquad
D\log\Omega_{\rm tm}\big|_{t=1}=-\frac1{21}.
\]

Thus causal persistence neither supplies nor implies a residual
\(D\)-quotient.  On a broader Bach-flat or conformally Einstein family with
no declared conformal-Killing continuation, the residual row is
`NO_CERTIFIED_MAP`, not `CERTIFIED` and not mode removal.  The exact
Kantowski--Sachs branch remains slabwise causal but is not a nonzero
whole-cylinder neighbourhood.  Hadamard, nonlinear and quantum promotions
remain outside this theorem.

### Frozen Berger Cauchy-graph obstruction (2026-07-20)

`BERGER_Q26_CAUCHY_BV_CARRIER_OBSTRUCTION_V1` answers the accepted Quantum
request on the frozen normalized 104-row graph.  The complete declared class
is the set of finite-order support-local degree-\(+1\) PBW operators satisfying

\[
q_C=\operatorname{ev}_0 q_{52}^{\rm normalized}
        \operatorname{Sol}_{A_{104}}
\]

on every formal Cauchy datum.  This identity fixes \(q_C\) uniquely, so the
search closes at every finite differential order rather than at an arbitrary
ansatz cutoff.  The unique member is the imported canonical graph candidate.
The classical consumer independently reproduces its 157 nonzero square
entries and 207 nonzero evolution-commutator entries.  Hence the frozen
104-row lift class is empty; cyclic-pairing, real and graded-adjoint
subclasses are empty a fortiori.

The carrier-extension witness uses an exact three-dimensional representation
of the noncommuting Berger derivative algebra, not a nonmultiplicative scalar
symbol substitution.  Its degree-block ranks force at least five added
degree-zero rows and one added degree-\(+1\) row.  This six-row bound is
necessary only.  A sufficient extension, changed companion, changed
\(A_{104}\), Cauchy/Krein form, real structure and Hadamard state remain open.
The atlas row is therefore `OBSTRUCTED` for this frozen causal crosswalk and
`NO_CERTIFIED_MAP` in the quantum column.

### Minimal six-row Berger cyclic obstruction (2026-07-20)

`BERGER_Q26_MINIMAL_SIX_ROW_CYCLIC_OBSTRUCTION_V1` closes the first carrier
extension count forced by the frozen-graph theorem.  Exactly six added rows
can satisfy the degreewise factorization lower bound in only one way:

\[
(n_{-1},n_0,n_1,n_2)=(0,5,1,0).
\]

It changes the frozen degree ranks from \((12,40,40,12)\) to
\((12,45,41,12)\).  A nondegenerate BV odd pairing of degree one requires
\(\operatorname{rank}C^d=\operatorname{rank}C^{1-d}\); consequently every
pairing on this six-row carrier has a radical of dimension at least four.
This proves that the complete exactly-six-row cyclic class is empty before
any PBW coefficient solve, independently of finite differential order,
degree-preserving companion changes, real involutions, adjoint conventions
and invertible support-local row redefinitions.

The next necessary cyclic rank profile is \((0,5,5,0)\), so at least ten
rows must be added.  This is a lower bound, not a construction or sufficiency
claim.  The exact decoupled control preserves the inherited 1018 \(q_C\)
entries, 470 \(A_{104}\) entries, 157 square defects and 207 commutator
defects.  Noncyclic or presymplectic six-row operators, larger carriers,
Cauchy/Krein data, Hadamard states and quantum conclusions remain open.

### Berger defect/free-dual module closure (2026-07-20)

`BERGER_Q26_FINITE_ROW_MODULE_CLOSURE_LOWER_BOUND_V1` strengthens the cyclic
rank count by closing the actual square and evolution-commutator images under
\(q_C\), \(A_{104}\), and their free algebraic dual actions.  Scalar symbols
are not used.  The producer realizes the specialized Berger algebra in its
exact nine-dimensional rational spin-four harmonic-polynomial
representation over \(\mathbf F_{1009}\).  The independent verifier uses the
quotient of \(\operatorname{Sym}^4\) by the invariant quadratic ideal instead.

The producer's certified column counts are

\[
139\longrightarrow522\longrightarrow936,
\]

and its final determinant is \(384\pmod{1009}\).  The independent quotient
rail obtains a separate nonzero full determinant \(929\pmod{1009}\).  Since
the ambient dimension is \(104\cdot9=936\), the defect/free-dual closure is
the full represented carrier.  One free PBW row contributes at most nine
represented dimensions, so any free extension through which this closure
factors requires at least 104 new rows.  Its lower-bound degree profile is
the full frozen profile \((12,40,40,12)\).

This is necessary, not sufficient.  No 104-row simultaneous solution,
physical Cauchy/Krein pairing, real involution, retained solution-map
contraction or no-finite-closure theorem has yet been supplied.  Non-free or
projective module presentations are outside this bound unless explicitly
admitted and independently classified.

### Canonical 104-row doubled-cone obstruction (2026-07-20)

`BERGER_Q26_104_ROW_CANONICAL_CONE_LIFT_OBSTRUCTION_V1` tests the first
rank-saturating free-copy architecture rather than assuming the 104-row lower
bound is sufficient.  The doubled cone

\[
Q_J=\begin{pmatrix}q&-q\\q&-q\end{pmatrix}
\]

has the forced copied degree profile, preserves the old-old \(q\) block and
satisfies \(Q_J^2=0\) identically.  With old-old evolution fixed to
\(A_{104}\), its complete upper-cone evolution ansatz reduces equivariance to
\(Dq=qA\).

The valid rational one-dimensional Berger representation
\(e_0=e_1=e_2=e_3=0\), at \((\alpha_B,u,v)=(2,1,3)\), gives

\[
\operatorname{rank}q=34,\qquad
\operatorname{rank}\binom q{qA}=35,\qquad
\operatorname{rank}(q\;\;Aq)=35.
\]

Explicit normalized right- and left-null witnesses prove that neither the
evolution lift nor its free-adjoint orientation exists over the rational PBW
source algebra.  This obstruction is architecture-specific: non-cone
off-diagonal 104-row factorizations remain open, and the global 104-row lower
bound is not raised.  No accepted physical pairing, real structure, retained
contraction, Hadamard or quantum result follows.

### Canonical-cone next defect module (2026-07-20)

`BERGER_Q26_104_ROW_CONE_NEXT_DEFECT_MODULE_V1` closes the residual
evolution-lift obstruction rather than merely recording the failed equation.
In the exact rational spin-four representation, the right obstruction
\(\operatorname{Im}(qA|_{\ker q})\) has rank 27, its free-adjoint partner has
rank 70, and their combined rank is 97.  Saturation under \(q\), \(A_{104}\)
and the free-dual actions gives

\[
97\longrightarrow344\longrightarrow856\longrightarrow936,
\]

with final determinant \(411\pmod{1009}\).  An independent quotient-model
rail obtains determinant \(472\pmod{1009}\).  Thus repairing the canonical
same-profile cone regenerates a full free orbit and requires at least another
104 rows: at least 208 added rows and 312 rows total in that architecture.

This does not raise the global lower bound.  A genuinely non-cone 104-row
off-diagonal factorization may avoid this regenerated orbit and remains the
active gate.  No 312-row construction, physical pairing, retained
contraction, Hadamard or quantum theorem is claimed.

### Fully mixed cone evolution and retained-SDR obstruction (2026-07-20)

`BERGER_Q26_104_ROW_FULLY_MIXED_CONE_SDR_OBSTRUCTION_V1` corrects an
important ambiguity in the canonical-cone branch.  Although the
upper-triangular evolution equation \(Dq=qA\) is obstructed, the same
nilpotent cone admits the exact fully mixed lift

\[
Q_{\rm cone}=N\otimes q,\qquad
A_{\rm mix}=N\otimes A,\qquad
N=\begin{pmatrix}1&-1\\1&-1\end{pmatrix},\quad N^2=0.
\]

Thus \(Q_{\rm cone}^2=[A_{\rm mix},Q_{\rm cone}]=0\) identically.  This
does not yield the requested carrier.  Under the exact rational
multiplicative specialization
\(e_\mu=0\), \((\alpha_B,u,v)=(2,1,3)\), its cohomology dimensions are
\((13,57,57,13)\), whereas the retained 26-row complex has
\((1,1,1,1)\).  Any support-local PBW contraction would specialize to an
SDR and preserve cohomology, so the mismatch obstructs the retained
contraction before pairing and reality conditions.

This closes the fully mixed canonical-cone branch, not general non-cone
104-row factorizations.  The active gate is now to impose retained
cohomology from the outset in the complete non-cone block system.

### Rational non-cone nilpotence feasibility control (2026-07-20)

`BERGER_Q26_104_ROW_NONCONE_RATIONAL_NILPOTENCE_FEASIBILITY_V1`
shows that the cone cohomology obstruction is not a general rank
obstruction.  At the exact multiplicative specialization
\(e_\mu=0\), \((\alpha_B,u,v)=(2,1,3)\), a non-cone 208-row
differential keeps all three frozen old-old \(q_{\rm Cauchy}\) blocks,
has ranks

\[
(23,56,23),
\]

squares to zero exactly and has cohomology \((1,1,1,1)\).  The payload
stores all rational entries; an independent rail checks nilpotency and
the ranks modulo a different good prime.

This is deliberately a feasibility control, not a PBW operator
completion.  It proves that the next obstruction must use evolution
equivariance, cyclicity, locality/PBW lifting or a nontrivial Berger
representation.  It supplies no \(A_{104}\) lift, pairing, real
involution, retained SDR, Hadamard or quantum datum.

### Rational non-cone evolution-extension obstruction (2026-07-20)

`BERGER_Q26_104_ROW_NONCONE_EVOLUTION_EXTENSION_OBSTRUCTION_V1`
closes the evolution question for that one serialized feasibility
differential without a global 3,488-by-6,978 solve.  At the left endpoint,

\[
d_{-1}e_{16}=(e_5,0),
\]

while the old covector \(e_{25}^*\) annihilates the old projection of the
entire boundary space.  The specialized frozen evolution instead gives

\[
e_{25}^*A_{104}^{(0)}e_5=-\frac{51}{2}.
\]

Thus any putative chain identity
\(E_0d_{-1}=d_{-1}E_{-1}\), with old-old degree-zero compression fixed to
\(A_{104}^{(0)}\), yields the contradiction \(-51/2=0\).  This eliminates
all unrestricted new-row evolution blocks at once.

The obstruction is exact but candidate-specific.  It does not rule out
another 104-new-row non-cone differential constructed simultaneously with
the \(A_{104}\) equations, and it does not raise the global lower bound.
Cyclicity, reality, retained SDR, Hadamard and quantum claims remain open.

### Tau-adic vacuum-cylinder causal BV trace obstruction (2026-07-20)

`TAU_ADIC_VACUUM_CYLINDER_CAUSAL_BV_TRACE_OBSTRUCTION_V1` disposes the
requested same-background causal integration negatively in the complete
declared finite differential class.

The normalization bridge is forced by the imported certificates:

\[
\delta g=2\omega g=\sigma g,\qquad
\delta\tau=\omega=\frac{\sigma}{2}.
\]

After adding \(\tau,\widehat\tau^*\), the exact canonical dressed change
isolates

\[
u=\phi_{\rm tr}-2\tau .
\]

The classical Weyl action has identically zero Bach Hessian on this dressed
trace.  Choose compactly supported \(f\), normalized by
\(\int 4f\,{\rm vol}=1\), outside the finite fifteen-dimensional span of
global conformal-Killing factors.  Then \(fu\) is closed.  The functional

\[
\lambda_u(h,\tau)
=\int {\rm tr}_{\bar g}(h-2\tau\bar g)\,{\rm vol}
\]

annihilates compactly supported diffeomorphism boundaries by Stokes and
annihilates the convention-correct Weyl boundary pointwise, while
\(\lambda_u(fu)=1\).  For the one-sided noncompact primitives relevant to a
Green homotopy, the tracefree metric equation would force the primitive ghost
to be a global conformal Killing field, hence force \(f\) back into that
fifteen-dimensional span.  This contradicts its choice.  Composing with the
certified endpoint projection lifts the obstruction from the 30-row endpoint
to the complete strict 386-row carrier.  Therefore
\(q_0\Lambda_\pm+\Lambda_\pm q_0=1\) is impossible on the complete tau-adic
carrier.

The no-go is stable under finite-order support-local cyclic changes,
contractible nonminimal/auxiliary additions, gauge-fermion transforms and
finite differential cyclic SDR lifts.  The obstruction is an arbitrary
compact-support family, not a removable finite zero mode.  A second
independent conformal gauge generator or an order-zero dressed-trace kinetic
term can evade it only by changing the theory.  The order-\(\hbar\)
Wess--Zumino term is not classical \(Q_0\) kinetic data and has no inverse
over the formal \(\hbar\)-adic ring when the leading trace Hessian vanishes.
No full tau-adic Hadamard kernel, positivity, Lorentzian QME or particle
claim follows.

### Complex compensator local action and quartet preflight (2026-07-20)

`COMPLEX_COMPENSATOR_ACTION_QUARTET_PREFLIGHT_V1` freezes the first coherent
action-derived complex-compensator theory on the formal \(\rho\ne0\) chart.
The canonical internal symmetry is global \(U(1)\), not local \(U(1)\), so
the phase remains a physical shift field and no unexported internal gauge
ghost is hidden in the field inventory.

The complete declared two-scalar-derivative/four-curvature-derivative action
has independent radial and phase coefficients:

\[
\begin{aligned}
S_0=\int\sqrt{-g}\bigg[&
\frac{\alpha_B}{8}C^2
-\frac{\kappa_r}{2}
 \left((\nabla\rho)^2+\frac16R\rho^2\right)
-\frac{\kappa_\theta}{2}\rho^2(\nabla\theta)^2
-\frac{\lambda}{4}\rho^4\\
&+\left(\frac{\rho}{f}\right)^4
\left[\alpha_RR(\widehat g)^2+\alpha_EE_4(\widehat g)
+\alpha_PP_4(\widehat g)\right]\bigg],
\qquad
\widehat g=(\rho/f)^2g.
\end{aligned}
\]

Writing \(\rho=f e^{-\tau}\), the exact canonical cotangent change is

\[
\widehat g^*=e^{2\tau}g^*,
\qquad
\widehat\tau^*=-\rho\rho^*+2g\!\cdot\!g^*.
\]

It contracts
\((\tau,\omega,\omega^*,\widehat\tau^*)\), together with the pointwise
nonminimal cotangent doublets, and leaves a nondegenerate
\((\theta,\theta^*)\) pairing.  The reduced two-derivative coefficients are

\[
M_P^2=-\frac{\kappa_r f^2}{6},
\qquad
Z_\theta=\kappa_\theta f^2.
\]

Thus the general formal polar theory admits
\(\kappa_r<0,\kappa_\theta>0\): the radial wrong-sign direction is removed by
the Weyl quartet, while the physical phase has positive residue.  The exact
fixture \((-1,1)\) gives \(M_P^2=f^2/6\) and \(Z_\theta=f^2\).

This refinement exposes a sharp subfamily no-go.  A regular
Cartesian-analytic \(O(2)\) kinetic term forces
\(\kappa_r=\kappa_\theta=\kappa_\Phi\), hence

\[
M_P^2Z_\theta=-\frac{\kappa_\Phi^2f^4}{6}<0.
\]

It cannot make both residues positive.  The viable unequal-coefficient
theory is smooth only in the declared polar chart and is not regular at
\(\Phi=0\).

For global \(U(1)\), \(\theta\) is one massless globally charged scalar.
The radial field is absent from reduced cohomology.  An independent
\(\alpha_RR(\widehat g)^2\) coupling adds the usual scalaron on the
nondegenerate flat branch; Euler and Pontryagin remain topological and
\(\Box R\) is horizontally exact.  The choice \(\rho=f\) is a Weyl gauge
chart, not spontaneous Weyl breaking, and \(f\) is introduced rather than
dynamically generated.  The Wess--Zumino functional remains at order
\(\hbar\) and does not enter the classical Hessian.  Background solutions,
causal Green operators, Hadamard states, anomaly coefficients and quantum
claims remain open.

### Complex compensator vacuum-cylinder causal parent (2026-07-20)

`COMPLEX_COMPENSATOR_VACUUM_CYLINDER_CAUSAL_PARENT_V1` closes the first
changed-action causal gate opened by the complex-compensator preflight.  It
does not reuse the obstructed kinetic structure of the naive strict
\(\tau\)-extension.

On the unit cylinder, choose the exact formal-polar fixture

\[
\kappa_r=-1,\qquad \kappa_\theta=1,\qquad f=1,\qquad M_P^2=\frac16.
\]

Because the cylinder is not Einstein, its temporal and spatial metric
equations cannot both be solved by the conformal \(\rho^2R\) term and a
vacuum constant alone.  The unique tuning in the declared action is

\[
\alpha_R=-\frac1{144},\qquad V_0=\frac14,\qquad \lambda=1.
\]

The dressed density

\[
F(R)=\frac{R}{12}-\frac{R^2}{144}-\frac14
\]

then has the exact double root

\[
F(6)=F'(6)=0,\qquad F''(6)=-\frac1{72}.
\]

For \(\delta\widehat g=u\widehat g_{\rm bar}\),
\(\delta R=-3(\Box+2)u\), and the complete new trace Hessian is

\[
H_u=-\frac18(\Box+2)^2.
\]

If \(G_2^\pm\) are the advanced/retarded Green operators of
\(P_2=\Box+2\), the exact trace inverse is

\[
G_u^\pm=-8G_2^\pm G_2^\pm .
\]

The iterated operator preserves the same causal cone.  The phase has the
ordinary scalar block \(H_\theta=\Box\).  Consequently the former arbitrary
compact-support dressed-trace class is no longer closed:

\[
q_{\rm changed}(fu)
=-\frac18(\Box+2)^2f\,u^*.
\]

This is a kinetic repair rather than a finite zero-mode subtraction.

The complete changed carrier has 390 rows,

\[
390=356+34,
\]

with endpoint ranks \((5,12,12,5)\).  In the eight-row dressed
scalar/phase block

\[
(\sigma,u,v,\theta,u^*,v^*,\theta^*,\sigma^*)
\]

the exact differential, odd pairing, and both Green homotopies satisfy

\[
q^2=0,\qquad q\Lambda^\pm+\Lambda^\pm q=1,\qquad
(\Lambda^+)^\sharp=\Lambda^-.
\]

The certified cyclic SDR and sharp causal-transfer theorem lift this block,
the unchanged strict endpoint complement, and the 356 algebraic rows to the
full carrier.  An independent verifier reconstructs the rational double
root, trace coefficient, eight-row matrices, iterated Green normalization,
carrier ranks, dependency hashes and fail-closed boundary; ten mutation
tests reject altered tunings, a single-wave inverse, wrong homotopy signs,
carrier drift, an order-\(\hbar\) Wess--Zumino kinetic insertion, and
Hadamard/positivity/QME promotions.

This theorem concerns the changed formal \(\rho\ne0\) unequal-kinetic polar
theory, not strict pure-Weyl gravity and not the sign-obstructed
Cartesian-analytic complex scalar.  Its negative \(\alpha_R\) scalar sector
is not certified stable or positive.  Changed residual cohomology, raw
\(D\)-Cartan, Berger specialization, a compatible complex structure,
Hadamard/Feynman states, anomaly/QME, particles, scattering and unitarity
remain open.

Deliver one human-readable report and machine-readable certificates containing:

- the `G0`--`G5` generality level and exact evidence for every promotion;
- the adjacent-work convention dictionary, reproduced benchmark, and new
  consequence stated in the adjacent literature's variables;
- precise phase spaces, gauge groups, boundary conditions, and assumptions;
- the strongest attempted counterexample in each setting;
- charge densities, surface terms, integrability and flux checks;
- exact complexes, representatives, trivializations, and Gram matrices;
- content hashes and provenance for every imported/generated input;
- exact verification commands, elapsed times, and test tiers;
- explicit open fields and fail-closed claim flags;
- one verdict per setting: `D_GAUGE`, `D_CHARGED`, `SECTOR_DEPENDENT`, or
  `NOT_HAMILTONIAN`.

Every material result must carry at least one exact dependency tag:
`LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`, `REDUCED-MODE`, or
`LORENTZIAN-CAUSAL`.  A reduced-mode or Euclidean calculation is not evidence
for a Lorentzian-causal claim.

## Live handoff

The fail-closed status matrix, schema, report, and verification commands live
in [`d_quotient_classical/`](../d_quotient_classical/README.md).  Untested
settings remain `OPEN` or `NOT_TESTED`; the machine record never assigns a
scientific verdict without its declared charge evidence and dependency tags.

Cross-team consolidation is governed by
[`d_quotient_programme/`](../d_quotient_programme/README.md).  New classical
results must identify their generator, phase space, boundary conditions, and
lifecycle layer using the shared registries before the programme ledger is
regenerated.
