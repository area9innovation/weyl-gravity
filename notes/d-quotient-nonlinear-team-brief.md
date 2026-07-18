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
result.

### Independent retained mixed-ell3 acceptance

The retained typed gravity--Maxwell `ell3` is now independently accepted by
`BERGER_RETAINED_MIXED_ELL3_INDEPENDENT_ACCEPTANCE`, pinned to classical
commit `41c58d20`. The quantum-side exact \(\mathbb Q(\sqrt{10})\) consumer
matches all 25,950 direct contact coefficients, with 18 nonzero retained
output rows. It also reconstructs the 96 gravity and 12 mixed second-inclusion
coefficients and evaluates the homological \(q_2 S q_2\) exchange rather than
inferring it from a support summary.

The gravity-outer/mixed-inner exchange channel has 144 raw coefficient pairs,
324 signed unshuffle contributions and 342 canonical full-complex PBW
coefficients. None survives the retained output projection. The other two
exchange channels have no raw pairs, so all three retained exchange sectors
vanish exactly. This sharpens the producer explanation: the first channel is
not absent in the full complex; it is killed by retained projection. All 36
relative arity-three rows close, and a localized one-coefficient mutation
produces two exact defects.

The resulting bracket is nontrivial: it contains 7,614 gravity-output terms
with two Maxwell inputs and 18,336 Maxwell-output terms with one Maxwell
input. Thus a genuine retained gravity--light interaction has been established.

Its physical quartic cyclicity is now independently replayed over exact
\(\mathbb Q(\sqrt{10})\): all 25,662 physical coefficients close with zero
defects, while a Maxwell pairing-weight mutation produces 17,108 defects on
14 rows. The remaining 288 coefficients are the ghost/antifield completion;
their cyclic transpose is still imported from the classical typed-transfer
theorem, so full retained BV cyclicity remains open.

The next nonlinear gate is the residual projection and mixing table. Project
the dynamical carrier onto the Einstein-like and extra-Weyl gravity branches
plus the Maxwell branch. Separately compute the action on the even dynamical
and odd topological deformation/vertex basis, its rank-one Euler--Lagrange
map, and the topological transgression witness. The odd topological class is
not a third particle branch. No unary kinetic operator, QME lifecycle state or
quantum claim is promoted.

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

The later observer-owned
`BERGER_84_ROW_OBSERVER_APPARATUS_HANDOFF` is now the authoritative forward
interface and supersedes the three-shared-rod/78-row assumptions for new
construction without invalidating the historical obstruction above.  It
imports six global detector-indexed rods and exact second-order metric
primitives, fixes the ordered 84-row carrier and odd pairing, realizes
`m_a,p_a` as bulk clock-transported scalars, separates `epsilon_R^2` from the
readout coupling `kappa`, and freezes the profile only through its exact
two-jet (`q1,q2,q3`).  The emitter currents remain external.  The next
apparatus gate is therefore the shifted-background 84-row unary, pairing, and
advanced/retarded Green complex; do not reconstruct a 78-row extension.

The observer-owned `BERGER_84_ROW_UNARY_PAIRING_GREEN_GATE` has now discharged
the part of that gate which does not require new gravity--rod coefficients.
It proves the exact two-detector memory--Maxwell `q1` blocks, unary cyclicity,
and the finite two-channel advanced/retarded inverse, including the two
`kappa^2` cross-detector Green terms.  This yields a certified 72-row causal
subcomplex on rows `0..63,70..73,80..83`.  Do not append six diagonal scalar
waves and call the result the 84-row BV complex: the global rods are
nonconstant, so `Gamma_R(xi)=Lie_xi Rbar` is nonzero.  The nonlinear handoff
now requested is content-addressed `Gamma_R`, its odd-pairing adjoint,
`K_Rh`, `K_hR`, the shifted metric Hessian `Delta_K_hh`, and a coupled causal
witness `W_rod`, with coefficientwise nilpotency and cyclicity receipts.

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
pure gravity--clock arity-two and arity-three results are certified.  The
repaired 64/36 gravity--Maxwell \(q_2\), typed mixed \(q_3\), transferred
\(\ell_3\), exchange audit, and full retained BV cyclicity have also landed.
Their remaining gate is invariant physical meaning, not another replay of the
same tensors.

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

