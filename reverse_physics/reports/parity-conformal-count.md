# The parity half, answered — and yes, `D = 6` has an analogue

**Certificate** `REVERSE_PHYSICS_PARITY_CONFORMAL_COUNT_V1`
**Rail** Forge, `tango/forge/examples/curvature_invariants_parity_gate.forge` — 20/20
**Answers** the second half of `WEYL_ACTION_SIX_DERIVATIVE_D6`
**Dependency tag** `LOCAL-ALGEBRAIC`

> **Lower bounds over the candidate families evaluated**, as with the parity-even
> counts. §5.

---

## 1. The half that stayed open

`REVERSE_PHYSICS_WEYL_ACTION_D6_V1` declared two questions: whether the `D = 4`
classification method scales to `D = 6`, and **whether the parity result has a
`D = 6` analogue**. The first has been answered three times over. The second was
recorded as *not answered* and stayed that way through every subsequent
certificate — for the plain reason that **no `ε`-carrying candidate had ever been
evaluated, in any dimension**.

## 2. What comes out

| | | parity-odd invariants |
|---|---|---|
| `D = 4`, weight 4 | the Pontryagin density | **1** |
| `D = 4`, weight 6 | | **2** |
| `D = 6`, weight 6 | | **2** |
| odd `D`, weight 6 | | **none exist** |

**The answer to the gate is yes.** There are parity-odd pointwise conformal
invariants of weight 6 in `D = 6`, and both are **exhibited**, not merely counted:
they are the complete contractions of one `ε` with three **Weyl** tensors.

The odd-dimension row is settled by **counting, not computing**: one `ε` carries
`D` indices and every weight-6 curvature shape carries an even number, so `D +
even` cannot close when `D` is odd. There is nothing for a rank to evaluate.

### The shape of the result

> In both dimensions the parity-odd invariant content is **exactly what the Weyl
> tensor supplies.**

The Riemann-built parity-odd candidates are mostly **identically zero**, and the
two that aren't are **not invariant** on their own. That is the substance — not the
count by itself.

## 3. Keeping a Levi-Civita tensor inside exact arithmetic

`ε_{a₁…a_D} = √|det g| · [a₁…a_D]`, and that square root is not rational. Taken
literally it puts the whole parity-odd sector outside exact rational arithmetic.

It doesn't have to. **Evaluate at a base point where `|det g| = 1`, and the tensor
*is* the symbol there, exactly.** That costs nothing: the fixtures are `G = L S Lᵀ`
with `L` unit lower-triangular over the integers, so `det G = ±1` by construction,
and a conformal partner `e^{2σ}g` with `σ` vanishing at the base point has the same
determinant there.

**It is checked, not assumed** — a mutation making the base metric non-unimodular
scores 18/20, failing exactly that check in both dimensions.

The other thing that makes this work: `ε` is **covariantly constant**, so it passes
straight through a covariant derivative and the derivative candidates need no extra
machinery.

## 4. Controls

- **The known-answer control.** In `D = 4` at weight 4 the Pontryagin density is
  nonzero on every fixture and its conformal variation vanishes on every sample.
  That reproduces by computation what `weyl_action_classification_gate` **asserts**
  when it writes `W±² = (C² ± P)/2` and calls both Weyl invariant.
- **The positive control.** A complete contraction of one `ε` with three Weyl
  tensors carries weight `−6` uniformly, so it *must* be conformally invariant. The
  gate checks both that those candidates are **nonzero** and that their variation
  **vanishes** — if either failed, the `ε` bookkeeping would be wrong.
- **A control that must vanish.** `ε` contracted with symmetric Ricci factors is
  identically zero, and comes back exactly zero.
- **Non-vacuity**, per-metric non-degeneracy, rank saturation, two rank rails, both
  signatures.

### A run that failed its own saturation check

An earlier run at six metrics reported **one fewer invariant in `D = 4`** than the
truth. Its saturation check failed — both ranks were still climbing when the
metrics ran out. Recorded because **the wrong number was not obviously wrong**;
only the saturation check distinguished it.

### The mutation battery

| mutation | score (baseline 20) |
|---|---|
| the Levi-Civita signs all set to `+1` | 13 |
| a wrong raised variant fed to a Weyl candidate | 18 |
| a non-unimodular base metric, breaking `|det g| = 1` | 18 |

## 5. What this does **not** establish

- **Not exactness.** These are **lower bounds** over the candidate families
  evaluated, exactly as the parity-even counts are. A family not written down
  cannot be found by a rank.
- **Nothing about two-`ε` candidates.** Those are parity-*even* and reduce into the
  sector already counted; none is evaluated.
- **Nothing about the trace anomaly.** No quotient by total derivatives is
  performed, so this says nothing about Lagrangians, actions, or anomaly
  coefficients — in particular **nothing about whether a parity-odd term appears in
  the `D = 6` trace anomaly.**
- **Not the `D = 6` analogue of the action-versus-field-equation result.** What is
  established is that parity-odd conformal invariants **exist** at weight 6 in
  `D = 6` and how many. Whether adjoining them leaves the *field equations*
  unchanged — as the parity-odd sector does in `D = 4`, which is the actual content
  of *"parity is independent on actions and redundant on field equations"* — is a
  **different computation and is not done.**
- **Nothing about `D > 6`,** other weights, dynamics, the ghost, or anything
  quantum.

## 6. Substrate

`math/levicivita` — parity-odd curvature scalars carrying one Levi-Civita tensor.
Permutations and signs by **Lehmer decoding** (the digit sum *is* the inversion
count, so the sign comes free), and two contraction drivers taking a **slot spec**
per operand: which slots feed the `ε`, and how the remainder pairs up. Summing over
permutations rather than over all index tuples is what makes it cheap — in `D = 6`
that is 720 terms rather than 46656.

---

## Verification

```bash
cd tango/forge && export FORGE_LIB=$PWD/lib
forge verify examples/curvature_invariants_parity_gate.forge   # 20/20, ~5 min
```

Exact rational arithmetic throughout. No floating point, no tolerance.
