# reverse_physics/ — assumption-necessity certificates

It asks whether this programme's certificate substrate can carry **reverse
physics** in the Carcassi–Aidala sense: not deriving laws from axioms, but
finding the minimal physical assumptions a law is equivalent to.

> **Start here: [`reports/OVERVIEW.md`](reports/OVERVIEW.md)** — the narrative
> account of what was asked, what was found, and what the negative results mean.
> The rest of this file is the index.

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

This directory imports nothing from the classical BV–BFV complex or from
`quantum-weyl/`, and nothing here may be cited inside those chains or vice
versa. The work item's `forbid` clause states this; there is no shared input to
go stale.
