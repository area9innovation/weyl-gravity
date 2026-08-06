# Bach flatness is a property of the conformal class

**Certificate** `BH0G_CONFORMAL_CLASS_INVARIANCE`
**Verifier** `black_hole_programme/bh0g_gauge_reduction.py` - 6 checks, all PASS
**Dependency tag** `LOCAL-ALGEBRAIC`

> Discharges the load-bearing half of an assumption `BH0B` declared. Section 3 is a real error
> this caught in my own earlier work, and it propagated - so it is recorded before the result.

---

## 1. The assumption, split in two

`BH0B` proved completeness in the gauge `b = 1/B` and declared:

> *"that an arbitrary static spherically symmetric metric `diag(-a, b, r^2, ...)` can be brought
> to that gauge by a conformal transformation and a radial reparametrisation is the standard
> Mannheim-Kazanas argument and is **assumed** here, not proved."*

That has two halves, and they are not equally hard:

- **(A) Conformal covariance.** Bach flatness must be preserved by `g -> Omega^2 g`, or
  classifying one gauge says nothing about the others.
- **(B) Reachability.** That some `Omega` actually *attains* `b = 1/a`.

**(A) is the load-bearing half** - without it the classification could be an artefact of the
gauge. It is computed here. **(B) is an ODE existence statement** and remains assumed.

## 2. What is computed

```
B_ab[Omega^2 g]  =  Omega^(-2) B_ab[g]           (conformal weight -2, D = 4)
```

verified for the Mannheim-Kazanas family with `beta, gamma, k` **symbolic** and `Omega` an
**unspecified function** - so this quantifies over every conformal transformation of the whole
family at once, not a sampled one.

Consequently **Bach flatness is a property of the conformal class**, and `BH0B` classifies
classes rather than a gauge-dependent slice. The residual assumption shrinks from "the
classification might be gauge-dependent" to "every class has a representative of the assumed
form".

## 3. A real error this caught, and it had propagated

The first draft used `B = 1 - 2 beta/r + gamma r - k r^2` - the **weak-field** Mannheim-Kazanas
form - and **check 3 failed**. It was right to. That form has `w = 1` and `u = 2 beta`, so

```
w^2 + 3 u gamma  =  1 + 6 beta gamma
```

which is **off** the constraint surface `BH0B` derived. It is not Bach-flat unless
`beta gamma = 0`. The check was correct and the input was wrong.

**The same weak-field form had been used in `BH0C`.** The exact family gives

```
v^2/c^2 = beta/r - 3 beta^2 gamma/(2r) + gamma r/2 - k r^2
v^4/c^4 = beta gamma (2 - 3 beta gamma) = 2 beta gamma (1 - 3 beta gamma / 2)
```

So `BH0C`'s scaling law is the **leading term** of an exact expression. What survives: the law
`v^4 = 2 G M gamma c^2` and the conditional built on it, to leading order, with a correction of
order `10^-14` for a galaxy. What does **not** survive: the claim that the Tully-Fisher slope is
*exactly* 4. The correction is itself mass-dependent, so the slope is 4 only in the limit
`beta gamma -> 0`. `BH0C` is corrected accordingly.

## 4. How the checks are built

- **`Omega` is unspecified** - a symbolic function, so the covariance statement is universal.
- **Non-vacuity** - a metric *off* the Bach-flat locus is required to have nonzero Bach, or
  covariance would concern a tensor that vanishes anyway.
- **The control is a non-conformal rescaling.** Rescaling only the spatial block - which is not
  a conformal transformation - is required to **break** flatness. Without it, the result would
  be satisfied by a computation insensitive to the metric altogether.

## 5. What this does not establish

- **Reachability.** The remaining half, and an ODE existence question.
- **Anything about radial reparametrisation.** Only the conformal half is treated.
- **Novelty.** Conformal covariance of the Bach tensor in D = 4 is classical. What is
  contributed is that `BH0B`'s gauge choice is now justified *inside this repository* rather
  than by citation.
- **Anything about non-static or non-spherically-symmetric metrics.**

## 6. Next

Reachability: given arbitrary `a(r), b(r)`, exhibit `Omega` solving the gauge condition, or
characterise when none exists. That is an ODE question rather than an algebraic one, which is
why it is separated out rather than attempted here.

---

## Verification

```bash
cd black_hole_programme
python3 bh0g_gauge_reduction.py    # 6 checks, all PASS
```
