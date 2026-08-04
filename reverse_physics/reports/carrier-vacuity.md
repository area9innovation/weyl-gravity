# Carrier vacuity — the operation behind both enlargements

**Certificate** `REVERSE_PHYSICS_CARRIER_VACUITY_V1`
**Rail** `reverse_physics/carrier_vacuity.py` — 33 graded pieces in `D = 2,3,4`,
10/10 checks, two independent rank routines
**Bears on** the stream's oldest open problem: no reversal over a weakenable base
**Dependency tag** `LOCAL-ALGEBRAIC`

---

## 1. Two instances of one move

Twice this stream has been stuck on an assumption that looked untestable in
principle, and twice the same move unstuck it.

| | why it was stuck | the enlargement | what came out |
|---|---|---|---|
| `RP-REVERSIBLE` (§4.2) | on Hamiltonian carriers every evolution is `exp(tA)`, so reversibility cannot fail | finite-state stochastic maps | `reversible ⟺ deterministic ∧ conserves information` |
| `RP-DIFF` (§4.7) | the carrier is curvature *scalars*, so diff-invariance cannot fail | drop the contraction requirement | 55 witnesses; the derived derivative order requires `RP-DIFF` |

Two instances is the point where it stops being a trick and starts being a
method. This report states the method, makes its central test mechanical, and
applies it to the whole Weyl ledger — where it finds **three** assumptions in
that position, not one.

## 2. The trichotomy

For an assumption `A` and a carrier `C`, exactly one holds:

```
VACUOUS   A holds on every element of C
EMPTY     A holds on no element of C
LIVE      both A and ¬A are realised in C
```

and the whole content is:

> **`A` can be witnessed on `C` iff `A` is not vacuous on `C`.**

Immediate, once stated: `T4` asks for an element of `C` satisfying the other
assumptions and failing `A`. If `A` is vacuous there is no such element **for
reasons having nothing to do with `A` being necessary**.

So *"no witness found"* and *"no witness can exist here"* are completely
different findings, and a ledger that does not distinguish them **reports a
property of its own arena as a property of the theory.** That is exactly what
§6 did with `RP-DIFF` for as long as it stood.

### The reverse-mathematics reading

This is what makes it worth formalising. Reverse mathematics asks which axioms
are equivalent to a theorem *over a base*, and the base must be weak enough not
to prove them already — asking whether an axiom is necessary over a base that
already proves it is meaningless.

```
the carrier IS the base
an assumption VACUOUS on the carrier IS an axiom the base already proves
```

That correspondence turns the stream's oldest open problem — *"no reversal over
a weakenable base"*, open since the beginning — from an abstract wish into a
**concrete operation with two worked instances**.

## 3. The operation

A carrier is not a bare set. It is presented by **construction constraints** —
*"built by contracting tensors"*, *"of the form `exp(tA)`"*, *"polynomial in
finitely many jets"*. The diagnosis:

> **An assumption that is also a construction constraint of the carrier is
> vacuous on it, and the enlargement that makes it testable is the removal of
> that constraint.**

Both historical cases are instances. `RP-DIFF` was the constraint *"indices
contract into scalars"*. `RP-REVERSIBLE` was *"evolutions are `exp(tA)`"*.
Neither was cleverness about the old carrier, and neither could have been.

## 4. What is computed

Order-zero metric densities `√−g · h^n · g^m`, graded by `(n,m)`, in `D = 2,3,4`.
For each graded piece, the exact dimension of the diff-invariant subspace over
ℚ, by two independent rank routines.

The condition is `δM = 0` on the **scalar factor**, not `δ(√−g M) = 0`. Under
`x' = x + εAx` the integral is invariant iff `δ_alg D = −tr(A)·D`, and with
`D = √−g M` and `δ(√−g) = −tr(A)√−g` the `√−g` contribution cancels from both
sides. `√−g` is *already* a scalar density of weight one, so the integral is
invariant exactly when `M` is a scalar.

| `D` | `n` | `m` | basis | diff-inv | weight | Weyl? |
|---|---|---|---|---|---|---|
| 2 | 0 | 0 | 1 | 1 | 1 | |
| 2 | 1 | 0 | 3 | 0 | 0 | ✅ |
| 2 | 1 | 1 | 9 | 1 | 1 | |
| 2 | 2 | 1 | 18 | 0 | 0 | ✅ |
| 2 | 2 | 2 | 36 | 2 | 1 | |
| 3 | 0 | 0 | 1 | 1 | 3/2 | |
| 3 | 1 | 1 | 36 | 1 | 3/2 | |
| 4 | 0 | 0 | 1 | 1 | 2 | |
| 4 | 1 | 1 | 100 | 1 | 2 | |
| 4 | 2 | 0 | 55 | 0 | 0 | ✅ |

33 pieces computed, 12 skipped over the basis-size cap and **listed** — no
silent truncation.

### Three findings, checked not asserted

**F1 — the diff-invariant subspace is nonzero exactly when `n = m`.** A monomial
with `n` upper and `m` lower index pairs can be fully contracted only when they
balance. Confirmed across three dimensions and the whole affordable grid.

