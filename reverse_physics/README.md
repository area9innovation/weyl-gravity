# reverse_physics/ — assumption-necessity certificates

A probe, not an established stream. It asks whether this programme's certificate
substrate can carry **reverse physics** in the Carcassi–Aidala sense: not
deriving laws from axioms, but finding the minimal physical assumptions a law is
equivalent to.

## What transfers, and what does not

Reverse physics needs three things. This substrate supplies two of them.

| | |
|---|---|
| **Sufficiency** — assumptions ⊢ law | a derivation. **Not supplied by the rails in this directory.** But see *The Rocq route* below — it is reachable, and this directory is not where it should be built. |
| **Necessity** — a system satisfying every assumption but one, in which the law fails | a no-go with an exact witness over a declared carrier. **This is exactly what the substrate already does.** |
| **An honest ledger** of what each derivation consumed | `assumption_tags`, `claim_boundary`, `does_not_establish`, `generality_level`. **Already load-bearing.** |

So the deliverable shape is an implication *digraph* — certified edges, plus
non-edges bounded by the `generality_level` of their separating witness — not
the equivalence lattice of reverse mathematics. That gap is stated in every
certificate's `does_not_establish` and is not to be papered over.

## Tag namespace

`RP-*` names **physical postulates**. It is disjoint from the programme's four
tags (`LOCAL-ALGEBRAIC` / `EUCLIDEAN-SPECTRAL` / `REDUCED-MODE` /
`LORENTZIAN-CAUSAL`), which name **computational regimes**. Never mix the two in
one field: `dependency_tags` takes the programme namespace, `assumption_tags`
takes `RP-*`. A test enforces this.

`RP-LINEAR-CARRIER` is a *scope restriction*, not a postulate, and is labelled as
such in `carriers.ASSUMPTION_GLOSS`.

## Lifecycle ladder

Separate from the quantum ladder; never promote across ladders.

```text
CARRIER_DECLARED → SEPARATION_CERTIFIED → NECESSITY_CERTIFIED
                 → SUFFICIENCY_CERTIFIED → EQUIVALENCE_CERTIFIED
```

Only the first three are reachable with the **rails in this directory**.
`SUFFICIENCY_CERTIFIED` and `EQUIVALENCE_CERTIFIED` require a derivation and a
reversal over a base theory, which exact rational computation cannot supply.

## The Rocq route

That is a limit of these rails, not of the substrate. `tango/forge` carries
`tools/conflux-proof`: a Conflux (Datalog/eq-sat) engine that **saturates** a
finite universe emitting a verdict certificate per cell, a *verified* checker
that validates engine-emitted certificates against hand-audited theories, and
Rocq 8.20.1 doing the inductive metatheory with `Print Assumptions` ledgers. The
emitter is fully in Forge. Its own slogan — *exhaustiveness = Conflux covers
every cell × Rocq covers every step* — is exactly the shape of a reverse-physics
deliverable: the assumption lattice is a finite universe of cells, and each
implication edge is a step to induct over.

Consequences for this directory:

- The **general-n certificate is the one that most wants to be a theorem.** Its
  derivation is uniform in n and its seven steps are already isolated; Rocq would
  replace "machine-checked at n = 1…7 plus a polynomial-identity argument" with a
  proof for all n, and the Python rail would remain as an independent numeric
  check rather than the whole evidence.
- **Conflux is opt-in and gated.** Per `AGENTS.md` and
  `planning/SCIENCE-FORGE-ADOPTION.md`, a stream may not run Conflux against
  physics without a declared importer, an independent replay, and a
  claim-specific activation gate named in its work item. The reverse-physics work
  item does **not** currently enable one. Structure-seeking work is also
  proof-first there: state the candidate theorem, proof obligations,
  counterexample strategy and exact finite remainder *before* an exploratory run.
- Nothing here may claim a Rocq-backed status until a gate exits 0 with its
  ledger printed. `FORMALLY_VERIFIED_IN_A_PROOF_ASSISTANT` is `false` in every
  certificate in this tree.

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
```

## Results

| certificate | generality | says |
|---|---|---|
| `..._LINEAR_G0_V1` | `G0` (n = 1, 2) | marginal information conservation is necessary but not sufficient; gap 4 at n = 2; obstruction localised in the inter-DOF block; survives to finite time — [report](reports/hamiltonian-privilege-linear-g0.md) |
| `..._GENERAL_N_V1` | `G2` (all n) | the separation threshold is exactly n = 2 and the gap `2n(n−1)` grows quadratically — [report](reports/hamiltonian-privilege-general-n.md) |

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
