# Tully–Fisher forces γ to be universal — and names it `a₀/(2c²)`

**Certificate** `BH0C_TULLY_FISHER_SCALING`
**Verifier** `black_hole_programme/bh0c_tully_fisher_scaling.py` — 14 checks, all PASS
**Dependency tag** `LOCAL-ALGEBRAIC`
**Builds on** `BH0B_GENERAL_STATIC_SPHERICAL_COMPLETENESS`

> This was run as a **falsifier** — the cheap test that could have killed the line early. It
> didn't. It turned the question into a prediction instead. §5 is what it does not say.

---

## 1. The computation

`BH0B` forced `B = c₀/r + c₁ + c₂r + c₃r²`. In Mannheim–Kazanas normalisation that is
`B = 1 − 2β/r + γr − kr²` with `β = GM/c²`. The locally measured circular velocity is
`v²/c² = rB′/(2B)` exactly; expanding at small field strength gives

```
v²/c²  =  β/r  +  γr/2  −  kr²
```

In the galactic regime (`k` negligible) this has a **stationary point**, and it is a
**minimum**:

```
r*      = √(2β/γ)
v²/c²   = √(2βγ)        at r*
v⁴      = 2 G M γ c²
```

That last line is the whole result.

## 2. What follows, and it runs the way reverse physics wants

| if | then |
|---|---|
| `γ` is a **universal constant** | `v⁴ ∝ M` exactly — the baryonic Tully–Fisher relation, slope 4 in `v` |
| `γ` carries a piece `∝ M` | `v⁴ ∝ M²` — slope 8, **wrong** |
| observed `v⁴ = G M a₀` | `γ = a₀/(2c²)` |

Read in the direction this programme cares about: **the observed Tully–Fisher relation,
combined with the forced form of the metric, forces `γ` to be a universal constant of nature
rather than a per-galaxy parameter — and identifies it with MOND's acceleration scale.**

That is a *prediction*, not a fit, and it is falsifiable in a specific way: if fitting galaxies
requires `γ` to carry a mass-dependent piece, the predicted slope moves off the observed one.
Both slopes are computed here, so the discriminating power is exhibited rather than claimed.

**Nothing is fitted.** No galaxy data enters. The only observational input is the *shape* of
Tully–Fisher, used as a premise in a conditional.

## 3. Where conformal gravity and MOND genuinely disagree

Beyond `r*` the conformal-gravity curve **rises** — verified, `dv²/dr` at `2r*` is `3γ/8 > 0` —
where MOND's are asymptotically **flat**. The two theories agree on the Tully–Fisher *scaling
at the flattest point* and disagree on the *shape away from it*. The only term available to
bend the rise back down is `−kr²`, and that is checked to be the only one.

So this is not "conformal gravity reproduces MOND". It is: they coincide on one scaling law and
part company on the profile, which makes the outer rotation curve a discriminant rather than a
detail.

## 4. A check that failed first, and why it should have

The first draft compared the exact orbit condition to the weak-field one at `β → 0`, leaving
`γ` and `k` finite. That is not a weak field at all — `rγ/(2(1 + γr))` is not `rγ/2` — and the
check failed, correctly. The weak field is **small deviation of `B` from 1**, which is what
scaling *all three* parameters by `ε` encodes. Worth recording because "take the small-mass
limit" is the intuitive move and it is the wrong one here.

## 5. What this does **not** establish

- **That `v_min` is the observed flat velocity.** The algebra gives the value at the *minimum*.
  Identifying that with what an observer fits as "flat" is an **interpretive step**, not a
  theorem, and everything downstream inherits it. It is the natural reading — the curve is
  flattest there — but it is a modelling choice and is flagged as one.
- **Any numerical value.** `a₀` is not measured here, no fitted `γ` from the literature is
  checked, and no magnitudes are compared. `γ = a₀/(2c²)` is an algebraic consequence of a
  premise, not a numerical agreement.
- **That `γ` is sourced by baryonic mass.** Same gap `BH0B` leaves, untouched. `γ` is still a
  free coefficient of the **vacuum** solution. The conditional says what `γ` must *be* if
  Tully–Fisher holds; it does not say what *determines* it. **This remains the crux.**
- **Any fit to any galaxy**, or comparison with dark-matter models.
- **That conformal gravity reproduces MOND** — see §3. It doesn't.

## 6. What is next, and it is now the only thing in the way

The **matter coupling**. `γ` is forced to *exist* as a coefficient (`BH0B`) and forced to be
*universal* if Tully–Fisher holds (here). Nothing yet says what fixes its value or ties it to
the matter distribution.

Conformal invariance forbids a mass scale, so the question is sharp: **what must be assumed
about how baryonic matter enters a conformally invariant action for the Newtonian coefficient
`β` to be `GM/c²` at all?** Flanagan's 2006 objection — that the Newtonian limit does not come
out right when matter is coupled conformally — now sits directly on the load path, and should
be formalised rather than cited.

---

## Verification

```bash
cd black_hole_programme
python3 bh0c_tully_fisher_scaling.py    # 14 checks, all PASS
```

Exact symbolic arithmetic (sympy). Needs the mise interpreter.
