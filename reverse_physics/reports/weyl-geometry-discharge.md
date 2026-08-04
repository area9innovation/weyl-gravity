# Four imported facts, discharged — and the search that should have come first

**Certificate** `REVERSE_PHYSICS_WEYL_GEOMETRY_DISCHARGE_V1` — 21 exact checks
**Engine** `black_hole_programme/weyl_geometry.py`, pinned by hash
**Verifier** `PYTHONPATH=. python3 -m reverse_physics.weyl_geometry_discharge --check`

---

## The mistake this starts with

[`PHYSICS-VS-MATH.md`](PHYSICS-VS-MATH.md) states its own sharpest weakness:

> **Geometry is imported wholesale.** `G1`–`G8` are standard, but they are **the
> bulk of the intellectual content** and none of them is machine-checked here.

and ranks the sharpest objection to the whole programme first:

> **Reject `G5`.** … What remains open is that the witness metric — matter-dominated
> FRW, `a(t) = t^{2/3}`, `R = 4/3t²` — is **named, not formalised**. Formalising it
> needs a Riemann tensor, **which this development does not have**.

That last clause was true of the reverse-physics stream and **false of the
repository.** `black_hole_programme/weyl_geometry.py` is an exact
Christoffel → Riemann → Ricci → Weyl → **Bach** engine with frozen `BH-0`
conventions, already consumed by a dozen black-hole modules. The Riemann tensor
was here the whole time; the ledger had simply never been wired to it.

The overview records this exact lesson from an earlier stream — *"search the
corpus before deriving; the import gates only help once wired, which should come
before the derivation, not after"* — and this is the second time it applies.

## What is now discharged

| | fact | why it matters |
|---|---|---|
| `G5` | matter-dominated FRW gives `R = 4/(3t²)` and `□R = −8/(3t⁴) ≠ 0` | **the sharpest self-identified attack.** Without some metric having `□R ≠ 0` the classification is vacuous — already a theorem — and the input was *named*, now *computed* |
| `G1` | `C² = Riem² − 2Ric² + R²/3`, equivalently `C² = E₄ + 2Ric² − (2/3)R²` | the coordinate vectors of the entire classification |
| `G2` | `R[e^{2σ}g] = e^{−2σ}(R − 6□σ − 6(∇σ)²)` | what makes the `R²` component carry the anomaly |
| `G3` | `C_abcd[e^{2σ}g] = e^{2σ}C_abcd` | **the derived derivative order `k = D/2` rests on this** — the stream's best result about Weyl gravity itself |

`R = 4/(3t²)` is exactly the value the report named. It is now output rather than
input.

## The control that found something

The wrong-coefficient control initially **failed**, and it was right to.

**Schwarzschild is Ricci-flat**, so `R = 0` *and* `Ric² = 0`. On it, `G1` collapses
to `C² = Riem²` and holds for *any* coefficients whatsoever — the `R²/3` and the
`−2Ric²` are simply invisible. A control aggregated over all test metrics would
have reported a failure that was really a statement about coverage, and a control
that merely averaged would have hidden it.

So the certificate now records, per metric, **which term that metric can see**:

| metric | `R ≠ 0` | `Ric² ≠ 0` |
|---|---|---|
| Schwarzschild | no | no |
| Schwarzschild–de Sitter | yes | yes |
| non-Einstein static | yes | yes |

and applies each wrong-coefficient control only where it can discriminate, while
separately asserting that *some* metric can. Without that pair of clauses the
whole check would pass on vacuum solutions alone — which is what most of this
repository computes with.

The same point makes `G5`'s witness a real choice rather than a formality:
Schwarzschild has `R ≡ 0`, hence `□R ≡ 0`, so **it cannot witness `G5`**. That is
asserted as its own control.

## The field-equation layer, which the ledger said was never computed

It was — by the repository, not by this stream. Wiring to the same engine
discharges:

| check | why |
|---|---|
| `∇^a B_ab = 0` | **this is `N1`'s content** — the metric variation of a local diff-invariant action is divergence-free, computed for the actual tensor rather than imported |
| `g^ab B_ab = 0` | trace-freeness, which is what makes the field equations conformally invariant |
| `B_ab[e^{2σ}g] = e^{−2σ}B_ab` | that invariance, directly |
| `B_ab = 0` on Schwarzschild | **why Schwarzschild solves Weyl gravity at all** — the fact the entire black-hole programme rests on, checked rather than assumed |
| `B_ab ≠ 0` on a non-Einstein metric | so none of the above is vacuous |

