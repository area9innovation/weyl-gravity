# ~~Parity is **not** redundant on the `D = 6` field equations~~ — RETRACTED

> ## ⛔ RETRACTED. The result below is wrong.
>
> The Lagrangian differentiated here is **not a scalar**. Its slot spec summed one
> contracted index over two **lower** slots and another over two **upper** slots, with no
> metric between either pair, so the value is **coordinate-dependent**: under `x = Ay` with
> `A ∈ SL(6,ℤ)` it moves from `6566972251/160` to `−200078513393/160`. The first of those
> is exactly the `L(g)` this report prints as its conformal-invariance control.
>
> So `E⁰⁰ = −12614421113/320` and `E¹² = 1224309325271/160` are the Euler–Lagrange
> expression of a chart-dependent quantity and **mean nothing**. The conclusion — that
> `RP-PARITY` is not redundant on the `D = 6` field equations — is **withdrawn**.
>
> **What is not wrong.** The **Euler operator** is untouched, including its `n = 6`
> exercise: `L = ∂₀√|det g|` is a total divergence by construction and its field equations
> still come back exactly zero. The instrument was right; the Lagrangian it was pointed at
> was not. The measure rule is also unaffected.
>
> **What the answer actually is.** The `D = 6` parity-odd cubic sector is **empty** —
> 3,240 patterns swept, all zero, with the **pair-exchange symmetry** `C_{abcd} = C_{cdab}`
> as the mechanism. There is no invariant here to differentiate. See
> [`parity-scalar-defect.md`](parity-scalar-defect.md), certificate
> `REVERSE_PHYSICS_PARITY_SCALAR_CONTROL_V1`.
>
> The original text follows, preserved as issued.

**Certificate** `REVERSE_PHYSICS_PARITY_FIELD_EQUATIONS_V1`
**Rail** Forge, `tango/forge/examples/curvature_parity_field_equations_gate.forge` — 6/6
**Dependency tag** `LOCAL-ALGEBRAIC`

> **Local, not global.** The Euler operator tests whether a Lagrangian is *locally a total
> divergence*. "Not topological" is **not** what is shown. §5.

---

## 1. The half that counting could not reach

The `D = 4` parity result is not *"parity-odd invariants exist"*. It is:

> `RP-PARITY` is **independent on actions** and **redundant on field equations**.

Adjoining the Pontryagin density gives `W±² = (C² ± P)/2`, both Weyl invariant — a
*two*-parameter family of **actions** but a *one*-parameter family of **field equations**,
because `P` is topological. Physically a **gravitational theta-angle**: it changes the
action, not the classical equations of motion.

[`parity-conformal-count.md`](parity-conformal-count.md) answered the existence half in
`D = 6` and recorded the rest as **not done** — because counting invariants is not a
variational question.

## 2. What comes out

Applying the Euler operator to the density of the `D = 6` parity-odd Weyl invariant:

| metric | component | value |
|---|---|---|
| 1 | `E^00` | `−12614421113/320` |
| 1 | `E^12` | `1224309325271/160` |
| 2 | `E^00` | `1290109675603/640` |

**Nonzero.** The invariant is **not locally a total divergence**, so it contributes to the
field equations. Parity is therefore **load-bearing** in `D = 6`: it cannot be dropped
without changing the physics.

**So the `D = 4` statement is special to four dimensions.**

## 3. That is the second one

[`weyl-action-d6.md`](weyl-action-d6.md) already showed the **uniqueness** of the Weyl
action is a `D = 4` accident — *"the method scales, the conclusion does not."* Parity
redundancy is the second structural fact in the ledger that doesn't travel.

And it reaches the ledger's headline. *"Six assumptions written as an action, five written
as field equations"* turns on `RP-PARITY` and `RP-TOPO-INERT` dropping out on the
field-equation side. If `RP-PARITY` doesn't drop out in `D = 6`, **that count is
dimension-dependent** — and for reverse physics as a method, the assumption lattice is not
a fixed object attached to a theory. The vocabulary-dependence the ledger already records
(action-side versus equation-side) gains a second axis.

## 4. The two controls, and why they were built first

A **nonzero** answer is the interesting direction, which is exactly where a bug masquerades
as a discovery. Both gaps below were identified *before* the number was claimed.

**The operator had never run at `n = 6`.** Every one of the Euler gate's fourteen checks is
`D = 4`. So: `L = ∂₀(√|det g|)` is `∂_a(δ^a_0 √|det g|)` — a total divergence **by
construction**, whose field equations vanish in any dimension. They do, **exactly**, on both
components, with the Lagrangian itself checked nonzero first.

**The invariant was re-implemented in jet form.** The counting certificate validated a
`Rat`-level construction; this is a separate rebuild, and a wrong `D = 6` Weyl coefficient
(`1/4`, `1/20`) would make it a *different, non-invariant* Lagrangian whose field equations
are nonzero **trivially**. Checked directly:

```
L(g) = L(e^{2σ}g) = 6566972251/160     exactly
```

Plus: the density is nonzero before any field equation is read from it, and the result is
reproduced on a second independent metric.

### Two things that had to be got right underneath

**The measure is `|det g|`, not `√|det g|`.** Summing over permutations contracts with the
ε **symbol** while the scalar is built with the **tensor**. At a point, where the fixtures
have `|det g| = 1`, the wrong choice is invisible; as a function it is not. Validated in
`D = 4` by assembling the Pontryagin density both ways.

**The ε sum is collapsed 8×** over the antisymmetry of the three index pairs — checked exact
against the full sum on a fixture where the result is **nonzero**. A first attempt checked
it where both sides vanished identically, which established nothing; three *distinct*
operands were needed to make the comparison mean anything.

## 5. What this does **not** establish

- **Nothing global.** Vanishing field equations means *locally* a total divergence.
  Topology is a different statement. **"Not topological" is not shown; "not locally
  trivial" is.**
- **Only one of the two** parity-odd invariants in `D = 6` is differentiated. A claim about
  the whole parity-odd sector needs the other.
- **The `D = 4` result is not wrong.** It is correct there and untouched. What is
  established is that it does not travel.
- **Nothing about actions modulo total derivatives** — two Lagrangians differing by one have
  the same field equations, and nothing here distinguishes them.
- **No statement about the trace anomaly.** The type-B coefficients multiply these
  invariants, so the structure constrains what anomalies *could* exist — but this is
  classical and `LOCAL-ALGEBRAIC`, and no quantum claim follows.
- **Nothing about other dimensions, dynamics, the ghost, or anything Lorentzian.**

---

## Verification

```bash
cd tango/forge && export FORGE_LIB=$PWD/lib
forge verify examples/curvature_parity_field_equations_gate.forge   # 6/6, ~19 min, parallel
```

Resting on `curvature_euler_gate` 14/14 (the operator, validated in `D = 4` against
Gauss–Bonnet, Pontryagin and the trace law), `curvature_invariants_parity_gate` 20/20 (the
invariant, exhibited as conformally invariant), and `curvature_covderiv_gate` 23/23 beneath
those.

> **Rail scores above are as issued.** Both gates have since gained checks —
> `curvature_invariants_parity_gate` is now **22/22** (the per-candidate chart audit)
> and `curvature_euler_gate` **15/15** (the Lagrangian chart rail). Running the
> commands today gives the higher numbers; the historical figures are left as written.

Exact rational arithmetic throughout. No floating point, no tolerance.
