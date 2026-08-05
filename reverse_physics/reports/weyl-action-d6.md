# `D = 6`: the method scales, the uniqueness does not

**Certificate** `REVERSE_PHYSICS_WEYL_ACTION_D6_V1`
**Rail** `reverse_physics/weyl_action_d6.py` — 12/12 checks
**Answers** the gate declared in [`OVERVIEW.md`](OVERVIEW.md) §8 —
`WEYL_ACTION_SIX_DERIVATIVE_D6`
**Dependency tag** `LOCAL-ALGEBRAIC`

---

## 1. The gate

> *"Six derivatives in six dimensions. The weight argument says the conformally
> invariant curvature degree is `k = D/2`, so odd dimensions have no such sector
> at all and `D = 6` selects the **cubic** one. Running the same exact linear
> algebra there tests whether the method scales and whether the parity result has
> an analogue."*

The last item this stream said it would do and hadn't. The answer is more
interesting than *"it scales"*, and it is partly a negative.

## 2. What scales — computed, dimension-general

| `D` | `k = D/2` | order | sector? |
|---|---|---|---|
| 2 | 1 | 2 | ✅ |
| 3 | 3/2 | — | ❌ |
| 4 | **2** | **4** | ✅ |
| 5 | 5/2 | — | ❌ |
| 6 | **3** | **6** | ✅ |
| 7 | 7/2 | — | ❌ |
| 8 | 4 | 8 | ✅ |

Exactly **one** degree in each even dimension, **none** in odd, derivative order
equal to the dimension — and the same line excludes the cosmological term
everywhere and Einstein–Hilbert everywhere except `D = 2`. All computed, all
dimension-general.

### `D = 2` is a degenerate hit

There `k = 1`, so the selected Lagrangian is `√−g R` — which in two dimensions is
the **Euler density**, hence topological. The invariant sector is nonempty but
**dynamically empty**.

*"The law selects a degree"* and *"there is an action"* are different statements,
and `D = 2` is where they first come apart.

## 3. What does not scale — the finding

The weight law fixes the **degree**. It says **nothing** about how many
independent invariants sit at that degree.

| | | quotient | |
|---|---|---|---|
| `D = 4`, `k = 2` | `{Riem², Ric², R²}` is 3-dim; `a + b + 3c = 0`; invariant `span{C², E₄}`; `E₄` topological | **1** | **computed here** |
| `D = 6`, `k = 3` | the three type-B invariants `I₁, I₂, I₃`, alongside the type-A Euler density `E₆` | **3** | **cited** |

> **"Exactly one degree" does not mean "exactly one action". The uniqueness this
> entire ledger rests on is special to four dimensions.**

The method scales. The conclusion does not.

## 4. What that costs the ghost argument

[`weyl-ghost-forced.md`](weyl-ghost-forced.md) argues the ghost cannot be tuned
away **because the action is unique** — *"there is no other conformal action"*, so
every proposal to modify the curvature terms is dead on arrival.

**That is a `D = 4` argument.** In `D = 6` there *are* other conformal actions — a
three-parameter family — so the **second** step fails there.

The **first** step is unaffected: the pole count from `D − 2k = 0` is
dimension-general, and the existing table already records `D = 6` as *worse* for
it (degree 3, sixth order, three poles). So the verdict *"dropping `RP-DIM4` does
not help"* stands. What changes is the **reasoning**: at `D = 6` it survives on
the pole count alone, not on uniqueness.

This is a qualification, not a correction. The argument is stated at `D = 4` and
is correct there.

## 5. What blocks the rest, named rather than glossed

The `D = 4` classification is a rank computation over a **three-dimensional**
coordinate space whose basis this stream wrote down. The cubic analogue needs

> a basis of cubic curvature invariants modulo total derivatives and
> dimension-dependent identities

which this stream does not have. The Bianchi reductions are the bulk of the work,
and dimension-dependent identities enter at cubic order in a way they do not at
quadratic. Until that exists the `D = 6` count is a **citation**, and is marked
`CITED` throughout.

**The parity half of the gate is therefore not answered either** — whether the
`D = 4` parity result has a `D = 6` analogue needs the same missing basis.

### The blocker dissolves on inspection

Written up separately as [`d6-forge-brief.md`](d6-forge-brief.md): the basis is
needed only by the **symbolic** route. Evaluate candidate contractions at enough
exact metrics and take the **rank over ℚ**, and every identity — Riemann
symmetries, both Bianchis, dimension-dependent identities — makes the
evaluations linearly dependent *automatically*. The rank quotients by all of them
without any being written down.

And the total-derivative quotient is not needed for *this* question: the three
`D = 6` invariants are **type-B**, i.e. *pointwise* conformal invariants, while
`E₆` is type-A and is not. ~~So the pointwise route returns exactly the number
wanted, with `E₆` correctly absent.~~

What remains is one genuine substrate gap — Forge's curvature layer inverts only
**diagonal** metrics, and diagonal metrics in `D = 6` are too special — plus the
controls. The brief has both.

### It has now been run, and that last prediction was wrong

**Done:** [`cubic-conformal-count.md`](cubic-conformal-count.md), certificate
`REVERSE_PHYSICS_CUBIC_CONFORMAL_COUNT_V1`, Forge rail 26/26.

The method worked and the substrate gap was closed. The **prediction struck out
above did not survive**: the pointwise route returns **2**, not 3.