The immediate N-G4 target is the invariant disposition of the landed retained
mixed \(\ell_3\).  On the unsplit cyclic 36-row carrier, construct the complete
admissible cyclic, support-local, jet-bounded redefinition complex for
\((F_2,F_3)\) and decide whether

\[
 \ell_3^{\rm mixed}\in
 \operatorname{im}\bigl([\ell_1,F_3]+[\ell_2,F_2]\bigr).
\]

Return an explicit trivializing redefinition or a normalized dual witness
annihilating every admissible redefinition while detecting \(\ell_3\).  This
test does not require inventing Einstein-like and extra-Weyl labels on the
unsplit carrier.  The exact cyclic rank-46 STF2 graph carrier is now available,
but its added complement is contractible and no branch projector has yet been
certified.  A branch-resolved mixing table begins only after a support-local
projector or another exact filtered/mapping-cylinder splitting is imported and
accepted.

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
| Positive Berger clock | zero on the declared smooth fixed-coupling linearized phase space | pure gravity--clock cyclic \(K_{\rm Berger}\)-Cartan contraction certified through arity three; repaired coupled Maxwell \(q_2\), typed mixed \(q_3\), retained \(\ell_3\), and full retained BV cyclicity are exact | classical advanced/retarded 54-row chain contractions certified; compact neutral Maxwell signal is sourced and unary | no Paper-IX one-particle claim | typed gravity--clock--Maxwell pairing is cyclic on the declared full and retained carriers | certified non-Einstein Weyl--matter control branch; canonical support-local same-bundle branch projector is obstructed on retained 36 rows |
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
The subsequent exact Douglis audit changes the raw-endpoint gate more sharply:
the full `L13` determinant contains the genuine extra characteristic
`p0^2=2|p_spatial|^2`, of speed `sqrt(2)`. Thus a background-metric-causal
inverse on arbitrary 13-row sources is impossible. This is not physical
superluminality: the extra cone lies in the acyclic clock/graph incidence.
The required hybrid route is already certified by
`BERGER_54_ROW_CAUSAL_GREEN_HOMOTOPY_V2`.  Its exact formula
`Lambda54,+/-=S_cl+iota_cl Lambda26,+/- pi_cl` first contracts all 28 acyclic
clock/nonminimal rows by the support-local cyclic SDR and then propagates the
retained 26-row complex with the typed Volterra/biwave homotopy.  Thus every
54-row unary chain-homotopy identity and same-sided support statement is
certified without inverting the raw `L13` endpoint on arbitrary sources.  The
raw extra-cone no-go and the hybrid theorem concern different architectures
and are simultaneously valid.  This lifecycle is already recorded as
causal `CERTIFIED` in atlas row
`classical.berger.retained_gravity_clock_maxwell`; the nonlinear atlas keeps
interacting causal products open because a unary chain homotopy does not
construct them.

The rank-46 branch input has also advanced.  The exact certificate
`BERGER_RETAINED_46_STF2_PHYSICAL_HELICITY_FILTERED_QUOTIENT_V1` derives the
rank-two transverse-traceless projective polarization module inside the full
six-dimensional degree-zero Berger null-symbol cohomology.  Its canonical
transpose supplies the paired degree-one module and the retained BV pairing
is nondegenerate.  Tensoring with the repeated-wave dual-number algebra gives
the rank-four generalized-wave module.  This closes the former unproved
helicity-rank assertion.

The filtered `V_2` gate has now also returned an exact obstruction.  After
allowing every principal gauge change, Hessian boundary, and physical-equation
representative at `zeta=(1,1,0,0)`, the normalized left-null witness evaluates
on the plus/cross columns as `(1,0)`.  The cross polarization lifts with
coefficient `71/40`, but the plus polarization does not.  Hence the declared
rank-46 contractible graph carrier admits no support-local branch projector
with that principal physical anchor.  This is not a global all-carrier no-go:
the live alternatives are the unsplit retained complex, a noncontractible or
mixed-bundle filtered enlargement, or an explicitly `REDUCED-MODE` nonlocal
split.

