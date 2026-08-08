# Bateman–Turok vs Mannheim: one premise slot, two fillings, five levels

**Certificate** `REVERSE_PHYSICS_BATEMAN_VS_MANNHEIM_LEDGER_V1`
**Verifier** `reverse_physics/bateman_vs_mannheim_ledger.py --check` — 9 checks, all PASS
**Dependency tag** `LOCAL-ALGEBRAIC` · **Lifecycle** `CLASSIFIED`

> Are they complementary, overlapping, or alternative reverse-physics options?
> **All three, at different levels** — and the level axis is what makes that a
> result rather than an evasion.

---

## 1. Why a level axis is forced

The same sentence flips truth value:

```
"the two completions agree"     TRUE  at the free level
                                FALSE in the interacting theory
```

Both truth values are already proved in this tree, which is what forces the
axis — exactly as in [`weyl_vs_einstein_ledger`](../weyl_vs_einstein_ledger.py),
where "Einstein gravity is contained in Weyl gravity" is true at the solution
level and false at the symplectic level.

- **Free** — Paper 04, `thm:bridge4`: the two completions *"induce the same
  complex quasifree functional on the gauge-invariant observable algebra `𝔄_inv`;
  they differ in involution and completion only."*
- **Interacting** — Paper 05, `cprop:krein`: Krein pseudo-unitarity is exact **on
  the same matrix elements** where every positive pointed metric is obstructed.
  They *separate*.

A comparison stated without the level column doesn't merely lose precision — it
contradicts itself.

## 2. The crux: one slot

Both programmes accept the same action, the same complex spectral covariance, and
the same non-negative-energy requirement. They differ in exactly one premise:

> **Which involution is physical?** — i.e. which operators are required to be
> self-adjoint.

| | Mannheim | Bateman–Turok |
|---|---|---|
| **filling** | positive definite | indefinite (Krein) |
| **requires** | diagonalizable ∧ real spectrum (`ghost_harmless`) | a charge grading with one-sided charge (`lem:chargenull`, `cprop:embedding`) |
| **price** | the field is rotated into the complex plane — Paper 06's *quarter-turn*; his own *"replace z by y = −iz"* | the Born rule is generalized to `tr(A†A)` |
| **field stays real** | **no** | **yes** — Paper 06: *"retains standard gravitational reality"* |

So these are **not two theories**. They are **two real forms of one complex
structure**, and choosing between them is choosing an involution.

## 3. The ledger

| level | | direction |
|---|---|---|
| **L1** | action and classical field equations | SHARED |
| **L2** | free state space and observables | SHARED — provably identical on `𝔄_inv` |
| **L3** | the coincident-pole (Jordan) point | **BT opens** |
| **L4** | interacting theory, second order | **BT opens** |
| **L5** | loops at the coincident point | **both stop** ← commonly misread |

**L3** — the positive metric has no nondegenerate continuation through `c₁ = 0`,
the similarity transformation is singular in the equal-frequency limit, and only
the Krein real form continues (Paper 04, `thm:term`). Mannheim's own §VI withdraws
the cutting rules there.

**L5 is the row people get wrong.** At loop level, at the coincident point,
*neither* programme has a result. Mannheim's cutting rules are withdrawn there by
his own §VI; Bateman–Turok prove positivity at **tree level only** and name
collinear infrared divergence as their obstacle. The literature reads each as
having settled the question. At the level that matters for Weyl gravity — whose
propagator *is* `1/k⁴`, a coincident-pole theory — both are open, and open for
unrelated reasons.

## 4. Why complementary rather than redundant

Reverse physics asks for independence witnesses: drop the premise, and see
whether anything still satisfies the rest. Each programme is the survivor of the
*other's* failure, and both witnesses are already computed here:

| drop | witness | survivor |
|---|---|---|
| **diagonalizable** (Mannheim) | the coincident-pole point — exactly where `1/k⁴` sits | Bateman–Turok |
| **one-sided charge** (BT) | split mass, ε ≠ 0, where both charge signs appear | Mannheim |

Neither premise is generic. Each is a boundary condition — and they are boundary
conditions on **different boundaries**. That is what complementarity means here,
and it is why neither camp can simply absorb the other.

## 5. Cross-fertilization

**(1) BT → Mannheim — concrete, and it is a candidate cure for exactly his
disease.** Mannheim's failure at coincident poles is that the cut weight becomes
`−δ′(s−m)`, which is no measure of any sign. That pathology belongs to the
**fourth-order variable**, not to the theory: the O(1,1) embedding replaces one
fourth-order field by two second-order fields with an off-diagonal propagator, so
the poles are simple and the cuts are ordinary delta functions. The double pole
is dissolved by a change of variables. That is why BT reach tree level at the very
point where Mannheim stops — and it suggests his programme could be continued
past §VI in their variables rather than his.

**(2) Mannheim → BT — speculative, and flagged.** BT's obstacle is collinear
infrared divergence *"affecting asymptotic states"*; PT/C machinery constructs
inner products where the naive one fails. Whether that bears on an *infrared*
rather than a *signature* problem is not established, and is not claimed.

**(3) This repository → BT — concrete.** `μ²ΩΥ` is a charge- **and**
degeneracy-preserving infrared mass — the regulator their loop extension needs.
`(ε/2)Ω²` destroys both, for the single reason that it carries charge +2
([`charge-grading-loop-stability`](charge-grading-loop-stability.md)).

**(4) Paper 04 → both — discipline.** Because the completions induce the same
functional on the gauge-invariant algebra, **any free-field-level dispute between
the camps is about the involution, not about predictions.** That retires a large
class of arguments without settling the physical question.

## 6. What this means for the programme

The decisive question is not "Mannheim or Bateman–Turok". At the point Weyl
gravity actually occupies, **only one structure survives nondegenerately** (L3),
and that structure's own gap is loops plus infrared (L5).

So the live question is **BT's loop extension**, and the charge sector has already
been cleared as an obstacle to it. What remains is the infrared, and — one step
before that — whether the O(1,1) charge is anomalous at one loop.

## 7. What this does not establish

- **No adjudication.** Every row points at a result proved elsewhere in this tree
  or quoted from the sources.
- **No new physics.** The contribution is the axis, the identification of the
  single contested slot, and placing the two independence witnesses on one page.
- The speculative Mannheim → BT transfer is **not** established.
- Nothing `LORENTZIAN-CAUSAL`.