The reasoning behind the strike-out conflated two senses of *pointwise*. Type-B
does mean the invariant is a pointwise conformal invariant — but "pointwise" there
does **not** mean "carries no derivatives of the curvature". What the route
actually counts is the invariants that are *cubic in Riemann with no derivatives*,
and in `D = 6` there are exactly **two** of those: the two complete contractions of
three Weyl tensors, which the rail builds and shows span the whole invariant space.
The third cited invariant is **not in that class**.

So the `D = 6` row below stays `CITED` at **3** — that count is not contradicted,
its **boundary is located**. What is now `COMPUTED` is a smaller, exactly stated
class, together with the `D = 4` and `D = 5` values that make the shape visible:

| | cubic curvature span | pointwise conformal invariants, no derivatives |
|---|---|---|
| `D = 4` | 6 | **1** |
| `D = 5` | 7 | **1** |
| `D = 6` | 8 | **2** |

The second invariant appears **exactly at six dimensions** — also not what was
expected, since `D = 5` was predicted to have two as well.

### And the derivative sector closes the remaining gap

**Done:** [`derivative-conformal-count.md`](derivative-conformal-count.md),
certificate `REVERSE_PHYSICS_DERIVATIVE_CONFORMAL_COUNT_V1`, Forge rail 33/33.

Adding the two derivative shapes at weight 6 — `∇R ∇R` and `R ∇∇R` — the count
in `D = 6` reaches **3**:

| | cubic span | cubic invariants | with derivatives |
|---|---|---|---|
| `D = 4` | 6 | 1 | **2** |
| `D = 5` | 7 | 1 | **2** |
| `D = 6` | 8 | 2 | **3** |

So the cited `3` below is now **matched by an independent computation** rather
than merely referenced. Two caveats keep it honest, and both are in the
certificate:

- it is a **lower bound**. The shape *linear* in the curvature with four
  derivatives (`□²R`) is not among the candidates, and adding candidates can only
  raise the count — so a fourth invariant, if there is one, hides there;
- **no basis is exhibited.** The count is a dimension; the third invariant is not
  written down.

The unexpected part is the **uniform `+1`**: the derivative sector supplies exactly
one more invariant in *every* dimension examined, and the `D = 4` and `D = 5`
counts — 2 and 2 — were not predicted at all.

### The parity half is answered too — and the answer is yes

**Done:** [`parity-conformal-count.md`](parity-conformal-count.md), certificate
`REVERSE_PHYSICS_PARITY_CONFORMAL_COUNT_V1`, Forge rail 20/20.

§5 above says the parity half *"is therefore not answered either — whether the
`D = 4` parity result has a `D = 6` analogue needs the same missing basis."* It
needed no basis; it needed an `ε`, which nothing in this stream had ever evaluated.

| | | parity-odd invariants |
|---|---|---|
| `D = 4`, weight 4 | the Pontryagin density | **1** |
| `D = 4`, weight 6 | | **2** |
| `D = 6`, weight 6 | | **2** |
| odd `D` | none exist, by index counting | **0** |

**There is a `D = 6` analogue.** Both invariants are *exhibited*: the complete
contractions of one `ε` with three **Weyl** tensors. The Riemann-built parity-odd
candidates are mostly identically zero, and the ones that are not are not invariant
on their own — so the parity-odd content is exactly what the Weyl tensor supplies.

The `D = 4` weight-4 row is the known-answer control: it computes what the
classification gate **asserts** when it calls `W±² = (C² ± P)/2` both Weyl invariant.

**What is still not done**, and it is the sharper half of the original `D = 4`
result: whether adjoining the parity-odd sector leaves the *field equations*
unchanged in `D = 6`, as it does in `D = 4`. That is a different computation.

### The sharper half is done too — and the answer is **no**

**Done:** [`parity-field-equations.md`](parity-field-equations.md), certificate
`REVERSE_PHYSICS_PARITY_FIELD_EQUATIONS_V1`, Forge rail 6/6.

The paragraph above is right that it is a different computation — counting
invariants is not a variational question — so it needed an **Euler operator**,
built over the same jet ring. Applied to the `D = 6` parity-odd invariant:

| metric | component | value |
|---|---|---|
| 1 | `E⁰⁰` | `−12614421113/320` |
| 1 | `E¹²` | `1224309325271/160` |
| 2 | `E⁰⁰` | `1290109675603/640` |

**Nonzero.** The invariant is **not locally a total divergence**, so it does
contribute to the field equations. In `D = 4` the parity-odd direction is a
gravitational theta-angle — it changes the action and not the equations of motion.
**In `D = 6` it does not.**

Which makes this the **second** finding in this report of the same shape. §6 says
of uniqueness that *"the method scales, the conclusion does not"*; parity
redundancy is the other one. And it reaches further than uniqueness did: the
ledger's *"six assumptions written as an action, five written as field equations"*
turns on `RP-PARITY` dropping out on the field-equation side, so **that count is
dimension-dependent**.

**Local, not global.** A nonzero Euler–Lagrange expression means *not locally* a
total divergence; "not topological" is a different statement and is not shown.
Only **one** of the two `D = 6` parity-odd invariants is differentiated.

---

```bash
PYTHONPATH=. python3 -m reverse_physics.weyl_action_d6 --check
```
