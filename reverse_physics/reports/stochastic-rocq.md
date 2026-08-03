# Reversibility was never an independent assumption

**Certificate** `REVERSE_PHYSICS_STOCHASTIC_ROCQ_V1`
**Proof** `rocq/ReversePhysicsStochastic.v` — Rocq 8.20.1, zero axioms
**Gate** `rocq/run.sh` — `RESULT: 10 green (0 red)`

## The hole this fills

`RP-DETERMINISTIC` and `RP-REVERSIBLE` appear under `consumed` in **every** other
certificate of this stream and under `under_test` in **none**.

That was structural, not an oversight. On the Hamiltonian carriers every
evolution is `exp(tA)` — deterministic and invertible by construction. Those
assumptions *could not fail there*, so they could not be tested. Two of the four
tags in the vocabulary had been carried, never examined.

## A carrier where they can fail

Four states, evolution by column-stochastic matrices over ℚ acting on probability
distributions. The ensemble picture rather than the point picture — closer to how
Carcassi and Aidala set things up, and the setting where the failures are
expressible:

- a **non-deterministic** evolution spreads a point mass over several states;
- an **irreversible** evolution merges distinct states.

| assumption | reading here |
|---|---|
| `deterministic` | a point mass evolves to a point mass — the matrix is the graph of a function |
| `conserves_information` | the uniform (maximum-entropy) ensemble is stationary — discrete Liouville |
| `reversible` | distinct states stay distinct — the underlying map is injective |

This development imports none of the torus modules and shares no definitions with
them.

## The result

```
reversible  ⟺  deterministic ∧ conserves_information
```

**Reversibility is not an independent postulate.** It is exactly the conjunction
of the other two.

Forward: if two states merged, the fibre over their common image would carry mass
two, contradicting the uniform ensemble being stationary. Backward: with the map
injective no fibre carries more than unit mass, and four such masses summing to
four are each exactly one.

Both conjuncts are needed:

| witness | deterministic | conserves info | reversible |
|---|---|---|---|
| collapse — everything → `s0` | ✓ | ✗ | ✗ |
| mixer — every entry `1/4` | ✗ | ✓ | ✗ |

The gate carries a negative control asserting determinism alone suffices; it is
rejected.

## What it says about the stream's vocabulary

Every certificate here has listed `RP-DETERMINISTIC` and `RP-REVERSIBLE` as two
separate consumed assumptions. On this carrier that **overstates how many
assumptions are in play**: determinism plus information conservation already
entails reversibility. The vocabulary was redundant.

This is noted at the definition site (`carriers.py`), not only here — but the
existing listings are **left as they are rather than silently merged**, because
the equivalence is proved for four states and one step, not for the continuous
carriers those certificates use.

It does, though, retroactively explain why the Hamiltonian carriers could bake
reversibility in without loss.

## Ledger

```
Print Assumptions    9/9 this module; 45/45 across five modules
coqchk axioms        <none>
negative controls    5, all rejected
```

## What this does not establish

- **That the equivalence transfers to the Hamiltonian carriers.** Those are
  continuous; this is four states and one step. The transfer is not proved and
  the other certificates' `consumed` lists are unchanged on that basis.
- Anything about continuous state spaces or more than one time step.
- Anything about entropy beyond stationarity of the uniform ensemble — Shannon
  entropy is not formalised.
- That the assumptions are redundant *in general* — only on this carrier.
- Not a reproduction, confirmation, or refutation of Carcassi–Aidala's derivation.
- No quantum, causal, or field-theoretic claim.

## Next gate

`REVERSE_PHYSICS_STOCHASTIC_GENERAL_N` — the proof is written for four states. A
general finite state space needs a pigeonhole argument this development sidesteps
by counting fibre masses over a fixed size.

## Verification

```bash
cd rocq && ./run.sh
PYTHONPATH=. python3 -m reverse_physics.stochastic_rocq --check
```

## Tier receipt

- **Tier 0/1** — five modules compile; gate 10 green / 0 red from a clean tree;
  `coqchk` empty axiom section; six provenance records hash-verified; the G0 and
  general-n certificates regenerated (they hash `carriers.py`, which gained the
  vocabulary note) and both independent rails re-run; 30-test Python suite green.
- **Tier 2 — not run, and not required.** Nothing outside `reverse_physics/` and
  `rocq/` imports or is imported by this work.
- **Tier 3 — not run, and not required.** No freeze, tag, or paper promotion.
