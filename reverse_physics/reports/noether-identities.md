# The Weyl gauge algebra has one scalar generator, and three impostors

**Certificate** `REVERSE_PHYSICS_NOETHER_IDENTITIES_V1`
**Rail** Forge, `tango/forge/examples/curvature_euler_gate.forge` — 19/19, 6m19s
**Dependency tag** `LOCAL-ALGEBRAIC`

> **Order zero in derivatives of `E`.** A statement at that order, and a lower bound on
> completeness in the same sense every count in this stream is. §5.

---

## 1. The question the stream had never asked

Noether's second theorem makes gauge symmetries and Noether identities **the same data**.
This stream *cites* that theorem in one direction — `RP-DIVFREE` is free from `RP-DIFF` via
`N1` — and had never computed the converse:

> **Are `N1` and `N2` all the identities there are?**

If they are, the gauge algebra `Diff ⋉ Weyl` is **forced by the action** and stops being an
assumption of the ledger — collapsing exactly the way the derivative order did in §4.3.

For the action and the field equations the stream asked *"what is this equivalent to?"* For
the gauge layer it had only asked *"is `RP-DIFF` independent?"* — strictly weaker.

## 2. What comes out

```
NOETHER  candidates 7   identities 4   generators 1   reparametrisations 3   kernel(dim) 4
```

| coefficient `T_{ab}` | `T_{rs}E^{rs}` | reading |
|---|---|---|
| `g` | **0** | the Weyl identity — **the generator** |
| `R·g` | **0** | `g` with `σ ↦ Rσ` |
| `R²·g` | **0** | `g` with `σ ↦ R²σ` |
| `\|Ric\|²·g` | **0** | `g` with `σ ↦ \|Ric\|²σ` |
| `Ric` | **≠ 0** | not an identity |
| `Ric·Ric` | **≠ 0** | not an identity |
| `R·Ric` | **≠ 0** | not an identity |

> **At order zero, the scalar Noether identity space of the Weyl action has exactly ONE
> generator: `g_{ab}E^{ab} = 0`.**

No hidden scalar gauge symmetry. Together with `N1` — the diffeomorphism identity
`∇_a B^{ab} = 0`, already computed and certified against this repository's own Bach tensor —
the gauge algebra at this order is exactly what the action forces, with nothing extra.

## 3. Four identities, one symmetry — read the line again

The kernel is **4-dimensional as a vector space** and **1-dimensional as a module**. That
gap is the whole methodological point.

Gauge symmetries form a **module over functions of the fields**, not a vector space.
`R·g_{ab}` annihilates `E` for exactly the same reason `g_{ab}` does: it is the Weyl
generator with the parameter rescaled. It is not a new symmetry. **A naive kernel dimension
would have reported four gauge symmetries and been wrong by three.**

This was written down in [`gauge-layer-brief.md`](gauge-layer-brief.md) *before* the
computation ran, and it is enforced rather than described: every candidate **declares in the
source** which generator it is a multiple of (`cand_generator`), so the module rank is a
stated claim that can be read and disputed — not a number inferred silently. Check 18
*requires* the vector-space dimension to **exceed** the generator count, so if the
reparametrisations ever stopped appearing, that would signal the enumeration had quietly
narrowed rather than looking like a cleaner answer.

## 4. Why the zeros are evidence

Three of the seven candidates come back **nonzero**, and that is what makes the four zeros
mean something. `Ric_{ab}E^{ab}` would require `R_{ab}B^{ab} = 0`, which is not an identity;
it is `−57/16` on the first fixture. Checks 16–17 make that a gate condition:

- **non-vacuity** — `E` itself is nonzero on every fixture, or every candidate vanishes for a
  reason having nothing to do with identities;
- **the negative control** — `Ric` and `Ric·Ric` must **fail** to be identities.

Without a candidate that fails, *"the kernel is spanned by the known identities"* is
indistinguishable from an enumeration that never ran. This session produced three separate
controls whose negative result was indistinguishable from the thing they were meant to
detect, so that is no longer a rhetorical point.

**Variance is structural, not careful.** `E^{ab}` is `δS/δg_{ab}` and carries **upper**
indices, so the coefficients are all-**lower** and the contraction contains no raise at all.
The one place variance could go wrong — inside `Ric·Ric` — has its inverse metric written
out explicitly. After eight malformed contractions were found in this stream this week, the
structure is built so the error cannot be made rather than so it can be checked for.

## 5. What this does **not** establish

- **Order zero only.** This reaches order zero in derivatives of `E`. Identities involving
  `∇E`, `∇∇E` are not enumerated. A **lower bound on completeness**.
- **The scalar sector only.** The vector sector's positive control is `N1`, already certified
  in the corpus; recomputing it costs more than the whole scalar sector and establishes
  nothing new, so it is **skipped, not passed**. The vector sector needs `E` as a **jet**
  rather than at a point — `euler_component` returns a `Rat` — which is a **degree-budget**
  cost, not an architectural gap: the pipeline is jets throughout and collapses at the last
  step.
- **Seven candidates, not all candidates.** The coefficient tensors are built from `g`, `Ric`
  and `R`. A coefficient built from the Weyl tensor or from derivatives of curvature is not
  tried. Adding candidates can only *raise* a count, so the direction is sound — but "one
  generator" is one generator **over this family**.
- **Nothing about the gauge algebra's structure constants, closure, or off-shell
  reducibility** — the BV/BRST content in `field_bv_identification/` and `quantum-weyl/` is
  not touched.
- **Nothing quantum.**

## 6. What it costs the ledger

The gauge layer was graded **witnessed** on the strength of `RP-DIFF`'s independence witness.
This is the first result that goes past *witnessed* toward *equivalent to* — the shape the
other three layers already have. It does not finish the layer, and §5 says why.

---

## Verification

```bash
cd tango/forge && export FORGE_LIB=$PWD/lib
forge -run examples/curvature_euler_gate.forge   # 19/19, 6m19s, peak RSS 180 MB
```

Exact rational arithmetic throughout. No floating point, no tolerance.

An independent sympy implementation of the same seven candidates lives at
`reverse_physics/noether_identities.py` (`--check --no-vector`). It is a **cross-check on a
different arithmetic stack with different fixtures**: the values differ, the identity pattern
must not.

**It has not run to completion.** The scalar-only sweep timed out at 1500 s, so the
cross-check is **unavailable, not passed** — a timeout is never a pass. One datum *is*
corroborated: a direct sympy probe on an independent fixture gives `trace(B) = 0` and
`Ric·B = −57/16`, matching Forge's split for those two candidates. The other five are
unconfirmed outside Forge, and **the result currently rests on one implementation.**

That is also not a clean speed comparison. The sympy fixture carries symbolic entries in all
six strictly-lower positions where the Forge run uses a lighter family, and sympy's cost here
is symbolic expression swell rather than arithmetic. The reading is that the cross-check
needs a cheaper fixture — not that Forge is four times faster.
