# Symbolic metric families are cheap, and that changes what is provable here

**Rail** Forge, `tango/forge/examples/curvature_symbolic_family_gate.forge` — 9/9, 4.15 s
**Substrate** `tango/forge/lib/math/jetfield.forge`
**Dependency tag** `LOCAL-ALGEBRAIC`

> A capability note, not a physics result. What it establishes is that a caveat carried by
> most of this stream's certificates is **removable at low cost** — not that it has been
> removed from any of them yet. §4.

---

## 1. The caveat this attacks

Every curvature result in this stream is computed **at specific metrics** — a dozen exact
rational fixtures, ranks taken over them. That is strictly stronger than an unverified
citation and strictly weaker than a theorem, and the certificates all say so.

"Zero at twelve fixtures" is not "zero for all metrics".

## 2. The lever

A jet **is** a truncated polynomial over its coefficient type. So the moment `Jet<Rat>`
satisfies the `Field` vocabulary that `Jet<T>` demands of its coefficients, jets nest:

```
Jet<Jet<Rat>>     outer variables = the spacetime coordinates
                  inner variables = the symbolic metric parameters
```

No new polynomial type, no second arithmetic to keep in step with the first. An identity
that comes back zero is zero **as a polynomial in the parameters** — every member of the
family at once.

**Division is the catch, handled by never asking.** `Field` demands `finv`, and a polynomial
ring inverts only units. `christoffel` takes `half` as an argument and `ci_weyl` takes
`1/(D−2)`; `metric_inverse` — the one routine that divides — is replaced by building
`g = L S Lᵀ` and `g⁻¹ = (L⁻¹)ᵀ S L⁻¹` directly, both polynomial because `L` is unit
lower-triangular. `jet_inv` still traps on a non-unit, which is the correct failure.

## 3. The cost, measured rather than predicted

| parameters | max terms in a Riemann coefficient |
|---|---|
| 1 | 1 |
| 2 | 3 |
| 3 | 4 |
| 4 | 7 |
| 5 | 10 |
| **6 — the full unit-lower-triangular family** | **10** |

Whole sweep, identities only: **2.75 s, 74 MB**; with Weyl tracelessness added, **3.85 s**.

**I predicted this was infeasible and was wrong by four orders of magnitude.** A worst-case
monomial count gives `C(22,6) = 74,613` terms at degree 16 with six parameters. The actual
maximum is **ten**, and growth *plateaus* at five — curvature polynomials are extremely
sparse, and jets store only nonzero terms.

The gate demands the **full** six-parameter family for exactly this reason: a prediction must
not be allowed to become a cap. Had I trusted my own arithmetic and stopped at three, the
ceiling would never have been found.

### Three things that had to be right at six slots and were not at two

- **`L⁻¹ = I − N + N² − N³` exactly**, since `N⁴ = 0` for a 4×4 strictly-lower matrix. The
  earlier `L⁻¹ = I − N` is valid only when `N² = 0` — true for two non-chaining slots,
  **wrong for six**, which chain through `(2,1)`, `(3,1)`, `(3,2)`. The `inv` column verifies
  `g g⁻¹ = I` as a polynomial identity at every parameter count.
- **The inner degree is derived, not tuned.** Entries linear in the parameters give `g⁻¹`
  degree 6, `Γ` degree 8, **Riemann degree 16**. Less than that silently truncates the
  curvature itself.
- **Every row reports `unsat`.** A family that outgrows the truncation announces itself
  instead of quietly returning zeros — the failure mode that turns "the identity holds" into
  a vacuous pass.

## 4. The first claim actually upgraded

**Weyl tracelessness.** `C^a{}_{bad} = 0` was established by `ci_trace_sq` at a dozen exact
fixtures. It now holds as a **polynomial identity** over the full six-parameter family, at
every parameter count from 1 to 6. Whole sweep with it included: **3.85 s**.

**No new tensor code was written.** The `ci_*` layer works on *values* of type `T` with
`Field<T>`, so taking the constant term in the **coordinates** first leaves
`ManualVec<Jet<Rat>>` — curvature at the base point, still polynomial in the parameters — and
`ci_lower_first`, `ci_ricci`, `ci_weyl`, `ci_trace_sq` all apply unchanged with
`T = Jet<Rat>`. The existing contraction layer was already generic enough; it just had never
been handed anything but rationals.

**The paired control is what makes the zero evidence.** The *same* trace operation applied to
**Riemann** gives Ricci and is required to come back **nonzero** — reported as
`riem-trace-nonzero` on every row. So the machinery demonstrably detects a nonzero trace, and
Weyl's vanishing is a fact about Weyl rather than about a routine that returns zero for
everything. Weyl is separately required to be nonzero and to depend symbolically on the
parameters, or the identity would hold for a family that is secretly one metric.

### The second: `G1`, the coordinate vectors

`REVERSE_PHYSICS_WEYL_GEOMETRY_DISCHARGE_V1` establishes `G1` **on a single metric**:

```
C² = Riem² − 2 Ric² + R²/3                        (D = 4)
C² = E₄ + 2 Ric² − (2/3) R²,   E₄ = Riem² − 4 Ric² + R²
```

These are the coordinate vectors **the entire `D = 4` classification is expressed in**, so
one metric was a thin footing. Both now hold as polynomial identities over the full
six-parameter family. Sweep with `G1` included: **4.15 s**.

The negative control is the same identity with `R²/4` in place of `R²/3` — it must **fail**,
and does on every row. Without it, "the identity holds" would be satisfied equally well by
three scalars that were all zero, which is why they are separately required to be nonzero.

Again no new tensor code: `ci_raise_slot`, `ci_raise2` and `ci_dot` used exactly as on
rationals. **The contraction layer keeps turning out to be generic enough already** — what
was missing was only ever a coefficient ring to hand it.

## 5. What this does **not** establish

- **Two claims are upgraded, not the ledger.** Weyl tracelessness and `G1` are done; the
  trace law `N2`, `N1` (`∇^a B_ab = 0`) and the Noether generator count are not.
- **"All metrics in the family" is not "all metrics".** `det g = −1` identically, so the
  family is **unimodular** — a codimension-one restriction — and the coordinate dependence is
  a fixed quadratic rather than general. An enormous step from twelve sampled points; still a
  family.
- **Five identities are verified so far** — last-pair antisymmetry, the first Bianchi
  identity, Weyl tracelessness, and the two `G1` forms. The first two exercise the pipeline
  rather than settling anything in doubt; tracelessness and `G1` were standing ledger claims.
- **The Euler operator is not yet available over this ring**, so the Noether-identity result
  is still at sampled fixtures.

## 6. What it opens

The next targets all need the same missing piece — **the Euler operator over this ring** —
because each is about the *variation* rather than the curvature: `N1` (`∇^a B_ab = 0`, which
needs the Bach tensor), the trace law `N2`, and the Noether identity generator count — which
would turn *"one generator at three fixtures"* into *"one generator for every metric in the
family"*, the actual reverse-physics statement about the gauge algebra.

---

## Verification

```bash
cd tango/forge && export FORGE_LIB=$PWD/lib
forge -run examples/curvature_symbolic_family_gate.forge   # 9/9, 4.15 s, 78 MB
```

Exact rational arithmetic throughout. No floating point, no tolerance.
