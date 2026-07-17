# Nonlinear team brief: do interactions preserve the \(D\)-quotient?

## Commission

Answer one question:

\[
\boxed{
\text{Is }D\text{ genuinely gauge after adding clocks, interactions, quantization, or boundaries?}
}
\]

Your task is **not** merely to calculate more vertices.  Construct the
strongest interaction that could invalidate the free \(D\)-quotient, then
compute whether the obstruction is present in the full BV/
\(L_\infty\) structure and in its transferred physical model.

The exact free contraction is input data subject to the classical import gate.
Do not reconstruct a competing contraction.  Use `pi_cl` for homological
projection, and keep the imported inclusion and homotopy conventions explicit.
The centered classes \([W_+^2]\) and \([W_-^2]\) are deformation/vertex
classes, not one-particle states.

The current low-arity transfer machinery and selected residual cubic data are
a bootstrap, not proof that the complete support-local interacting BV tensor
transfers or that the quotient is interaction-stable.

## Paper IX nonlinear signoff commission

Issue the machine-readable result
`PAPER_09_NONLINEAR_K_GENERATOR_SIGNOFF` after independently checking the
Paper IX claim table and its pinned `q2`, `q3`, Green-homotopy and Cartan
certificates. The signoff must affirm only that the certified Taylor and
Cartan operations concern

\[
K_{\rm Berger}=D-\omega R
\]

through arity three. It must explicitly reject affine raw-\(D\) Cartan,
unconditional all-orders closure, residual/BFV promotion, Hadamard data, QME
restoration and quantum claims. Publish a strict Draft 2020-12 schema,
independent verifier, source hashes and mutation guards; prose approval is not
a signoff.

### Coupled Maxwell cyclicity-repair gate

Keep the certified 54-row pure gravity--clock result separate from the later
64/36-row gravity--Maxwell overlay. The landed repair uses a common factor two
on Maxwell-output \(q_2\) together with the BV-canonical coboundary
\([q_1,F_2]\), where \(F_2(c_M)=c_M-2\iota_cA\). The independent consumer
reconstructs 1,890 full and 1,474 retained coefficients and finds zero full
and retained \(q_1q_2\) defects, zero full and retained cyclicity defects, and
zero missing, extra, or changed transfer coefficients. Causal unary flags are
preserved. The machine verdict is
`ACCEPTED_COUPLED_Q2_CYCLIC_REPAIR`.

The fail-closed receiving contract is
`quantum-weyl/transfer/schema/berger-coupled-cyclicity-repair-input-v1.schema.json`.
Its certificate retains the real obstructed baseline as a negative control
and pins the accepted repair by commit and content hash. The repaired
classical cyclic vertex is accepted and mixed \(q_3\) is unblocked. This does
not itself compute mixed \(q_3\), promote residual or quantum transfer, or
reopen the already-certified pure gravity--clock \(q_2,q_3\) and arity-three
Cartan calculation.

### Independent mixed-q3 acceptance

The committed typed gravity--Maxwell `q3` at `ba51c385` is now independently
accepted by `BERGER_MIXED_Q3_INDEPENDENT_ACCEPTANCE`. The quantum-side
consumer does not execute the classical producer: it reconstructs 1,848
unary, 150,305 gravity-`q2`, 1,890 typed mixed-`q2`, and 59,598 mixed-`q3`
PBW coefficients over exact \(\mathbb Q(\sqrt{10})\). Typed `q2` and `q3`
graded-symmetry defects vanish, as does the mixed part of
\(q_1q_3+q_2q_2\) on all 64 rows. A one-coefficient mutation produces two
exact defects.

This is a `LOCAL-ALGEBRAIC` classical-input acceptance, not a QME or quantum
result. The next nonlinear gate is retained \(\ell_3\), with both the direct
contact term \(\pi q_3(\iota,\iota,\iota)\) and the homological exchange term
built from \(q_2 S q_2\). The live typed-pairing refinement must be committed
and pinned before that transfer is evaluated.

### Extended rod–memory–Maxwell unary gate

The first apparatus gate is now sharply classified by
`BERGER_EXTENDED_ROD_MEMORY_MAXWELL_UNARY_GATE`. The existing 64-row
gravity--clock--Maxwell \(q_1\), odd pairing, and causal homotopy remain valid.
Moreover, the cyclic memory--Maxwell Hessian has a universal finite retarded
inverse, so no infinite Neumann construction is needed once the physical
profile operator is supplied.

