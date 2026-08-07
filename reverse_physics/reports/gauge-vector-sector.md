# The gauge layer, vector sector: what else could generate a symmetry, and does it

**Status** result
**Dependency tag** `LOCAL-ALGEBRAIC`
**Certificate** `REVERSE_PHYSICS_GAUGE_VECTOR_SECTOR_V1`
**Gate** `tango/forge/examples/curvature_symbolic_family_gate.forge`, checks 16-18, 18/18

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

At **every derivative order up to and including three**, the only vector-parameter generator is
the **diffeomorphism** one — at curvature degree ≤ 2 in the coefficient for orders zero and one,
and at degree zero for order three. Orders zero, one and three are computed; order two is **empty
by index parity** (§4b), and so is order four.

The scalar sector is settled at the *same* curvature degree, so both halves of the claim now
stand at the same degree rather than one half-claim beside another: the gauge algebra at these
orders is `Diff ⋉ Weyl`, with nothing hidden.

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

## 4b. Order zero, and why order two costs nothing

**Order two is empty by counting indices.** A coefficient at derivative order `k` in a vector
parameter carries `2 + k + 1` indices. Every tensor built from the metric, its inverse, `δ` and
**undifferentiated** curvature has **even** rank — `g` and `δ` are rank 2, Ricci 2, Riemann 4,
the scalar 0. The odd-rank coefficient the even orders require cannot be built. **The next
possible order after one is three, not two.**

**That argument has a limit, and it is exactly why order zero was computed** rather than
dismissed with it: *derivatives* of curvature have **odd** rank (`∇_aR` is rank 1, `∇_aR_{bc}`
is rank 3). So order zero *is* reachable, with one derivative on the curvature. Two candidates
were posed — `∇^ρR_{μν}` and `∇_μR δ^ρ_ν` symmetrised — and both come back **nonzero**. No
generator there either.

Order zero is also the cheap sector: its adjoint is `T_{μν}^ρ E^{μν}` with no integration by
parts — a **contraction** rather than a divergence.

## 4bb. Curvature degree two, and the candidate it would have been easy to omit

The scalar sector was already settled at curvature degree ≤ 2 while the vector sector stopped
at ≤ 1, so the joint claim was lopsided. Three structurally distinct candidates close it —
**not** three variations on one:

| candidate | what carries the indices |
|---|---|
| `\|Ric\|² δ^ρ_μ δ^σ_ν` | a degree-2 **scalar** times the known generator |
| `Ric^ρ_μ Ric^σ_ν` | both free indices carried by **Ricci** |
| `R^ρ{}_μ{}^σ{}_ν` | built from **Riemann** beyond its Ricci trace |

All three come back **nonzero**. No generator hides at degree 2 either.

**The Riemann-built one is the point**, and the scalar sector is why. Its inherited
seven-tensor list was built from `g` and `Ric` alone, and the candidates it *omitted* were
exactly the ones contracting against Riemann — an omission that was caught and cost a
correction. `E^{μν}` here **is** the Bach tensor, which sees the full Weyl tensor and not only
its traces, so a Riemann-built candidate is precisely the kind that could carry a second
generator. Leaving it out would have repeated a known omission knowingly.

## 4c. Triviality is excluded by construction, not asserted

Every action has **trivial** gauge symmetries `Δ = M[E]` with `M` antisymmetric under exchange
of its index pairs. They exist for any action whatsoever, are infinite in number, and must not
be counted — a count that ignores them is meaningless.

They are excluded here **by construction**: every coefficient enumerated is built from the
metric and curvature and never from `E`, and the Bach tensor is fourth order in the metric, so
no candidate at this degree can contain it.

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

## 6b. Order three, and the witness that settles it by failing

Order three is affordable for a reason worth recording: a degree-zero coefficient is built from
`g`, `g^{-1}` and `δ`, so it is **covariantly constant** and passes straight through the
derivatives —

```
∇∇∇( S E )  =  S · ∇∇∇E
```

— so one third covariant derivative of the Bach tensor is computed **once** and every candidate
is a contraction of it. `∇³B` is seventh order in the metric, so the jets run at outer degree 7.

