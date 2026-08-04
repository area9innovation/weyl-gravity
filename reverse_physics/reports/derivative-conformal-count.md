# The derivative sector, and the `D = 6` count reaching three

**Certificate** `REVERSE_PHYSICS_DERIVATIVE_CONFORMAL_COUNT_V1`
**Rail** Forge, `tango/forge/examples/curvature_invariants_deriv_gate.forge` — 33/33
**Dependency tag** `LOCAL-ALGEBRAIC`

> **This is a lower bound that equals the cited value**, not a proof of exactness.
> §5 says where a fourth invariant could still hide.

---

## 1. What was left open

[`cubic-conformal-count.md`](cubic-conformal-count.md) counted the weight-6 pointwise
conformal invariants **cubic in Riemann with no derivatives** and got `2` in `D = 6`,
against a cited `3`. It located the boundary rather than contradicting the citation:

> *"type-B" means **pointwise conformal invariant**. It does **not** mean "carries no
> derivatives of the curvature."*

Two of the three cited type-B invariants are complete contractions of three Weyl tensors —
the earlier rail builds both and shows they span the whole invariant space it could see —
and **the third is not in that class**. So the open edge was the derivative sector.

## 2. What comes out

Adding the two derivative shapes at weight 6 — `∇R ∇R` and `R ∇∇R`:

| | cubic span | cubic invariants | **with derivatives** |
|---|---|---|---|
| `D = 4` | 6 | 1 | **2** |
| `D = 5` | 7 | 1 | **2** |
| `D = 6` | 8 | 2 | **3** |

Two things, and the second is the one I'd have missed:

- **`D = 6` reaches three.** The cited count is now matched by an independent computation
  rather than referenced.
- **The derivative sector supplies exactly one more invariant in *every* dimension.**
  Not a `D = 6` special effect. `D = 4` and `D = 5` were not predicted and came out `2`.

## 3. Why matching a cited number counts as evidence here

It usually doesn't. The brief that started this stream said so itself: *matching a cited
number is weak evidence when the number was known in advance.* What carries the weight is
everything that **wasn't** known in advance:

- **the `D = 4` and `D = 5` counts** — no prediction, both came out `2`;
- **the uniform `+1`** across three dimensions;
- **the cubic sub-counts.** The gate recomputes the cubic span (`6, 7, 8`) and the
  cubic-only invariant count (`1, 1, 2`) through a *different candidate pipeline* and has
  to reproduce the separately committed certificate. It does, exactly. That is a
  cross-check between two implementations, not a restatement of one.

## 4. The derivative layer is certified before it is used

`∇R` and `∇∇R` are new machinery, and there is no second implementation to compare
against — so the layer is checked against identities it cannot satisfy by accident
(`curvature_covderiv_gate`, 23/23, in `D = 4, 5, 6`):

- **the second Bianchi identity** on `∇R` — linear, and it fails under almost any index or
  sign error;
- **the Ricci commutator** on `∇∇R`, expanded as four Riemann contractions. **Nonlinear**,
  so it tests the second derivative, the index bookkeeping of the second application, and
  the sign convention together;
- **the differentiated second Bianchi identity** — needed because the commutator
  *antisymmetrises*, and therefore cancels any error symmetric in the two derivative
  indices. A truncation bug lived exactly there;
- **a symmetric space.** The round sphere has `∇R = ∇∇R = 0` while `R` is nowhere zero — a
  flat metric cannot make that distinction.

### Three defects that testing found in my own work

Worth recording, because none of them showed up as a red exit code.

- **The Hessian dropped its factor of 2 on the diagonal.** Written
  `if .. {1} else {0} + if .. {1} else {0}`, the exponent row binds as
  `if .. {1} else {0 + if ..}`, so `∂_w∂_w` read the wrong monomial entirely and returned
  zero.
- **I miscounted the gate's own `expect`** — 16 where there were 17 checks. It returned 16
  and I read it as green while that bug was failing. A failing check now **prints which
  one**.
- **The metric fixture sat in normal coordinates**, so `Γ(0) = 0` and every connection term
  was multiplied by zero. Three mutations that deleted or sign-flipped those terms scored a
  **clean baseline** against it. Same class of trap as the `g(base) = δ` one in the previous
  report — found only by mutation testing, both times.

## 5. What this does **not** establish

- **Not that the count is exactly 3.** It is a **lower bound** that happens to equal the
  cited value. The weight-6 shape *linear* in the curvature with four derivatives — whose
  only independent representative is `□²R` — is **not** among the candidates, because it
  needs the metric at degree 6 where the jets carry 924 terms per component. **That is
  where a fourth invariant would hide.**
  The bound is sound in that direction: adding a non-invariant candidate raises
  `rank(values)` and `rank(variations)` together and leaves the difference alone, while
  adding an invariant one raises only the first — so more candidates can only *increase*
  the count.
- **No basis is exhibited.** The count is a dimension. No candidate is identified with
  `I₁`, `I₂` or `I₃` individually; the two cubic Weyl contractions are shown invariant, but
  **the third invariant is not written down**.
- **No quotient by total derivatives**, so nothing here is a statement about **Lagrangians**,
  actions, or the trace anomaly's coefficients.
- **`E₆` is not constructed.**
- **The parity-odd sector is untouched** in every dimension — no `ε`-carrying candidate is
  evaluated, so the `D = 6` analogue of the `D = 4` parity result stays open exactly as
  `REVERSE_PHYSICS_WEYL_ACTION_D6_V1` records it.
- **Nothing about `D > 6`, other weights, dynamics, the ghost, or anything quantum.**

## 6. What it cost in substrate

The blocker this time was arithmetic, not geometry.

- **`jet_mul` and `jet_add` did not scale.** `jet_accum` finds the term to add into by
  **linear scan**, so both were quadratic in the result size — invisible at the degree-2
  jets curvature normally uses, fatal at degree 4, where one Christoffel computation took
  **27 seconds**. Both now pack the exponent row into a single `i64` key and accumulate
  through an open-addressed table. The reference implementations stay as `jet_mul_ref` and
  `jet_add_ref` and are the **oracle**: `jet_mul_gate` compares them by a dense sweep of
  every monomial, so a term either path invented *or dropped* is caught.
- **`jet_truncate`** — each stage is truncated explicitly to what the next one reads.
- **`math/curvcov`** — the covariant derivatives, carried as Taylor coefficient arrays
  rather than jets. In `D = 6` the first derivative of Riemann is a rank-5 object; as jets
  that is over a **billion** coefficient operations, nearly all of them computing Taylor
  coefficients no invariant at a point ever reads.

---

## Verification

```bash
cd tango/forge && export FORGE_LIB=$PWD/lib
forge verify examples/curvature_invariants_deriv_gate.forge      # 33/33, ~15 min
forge verify --full examples/curvature_covderiv_gate.forge       # 23/23, the derivative layer
forge verify --full examples/jet_mul_gate.forge                  # 14/14, the jet arithmetic
forge verify --full examples/curvature_invariants_d6_gate.forge  # 26/26, the cubic count
```

The derivative gate is deliberately **not** a per-commit rail: C backend only, about
fifteen minutes. The fast rails are the other curvature gates.

Exact rational arithmetic throughout — jets over ℚ for the curvature, Taylor coefficient
arrays over ℚ for the covariant derivatives, exact rational Gaussian elimination for every
rank. No floating point, no tolerance.
