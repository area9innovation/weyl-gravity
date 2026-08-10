# reverse_physics/ — assumption-necessity certificates

It asks whether this programme's certificate substrate can carry **reverse
physics** in the Carcassi–Aidala sense: not deriving laws from axioms, but
finding the minimal physical assumptions a law is equivalent to.

> **Start here: [`reports/WEYL-CHARACTERIZATION.md`](reports/WEYL-CHARACTERIZATION.md)**
> — the consolidated answer to the stream's standing question: what the Weyl
> action is *equivalent* to, layer by layer, with every assumption's witness and
> every open edge in one place.
>
> **[`reports/OVERVIEW.md`](reports/OVERVIEW.md)** — the narrative
> account of what was asked, what was found, and what the negative results mean.
> The rest of this file is the index.
>
> **[`reports/AOP-CONNECTION.md`](reports/AOP-CONNECTION.md)** — where these
> results bear on Carcassi and Aidala's own programme, and where conformal
> gravity bears on their open conjecture for general relativity.
>
> **[`reports/coprime-hierarchy-rocq.md`](reports/coprime-hierarchy-rocq.md)** —
> the one result that engages *this programme's* own open corpus rather than a
> carrier built to demonstrate the method. Start here if the question is whether
> any of this is physics.

## What transfers

Reverse physics needs three things. All three now have an instance here.

| | | where |
|---|---|---|
| **Necessity** — a system satisfying every assumption but one, in which the law fails | an exact witness over a declared carrier | the shape the substrate already had |
| **Sufficiency** — assumptions ⊢ law | a derivation | `rocq/`, zero-axiom |
| **An honest ledger** of what each derivation consumed | `assumption_tags`, `claim_boundary`, `does_not_establish`, `generality_level` | load-bearing throughout |

The deliverable started as an implication *digraph* — certified edges plus
non-edges bounded by the `generality_level` of their separating witness. With
`REVERSE_PHYSICS_TORUS_REVERSAL_ROCQ_V1` there is now one genuine **equivalence
with independence**, which is the reverse-mathematics shape. Read the scoping
note under *Lifecycle ladder* before treating it as more than that.

## Tag namespace

`RP-*` names **physical postulates**. It is disjoint from the programme's four
tags (`LOCAL-ALGEBRAIC` / `EUCLIDEAN-SPECTRAL` / `REDUCED-MODE` /
`LORENTZIAN-CAUSAL`), which name **computational regimes**. Never mix the two in
one field: `dependency_tags` takes the programme namespace, `assumption_tags`
takes `RP-*`. A test enforces this.

`RP-LINEAR-CARRIER` is a *scope restriction*, not a postulate, and is labelled as
such in `carriers.ASSUMPTION_GLOSS`.

**The vocabulary is redundant.** `REVERSE_PHYSICS_STOCHASTIC_ROCQ_V1` proves that
on a finite-state stochastic carrier `RP-REVERSIBLE` is exactly
`RP-DETERMINISTIC ∧ RP-INFORMATION-CONSERVING`. Certificates on the Hamiltonian
carriers list determinism and reversibility as two separate consumed assumptions,
which on that evidence overstates how many are in play. The equivalence is *not*
proved for the continuous carriers, so those listings are left alone rather than
silently merged — but do not read them as a count of independent postulates.

## Lifecycle ladder

Separate from the quantum ladder; never promote across ladders.

```text
CARRIER_DECLARED → SEPARATION_CERTIFIED → NECESSITY_CERTIFIED
                 → SUFFICIENCY_CERTIFIED → EQUIVALENCE_CERTIFIED
```

`EQUIVALENCE_CERTIFIED` is now reached, once, by
`REVERSE_PHYSICS_TORUS_REVERSAL_ROCQ_V1` — and the promotion is **scoped**.

That certificate proves `law ⟺ A1 ∧ A2 ∧ A3` with each assumption derived *from*
the law and each independent by an explicit witness. That is a genuine reversal,
and it was the missing half.

What it is **not** is a reversal over a *weakenable* base. The base theory here
is the carrier declaration — fixed `ω`, fixed DOF split, trigonometric-polynomial
fields — which is definitional context, not an axiom schema one can weaken and
compare against. Reverse mathematics needs the latter. Do not cite this as a
reverse-mathematics result without that qualifier; the certificate's
`base_theory.honesty` field states it, and `next_gate` names what would close it.

## The Rocq route

The exact-rational rails in this directory cannot prove; `tango/forge` carries
`tools/conflux-proof`: a Conflux (Datalog/eq-sat) engine that **saturates** a
finite universe emitting a verdict certificate per cell, a *verified* checker
that validates engine-emitted certificates against hand-audited theories, and
Rocq 8.20.1 doing the inductive metatheory with `Print Assumptions` ledgers. The
emitter is fully in Forge. Its own slogan — *exhaustiveness = Conflux covers
every cell × Rocq covers every step* — is exactly the shape of a reverse-physics
deliverable: the assumption lattice is a finite universe of cells, and each
implication edge is a step to induct over.

Consequences for this directory:

- The **general-n certificate is now the one that most wants to be a theorem.**
  The torus results have been proved; general-n is still "machine-checked at
  n = 1…7 plus a polynomial-identity argument". Its derivation is uniform in n
  and its seven steps are already isolated, so Rocq would replace that with a
  proof for all n, leaving the Python rail as an independent numeric check
  rather than the whole evidence.
- **Conflux is opt-in and gated.** Per `AGENTS.md` and
  `planning/SCIENCE-FORGE-ADOPTION.md`, a stream may not run Conflux against
  physics without a declared importer, an independent replay, and a
  claim-specific activation gate named in its work item. The reverse-physics work
  item does **not** currently enable one. Structure-seeking work is also
  proof-first there: state the candidate theorem, proof obligations,
  counterexample strategy and exact finite remainder *before* an exploratory run.
- Nothing may claim a Rocq-backed status until a gate exits 0 with its ledger
  printed. `FORMALLY_VERIFIED_IN_A_PROOF_ASSISTANT` is `true` only on the three
  `rocq/`-backed certificates and `false` on every Python-rail one.

## Contents

