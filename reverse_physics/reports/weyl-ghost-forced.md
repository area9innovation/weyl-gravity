# The uniqueness theorem and the ghost theorem are the same theorem

**Certificate** `REVERSE_PHYSICS_WEYL_GHOST_FORCED_V1`
**Proof** `rocq/WeylGhostForced.v` — zero axioms, 14/14 closed
**Gate** `rocq/run.sh` — `RESULT: 26 green (0 red)`, 26 fail-closed negative controls
**Second rail** tango `forge/examples/weyl_ghost_forced_gate.forge` — 26/26,
`verify -full`: `c==native`, ASan-clean on both backends
**Builds on** [`weyl-action-reverse-physics.md`](weyl-action-reverse-physics.md)

---

## Why this exists

The Weyl-action classification is textbook. Reported honestly, it told nobody
anything they did not already know — its value was the *ledger*, which is a
methodological artifact, not a fact about gravity. The obvious question is
whether the ledger points at anything.

It does, and it is this:

> **The same five assumptions that make the Weyl action unique also force the
> Ostrogradsky ghost.** Both follow from one equation, `D − 2k = 0`.

That is not a fact about a particular Lagrangian. It is a fact about the
*assumption set*, which is what reverse physics is supposed to produce.

## The consequence, which is the point

Because the action is **unique**, the ghost cannot be tuned away by choosing a
better conformal action. There is no other conformal action. Every proposal of
the form *"take conformal gravity but modify the curvature terms"* is dead on
arrival, and it is dead for the same reason the theory is canonical in the first
place.

Any escape must drop one of the five assumptions. Two of them provably do not
help.

| drop | does it remove the ghost? | why |
|---|---|---|
| `RP-WEYL` | **No** | quadratic gravity keeps curvature degree 2, hence fourth order, hence the pole count. Stelle 1977 — renormalisable *and* ghost-ridden. |
| `RP-DIM4` | **No, worse** | `D = 6` forces degree 3, sixth order, three poles. |
| `RP-LOCAL` | *plausibly yes* | infinite-derivative gravity with an entire form factor adds no poles. **A citation, not a theorem here.** |
| `RP-METRIC` | *plausibly yes* | a compensator scalar allows a second-order conformal theory. **Also a citation.** |
| `RP-DIFF` | not analysed | it is what makes the coordinate space the right space; no witness in this framework. |

The negative half is the useful half. It is routine to hope some variant of
conformal gravity is ghost-free; the arithmetic says the two most natural
variations — weaken the symmetry, change the dimension — provably fail. What is
left is locality and field content, and both take you outside the theory this
repository is about.

## The mechanism, and it is exact rational arithmetic

A curvature-degree-`k` action has a kinetic operator of order `2k` — a degree-`k`
polynomial in `k²` — hence `k` poles in the propagator. The partial-fraction
residue at a simple root is

```
R_i  =  1 / ∏_{j≠i} (r_i − r_j)
```

and for sorted roots the sign of that product is `(−1)^{n−1−i}`: **the residues
alternate.** So the moment there are two poles, one has a negative residue —
which is a negative-norm state.

There is no choice of pole locations that avoids it. Written division-free, with
two simple poles at `a < b`:

```
A(b − a) = 1   and   B(a − b) = 1        force        A > 0 > B
```

And the conformal weight law pins the pole count. `D − 2k = 0` means `k = D/2`,
so **the number of poles is exactly half the dimension**:

| `D` | curvature degree | derivative order | poles | ghost? |
|---|---|---|---|---|
| 2 | 1 | 2 | 1 | no — but `√−g R` is the Euler density, topological |
| **4** | **2** | **4** | **2** | **yes** |
| 6 | 3 | 6 | 3 | yes |
| 8 | 4 | 8 | 4 | yes |

> **Conformal gravity has a ghost in every dimension in which it is non-trivial,
> and the only ghost-free member of the family is empty.**

The threshold is sharp and proved in both directions: two or more poles for every
even `D ≥ 4`, exactly one at `D = 2` and nowhere else.

## Where the two results become one

`WeylActionClassification.v` used `D − 2k = 0` to prove *the derivative order is
not an assumption*. `WeylGhostForced.v` uses the same equation to prove *the pole
count is D/2*. One equation, two conclusions — the uniqueness of the action and
the presence of the ghost — and that is the whole content of the title.

