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

## Correction: quadratic preflight is not vacuum compatibility

Paper 05 records `m±² = μ² ± √(εg)` for a quadratic form carrying
`μ²ΩΥ` and `(ε/2)Ω²`. One line of charge arithmetic separates them, but only at
a held background:

| term | charge | grading | held-background degeneracy | vacuum compatibility |
|---|---|---|---|---|
| `μ²ΩΥ` | **0** | preserved | preserved — both formal poles sit at `μ²` | **fails:** `∂_ΥV|(v,0)=vμ²` |
| `(ε/2)Ω²` | **+2** | broken (hence `cprop:embedding`'s *"exact iff ε = 0"*) | broken — splits by `2√(εg)` | fails exact boost invariance |

The earlier conclusion that `μ²ΩΥ` names the regulator the loop extension
should use is withdrawn. The exact
[`BT_IR_REGULATOR_TRILEMMA`](bt-ir-regulator-trilemma.md) shows that stationarity
of an invariant `V=F(ΩΥ)` at `(v,0)` forces `F′(0)=0`, hence a massless double
root. Moving the mass-deformed theory to its true stationary branch instead
gives one massless and one massive simple root. The charge theorem above is
unchanged; it never implied vacuum compatibility.

## Where the work moved

The primary infrared gate is now a non-mass architecture: dimensional or
off-shell regulation, inclusive/KLN cancellation, or dressed asymptotic
states. The concrete next test is whether the negative-charge trace radical is
closed under the first collinear inclusive sum.

Separately, the grading argument is classical bookkeeping. It assumes the
`SO⁺(1,1)` charge survives quantization, so **is the boost charge anomalous at
one loop?** remains an open measure question rather than the sole successor.

## Controls

A diagonal propagator (`⟨ΩΩ⟩ ≠ 0`) and a charge-carrying vertex (`Ω³Υ`) each
break the theorem, and are verified to do so — the enumeration detects charge
movement when it is there. The enumeration is checked non-vacuous.

## What this does not establish

- **Not the loop extension.** No loop integral is computed, no infrared
  divergence regulated, nothing resummed.
- **Not a vacuum-compatible infrared mass.** The neutral candidate fails the
  stationary-vacuum test in the trilemma certificate.
- **Not** that the charge is non-anomalous — that is the open successor.
- **Nothing about the tensor case.** This is the Bateman–Turok **scalar** model;
  Weyl gravity is the gauge-invariant tensor version.
- Nothing `LORENTZIAN-CAUSAL`, and nothing about `g−2`.
