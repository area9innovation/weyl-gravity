# The linear potential is forced, not chosen

**Certificate** `BH0B_GENERAL_STATIC_SPHERICAL_COMPLETENESS`
**Verifier** `black_hole_programme/bh0_general_completeness.py` — 24 checks, all PASS, 4.03 s
**Dependency tag** `LOCAL-ALGEBRAIC`

> Closes the gap `BH0` declared: *"completeness beyond the Laurent class (Riegert's
> classification is a literature target, not a repository theorem)."* §4 is what this does
> **not** say, and for this particular result that section is the important one.

---

## 1. What was missing

`BH0` proved that within a **six-term Laurent ansatz** `B = w − u/r + γr − kr² + c₂/r² +
c₃r³`, the Bach equations force `c₂ = c₃ = 0` and `w² + 3uγ = 1`. That is a statement about a
family someone wrote down. It leaves open whether some *other* function — a logarithm, an
exponential, anything not in the list — also solves them.

For anything downstream that matters, the difference is everything. "The linear term appears
in a family we chose" is not a physical claim. "The linear term is one of the four
coefficients of the general solution" is.

## 2. The structure that makes it closable

With `B` an unspecified function, the three independent Bach rows are **not three independent
equations**. Define

```
L := (r B)''''                                              ← LINEAR in B
N := 2r⁴(B B'''' + B'B''') − r⁴B''² + 4r³(B B''' + B'B'')
     − 4r²(B B'' + B'²) + 8r B B' − 4B² + 4                 ← nonlinear
```

Then, as exact identities in `B` and its derivatives,

```
B_θθ = N / (24 r²)
B_tt = B (N + 2r³B L) / (24 r⁴)
B_rr = (−N + 2r³B L) / (24 r⁴ B)
```

All three rows lie in the span of `{N, r³BL}` — and **both generators are recovered from the
rows**, so the implication runs both ways:

```
Bach = 0   ⟺   L = 0  and  N = 0          (on a domain where B ≠ 0)
```

**The linearity is the whole point.** A nonlinear fourth-order ODE would need an ansatz to
solve, and completeness would stay out of reach — which is exactly why `BH0` stopped where it
did. But the system is *not* nonlinear in the direction that matters: the part fixing the
**functional form** is linear, and the nonlinearity is confined to a condition that becomes
purely **algebraic** once the form is fixed.

## 3. The theorem

Substituting `u = rB`, the linear equation `L = 0` is `u'''' = 0`. Its solution space is
exactly the cubics — by four integrations, with no ansatz and no Laurent assumption. Hence

```
B = c₀/r + c₁ + c₂r + c₃r²          is FORCED
```

and on that family `N` collapses to the constant `4(1 + 3c₀c₂ − c₁²)`, so all that remains is

```
c₁² − 3c₀c₂ = 1
```

which is `BH0`'s `w² + 3uγ = 1` under `c₁ = w, c₀ = −u, c₂ = γ, c₃ = −k`. The Laurent result
is recovered as a corollary, and the ansatz is gone.

## 4. Why it matters — and the sentence that must travel with it

`γ = c₂` is the coefficient of the **linear potential**, the term conformal gravity is used to
fit galactic rotation curves with. `BH0`'s Einstein/extra split gives `E_θθ = −γ(r − 3β)/2`,
so the family is Einstein **exactly when `γ = 0`**.

Put together: **the linear potential is not a term appended to a solution to fit data.** It is
one of the four coefficients of the general solution of a *linear* fourth-order equation, and
it is precisely the non-Einstein content. Conformal invariance + vacuum + staticity +
spherical symmetry force the term to be *available*.

**They do not make it sourced.** The theorem says `γ` is a free coefficient of the *vacuum*
solution. Whether a galaxy's baryonic mass **determines** `γ` is a question about **matter
coupling**, which conformal invariance makes delicate because it forbids a mass scale — and
`BH0` explicitly does not certify *any physical matter or clock conformal frame*. Until that is
settled, fitting `γ` per galaxy is **fitting, not prediction**. That is the crux for any
phenomenological claim and this result does not touch it.

## 5. How the checks are built

