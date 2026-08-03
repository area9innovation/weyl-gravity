# The loop closes: reversible ⟺ no entropy production

**Certificate** `REVERSE_PHYSICS_ENTROPY_CONVERSE_ROCQ_V1`
**Proof** `rocq/ReversePhysicsEntropyConverse.v` — Rocq 8.20.1, zero axioms
**Gate** `rocq/run.sh` — `RESULT: 13 green (0 red)`
**Closes** `REVERSE_PHYSICS_ENTROPY_CONVERSE`

## The theorem

For doubly stochastic evolution on the four-state carrier:

```
reversible M  ⟺  purity (evolve M p_test) == purity p_test
```

**Reversibility and the absence of entropy production are the same condition.**

Forward (proved previously): nothing is lost because nothing is mixed.
Backward (here): any mixing shows up as a strictly positive deficit, so
preserving purity forces every row to be a point mass; unit column sums then make
the resulting map a permutation, reconstructed explicitly via `col_arg` and
proved injective.

## Why the first attempt failed, and what fixed it

The previous certificate recorded the converse as not done and named the cause:
a case analysis over (row, pair, pair) with the test distribution's values
expanded by `compute in *`, producing enormous goals — `coqc` killed after 2m40s.
It also named the cheaper route.

That route worked, and the repair is **entirely structural**:

- `row_deficit_expr` stays a folded `Definition` — the six terms are never
  expanded during the split;
- `p_test` stays opaque and is used only through `p_test_sq_pos`;
- the four-way split happens **once**, in `each_row_deficit_zero`, on four atoms.

The file compiled first try in **2.2 seconds**. The failure was never
mathematical.

## One distribution suffices

No quantification over distributions is needed. A single `p` with pairwise
distinct entries detects every failure, because no squared difference can be the
vanishing factor — the whole content falls on the coefficients.

The gate carries a control showing this is **essential**: every doubly stochastic
map preserves the *uniform* distribution exactly, so a uniform test would prove
nothing. The mixer would pass it and is not reversible. That control is rejected,
which is why `p_test` has distinct entries.

## Lattice status — the first closed loop

The stream's two laws are now linked in **both** directions on this carrier:

- `conserves_information` makes reversibility redundant
  (`..._STOCHASTIC_ROCQ_V1`) and entails the arrow of disorder
  (`..._SECOND_LAW_ROCQ_V1`);
- reversibility **is** the absence of entropy production (here).

That is a closed loop rather than a directed edge — the first genuine cycle in
the lattice.

## Ledger

```
Print Assumptions    10/10 this module; 71/71 across eight modules
coqchk axioms        <none>
negative controls    8, all rejected
```

## What this does not establish

- Nothing about Shannon entropy; Rényi-2 purity only.
- **Not a general finite state space** — the proof is written for four states and
  the case analyses are sized to it.
- Nothing about many steps, equilibration, or approach to uniformity.
- No transfer to the Hamiltonian carriers.
- Not a reproduction, confirmation, or refutation of Carcassi–Aidala's derivation.
- No quantum, causal, or field-theoretic claim.

## Next gate

`REVERSE_PHYSICS_STOCHASTIC_GENERAL_N` — lift the four-state case analyses to a
general finite state space. This is a **refinement, not a new finding**.

## Verification

```bash
cd rocq && ./run.sh
PYTHONPATH=. python3 -m reverse_physics.entropy_converse_rocq --check
```

## Tier receipt

- **Tier 0/1** — eight modules compile; gate 13 green / 0 red from a clean tree
  in 34 s; `coqchk` empty axiom section; nine provenance records hash-verified;
  30-test Python suite green.
- **Tier 2 — not run, and not required.** Nothing outside `reverse_physics/` and
  `rocq/` imports or is imported by this work.
- **Tier 3 — not run, and not required.** No freeze, tag, or paper promotion.