```
exact_linalg.py                        exact rational kernel; two independent rank routines
carriers.py                            declarations only — Ω, the DOF split, the witnesses
hamiltonian_privilege_linear_g0.py     G0 rail A: dimensions from constraint ranks
verify_hamiltonian_privilege_linear_g0.py
                                       G0 rail B: spanning sets, Bareiss, Leibniz
hamiltonian_privilege_general_n.py     general-n rail A: the structural derivation
verify_hamiltonian_privilege_general_n.py
                                       general-n rail B: brute-force ranks, n = 1…6

                                       — the Weyl-gravity ledger itself —
weyl_geometry_discharge.py             G1, G2, G3, G5, N1 against the repository's
                                       exact curvature engine
weyl_dual_discharge.py                 G6 and G8, both signatures; the dual's index
                                       placement, fixed by reproducing hodge.py's
                                       star square
weyl_trace_law.py                      N2 as a trace law, and E^(C²) = 4B computed
                                       against the engine's own Bach tensor
diff_independence.py                   RP-DIFF's independence witness, on a carrier
                                       where the assumption can fail
weyl_vs_einstein_ledger.py             the OPENS / CHALLENGES comparison ledger and
                                       the rails that keep its citations honest
carrier_vacuity.py                     the VACUOUS / LIVE / EMPTY trichotomy, the
                                       enlargement operation behind 4.2 and 4.7,
                                       and an audit of this ledger against it
carrier_enlargements.py                RP-METRIC and RP-LOCAL, the two the audit
                                       found still vacuous -- witnessed by the
                                       same operation
einstein_classification.py             Lovelock in D = 4 at degree <= 2, from the
                                       forced head plus divergence-freedom; the
                                       Lanczos tensor derived, not imported
ghost_harmless.py                      the three ghost-escape routes shown to be
                                       one condition: diagonalizable + real
mannheim_cutting_rules.py              the published loop-unitarity theorem read
                                       for scope: it stops one point short of
                                       1/k^4, by its own Sec. VI
ghost_parity_double_pole.py            manifest ghost parity and a coincident
                                       double pole are incompatible -- so the
                                       symmetry must be broken by the VACUUM
bateman_vs_mannheim_ledger.py          the two camps as ONE complex structure
                                       with two real forms; five levels, and
                                       the answer changes between them
charge_grading_loop_stability.py       loops cannot generate positive charge --
                                       the propagator is off-diagonal, so the
                                       one-sidedness hypothesis is loop-stable
bt_ir_regulator_trilemma.py            exact obstruction to a local invariant
                                       mass at the stationary BT broken vacuum;
                                       points the project to non-mass IR rails
bt_inclusive_radical_closure.py        finite Eq. (20) completeness sums preserve
                                       the relative negative-charge radical in
                                       the one-sided image; the
                                       physical real-plus-virtual map stays open
bt_offshell_jet_obstruction.py         proves the delta-prime Born functional
                                       needs square-free external-virtuality
                                       jets and cannot descend to on-shell data
bt_five_point_tree_jet.py              complete 25-graph PS five-point tree jet:
                                       virtuality degree starts at three, so
                                       its pointwise fivefold square vanishes
bt_five_point_collinear_layer.py       exact correlated channel/mass blow-up:
                                       a shrinking collinear phase-space slice
                                       is nonzero at total projector order five
bt_five_point_independent_mass_threshold.py
                                       independent-mass threshold integral:
                                       ordinary mixed derivative fails logarithmically
bt_perfect_square_rg_separatrix.py     PS is an exact one-loop RG separatrix;
                                       public loop data still miss its finite top jet
bt_four_point_bubble_log_jet.py        first virtual coefficient: arbitrary-mass
                                       bubble logarithm and four-leg interference jet
bt_triangle_box_log_jet.py             complete triangle and box logarithmic jets;
                                       inverse-power collinear terms cancel in the
                                       full topology sum, leaving one ratio logarithm
bt_external_projector_carrier_mismatch.py
                                       applies the four-mass phase projector to the
                                       hard log and proves it is not the real
                                       threshold's external-mass-ratio carrier
bt_external_mass_boundary_log_jet.py   computes the missing nonanalytic external-
                                       mass loop cut from cubic splitting times the
                                       complete five-point tree
bt_real_virtual_axis_gluing.py         completes the final-pair real kernel, inner
                                       angle, identical-particle sum, and proves an
                                       axis-compatible regulator noncancellation
bt_born_trace.py                       the same reading for the Krein camp: the
                                       obstruction is invisible to their Born
                                       rule on the shell, and their nullity
                                       hypothesis is a boundary property
operational_witness.py                 one witness given states, evolution and a
                                       measurement -- the bridge to an
                                       experimental-verifiability framework
chain_imports.py                       the four conditions replacing the blanket
                                       cross-chain ban, and their enforcement
aop_vacuity_audit.py                   the vacuity instrument turned on the
                                       Assumptions of Physics framework
weakenable_base.py                     carrier = base, constraints = axioms:
                                       the lattice, its monotonicity, and the
                                       migration invariant
ghost_signature.py                     inertia (1,2): the criterion survives, and
                                       "harmless" is weaker than "no ghost"
weyl_action_d6.py                      the declared D = 6 gate: the method
                                       scales, the uniqueness does not

schema/  certificates/  tests/  reports/

../rocq/ReversePhysicsTorus.v          the topological step, all modes
../rocq/ReversePhysicsTorusChain.v     the four-level chain, both inclusions strict
../rocq/ReversePhysicsTorusReversal.v  the reversal: law <-> A1 /\ A2 /\ A3
../rocq/ReversePhysicsTorusSplit.v     why A2 is the remainder of a split choice
../rocq/ReversePhysicsStochastic.v     a finite-state carrier: reversibility is
                                       not an independent assumption
../rocq/ReversePhysicsSecondLaw.v      a second law on that carrier: disorder
                                       never decreases
../rocq/ReversePhysicsEntropyEquality.v
                                       the equality case, forward half
../rocq/ReversePhysicsEntropyConverse.v
                                       the converse, and the biconditional
../rocq/ReversePhysicsAOPBridge.v      our omega proved to be their J (x) I_n,
                                       and the three findings in their notation
../rocq/ReversePhysicsConformalCount.v the parity obstruction to a conformally
                                       invariant degree-of-freedom count
../rocq/ReversePhysicsNoConformalCount.v
                                       and the refutation of the last branch
../rocq/ReversePhysicsRelationalCount.v
                                       what replaces it: one scaling exponent
../rocq/ReversePhysicsExponentAdditivity.v
                                       and independence becomes its additivity
../rocq/CoprimeHierarchyOrderLaw.v     the coprime-ratio order law, proved
../rocq/CoprimeHierarchyKernelParity.v and which kernel carries it
../rocq/run.sh                         the zero-axiom gate (coqc, coqchk, controls)
```

## Results

