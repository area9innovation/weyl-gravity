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

**The cross-check that licenses this.** The certificate's gauged block and this
stream's factor companion came from completely different routes — theirs by a
rational gauge `T = [J,N]` on the six-state system, ours by clearing denominators
in `D_r*²u + 2iω D_r*u − Vu = 0`. They agree entrywise at 30 radii:
`6(r−1)/(r²(r−2))` is our `V₂/f²`, and `−2i(ωr²−i)/(r(r−2))` expands to
`−(2+2iωr²)/(r²−2r)`, exactly our `−P`.

**Result:**

```
X(2.4 → 3.0), entry (1,0) ∈ [0.07592875168485574, 0.07718132970732572]
```

**Nonzero** — the extension genuinely does not split. The corpus certifies
`axial_ell2_nonsplit_all_positive_real` abstractly; this is that fact as a
number.

## What remains — quantitative, not structural

All three `T₋` objects now exist. What is left is sharpening:

1. **Tighten the enclosures.** The interaction picture's saturated width `~2.2`
   is bounded but not sharp, and is dominated by the `[3,30]` leg where the
   coefficient is largest — starting further out and refining steps is the lever.
2. **Push the amplitudes through** the matching layer already validated, giving
   `|A_in_s|`, then `det(L_H) = 1/(|A_in₂|⁴|A_in₁|²)` as a number rather than the
   programme's current bound `0 < det(L_H) < 0.9786…`, and finally `spec(L_H)`
   against `(0,1)` — which closes the ghost question either way.

With all three, `T₋` assembles, `L_H = G⁻¹T₋⁻†H_H T₋⁻¹` follows, and
`ivmat`'s validated eigenvalue enclosures decide `spec(L_H) ⊂ (0,1)` — closing
the ghost question either way.

## Verification

```bash
cd forge && FORGE_LIB=$PWD/lib forge verify -full \
    examples/weyl_rw_factor_transport_gate.forge     # 17/17, c==native, asan clean
```