**Three positive controls hold.** Whenever the *innermost* derivative contracts with an index of
`B`, the innermost operation is `∇·B`, which N1 says is zero. All three such contractions vanish
identically through a rank-5 object — N1 differentiated twice.

**The interesting part is the other three.** Each is separately **nonzero**, but their
base-point **rank is 2 of 3** — which looks like a fourth symmetry. So the vanishing combination
is *exhibited*, by carrying an identity through the elimination (the technique the cubic
quotient uses), and rebuilt on the **full jets**, where a real relation would have to be the zero
polynomial at every outer order.

**It is not.** One witness at the base point, **zero** verified identically.

That decides it, in the **opposite direction** to what the rank suggested. The base-point kernel
is one-dimensional, spanned by that witness. Any identically-vanishing combination would also
vanish at the base point, hence be proportional to the witness — and the witness demonstrably
does not vanish identically. So none does: the true rank is **exactly 3**, the kernel is
**exactly 3**, and those three are the contractions that vanish *because of* N1 and N2 — the
differential reparametrisations of `Diff` and `Weyl`.

**Nothing new at order three**, and the reparametrisation span never needed enumerating: the
kernel is already exactly the set that vanishes for N1/N2 reasons.

### Why this is worth stating as a method, not just a result

Both wrong readings were live.

- Reading the base-point rank of 2 as exact would have **invented a symmetry that is not there**.
  It was an apparent degeneracy at one point, not a relation.
- Reading *"each of the three is nonzero"* as sufficient would have reached the **right answer for
  the wrong reason** — the same confusion that forced the cubic action count from 7 down to 5.

A rank is a floor in one direction; a witness is what closes it in the other. Here it closes it
by **failing** to verify.

## 6c. Curvature in the coefficient at order three — sampled, not enumerated

The covariant-constancy shortcut is **gone** here: `∇S ≠ 0`, so the derivatives act on the
coefficient too and the adjoint must be taken of the *product*.

The naive route was not attempted — `∇³` of the rank-4 product is `n⁷` jets at outer degree 7,
gigabytes of exact rationals per candidate. Instead the divergence is taken **at every step**:
each derivative index meets an index of the object it differentiates and the innermost contracts
first, so

```
Y_{ρστλ}  --div ρ-->  A_{στλ}  --div σ-->  B_{τλ}  --div τ-->  C_λ
```

and the rank never exceeds `n⁵`. Same peak cost as degree zero; only the order of contraction
changed.

**The control is the degree-zero answer.** Run with the coefficient set to the constant `1`, this
pipeline must reproduce what the covariantly-constant route already settled — the innermost
divergence lands on `B`, that divergence is N1, the adjoint vanishes. It does. A new pipeline is
checked against the settled one *before* any new answer is read off it.

**Result:** three structurally distinct candidates — scalar-weighted, trace-weighted, and
**Riemann-built** — are all **nonzero**, so none is a symmetry. The Riemann-built one is in the
set precisely because it is the shape an inherited `g`-and-`Ric` list omits, an omission this
programme has already been bitten by.

**This is weaker than the degree-zero result, and is stated as such.** At degree zero every
contraction pattern was enumerated, ranked, and closed with a witness. Here three candidates are
**sampled**. *"These three fail"* is not *"the space is empty"*.

## 7. What this does not establish

- **An exhaustive result at curvature degree ≥ 1 at order three.** Three candidates were sampled
  and all fail (§6c); the enumeration is not done. Nor anything at derivative order five or above
  (four being empty by parity). The claim is a *lower bound on completeness*.
- **That the algebra is forced.** It establishes that nothing else appears at this order, which
  is the *evidence* for forcing, not the statement of it.
- **Anything about the Stückelberg entanglement** (gap 2). `RP-DIFF` independence remains
  conditional on `RP-METRIC`.
- **Anything at degrees `(3,1)`, `(4,2)`** of the enlarged carrier — gap 1 is untouched.

## 8. Next

**Enumerate curvature degree one at order three properly**, rather than sampling it. The
contract-as-you-go pipeline and its degree-zero control already exist, so what remains is the
candidate list itself plus a rank and witness over it — the same shape that closed degree zero.
Gap 2 is likely structural, and the honest outcome there may remain *"recorded,
not resolved"*; gap 1, the degrees `(3,1)` and `(4,2)`, is untouched.