The first N-G4 filtration page has now closed exactly.  The certificate
`BERGER_RETAINED_MIXED_ELL3_CONSTANT_FIELD_REDEFINITION_V1` lowers the
unsplit physical action with the typed pairing and sets every PBW derivative
word to zero.  On the complete 550-dimensional
`Sym^2(G*) tensor Sym^2(A*)` sector, the 2,690-column matter-parity-preserving
cyclic cotangent-lift coboundary map has exact rank 550 and zero cokernel.  A
51-coefficient `F3` primitive reconstructs all 63 nonzero constant-field
coordinates of the landed mixed `ell3`.  Consequently the two zero-derivative
Paper 11 evaluations remain valid representative witnesses but cannot be
nonremovability witnesses.  This is a `G0`, `LOCAL-ALGEBRAIC` result: the
positive-jet `F2,F3` complex, its higher-order cancellation conditions, and
the operation on `ell1` cohomology remain open.

The first positive-jet page has now also closed exactly.  The certificate
`BERGER_RETAINED_MIXED_ELL3_FIRST_JET_REDEFINITION_V1` solves the coupled
system `A*x0=t0`, `B_a*x0+C*y_a=t1_a` without freezing the earlier 51-term
primitive: all 2,690 zero-jet coefficients remain available in the Schur
solve.  Exact first-order integration by parts gives 1,330 coordinates per
PBW axis.  The positive-jet map has rank 1,327 and cokernel dimension three;
the resulting `562 x 2690` Schur system has rank 557 and accepts the target.
An explicit primitive uses 51 zero-jet coefficients and positive-jet counts
`(43,94,95,108)` on the four axes.  Thus neither jet order zero nor one of the
degree-zero physical action supplies a nonremovability witness.  This remains
`G0` and `LOCAL-ALGEBRAIC`: the 288 ghost/antifield coefficients and total jet
order two are the next honest gate.

The full-BV consumer now has a frozen Taylor-level sign prerequisite.
`BERGER_SUPER_COTANGENT_REDEFINITION_CONVENTION_V1` regenerates the landed
64-row Maxwell covariant-ghost shear from the generic degree-zero formula
`F^(i*)=-(-1)^parity(i) F^B`, with the dual output inserted before graded
completion.  All rows agree exactly; suppressing the odd-input sign fails on
the four ghost-dual rows 49--52.  This certificate does not decide the
redefinition problem.  It exists to prevent the full-BV solver from extending
the degree-zero physical absolute-weight shortcut into the suspended Darboux
sectors, which is not an admissible convention.

The next zero-PBW full-BV page has now returned a scoped obstruction.
`BERGER_RETAINED_MIXED_ELL3_ZERO_JET_FULL_BV_REDEFINITION_V1` uses 810
physical-base `F2` and 4,160 physical-base `F3` coefficients with their typed
super-cotangent partners.  The two-Maxwell matrix is `4814 x 4970`; its
target-connected `477 x 286` block has rank 129 and augmented rank 130.  A
single normalized dual coordinate detects the defect: output 23 on inputs
`(1,30,35)` has target coefficient `3 sqrt(10)/10`, every admitted column
vanishes there, and dual weight `sqrt(10)/3` evaluates to one.  This is a
ghost/antifield-completion obstruction: the physical projection remains
compatible.  The exact PBW augmentation audit checks all positive words
through length six and proves that first/second-jet maps cannot hit this
zero-word witness.  It is not yet the N-G4 verdict because nonlinear
ghost-coordinate redefinitions were not admitted.  The earlier provisional
obstruction from an absolute-weight or untyped zero-jet matrix is superseded
and must not be cited.

