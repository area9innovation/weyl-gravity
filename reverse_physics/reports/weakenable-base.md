# The weakenable base — recognised, not invented

**Certificate** `REVERSE_PHYSICS_WEAKENABLE_BASE_V1`
**Rail** `reverse_physics/weakenable_base.py` — 10/10 checks
**Bears on** the stream's oldest open problem
**Dependency tag** `LOCAL-ALGEBRAIC`

> **This does not close the problem.** It gives it a shape, and shows the shape
> was already there. §5.

---

## 1. The problem

Reverse mathematics proves `T ⟺ A` **over a base**, and the base must be weak
enough not to prove `A` already. Every equivalence in this stream is instead over
a **declared carrier** — a set of objects, not a theory — and a set of objects
cannot be weakened one axiom at a time. Every certificate says so.

## 2. The observation

**A carrier is not a bare set.** It is presented by *construction constraints* —
*"an integral of a local density"*, *"built from the metric alone"*, *"every
index contracted into a scalar"*. And a set of constraints **is a theory**.

```
carrier                    the base
construction constraints   the axioms of the base
C ⊆ C'                     T(C) ⊢ T(C'), so C' is the WEAKER base
A vacuous on C             T(C) ⊢ A
enlarge until A is live    weaken until the base no longer proves A
```

So this stream has been **weakening a base three times already** and calling it
carrier enlargement. The weakenable base did not need inventing. It needed
recognising, writing down, and ordering.

## 3. The lattice

Take the classification carrier's constraints as base axioms. Every subset is a
base, ordered by inclusion.

| base (axioms retained) | testable | vacuous |
|---|---|---|
| locality, metric-only, indices-contract | 4 | `RP-LOCAL`, `RP-METRIC`, `RP-DIFF` |
| locality, metric-only | 5 | `RP-LOCAL`, `RP-METRIC` |
| locality, indices-contract | 5 | `RP-LOCAL`, `RP-DIFF` |
| metric-only, indices-contract | 5 | `RP-METRIC`, `RP-DIFF` |
| locality | 6 | `RP-LOCAL` |
| metric-only | 6 | `RP-METRIC` |
| indices-contract | 6 | `RP-DIFF` |
| **(empty — the weakest)** | **7** | **none** |

Two things are checked rather than assumed:

**Vacuity is monotone in the base.** Dropping an axiom can only make more
assumptions live, never fewer. That is what makes the order meaningful.

**The migration invariant is constant.** `(axioms in the base) + (live
assumptions) = 7` everywhere on the lattice. **Content is conserved; only its
visibility moves.** A base is *better* when it is *weaker*, because more of the
content has become testable.

## 4. Migration is the operation

When a construction constraint coincides with an assumption, removing it from
the base and **adding it to the assumption set** preserves the theorem. The
constraint used to cut the carrier down; the assumption now does it instead.

| base axiom | assumption | status |
|---|---|---|
| locality | `RP-LOCAL` | **migrated** — [`carrier-enlargements.md`](carrier-enlargements.md) |
| metric-only | `RP-METRIC` | **migrated** — same |
| indices-contract | `RP-DIFF` | **migrated** — [`diff-independence.md`](diff-independence.md) |

A fourth candidate, *"curvature degree exactly two"*, is **not an independent
axiom**: the derived derivative order obtains it from `RP-WEYL ∧ RP-DIM4`, so
including it would be redundant. The stream's own best result is what removes it.

With all three migrated, the remaining base is: **a real-valued functional of
some field content, with the field content itself unconstrained.** Everything
else is an assumption carrying a witness.

**The last three certificates reached the weakest base without announcing it.**
This report is the recognition, not the work.

## 5. What this does not establish

- **Not that the equivalence survives an arbitrary migration.** Verified for the
  three actually done, each with a certificate and witness; a declared structure
  for the rest. *A base one **can** weaken is not the same as having weakened it
  everywhere it matters.*
- **Not reverse mathematics.** There is no proof system here, no notion of what
  a base *proves* beyond "which assumptions hold identically on the objects it
  admits", and no independence results in the logical sense. The correspondence
  is **structural** — useful, and calling it more would be the overclaim this
  ledger exists to catch.
- **Not a construction of the weakest base.** *"A real-valued functional of some
  field content"* is a description, and no computation in this stream is carried
  out over it.
- **Not a complete constraint list.** These are the constraints this stream
  declared for its own carrier; another reading might find more.

---

```bash
PYTHONPATH=. python3 -m reverse_physics.weakenable_base --check
```
