# Toward `T₋`: the transport engine and the horizon start, landed

**Gates** tango: `weyl_rw_factor_transport_gate.forge` 20/20,
`weyl_horizon_frobenius_gate.forge` 34/34, `weyl_jost_matching_gate.forge` 26/26,
and the new library `math/ivtrans` with `ivtrans_gate.forge` 34/34.
Both `verify -full`: **`c==native`, ASan-clean on both backends**
**Engine** `math/ivlinode` (rigorous linear IVPs) + `math/interval`

---

## Where this sits

The ghost question is one object from settled. Both Grams are explicit, the
criterion is `CLASSIFIED`, and
[`c-factorisation-not-determined.md`](c-factorisation-not-determined.md) proved
the certified data cannot decide it — so `T₋` is logically required.

This lands the first piece of computing `T₋`, and unlike the parametric gate it
meets the bar: **ASan-clean, both backends.**

## What is certified

The factor equations, verbatim from `axial_incoming_connection_analytic`:

```
spin two:  D_r*² u + 2iω D_r* u − V₂ u = 0,   V₂ = 6(r−2)(r−1)/r⁴
spin one:  D_r*² y + 2iω D_r* y − V₁ y = 0,   V₁ = 6(r−2)/r³
```

With `D_r* = f·d/dr`, `f = (r−2)/r`, expanding and dividing by `f²` gives

```
A = [[0, 1], [V/f², −P]],    P = f′/f + 2iω/f = (2 + 2iωr²)/(r² − 2r)
V₁/f² = 6/(r² − 2r)          V₂/f² = 6(r−1)/(r²(r−2))
```

`P` is the **same for both spins** — it never sees the potential — so one
Wronskian rail serves both.

Certified: validated fundamental matrices for both factors on `r ∈ [3,4]`, with
existence and uniqueness; two step counts whose enclosures **meet**, with
refinement provably **tightening**; and the whole certified cell `ω ∈ [1/2, 3/4]`
carried as **one interval extension**, so the enclosure covers every frequency in
the pilot cell rather than a sample — and is checked to contain the pointwise flow
at `ω = ½`.

## The conservation rail

For `u″ + Pu′ + Qu = 0` the Wronskian obeys `W′ = −PW` **exactly**. Transporting
`q′ = Pq` on the same interval and pairing the flows through the lifted
symplectic current gives a defect that must enclose zero. It does, for both
spins — an independent check on the transport that no solver bug respecting no
conservation law could pass.

**And the rail is discriminating — which took a correction worth recording.** A
*large* perturbation over the whole interval is **not** rejected: it only inflates
the enclosure until it swallows zero, so it proves nothing. The sharp control is a
*small* mutation on one **retained local factor**, where the enclosure is still
tight. A `1/100` shift is rigorously rejected, and the unmutated local factor is
separately asserted to pass, so the control is not always-fail.

Two more non-vacuity guards: the two spins are asserted to give **different**
flows (catching a transcription collapse where both potentials were typed the
same, which every other check would have survived), and an unsound-extension
claim is asserted to be **refused**.

## The horizon start — landed

`r = 2` is a **regular** singular point, so the transport cannot start there.
With `x = r − 2` and denominators cleared, both factor equations have indicial
polynomial `s(s + 4iω)` — roots `{0, −4iω}`, exactly as certified. The ingoing
branch is `s = 0`, normalised `a₀ = 1`, and since `−4iω` is not a nonnegative
integer for real `ω ≠ 0` there is **no log term**.

The recurrences are exact with never-vanishing `a_{n+1}` coefficients:

```
spin 1:  2(n+1)(n+1+4iω) a_{n+1} = −[(n²+8iωn−n−6)a_n + (2iωn−2iω)a_{n−1}]
spin 2:  4(n+1)(n+1+4iω) a_{n+1} = −[(4n²+24iωn−2n−6)a_n
             + (n²+12iωn−3n−12iω−4)a_{n−1} + (2iωn−4iω)a_{n−2}]
```

