# A second law — and the two laws consume the same assumption

**Certificate** `REVERSE_PHYSICS_SECOND_LAW_ROCQ_V1`
**Proof** `rocq/ReversePhysicsSecondLaw.v` — Rocq 8.20.1, zero axioms
**Gate** `rocq/run.sh` — `RESULT: 11 green (0 red)`

## Why a second law

Reverse physics pays off as a **lattice** of law/assumption pairs. Until now this
stream had one law — Hamiltonian privilege — plus a side-result about the
vocabulary. One law is a data point; two that interact is a structure.

## Keeping it exactly rational

The usual second law needs Shannon entropy, whose logarithms are not rational and
would break the exactness the whole stream depends on. Two ways round it:

- **Majorization** (Hardy–Littlewood–Pólya) — `p ≺ q` iff `p = Dq` for doubly
  stochastic `D`. Order-theoretic, logarithm-free, but stating it needs sorting,
  which is heavy to formalise.
- **Purity** `Σᵢ pᵢ²`, the collision probability. This is the exact rational
  content of the Rényi-2 entropy `−log(Σp²)`: since `−log` is monotone, *entropy
  does not decrease* **is** *purity does not increase*, with no logarithm
  anywhere. Purity is Schur-convex, so this is the majorization statement
  evaluated on one Schur-convex functional.

This file takes the second route.

## The theorem

```
purity_never_increases :
  nonneg M → column sums 1 → conserves_information M
           → purity (evolve M p) ≤ purity p
```

**A doubly stochastic evolution never increases purity. Disorder never
decreases.**

The entire analytic content is one polynomial identity, decided by `ring`:

```
(Σw)(Σ w x²) − (Σ w x)²  =  Σ_{j<k} w_j w_k (x_j − x_k)²
```

Stated with an *unconstrained* weight sum, so no side condition is needed and
`ring` alone settles it. With the weights summing to one it is Jensen; the right
side is manifestly nonnegative. No analysis, no limits, no logarithms.

The proof is then two moves: row by row, each output entry is a convex
combination of the input (row sums one), so its square is at most the
corresponding combination of squares; summing over rows and regrouping by column
turns the bound into the column sums, each of which is one.

## Not vacuous

| | purity |
|---|---|
| point mass on `s₀` | `1` |
| after uniform mixing | `1/4` |

Strict. And `mixer_is_admissible` proves the mixer satisfies *every* hypothesis
of the theorem, so the strictness isn't obtained by stepping outside them. A
negative control asserting purity is *conserved* rather than non-increasing is
rejected by the gate.

## The lattice point

Both hypotheses are already in the vocabulary and neither is new: column sums one
is conservation of probability; row sums one is `conserves_information` —
stationarity of the uniform ensemble.

**So the second law is not an extra postulate on this carrier. It is entailed by
information conservation.**

And that assumption is now load-bearing for *both* laws in this stream:

- it makes reversibility redundant (`..._STOCHASTIC_ROCQ_V1`);
- it entails the arrow of disorder (here).

Two laws, one assumption. That's the first genuine structure in the lattice
rather than a pair of isolated results.

## What this does not establish

- **Nothing about Shannon entropy.** Rényi-2 only; the logarithmic quantity is
  not formalised.
- **Not full majorization.** Purity is one Schur-convex functional, not the
  order itself.
- **The equality case is not characterised.** That reversible evolution
  *preserves* purity exactly is not proved — only that it does not increase it.
  So *"reversible iff no entropy production"* is **not** established, and the
  loop between the two laws is not closed.
- Nothing about many steps, equilibration, or approach to uniformity.
- No transfer to the Hamiltonian carriers.
- Not a reproduction, confirmation, or refutation of Carcassi–Aidala's derivation.
- No quantum, causal, or field-theoretic claim.

## Next gate

`REVERSE_PHYSICS_ENTROPY_EQUALITY` — characterise the equality case. That would
give *"reversible ⟺ no entropy production"* and close the loop between the two
laws on this carrier.

## Verification

```bash
cd rocq && ./run.sh
PYTHONPATH=. python3 -m reverse_physics.second_law_rocq --check
```

## Tier receipt

- **Tier 0/1** — six modules compile; gate 11 green / 0 red from a clean tree;
  `coqchk` empty axiom section; seven provenance records hash-verified; 30-test
  Python suite green.
- **Tier 2 — not run, and not required.** Nothing outside `reverse_physics/` and
  `rocq/` imports or is imported by this work.
- **Tier 3 — not run, and not required.** No freeze, tag, or paper promotion.
