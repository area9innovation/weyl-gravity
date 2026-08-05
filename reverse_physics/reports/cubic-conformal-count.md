# Cubic conformal invariants, counted — and where `D = 6` gets its second one

**Certificate** `REVERSE_PHYSICS_CUBIC_CONFORMAL_COUNT_V1`
**Rail** Forge, `tango/forge/examples/curvature_invariants_d6_gate.forge` — 27/27,
`c == native`, ASan clean on both backends, ~20 s
**Dependency tag** `LOCAL-ALGEBRAIC`

> **This does not overturn the cited `3`.** It computes a *different, smaller*
> class exactly, and locates the boundary of the citation. §5.

---

## 1. The blocker was real only for the route nobody had to take

`REVERSE_PHYSICS_WEYL_ACTION_D6_V1` names its blocker precisely:

> a basis of cubic curvature invariants **modulo total derivatives and
> dimension-dependent identities**

and calls it expensive — Bianchi reductions, dimension-dependent identities at
cubic order. All true **of the symbolic route**.

**Evaluate instead.** Take candidate contractions, evaluate them at exact
metrics, and compute the **rank over ℚ**. Every identity — Riemann symmetries,
first and second Bianchi, the dimension-dependent ones — shows up as a linear
*dependence among the evaluations*. The rank quotients by all of them **without
any of them being constructed**.

The gate makes that testable rather than rhetorical: ten candidates go in, two of
them duplicates reachable *only* through the first Bianchi identity and the pair
symmetries. Nothing in the rail knows either. The rank comes back **8**.

## 2. What came out

| | cubic curvature span | pointwise conformal invariants |
|---|---|---|
| `D = 4` | 6 | **1** |
| `D = 5` | 7 | **1** |
| `D = 6` | 8 | **2** |

Two readings, and the second is the one worth having:

- **the span grows** 6 → 7 → 8 as the dimension-dependent identities thin out.
  Nothing was told that four dimensions has identities six does not; the rank
  found them.
- **the invariant part stays at one through `D = 5` and reaches two at `D = 6`.**
  So the second cubic conformal invariant **appears exactly at six dimensions**.
  It is not a generic feature that `D = 4` happens to lose — which is what I
  expected before running it, and was wrong about.

## 3. Why the invariant subspace is the cubic-Weyl span

One line, and it makes the count mean something:

> `C^a_bcd` is conformally invariant, so `C_abcd` carries weight `+2`, and a
> complete contraction of three of them needs six inverse metrics:
> `3(+2) + 6(−2) = −6` — a **uniform** weight.

So **every** complete cubic Weyl contraction is automatically a pointwise
conformal invariant, and *"how many invariants"* is exactly *"how many
**independent** cubic Weyl contractions"* — a dimension-dependent question, which
is what the rank measures.

The rail checks both directions rather than assuming the equivalence: the two
Weyl candidates' variations vanish on **every** sample, and adding them raises the
rank of the Riemann candidates by **nothing**.

## 4. The controls are where this is won

Every one of these exists because this stream has been caught by its absence.