**The design point.** The true radius is 2 (nearest other singularity at `r = 0`),
so coefficients decay like `2⁻ⁿ` — but a naive absolute-value majorant *cannot see
that*: spin-two's characteristic polynomial is `4w²+4w+1 = (2w+1)²`, a **double
root** at `w = −½`, and taking moduli destroys the cancellation, giving `K ≈ 1.53`
instead of `0.5`. Rather than fight for a sharp majorant, the series is evaluated
at `x₀ = 1/8` where even the crude `K` gives `Kx₀ < 0.2`, and the validated flow
covers the rest. **Series on a small disk + validated transport for the remainder
is the architecture**, and it's why the crude bound suffices.

Result at `ω = ½`:

```
spin one  u(17/8) ∈ [1.064009617191854,  1.0640096171918558]
spin two  u(17/8) ∈ [1.0343900269412738, 1.0343900269412751]
tails      1.3e−69  and  8.1e−54
```

The tails are utterly negligible against the ~`2e−15` enclosure width — which is
therefore set by the interval arithmetic, not the truncation. Then transported to
`r = 3` with 4096 steps, certified.

Controls, because a majorant test that accepts anything proves nothing: the
spin-two majorant must **reject** `K = 0.9` and spin-one must **reject** `K = 0.60`,
so the accepted values are binding; a 40-term truncation must **meet** the
60-term one with its larger tail allowed for, and that tail is asserted strictly
wider.

## The review pass — and what it caught

Before moving to the Jost match I audited both gates. Five gaps, one of them an
honesty defect, and fixing that one immediately found an error.

**The header claimed a test that did not exist.** The Frobenius gate advertised
an "independent ODE-residual test on the series itself". There wasn't one. It now
exists — and **on its first run it failed**: my hand-typed residual had dropped
the `2x` from spin two's `B = 2iωx³ + 12iωx² + 24iωx + 16iω + 2x + 4`, writing
the real part as `4` rather than `2x + 4`. The *recurrence* was correct — it came
from the symbolic extraction — so the error was in the test. That is still
exactly why the test needed writing.

**The majorant ran in raw `f64`.** A rigorous bound cannot rest on unrounded
arithmetic however wide the margin. It is now interval-rounded, with the verdict
taken from the low end of the slack.

**The horizon-side transport had no conservation rail** — the leg with the
largest coefficients, hence the one most in need of a check, was the one without.

**Nothing compared the series against the solver.** Now: evaluate at `x = 1/16`,
transport to `x = 1/8`, and require it to meet the direct evaluation. Two
entirely different pieces of machinery have to agree.

**The majorant's conclusion was never checked against reality.** `|aₙ| ≤ CKⁿ` is
now asserted for every computed `n ≥ n₀`.

And in the transport gate: the companion entries are checked against the
*certified* potentials `V₁ = 6(r−2)/r³`, `V₂ = 6(r−2)(r−1)/r⁴`, written
independently of the reduced `V/f²` forms the solver uses.

The numbers did not change — which is the point. The enclosures were right; the
*argument* for them wasn't fully rigorous, and one advertised check was absent.

## Infinity — the matching layer, and a Forge gap closed to reach it

**The setup is better than expected.** Substituting `u = e^{−iωr*}ψ` turns the
Regge–Wheeler form into the certificate's factor form, so `A_in` is simply the
**constant part** of `u` at infinity. And setting `A_out′ = A_out·e^{−2iωR*}`
absorbs the unknown phase — same modulus — so the tortoise coordinate drops out
of the match entirely. The moduli are exactly what
`det(L_H) = 1/(|A_in₂|⁴|A_in₁|²)` needs.

The corrections are *exactly* computable: the Jost Volterra kernel is bounded by
`1/ω`, and both tails close in elementary form because `dr* = r dr/(r−2)` cancels
the `(r−2)` in each potential:

```
∫_R^∞ V₁ dr* = ∫_R^∞ 6/r² dr           = 6/R
∫_R^∞ V₂ dr* = ∫_R^∞ (6/r² − 6/r³) dr  = 6/R − 3/R²
```

with `e^t ≤ 1/(1−t)` giving a rigorous exponential bound and no transcendental at
all. Both closed forms are checked against `math/ivode`'s validated quadrature.

**But the transport didn't survive the trip — and that turned out to be a Forge
gap, not a physics one.** Measured:

| R | naive width | interaction picture |
|---|---|---|
| 30 | 7.3×10¹² | **1.32** |
| 100 | 1.5×10⁴⁴ | **1.96** |
| 400 | 4.0×10¹⁷⁴ | **2.21** |
| 1500 | **refused** | **2.28** |
| 6000 | — | **2.30** |

The naive flow suffers Gronwall wrapping: `‖A‖ ~ 2ω/f ~ 1`, so the bound is `e^L`
and grows without limit with range. In the **interaction picture**
`u = a + b e^{−2iωr*}` the coefficient is `(V/f)/(2ω) = 3/(ωr²)`, so the Gronwall
integral *converges* — `∫₃^∞ = 2`, bound `e² ≈ 7.4`, uniformly in `R`. Same
equation, same solver, same arithmetic; different coordinates.

That route needs `e^{±2iωr*}`, hence validated `log`, `sin`, `cos` — which
`math/interval` did not have. **So the gap got closed rather than routed around:**
`math/ivtrans` now supplies `iv_exp`, `iv_log`, `iv_sin`, `iv_cos`, with `π` and
`ln 2` *derived* in exact rationals (Machin; alternating partial sums bracket the
limit) rather than typed in. Its gate validates almost entirely by identities —
`sin²+cos²=1`, double-angle, `exp∘log = id` both ways, `exp(a+b)=exp a·exp b` —
and feeds the module's own `π` back through its own sine. 34/34, ASan-clean.

## The extension coefficient — and it is a single constant

The last object, and it turned out far more tractable than expected once the
certified gauge data was read properly. `axial_rw_lx_triangular_preflight`
gauges the four-state carrier module into `transformed_A4`, which is **block
triangular**:

```
[ 0                    1                      0     0   ]
[ 6(r-1)/(r²(r-2))   -2i(ωr² - i)/(r(r-2))    1     0   ]  ← the coupling
[ 0                    0                      0     1   ]
[ 0                    0                   L_x entries  ]
```

So with `y = (y_RW, y_x)`: `y_x′ = A_x y_x` and `y_RW′ = A_RW y_RW + C y_x`, with
`C` carrying a **single entry equal to 1**. The spin-one factor decouples
entirely and drives the spin-two one as a source. The extension coefficient is
therefore `X = ∫ Φ_RW(r,s) C Φ_x(s,r₀) ds`, and by triangularity it is simply the
**upper-right block of the transported fundamental matrix**.

**The cross-check that licenses this — and a correction to it.** The first
version of that check was partly vacuous: `ours_q` and `theirs_10` were defined
by the *same typed expression*, so it compared a function to itself. Each side is
now built from the quantities its own derivation starts from — ours from
`f = (r−2)/r`, `f′ = 2/r²`, `V₂ = 6(r−2)(r−1)/r⁴` as `V₂/f²` and
`−(f′/f + 2iω/f)`; theirs as the certificate writes it, with
`(−2i)(ωr²−i)/(r(r−2))` evaluated as a *complex product* rather than
pre-simplified. So the check now verifies the algebraic reduction rather than
restating it. The computed value moved only in its last digit — which is what
agreement between two genuinely different arithmetic paths looks like.

The RW diagonal sub-block of the carrier flow is also now checked against a
standalone spin-two flow built from our primitives. The `L_x` sub-block had been
checked that way; the RW one — the block the *certified gauge data* supplies —
had not, which was the wrong way round.

**Result:**

```
X(2.4 → 3.0), entry (1,0) ∈ [0.07592875168485574, 0.07718132970732572]
```

**Nonzero** over this range: the coupling genuinely contributes. That is
*consistent with* and exhibits the corpus's abstract
`axial_ell2_nonsplit_all_positive_real`, but does not re-prove it — nonsplitness
is a statement about the module, not about one sub-range, and an earlier draft of
this report overstated it.

## End to end — the chain runs, and the Wronskian validates it

`weyl_ain_endtoend_gate.forge` (21/21, ASan-clean) runs horizon Frobenius →
interaction-picture transport → `A_in`, in one chain.

**No matching matrix is needed.** With `u = a + b e^{−2iωr*}` and the
variation-of-parameters constraint, `ψ = a e^{+iωr*} + b e^{−iωr*}` holds at
*every* radius — so `a → A_in` directly. And the normalisation lines up with the
certificate's `exp(+iωv)` convention: the horizon-regular branch is the analytic
one, exponent 0, which is the Frobenius series with `a₀ = 1`.