| certificate | generality | says |
|---|---|---|
| `..._LINEAR_G0_V1` | `G0` (n = 1, 2) | marginal information conservation is necessary but not sufficient; gap 4 at n = 2; obstruction localised in the inter-DOF block; survives to finite time — [report](reports/hamiltonian-privilege-linear-g0.md) |
| `..._GENERAL_N_V1` | `G2` (all n) | the separation threshold is exactly n = 2 and the gap `2n(n−1)` grows quadratically — [report](reports/hamiltonian-privilege-general-n.md) |
| `..._TORUS_G1_V1` | `G1` (T⁴, N ≤ 3) | on a manifold the chain has **four** levels; the symplectic→Hamiltonian gap is `b₁ = 4` at every truncation and entirely in the zero mode, while the local gaps grow — so part of the missing assumption is topological, not physical — [report](reports/hamiltonian-privilege-torus-g1.md) |
| `..._TORUS_ALL_MODES_ROCQ_V1` | `G4` (all modes) | the topological step **proved**, not computed: at every mode with a nonzero frequency closed = exact, so the gap is carried by the zero mode for *every* truncation — zero-axiom Rocq, kernel-rechecked — [report](reports/torus-all-modes-rocq.md) |
| `..._TORUS_FULL_CHAIN_ROCQ_V1` | `G4` (all modes) | the rest of the chain proved, both inclusions **strict**; and the marginal condition is exactly the *intra*-DOF content of symplecticity — the same localisation G0 found on the linear carrier — [report](reports/torus-full-chain-rocq.md) |
| `..._TORUS_REVERSAL_ROCQ_V1` | `G4` (all modes) | **the reversal**: law ⟺ A1 ∧ A2 ∧ A3, each derived *from* the law, each independent by witness — [report](reports/torus-reversal-rocq.md) |
| `..._TORUS_SPLIT_ROCQ_V1` | `G4` (all modes) | **why A2 isn't physical**: A1's split-dependence cancels against it exactly, so the physical/geometric division is *not canonical*; corrects the earlier split-dependence theorem, which used an isotropic pairing — [report](reports/torus-split-rocq.md) |
| `..._STOCHASTIC_ROCQ_V1` | `G1` (4 states) | a **different carrier** where determinism and reversibility can fail: reversible ⟺ deterministic ∧ information-conserving, so **reversibility was never an independent assumption** — [report](reports/stochastic-rocq.md) |
| `..._SECOND_LAW_ROCQ_V1` | `G1` (4 states) | **a second law**: information conservation entails that disorder never decreases (purity/Rényi-2, no logarithms). The same assumption carries both laws — [report](reports/second-law-rocq.md) |
| `..._ENTROPY_EQUALITY_ROCQ_V1` | `G1` (4 states) | reversible evolution preserves purity **exactly**, and spreading strictly produces entropy — [report](reports/entropy-equality-rocq.md) |
| `..._ENTROPY_CONVERSE_ROCQ_V1` | `G1` (4 states) | **the biconditional**: reversible ⟺ no entropy production. The lattice's first closed loop — [report](reports/entropy-converse-rocq.md) |
| `..._CONFORMAL_COUNT_ROCQ_V1` | `G3` (all dims) | **the fourth desideratum**: no conformally invariant DOF density exists in odd dimension, by parity. A Cauchy surface is 3-dimensional — [report](reports/conformal-count-rocq.md) |
| `..._NO_CONFORMAL_COUNT_ROCQ_V1` | `G3` (flat space) | **the last branch falls**: every ball ties, additivity never used. No informative conformally invariant DOF count exists at all — [report](reports/no-conformal-count-rocq.md) |
| `..._RELATIONAL_COUNT_ROCQ_V1` | `G3` (flat space) | **what replaces it**: a *relative* count survives, is multiplicative, and is generated by a single scaling exponent — [report](reports/relational-count-rocq.md) |
| `..._EXPONENT_ADDITIVITY_ROCQ_V1` | `G3` (products) | **their assumption transposed**: DOF-independence becomes additivity of that exponent, proved without logarithms — [report](reports/exponent-additivity-rocq.md) |
| `..._COPRIME_HIERARCHY_ROCQ_V1` | `G4` (all coprime p:q) | **the programme's own open conjecture**: order clause proved, kernel clause proved and refined, even `p` shown unobstructed on six loci, four new instances — [report](reports/coprime-hierarchy-rocq.md) |
| `..._COPRIME_CHARGE_BOUND_ROCQ_V1` | `G4` (all p,q > 0) | **a retraction, with proof**: the physics reading above was backwards. `J = p·n̂₁ + q·n̂₂` has the resonant sector as its exact commutant, so every possible obstruction conserves it — and `J` is positive, so it *bounds* both occupations. Pair creation, which does run away, provably breaks it — [report](reports/coprime-charge-bound.md) |
| `..._SCATTERING_C_FACTORISATION_V1` | `G4` (all Hermitian pairs of inertia (1,2)) | **an independent reproduction, and a correction.** The pencil criterion (`L_H` diagonalizable with `spec(L_H) ⊂ (0,1)`) was already `CLASSIFIED` in `black_hole_programme/phase4/channel_factorized_c_pullback_test_v1`. Re-deriving it independently is a cross-check, not a discovery — and the comparison corrected two things: the blocker is **`T₋`**, not `T₊` (it drops out of `K₊ = G − K_H`), and a **Jordan failure mode** had been missed, where the spectrum lies inside the interval but the operator is not diagonalizable — [report](reports/scattering-c-factorisation.md) |
| `..._WEYL_GHOST_DIPOLE_V1` | `G4` (all rank-two Jordan blocks) | **the degenerate case, and the cross-programme join**: a dipole's commutant is only `a·I + b·N`, so `det(Gη) = −g²a²` is never positive — indefinite or degenerate, never curable. The black-hole programme had already computed this on Schwarzschild, converging on `RP-LOCAL` from the opposite end. Imports their certificates **by content hash, fail-closed on drift** — [report](reports/ghost-and-the-black-hole.md) |
| `..._WEYL_GHOST_FORCED_V1` | `G4` (all even `D`) | **the uniqueness theorem *is* the ghost theorem**: `D − 2k = 0` gives both the unique action and a pole count of `D/2`, and two or more poles always include a negative residue. So the ghost cannot be tuned away — there is no other conformal action — and dropping `RP-WEYL` or `RP-DIM4` provably does not help, leaving locality and field content — [report](reports/weyl-ghost-forced.md) |
| `..._WEYL_ACTION_V1` | `G4` (all quadratic curvature actions, all `D`) | **reverse physics on the subject itself**: the Weyl action is *equivalent* to `RP-LOCAL ∧ RP-METRIC ∧ RP-DIFF ∧ RP-WEYL ∧ RP-DIM4` modulo topological terms, each independent; the derivative order is **derived**, not assumed; and parity is independent on actions but **redundant** on field equations, with `[W₊²]`/`[W₋²]` as its eigenbasis — [report](reports/weyl-action-reverse-physics.md), [separation ledger](reports/PHYSICS-VS-MATH.md) |

