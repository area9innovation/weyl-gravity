# The cubic sector, modulo total derivatives

**Certificate** `REVERSE_PHYSICS_CUBIC_ACTION_QUOTIENT_V1`
**Rail** `tango/forge/examples/curvature_symbolic_euler_gate.forge`, check 9
**Dependency tag** `LOCAL-ALGEBRAIC`

> The first statement in this repository about the dimension of a space of cubic **actions**
> rather than cubic **invariants**. Both numbers are one-sided bounds, and section 3 says why
> that is sound rather than a hedge.

---

## 1. The gap this addresses

Two certificates say the same sentence verbatim:

> *"the quotient by total derivatives. It is not needed for a pointwise count and **it was not
> performed**, so nothing here is a statement about LAGRANGIANS, about actions, or about the
> trace anomaly's coefficients."*

The quadratic case was done earlier, on a sector whose answer was independently known
(Gauss-Bonnet). **The cubic sector is where that sentence actually sits.**

## 2. The computation

The Euler operator *is* the quotient: `E[L] = 0` exactly when `L` is a total divergence, so the
space of actions is the image of `L -> E[L]` and the total derivatives are its kernel.

Over the eight standard cubic scalars - `R^3`, `R|Ric|^2`, `R|Riem|^2`, `Ric^3`,
`Ric.Ric.Riem`, `Ric.Riem^2`, and the two `Riem^3` contractions:

```
rank(VALUES) = 8          rank(EULER) = 5
```

**Two ranks, not one, and the second alone would mislead.** A linear relation among the
scalars that is a *scalar identity* in D = 4 passes through the Euler operator trivially and is
**not** a total derivative. So

```
dim(total derivatives) = rank(VALUES) - rank(EULER)
```

Here `rank(VALUES) = 8` saturates, so the eight are genuinely independent as functions and
**every element of the Euler kernel is a real total derivative**, not an identity among the
scalars.

## 3. The bounds, and why one-sided is sound

A rank at a point is a **lower** bound on the generic rank.

- `rank(VALUES) = 8` is **exact** - 8 is the number of rows and cannot be exceeded.
- `rank(EULER) >= 5`, hence `dim(kernel) <= 3` and `dim(actions) >= 5`.

Neither is claimed as an equality. Pinning them means exhibiting the kernel explicitly - three
combinations verified to be total derivatives - which is not done here.

## 4. How the checks are built

- **Each scalar must have a nonzero Euler derivative.** Required, or a scalar that happened to
  be a total derivative on its own would quietly reduce the rank without that being visible.
- **Evaluated off the parameter origin.** At the origin the family degenerates to the **flat**
  metric and every curvature scalar vanishes; an earlier quotient check read `RANK = 0` for
  exactly that reason. Both ranks are taken at distinct small rationals.
- **Fraction-free elimination**, so the whole computation stays in exact integer-ratio
  arithmetic.

## 5. What this does not establish

- **Exact dimensions.** At least 5 actions, at most 3 total derivatives.
- **Anything about D = 6 or the weight-6 derivative sector.** Only the cubic algebraic carrier
  in D = 4. Weight 6 needs the metric at degree 6, where the jets hold 924 terms per component,
  and remains the cost problem.
- **That the eight are a complete spanning list.** They are the standard eight; completeness is
  inherited from the literature, not derived. An invariant outside the span would not be seen -
  the same boundary that made an inherited candidate list incomplete elsewhere in this stream.
- **Any conformal count.** This is the quotient of the *full* cubic carrier, not of its
  conformally invariant subspace, so it does not by itself convert the published cubic conformal
  counts into action counts.

## 6. The kernel, exhibited but not pinned

Candidates come from augmenting the Euler matrix with an identity and reducing the `M` half; a
row whose `M`-part vanishes carries the combination in its `I`-part. Each is then **verified
identically** - the combination's Euler derivative must be the zero *polynomial*, not merely
zero at the evaluation point.

**3 candidates, 1 verified.** Two were artefacts of the point, which is exactly what the second
pass exists to catch. A second evaluation point (free - the polynomial rows are already
computed) also gives rank 5.

**The tension is reported, not resolved.** If the generic kernel were the full 3-space, all
three basis vectors would verify; one does. If the generic rank exceeded 5, a generic point
should show it; two points both show 5. So either both points are special, or the kernel is
sensitive to the basis the elimination happens to produce.

What *is* established: **at least one genuine total derivative**, verified as a polynomial
identity, and the kernel lies inside an explicit 3-space - so `dim(cubic actions)` is between
**5 and 7**.

## 7. Next

**Pin the kernel.** Deciding whether the other two dimensions are real needs either a third
evaluation point that separates them, or - better - solving for the identical nullspace
*within* that 3-space directly, rather than testing whichever basis the elimination produced.
The latter is a small linear problem over the polynomial coefficients. Pinning it would give
the cubic analogue of `E_4 = Riem^2 - 4 Ric^2 + R^2`, where exhibiting the combination is
precisely what made the quadratic result sharp.

Then the conformally invariant subspace, which is what would actually convert the published
cubic conformal counts from counts of *invariants* into counts of *actions*.