**Two bugs, both caught by checks written to be able to fail.**

*`iv_mul(a,a)` is not a square.* It's the product of two independent intervals,
so an enclosure straddling zero gets a negative lower bound and `iv_sqrt` traps.
Compounding it, `iv_add` rounds outward — so even a sum of clamped squares comes
back with `lo = f64_pred(0) < 0`, and the clamp has to sit immediately before the
square root.

*The derivative was in the wrong measure.* The relation `bE = iu′/(2ω)` is in
**tortoise** measure, but the Frobenius series differentiates in `x = r−2`.
Omitting `u′_{r*} = f·u′_r` scales the derivative by ~17 at `r₀ = 17/8`. It was
caught by using the *sharp* form of the check: `|a|² − |b|²` is **conserved**
along the flow — it *is* the Wronskian — so it must already equal 1 **at `r₀`**,
where the enclosure is still tight. Checking it only at infinity would have been
far weaker: the spin-one enclosure there is wide enough to contain 1 regardless,
and did. **Test a conserved quantity where the arithmetic is sharp, not where the
answer lives.**

After the fix, at `r = 60`:

```
spin two  |A_in|² − |A_out|² ∈ [−0.751,  3.231]   contains 1
spin one                     ∈ [−18.97, 24.33]    contains 1
```

## Precision — reported, not claimed

The Wronskian forces `|A_in_s|² ≥ 1`, hence `det(L_H) ≤ 1` at any precision. A
*lower* bound needs `|A_in|²` bounded above, and the spin-one enclosure still
reaches zero at this step budget. The gate therefore prints

```
det(L_H) >= 0.0039 ; NO upper bound at this step budget
```

rather than a number it hasn't earned.

The step budget is sized so `verify -full` — two backends under ASan — fits the
ten-minute budget rather than timing out, since a timeout is not a pass. A
100000-step/`r=100` run gives a much tighter spin-two Wronskian `[0.247, 1.820]`
but blows that budget. **Validation and precision are separate axes**: the
identity holds at this budget; precision is bought by step count, first order in
step size (widths `31.0, 6.52, 1.34, 0.34` at `4e3, 2e4, 1e5, 4e5` steps).

## The workarounds went back into the substrate

The two bugs above were not really *our* bugs — they were two missing operations in
`math/interval`, worked around by hand at the call site. Both are now named library
operations (tango `e8379bb1e`):

- **`iv_sqr`** — a true square. `iv_mul(a,a)` is the product of two *independent*
  intervals, so `iv_mul([-1,2],[-1,2]) = [-2,4]` where the square is `[0,4]`. The
  straddling lower bound is **exactly** zero: zero is attained, so there is nothing
  to round outward.
- **`iv_nonneg`** — intersect with `[0,∞)`, the sound way to say *this is a modulus*.
  It **traps rather than clamps** when the enclosure is provably negative, so a
  contradiction cannot be laundered into a plausible answer.
- **`iv_pow`** — extremal endpoints by sign and parity, binary exponentiation:
  `log₂(n)` roundings instead of `n`, with no compounded dependency.
- **`iv_sqrt`** no longer returns a negative lower bound. `iv_sqrt([0,4])` was
  `[-4.9e-324, 2.0000000000000004]` — sound as an enclosure, *outside the codomain*,
  and the reason the next square root in the chain trapped.
- **`rat_of_f64`** — exact `f64 → Rat`. Every finite float **is** a rational, and
  without that bridge the module's only oracle widened by an ulp on each side — the
  same size as the effects directed rounding must get right. The gate now checks
  4096 interval pairs against true ranges computed in exact rational arithmetic.

The gate drops both hand-written workarounds and reports `|A_in_1|² ∈ [0, 24.33]`
instead of `[-5e-324, 24.33]`.

