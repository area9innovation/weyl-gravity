# Brief: the `D = 6` cubic invariant count, in Forge

**Blocks** `REVERSE_PHYSICS_WEYL_ACTION_D6_V1`, whose `D = 6` quotient is `CITED`
**Target** compute it, and make the parity half answerable
**Substrate** Forge (`tango`), not Python — per the standing preference

This is a work brief, written to be executed after a compaction. It records what
exists, the route that avoids the hard part, the sub-tasks, and the controls.

---

## 1. What the blocker actually was, and why it dissolves

`weyl-action-d6.md` named the blocker as

> a basis of cubic curvature invariants **modulo total derivatives and
> dimension-dependent identities**

and called it a substantial build — Bianchi reductions, dimension-dependent
identities at cubic order. That is true **of the symbolic route**.

**The pointwise route does not need any of it.** Evaluate every candidate
contraction at enough exact metrics and take the **rank over ℚ**. Every identity
— Riemann symmetries, first and second Bianchi, dimension-dependent identities —
makes the evaluations linearly dependent *automatically*. The rank quotients by
all of them without any of them being written down.

And the quotient by total derivatives is **not needed for this question**. The
three `D = 6` invariants are *type-B*, meaning **pointwise** conformal
invariants; the Euler density `E₆` is *type-A* and is not pointwise invariant.
So a pointwise computation should return **exactly 3**, with `E₆` correctly
absent. The number we want is the one the pointwise route naturally gives.

## 2. What Forge already has

| | |
|---|---|
| `lib/math/curvature.forge` | exact Christoffel / Riemann / Ricci / scalar over any `Field<T>`, **dimension-general** (takes `n`), via truncated Taylor jets about an exact rational base point. Exact automatic differentiation over ℚ — no CAS, no floats |
| `lib/math/qmat.forge` | exact rational matrices: `qm_rank`, `qm_rref`, `qm_nullspace`, `qm_solve`, `qm_det` |
| `lib/math/jet.forge` | the jet ring the curvature layer runs on |
| `lib/math/tensor.forge` | the tensor layer underneath |
| `examples/weyl_action_classification_gate.forge` | **the `D = 4` classification already in Forge**, 40/40 |

So the arithmetic, the curvature, and the rank machinery all exist. What is
missing is one substrate gap and the enumeration.

## 3. The one substrate gap — and it is the Jacobian-goal piece

`curvature.forge` computes the inverse metric only for **diagonal** metrics
(`metric_inverse_diag`), and *refuses* a metric with a nonzero off-diagonal
constant term rather than silently pretending. That refusal is correct and it is
the blocker here: **diagonal metrics in `D = 6` are too special** — they will
make distinct invariants coincide and understate the rank, which is exactly the
non-degeneracy trap this stream has hit repeatedly.

> **Sub-task S1 — general metric inverse over the jet ring.** Gaussian
> elimination over `Jet<T>`, exact wherever the constant-term matrix is
> invertible. This is a genuine substrate improvement, reusable well beyond this
> result, and it is the natural next increment for `curvature.forge`.

## 4. The route

**S1** general (non-diagonal) metric inverse over the jet ring → `curvature.forge`

**S2** enumerate candidate cubic contractions of three Riemann tensors. 12
indices, contracted in 6 pairs. **No symmetry reduction is needed** — redundancy
is what the rank removes. Enumerate generously; over-counting costs rank-matrix
columns, not correctness.

**S3** evaluate each candidate at `M` exact non-diagonal `D = 6` metrics,
generic enough to avoid degeneracy. Build the `candidates × M` rational matrix.

**S4** `qm_rank` → the dimension of the pointwise cubic invariant span.

**S5** impose pointwise Weyl invariance: evaluate each candidate at `g` and at
`e^{2σ}g` for **non-constant** exact `σ`, form the variation, and take
`qm_nullspace` → the invariant subspace.

**S6** report the dimension. **Expected: 3.**

## 5. Controls — and this is where the result is won or lost

Every one of these is a check this stream has learned to need the hard way.

- **`D = 4` known-answer control.** Run the *quadratic* version of the same
  pipeline in `D = 4`. It must return the coordinate space as **3-dimensional**
  and the pointwise conformal invariant subspace as **1-dimensional** (`C²`).
  If the pipeline cannot reproduce the result this stream already computed by a
  different route, nothing downstream is trustworthy.
- **Metric non-degeneracy, reported per metric.** Ricci-flat, conformally flat
  and Einstein metrics each make whole families of invariants vanish or
  coincide. Every metric must report what it can and cannot see, exactly as
  `weyl_dual_discharge` and `weyl_trace_law` do — a rank computed only on
  degenerate metrics is an *understatement*, and it will look like a clean
  answer.
- **Rank saturation.** Increase `M` until the rank stops growing, and report the
  `M` at which it saturated. A rank that is still climbing when you stop is a
  lower bound presented as an answer.
- **Two independent rank routines** (the rail-A / rail-B convention), or `qm_rank`
  cross-checked modulo several primes.
- **A negative control that must fail:** feed a combination known *not* to be
  conformally invariant (e.g. `R³` alone) and require the invariance test to
  reject it.
- **`E₆` must be absent** from the pointwise-invariant subspace. If it appears,
  the invariance test is testing the wrong thing.

## 6. What success looks like, and what it does not

**Success:** `REVERSE_PHYSICS_WEYL_ACTION_D6_V1`'s `D = 6` row moves from `CITED`
to `COMPUTED`, and the parity half becomes answerable by the same pipeline with
`ε`-carrying candidates.

**Not success:** a number that matches the literature obtained on degenerate
metrics, or without the `D = 4` control passing first. Matching a cited number is
*weak* evidence when the number was known in advance — the controls are what
make it evidence at all.

**Still not established afterwards:** the quotient by total derivatives (not
needed for type-B, but needed if the question ever becomes about Lagrangians),
`D > 6`, and anything about Weyl gravity's dynamics.

## 7. Shared-tree discipline

`tango` is a shared worktree. Commit only by explicit pathspec; never `git add
-A`, never `--amend`, never force. `s-f git status` before starting; the Science
Forge status is authoritative because concurrent commits leave the shared index
stale.

---

**Entry point after compaction:** read this file, then
`tango/forge/lib/math/curvature.forge` (the diagonal-inverse refusal at
`metric_inverse_diag`) and `tango/forge/examples/weyl_action_classification_gate.forge`
(the `D = 4` pipeline to mirror). Start with **S1**, since everything else waits
on non-diagonal metrics.