The declared rods do not yet define an uncurved extension on the unchanged
Berger background. Their unit orthonormal spatial Jacobian and standard-sign
action give the exact stress

\[
T^R_{\hat a\hat b}=\operatorname{diag}(3/2,-1/2,-1/2,-1/2).
\]

The detector preflight discarded this as order-
\(\epsilon_R^2\) probe stress. At nonzero coupling it is therefore a metric
tadpole, so the action-derived BV Taylor expansion has \(q_0\ne0\) and cannot
be promoted as a nilpotent uncurved 78-row \(q_1\) at that fixed point. This
does not yet obstruct a nearby backreacted rod branch.

`BERGER_ROD_TADPOLE_COMPACT_SOLVABILITY_GATE` now performs the first exact
screen. In the stationary homogeneous retained metric block, the conditional
diagonal rod source is closed, has zero pairing with all three constant-mode
adjoint-kernel generators, and admits a displayed exact \(\Phi_2\). Thus
there is no constant-mode Taub obstruction. The global compact verdict
remains `INPUT_BLOCKED`: the detector input exports only local chart Cauchy
germs, not a global \(q_0^{\rm rod}\) or the full compact adjoint-kernel
projector. Those objects must be supplied before constructing a complete
background. A nonzero global pairing would require compensating clock,
coupling, or apparatus stress. Explicit local detector operators
\(B_a,B_a^*\) and memory transports remain separate later inputs. Treating
the rods as external probes does not satisfy the dynamical apparatus
commission.

The healthy Berger-clock branch now carries a certified scoped classical
verdict: the fixed-coupling lapse equation and compact averaging prove
`D_GAUGE` on `positive_berger_fixed_coupling_linearized_solutions`.  This
settles the charge classification only.  The registered minimal clock-sector
theorem now contracts exactly 8 of 34 minimal rows and retains 26 dressed-
metric/spatial-diffeomorphism rows.  The quantum import records this as
`PARTIAL_CLOCK_SECTOR_SDR_AVAILABLE`: the current handoff carries formulas and
operator fingerprints, not portable map entries, and does not compute
`D`-equivariance.  It therefore does not satisfy the ND2
`classical_contraction` artifact.  The strict receiving contract is
`quantum-weyl/transfer/schema/berger-clock-partial-sdr-portable-v1.schema.json`.
The retained/nonminimal contraction and nonlinear tensor export remain
separate required inputs.

## Shared relative-complex assignment

Use the canonical Einstein--Weyl spine in
[`universe-building-roadmap.md`](universe-building-roadmap.md).  The nonlinear
team owns `EINSTEIN_WEYL_RELATIVE_LINFINITY_THROUGH_ARITY_THREE`.

Import the Einstein team's linear map and cofiber by content hash and the
classical team's authoritative \(q_2,q_3\) tensors through the existing import
gate.  Do not rebuild either input.  On every declared setting compute the
arity-two morphism defect

\[
\Delta_2(x,y)=q_2^{\rm Weyl}(\iota x,\iota y)
-\iota q_2^{\rm Einstein}(x,y),
\]

project it to the relative cofiber, and classify it as zero, exact with an
explicit \(\iota_2\), or obstructed with a cohomology witness.  Then compute
the complete arity-three morphism identity, including the \(q_3\), mixed
\(q_2\iota_2\), and \(\iota_2q_2\) terms.  Construct \(\iota_3\) when the
defect is exact.

Resolve, rather than suppress, the bracket channels

\[
EE\to X,\qquad EX\to E\oplus X,\qquad XX\to E\oplus X,
\]

and test their cyclicity under the transported/direct relative forms.  These
channels decide whether Einstein data are closed, obstructed, or sourced by
extra modes.  Do not call the result an interacting extension until the
relevant \(L_\infty\) identities and domain conditions pass.

Use the shared row format:

| Setting | Map \(\iota\) | Cofiber | Relative pairing | \(\mathfrak O_2\) | Residual action | Observable map | Quantum lift |
|---|---|---|---|---|---|---|---|
| Explicit background/sector/boundaries | imported status + hash | imported/constructed | cyclicity verdict | computed verdict | derivation defect | dependency only | `NOT_APPLICABLE` |