The composition is a real one, not packaging: `D ≥ 4` plus the weight law give
the pole count, the pole count discharges the `O2` bridge, and the bridge feeds
the residue lemma. And the dimension hypothesis is doing work —
`at_dimension_two_the_bridge_is_vacuous` proves the theorem does not secretly
apply to everything.

## Two rails, and the second one earned its keep

| | method |
|---|---|
| **Rocq** | division-free sign lemmas over ℚ; never computes a residue |
| **Forge** | *evaluates* residues as exact rationals for 1–6 poles, and checks the partial-fraction identity by clearing denominators at five rational points |

The first version of the Forge residue used `∏(r_j − r_i)` instead of
`∏(r_i − r_j)` — off by `(−1)^{n−1}`. **The sign-alternation checks still
passed.** The partial-fraction identity check failed and located it.

That is the difference between checking the answer and checking the object, and
it is why the identity clause is in the gate at all.

## What this does **not** establish

- **Any linearised analysis of Weyl gravity.** No gauge fixing, no propagator
  computed, no degree-of-freedom count derived. What is proved is about pole
  counts and residue signs; everything connecting it to "Weyl gravity has a
  ghost" is the standard readings `O1`–`O3`, asserted.
- **The degenerate case — which is the one that actually occurs.** Weyl gravity's
  kinetic operator is `□²`: a **double** pole at `k² = 0`, not two distinct
  simple poles. That this is a dipole ghost and therefore no better is `O3`,
  cited to Riegert 1984 (and the `6 = 2 + 4` count), *not proved here*. The
  theorems cover the generic split of which it is the limit. **This was the
  load-bearing citation; it is now discharged by `rocq/WeylGhostDipole.v` — see
  the note above.**
- **That dropping `RP-LOCAL` or `RP-METRIC` actually works.** Citations, recorded
  as such.
- **Novelty of the ingredients.** Ostrogradsky, Stelle, and the uniqueness
  theorem are all classical. The composition, the sharp dimension threshold, and
  the arithmetic half of the escape lattice are what is added.
- **Anything quantum**, or about the BV–BFV complex, the residual classes, or the
  physical spectrum. This is the linearised classical propagator. The two scoped
  Lorentzian no-go theorems are neither used nor affected.

## The next gate — now CLOSED

> **Closed by [`ghost-and-the-black-hole.md`](ghost-and-the-black-hole.md) and
> `rocq/WeylGhostDipole.v`.** And the interesting part is where the statement
> came from: the black-hole programme had already computed it, on Schwarzschild,
> in the odd-parity spin-two sector. The commutant is `a·I + b·N` with `N²=0`,
> the flux metric has `det = −g²a²`, and it is indefinite or degenerate — never
> positive. The abstract lattice and the concrete scattering analysis had
> converged on the same object without either knowing it.

`WEYL_GHOST_DEGENERATE_LIMIT` — prove the dipole case instead of citing it. The
object is `1/k⁴`, a double pole, and the statement is that the Jordan block
admits no positive-definite inner product. That is exact linear algebra on a 2×2
nilpotent block over ℚ, squarely in range, and it would move `O3` from the
asserted column to the proved one. `O3` is currently the load-bearing citation
for **the case that actually occurs**, so this is the most valuable single thing
left in this line.

## Verification

```bash
cd rocq && ./run.sh                                   # 26 green (0 red)
PYTHONPATH=. python3 -m reverse_physics.weyl_ghost_forced --check

# upstream, in tango:
cd forge && FORGE_LIB=$PWD/lib forge -run \
    examples/weyl_ghost_forced_gate.forge             # exit 26
cd forge && FORGE_LIB=$PWD/lib forge verify -full \
    examples/weyl_ghost_forced_gate.forge             # c==native, asan clean
```

## Tier receipt

- **Tier 0/1** — twenty-one Rocq modules compile; gate 26 green / 0 red; `coqchk`
  axiom section `<none>`; 198/198 `Print Assumptions` closed; twenty-six
  fail-closed negative controls; eighteen provenance records hash-verified;
  30-test Python suite green.
- **Upstream** — `weyl_ghost_forced_gate.forge` 26/26, `verify -full`
  `c==native`, ASan-clean on both backends.
- **Tier 2/3 — not run, and not required.** This adds one module, one gate and
  one provenance record; it changes no shared operator, schema, or generated
  artifact that another certificate chain consumes.
