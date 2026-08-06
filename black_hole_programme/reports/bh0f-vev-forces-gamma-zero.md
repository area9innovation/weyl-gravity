# A constant scalar VEV forces gamma = 0

**Certificate** `BH0F_CONSTANT_VEV_FORCES_GAMMA_ZERO`
**Verifier** `black_hole_programme/bh0f_vev_forces_gamma_zero.py` - 12 checks, all PASS
**Dependency tag** `LOCAL-ALGEBRAIC`
**Builds on** `BH0B` (the forced family) and `BH0E` (the dilemma)

> Costs the second branch of the `BH0E` dilemma. It does not eliminate it - section 4 is the
> part that matters, and it is a relocation of the question rather than a refutation.

---

## 1. Three steps

**Step 1 - the scalar pins the curvature.** For the conformally coupled scalar in D = 4 the
field equation is `box S + (1/6) R S + 4 lambda S^3 = 0`. For a **constant** vacuum expectation
value `S0 != 0` the derivative term drops and this becomes algebraic:

```
R = -24 lambda S0^2        (and R = 0 when lambda = 0)
```

A constant VEV does not merely supply a scale. It **pins the Ricci scalar to a constant.**

**Step 2 - the curvature of the forced family**, computed from the metric rather than quoted:

```
R = 12k - 6 gamma / r + 2(1 - w) / r^2
```

**Step 3 - constancy.** That is constant in `r` **if and only if** `gamma = 0` and `w = 1`.

## 2. The conclusion

```
constant scalar VEV   ==>   R constant   ==>   gamma = 0
```

The linear potential - the entire reason conformal gravity is of interest for rotation curves -
is **incompatible** with the simplest form of the symmetry breaking that was supposed to rescue
the matter coupling. The two features cannot both be had from a constant VEV.

## 3. Why the check is built the way it is

- **`R` is computed, not asserted** - taken from the metric through the curvature engine, with
  the target expression verified against it afterwards.
- **All `r`, not some `r`.** `dR/dr = 0` is solved as a *polynomial* after clearing
  denominators, so the conclusion is "constant for all `r`" rather than "constant wherever
  sympy happened to simplify".
- **The implication is not vacuous.** `R` is required *not* automatically constant, and with
  `gamma != 0` it is required *not* constant. Without those, "R constant implies gamma = 0"
  would be a statement about an `R` that was constant anyway.
- **`u` drops out.** `R` is verified independent of the Newtonian coefficient. So the
  obstruction is specific to the *linear* term and does not touch the Newtonian one - which is
  what makes this a statement about `gamma` rather than about the solution generally.
- **Consistency with `BH0`.** At `gamma = 0, w = 1` the constant value is `12k`, the (A)dS
  curvature, matching `BH0`'s Einstein locus by an independent route.

## 4. What this does and does not refute

**It does not refute the programme.** A working construction can take the scalar
**non-constant**, and Mannheim's does.

What is established is that it **must** - constancy is not available - and that this **moves
the universality question**. With a position-dependent scalar the profile is a property of each
configuration. `BH0C` requires `gamma` to be the *same constant for every galaxy*, and `gamma`
is now tied to the scalar profile. So the requirement transfers:

> *"Is gamma universal?"* becomes *"is the scalar profile universal across galaxies?"*

That is a question about the **symmetry-breaking sector**, not about gravity, and there is no
obvious reason for it to answer yes.

## 5. What this does not establish

- **Anything about a non-constant scalar.** The whole content concerns a constant VEV. That is
  precisely where a working construction lives.
- **The form of the scalar action.** The conformally coupled scalar in D = 4 is entered as a
  premise, not derived. A different matter sector gives a different condition.
- **That Mannheim's construction is wrong.** It uses a non-constant scalar - the case not
  covered here. What is shown is that the non-constancy is **load-bearing rather than
  incidental**.
- **Any statement about rotation curves, galaxies, or observation.**
- **The resolution of `BH0E`.** Branch two is *costed*, not eliminated.

## 6. Next

The non-constant scalar, now the only place branch two can live. The question to pose is not
whether a profile exists - one does - but what **universality** it must have. Making that
transfer precise would say exactly what a rotation-curve fit assumes about the
symmetry-breaking sector, which is the sharpest remaining question on this line.

---

## Verification

```bash
cd black_hole_programme
python3 bh0f_vev_forces_gamma_zero.py    # 12 checks, all PASS
```
