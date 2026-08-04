# Toward `T₋`: the transport engine and the horizon start, landed

**Gates** tango `forge/examples/weyl_rw_factor_transport_gate.forge` — 20/20, and
`forge/examples/weyl_horizon_frobenius_gate.forge` — 34/34.
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

## What remains, precisely

Two things, and they are the harder two:

1. **Infinity** — an *irregular* singular point. Needs a validated asymptotic
   (Jost) remainder to read `A_in` off `u ~ A_in e^{+iωr*} + A_out e^{−iωr*}`.
   Unlike the horizon there is no convergent series; the expansion is divergent
   and needs Levinson/Olver-type error control.
2. **The extension coefficient** coupling the two spin-two copies. The Wronskian
   does not constrain it — it is the one genuinely free transport integral, and
   the reason `det L_H` is known while `spec L_H` is not.

With all three, `T₋` assembles, `L_H = G⁻¹T₋⁻†H_H T₋⁻¹` follows, and
`ivmat`'s validated eigenvalue enclosures decide `spec(L_H) ⊂ (0,1)` — closing
the ghost question either way.

## Verification

```bash
cd forge && FORGE_LIB=$PWD/lib forge verify -full \
    examples/weyl_rw_factor_transport_gate.forge     # 17/17, c==native, asan clean
```
