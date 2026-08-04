# Toward `T₋`: the validated factor transport, landed

**Gate** tango `forge/examples/weyl_rw_factor_transport_gate.forge` — 17/17,
`verify -full`: **`c==native`, ASan-clean on both backends**
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

## What remains, precisely

This is **not** `T₋`. Three things are left, and the first two are the genuinely
hard ones:

1. **The horizon**, `r = 2` — a regular singular point with exponents `0` and
   `−4iω`. Needs a Frobenius start with a rigorous enclosure to reach `r₀ > 2`.
2. **Infinity** — an irregular singular point. Needs a validated Jost remainder
   to read `A_in` off `u ~ A_in e^{+iωr*} + A_out e^{−iωr*}`.
3. **The extension coefficient** coupling the two spin-two copies. The Wronskian
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
