# reverse_physics/ — assumption-necessity certificates

A probe, not an established stream. It asks whether this programme's certificate
substrate can carry **reverse physics** in the Carcassi–Aidala sense: not
deriving laws from axioms, but finding the minimal physical assumptions a law is
equivalent to.

## What transfers, and what does not

Reverse physics needs three things. This substrate supplies two of them.

| | |
|---|---|
| **Sufficiency** — assumptions ⊢ law | a derivation. **Not supplied here.** No proof assistant, no base theory. |
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

Only the first two are reachable with the rails available today.
`EQUIVALENCE_CERTIFIED` requires a reversal over a base theory and is currently
unreachable by construction.

## Contents

```
exact_linalg.py                        exact rational kernel; two independent rank routines
carriers.py                            declarations only — Ω, the DOF split, the witnesses
hamiltonian_privilege_linear_g0.py     rail A: dimensions from constraint ranks
verify_hamiltonian_privilege_linear_g0.py
                                       rail B: dimensions from spanning sets, Bareiss, Leibniz
schema/                                the certificate schema
certificates/                          the emitted certificate
tests/                                 falsification + mutation tests
reports/                               the human-readable entry
```

## The G0 result

`REVERSE_PHYSICS_HAMILTONIAN_PRIVILEGE_LINEAR_G0_V1` — see
[`reports/hamiltonian-privilege-linear-g0.md`](reports/hamiltonian-privilege-linear-g0.md).

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
