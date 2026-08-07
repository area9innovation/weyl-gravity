# The gauge layer: what exists, and the one question nobody has asked

**Status** brief — scoping. **The vector half of §3 is now a result**: see
`gauge-vector-sector.md` and `REVERSE_PHYSICS_GAUGE_VECTOR_SECTOR_V1`. This file remains the
scoping document for what is still open.
**Dependency tag** `LOCAL-ALGEBRAIC` (the computation it specifies would be)

> **First finding, and it is a correction.** The work item's `objective` says the gauge
> structure is *"UNTOUCHED and is the largest genuine hole."* **That is stale.** It predates
> `diff_independence.py`. The consolidated report already grades the layer **witnessed**.
> Anyone starting from the objective would rebuild something that exists.

---

## 1. What already exists

This section is the point of the brief. The stream's recorded failure mode is *building
things the repository already has*, and the gauge layer is the worst place for it, because
the relevant work is spread across five directories that reverse physics has never cited.

**In `reverse_physics/` — the assumption-level work.**

| | |
|---|---|
| `RP-DIFF` independence | `REVERSE_PHYSICS_DIFF_INDEPENDENCE_V1`. On the enlarged carrier of local metric densities at derivative order zero, the lowest weight-zero degree `√−g h^{ab}h^{cd}` is 55-dimensional and **entirely Weyl-invariant**, while its Diff-invariant subspace is **exactly 0** — two independent exact-rational rank routines, with a control space of known dimension 1 found to be 1. All 55 are witnesses. |
| the consequence | the derived derivative order `k = D/2` — the ledger's strongest result, *"four derivatives is a consequence, not an assumption"* — **silently requires `RP-DIFF`**. |
| `N1` | `∇^a B_ab = 0`, **computed** against the repository's own Bach tensor, not imported. This *is* the Noether/diff content. **Since generalized** — `REVERSE_PHYSICS_SYMBOLIC_FAMILY_V1` now holds it as a **polynomial identity** over a symmetric metric family rather than against specific metrics, over a smaller sub-family than `G1`/`G3` because three covariant derivatives are expensive. |
| `N2` | the trace law `g^{mn} E_mn = 2(a + b + 3c) □R`, discharged. For `C²`, `a + b + 3c = 0`, so the Bach tensor is traceless — the Noether/Weyl content. |
| `N3` | topological terms have identically vanishing variation. |

**Elsewhere — the BV/BRST machinery reverse physics has never engaged.**

- `field_bv_identification/` — an exact chain isomorphism between the minimal BV tangent
  chain and the raw `G → M → E → I` chain, with explicit projector and homotopy proving
  `Q s + s Q = P`, in exact rational matrices. Real, certified BV structure.
- `quantum-weyl/` (≈380 files touching BRST/BV) — local BV, the anomaly vector, the
  one-loop QME obstruction and its compensator.
- `d_quotient_classical/` (≈150) and `closed_universe_observers/` (≈64).

**So the honest summary is:** the gauge layer has *one* assumption-level result and a
*mountain* of structural machinery, and the two have never been connected.

## 2. The three gaps, each stated by the existing certificate itself

1. **The witness is one degree deep.** Only the lowest weight-zero degree `(2,0)`. Degrees
   `(3,1)`, `(4,2)`, … are also weight zero and unclassified. The order-zero space is
   infinite-dimensional as a polynomial algebra; only its lowest graded piece is settled.
2. **Independence is conditional.** The Stückelberg escape — promote the coordinates to
   fields and any non-covariant theory becomes covariant — is **blocked by `RP-METRIC`, not
   refuted**. What holds is `RP-DIFF` independent *given* `RP-METRIC`; the two are entangled.
3. **The reverse-physics question has never been asked of the gauge structure.** For the
   action and the field equations the stream asked *"what is this equivalent to?"* For the
   gauge layer it asked only *"is `RP-DIFF` independent?"* — a strictly weaker question.
   **PARTLY DISCHARGED.** Both sectors of the generator span are now computed at bounded
   order: the **scalar** one by the generator count in `REVERSE_PHYSICS_SYMBOLIC_FAMILY_V1`
   (exactly one generator, complete ten-element list), and the **vector** one by
   `REVERSE_PHYSICS_GAUGE_VECTOR_SECTOR_V1` (only the diffeomorphism generator, with three
   curvature-weighted negatives that all fail). What remains is higher order — see §8 of
   `gauge-vector-sector.md`.

## 3. The question worth asking

> **Is the gauge algebra `Diff ⋉ Weyl` an assumption, or is it forced by the action?**