- **The known-answer control ran first.** The same pipeline shape on the `D = 4`
  *quadratic* question, where the answer is independent: span 3, invariant
  dimension 1, `C² = (1, −2, 1/3)` **inside**, Gauss-Bonnet `E4 = (1, −4, 1)`
  **outside**. That gate ([25/25](#verification)) also **discharges a standing
  caveat**: `weyl_action_classification_gate` carries both of those vectors under
  *"GEOMETRY ASSERTED, NOT DERIVED"*. They are now computed from generated
  metrics.
- **The fixture's own non-degeneracy is a check, not an assumption.** An earlier
  version used `g(base) = δ`, where raising and lowering **coincide** — and two
  mutation tests scored a clean baseline against it. Every up/down index error was
  invisible. The base metric is now `G = L S Lᵀ`, generic and non-diagonal.
- **Degeneracy tests are sums of *component* squares**, not contracted norms. A
  contracted norm can vanish on a nonzero tensor whenever the metric is
  indefinite.
- **Both signatures.** Euclidean and Lorentzian base metrics both appear. The
  count is algebraic and must not depend on signature; the rail would notice.
- **Rank saturation**, reported. A rank still climbing when the sampling stops is
  a bound presented as an answer.
- **Two rank rails**, `rank(M)` against `rank(Mᵀ)`.
- **The Weyl tensor is built explicitly**, so its tracelessness — which no scalar
  contraction can see — is a check.
- `R^ab R^cd R_abcd` **vanishes identically** on every fixture. Riemann's
  antisymmetry, found rather than assumed.

### The mutation battery

A gate that scores its baseline under mutation is not testing what it claims to.

| mutation | score (baseline 26) |
|---|---|
| `σ` made constant — the conformal test emptied | 21 |
| both cubic pairings made the **same** pairing | 23 |
| a Weyl index raised with `g` instead of `g⁻¹` | 21 |
| the wrong scalar coefficient in the Weyl tensor | 15 |

## 5. What this does **not** establish

Stated before the substrate notes, because the gap is the interesting part.

- **Not the cited `3`.** The literature count of three type-B invariants in
  `D = 6` is **not contradicted** — its boundary is located. Two of the three are
  complete contractions of three Weyl tensors, and this computes that there are
  **exactly two** of those. The third is **not in that class**. Which invariant it
  is, and whether it lies in the derivative sector, is **not established here**
  and stays `CITED`.
- **Nothing about invariants carrying derivatives of the curvature.** The class
  computed is *cubic in Riemann, no derivatives*. Nothing rules out further
  pointwise invariants at the same weight built from Riemann **and its
  derivatives** — and the cited third invariant is precisely the reason to expect
  one. **This is the open edge.**
- **No quotient by total derivatives.** Not needed for a pointwise count, not
  performed. So nothing here is a statement about **Lagrangians** or actions.
- **`E₆` is not constructed**, so "the Euler density is absent from the invariant
  subspace" is not checked directly.
- **The parity-odd sector is untouched** in every dimension. No `ε`-carrying
  candidate is evaluated, so the `D = 6` analogue of the `D = 4` parity result
  stays open exactly as `REVERSE_PHYSICS_WEYL_ACTION_D6_V1` records it.
- **Nothing about `D > 6`**, and nothing about dynamics, the ghost, or anything
  quantum. This is a count of algebraic invariants **at a point**.

## 6. What it cost in substrate

The blocker dissolved; a different one was real. `math/curvature` could invert only
**diagonal** metrics — and diagonal metrics in `D = 6` are far too special: they
make distinct invariants coincide and **understate** every rank computed from them.

- **`metric_inverse`** — Gauss-Jordan over the jet ring, pivoting on nonzero
  **constant term**. Taking the constant term is a ring homomorphism `Jet<T> → T`,
  so such a pivot exists whenever `g(0)` is invertible *and is a unit*, making
  `jet_inv` exact on it. The refusal becomes the honest condition **"degenerate at
  the base point"** instead of "not diagonal".
- **`metric_inverse_diag` tightened.** Its refusal tested only the off-diagonal
  *constant term* — not sufficient. A metric diagonal **at** the base point but not
  near it got an inverse wrong in its **derivatives**, which surfaced as spurious
  curvature in an exactly flat metric. The gate **exhibits** that inverse and the
  curvature it manufactures rather than asserting the bug.
- **`riemann_full`** and its trace check against both existing Ricci rails.
- **`riemann_const`** — Riemann *at* the base point from the Christoffels'
  constant and linear coefficients, no rank-4 jets. `riemann_full` in `D = 6`
  spends ~12 million coefficient products computing derivatives of the curvature
  no invariant reads. **185 s → 20 s**, and it is pinned componentwise to the slow
  path in every dimension.
- **`math/curvinv`** — the exact tensor layer: raising and lowering, Ricci, the
  Weyl tensor, tracelessness, component-square tests, and the pair-matrix cube that
  every cubic contraction reduces to.

---

## Verification

```bash
cd tango/forge && export FORGE_LIB=$PWD/lib
forge verify --full examples/curvature_invariants_d6_gate.forge    # 27/27
forge verify --full examples/curvature_invariants_d4_gate.forge    # 25/25, the control
forge verify --full examples/curvature_general_inverse_gate.forge  # 20/20
forge verify --full examples/curvature_gate.forge                  # 18/18, unchanged
```

Exact rational arithmetic throughout — jets over ℚ for the curvature, exact
rational Gaussian elimination for every rank. No floating point, no tolerance.
