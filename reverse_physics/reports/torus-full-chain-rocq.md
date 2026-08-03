# The full chain is proved — and the two carriers agree on where the gap lives

**Certificate** `REVERSE_PHYSICS_TORUS_FULL_CHAIN_ROCQ_V1`
**Proof** `rocq/ReversePhysicsTorusChain.v` — Rocq 8.20.1, zero axioms
**Gate** `rocq/run.sh` — `RESULT: 7 green (0 red)` — `GATE: PASS`
**Closes** `REVERSE_PHYSICS_TORUS_FULL_CHAIN_ROCQ`

## What was open

The topological step was proved for all modes. The other two levels —
`symplectic ≤ marginal ≤ volume-preserving` — were still only computed, by the
Forge gate, at N ≤ 3.

## Proved

| theorem | says |
|---|---|
| `hamiltonian_implies_symplectic` | Hamiltonian ⟹ preserves ω |
| `symplectic_implies_marginal` | preserves ω ⟹ each DOF preserves its own area |
| `marginal_implies_volume` | per-DOF ⟹ total volume |
| `the_chain` | all three, at every mode |
| `marginal_not_symplectic` | `X = cos(2πq₂)∂_{q₁}` is marginal and volume preserving but does **not** preserve ω |
| `volume_not_marginal` | `X = cos(2π(q₁+q₂))(∂_{q₁} − ∂_{q₂})` preserves total volume while **neither** DOF preserves its own |

Both strictness witnesses matter: an inclusion chain that silently collapsed
would make the whole separation vacuous. The gate enforces this — one of its
negative controls is a false proof that `marginal ⟹ symplectic`, which must be
and is rejected.

## The structural payoff — the two carriers agree

`symplectic_implies_marginal` turns out to consume only **two of the six**
closedness equations: the **intra**-degree-of-freedom pairs `(q₁,p₁)` and
`(q₂,p₂)`. The other four — the inter-DOF pairs — are exactly what the marginal
condition cannot see, and `marginal_is_exactly_the_intra_dof_content` proves they
are not recoverable from it.

That is the torus counterpart of the G0 finding on the linear carrier, where the
residual obstruction sat precisely in the inter-DOF block `J A₁₂ = −(A₂₁)ᵀ J`.

**Two structurally different carriers — a vector space and a compact manifold,
one measured by rank and the other by cohomology — localise the gap in the same
place.** What a per-degree-of-freedom condition cannot express is inter-degree-of-freedom
coupling. That was a conjecture across the G0 and G1 reports; it is now a theorem
on both sides.

## Ledger

```
Print Assumptions     18/18 across both modules, closed under the global context
coqchk axioms         <none>
source                no Axiom/Parameter/Hypothesis/Conjecture/Admitted/admit
negative controls     2, both rejected by coqc
```

## A pin repair, recorded rather than hidden

Extending `run.sh` to drive the second module tripped the fail-closed hash check
on `REVERSE_PHYSICS_TORUS_ALL_MODES_ROCQ_V1`, which had pinned the gate script
alongside the proof. `ReversePhysicsTorus.v` is byte-identical (`634eacc8…`), so
no theorem changed — only the harness grew. The repair is recorded in that
certificate's `provenance.pin_repair`, with the previous hash preserved.

The lesson is recorded too: **pinning a harness script alongside the mathematics
couples a certificate to changes that cannot affect its claims.** This new
certificate pins only the `.v` and names `run.sh` without hashing it.

## What is now proved versus computed

| | status |
|---|---|
| the inclusion structure, all modes | **proved** |
| both inclusions strict, all modes | **proved** |
| the topological step, all modes | **proved** (previous certificate) |
| per-mode **dimensions** (4, 2, 6, 8−2d) | computed only |
| the totals in the G1 report | computed only |

So the whole *structure* of the G1 result is proved; the *dimension counts* are
still exact computation at N ≤ 3.

## What this does not establish

- The per-mode dimensions or the report's totals.
- Anything about a general symplectic manifold, or non-polynomial fields.
- Not a reproduction, confirmation, or refutation of Carcassi–Aidala's derivation.
- **Every theorem in this stream is an implication.** There is still no reversal
  over a base theory anywhere, so `EQUIVALENCE_CERTIFIED` remains unreached and
  this certificate does not move toward it.
- No quantum, causal, or field-theoretic claim.

## Next gate

`REVERSE_PHYSICS_REVERSAL` — the standing gap. A reverse-mathematics result needs
a base theory and a derivation of an assumption *from* the law. Nothing in this
tree has one.

## Verification

```bash
cd rocq && ./run.sh
PYTHONPATH=. python3 -m reverse_physics.torus_full_chain_rocq --check
```

## Tier receipt

- **Tier 0/1** — both modules compile; gate 7 green / 0 red from a clean tree
  (`.vo` removed first); `coqchk` empty axiom section; both provenance records
  hash-verified and byte-deterministic; 30-test Python suite green.
- **Tier 2 — not run, and not required.** Nothing outside `reverse_physics/` and
  `rocq/` imports or is imported by this work.
- **Tier 3 — not run, and not required.** No freeze, tag, or paper promotion.