| `..._GHOST_MODEL_OBSTRUCTION_ROCQ_V1` | `G4` (all coprime `p,q`) | the successor to the retraction: the coprime obstruction decides the ghost's dynamical fate in **neither** direction — [report](reports/ghost-model-obstruction.md) |
| `..._LH_ASSEMBLY_V1` | `G4` (Krein pencils) | the `L_H` assembly, with `det`-ratio-of-Grams and the `L_x` factorisation after `LRW` — [report](reports/lh-assembly.md) |
| `..._WEYL_GEOMETRY_DISCHARGE_V1` | metrics, exact | **the middle column stops being a promise**: `G1`, `G2`, `G3`, `G5`, `N1` computed against this repository's own curvature engine rather than imported. `G5`'s witness — matter-dominated FRW, `□R = −8/(3t⁴)` — was *named* and is now *computed*, and Schwarzschild is shown unable to witness it — [report](reports/weyl-geometry-discharge.md) |
| `..._WEYL_DUAL_DISCHARGE_V1` | metrics, both signatures | **`G8` is two statements, not one**: Euclidean `W±² = (C² ± P)/2` with real projectors, Lorentzian `W±² = (C² ∓ iP)/2` with complex ones — and the textbook form is *checked false* in Lorentzian signature. `G6`'s computable clause discharged; the check is **vacuous on Ricci-flat metrics**, so every row reports whether it can see anything — [report](reports/weyl-dual-discharge.md) |
| `..._WEYL_TRACE_LAW_V1` | metrics, exact | **N2, and the bridge between the two ledgers**: `g^mn E_mn = 2(a + b + 3c)□R`, where `a + b + 3c = 0` is exactly the classification's Weyl equation — so the kernel of the trace map is `span{C², E₄}` and `RP-WEYL ⟺ RP-TRACELESS` gets its reverse direction. `N2` and `G5` need the **same witness**. The variational link `E^(C²) = 4B` is now *computed*, not cited — [report](reports/weyl-trace-law.md) |
| `..._DIFF_INDEPENDENCE_V1` | `D = 4`, order 0 | **an assumption believed untestable in principle, witnessed**: on a carrier where `RP-DIFF` *can* fail, the lowest weight-zero degree is 55-dimensional and its diff-invariant subspace is exactly **0**. Consequence: the **derived derivative order requires `RP-DIFF`** — §4.3 was silently using it. Independence is *given* `RP-METRIC` — [report](reports/diff-independence.md) |
| `..._WEYL_VS_EINSTEIN_LEDGER_V1` | comparison | **what Weyl gravity opens and challenges**: one *forced* assumption swap over a shared base, so OPENS and CHALLENGES are two halves of one trade. Adds a **direction** and a **level** axis, the latter forced because "Einstein gravity is contained in Weyl gravity" is *true at `L2` and false at `L3`* — both established here — [report](reports/OPENS-AND-CHALLENGES.md) |

| `..._CARRIER_VACUITY_V1` | `D = 2,3,4`, order 0 | **the operation behind both carrier enlargements**, and the stream's oldest open problem given a shape: the carrier *is* the base, and an assumption vacuous on it is an axiom the base already proves. `RP-DIFF ∧ RP-WEYL` is shown **never simultaneously satisfiable at derivative order zero in any dimension**, which is the sharp form of why the derived order needs `RP-DIFF`. Audit: **three** ledger assumptions are vacuous, not one — [report](reports/carrier-vacuity.md) |

| `..._CARRIER_ENLARGEMENTS_V1` | `D` general, order 0 | **the last two vacuous assumptions, witnessed.** `RP-METRIC`: a compensator gives `√−g φ^{2D/(D−2)}`, diff- *and* Weyl-invariant at derivative order **zero** — the exponent falls out and reproduces `φ⁶,φ⁴,φ³` in `D = 3,4,6`. `RP-LOCAL`: `k − j = D/2` has one solution locally and one per inverse box otherwise, so locality is what makes the classification **unique**. Jointly: the derived derivative order requires **all three** of `RP-DIFF`, `RP-METRIC`, `RP-LOCAL`, each failing differently — [report](reports/carrier-enlargements.md) |

| `..._EINSTEIN_CLASSIFICATION_V1` | `D = 4`, degree ≤ 2 | **Lovelock computed in our own carrier**, closing the one citation the comparison ledger's central claim rested on. No field-equation formula imported: the forced head plus divergence-freedom (`N1`) leaves a two-parameter family, `RP-2ND-ORDER` picks out a unique tensor — **the Lanczos tensor, derived not looked up** — and it vanishes identically in `D = 4`, so degree two contributes nothing and the field equations are `aG_mn + bg_mn`. Also upgrades the Lanczos citation in the trace law — [report](reports/einstein-classification.md) |

| `..._GHOST_HARMLESS_V1` | Krein `(1,1)` | **three ghost escapes are one condition.** A conserved positive charge, quasi-Hermiticity/PT, and a positive invariant subspace all reduce to *diagonalizable ∧ real spectrum* — a positive-definite conserved charge **is** a metric operator. 1014-point scan, 0 mismatches. `C-GHOST-DYNAMICS` stays **OPEN** — [report](reports/ghost-harmless.md) |
| `..._OPERATIONAL_WITNESS_V1` | Krein `(1,1)` | **one witness with states, evolution and a measurement**, to test whether the bridge to an experimental-verifiability framework is buildable. It is, once: the three regimes are bounded / secular / exponential, and **no verification modality confirms all three** — harmlessness needs the parameters, the exceptional point needs the trajectory — [report](reports/operational-witness.md) |
| `..._AOP_VACUITY_AUDIT_V1` | audit | **the instrument turned outward.** Three of the four Assumptions-of-Physics assumptions are `LIVE`, two with witnesses the authors supply themselves. What it flags is a *derived step*: closedness of `ω` imposes **zero** conditions at one degree of freedom, since a 3-form does not exist on a 2-manifold — [report](reports/AOP-CONNECTION.md) §2.1e |
| `..._CHAIN_IMPORTS_V1` | discipline | the four conditions replacing this stream's blanket cross-chain ban — no cycles, tags travel, pinned, middle-column only — with the scan confirming the dependency is one-way |
| `..._WEAKENABLE_BASE_V1` | method | **the stream's oldest open problem, given a shape** — and the shape was already there. Construction constraints **are** a theory: carrier = base, enlarging = weakening, vacuous = proved outright. Vacuity is **monotone** and `(axioms) + (live assumptions)` is **constant**. All three migratable constraints are migrated. **Not closed** — no proof system — [report](reports/weakenable-base.md) |

