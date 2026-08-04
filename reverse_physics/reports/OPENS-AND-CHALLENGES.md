# What Weyl gravity opens and challenges — the comparison ledger

**Certificate** `REVERSE_PHYSICS_WEYL_VS_EINSTEIN_LEDGER_V1`
**Rail** `reverse_physics/weyl_vs_einstein_ledger.py` — 18 rows, 0 failures,
13/13 negative controls rejected
**Extends** [`PHYSICS-VS-MATH.md`](PHYSICS-VS-MATH.md)

---

## 1. Why the three-column ledger is not enough

[`PHYSICS-VS-MATH.md`](PHYSICS-VS-MATH.md) sorts one theory's claims into
PHYSICS, GEOMETRY and MATHEMATICS. That is enough to say what Weyl gravity
**is**. It is not enough to say what Weyl gravity **does relative to Einstein
gravity**, because a comparative sentence carries two things the three columns
have nowhere to put.

**A direction.** Does the claim describe something Weyl gravity makes available
that Einstein gravity forbids (**OPENS**), something Einstein gravity supplies
that Weyl gravity must now pay for (**CHALLENGES**), or something both theories
owe equally (**SHARED**)? The third is the one that goes wrong most often, by
charging Weyl gravity for a bill Einstein gravity also owes.

**A level.** Actions, field equations, solution loci, symplectic structure and
the quantum theory are five different places to assert a comparison, and *the
same sentence can flip truth value between them*.

| | level |
|---|---|
| `L0` | the action |
| `L1` | the field equations |
| `L2` | the solution locus |
| `L3` | symplectic / dynamical structure — Cauchy data, energy, counting |
| `L4` | the quantum theory |

The level axis is not invented here. Two results this repository already holds
make it impossible to state the Einstein comparison without one:

> `L2` — `Ric(g) = Λg ⟹ B_mn(g) = 0`. Every Einstein vacuum solution is a Weyl
> solution. **Proved**, `LOCAL-ALGEBRAIC`.
> ([`conformal-einstein-sector-theorem.md`](../../notes/conformal-einstein-sector-theorem.md))
>
> `L3` — `REDUCED_FLAT_EINSTEIN_SYMPLECTIC_EMBEDDING_REFUTED`. The restricted
> pure-Weyl and Einstein–Hilbert Cauchy matrices have ranks **zero** and **two**;
> no nonzero normalisation identifies them.
> ([`flat-einstein-symplectic-restriction.md`](../../reports/flat-einstein-symplectic-restriction.md))

So *"Einstein gravity is contained in Weyl gravity"* is **true at `L2` and false
at `L3`**, and both halves are established here. A comparison ledger without a
level column does not merely lose precision — it contradicts itself.

§3.2b of the three-column ledger already found the weaker version of this: the
*assumption count* differs between actions and field equations, six versus five,
for the same theory. The Einstein pair shows the *truth value* differs too.

---

## 2. The organising claim: one swap, not two lists

In reverse-physics currency, comparing two theories is not comparing
predictions. It is comparing assumption sets. Einstein gravity and Weyl gravity
sit over the **same base** and differ by exactly **one swap**:

```text
shared base   RP-LOCAL, RP-METRIC, RP-DIFF, RP-DIM4

Einstein      + RP-2ND-ORDER               →  Lovelock   →  G_ab + Λ g_ab
Weyl          + RP-WEYL (+ RP-TOPO-INERT)  →  D − 2k = 0 →  B_ab
```

Both additions are uniqueness hypotheses, and both uniqueness theorems are
stated over the same coordinate space. The Einstein one is an **import**
(Lovelock 1971/72, filed GEOMETRY in the certificate's `swap` block, cited in
place because the framing is unsupported without it). The Weyl one is **proved
here**.

**The swap is not a menu.** The conformal weight law `D − 2k = 0` admits a
Weyl-invariant local curvature action of degree `k` only when `D = 2k`, and
curvature degree `k` gives derivative order `2k`. At `D = 4` that is `k = 2` and
fourth order; Einstein–Hilbert is `k = 1`, Weyl invariant only at `D = 2`. So
**no local metric action in four dimensions is both Weyl invariant and second
order** — `RP-WEYL` and `RP-2ND-ORDER` are jointly unsatisfiable.

That is what makes OPENS and CHALLENGES two halves of **one trade** rather than
a pros-and-cons list. Every row traces to the swap, and the sharpest instance is
a pair that is literally one theorem seen twice:

| | |
|---|---|
| **OPENS** `O-DERIVED-ORDER` | the derivative order is *derived*, not assumed — one fewer physical input than the standard motivation uses |
| **CHALLENGES** `C-GHOST-FORCED` | the Ostrogradsky ghost is *forced* — `D − 2k = 0` pins the pole count at `D/2`, and two or more poles always include a negative residue |

Same equation. **The ghost is not a defect of a particular Lagrangian.** It is
the price of the assumption `RP-2ND-ORDER` was buying on the Einstein side, and
[`weyl-ghost-forced.md`](weyl-ghost-forced.md) proves the two natural evasions —
drop `RP-WEYL`, change `RP-DIM4` — provably fail.

