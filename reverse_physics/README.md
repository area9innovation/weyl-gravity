# reverse_physics/ — assumption-necessity certificates

It asks whether this programme's certificate substrate can carry **reverse
physics** in the Carcassi–Aidala sense: not deriving laws from axioms, but
finding the minimal physical assumptions a law is equivalent to.

> **Start here: [`reports/OVERVIEW.md`](reports/OVERVIEW.md)** — the narrative
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
`quantum-weyl/`.~~ **That is no longer accurate, and the exact position is:**

**What is imported, and why.** Discharging the GEOMETRY column meant computing
against something. Three modules import
`black_hole_programme/weyl_geometry.py` — the exact Christoffel / Riemann /
Ricci / Weyl / Bach engine — **as a computational tool, pinned by SHA-256**, and
fail closed on drift. `weyl_dual_discharge.py` additionally reproduces
`quantum-weyl/local_bv/hodge.py`'s `star_square_sign` as a *checked row*, and
**cites** `EULER_TRANSGRESSION_CERTIFICATE` and
`symbolic/verify_conformal_dynamical_topological.py` for `G4`, `G7` and `N3`,
each carrying its source's own declared boundary.

**Why that is the middle column working, not a leak.** `G1`–`G8` and `N1`–`N3`
are *by construction* imported results — that is what the GEOMETRY column is
for. Citing an in-repository certificate with a machine-readable boundary is
strictly more auditable than citing a textbook, which is what the alternative
was. Nothing imported is used to establish a PHYSICS-column claim.

**What the `forbid` still buys, in the direction that matters.** No certificate
in this stream is cited as evidence inside the classical or quantum Weyl chains.
That is the load-bearing half: the chains do not lean on this stream, so nothing
here can prop up a result over there. `diff_independence.py` and
`weyl_vs_einstein_ledger.py` import nothing outside `reverse_physics/` at all.

**The tension is real and is recorded rather than resolved.** The work item's
`forbid` says "or vice versa", and the `G4`/`G7`/`N3` citations are that
direction. They are visible, hashed, and boundary-carrying — but a reader who
reads the `forbid` strictly should know the stream now takes three imports from
the quantum chain, and that they are all GEOMETRY-column entries.