| `..._GHOST_SIGNATURE_V1` | Krein `(1,2)` | **the criterion survives where the black-hole programme works** (`lh_assembly` records inertia `(1,2,0)`), so `(1,1)` was no accident — and it sharpens the meaning: in the harmless case the `η`-norms are `[+1,−1,−1]`, so **two negative-norm directions survive**. "Harmless" means a positive inner product *exists*, **not** that the ghost is gone — [report](reports/ghost-signature.md) |
| `..._MANNHEIM_CUTTING_RULES_V1` | `1/k⁴` | **the one loop-diagram paper in the fourth-order literature, read for scope** — Mannheim, PRD **98**, 045014 (2018), cited nowhere here before. Its §VII offers conformal gravity as "fully consistent"; its §VI says that in the Jordan-block case *"the standard cutting rules would not apply"*. Eq. (84), verified exactly in `ℚ[E,ω]`, shows §VII's object **is** §VI's. The reconciling step, Eq. (85)–(86), is the named assumption: `d/dM²` carries `δ(s−M²)` to `−δ′(s−M²)`, so the step that makes the *propagator's* limit non-singular destroys the *cut weight's* positivity — total mass `0`, first moment `1`. Appendix A(2)'s own norms go **null** like `(M₁²−M₂²)`. Does **not** show Weyl gravity is non-unitary — [report](reports/mannheim-cutting-rules.md) |
| `..._GHOST_PARITY_DOUBLE_POLE_V1` | quadratic sector | **the queued tensor test was the wrong necessary condition, and 2×2 algebra says so.** For `L = ∂Ω·∂Υ + aΩ² + bΥ²` the exchange is a symmetry iff `a = b` — and then either `⟨ΩΩ⟩ ≡ 0` or the poles **split** to `k² = ±2a`. **Manifest ghost parity ⟹ no coincident double pole**; the double pole needs `a ≠ b`. This explains rather than refutes Bateman–Turok: their *action* is symmetric and the asymmetric term comes from the **vacuum** `⟨Ω⟩ = λ⁻¹`, so ghost parity is **spontaneously broken** — presumably what *"hidden"* means in their title. Corroborated by their own `Ω > 0` caveat and by Paper 05's `m± = μ² ± √(εg)` splitting with ε. **Consequence:** a gravitational lift must supply an exchange-symmetric action **and** a vacuum that is BRST-invariant *while breaking the exchange* — a far sharper target than a commutator check — [report](reports/ghost-parity-double-pole.md) |
| `..._BATEMAN_VS_MANNHEIM_LEDGER_V1` | 5 levels | **complementary, overlapping, or alternative? All three — and the level axis is the result.** They are **two real forms of one complex structure**, differing in a single premise: *which involution is physical*. Mannheim fills it *positive-definite* (needs diagonalizable ∧ real spectrum; price: the field is complexified) and BT *indefinite* (needs one-sided charge; price: a generalized Born rule; the field stays real). **SHARED** at L1–L2, where `thm:bridge4` proves the same functional on `𝔄_inv`; **BT-opens** at L3–L4, where only the Krein form continues and the two separate; **BOTH-STOP** at L5 — the commonly-misread row, where neither has a loop result at the coincident point *that Weyl gravity occupies*. Each survives the other's failure (independence witnesses on both sides), so neither can absorb the other. Best transfer: **BT's embedding dissolves Mannheim's `−δ′` pathology**, which belongs to the fourth-order *variable*, not the theory — [report](reports/bateman-vs-mannheim.md) |
| `..._CHARGE_GRADING_LOOP_STABILITY_V1` | O(1,1) model | **the cheap question that had to precede the expensive one, and it clears.** Bateman–Turok's positivity needs "no positively charged operators"; if a loop could make one, the extension was dead. It cannot: the vertex `Ω²Υ²` is charge **neutral** and the propagator is purely **off-diagonal** (`⟨ΩΩ⟩=⟨ΥΥ⟩=0`), so every contraction pairs `Ω` with `Υ` and is neutral too — **operator charge is fixed by the external legs, independent of loop order.** The earlier mass-regulator corollary is withdrawn: charge preservation alone does not imply vacuum compatibility. The primary successor is a non-mass infrared architecture; a possible boost anomaly is a separate open gate — [report](reports/charge-grading-loop-stability.md) |
| `..._BT_IR_REGULATOR_TRILEMMA_V1` | local invariant potentials | **the obvious mass regulator is exactly obstructed at the stationary BT vacuum.** For every local boost-invariant `V=F(ΩΥ)`, stationarity at `(v,0)` forces `F′(0)=0`, while the coincident-pole mass is precisely `F′(0)`. Thus `μ²ΩΥ` has a massive double root only at a held background with tadpole `vμ²`; at its true stationary branch the determinant is `−z(z+2μ²)`, leaving a massless simple root. A fixed-`v` tadpole subtraction breaks the boost unless treated spurionically. This is `LOCAL-ALGEBRAIC`, not a no-go for inclusive, dressed, dimensional, off-shell, derivative, or nonlocal regulation — [report](reports/bt-ir-regulator-trilemma.md) |
| `..._BT_INCLUSIVE_RADICAL_CLOSURE_V1` | finite Eq. (20) charge carrier | **the relative negative-charge radical inside BT's one-sided nonpositive image survives every finite unresolved completeness sum generated by the off-diagonal kernel.** A sandwich shifts charge by `qL+qR`; it preserves that negative sector iff the shift is nonpositive. Both BT entries have shift zero, as do all tensor powers. The sector is not globally radical (`τ((t⁻¹)†t⁺¹)=1`). The sharp mutation `W^{ΩΩ}` has shift `+2` and exposes `t⁻² → 1`; `W^{ΥΥ}` has shift `−2` and still closes, showing closure alone does not reconstruct ghost parity. This clears the relative-radical gate but constructs no physical inclusive map, loop amplitude, KLN cancellation, regulator, resummation, or beyond-tree positivity theorem — [report](reports/bt-inclusive-radical-closure.md) |
| `..._BT_OFFSHELL_JET_OBSTRUCTION_V1` | exact external-virtuality jets | **the first real-plus-virtual BT probability cannot be reconstructed from published on-shell amplitudes.** With one delta-prime factor per external leg, the exact carrier is `Q[x₁,…,xₙ]/(xᵢ²)` and the Born projector selects the top square-free coefficient. `M=1` and `M=1+a x₁⋯xₙ` agree on shell but their projected squared probabilities differ by `2a`. Thus the NLO virtual channel requires a 16-slot four-leg jet and real emission a 32-slot five-leg jet; every slot has a complementary partner. The public companion calculations remain “to appear.” This does not declare PS ambiguous: it makes the missing off-shell/scheme-invariance object precise and leaves the physical NLO map, regulator cancellation, and beyond-tree positivity unconstructed — [report](reports/bt-offshell-jet-obstruction.md) |
| `..._BT_FIVE_POINT_TREE_JET_V1` | exact five-point rational-function jet | **the complete 25-graph tree `2→3` amplitude starts at external-virtuality degree three.** The 10 cubic–quartic and 15 three-cubic graphs cancel in all 16 slots of degree at most two in `Q(s₀,…,s₄)`; the remaining `10+5+1` coefficient functions are computed and content-hashed. Hence the ordinary on-shell five-point amplitude and the pointwise fivefold coefficient of its square both vanish exactly. Flipping the topology-family sign populates all 32 slots and makes the projector nonzero. Leading degree-three coefficients have simple soft/collinear poles, so this does not yet prove the integrated real probability vanishes: differentiated phase-space boundaries and regulator ordering remain open — [report](reports/bt-five-point-tree-jet.md) |
| `..._BT_FIVE_POINT_COLLINEAR_LAYER_V1` | reduced collinear phase-space slice | **the differentiated-boundary warning is active at exactly the dangerous order.** On the physical mass ray `xᵢ=δ(1,4,9,16,25)` with pair channel `t=δτ`, the complete normalized amplitude is `A₅=δ²C(τ)+O(δ³)`, where `C(τ)=−3(979τ²−5620τ+5193)/(4τ²)`. The inner two-body Källén density is `√((τ−9)(τ−1))/τ`, and `dt=δdτ`; hence the squared differential slice is `δ⁵` times a strictly positive coefficient on `10≤τ≤11`, with exact lower bound `59371743123/1600000` after positive universal factors are removed. This blocks passing the pointwise zero through phase-space integration. It does **not** prove the mixed five-mass distribution is nonzero: a common ray cannot isolate `x₀x₁x₂x₃x₄`, so the independent-mass distributional prescription is now the exact missing object — [report](reports/bt-five-point-collinear-layer.md) |
| `..._BT_FIVE_POINT_INDEPENDENT_MASS_THRESHOLD_V1` | independent-mass reduced threshold | **the missing ordinary derivative does not exist.** For arbitrary mass ratios the complete amplitude still starts at collinear order two. After the three spectator derivatives, the exact pair-threshold integral is `H(r)=[−5r³+3r²−3r+5+6r(r+1)log r]/[16(r−1)]`, so `H(r)=−5/16+r[−(3/8)log r−1/8]+…`. The remaining mixed slope diverges logarithmically. A finite part can be assigned, but rescaling the ratio cutoff by `c` shifts it by `−(3/8)log c`; `c=4` changes the result by `−(3/4)log 2`. A four-ray quadratic annihilator has a strictly negative rationally bounded defect, independently proving there is no joint quadratic jet. This is a reduced real-emission obstruction, not a completed inconsistency theorem: the four-leg virtual jet may cancel or fix the ambiguity — [report](reports/bt-five-point-independent-mass-threshold.md) |
| `..._BT_PERFECT_SQUARE_RG_SEPARATRIX_V1` | one-loop coupling algebra | **the PS theory is closed under Holdom's published one-loop RG flow.** With `λ₃=−λ`, `λ₄=−λ²/2`, and `F=λ₃²+2λ₄`, exact reduction gives `β(F)=−[5/(4π²)]F(λ₄+3λ₃²/2)`. Thus `F=0` is invariant and `βλ=−5λ³/(16π²)`: PS is asymptotically free. Among `λ₄=cλ₃²`, it is the unique invariant parabola with nonzero quartic coupling. The pole counterterm is proportional to the whole PS action, and the four-point loop has exactly box, triangle, and bubble vertex-count sectors. But a finite crossing-symmetric `x₁x₂x₃x₄` mutation is invisible to all quoted beta functions and on-shell cuts, proving those public data do **not** fix the required 16-slot virtual jet. The real `−3/8` matching coefficient remains open — [report](reports/bt-perfect-square-rg-separatrix.md) |
| `..._BT_FOUR_POINT_BUBBLE_LOG_JET_V1` | fixed-`(s,t)` four-mass virtual jet | **the first actual virtual coefficient is computed.** Two internal-mass derivatives of the ordinary massive cut give the arbitrary-external-mass double-pole channel polynomial `P=7S²+ST+T²−(7S+T)Σx+xₐx_b+x_cx_d+7Σ_cross x_ix_j`, reducing exactly to Holdom's on-shell logarithm. Interference with the complete PS tree amplitude yields a nonzero 28-integer four-mass logarithmic jet over denominator `s²t²(s+t)²`, independently reproduced by rational CM-frame angular fixtures and a square-free subset algebra. Its collinear expansion begins `(15L−ℓ)/r²+(−45L+3ℓ−35)/r`; the bubble alone is therefore too singular to compare with the real `−3/8` threshold. Triangle and box completion is mandatory, not optional — [report](reports/bt-four-point-bubble-log-jet.md) |
| `..._BT_TRIANGLE_BOX_LOG_JET_V1` | complete cut-constructible one-loop topology jet | **the triangle and box logarithmic sectors are now exact.** The PS four-point tree has universal low-virtuality identity `A^(0)=A^(1)=0`, `A^(2)=½Σ_{i<j}x_i x_j`; writing `A=E−Q` reduces the projector-relevant triangle and box cuts to polynomial angular moments. Their arbitrary-mass channel polynomials reproduce Holdom's generic forward coefficients `19` and `6` and cancel the bubble on shell channel by channel. The individual jets contain inverse powers, but `J_B+J_T+J_X=15(L_s+L_t+L_u)`: every `r^-2` and `r^-1` term cancels, leaving `15(3L−ℓ)`. This closes the logarithmic topology gate, not the physical NLO gate: cut-free finite terms, the external phase-space projector, common IR prescription, real `−3/8` matching, and beyond-tree positivity remain open — [report](reports/bt-triangle-box-log-jet.md) |
| `..._BT_EXTERNAL_PROJECTOR_CARRIER_MISMATCH_V1` | projected hard virtual log versus real threshold | **the four-mass external phase projector is now applied, and it reveals that the apparent matching target was the wrong variable.** Since both tree and complete logarithmic loop amplitudes start at mass degree two, phase-density derivatives decouple and `dσ_virt,log/dΩ=5λ⁶(L_s+L_t+L_u)/(256π⁴s)`. Its surviving `ell=log(-t/s)` is a hard Mandelstam-ratio log, while the real obstruction is `-(3/8)x₀x₁log(x₁/x₀)`. Rescaling the mass ratio changes the real finite part by `-(3/8)log c` and the computed virtual hard log by zero. This does not prove failure of full cancellation; it identifies the missing object as a nonanalytic virtual external-mass boundary layer invisible to the ordinary hard-region Taylor jet — [report](reports/bt-external-projector-carrier-mismatch.md) |
| `..._BT_EXTERNAL_MASS_BOUNDARY_LOG_JET_V1` | complete external-virtuality one-loop cut | **the missing nonanalytic virtual carrier is now exact on the physical collinear family.** Cutting one external virtuality factorizes the full loop boundary into the cubic splitting vertex times the complete 25-graph five-point tree, automatically joining lower-point insertions to the 1PI triangle/box boundary pieces. A symbolic square-free jet proves independence from both splitting fraction and outer scattering ratio. The loop term is `E_i=[-2x_i Σ_{j≠i}x_j+10Σ_{j<k;j,k≠i}x_jx_k]L_i`; interference gives `12Σ_iL_i`, and the BT projector yields `dσ_boundary,log/dΩ=3λ⁶Σ_iL_i/(128π⁴s)`. Cancellation remains open because the virtual carrier has one recombined parent mass whereas the real carrier has two daughter masses; the full **real** splitting kernel and a common regulator gluing are not yet defined — [report](reports/bt-external-mass-boundary-log-jet.md) |
| `..._BT_REAL_VIRTUAL_AXIS_GLUING_V1` | complete final-state collinear logarithmic response | **the ordinary independent-mass regulator route meets an exact scoped obstruction.** The spectator-projected complete five-point square is independent of both splitting fraction and outer ratio, so the inner solid angle gives `4π`. Restoring `(-1)^5` from the five delta-prime factors, `1/(2!3!)`, factorized three-body phase space, and all three unordered final pairs gives the real normalization response `+3λ⁶log(c)/(512π⁴s)`. For every axis-compatible parent map `G(x,y)=xg(y/x)` with `g` continuous at zero and finite nonzero `g(0)`—including the physical threshold `(√x+√y)²`—the virtual parent logarithm has zero constant daughter-ratio response. The logarithmic terms therefore do not cancel on this declared class. This is not a full NLO or theory no-go: a distributional normalization, degenerate incoming/dressed states, or resummation changes the architecture — [report](reports/bt-real-virtual-axis-gluing.md) |
| `..._BT_BORN_TRACE_V1` | obstructed shell | **a negative result about a shortcut, plus a repair.** The BT Born formula on the fixed split-mass shell is **positive by inspection** (positive rational·`√5` + positive rational), but **not because the obstruction is null**: it contributes `‖T₋‖² = 2c² = 482403/1554251776`, exactly the quantity `lem:chargenull` sends to **zero**. A truncated shell carries no boost action, so the mechanism is absent and the trace is positive only because κ-even outweighs κ-odd ≈ 26×. **This quantifies why the capstone needs the process operator *transported* along the `s → 0` family rather than held fixed** — Paper 05's own instruction. The charge rule and the `ε = 0` one-sidedness are Paper 05's, restated not claimed. Useful by-product: on a finite shell weak ghost symmetry collapses to the single inequality `‖A₋‖ ≤ ‖A₊‖`. Also **repairs an `nsimplify` float-leak** in `verify_doubled_theory.py` that had fabricated `T[1,1]` — [report](reports/bt-born-trace.md) |
| `..._WEYL_ACTION_D6_V1` | `D = 2…12` | **the declared `D = 6` gate.** `D − 2k = 0` selects exactly one degree per even dimension and none in odd — that scales. **The uniqueness does not**: the quotient at the selected degree is 1 at `D = 4` (computed) and 3 at `D = 6` (cited), so *"one degree"* ≠ *"one action"* and the ledger's uniqueness is **special to four dimensions**. Blocker named: no cubic invariant basis — [report](reports/weyl-action-d6.md) |
| `..._CUBIC_CONFORMAL_COUNT_V1` | `D = 4, 5, 6` | **the named blocker dissolved — for the symbolic route only.** Evaluate candidates at exact metrics, take the **rank over ℚ**, and every identity shows up as a linear dependence: the rank quotients by all of them without any being built. Cubic curvature span **6, 7, 8**; pointwise conformal invariants **1, 1, 2**, so the second one appears **exactly at `D = 6`**. **The count is 2, not the 3 that was predicted** — "type-B" means *pointwise*, it does **not** mean *no derivatives of the curvature*, so the row above stays `CITED` at 3 with its boundary now located. Forge rail, 26/26 — [report](reports/cubic-conformal-count.md) |
| `..._DERIVATIVE_CONFORMAL_COUNT_V1` | `D = 4, 5, 6` | **the derivative sector, and the `D = 6` count reaching 3.** Adding the weight-6 shapes that carry derivatives — `∇R ∇R` and `R ∇∇R` — the counts go **2, 2, 3**, so the derivative sector supplies **exactly one more invariant in every dimension** and `D = 6` now **matches the cited 3 by computation**. A **lower bound**, not an exactness proof: `□²R` is not among the candidates and that is where a fourth would hide, and **no basis is exhibited**. The cubic columns reproduce the row above through a *different* pipeline — [report](reports/derivative-conformal-count.md) |
| `..._PARITY_CONFORMAL_COUNT_V1` | `D = 4, 6` | **CORRECTED** — the weight-6 counts are **1 in `D = 4`** and **0 in `D = 6`**, not 2 and 2; the weight-4 Pontryagin row and the odd-`D` row are unchanged. See `..._PARITY_SCALAR_CONTROL_V1`. Original entry: **the parity half of the `D = 6` gate, answered — yes.** Parity-odd pointwise conformal invariants at weight 6: **2 in `D = 4`, 2 in `D = 6`**, none in odd dimensions (by index counting). Both are **exhibited**: complete contractions of one `ε` with three **Weyl** tensors. The Riemann-built candidates are mostly identically zero, so the parity-odd content is exactly what the Weyl tensor supplies. Known-answer control: the Pontryagin density, which the classification gate only **asserts** to be Weyl invariant. `ε` stays rational because `|det g| = 1` at the base point — **checked**, not assumed — [report](reports/parity-conformal-count.md) |
| ~~`..._PARITY_FIELD_EQUATIONS_V1`~~ | `D = 6` | **RETRACTED** — the Lagrangian it differentiated is **not a scalar** (chart-dependent under `SL(6,ℤ)`); see `..._PARITY_SCALAR_CONTROL_V1` and [report](reports/parity-scalar-defect.md). The Euler operator itself is untouched. Original entry: **the field-equation half, and it flips.** The `D = 4` statement is *"`RP-PARITY` is independent on **actions**, redundant on **field equations**"* — a gravitational theta-angle. In `D = 6` the Euler–Lagrange expression of the parity-odd invariant is **nonzero** (`E⁰⁰ = −12614421113/320`, two components, two metrics), so it is **not locally a total divergence** and parity is **load-bearing**. That makes the ledger's *"six as an action, five as field equations"* **dimension-dependent** — the second structural fact after uniqueness that does not travel out of `D = 4`. Controls built first because *nonzero* is where a bug reads as a discovery: the operator is exercised at `n = 6` against a construction-total-divergence (exactly zero), and this jet-level rebuild of the invariant is checked conformally invariant. **Local**, not global — [report](reports/parity-field-equations.md) |

