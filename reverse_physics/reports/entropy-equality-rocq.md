# Reversible evolution is exactly entropy-neutral — and the converse is not proved

**Certificate** `REVERSE_PHYSICS_ENTROPY_EQUALITY_ROCQ_V1`
**Proof** `rocq/ReversePhysicsEntropyEquality.v` — Rocq 8.20.1, zero axioms
**Gate** `rocq/run.sh` — `RESULT: 12 green (0 red)`
**Partially closes** `REVERSE_PHYSICS_ENTROPY_EQUALITY`

## What was open

The second-law certificate recorded, specifically: *"that reversible evolution
**preserves** purity exactly is not proved — only that it does not increase it —
so 'reversible iff no entropy production' is NOT established."*

## Proved

```
reversible M  →  purity (evolve M p) == purity p
```

**Reversible evolution preserves purity exactly.** No entropy is produced.

The mechanism is `sparse_square`: with the underlying map injective, at most one
term of each row survives, so squaring the sum is the same as summing the
squares. **Nothing is lost because nothing is mixed.**

And the converse's mechanism, stated positively:

```
row_deficit :  purity lost in row i  =  Σ_{j<k} M_ij M_ik (p_j − p_k)²

spreading_produces_entropy :
  0 < M i j → 0 < M i k → p j ≠ p k → 0 < deficit
```

**Mixing is exactly what produces entropy.** A row that puts positive weight on
two states carrying different probability strictly loses purity.

## What is not proved — and why

The **biconditional is not established**. The converse — purity preserved ⟹
reversible — would need:

1. extracting from the vanishing *total* deficit that each of the twenty-four
   nonnegative terms vanishes, hence every row has at most one nonzero entry;
2. reconstructing the permutation from row sparsity plus unit column sums.

I attempted step 1 and abandoned it: the case analysis over (row, pair, pair)
with the test distribution's values expanded exhausted memory — `coqc` was killed
after 2m40s. A cheaper route exists (keep the twenty-four terms opaque and split
the sum once rather than per case), but it is not done here.

`spreading_produces_entropy` *is* the mathematical content of step 1, stated
positively and proved. The extraction and step 2 remain.

This is recorded rather than quietly dropped, and the module header says the same.

## Lattice status

The stream's two laws are now linked **in one direction**: reversibility — the
assumption the first carrier showed to be redundant — implies no entropy
production, the second law's equality case. The reverse link is open.

## Ledger

```
Print Assumptions    9/9 this module; 61/61 across seven modules
coqchk axioms        <none>
negative controls    7, all rejected — the new one a false claim that every
                     doubly stochastic map preserves purity (the mixer refutes it)
```

## What this does not establish

- **The biconditional.** Forward only.
- That preserving purity forces reversibility.
- Nothing about Shannon entropy; Rényi-2 only.
- Nothing about many steps, equilibration, or continuous state spaces.
- No transfer to the Hamiltonian carriers.
- Not a reproduction, confirmation, or refutation of Carcassi–Aidala's derivation.
- No quantum, causal, or field-theoretic claim.

## Next gate

`REVERSE_PHYSICS_ENTROPY_CONVERSE` — steps 1 and 2 above, which would give the
biconditional and close the loop between the two laws.

## Verification

```bash
cd rocq && ./run.sh
PYTHONPATH=. python3 -m reverse_physics.entropy_equality_rocq --check
```

## Tier receipt

- **Tier 0/1** — seven modules compile; gate 12 green / 0 red from a clean tree
  in 31 s; `coqchk` empty axiom section; eight provenance records hash-verified;
  30-test Python suite green.
- **Tier 2 — not run, and not required.** Nothing outside `reverse_physics/` and
  `rocq/` imports or is imported by this work.
- **Tier 3 — not run, and not required.** No freeze, tag, or paper promotion.