If forced, the gauge structure stops being a layer of the ledger at all — it collapses
exactly the way the derivative order did, and for the same kind of reason. That is the
shape of the stream's best existing result, applied to the one layer that has never had it.

**Why it is answerable.** Noether's second theorem makes gauge symmetries and Noether
identities the same data. The stream currently **cites** that theorem in one direction
(`RP-DIVFREE` is free from `RP-DIFF` via `N1`). The converse — *are `N1` and `N2` all the
identities there are?* — has never been computed. Both known identities are already
computed exactly, so the controls exist before the experiment does.

**The claim to aim at.** The space of Noether identities of `S = ∫√−g C²`, at bounded
derivative order, has dimension exactly `D + 1` — `D` from diffeomorphisms, one from Weyl —
and is spanned by `∇_μ E^{μν} = 0` and `g_{μν} E^{μν} = 0`. Nothing hidden.

## 4. How to compute it, and the trap in it

**The formulation.** `δS = ∫ E^{μν} δg_{μν}`. A local operator `Δ_{μν}[ε]`, linear in a
parameter `ε` with bounded derivative order, generates a gauge symmetry exactly when
`E^{μν}Δ_{μν}[ε]` is a total divergence for every metric — equivalently when the adjoint
`Δ†[E]` vanishes identically, which is the Noether identity. Enumerate a basis of such `Δ`
with **constant** coefficients over metric-built tensors, impose the condition at many exact
metrics, and take the kernel over ℚ. That is the stream's standard rank idiom, and the
Euler operator needed to apply it already exists and is now chart-audited (15/15).

**The trap, and it would produce a wrong count** — and it is **worse than stated here**; the
vector-sector computation found that the quotient must be by *differential* operators on the
parameter, not merely by function multiplication, because `g_{μν}(∇·ξ)` is the Weyl generator
with `σ = ∇·ξ`. See §6 of `gauge-vector-sector.md`. The gauge symmetries form a **module over
functions of the fields**, not a vector space. `Δ_{μν} = g_{μν}σ` is the Weyl generator; but
`Δ_{μν} = g_{μν} R σ` also satisfies the condition, and is **not a new symmetry** — it is
the same generator with the parameter reparametrised, `σ ↦ Rσ`. A naive kernel dimension
counts these separately and **overcounts**. The count must be taken modulo field-dependent
reparametrisation of the parameter, and *any result that does not say how it handled this is
not to be believed.* This is the same class of error as the one
`REVERSE_PHYSICS_PARITY_SCALAR_CONTROL_V1` corrects: an object that satisfies every test
posed while not being the thing the test was about.

**Controls, both directions.**

- *Positive:* the Lie derivative `∇_μ ξ_ν + ∇_ν ξ_μ` and the Weyl generator `g_{μν}σ` must
  appear. If they do not, the enumeration or the adjoint is wrong.
- *Negative — the one that makes it evidence:* a candidate that must **fail**. `R_{μν}σ`
  requires `B^{μν}R_{μν} ≡ 0`, which is not an identity. It must come back **not** a
  symmetry. Without a candidate that fails, "we found exactly two" is indistinguishable from
  an enumeration that never ran — the failure mode this stream has now hit three times in
  one session.
- *Chart control:* every operand is a hand-built contraction, so the `SL(n,ℤ)` rail from
  `curvature_coord_scalar_control_gate` applies and should be wired in from the start rather
  than added after a retraction.

**Bounded order is a real boundary, not a formality.** Whatever order the enumeration
reaches, the result is a statement at that order — a **lower bound on completeness**, in the
same sense every count in this stream is a lower bound over the family evaluated. It must be
reported that way.

## 5. What would falsify it

A Noether identity independent of `N1` and `N2` at the order computed. That would mean Weyl
gravity has a gauge symmetry nobody has written down — which is a much larger claim than the
expected answer, and correspondingly needs the negative control to be beyond doubt before it
could be believed.

## 6. Why not the other two gaps first

**Gap 1** (extend the witness past degree `(2,0)`) is cheap and closes a stated boundary,
but it extends a witness rather than answering a new question — the answer is very likely
"still zero", and the ledger does not change either way.

**Gap 2** (the Stückelberg entanglement) is the sharpest conceptually, and I suspect the
entanglement is **structural** — that `RP-DIFF` cannot be made unconditionally independent
while `RP-METRIC` holds, because the escape is exactly the introduction of a second field.
If so the honest outcome is *"recorded, not resolved"*, which the certificate already says.

Gap 3 is the only one of the three whose answer changes the ledger.