The scoped obstruction has now supplied its missing carrier and is superseded
as a zero-page verdict.  `BERGER_RETAINED_MIXED_ELL3_ZERO_JET_GHOST_SHEAR_COMPLETION_V1`
adds exactly the three retained components of the already-certified typed
Maxwell covariant-ghost shear.  The target-connected matrix becomes
`477 x 289` with rank and augmented rank both 132.  An explicit 67-coefficient
primitive, entirely in `F2`, includes the three ghost-shear base maps with
coefficient `-1` and reconstructs all 186 canonical two-Maxwell zero-word BV
coefficients with zero missing, extra, or changed entries.  Thus the complete
zero-PBW full-BV page is trivial in the extended certified ansatz; the
physical-only witness was a useful smallest-missing-carrier diagnostic, not a
deformation obstruction.

The total-order-two consumer and source are now frozen separately from the
pending solve. `BERGER_RETAINED_MIXED_ELL3_SECOND_JET_SOURCE_V1` represents
mixed quartic densities by their exact variational Euler images after Berger
PBW reduction. It reproduces the zero and first physical pages with zero
residual and kills 4 first plus 16 second total-derivative mutations. The
frozen lower primitive leaves 724 order-one and 5,212 order-two density terms,
whose Euler image has 1,221 and 8,822 coordinates respectively. The complete
symmetric physical second-input-jet ansatz has 155,640 labels (with the
first-jet enumeration independently reproducing `4 x 6560 = 26240`). This is
`SOURCE_COMPUTED_SOLVE_PENDING`, not an obstruction: the affine second-jet
image solve and positive-jet full-BV lift remain required.

The physical affine solve has now closed exactly.
`BERGER_RETAINED_MIXED_ELL3_SECOND_JET_EXACT_PRIMITIVE_V1` reduces the mixed
order-two local-functional space to 39,170 independent Euler coordinates and
exports a 4,276-coefficient homogeneous correction to the frozen lower
primitive. All 550 zero-page equations, all four 1,330-row first-page blocks,
and all 10,043 nonzero order-two Euler target coordinates replay exactly with
zero missing, extra, or changed terms. Thus the complete degree-zero physical
action through summed differential order two is trivializable. This is not
the final cyclic deformation verdict: the positive-jet ghost/antifield lift
is now the only remaining N-G4 gate.

The derivative-aware cotangent convention for that gate is now frozen.
`BERGER_POSITIVE_JET_SUPER_COTANGENT_REDEFINITION_CONVENTION_V1` transposes
each differentiated input by its formal adjoint over the output-antifield and
remaining-input product before exact Berger PBW reduction. Its zero-word
restriction reproduces all 934 F2 and 5,050 F3 base labels of the certified
algebraic convention with zero defects. An odd first-derivative sign mutation
changes the dual carrier, and the noncommuting word `(2,1)` retains a genuine
order-one commutator tail. This closes a convention prerequisite only: the
order-two full-BV coboundary replay and its primitive/obstruction verdict are
still the active N-G4 gate.

The active N-G4 gate is now terminally closed by
`BERGER_RETAINED_MIXED_ELL3_POSITIVE_JET_FULL_BV_OBSTRUCTION_V1`.
The solve couples all 5,984 zero-page base directions rather than freezing
the earlier 67-term primitive; this is essential because an individually
zero `F2` direction cancels the first provisional coordinate witness.  After
that kernel freedom is included, a normalized 22-row functional over
`Q(sqrt(10))` annihilates every zero-page column and all 14,998 admissible
first-jet columns on each of four axes, while evaluating to one on the
first-page residual.  The obstruction therefore occurs on the first
associated-graded page of the summed pre-reduction PBW filtration.  No
nonnegative filtered order-two or higher profile can repair it.

This supplies the promised invariant strengthening, with an exact boundary:
the landed mixed `ell3` is not removable by the declared derivative-aware
cyclic super-cotangent `F2/F3` transformations.  The displayed functional,
its 22 coordinates, and the frozen SDR basis remain representative-dependent;
the nonzero obstruction class and its zero/nonzero verdict are invariant only
within that declared filtered cyclic equivalence relation.  Residual
cohomology, SDR-independent deformation cohomology, Einstein-like versus
extra-Weyl support, topological inertness, and physical norm remain open.

