# The certified data does not determine the answer — an explicit `T₋` is unavoidable

**Gate** tango `forge/examples/weyl_c_factorisation_parametric_gate.forge` — 25/25 `forge -run`
**Known defect** the gate **fails `verify -full`**: a residual ~500-byte leak. Not claimed ASan-clean. See below.
**Uses** the two physical Grams, exactly, from `axial_null_flux_gram` and
`axial_horizon_grassmann_mobius_to_r4_taylor2`

---

## The question this settles

Not *"does `C` factorise?"* — that still needs `T₋`. The question **before** that one:

> With the actual `G` and `H_H`, is the answer already forced by what the corpus
> certifies, or is it genuinely free?

If forced, the ghost question closes with no transport at all. It isn't. And that
is now proved with the real matrices rather than abstract stand-ins.

## What was done

Both Grams are explicit. Typed into Forge in exact ℚ(i) and **checked against
their published leading principal minors**:

| | minor 1 | minor 2 | minor 3 |
|---|---|---|---|
| `G` at ω=1/2 | `1152/5` | `−18432/5` | `1769472/125` |
| `H_H` | `96ω(16ω⁴+41ω²+7)/(5(ω²+1))` | `−73728ω²(4ω²+1)(16ω²+1)/(25(ω²+1))` | `884736ω³(4ω²+1)(16ω²+1)²/(125(ω²+1))` |

All reproduce exactly, both give inertia `(1,2,0)`, and **both Einstein
directions are confirmed isotropic** — the `(3,3)` entry vanishes in each.
That is the guard against the experiment being about the wrong matrices.

Then, over the admissible set — `K_H` congruent to `H_H`, `K₊ = G − K_H` of
inertia `(1,2,0)`, determinant ratio in `(0,1]`:

**A NO witness set.** 528 admissible congruences `A†H_H A` at ω=1/2 (and 32 more
at ω=3/4). **Every one fails** the criterion.

**A YES witness.** `K_H = G/2`. By Sylvester it *is* a congruence of `H_H` (same
inertia), `K₊ = G/2` also has inertia `(1,2,0)`, its determinant ratio is `1/8`,
and its pencil spectrum is `{½,½,½} ⊂ (0,1)`. **The criterion holds.**

## The verdict

> **Both outcomes are reachable with the actual physical Grams.**
> The certified data does not determine whether `C` factorises. An explicit `T₋`
> is **logically unavoidable**, not merely convenient.

This is the same shape as the earlier abstract no-shortcut theorem, but now for
the real `G` and `H_H` rather than hand-built witnesses — which is what makes it
about this black hole rather than about signature `(1,2)` in general.

## A secondary finding

`G⁻¹H_H` does **not** have positive real spectrum. Since `K_H = t·H_H` gives
`L_H = t·(G⁻¹H_H)`, that kills the **entire scaling direction** at once: no
rescaling of the horizon Gram can ever satisfy the criterion. Only genuine
congruences have a chance.

## What this does *not* say

- **It does not say the answer is NO.** 528 sampled failures are a sample, not
  the orbit; and the `G/2` witness shows YES is reachable. The scan's value is
  as a *counterweight* to the YES witness, jointly establishing freedom.
- **It does not compute `T₋`.** That remains the blocker, and it remains the
  black-hole package's own stated `minimal_missing_object`.
- **Nothing `LORENTZIAN-CAUSAL`.** The imported certificates carry
  `REDUCED-MODE` and none is promoted.

## The known defect

The gate passes `forge -run` 25/25 and **fails `forge verify -full`** on a
LeakSanitizer report of roughly 500 bytes. An ownership pass removed ~2270 of the
original 2274 leaked objects — the culprits were temporaries passed to `borrow`
parameters and destructured tuples, neither of which auto-drop — but the last few
resisted localisation.

It is recorded rather than hidden, and **no certificate claims this gate is
ASan-clean**. The arithmetic is unaffected: every value is exact rational and the
result is deterministic. Cleaning it is outstanding work, and until it is done
this gate sits below the standard the other four meet.

## Verification

```bash
cd forge && FORGE_LIB=$PWD/lib forge -run \
    examples/weyl_c_factorisation_parametric_gate.forge     # 25/25

# and see the defect for yourself:
cd forge && FORGE_LIB=$PWD/lib forge verify -full \
    examples/weyl_c_factorisation_parametric_gate.forge     # FAILS: leak
```