The current compact-product linear input now covers the principal,
generic-axial, and generic-polar ungauged equation/Noether squares. It still
does not provide a cyclic polar BV morphism or the all-sector relative
triangle. Use the certified Plebański--Hacyan stabilizer
\(\mathbb R H\oplus\mathbb R P_x\oplus\mathfrak{so}(3)\); do not import the
vacuum-cylinder \(SO(4,2)\) quotient. Stabilizer reduction is permitted only
after constructing the common moment-map/Taub-zero sector and proving a null
subalgebra. Keep that derived-sector gate separate from nonlinear
\(q_2,q_3\) transfer.

## Work package N-D1: transfer the full low-arity structure

Write the interacting cohomological vector field and transferred operations as

\[
Q_{\mathrm{int}}=q_1+q_2+q_3+\cdots,
\qquad
\ell_1,\ell_2,\ell_3,\ldots .
\]

Import content-addressed classical Taylor tensors and compute, at minimum:

- every cubic bracket \(\ell_2\), including ghost, antifield, matter, and
  boundary-relevant components;
- the direct quartic contact contribution and all exchange-tree contributions
  to \(\ell_3\);
- the arity-three \(L_\infty\) identity and the quartic obstruction it tests;
- \(D\)-weights and particle-number changes of every nonzero component;
- cyclicity under the transported pairing, with exact sign conventions;
- dynamical/topological mixing involving \([W_+^2]\) and \([W_-^2]\).

Test the derivation identity rather than assuming it from covariance:

\[
\mathcal L_D\ell_n(x_1,\ldots,x_n)=
\sum_j\ell_n(x_1,\ldots,\mathcal L_Dx_j,\ldots,x_n).
\]

Record the full defect tensor, not only whether selected matrix elements vanish.
Use exact rational or algebraic arithmetic for canonical forms, ranks, weights,
and identities.  Do not hard-code the expected residual basis.

## Work package N-D2: construct or obstruct the interacting contraction

Seek an arity-filtered homotopy

\[
\iota_D^{\mathrm{int}}=
\iota_D+\iota_D^{(2)}+\iota_D^{(3)}+\cdots
\]

satisfying

\[
[Q_{\mathrm{int}},\iota_D^{\mathrm{int}}]=\mathcal L_D.
\]

Expand this identity by arity.  At each order:

1. compute the defect generated by lower-order data;
2. derive its consistency condition from \(Q_{\mathrm{int}}^2=0\);
3. identify the deformation/endomorphism cohomology group containing it;
4. solve for the next \(\iota_D^{(n)}\) or retain an explicit nontrivial
   obstruction representative;
5. verify compatibility with cyclicity, reality, the boundary conditions, and
   the chosen \(D\)-action.

Failure at cubic order is an immediate counterexample to interaction stability.
If a correction exists, retain it as a witness; a zero selected matrix element
is not a construction of the homotopy.

Do not use this classical nonlinear calculation to promote a quantum result.
Renormalized corrections cannot be transferred before `QME_RESTORED`.

## Work package N-D3: calculate the vacuum-instability channel

In the unreduced mode theory, enumerate the lowest cubic and quartic couplings
that could mediate positive/negative-energy pair production.  Include the
conventional Einstein and extra fourth-order/Weyl branches, ghosts, constraints,
and \(D\)-neutral composites.

For each candidate channel, transfer the vertex to physical cohomology and
compute:

- the on-shell or minimal-model amplitude;
- its \(D\)-weight and charge balance;
- whether it vanishes kinematically or algebraically;
- whether it is BRST exact, with an explicit primitive;
- whether it is absent only because a proposed external class is trivial;
- whether a \(D\)-neutral composite channel survives;
- the induced quadratic form on any regenerated physical direction.

Do not answer this rail by repeating that the free one-particle sector is zero.
The target is the transferred vertex, obstruction, or amplitude.  The strongest
counterexample is an admissible interaction that creates a nonzero physical
channel with a negative direction or makes the \(D\)-homotopy unsolvable.

## Work package N-D4: add matter early

Test, in order:

1. a conformally coupled scalar, first as ordinary matter and then as a
   relational clock;
2. Abelian gauge theory;
3. non-Abelian Yang--Mills;
4. fermions.

For each combined theory determine whether there exists:

- a cyclic strong deformation retract;
- an interacting \(D\)-Cartan homotopy;
- a causal homotopy in the declared analytic setting;
- the full residual action without an unaccounted boundary charge;
- gauge-invariant relational observables with nontrivial clock evolution;
- a positive reduced pairing on the surviving physical classes.