| `..._PARITY_SCALAR_CONTROL_V1` | `D = 4, 5, 6` | **the control the counting apparatus shipped without — and what it cost.** A contraction is covariant only when each repeated index appears once **up** and once **down**; **eight** parity-odd candidates did not, and the published `D = 6` count of 2 came entirely from two of them. Nothing caught it because the conformal test is **vacuous on Weyl-built candidates** (`C^a{}_{bcd}` carries no derivative-of-`σ` terms, so *any* index pattern passes) and the weight count **cancels** (`−2` and `+2`). The falsifier is a chart change `x = Ay`, `A ∈ SL(n,ℤ)`, calibrated both ways: `R`, `C²` and the Pontryagin density must survive, a malformed `Σ R_ab R_ab` must move. Corrected: **1** and **0**. The `D = 6` zero is now a **count, not a lower bound**: `3240` patterns swept whole (the first Bianchi identity, verified componentwise, forces the `ε` split to `(2,2,2)`), all zero — while a generic tensor gives **3240 of 3240** nonzero. And it has a **mechanism**: antisymmetry within pairs leaves **2208** alive, and adding the **pair-exchange symmetry `C_{abcd} = C_{cdab}`** kills every one. Not Bianchi, not tracelessness — [report](reports/parity-scalar-defect.md) |

