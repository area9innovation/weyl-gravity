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

So there are **exactly three** total-derivative combinations among the eight, and **exactly five**
independent cubic actions. Both are equalities.

> **Correction.** The first issue of this report said *seven* actions and *one* total derivative.
> Both `Riem^3` members of the basis were **malformed contractions** - one summed a repeated
> index over two *upper* slots, the other over two *down* slots. A contraction is covariant only
> when each repeated index appears once up and once down, so neither was a scalar. Repaired, the
> ranks move. Section 3b is how it was found, and it is the useful part.

## 3. Why these are exact, and why the point method had to go

The Euler rank uses **no evaluation point**. Each entry is a *polynomial* in the metric
parameters, and `sum_i c_i E_i = 0` *identically* is a linear condition on `c` over the
polynomial **coefficients**. Flattening `(component, monomial)` into columns gives a rational
matrix whose rank **is** the generic rank and whose nullspace **is** the space of total
derivatives. The monomial list is the *union of exponent vectors actually present*, collected
rather than enumerated, so it is complete without assuming a degree bound.

The `VALUES` rank is taken at a point, and that is sound for a specific reason: it comes out
**8**, the row count, and a rank cannot exceed it. A saturating point rank is exact.

**And here is the finding that forced the change.** An earlier version evaluated the Euler
matrix at a point and got rank **5** - "at least 5 actions, at most 3 total derivatives". Three
null candidates appeared and only **one** verified identically. A second, independently chosen
point *also* gave rank 5. Both were **non-generic**: the true rank is 7.

So two independent point evaluations agreed with each other and were both wrong, and the only
reason that was visible was the identical-verification pass reporting 1 of 3. Chasing the bound
with more points would not have converged. The object had to become exact.

## 3b. How the error was found

Not by re-reading the contractions. By a **known-answer control added for a different purpose.**

Extending the gate to the conformally invariant subspace needed a control, and the natural one
is that `sqrt(-g) C^2` - the Weyl action - is conformally invariant, so its defect must be
exactly zero. **That control failed**, and diagnosing it surfaced the malformed contractions in
a neighbouring, already-committed result.

The lesson is the one this programme keeps relearning, from the other direction: a control
added for one claim can falsify a **different** one. Controls are worth adding even where the
claim already looks settled.

Two control bugs of mine surfaced alongside it, both recorded rather than quietly fixed. The
pass condition tested `weyl3_live` where it meant `weyl3_ok`, so the gate reported 10/10 while
its control was failing. And the defect was first compared over *whole jets* when only orders up
to `xd - 2` are valid - Riemann costs two derivatives - which made a true identity look false.

## 4. How the checks are built

- **Each scalar must have a nonzero Euler derivative.** Required, or a scalar that happened to
  be a total derivative on its own would quietly reduce the rank without that being visible.
- **Evaluated off the parameter origin.** At the origin the family degenerates to the **flat**
  metric and every curvature scalar vanishes; an earlier quotient check read `RANK = 0` for
  exactly that reason. Both ranks are taken at distinct small rationals.
- **Fraction-free elimination**, so the whole computation stays in exact integer-ratio
  arithmetic.

## 5. What this does not establish

- **Anything about D = 6 or the weight-6 derivative sector.** Only the cubic algebraic carrier
  in D = 4. Weight 6 needs the metric at degree 6, where the jets hold 924 terms per component,
  and remains the cost problem.
- **That the eight are a complete spanning list.** They are the standard eight; completeness is
  inherited from the literature, not derived. An invariant outside the span would not be seen -
  the same boundary that made an inherited candidate list incomplete elsewhere in this stream.
- **Any conformal count.** This is the quotient of the *full* cubic carrier, not of its
  conformally invariant subspace, so it does not by itself convert the published cubic conformal
  counts into action counts.

## 6. The kernel

Candidates come from augmenting the coefficient matrix with an identity and reducing the `M`
half; a row whose `M`-part vanishes carries the combination in its `I`-part. Each is then
**re-verified as the zero polynomial**.

**1 candidate, 1 verified.** The kernel is one-dimensional and exhibited - the cubic analogue
of `E_4 = Riem^2 - 4 Ric^2 + R^2`, where exhibiting the combination is precisely what made the
quadratic result sharp.

## 7. Next

**Repair the conformal defect machinery, then read the subspace.** The restriction to the
conformally invariant subspace is implemented but its result is **withheld**: the Weyl-cubic
control fails, so the machinery is not validated at density weight `-2` and any count from it
would be an artefact. The `C^2` control passes (density weight 0, no weight factor applied) and
the cubic one fails (density weight `-2`, weight factor applied), which localises the fault to
the **weight-factor handling** rather than to the tensors. The gate prints the subspace number
only when both controls pass.

Then the **weight-6** sector, which is cost rather than method: the metric at degree 6 holds 924
terms per component.

Then the conformally invariant subspace, which is what would actually convert the published
cubic conformal counts from counts of *invariants* into counts of *actions*.