Separate failure of the finite residual quotient from failure of the local
causal BV complex.  A legitimate matter interaction that obstructs the
\(D\)-contraction or regenerates a negative physical class vindicates the critic.
A surviving quotient requires explicit corrected homotopies and cyclicity
witnesses, not an appeal to symmetry.

## Background and boundary challenge

Repeat the low-arity obstruction on the weakly deformed cylinder and on boundary
phase spaces when inputs exist.  If \(D\) carries a boundary charge, treat it as
a physical symmetry and test equivariance of the transferred brackets; do not
force a contracting homotopy for a charged generator.

For a background perturbation \(Q\mapsto Q+\Delta Q\), state the filtration or
norm controlling the homological perturbation series and compute the first mixed
background-interaction obstruction.  Distinguish exact Killing/conformal
Killing identities from identities valid for a generic causal complex.

## Generalization programme

Begin this rail after the current paper-improvement investigation and its
immediate certificate repairs are frozen.

Classify every result by this promotion ladder:

```text
G0  exact fixture or finite reduced-mode block
G1  complete invariant/harmonic sector on one background
G2  full support-local low-arity complex on one background
G3  uniform family of backgrounds/couplings
G4  nonlinear Cartan and stability theorem on that family
G5  causal/quantum interacting completion
```

The acyclic zero-weight Berger result is `G0`.  It validates the pipeline but
is not evidence for radiative stability.

### Work package N-G1: resonant nonzero-weight channel

Compute the action-derived channel

\[
\mathcal C_\lambda\otimes\mathcal C_{-\lambda}
\longrightarrow\mathcal C_0
\]

with every field, ghost, antifield, and pairing row required by cyclicity.
The inputs must survive unary cohomology and carry nonzero (D)-weight.  Test
whether the neutral output is Taub-forbidden, (q_1)-exact with an admissible
primitive, negative in the physical pairing, or a nontrivial source for
(iota_D^{(2)}).

The finite nonzero-weight closure no-go forbids a finite cyclic truncation as
a substitute.  Use the infinite all-weight completion or the full
support-local polydifferential complex.

### Work package N-G2: complete support-local Berger arity two — completed

Export and consume the complete gauge-fixed 54-row `q2/D` package.  Require
all output rows, derivative orders, cyclicity, local (D)-equivariance, the
arity-two (Q^2=0) identity, support-local admissibility, and an ND2 primitive
or normalized obstruction.  This is the first result allowed to support a
full interacting Berger Cartan verdict.

The receiving contract is
`quantum-weyl/transfer/schema/berger-54-row-support-local-q2-portable-v1.schema.json`.
It binds the sparse bilinear PBW tensor to the certified 54-row layout and the
existing `q1`, `D54`, `iota_cl`, `pi_cl`, `S_cl`, and cyclic-pairing hashes.
The authoritative support-local export subsequently landed and was consumed;
the old readiness receipt remains only as a historical interface receipt. The
pure gravity--clock arity-two and arity-three results are certified, while the
separate repaired 64/36 gravity--Maxwell (q_2) now supplies the input for the
next mixed (q_3) calculation.

### Work package N-G3: uniform background-interaction obstruction

Let the background and interaction vary together.  Compute the first mixed
background/arity-two obstruction on conformally flat deformations, the
Berger family, and one conformally Einstein or Bach-flat family.  Identify
the obstruction bundle or cohomology over parameter space and determine
where the primitive ceases to exist.

### Work package N-G4: particle and branch stability

Use particle-number and branch filtrations to test higher-bracket mixing of
Einstein and extra-Weyl modes, positive and negative pairing sectors,
radiative and centered classes, and clock/gravity excitations.  Compute the
first transferred vertex or certify its exact vanishing; do not reuse the
free absence of one-particle cohomology as the conclusion.

### Work package N-G5: Einstein projection and one amplitude fixture

Once a physical support-local transferred cubic tensor exists, restrict it to
the certified Einstein-sector inclusion and test whether the nonlinear source
remains tangent to that sector. Translate the projection into helicity or
twistor variables and reproduce one standard three-point or MHV fixture.
Determine whether the compact charge-sector obstruction becomes a forbidden
external state, a vanishing projected vertex, a boundary selection rule, or
has no amplitude interpretation in the tested regime. This is one bridge
calculation, not a twistor reformulation of the complex.

### External bridge N-X: test adjacent proposals on the gauge complex

