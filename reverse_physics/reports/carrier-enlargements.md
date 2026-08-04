# `RP-METRIC` and `RP-LOCAL` — the last two vacuous assumptions

**Certificate** `REVERSE_PHYSICS_CARRIER_ENLARGEMENTS_V1`
**Rail** `reverse_physics/carrier_enlargements.py` — 14/14 checks
**Completes** the audit in [`carrier-vacuity.md`](carrier-vacuity.md)
**Dependency tag** `LOCAL-ALGEBRAIC`

---

## 1. What was left

The vacuity audit found **three** assumptions vacuous on the carrier the
classification used — `RP-LOCAL`, `RP-METRIC`, `RP-DIFF` — and only `RP-DIFF`
had been enlarged. The other two were named as the same shape of task. This is
that task, by the same operation: **remove the construction constraint that made
the assumption vacuous, and see what appears.**

| assumption | constraint removed | enlargement |
|---|---|---|
| `RP-METRIC` | *built from the metric alone* | admit a compensator scalar |
| `RP-LOCAL` | *polynomial in finitely many jets* | admit inverse box operators |

Both are settled by **weight bookkeeping**, which is why they are cheap. At
derivative order zero the Weyl transformation is purely multiplicative, so a
density is invariant exactly when its weight vanishes, while diffeomorphism
invariance is a separate index-counting condition. The two conditions compete,
and that competition is the whole story.

## 2. `RP-METRIC` — and the exponent that comes out right

A conformally coupled scalar carries weight `−(D−2)/4` under `g → λg`, so

```
√−g · h^n · g^m · φ^k     has weight   D/2 − n + m − k(D−2)/4
```

`φ` is a `GL` scalar and contributes nothing to the diffeomorphism condition,
which is still `n = m` (finding F1). Imposing both:

```
n = m    and    D/2 = k(D−2)/4     ⟹     k = 2D/(D−2)
```

That is exactly the conformal scalar potential exponent. **It was not put in** —
it falls out of two independent conditions, and it reproduces the standard
answer:

| `D` | `φ` weight | `k = 2D/(D−2)` | witness |
|---|---|---|---|
| 3 | −1/4 | **6** | `√−g φ⁶` |
| 4 | −1/2 | **4** | `√−g φ⁴` |
| 5 | −3/4 | 10/3 | — not an integer power |
| 6 | −1 | **3** | `√−g φ³` |

And the integer cases are **exactly `D = 3, 4, 6`**, checked out to `D = 50`:
`2D/(D−2) = 2 + 4/(D−2)` is an integer iff `(D−2)` divides `4`. That trio is the
classical answer for which dimensions admit a *polynomial* conformal scalar
potential, and it is the sharpest available check that the bookkeeping is right.

**So `√−g φ⁴` witnesses `RP-METRIC`**: local, diffeomorphism-invariant,
Weyl-invariant, parity-even, `D = 4`, at **derivative order zero** — and the law
fails on it.

### It breaks both findings of the vacuity report

- **F3 fails.** In pure metric gravity, `RP-DIFF` and `RP-WEYL` are *never*
  simultaneously satisfiable at derivative order zero, in any dimension. With
  one compensator scalar they are.
- **F2 fails.** In odd dimension the metric-only carrier has no weight-zero
  density at all. `D = 3` with `φ⁶` has one.

That both findings survive exactly as far as `RP-METRIC` holds, and fail the
moment it is dropped, is what makes them findings *about the assumption* rather
than about the arena.

### The control

`φ` being `GL`-inert is what leaves the diffeomorphism condition untouched. If
the compensator carried an index, the answer would change — and it does: the
inert-like case (`h^ab`) has 0 invariants where the index-carrying case
(`h^ab g_cd`) has 1. The computation is sensitive to inertness rather than
indifferent to it.

## 3. `RP-LOCAL` — why the classification is unique at all

Allow `j` inverse box operators. `□` carries one inverse metric, so `□⁻¹`
carries weight `+1`, and a density of curvature degree `k` with `j` of them has

```
weight = D/2 − k + j        invariant  ⟺  k − j = D/2
```

| | |
|---|---|
| `j = 0` (local) | `k = D/2` — **one** solution. The classification's uniqueness. |
| `j` unbounded | `k = D/2 + j` for every `j ≥ 0` — **infinitely many**. |

Checked in `D = 4` and `D = 6`: exactly 1 local solution, and `j+1` solutions up
to any bound `j`.

**So `RP-LOCAL` is what makes the invariant family unique**, and dropping it
destroys the uniqueness rather than merely adding an option. An explicit witness
sits at `(k, j) = (3, 1)`.

### What does *not* change, stated because it's easy to get wrong

The **net** derivative order of such a term is `2k − 2j = 2(k−j) = D` — still
four in `D = 4`. Verified: every solution has the same net order.

**Nonlocality does not buy a different derivative count.** It buys a different
*pole structure*, which is the actual mechanism cited for infinite-derivative
gravity. This computation does not reach that, and the certificate says so.

## 4. The joint consequence

§4.3 — the stream's best result — says the derivative order is *derived* rather
than assumed: `D − 2k = 0` forces `k = D/2`. All three vacuous assumptions turn
out to be load-bearing for it, and **each fails differently**:

| drop | what becomes available |
|---|---|
| `RP-DIFF` | derivative order **0** — F3 says diff and Weyl invariance cannot both hold there, and without `RP-DIFF` only the second is required |
| `RP-METRIC` | derivative order **0** via `√−g φ^{2D/(D−2)}`, which is diff *and* Weyl invariant |
| `RP-LOCAL` | every `k ≥ D/2`; uniqueness is destroyed, not weakened |

§4.3 said the standard motivation *"uses one more physical input than it needs"*.
That stands. What is added is **precisely which inputs it does need** — and all
three were untested until the vacuity audit and this.

## 5. A row of the ghost table, filled in carefully

[`weyl-ghost-forced.md`](weyl-ghost-forced.md) lists the escapes from the
Ostrogradsky ghost. `RP-LOCAL` and `RP-METRIC` are *"plausibly yes — a citation,
not a theorem here"*. `RP-DIFF` was **"not analysed"**, because it had no witness
in this framework.

It can now be analysed, and the statement is narrow:

> Dropping `RP-DIFF` makes weight-zero densities available at derivative order
> zero, so **the pole-count argument no longer runs.**

That is **not** the same as removing the ghost. A non-covariant theory is not
thereby ghost-free, and neither is a nonlocal or multi-field one without a
separate argument. What is established is that the *derivation* fails — which is
exactly the status the other two rows already carry, so `RP-DIFF` joins them
rather than outranking them.

## 6. What this does not establish

- **No ghost is removed.** Only the derivation is shown not to run.
- **Nothing at nonzero derivative order for Part A.** The compensator analysis is
  at order zero. The conformally coupled *kinetic* term is a separate, standard
  object and is not computed here.
- **Part B counts solutions of a weight condition**, not independent invariants
  at each `(k, j)`. The actual dimension at each point is not computed.
- **Infinite-derivative gravity is not shown ghost-free.** The net derivative
  order is shown *unchanged* by finitely many inverse boxes; the literature's
  mechanism is an entire form factor, which is outside this computation.
- **No witness is claimed to be a sensible theory.** A witness need not be.

---

## Verification

```bash
PYTHONPATH=. python3 -m reverse_physics.carrier_enlargements --check
# integer powers exactly in D = [3, 4, 6]; 14/14; PASS
```

Pure `fractions.Fraction`; no sympy, no floating point.