There is one further Forge-only result with **no certificate**, deliberately:
[`c-factorisation-not-determined.md`](reports/c-factorisation-not-determined.md)
runs the factorisation criterion against the actual physical Grams and shows both
outcomes are reachable, so an explicit `T₋` is logically unavoidable. Its gate
passes `forge -run` 25/25 but **fails `verify -full`** on a residual leak, so it
is reported as a finding and **not** promoted to a certificate.

And one further Forge-only piece, this one **fully verified** (`c==native`,
ASan-clean): [`t-minus-transport-engine.md`](reports/t-minus-transport-engine.md)
lands the validated transport for the exact Weyl axial factor equations with an
independent Wronskian conservation rail — the engine `T₋` needs. What remains is
the horizon Frobenius start, the Jost match at infinity, and the extension
coefficient.

The G1 computation lives **in Forge** (`math/qmat` exact rational rank), gated at
`forge/examples/reverse_physics_torus_gate.forge` in tango and pinned here by
content hash. `torus_g1_provenance.py` computes no physics — it is the import
gate, and it fails closed on drift.

## Rails

Rail B is not a rerun of rail A. Dimensions: constraint-nullspace rank vs
explicit-spanning-set rank. Elimination: Gauss–Jordan over ℚ vs fraction-free
Bareiss over ℤ. Hamiltonicity: "ΩA symmetric" vs "AᵀΩ + ΩA = 0". Determinant:
Gaussian vs the Leibniz permutation sum. They share only `carriers.py`, which
computes nothing.