For Bender--Mannheim/PT quantization and critical/log gravity, deliver:

1. an exact import and convention dictionary for the proposed metric,
   Hamiltonian, mode basis, and real form;
2. reproduction of one published oscillator or critical-gravity benchmark;
3. unary BRST/Taub descent and interacting cyclicity tests;
4. an explicit consequence stated as positivity, pseudo-Hermiticity,
   branch closure, or failure thereof in the adjacent vocabulary.

The key bridge question is not whether the Pais--Uhlenbeck oscillator admits
a positive metric, but whether that metric descends to physical gravitational
BRST/Taub cohomology and remains compatible with (q_2).  Report a positive
descent theorem or the first normalized incompatibility witness.  Treat the
authors' original scope accurately and do not present an oscillator theorem
as a claim about the full interacting gauge theory.

The direct Mannheim/PT versus Fock-BRST versus causal-BV comparison remains
deferred until a Lorentzian asymptotic state space and quantum QME disposition
exist. Follow the gate and common-fixture requirements in
[`universe-building-roadmap.md`](universe-building-roadmap.md); use
[`adjacency-bridge-note-template.md`](adjacency-bridge-note-template.md) for
the eventual external note.

## Common background matrix

Complete every cell established by your work; write `OPEN`, `NOT TESTED`, or
`NOT APPLICABLE` rather than extrapolating.

| Setting | \(D\) charge | Cartan contraction | Causal homotopy | One-particle sector | Pairing | Einstein sector |
|---|---|---|---|---|---|---|
| Vacuum cylinder | known classical target; import only after verification | free target; interacting identity open | proved free baseline | zero in stated free absolute residual complex | \(I_2\) on centered free classes; interacting open | proper free solution sector |
| Positive Berger clock | zero on the declared smooth fixed-coupling linearized phase space | pure gravity--clock cyclic \(K_{\rm Berger}\)-Cartan contraction certified through arity three; repaired coupled Maxwell \(q_2\) accepted and mixed \(q_3\) open | classical advanced/retarded 54-row chain contractions certified; compact neutral Maxwell signal is sourced and unary | no Paper-IX one-particle claim | pure gravity--clock pairing complete; repaired coupled Maxwell overlay is cyclic on full 64 and retained 36 rows | certified non-Einstein Weyl--matter control branch |
| Cylinder + scalar clock | open | first matter test | open | open | open | open |
| Cylinder + Yang--Mills | open | second matter test | open | open | open | open |
| Weakly deformed background | open | mixed obstruction open | open | open | open | open |
| Lorentzian dS/AdS | boundary-dependent | open | open | open | open | selected-sector question open |
| Asymptotically flat | physical charge expected | do not contract a charged symmetry | open | expected nonzero; compute | open | decisive |

## Priority and stop/go decisions

The complete 54-row pure gravity--clock support-local `q2` is imported and its
`q1/q2`, `D/q2`, and cyclic identities replay exactly. This sentence does not
include the noncyclic coupled Maxwell overlay described above. The bare unary
equation is not merely pending: the pinned null-symbol class proves that no finite-order
support-local `iota_D^(1)` exists on the bare 26-row complex, and the
`D`-equivariant SDR transfers that no-go to the bare 54-row extension.  Do not
form the bare arity-two source `[q2,iota_D^(1)]`.

The classical conditional causal-transfer theorem is now pinned and its
universal-algebra identities are independently replayed. Conditional on a
`D`-equivariant retained causal contraction it supplies
`iota_D,s^(1)=Lambda_s D` and the noncyclic raw binary primitive
`iota_D,s,raw^(2)=-Lambda_s[q2,iota_D,s^(1)]`.  It does not itself supply the
retained advanced/retarded Green homotopy or cyclic binary completion.