**One negative result worth recording.** Exact-aware rounding (error-free
transformations — the residual is computed exactly, so a bound is bumped only on the
side it points to, and not at all when the operation is exact) was measured on
`iv_add`/`iv_sub` and **rejected**: 7.7% slower for 1.5e-10 of width on 3.18. This
enclosure is truncation-dominated — width falls first order in step count — so the
same 7.7% spent on steps is worth ≈0.24 instead. The ulp floor is real (24000 exact
additions accumulate 8.0e-12 out of nothing) but would take ~1e9 steps to bind. It is
used where exactness is *structural* (`iv_sqr`, `iv_pow`, `iv_sqrt`), where it is free.
Sign-dispatched multiplication was free at equal precision and cut `verify -full` on
this gate from 4m10s to 3m23s.

## det(L_H) ∈ [0.659, 0.883] — the budget was being spent in the wrong place

The chain was right. Every one of its *resources* was misallocated, and the fix was
three measurements, each of which moved the answer more than raising the step count
ever did. The reset frames named above were never needed.

**The mesh.** `local_transition` encloses `exp(A_box·h)` where `A_box` is a **box**
over the whole step, so its width goes like `|A'|·h` — the method is **first order
regardless of the Peano–Baker order**. Cost is therefore governed by `∫|A'| dr`, and
with `A = c(r)M(θ)`, `c = 6/r²`, `dθ/dr = r/(r−2)`:

    |A'| ~ 6 / (r(r−2))

**That `1/(r−2)` is the oscillation, not the potential** — invisible if you look only
at `V`. Over `[2.125, 60]` the leg `[2.125, 3]` carries **62% of the weight in 1.5% of
the length**, while `[10, 60]` absorbs 86% of a uniform mesh's steps to carry 6.8%.
Grading by `h ∝ |A'|^{−1/2} ∝ √(r(r−2))` — equal steps per unit `arccosh(r−1)` — bought
**16×** on `|A_in₁|²` at the *same* step count. More than the 4.4× the weight integral
predicts, because an error made near the horizon is then amplified by the whole
remaining transport.

**The domain.** After grading, 16× more steps bought 10%. Saturated — and the floor was
not the integrator. The tail bound is `6/R`, an **additive** error no step count can
touch, and `4|a|(6/R)` at `R = 60` is 0.8, exactly the width that had stopped moving.
Grading makes large `r` nearly free, so `R → 6000` took the floor with it.

**The order.** 12 reproduces 4 to **nine significant digits** at 2.1× the cost:
`αh ≈ 1e−4`, so the truncation tail was never binding — the coefficient box width was.

| | before | after |
|---|---|---|
| `det(L_H)` | `≥ 0.0039`, no upper bound | **`[0.659, 0.883]`** |
| `|A_in₁|²` | `[0, 24.33]` | `[1.172, 1.378]` |
| `|A_in₂|²` | `[0.051, 3.231]` | `[0.983, 1.049]` |

**Two results, both asserted now rather than printed.**

`det(L_H) ∈ [0.659, 0.883]` lands strictly inside the programme's **independently
derived** `0 < det(L_H) < 0.9787`. Two unrelated derivations of the same quantity that
have to agree — and do.

`|A_in₁|² ∈ [1.172, 1.378]`, whose strict lower bound above 1 *is* `|A_out₁|² > 0`:
**certified nonzero reflection in the spin-one channel.** Spin two is **not** claimed —
`[0.983, 1.049]` still straddles 1, and a straddle is not a result.

Both checks fail at 20000 steps and both fail at `R = 60`, so they are falsifiable at
this budget rather than decoration. The under-resolved reporting branch is kept: a run
that cannot bound the reciprocal must still say so.

## What this does not establish

**The criterion is about eigenvalues.** `spec(L_H) ⊂ (0,1)` is not decided by a
determinant. `det(L_H) ∈ (0,1)` is a necessary condition and a cross-check on the
programme's own bound, nothing more. Closing the ghost question needs the spectrum —
`T₋` assembled, `L_H = G⁻¹T₋⁻†H_H T₋⁻¹` formed, and `ivmat`'s validated eigenvalue
enclosures applied — not a sharper `det`.

Nearer term, `|A_in₂|²` still straddles 1, so spin-two reflection is undecided. Same
lever again: the enclosure is now integration-limited rather than domain-limited, so
step count buys it back at first order until the next floor appears.

## Verification

```bash
cd forge && FORGE_LIB=$PWD/lib forge verify -full \
    examples/weyl_rw_factor_transport_gate.forge     # 17/17, c==native, asan clean
```