- **Arbitrary function, not a fixture.** `B` is a symbolic function throughout; the row
  identities are verified as identities in `B` and its derivatives.
- **Controls that must fail.** Four non-solution probes — `log r`, `eʳ`, `1/r²`, `r³` — are
  each required to have `L ≠ 0`. Without them, "B must be a cubic over r" would be untested.
- **The constraint is checked from both sides.** It must *cut something out* (`c₀=c₁=c₂=0`
  gives `N = 4 ≠ 0`, so not every cubic is a solution) and it must *admit solutions*
  (`c₀=1, c₁=2, c₂=1` gives `N = 0`). A constraint excluding everything, or nothing, would be
  equally useless.
- **Linearity is checked, not asserted**, and the Wronskian of `{1/r, 1, r, r²}` is computed
  and found nonzero (`12/r⁴`).

## 6. What this does **not** establish

- **The general two-function ansatz.** This is proved in the conformal gauge `b = 1/B`. That
  an arbitrary `diag(−a, b, r², …)` can be brought there by a conformal transformation and a
  radial reparametrisation is the standard Mannheim–Kazanas argument and is **assumed**, not
  proved. `BH0` computes the general two-function rows separately; joining them is a further
  step.
- **Anything where `B` vanishes.** The decomposition divides by `B`, so the equivalence holds
  where `B ≠ 0` — outside horizons.
- **Novelty.** That the general static spherically symmetric vacuum solution of conformal
  gravity has this form is Mannheim–Kazanas 1989 and Riegert 1984. What is contributed is that
  it is **computed here rather than cited**, with the ansatz removed — the same currency as the
  rest of the programme.
- **Nothing about rotation curves, MOND, dark matter, or Tully–Fisher.** No phenomenology.
- **Nothing about the ghost, stability, quasinormal modes, or the quantum theory.**

## 6b. Independence — a gap this report originally had

`verify_bh0_background.py` states the standard: a verifier must be *"structurally independent"*
of its producer, recomputing curvature *"with separately written code"* so that *"a common-mode
'always zero' failure of the tensor pipeline is detected here independently."*

**This certificate did not meet it when first written.** The proof above computes Bach with
`weyl_geometry.Geometry.bach()` — the same engine `BH0` uses. A common-mode bug there would
have made the completeness theorem a theorem about the wrong tensor.

**The rail**: `tango/forge/examples/bh0_bach_independent_gate.forge`, 6/6, 361.96 s. Different
language (Forge), arithmetic (GMP rationals in jets), representation (Taylor jets about a base
point), and code path (`lib/math/curvature`+`curvinv`+`curvcov`). With `β, γ, k` symbolic the
MK family is Bach-flat as a polynomial identity; perturbing `w` off the constraint breaks it;
and a `δ/r²` term breaks it — `BH0`'s `c₂ = 0`, reproduced from a stack sharing nothing with it.
The two controls are *independent* deformations, so neither stands in for the other.

**What the rail does not confirm.** It checks the *conclusion* — which metrics are Bach-flat —
not the **row decomposition** itself. Those identities are statements about an *unspecified*
function, and Forge's jets are truncated Taylor data. So the part that actually removes the
ansatz still rests on one implementation. Closing that needs symbolic differentiation over
Forge's expression IR, which does not exist yet.

## 7. What is next

The **matter-coupling question**, which decides whether any of this is physics: state
precisely what must be assumed about how baryonic matter enters a conformally invariant action
for `γ` to be *determined by mass* rather than fitted. Flanagan's 2006 objection lives exactly
there. Formalising the assumption is a result even if the answer is unwelcome — and it is a
reverse-physics question in the strict sense, which the rotation-curve literature does not ask.

Separately and cheaply: **the asymptotic scaling**. Conformal gravity gives `v² ≈ γc²r/2`,
which *rises*; MOND gives asymptotically flat curves and *predicts* the baryonic Tully–Fisher
relation `v⁴ ∝ M`. Computing that tension honestly is the sharpest early falsifier.

---

## Verification

```bash
cd black_hole_programme
python3 bh0_general_completeness.py    # 24 checks, all PASS, 4.03 s
```

Exact symbolic arithmetic (sympy). Needs the mise interpreter.