`NONLINEAR_SOURCE_TRANSFER_TANGENT_CONE_DICTIONARY_V1` now fixes the adjacent
source conventions.  With factorial Taylor tensors,

\[
D^2E_{\bar\Phi}(u,u)=q_2(u,u),\qquad
q_1v=-\frac12q_2(u,u)
\]

for `Phi=barPhi+epsilon*u+epsilon^2*v`, while
`ell2=pi_cl q2(iota,iota)`, `I2=-S q2(iota,iota)`, and `ell3` is the direct
`q3` term plus the complete shuffled `q2(I2,iota)` exchange.  Thus `ell2` is
the quadratic tangent-cone source; `ell3` belongs to the next Taylor order
and quartic deformation problem.

For an admissible field/equation isomorphism preserving the harmonic carrier,
boundaries, Noether/gauge reduction and correction class `C`, the complete
obstruction map transforms as

\[
\mathcal O'_{\mathcal C'}(u)
=U_{\rm coker}\,\mathcal O_{\mathcal C}(Tu),
\qquad
\mathcal Z_2^{\mathcal C'}=T^{-1}\mathcal Z_2^{\mathcal C}.
\]

The `q1 F2` Hessian-coordinate term is cokernel-exact.  Changing from
bounded/quasiperiodic to smooth-secular or causal/retarded corrections changes
the operator image and is therefore a change of theorem, not a coordinate
redefinition.

The generated claims ledger is
`d_quotient_classical/atlas/nonlinear-atlas-fragment.json`.  It records the
full-BV filtered obstruction, the abstract tangent-cone naturality theorem,
and a fail-closed retained-to-residual branch crosswalk.  Until a new
noncontractible/mixed-bundle or explicitly `REDUCED-MODE` branch map lands,
all Einstein-like/extra-Weyl/topological mode-pair source rows remain
`NO_CERTIFIED_MAP`; no local PBW row is silently identified with a harmonic
mode.

The ledger also imports one independently certified mode-pair source on the
different compact product background: the positive-frequency axial/polar
Einstein minus-branch pair has a nonzero axial `ell=2,m=0,k=0` sum-frequency
source, but that selected four-row block is off shell and admits an exact
second-order correction.  This is an explicit `D^2E=q2` source/image verdict,
not a Berger crosswalk, residual operation, or cyclic `L_infinity` field
redefinition.  Its causal and final-cohomology images remain fail-closed.

### Active bridge

The active nonlinear bridge is bridge 2, **invariant interaction to physical
branches**.  Its activation gate is bridge 1: an admissible branch map on the
same fixed rational Berger background, with explicit carrier crosswalk,
chain/cohomology maps, pairing transport, gauge/nondynamical disposition and
`K_Berger` equivariance.  The fail-closed importer is
`BERGER_MIXED_ELL3_BRANCH_PROJECTION_IMPORTER_PREFLIGHT_V1`; it accepts a
support-local mixed-bundle map, noncontractible cofiber, or explicitly tagged
`REDUCED-MODE` nonlocal map and rejects background-name matching.  The input
contract requires the complete atlas mode scope and typed, schema-validated,
content-addressed evidence
roles for the carrier crosswalk, chain map, inclusion/projection/cofiber,
pairing transport, gauge/nondynamical disposition, `K_Berger` equivariance,
cohomology map and independent verifier.  Its independent verifier is
activation-neutral: it accepts either the current fail-closed missing state or
a future imported candidate after exact replay, rather than rejecting the
scientific handoff merely because it arrived.  No input is present, so the
corresponding atlas row
`nonlinear.berger.bridge2.invariant_interaction_to_physical_branches` remains
`NO_CERTIFIED_MAP` on every axis.  Once activated, use the landed
`D^2E`--`q2`--`ell_n` dictionary to decide cohomology survival, cyclic
deformation nontriviality, or removal by a displayed admissible redefinition.
The generated row is activation-sensitive: after a valid import it copies the
certified mode scope, marks pairing/branch-carrier readiness `CERTIFIED`, and
opens only the still-uncomputed nonlinear dispositions.  Causal status opens
only for an explicitly `LORENTZIAN-CAUSAL` input; observational and quantum
axes remain `NO_CERTIFIED_MAP`.
The certified filtered-cyclic `ell3` obstruction is preserved and `q4` is not
authorized.

