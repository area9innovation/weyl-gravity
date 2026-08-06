# The Bach vacuum equation is biharmonic

**Certificate** `BH0D_BACH_VACUUM_IS_BIHARMONIC`
**Rail** Forge, `tango/forge/examples/weyl_biharmonic_source_gate.forge` — 9/9
**Dependency tag** `LOCAL-ALGEBRAIC`
**Builds on** `BH0B` (the linear equation) and `BH0C` (Tully-Fisher forces gamma universal)

> Section 5 separates what is computed from what is argued, and for this result that line
> matters more than usual — the identity is exact, the sourcing conclusion is not.

---

## 1. The identity

In spherical symmetry the Laplacian is `f'' + 2f'/r`. Applying it twice to an **unspecified**
`B`:

```
nabla^4 B  =  B'''' + 4 B'''/r  =  (1/r) (r B)''''
```

verified by two independent routes as an identity in `B` and its derivatives.

So `BH0B`'s linear equation `L = 0` **is** `nabla^4 B = 0`. The Bach vacuum condition in the
conformal gauge says, simply: **B is biharmonic.** The forced solution space
`{1/r, 1, r, r^2}` is the radial biharmonic kernel — and `r^3` and `r^(-2)`, its nearest
neighbours, are verified *not* to lie in it.

That the equation is linear and fourth-order is not an accident of the gauge choice. It is
what a fourth-order conformal theory is.

## 2. Why this changes the status of gamma

`BH0B` showed the linear potential `gamma r` **survives** as one of four coefficients. This
says why the equation has that shape, and it upgrades the claim:

| operator | point-source potential | its coefficient |
|---|---|---|
| `nabla^2` | `1/r` | the mass — Newton, and where `beta = GM/c^2` comes from |
| `nabla^4` | `r`, since `nabla^2 r = 2/r` is harmonic away from the origin | the total fourth-order source |

**`gamma r` is the point-source response of the operator.** Not a term that merely survives
the equation — the term the equation *produces* for a localised source. That is a
considerably better reason for it than surviving an ansatz.

## 3. The fork this sharpens

The coefficient of a point-source response scales with whatever the source integrates to.
`BH0C` established that Tully-Fisher forces `gamma` to be **universal**, and that a `gamma`
carrying a piece proportional to `M` gives `v^4` proportional to `M^2` — the wrong slope.

So there is a fork, and both branches are informative:

- the fourth-order source integral is **not** proportional to baryonic mass — which requires a
  specific conformal matter coupling, and exhibiting it *is* the physical content; or
- the Tully-Fisher slope comes out **wrong**.

Exposing that rather than smoothing it over is the point of computing this.

## 4. How the checks are built

- **Unspecified function, not a fixture.** `B` is an opaque head throughout.
- **Two routes to one operator** — the twice-applied Laplacian and `(1/r)(rB)''''` must agree.
  That is what makes this a computation rather than a restatement.
- **The Laplacian is pinned first.** `1/r` must be harmonic *and* `nabla^2 r` must equal `2/r`,
  so a wrong Laplacian is caught before anything downstream is believed, and an operator that
  annihilates everything is excluded at step one.
- **The operator must exclude things.** `r^3` and `r^(-2)` are required non-biharmonic —
  without that, "the kernel is `{1/r, 1, r, r^2}`" would be satisfied by an operator that
  annihilates everything.

## 5. What is computed, and what is argued

Every check is an exact symbolic identity over the rationals. **The sourcing conclusion is
not computed.** The step from *"r is the biharmonic analogue of 1/r"* to *"gamma tracks the
total source"* is an argument about Green's functions: no Green's function is constructed and
no multipole integral is evaluated. The further step from *"the total source"* to *"the
baryonic mass"* is precisely the matter-coupling question, which remains open.

The certificate claims the **identification**, not the sourcing.

## 6. A substrate gap this exposed

The first run scored **7/9**, and the two failures were a finding rather than an error.
Forge's `canon` gives a confluent *structural* normal form but does not distribute products
over sums — a documented "not a CAS" boundary — so `sym_eq` could not decide an identity whose
two sides differ by distribution. `sym_expand` was added as a deliberate opt-in extension
leaving `canon` byte-identical for existing callers.

This is the **second** substrate gap this physics line exposed. The first was the absence of
symbolic differentiation altogether.

## 7. What this does not establish

- **That gamma is proportional to baryonic mass.** Untouched. Conformal invariance forbids a
  mass scale, which is what makes it hard.
- **Any Green's function.** None constructed, no integral evaluated.
- **Novelty.** The reduction to a fourth-order Poisson problem is Mannheim-Kazanas 1989. What
  is contributed is the identification computed for an *unspecified* function here, with the
  kernel and its non-members verified, rather than cited.
- **Anything about rotation curves, MOND, dark matter, or observation.**
- **The general two-function ansatz** — same gauge assumption `BH0B` carries.

## 8. Next

The matter coupling, now posed as sharply as it can be: **does the fourth-order source
integrate to something proportional to baryonic mass?** If yes, `gamma` is proportional to `M`
and `BH0C` says the Tully-Fisher slope is wrong. If no, the conformal matter coupling that
avoids it is the physical content and should be exhibited. Flanagan 2006 argues the Newtonian
limit fails when matter is coupled conformally; that objection sits exactly on this fork.

Either branch is a result.

---

## Verification

```bash
cd tango/forge && export FORGE_LIB=$PWD/lib
forge -run examples/weyl_biharmonic_source_gate.forge    # 9/9
```

Exact rational arithmetic, symbolic differentiation over unknown functions. No floating point.