The certificate records the trade graph explicitly. It is deliberately
many-to-one: one cost can buy several things.

```text
C-GHOST-FORCED        buys  O-DERIVED-ORDER, O-RENORMALIZABILITY
C-NO-NEWTON-CONSTANT  buys  O-SCALE
C-CAUCHY-DATA         buys  O-EXTRA-TOWERS
```

---

## 3. Why the separation is mandatory here, not merely tidy

Three failure modes that only the columns catch. One example of each is already
in this repository.

**A claim whose risk is not where the sentence sounds like it is.** *"The
Mannheim–Kazanas metric is an exact static Bach-flat solution with residual-basic
charges and simultaneous horizon first laws"* is certified here (Paper 18,
`O-STATIC-FAMILY`, MATHEMATICS). *"Weyl gravity accounts for galactic rotation
curves without dark matter"* is `O-ROTATION-CURVES` — PHYSICS, CITED, contingent
on galactic data, **not established by the first**. Same object, different
columns, and merging them would report a citation's risk as a theorem's.

**A challenge filed in the wrong column.** The ghost is usually written up as a
defect awaiting a fix, which files it under PHYSICS. Here it is MATHEMATICS: a
zero-axiom theorem. Filing it under PHYSICS is exactly what makes people look
for fixes that provably do not exist — anything calling itself a fix is an
*assumption drop*, and the ledger says which one.

**A claim with no counterfactual at all.** This stream published one — that the
coprime obstruction is how a ghost destabilises a healthy mode — and retracted
it with proof ([`coprime-charge-bound.md`](coprime-charge-bound.md)). The
successor row `C-GHOST-DYNAMICS` is **OPEN** and says so.

---

## 4. The ledger

18 rows. `PROVED` 10, `DISCHARGED` 1, `REFUTED` 1, `CITED` 3, `OPEN` 3.
By column: MATHEMATICS 12, PHYSICS 5, GEOMETRY 1.

### 4.1 OPENS

| row | level | column | status | claim |
|---|---|---|---|---|
| `O-SCALE` | `L0` | MATH | **proved** | No dimensionful constant. `√−g C²` has conformal weight zero at `D = 4`, so `α` is dimensionless, and the invariant quotient is one-dimensional so there is no second coefficient to carry a scale. |
| `O-DERIVED-ORDER` | `L0` | MATH | **proved** | Derivative order is derived. Einstein must posit `RP-2ND-ORDER`; `D − 2k = 0` forces `k = D/2`, and the same line excludes `k = 0` and `k = 1`. |
| `O-EINSTEIN-SOLUTIONS` | `L2` | MATH | **proved** | Every `D = 4` Einstein vacuum solution is a Weyl solution; the inclusion is generally **proper**. `LOCAL-ALGEBRAIC`. |
| `O-EXTRA-TOWERS` | `L2` | MATH | **proved** | The certified linear cylinder solution space carries the `A` and `L` towers beyond the Einstein-root `E` tower — dynamical extra content, not gauge copies. `REDUCED-MODE`. |
| `O-PARITY-DIRECTION` | `L0` | MATH | **proved** | `αW₊² + βW₋²` is a genuine two-parameter family of *actions*; the map is injective and `W₊²` is provably not parity-even. |
| `O-STATIC-FAMILY` | `L2` | MATH | discharged | An exact static vacuum family strictly larger than Schwarzschild–de Sitter, with residual-basic charges and simultaneous horizon first laws. |
| `O-ROTATION-CURVES` | `L2` | **PHYS** | cited | The extra term has been argued to fit rotation curves without dark matter. Mannheim–Kazanas. **Not assessed here.** |
| `O-RENORMALIZABILITY` | `L4` | **PHYS** | cited | Dimensionless coupling ⟹ power-counting renormalizable. Stelle; Fradkin–Tseytlin. **Not established here** — no Lorentzian construction exists in this repository. |

### 4.2 CHALLENGES

| row | level | column | status | claim |
|---|---|---|---|---|
| `C-GHOST-FORCED` | `L3` | MATH | **proved** | The ghost is forced by the same equation that makes the action unique. Einstein avoids it precisely by assuming `RP-2ND-ORDER`. |
| `C-NO-CHEAP-FIX` | `L0` | MATH | **proved** | No other conformal action exists, so the ghost cannot be tuned away. Dropping `RP-WEYL` keeps degree 2; `D = 6` is worse. |
| `C-NOT-A-SUBSYSTEM` | `L3` | MATH | **refuted** | Containment of solutions does not upgrade to containment of dynamics. Cauchy matrix ranks 0 and 2. `REDUCED-MODE`, `LORENTZIAN-CAUSAL`. |
| `C-CAUCHY-DATA` | `L3` | GEOM | cited | Fourth order needs twice the initial data — the same doubling Ostrogradsky converts into the ghost. Imported, not re-derived. |
| `C-NO-NEWTON-CONSTANT` | `L2` | **PHYS** | **open** | No scale in the action means the gravitational scale must be *generated*. Newtonian recovery is not established here. |
| `C-DOF-NOT-WELL-POSED` | `L3` | MATH | **proved** | *"How many degrees of freedom in this region"* is not well posed in a conformally invariant theory — all three branches close. |
| `C-GHOST-DYNAMICS` | `L3` | **PHYS** | **open** | Whether the ghost destabilises the physical sector is uncharacterized. `GHOST_MODEL_OBSTRUCTION` showed the coprime obstruction decides it in *neither* direction. |