The compact-product
`EINSTEIN_WEYL_RELATIVE_BRANCH_DICTIONARY_V1` is now imported by hash into
the nonlinear atlas.  It supplies sectoral same-background generic axial and
polar cofibers and action-derived pairings, but its own global Bridge-1 flag is
false: polar cyclic BV compatibility, exceptional/global cofibers and final
endpoints remain open.  Accordingly these rows are usable as scoped branch
labels, not as the all-sector relative triangle and never as a Berger
crosswalk.  The earlier `a,b,d` crossed with `ell=2` extra-shell source matrix
has now been completed by the exact twist position and velocity columns.  In
the declared `k=0` homogeneous/twist carrier, the twist-position resonance map
has rank two and the twist-velocity map has pointwise rank four for every real
time; a non-axisymmetric Clebsch--Gordan fixture fixes every `m`.  The resulting
common-zero calculation is now also complete in this declared nonzero-extra
carrier.  Exact polynomial elimination forces `a=b=d=0`; after rotating the
nonzero twist velocity to one axis, the residual rank stratification and
rotation moment map force the extra `ell=2` tensor and twist position to share
that axis.  Thus the complete locus is the aligned `SO(3)` orbit
`beta^2=Q_e^2/2+(2/3)X`, with no additional off-axis branch.  The bounded or
finite-quasiperiodic second-order problem is now obstructed at every nonzero
point of this orbit.  The balance forces `B != 0`, while the zero-frequency
polar `L=2` metric-equation source contains the exact quadratic coefficient
`-7*B^2*t^2`; the stationary Weyl--Maxwell operator maps bounded
finite-quasiperiodic corrections (with bounded derivatives through its order)
to bounded sources, so it cannot cancel this growth.  This is a
correction-class-specific no-go.  Smooth exponential-polynomial correction
is already constructive on the decisive twist-self subblock: the exact full
polar `L=2` primitive is
`A_t2=-5*B^2/6`, `B2=0`,
`C_t2=5*B^2/6-2*(A+B*t)^2/3`, and `U2=-7*B^2/36`, with all eight projected
remainders zero.  Thus the obstruction is genuinely caused by the bounded
correction class, not by failure of the linearized equations.  The complete
global--extra mixed-channel assembly remains a separate gate until its
certificate is committed, and the causal/retarded class remains
`NO_CERTIFIED_MAP`.
Neither source handoff activates a cyclic Bridge 2 calculation.  The
axial--polar source uses the polar leg whose
fixed identity cyclic compatibility is obstructed and whose corrected
nonidentity/homotopy alternative remains open, while the homogeneous/twist
source uses global legs whose all-BV off-shell cyclic relative map is absent.
The exceptional `ell=1,k=0` update now supplies explicit CRT solution
projectors and a nonradical extra Gram matrix `diag(16,3)`, but remains
`ONSHELL_MAP_ONLY`; its off-shell ghost--field--equation--identity map and
nonzero-`k` cofiber are still absent.  It therefore strengthens the atlas
without activating cyclic Bridge 2.

