# The truncation gate closes — and it closes without an induction

**Certificate** `REVERSE_PHYSICS_TORUS_ALL_MODES_ROCQ_V1`
**Proof** `rocq/ReversePhysicsTorus.v` — Rocq (Coq) 8.20.1, zero axioms
**Gate** `rocq/run.sh` — `RESULT: 6 green (0 red)` — `GATE: PASS`
**Closes** `REVERSE_PHYSICS_TORUS_ALL_TRUNCATIONS`, opened by the G1 certificate

## What was open

The Forge gate computes the symplectic→Hamiltonian gap on `T⁴` at truncations
N = 0, 1, 2, 3 and finds 4 every time, carried entirely by the zero mode. Four
values of N are not a theorem in N.

## The right theorem is not an induction

I expected to induct over the truncation. That turned out to be the wrong shape.
The statements below are quantified over **all modes**, and since any truncation
is just a set of modes, they subsume every truncation at once — including
infinite ones. No bound on N appears anywhere, and no induction is needed.

The reason is constructive: at a mode with some nonzero frequency, the potential
is **built explicitly** from a direction `m` whose frequency doesn't vanish
(`s := A_m / k_m`, `c := −B_m / k_m`). Nothing about that construction cares how
large the mode is.

## The theorems

Writing a mode's 1-form `α = ι_X ω` as `α_j = A_j cos_k + B_j sin_k`:

| theorem | says |
|---|---|
| `exact_implies_closed` | Hamiltonian ⟹ symplectic, at every mode |
| `closed_at_zero_mode` | at `k = 0` every 1-form is closed |
| `exact_at_zero_mode_iff_vanishing` | at `k = 0` exactness forces vanishing |
| `zero_mode_has_four_independent_classes` | `b₁(T⁴) = 4` in coordinates |
| **`closed_iff_exact_at_nonzero`** | **for every `k ≠ 0`, closed and exact coincide** |
| `nonzero_mode_contributes_no_class` | such a mode contributes nothing to the gap |
| `mode_dichotomy` | every mode is zero or has a nonzero frequency |
| **`gap_is_carried_entirely_by_the_zero_mode`** | **for every `k` and every closed form at `k`: either `k = 0`, or the form is exact** |
| `translation_is_closed_but_not_exact` | the zero mode really does carry something |

The fifth is the heart: **there is no cohomology away from the constants**. The
eighth is the theorem, and it mentions no truncation.

The last one keeps the result from being vacuous — uniform translation
`X = ∂_{q₁}` on `T⁴` is closed and not exact. Deterministic, reversible, volume
preserving globally and per degree of freedom, preserves ω, and admits no global
Hamiltonian.

## The ledger

```
Print Assumptions        9/9 closed under the global context
coqchk axiom section     <none>
type-in-type             <none>
unsafe (co)fixpoints     <none>
assumed positivity       <none>
source                   no Axiom, Parameter, Hypothesis, Conjecture, Admitted, admit
```

Six gate checks, including a **fail-closed negative control**: a deliberately
false claim — that uniform translation *is* exact at the zero mode — must be
rejected by `coqc`, and is. A gate that accepted it would prove nothing.

## What is now proved versus computed

This is the honest split, and it matters:

| | status |
|---|---|
| symplectic/Hamiltonian structure, all modes | **proved** (zero-axiom Rocq, kernel-rechecked) |
| the marginal and volume-preserving levels | computed only (Forge gate, N ≤ 3) |
| the per-mode rank computations | computed only |
| the arithmetic summing per-mode dims into the report's totals | computed only |

So the *topological step* of the chain is proved for all truncations; the rest of
the four-level chain is still exact computation at N ≤ 3.

## What this does not establish

- The marginal or volume-preserving levels — only closed/exact is formalised.
- Anything about a general symplectic manifold; the model is flat `T⁴`.
- Anything about non-polynomial vector fields.
- Not a reproduction, confirmation, or refutation of Carcassi–Aidala's derivation.
- **Not an equivalence in the reverse-mathematics sense.** Proving one implication
  in Rocq is not a reversal over a base theory. `EQUIVALENCE_CERTIFIED` remains
  unreached, and this certificate does not move the lifecycle toward it.
- No quantum, causal, or field-theoretic claim.

## Next gate

`REVERSE_PHYSICS_TORUS_FULL_CHAIN_ROCQ` — formalise the marginal and
volume-preserving levels too, so the whole four-level chain is proved rather than
computed.

## Verification

```bash
cd rocq && ./run.sh
PYTHONPATH=. python3 -m reverse_physics.torus_all_modes_rocq --check
```

The provenance record fails closed: if `ReversePhysicsTorus.v` or `run.sh` no
longer hashes to the recorded digest, `--check` refuses.

## Tier receipt

- **Tier 0/1** — `coqc` exit 0; `rocq/run.sh` 6 green / 0 red; `coqchk` standalone
  kernel re-check with an empty axiom section; provenance record byte-deterministic
  and hash-verified; the 30-test Python suite unaffected and still green.
- **Tier 2 — not run, and not required.** Nothing outside `reverse_physics/` and
  `rocq/` imports or is imported by this work.
- **Tier 3 — not run, and not required.** No freeze, tag, or paper promotion.
