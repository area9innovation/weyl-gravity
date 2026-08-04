# Lovelock in `D = 4`, computed — the swap is now symmetric

**Certificate** `REVERSE_PHYSICS_EINSTEIN_CLASSIFICATION_V1`
**Rail** `reverse_physics/einstein_classification.py` — 11/11 checks
**Closes** the citation in the comparison ledger's swap block
**Dependency tag** `LOCAL-ALGEBRAIC`

---

## 1. The hole this closes

The comparison ledger's organising claim is that Einstein and Weyl gravity sit
over the same base and differ by **one forced swap**:

```text
Einstein   + RP-2ND-ORDER               →  Lovelock   →  G_ab + Λ g_ab
Weyl       + RP-WEYL (+ RP-TOPO-INERT)  →  D − 2k = 0 →  B_ab
```

Both sides are uniqueness theorems. The Weyl side is **proved** in this stream.
The Einstein side was **cited** — Lovelock 1971/72, filed `GEOMETRY` in the
swap block. So the ledger's central claim rested on one computed theorem and one
import, which is exactly the asymmetry the three-column discipline exists to
make visible. It bothered me on reflection, and this closes it.

## 2. What is assumed — less than a field-equation formula

**No closed form for any quadratic field-equation tensor is imported here.**
Three inputs, and only the third is under test:

1. **The forced head.** In `δ(√−g Riem²)/δg^mn` two terms are not a choice:
   `−½g_mn Riem²` from `δ√−g`, and `2R_mabc R_n^abc` from lowering indices.
   Everything else is unknown.
2. **Divergence-freedom.** The metric variation of a local diff-invariant action
   is divergence-free — `N1`, already discharged against this repository's
   curvature engine. Not a new import.
3. **`RP-2ND-ORDER`** — the assumption under test.

## 3. The derivation

Write the unknown remainder over the eight remaining tensor structures and
impose divergence-freedom **identically in the coordinates** — every monomial
coefficient is a separate equation, not a single condition at a point. That
gives 11 equations, and leaves a **two-parameter family**.

That residue is not a defect. It is exactly what it should be: adding any
multiple of the `Ric²` or `R²` field-equation tensors preserves both the forced
head *and* divergence-freedom, so the family is their span. The two free
parameters are the coefficients of `∇_m∇_n R` and `g_mn □R`.

Now impose `RP-2ND-ORDER`. The three derivative structures are `□R_mn`,
`∇_m∇_n R`, `g_mn □R`, and the solution ties them:

```text
coefficient of □R_mn  =  −2 (x_∇∇R + x_g□R)
```

so demanding all three vanish forces the other two to zero and leaves **one**
tensor:

```text
2R_mabc R_n^abc − ½g_mn Riem² − 4R_manb R^ab − 4R_ma R^a_n
    + 2R R_mn + 2g_mn Ric² − ½g_mn R²
```

which is the **Lanczos tensor** — derived, not looked up. The reference
coefficients appear in the module only so the check can *compare* against them;
they are never substituted into the computation.

## 4. And in `D = 4` it vanishes

| metric | Lanczos tensor identically zero |
|---|---|
| `schwarzschild` | ✅ |
| `non_einstein_static` | ✅ |
| `taub_nut` (twisted, non-diagonal) | ✅ |

**So at curvature degree exactly two in `D = 4`, the second-order subspace is
one-dimensional and its field equations are identically zero.** A degree-two
term contributes nothing to any second-order theory, and `RP-2ND-ORDER`
collapses degree ≤ 2 to degree ≤ 1.

There the variation is computed directly:

```text
√−g     →  −½ g_mn      the cosmological term
√−g R   →   G_mn        the Einstein tensor
```

both divergence-free — the second being the contracted Bianchi identity
**discharged rather than quoted**.

Hence in `D = 4` the field equations of any degree-≤2 local metric Lagrangian
with second-order field equations are

```text
a G_mn + b g_mn
```

Lovelock's conclusion, in the same carrier and the same exact rational
arithmetic as the Weyl side. **The swap now rests on two computed uniqueness
theorems.**

### A check that looked like a failure

Schwarzschild returns `G_mn = 0`. My first version flagged that as a failed
check — wrongly. Schwarzschild is Ricci-flat, so `G_mn = 0` there is exactly the
statement that **it solves the vacuum Einstein equations**. It is now a
correctness check that passes for the right reason, and `einstein_tensor_is_
nonzero` is recorded as *visibility* rather than pass/fail — the same vacuity
trap the geometry discharges already carry flags for. A metric with `G_mn = 0`
cannot witness that the variation is non-trivial, so a second metric does.

## 5. A second thing this buys

[`weyl-trace-law.md`](weyl-trace-law.md) used the Lanczos identity
`E^(Riem²) = 4E^(Ric²) − E^(R²)` as a **cited** input, flagged there as the same
content as `G4`/`N3`. That identity is exactly *"the Lanczos tensor vanishes in
`D = 4`"*, which is discharged here. **The citation is upgraded.**

## 6. What this does not establish

- **Curvature degree ≤ 2 and `D = 4` only.** Full Lovelock is a statement at
  every degree and in every dimension. The higher Euler densities — which matter
  in `D > 4` and vanish identically in `D = 4` — are not treated.
- **Not the `D > 4` Gauss–Bonnet dynamics.** The decisive fact used here is the
  *identical vanishing* in `D = 4`; in higher dimensions the tensor does not
  vanish and the argument changes character.
- **Not uniqueness among nonlocal or non-polynomial Lagrangians.** The carrier
  is polynomial in curvature; `RP-LOCAL` is a separate assumption with its own
  witness ([report](carrier-enlargements.md)).
- **Nothing about which `a` and `b` are physically realised.** The values are not
  fixed by anything here.

---

## Verification

```bash
PYTHONPATH=. python3 -m reverse_physics.einstein_classification --check
# 11 equations; 2-parameter family; +RP-2ND-ORDER → 1 solution = Lanczos;
# vanishes identically on 3 metrics; 11/11; PASS
```

Needs the mise Python (sympy). Takes a few minutes, so the fast rail is
`reverse_physics/tests/test_einstein_classification.py`.