The first dressed cyclic `P34` is no longer an admissible Green endpoint: its
metric principal rank is eight rather than the required ten.  The corrected
raw BV-canonical endpoint is independently replayed and principal-compatible.
Its exact 10+2 preflight exposes a rank-one, wave-divisible order-six
Schur term. The 13-row support-local scalar-wave prolongation of that term is
now imported and exactly replayed. Its paired 36-row cyclic analytic
realization, source/solution graph SDRs, and formal adjoint are also imported;
the added `y,y*` pair does not alter the authoritative 34-row BV cohomology.
The authoritative lower-by-two theorem from classical commit `db099319` is
now pinned and independently replayed: `A10=Box_2^2+V_2` with
`ord(V_2)<=2`, and all 92 nonzero quadratic-symbol entries obstruct a
factorization fixing one canonical rough-wave factor. The downstream exact
lower-order screen further rules out a factorization into two
scalar-principal second-order factors sharing the same invariant connection:
the quadratic remainder has normalized dual witness
`-u^-2 [p0 p3] R2[h00,h03]=1`.  This is not a general Green no-go. Unequal
subprincipal factors, auxiliary/first-order reductions, and a causal
Volterra/Levi resolvent remain live.
The subsequent exact Douglis audit changes the endpoint gate more sharply:
the full `L13` determinant contains the genuine extra characteristic
`p0^2=2|p_spatial|^2`, of speed `sqrt(2)`. Thus a background-metric-causal
inverse on arbitrary 13-row sources is impossible. This is not physical
superluminality: the extra cone lies in the acyclic clock/graph incidence.
The active PDE gate is now `BERGER_HYBRID_RETAINED_CAUSAL_CHAIN_HOMOTOPY`:
contract that incidence support-locally first, then construct the retained
causal chain homotopy.

1. Choose and certify a residual/BFV, derived zero-charge, or causal Green
   extension of the complex.  The extension must state its rows, support
   category, pairing, and replacement unary Cartan identity explicitly.
2. On the causal route, construct
   `BERGER_HYBRID_RETAINED_CAUSAL_CHAIN_HOMOTOPY`. Do not require a
   metric-causal inverse of the complete `L13` on arbitrary sources; that
   architecture is exactly obstructed. Apply the certified support-local
   clock/graph contraction first, construct the causal homotopy on retained
   sources, prove cyclic adjointness, and lift it through the certified
   54-to-26 contraction.
3. Transfer the full `ell2` on the chosen extension and only then form the
   corrected arity-two Cartan source.
4. Solve for `iota_D^(2)` on that extension or retain its normalized
   obstruction witness.
5. Compute \(\ell_3\), the quartic identity, and the first resonant
   \(+\lambda,-\lambda\to0\) instability channel.
6. Add Yang--Mills only after the scalar-clock rail is understood.

The Green assignment is a temporary parallelization and does not promote an
interacting claim.  The handback and later physical activation gates are in
[`universe-building-roadmap.md`](universe-building-roadmap.md).

Escalate immediately if the cubic defect is nontrivial, if cyclicity fails, or
if a negative physical channel survives transfer.  A no-go certificate is a
successful result.

## Required handoff

Deliver one human-readable report and machine-readable certificates containing:

- the `G0`--`G5` generality level and exact evidence for every promotion;
- the adjacent-work convention dictionary, reproduced benchmark, and the
  BRST/(q_2) consequence in the adjacent proposal's own observables;
- hashes and independent verification of all classical imported tensors;
- complete low-arity tensors, degrees, \(D\)-weights, signs, and provenance;
- \(L_\infty\), derivation, cyclicity, and strong-deformation-retract checks;
- corrected \(\iota_D^{(n)}\) witnesses or explicit obstruction classes;
- unreduced candidate instability vertices and their transferred amplitudes;
- relational-clock and matter-coupling results;
- exact commands, elapsed times, applicable test tiers, and skipped-tier reasons;
- open inputs and fail-closed claim flags;
- one verdict per setting: `INTERACTING_CARTAN_EXISTS`,
  `INTERACTING_CARTAN_OBSTRUCTED`, canonical `D_CHARGED`, or
  `INPUT_GATE_BLOCKED`.

`D_CHARGED_NO_QUOTIENT` is a route description, not an additional scientific
verdict.  A total-`D` handoff must satisfy
`quantum-weyl/transfer/schema/total-d-disposition-v1.schema.json`; a physical
ND2 run additionally binds its phase space, boundary-condition hash,
classical commit, dependency-tag union, and source hashes.

Every result must carry at least one exact dependency tag:
`LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`, `REDUCED-MODE`, or
`LORENTZIAN-CAUSAL`.  Reduced-mode transfer does not establish causal
interaction stability.

## Cross-team contribution contract

Submit new results through
[`d_quotient_programme/`](../d_quotient_programme/README.md).  Import the
classical generator, phase-space, clock, and tensor definitions by content
hash; do not rebuild a competing scalar-clock setting or promote a free
sector verdict to an interacting Cartan theorem.
