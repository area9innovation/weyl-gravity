# `RP-DIFF` has a witness — and the derived derivative order needs it

**Certificate** `REVERSE_PHYSICS_DIFF_INDEPENDENCE_V1`
**Rail** `reverse_physics/diff_independence.py` — 11/11 checks, two independent
rank routines, control space validated
**Closes** the gap declared in [`PHYSICS-VS-MATH.md`](PHYSICS-VS-MATH.md) §6
**Dependency tag** `LOCAL-ALGEBRAIC`

---

## 1. The gap, and why it was a carrier artifact

The separation ledger recorded one assumption as having no independence witness
at all:

> **`RP-DIFF` is invisible.** It is what makes "the space of curvature scalars"
> the right space at all, so it never appears as a row in a matrix. That is a
> real gap: an assumption doing structural work should still get a witness.

That diagnosis is correct, and it is a statement about the **carrier**, not
about the assumption. The stream has hit this exact shape once before. `§4.2`:
`RP-REVERSIBLE` *"appeared under `consumed` in every certificate and
`under_test` in none — structurally, because on the Hamiltonian carriers every
evolution is `exp(tA)` and neither determinism nor reversibility can fail."*
The fix was not cleverness about the old carrier. It was **moving to a carrier
where the assumption can fail**.

The classification's carrier is *quadratic curvature scalars* — diff-invariant
**by construction**, since every element is built from tensors and fully
contracted. `RP-DIFF` cannot fail inside it, so no witness can exist there. That
is a property of the arena, not evidence about the assumption.

## 2. The enlarged carrier

Drop the contraction requirement. Take **local densities built algebraically
from the metric components**, at derivative order zero. These are perfectly good
local functionals of the metric; they are simply not covariant, which is exactly
the property under test.

Under `g → λg` one has `h ≡ g⁻¹ → λ⁻¹h`, `g → λg`, `√−g → λ²√−g`, so

```
√−g · hⁿ · gᵐ    has Weyl weight   2 − n + m
```

and Weyl invariance is exactly `n − m = 2`. At derivative order zero there are
**no derivatives of the conformal factor**, so weight zero *is* invariance — no
inhomogeneous terms. That is what makes this order both decisive and cheap.

## 3. The computation

The lowest weight-zero degree is `(n,m) = (2,0)`, i.e. `√−g h^ab h^cd`.
Classified **completely**, not sampled:

| | |
|---|---|
| Weyl-invariant space | **55**-dimensional (all of it) |
| Diffeomorphism-invariant subspace | **0**-dimensional |

Diff-invariance at a point, for a density with no derivatives, is invariance
under the `GL(4)` action on the metric. It is imposed here by computing the
kernel of the sixteen generators exactly over ℚ, by **two independent rank
routines** (Gauss–Jordan and fraction-free Bareiss, the repository's rail-A /
rail-B convention). Rank 55 of 55; the rails agree.

The zero has a reason: the only `GL`-invariant algebraic function of a single
nondegenerate symmetric form is a constant, and a constant times `√−g` has
weight `2`, not `0`.

**So every one of the 55 is an independence witness.** An explicit one:

```
√−g (g⁰⁰)²
```

local ✓, metric-only ✓, `D = 4` ✓, parity-even ✓, Weyl-invariant (weight
`2−2+0 = 0`) ✓, not topological ✓ — and **not** diffeomorphism-invariant. Seven
of the sixteen `GL(4)` generators move it, so it is not accidentally in the
kernel.

### Why the zero isn't a bug

A zero-dimensional answer from an invariance computation is exactly the kind of
result that is a bug. So the **identical machinery** is run on a control space
whose invariants are known: the bilinears `h^ab g_cd`, whose `GL`-invariants are
one-dimensional, spanned by the trace `h^ab g_ab = 4`.

It returns **1**. The machinery finds invariants when invariants exist.

## 4. The consequence, which is the point

The witness sits at **derivative order zero**.

The stream's best result is that the derivative order is *derived*, not assumed:
`D − 2k = 0` forces `k = D/2`, hence four derivatives at `D = 4`. §4.3 calls it
*"not an assumption at all — the standard motivation uses one more physical
input than it needs."*

That derivation runs through `G3`, the conformal weight of the **Weyl tensor** —
a curvature scalar, hence already diff-covariant. Drop `RP-DIFF` and the
derivation has nothing to run on. And here is an explicit Weyl-invariant local
metric density with **zero** derivatives, which `k = 2` forbids.

> **The derived derivative order requires `RP-DIFF`.**

An assumption the ledger recorded as carrying *no witness at all* turns out to
be load-bearing for the stream's best result. This does not weaken §4.3 — the
derived order stands. It **names the input §4.3 was silently using.**

## 5. What this does not establish

Written out because the temptations are obvious.

- **Only derivative order zero, and only the lowest weight-zero degree `(2,0)`.**
  The degrees `(3,1)`, `(4,2)`, … are also weight zero and are *not* classified
  here. The order-zero space is infinite-dimensional as a polynomial algebra;
  only its lowest graded piece is settled.
- **No claim that any witness is a sensible theory.** A witness need not be.
  `R²` witnesses `RP-WEYL` and nobody proposes `R²` gravity. Sensibleness is not
  the test; satisfying the *other* assumptions while failing this one is.
- **The Stückelberg escape is blocked, not refuted.** Promote the coordinates to
  fields and any non-covariant theory becomes covariant — but that needs a
  second field, which `RP-METRIC` forbids. So what is established is the
  independence of `RP-DIFF` **given `RP-METRIC`**. The two assumptions are
  entangled, and that is recorded rather than hidden.
- **Nothing quantum.** This repository's quantum chain separately computes that
  the pure-`Diff` anomaly cohomology vanishes in `D = 4`. That is a different
  question at a different level, it is **not** used as evidence here, and this
  is not evidence for it.

## 6. Where the ledger stands now

`RP-DIFF` moves from *"no witness — the largest genuine hole"* to **witnessed,
with a stated conditional (`given RP-METRIC`) and a named consequence**.

It also joins the list in §4 as a seventh instance of the separation changing
the answer — and it is the first one where the thing that changed was an
assumption previously believed to be untestable in principle.

---

## Verification

```bash
PYTHONPATH=. python3 -m reverse_physics.diff_independence --check
# Weyl-invariant 55, Diff-invariant 0 (rails agree), control 1, 11/11, PASS
```

Pure `fractions.Fraction` arithmetic; no sympy, no floating point. Runs in
under a second.
