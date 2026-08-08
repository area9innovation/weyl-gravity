# Can a loop generate positive charge?

**Certificate** `REVERSE_PHYSICS_CHARGE_GRADING_LOOP_STABILITY_V1`
**Verifier** `reverse_physics/charge_grading_loop_stability.py --check` — 8 checks, all PASS (0.1 s)
**Dependency tag** `LOCAL-ALGEBRAIC` · **Lifecycle** `CLASSIFIED`

> The cheap question that had to be answered before the expensive one. If the
> answer had been yes, the whole loop extension was dead and no amount of
> infrared work would have saved it.

---

## The question

Bateman–Turok's positivity proof rests on one hypothesis: *"the R_t homomorphism
does not yield any positively charged operators"*, which is what makes the
negatively-charged part null in the trace. They prove positivity **at tree
level** and name their own obstacle — *"like QCD, the massless theory has
collinear infrared divergences which affect asymptotic states."*

So: is the hypothesis even **stable under loops**? A one-loop process operator
with a positive-charge component would break the mechanism regardless of
regulator.

## The answer: no, and it is structural

Two facts, both read off their Eq. (14) and their Wightman function:

1. **The vertex is charge neutral.** `S₁,₁ = ∫[∂Ω∂Υ + ½λ²Ω²Υ²]`, with
   `q(Ω) = +1`, `q(Υ) = −1` under `(Ω,Υ) → (e^σΩ, e^{−σ}Υ)`. So the quartic
   carries `q = 2(+1) + 2(−1) = 0`.
2. **The propagator is purely off-diagonal.** The kinetic term `∂Ω·∂Υ` gives
   quadratic form `[[0,1],[1,0]]`, whose inverse is again `[[0,1],[1,0]]`. Their
   Wightman function agrees: `W^{ΩΥ} = W^{ΥΩ} = θ(p⁰)δ(p²)`, `W^{ΩΩ} = W^{ΥΥ} = 0`.
   So **every** Wick contraction pairs one `Ω` with one `Υ` and is itself neutral.

Neutral vertices plus neutral contractions give the grading theorem:

> **The charge of a process operator is fixed by its external legs and is
> independent of loop order.**

Loops *dress* an operator; they cannot move it up the charge ladder. A
tree-level image with charges ≤ 0 stays at charges ≤ 0 to all orders.

Verified by direct enumeration of every partial matching for all external
contents up to four legs and up to two vertex insertions — the surviving charge
set is always exactly `{charge(external)}`.

## Corollary: which regulator to use

Paper 05 records `m±² = μ² ± √(εg)` for a regulated Lagrangian carrying an IR
mass `μ²ΩΥ` and a regulator `(ε/2)Ω²`. One line of charge arithmetic separates
them:

| term | charge | grading | degeneracy |
|---|---|---|---|
| `μ²ΩΥ` | **0** | preserved | preserved — at ε = 0 both poles sit at `μ²` |
| `(ε/2)Ω²` | **+2** | broken (hence `cprop:embedding`'s *"exact iff ε = 0"*) | broken — splits by `2√(εg)` |

One parameter, both damages, for one reason. So **`μ²ΩΥ` is a
degeneracy-preserving, grading-preserving infrared mass** — the kind the loop
extension needs, and which Bateman–Turok describe as not yet supplied.

## Where the risk moved

The grading argument is classical bookkeeping. It assumes the `SO⁺(1,1)` charge
survives quantization — and that is a **global** symmetry, which can be
anomalous. Bateman–Turok themselves flag that the `φ` and `(Ω,Υ)` path integrals
are inequivalent, *"the former integrates over Ω > 0 whereas the latter
integrates over all Ω"*, so the measure is exactly where such an anomaly would
live.

**Is the O(1,1) boost charge anomalous at one loop?** That is the successor
question. It is not answered here, and it is tractable with the anomaly
machinery already in `quantum-weyl/`.

## Controls

A diagonal propagator (`⟨ΩΩ⟩ ≠ 0`) and a charge-carrying vertex (`Ω³Υ`) each
break the theorem, and are verified to do so — the enumeration detects charge
movement when it is there. The enumeration is checked non-vacuous.

## What this does not establish

- **Not the loop extension.** No loop integral is computed, no infrared
  divergence regulated, nothing resummed.
- **Not** that the charge is non-anomalous — that is the open successor.
- **Nothing about the tensor case.** This is the Bateman–Turok **scalar** model;
  Weyl gravity is the gauge-invariant tensor version.
- Nothing `LORENTZIAN-CAUSAL`, and nothing about `g−2`.