```bash
PYTHONPATH=. python3 -m reverse_physics.hamiltonian_privilege_linear_g0 --check
PYTHONPATH=. python3 -m reverse_physics.verify_hamiltonian_privilege_linear_g0
PYTHONPATH=. python3 -m unittest reverse_physics.tests.test_hamiltonian_privilege_linear_g0 -v
```

## Independence from the Weyl programme

~~This directory imports nothing from the classical BV–BFV complex or from
`quantum-weyl/`, and nothing here may be cited inside those chains or vice
versa.~~ **That rule was over-broad and has been replaced by four conditions**,
enforced by `reverse_physics/chain_imports.py`
(`REVERSE_PHYSICS_CHAIN_IMPORTS_V1`).

The ban was protecting against three things. **Circular evidence** is the real
one — if the chains cite this stream *and* this stream cites the chains, the two
prop each other up and look like independent confirmation. But circularity needs
a **cycle**, and the dependency has always been one-way: the scan finds **no
certificate outside this stream citing it**, only `planning/` work items and
events, which are coordination rather than evidence. A ban on citing *into* this
stream forbids something that cannot close the loop.

**Tag laundering** is also real, and sharpest where this stream is headed next —
the ghost question is exactly where a Euclidean or reduced-mode result could get
quoted as if it settled a Lorentzian one. But that is prevented by *carrying the
boundary*, not by refusing to cite. **Staleness** is the weakest, and content
hashes solve it.

What the old clause did not state, and what is worth preserving: part of this
stream's value is that it audits the programme **from outside** — it is how it
could say *"your carrier has the answer baked in"* about this repository's own
ledger and about an external programme's framework. An auditor that shares the
auditee's *inputs* is weaker. That argues for keeping the **evidence direction**
clean, not for refusing to read.

| | condition |
|---|---|
| **C1** | **No cycles.** No certificate in the Weyl chains may cite this stream as evidence. One-way only. |
| **C2** | **Tags travel.** Every import declares its source's dependency tags, and no claim here may be stated at a tag its inputs do not support. The prohibition *"`REDUCED-MODE` and `EUCLIDEAN-SPECTRAL` are not evidence for `LORENTZIAN-CAUSAL`"* is mechanical. |
| **C3** | **Pinned, fail-closed.** Content-hashed; drift fails. |
| **C4** | **Middle column only.** Imports land in `GEOMETRY`, never establishing a `PHYSICS`-column claim. |

Seven imports: two tools/conventions and five evidence. Two come from sources
that **declare no dependency tag at all** — `symbolic/verify_conformal_dynamical_topological.py`
and Paper 18. A tag that does not exist cannot be carried, so those are recorded
`UNDECLARED` and nothing tagged may rest on them. Surfacing that beats silently
assuming the weakest tag on the source's behalf.

```bash
PYTHONPATH=. python3 -m reverse_physics.chain_imports --check
```
