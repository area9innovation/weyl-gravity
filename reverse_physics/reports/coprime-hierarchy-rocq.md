# The coprime-ratio hierarchy: order clause proved, and a parity selection rule

**Certificate** `REVERSE_PHYSICS_COPRIME_HIERARCHY_ROCQ_V1`
**Proofs** `rocq/CoprimeHierarchyOrderLaw.v`, `rocq/CoprimeHierarchyKernelParity.v` — zero axioms
**Gate** `rocq/run.sh` — `RESULT: 20 green (0 red)`
**Upstream** tango `5be183077` — gates, results document, conjecture event
**Preregistration** tango `02d92f069`, committed **before** any computation

---

## Why this one is different

Every previous certificate in this stream tested a carrier built to demonstrate
the method. A reviewer would call that bookkeeping, and would be right.

This one engages the programme's **own open corpus**:
`sf:program/conjecture/coprime-ratio-hierarchy`, standing at
`VERIFIED_ON_FIXTURES` with the `does_not_establish` line *"No ansatz proof
exists"*, five fixtures, and a scoping to `p` odd marked *"pending evidence"*.

That `does_not_establish` line was the work queue.

## 1. The preregistered attack

Predictions committed to git before computing: the `p`-odd scoping is
over-cautious, so even-`p` loci should obstruct at `p+q−2` like everything else.

**Falsified**, in the way the preregistration named as the better outcome.

| locus | predicted | computed through | result |
|---|---|---|---|
| 4:1 | order 3 | 6 | **zero** |
| 4:3 | order 5 | 6 | **zero** |
| 6:1 | order 5 | 6 | **zero** |
| **8:1** | **order 7** | **7** | **zero — at its own predicted order** |
| 8:3 | order 9 | 6 | zero (selection rule only) |
| 6:5 | order 9 | 6 | zero (selection rule only) |

Even `p` is not obstructed at a *different* order. It is **not obstructed at
all**. The scoping is load-bearing.

Nothing the conjecture *claimed* was refuted — what was refuted was my guess
about it. Two preregistered loci (2:3, 2:1) turned out **ill-posed**: the PU
model needs `w1 > w2`. Recorded, not dropped.

## 2. Four new instances

| locus | order | kernel | coefficient |
|---|---|---|---|
| 5:2 | 5 | symmetric | `(3428125/82383485184)·√210·i` |
| 7:2 | 7 | symmetric | `−(907393050914777/74135047090515840000000)·√70·i` |
| 7:3 | 8 | antisymmetric | `−(9485356180222981009/602416626339850223616000000)·√21` |
| 9:1 | 8 | antisymmetric | `−(4769192322628191/4250934993087841592934400000)` |

7:3 and 9:1 are the loci the conjecture names as unchecked. Order 8 is deeper
than anything previously computed in that corpus, where the maximum was 6.

## 3. The order clause, proved

Two facts.

**A word at order `n` has degree exactly `n+2`.** Cubic vertex; the Moyal
bracket of degrees `d₁,d₂` has degree `d₁+d₂−2`; `n` vertices and `n−1` brackets
give `3n − 2(n−1)`. Exactly, not at most.

**At degree `p+q` the resonance has essentially one solution.** Coprimality
forces `n₁−m₁ = kq`, `n₂−m₂ = −kp`; the degree budget forces `|k| ≤ 1`; `k = ±1`
pins the exponents completely to the conversion kernel.

Together the kernel can be carried **only** at `n = p+q−2`, and vanishes
identically below — the order law and the selection rule in one statement.

## 4. The kernel clause, proved and refined

The vertex is `v = −i(cy+isp)³`, a cube of one combination
`u = A(a2+a2b) + B(a1−a1b)`. Under

```
K :   a1 ↔ a1b,    a2 → −a2b,    a2b → −a2
```

`u → −u`: the vertex is odd, `h0` is even, so an order-`n` contribution has
eigenvalue `(−1)ⁿ`. Matching on the kernel gives **symmetric iff `q` even**, and
the other combination is *forbidden*, not merely unobserved.

**The symmetry follows `q`, not the order.** The corpus could not distinguish
these because every fixture had `p` odd; 3:2 is the locus that separates them —
odd order, symmetric kernel.

**And a sub-law nobody had stated:** the radical is `√(w1·w2)` for `q` odd and
`√(w1·w2·sqfree(w1²−w2²))` for `q` even. Nine of nine — and it *predicted* the
absence of a radical at 9:1, where `√(w1w2) = 3`.

## 5. The physics reading — interpretation, not theorem

Flagged as such, and separable from everything above.

The Pais–Uhlenbeck oscillator is the higher-derivative sector in miniature — the
toy model for the fourth-order dynamics that makes Weyl gravity hard. Its two
modes are the healthy one and the ghost.

An obstruction at a `p:q` resonance means the cubic interaction **cannot** be
removed by a canonical transformation: there is a genuine on-shell `q ↔ p` quanta
conversion between the modes. That conversion is the channel through which the
ghost sector talks to the healthy one — the perturbative mechanism of the
instability.

On that reading, the result says: **the ghost-conversion channel is closed at
every even-`p` resonance.** A parity selection rule protects the sector at half
the resonances.

The caveats are severe and I do not want them lost. This is one specific cubic
vertex, in one toy model, perturbatively, and "zero through order 6 or 7" is not
"zero to all orders". PU is a toy for Weyl gravity, not Weyl gravity. Whether
any of this survives to the real theory is exactly the open question, and
nothing here touches the certified BV–BFV complex or the residual classes.

## 6. What is open — and it is sharper than before

**Why the even-`p` coefficient vanishes.** Neither mechanism explains it: the
degree count never mentions `p`'s parity, and the involution constrains *which*
combination appears, not whether its coefficient is nonzero. Both `K₊` and `K₋`
remain allowed at either parity. So the vanishing is **dynamical**.

Before this work the question was *"does the law hold at even `p`?"*. Now it is
*"what makes the even-`p` coefficient vanish?"*, with six loci of evidence that
it does. That is a better question.

Also open: non-vanishing at odd `p` is still observational (nine instances) — the
order law says where an obstruction *can* appear, never that one does. And 8:3
and 6:5 were computed only to order 6, below their predicted 9.

## Verification

```bash
cd rocq && ./run.sh                                   # 20 green (0 red)
PYTHONPATH=. python3 -m reverse_physics.coprime_hierarchy_rocq --check

# upstream, in tango at 5be183077:
cd forge && FORGE_LIB=$PWD/lib /tmp/forgebin -run -I tools/physics-moyal \
    tools/physics-moyal/coprime_parity_gate.forge     # exit 17, ~8 s
cd forge && FORGE_LIB=$PWD/lib /tmp/forgebin verify -full \
    tools/physics-moyal/coprime_parity_gate.forge     # c==native, asan clean
cd forge && FORGE_LIB=$PWD/lib /tmp/forgebin -run -I tools/physics-moyal \
    tools/physics-moyal/coprime_parity_deep.forge     # exit 10, ~42 s
```

## Tier receipt

- **Tier 0/1** — fifteen Rocq modules compile; gate 20 green / 0 red; `coqchk`
  empty axiom section; 109/109 `Print Assumptions` closed; fourteen provenance
  records hash-verified; 30-test Python suite green.
- **Upstream** — fast rail 17/17 with `verify -full` (`c==native`, ASan-clean on
  both backends); certificate-tier rail 10/10. Gates split per AGENTS.md because
  the combined gate exceeded the ten-minute verify budget.
- **Tier 2/3 — not run, and not required.**
