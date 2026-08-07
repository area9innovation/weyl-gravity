# The gauge layer, vector sector: what else could generate a symmetry, and does it

**Status** result
**Dependency tag** `LOCAL-ALGEBRAIC`
**Certificate** `REVERSE_PHYSICS_GAUGE_VECTOR_SECTOR_V1`
**Gate** `tango/forge/examples/curvature_symbolic_family_gate.forge`, check 16, 16/16

---

## 1. The question, and which half of it this is

`gauge-layer-brief.md` §3 records the gap plainly: **the reverse-physics question has never
been asked of the gauge structure.** For the action and the field equations the stream asked
*"what is this equivalent to?"*. For the gauge layer it asked only *"is `RP-DIFF`
independent?"* — strictly weaker.

The question worth asking is whether the gauge algebra `Diff ⋉ Weyl` is an **assumption** or is
**forced by the action**. If forced, the gauge structure stops being a layer of the ledger at
all — it collapses the way the derivative order did, and for the same kind of reason.

That question splits in two by the type of the gauge parameter:

| sector | parameter | status |
|---|---|---|
| scalar | `σ` | **already settled** — `REVERSE_PHYSICS_SYMBOLIC_FAMILY_V1`, exactly one generator at curvature degree ≤ 2 over a *complete* ten-element list |
| vector | `ξ_μ` | **this report** |

## 2. Why it is computable at all

Noether's second theorem makes gauge symmetries and Noether identities the same data. A local
operator `Δ_{μν}[ξ]` generates a gauge symmetry exactly when `E^{μν}Δ_{μν}[ξ]` is a total
divergence for every metric — equivalently when the **adjoint** vanishes identically. At
derivative order one in the parameter,

```
Δ_{μν}[ξ] = S_{μν}^{ρσ} ∇_ρ ξ_σ        adjoint:   ∇_ρ ( S_{μν}^{ρσ} E^{μν} )
```

Writing `W^ρ_σ = S_{μν}^{ρα} E^{μν} g_{ασ}`, the condition is `∇_ρ W^ρ_σ = 0` identically — a
covariant divergence of a rank-2 object, which is **exactly the operation N1 already
performs**. So the machinery is reused rather than rebuilt: the same Bach tensor, the same
`cov_jets`, the same symbolic metric family. (The stream's recorded failure mode is building
what the repository already has; this is the cheap way not to.)

## 3. The result

At **derivative order one** in the parameter and **curvature degree ≤ 1** in the coefficient,
the only vector-parameter generator is the **diffeomorphism** one.

With the scalar sector's single generator, the gauge algebra at this order is `Diff ⋉ Weyl`,
with nothing hidden.

## 4. The negatives are the result

The two positive cases are already known, and are recomputed here only as premises:

| candidate | adjoint | is |
|---|---|---|
| `δ^ρ_μ δ^σ_ν` | `∇_ρ E^{ρσ}` | **N1**, the Diff generator |
| `g_{μν} g^{ρσ}` | `∇^σ (tr E)` | **N2**, the Weyl generator |

What makes *"exactly these"* evidence rather than an enumeration that never ran is that
curvature-weighted candidates **must fail**. Three were posed and all three do:

- `R δ^ρ_μ δ^σ_ν` → `(∇_ρ R) B^ρ_σ`. Note this is **not** the reparametrisation `ξ ↦ Rξ`,
  which would carry extra `∇R` terms — it is a genuinely different candidate.
- `Ric_{μν} g^{ρσ}` → `∇^σ (B^{μν} Ric_{μν})`. This is the negative the brief names by hand,
  requiring `B^{μν}R_{μν} ≡ 0`, which is not an identity.
- `Ric` as a mixed factor → `∇_ρ (B^ρ_a Ric^a_σ)`.

**Liveness is checked before any of them**, because every test here is satisfied by the zero
tensor. The Bach tensor must be nonzero over the family, and so must `R` and `B^{μν}Ric_{μν}`.

## 5. One control is vacuous, and says so

The Weyl candidate `g_{μν}g^{ρσ}` has adjoint `∇^σ(tr E)`. The Bach tensor is **traceless**, so
`tr E` is identically zero and its gradient vanishes *for that reason*, not independently. It
is reported as **reducing to N2**, not as a passing check.

A control evaluated where the thing it measures degenerates proves nothing, and this programme
has hit that failure mode repeatedly. Saying so is cheaper than being caught by it later.

## 6. The module trap, sharpened

The brief warns that gauge symmetries form a **module over functions**, so `g_{μν}Rσ` is the
Weyl generator reparametrised rather than a new symmetry, and a naive kernel dimension
overcounts.

The vector sector shows the trap is **strictly worse**. The degree-zero candidate
`g_{μν}g^{ρσ}` gives

```
Δ_{μν} = g_{μν} (∇·ξ)
```

which is the Weyl generator with parameter `σ = ∇·ξ` — a **differential** reparametrisation of
the parameter, not a functional one. So the quotient must be taken by *differential operators*
on the parameter, and a count that quotients only by function multiplication **still
overcounts**.

Concretely: the naive degree-zero kernel has **three** elements (`δδ`, `δδ` transposed, `gg`)
and the generator count is **two**.

## 7. What this does not establish

- **Completeness at higher order.** This is derivative order one and curvature degree ≤ 1. The
  boundary is real; the claim is a *lower bound on completeness* at the order computed.
- **That the algebra is forced.** It establishes that nothing else appears at this order, which
  is the *evidence* for forcing, not the statement of it.
- **Anything about the Stückelberg entanglement** (gap 2). `RP-DIFF` independence remains
  conditional on `RP-METRIC`.
- **Anything at degrees `(3,1)`, `(4,2)`** of the enlarged carrier — gap 1 is untouched.

## 8. Next

Extend the coefficient degree, and the parameter's derivative order to two. The order-zero
sector `T_{μν}^ρ ξ_ρ` is also unenumerated, though at curvature degree ≤ 1 there is no natural
rank-3 candidate built from `g` alone. Gap 2 is likely structural, and the honest outcome there
may remain *"recorded, not resolved"*.