`C-DOF-NOT-WELL-POSED` is worth singling out: it challenges the **question**,
not the answer. What survives is a *relative* count generated by a single
scaling exponent. Only a column-separated ledger can record the difference
between "Weyl gravity gets this number wrong" and "this number does not exist".

### 4.3 SHARED — not chargeable to either side

| row | level | status | claim |
|---|---|---|---|
| `S-DIFF-WITNESSED` | `L0` | **proved** | `RP-DIFF` is independent **given `RP-METRIC`**, in both theories. Supersedes `S-DIFF-INVISIBLE`, which called it the largest hole — that was true of the *carrier*, not the assumption. See [`diff-independence.md`](diff-independence.md). |
| `S-LOCAL-METRIC-UNTESTED` | `L0` | **open** | `RP-LOCAL` and `RP-METRIC` bound the coordinate space of both theories rather than being tested inside it. |
| `S-PARITY-CLASSICALLY-FREE` | `L1` | **proved** | At field-equation level the parity direction costs and distinguishes nothing — the chiral family collapses because `P` is topological. |

`S-LOCAL-METRIC-UNTESTED` is load-bearing rather than pedantic: `RP-LOCAL` and
`RP-METRIC` are exactly the two escapes left open by `C-NO-CHEAP-FIX`. **The
only surviving routes out of the ghost run through assumptions that neither
theory tests.** That sentence is only available once the SHARED bucket exists.

---

## 5. What keeps the citations trustworthy

The rule adopted for this stream is that *citations are sufficient if they are
trustworthy*. The rail is aimed at exactly what makes a citation stop being
trustworthy, and every check has a negative control that must be rejected —
13/13 are.

| | check | why |
|---|---|---|
| `C1` | fixed vocabulary for direction/level/column/status | an ad-hoc status is how a ledger stops being comparable |
| `C2` | **every in-repo source path exists** | a dangling citation is the primary failure, and it fails *silently* in prose |
| `C3` | MATHEMATICS requires `PROVED`/`DISCHARGED`/`REFUTED` **and** an in-repo source | you cannot cite your way into the right-hand column |
| `C4` | PHYSICS requires a non-empty `contingent_on` | test `T2`, made mechanical: name what would falsify it |
| `C5` | `CITED` requires `literature` and forbids MATHEMATICS | keeps imports visibly imported |
| `C6` | every row traces to a declared assumption | no free-floating opinions about gravity |
| `C7` | `flips_with` must be mutual, cross-level, opposite in direction | test `T5`, made mechanical |
| `C8` | `paid_for_by`/`buys` must resolve and point the other way | stops the ledger degenerating into pros-and-cons |
| `C9` | a SHARED row may not trace only to a differentiator | stops shared bills being charged to one side |

`C3` and `C4` are the two that carry the separation. `C3` says a claim cannot
reach the MATHEMATICS column by citation, however good the citation. `C4` says a
claim in the PHYSICS column must name the observation that could kill it. Between
them, a row that is really a physics claim cannot masquerade as a theorem, which
is the specific failure this document exists to prevent.

---

## 6. What this is not

- **No new physics.** Every row points at content that already exists, or is
  marked `OPEN`. The ledger is an organisational artifact.
- **No promotion.** Rows tagged `REDUCED-MODE` or `LOCAL-ALGEBRAIC` are not
  evidence for `LORENTZIAN-CAUSAL` claims and are not used as such.
- **Not complete.** The row set is open by construction and is not claimed to
  exhaust the comparison.
- **`OPEN` means open.** Three rows are unresolved, and the certificate reports
  the open count as a first-class number rather than burying it. In particular
  the dynamical consequence of the ghost is open, and nothing here settles it.

---

## 7. The one-line version

Weyl gravity and Einstein gravity differ by a single assumption swap that is
*forced* — no four-dimensional local metric action is both Weyl invariant and
second order. Everything Weyl gravity opens and everything it challenges is one
side or the other of that one trade, and the sharpest pair is a single theorem
read twice: the equation that lets you *derive* the derivative order instead of
assuming it is the same equation that *forces* the ghost. Which of those two you
are entitled to say depends on the column, and whether either is even true
depends on the level.

---

## Verification

```bash
PYTHONPATH=. python3 -m reverse_physics.weyl_vs_einstein_ledger --check
# rows 18 (OPENS 8, CHALLENGES 7, SHARED 3); negative controls rejected 13/13; PASS
```