**The variational link itself is cited, not re-derived.**
`δ∫√−g C² = 4∫√−g B_mn δg^mn` is checked elsewhere in this repository, on the
Nariai product family `g(x,y) = x·g_{dS₂} + y·g_{S²}`, where the standard
variation `diag(2/3, −2/3, 2/3, 2/3)` along `∂ₓ−∂_y` is reproduced exactly with
`B_action = −2B_standard`. `bh1b_dynamical.py` records the Lee–Wald form
`δ(√−g αC²) = div(√−g θ)` on shell. `verify_conformal_dynamical_topological.py`
states the same variation as a **declared field-theory identity and does not
re-derive it** — which is the honest status, now recorded in one place instead of
three.

What is computed here is everything about that link visible *pointwise*.

## What remains imported

Honest, because the point of the middle column is that it is visible:

- `G4`, `G7` — `∫√−g E₄` and `∫√−g P` are topological. **Global** statements; a
  pointwise curvature engine cannot reach them.
  **Now cited** ([report](weyl-dual-discharge.md)) to this repository's existing
  transgression work, each with its source's own boundary: `G4` to
  `EULER_TRANSGRESSION_CERTIFICATE` for the *variational* content only (not an
  index theorem), and `G7` to the Chern–Weil transgression in
  `symbolic/verify_conformal_dynamical_topological.py`, whose docstring states
  that global triviality of the Pontryagin class is explicitly not claimed.
- `G6`, `G8` — `P = C·C̃` spans the parity-odd invariants, and `W±² = (C² ± P)/2`.
  ~~The engine has no dual yet; adding one makes both reachable.~~
  **Done** ([report](weyl-dual-discharge.md), certificate
  `REVERSE_PHYSICS_WEYL_DUAL_DISCHARGE_V1`). `G8` splits into **two different
  statements**: Euclidean `W±² = (C² ± P)/2` with real projectors, and
  Lorentzian `W±² = (C² ∓ iP)/2` with the complex projectors `hodge.py`
  specifies — the textbook form being *checked false* in Lorentzian signature.
  `G6`'s computable clause (`Riem·⋆Riem = C·⋆C`) is discharged; its spanning
  clause is a dimension count and is cited. Note the trap: the `G6` check is
  **vacuous on a Ricci-flat metric**, where `Riem = C` identically, so it is
  carried by non-Einstein metrics and the certificate records
  `ricci_is_nonzero` per row.
- `N2`, `N3` — the remaining Noether facts. `N2` (the trace of the variation is a
  nonzero multiple of the anomaly) is a quantum statement; `N3` (a topological term
  has identically vanishing variation) needs the variation of `E₄`, not curvature at
  a point. `N1` is discharged above.
  **`N3` is now cited**: it is the *same content* as `G4`'s
  `delta_E4_minus_dTheta`, so the same certificate carries it.
  ~~**`N2` is the one entry still genuinely open**~~ **`N2` is now discharged**
  ([report](weyl-trace-law.md)) as a trace law, `g^mn E_mn = 2(a + b + 3c)□R`.
  The bridge between the two ledgers is therefore built: the multiple is `2`,
  hence nonzero, and `□R ≠ 0` is `G5` above — **`N2` and `G5` need the same
  witness.** The geometry column is closed.

## What this is, and is not

Each fact is verified **exactly** — sympy rationals and symbols, no floating point
— at specific metrics chosen to be non-vacuous. That is **strictly stronger than
an unverified import and strictly weaker than a theorem for all metrics.**

It is a discharge, not a proof, and the certificate says so in those words. What
would make it a proof is a formalised Riemann tensor with the algebraic
symmetries, which is a different and much larger build.

## Verification

```bash
PYTHONPATH=. python3 -m reverse_physics.weyl_geometry_discharge --check
# REVERSE_PHYSICS_WEYL_GEOMETRY_DISCHARGE_V1: PASS — 21 exact checks, engine pinned
```

Needs sympy; on this workstation that is the mise interpreter,
`~/.local/share/mise/installs/python/3.12.13/bin/python3`. Runs in ~13 s.