**F2 — Weyl invariance needs `n − m = D/2`**, which has **no integer solution in
odd dimension**. So there is no Weyl-invariant order-zero metric density at all
there. This meets §3.9's *"odd dimensions admit no conformally invariant
curvature action"* and §4.6's odd-dimension parity obstruction **from a third
direction**, and none of the three was set up to find the others.

**F3 — therefore `RP-DIFF` and `RP-WEYL` are never simultaneously satisfiable at
derivative order zero, in any dimension.** `n = m` and `n − m = D/2` force
`D = 0`.

**F3 is the sharp form of §4.7's consequence.** The derived derivative order does
not merely *use* `RP-DIFF` somewhere. `RP-DIFF` is **what makes derivative order
zero impossible** — and only once order zero is excluded does the weight law
`D − 2k = 0` pin the order at `D/2`. Drop `RP-DIFF` and the theory has a
weight-zero sector with no derivatives at all.

## 5. The audit — three vacuous assumptions, not one

Applying the trichotomy to the Weyl ledger on the carrier the classification
actually used:

| assumption | | why |
|---|---|---|
| `RP-LOCAL` | **VACUOUS** | the carrier is local densities by construction |
| `RP-METRIC` | **VACUOUS** | the carrier is built from `g` alone by construction |
| `RP-DIFF` | **VACUOUS** | the carrier is curvature *scalars* by construction |
| `RP-DIM4` | LIVE | `D` is a parameter of the family, not a constraint on elements |
| `RP-WEYL` | LIVE | `R²` fails it, `C²` satisfies it, both in the carrier |
| `RP-TOPO-INERT` | LIVE | `E₄` is in the carrier and is the witness |
| `RP-PARITY` | LIVE | `W₊²` is in the parity-extended carrier |

The ledger already half-knew this. It says `RP-LOCAL` and `RP-METRIC` *"bound
the coordinate space rather than being tested inside it"*, and separately that
`RP-DIFF` *"is invisible"*. **Those are one phenomenon with one cure, filed as
two different kinds of caveat.**

~~Only `RP-DIFF` has been enlarged.~~ **All three are now enlarged**
([report](carrier-enlargements.md)):

- `RP-METRIC` → admit a compensator scalar. `√−g φ^{2D/(D−2)}` is diff- **and**
  Weyl-invariant at derivative order zero, which **breaks F2 and F3 above**. The
  exponent falls out rather than being put in, and reproduces `φ⁶`, `φ⁴`, `φ³`
  in `D = 3, 4, 6` — the classical trio, integer exactly when `(D−2) | 4`.
- `RP-LOCAL` → admit inverse boxes. `k − j = D/2` has **one** solution when
  `j = 0` and one per `j` otherwise, so locality is what makes the
  classification *unique*.

Both are exactly the two escapes left open by `C-NO-CHEAP-FIX` in the comparison
ledger — and with all three now enlarged, the joint statement is that **the
derived derivative order requires all three**, each failing differently. See
[`carrier-enlargements.md`](carrier-enlargements.md) §4.

**These assignments are declarations** — judgement about which construction
constraints define the carrier — recorded so they can be disputed. Only the
graded computation is mechanical.

## 6. A self-criticism this audit surfaces

On the order-zero carrier, `RP-DIFF` is **EMPTY, not LIVE**: by F3 nothing there
is diff-invariant.

The witness stands — `T4` asks only for an element satisfying the others and
failing `A`, which the 55 do. But **a LIVE carrier is strictly better**, because
on an empty one the law itself is absent and the reader has to take the
comparison on trust.

The union carrier — order zero **plus** the quadratic curvature scalars — *is*
live, and that is checked: **3 of 58**. The two pieces sit in different
derivative orders and the `GL` action preserves derivative order, so the
invariant subspace of the direct sum is the direct sum of the invariant
subspaces.

So the honest statement of §4.7 is: the witness is valid on an empty carrier and
becomes a *live* witness on the union, which is the carrier the ledger should
quote.

## 7. What this does not establish

- **The audit's assignments are declarations**, not computations. Only the
  graded piece is mechanical.
- **F1 beyond the affordable grid.** Everything skipped by the basis cap is
  listed in `skipped`.
- **Nothing at nonzero derivative order.** The whole computation is at order
  zero, where the Weyl transformation is purely multiplicative and there are no
  derivatives of the conformal factor to handle.
- **Enlargement is not guaranteed to be available.** This is a diagnosis and a
  direction. `RP-LOCAL` and `RP-METRIC` are *named*, not solved.
- **This is not a weakenable base.** It identifies the operation such a base
  would systematise and gives it two worked instances. It does not build one.

---

## Verification

```bash
PYTHONPATH=. python3 -m reverse_physics.carrier_vacuity --check
# 33 graded pieces, 12 skipped and listed; F1 F2 F3 hold; 10/10; PASS
```

Pure `fractions.Fraction`; no sympy, no floating point.