The compact-product Bridge-2 receiver is now frozen as
`EINSTEIN_WEYL_RELATIVE_LINFINITY_THROUGH_ARITY_THREE_PREFLIGHT_V1`, with
atlas row
`nonlinear.product.bridge2.relative_linfinity_through_arity_three_preflight`.
Its activation gate is exactly three same-background inputs: the full
off-shell `EINSTEIN_WEYL_RELATIVE_LINEAR_TRIANGLE_V1`, the complete
`EINSTEIN_MAXWELL_PRODUCT_LINFINITY_THROUGH_ARITY_THREE_V1`, and the complete
`WEYL_MAXWELL_PRODUCT_LINFINITY_THROUGH_ARITY_THREE_V1`.  All three are
currently `MISSING`, so every atlas axis is `NO_CERTIFIED_MAP`.  The receiver
publishes the triangle handoff contract at
`d_quotient_classical/schema/relative-linfinity-triangle-input-v1.schema.json`;
it requires content-addressed source/target `q1`, inclusion,
projection-or-cofiber and pairing-or-current artifacts rather than accepting
status flags alone.  It also requires hashed artifacts for both the generic
fixed-identity cyclic obstruction and its corrected resolution, plus an
explicit nonidentity, pairing-improvement or declared chain-homotopy
resolution kind.  A corrected-nonidentity resolution must not reuse the
identity map; a pairing improvement or declared chain homotopy may retain it
only explicitly and with its resolution artifact pinned.  Thus the obstructed
inclusion cannot be silently relabelled as the full cyclic triangle.  The receiver
validates full-BV rows, support locality,
cyclic pairing, the arity-two and
arity-three identities, `H_product` equivariance, exact artifact hashes and
an independent-verifier flag.  It rejects Berger-background payloads and
does not accept sectoral/on-shell branch maps or selected source fixtures as
scientific substitutes.  Once all inputs pass, compute `Delta2`, its exact
primitive or normalized cofiber witness, the complete arity-three morphism
defect, and then the induced cohomology/deformation verdict.  The existing
Berger filtered-cyclic `ell3` obstruction remains untouched and `q4` remains
unauthorized.

The generic Bridge-1 identity route has since closed negatively and is now a
separate fail-closed atlas row,
`nonlinear.product.bridge1.generic_identity_cyclic_compatibility_obstruction`.
`EINSTEIN_WEYL_GENERIC_IDENTITY_CYCLIC_OBSTRUCTION_V1` proves on every
physical `ell>=2` fibre and allowed compact momentum that the induced
solution-pairing defect `D=R-I` is nonzero and rank two in both axial and polar
parities.  Hence the certified polynomial chain maps cannot be strict cyclic
maps while their field inclusion is fixed to the physical identity.  This is
not an obstruction to a corrected nonidentity symplectic identification, a
pairing improvement, or a cyclic morphism up to a declared chain homotopy.
Those alternatives, the exceptional/global off-shell maps and final residual
descent remain open; Bridge 1 and the relative nonlinear receiver therefore
remain inactive.

1. Treat the repaired mixed \(q_2\), typed \(q_3\), retained \(\ell_3\),
   exchange audit, and full retained BV cyclicity as complete on their pinned
   carriers.  Do not recompute them as if they were open.
2. Treat N-G4 as closed by the first-page full-BV dual obstruction.  Do not
   enlarge the calculation to `q4` or reinterpret the exact physical-action
   primitive as a full-BV trivialization.  The next interaction calculation
   is the branch/mode-pair quadratic-source table, but it remains
   `NO_CERTIFIED_MAP` until an admissible residual branch crosswalk lands.
3. Treat the Green/BGG assignment as complete at the unary hybrid-chain level:
   `BERGER_54_ROW_CAUSAL_GREEN_HOMOTOPY_V2` contracts the acyclic clock/graph
   incidence before retained causal propagation.  Preserve the raw `L13`
   metric-cone no-go, and do not promote this unary theorem to interacting
   retarded products, Hadamard data, or a quantum claim.
4. Do not continue the obstructed rank-46 contractible-projector ansatz.
   Choose between an unsplit retained observable and the smallest
   noncontractible/mixed-bundle filtered enlargement.  Produce an
   Einstein-like/extra-Weyl/Maxwell mixing table only after that new carrier
   passes; a nonlocal split must remain explicitly `REDUCED-MODE`.
5. Add apparatus \(q_2,q_3\), \(K_{\rm Berger}\)-equivariance, and observer
   morphism stability only after the observer team closes the mixed
   \(\epsilon_R^2\kappa\) unary gate.
6. Do not begin \(q_4/\ell_4\) merely because arity three landed.  Open arity
   four or Yang--Mills only after the invariant \(\ell_3\) disposition or an
   exact obstruction makes the next identity scientifically decisive.

The closed unary Green assignment does not replace the invariant interaction
gate.  The handback and later physical activation gates are in
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
