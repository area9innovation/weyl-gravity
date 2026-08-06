# What conformal invariance demands of matter, and why a galaxy is not it

**Certificate** `BH0E_MATTER_TRACE_DILEMMA`
**Rail** Forge, `tango/forge/examples/weyl_matter_trace_gate.forge` - 8/8
**Dependency tag** `LOCAL-ALGEBRAIC`
**Builds on** `BH0B`, `BH0C`, `BH0D`, and the Noether identity in `REVERSE_PHYSICS_SYMBOLIC_FAMILY_V1`

> This closes the crux the previous three left open. It does not close it with a yes or a no,
> and section 5 is why that is the honest outcome rather than a dodge.

---

## 1. One theorem, used twice

The Noether work established that a conformally invariant action satisfies

```
g_ab (delta S / delta g_ab) = 0
```

which is what the Euler gate computes for `sqrt(-g) C^2`. Applied to the **matter** action
rather than the gravitational one, the identical statement reads

```
T^mu_mu = 0
```

That is imported here, not re-derived. What this gate computes is what it **costs**.

## 2. The cost

For a perfect fluid the trace is `3p - rho`. So tracelessness holds **if and only if**

```
p = rho/3        -- radiation, uniquely
```

and **dust** (`p = 0`) forces `rho = 0`. Pressureless matter is excluded outright.

A galaxy's baryons are pressureless to excellent approximation. So on the conformal branch,
**a galaxy is not an admissible source at all.**

## 3. The dilemma

`BH0D` established that `gamma` is the point-source response of the biharmonic operator, so its
coefficient tracks the total fourth-order source. `BH0C` established that Tully-Fisher forces
`gamma` to be **universal**. Together with section 2, the fork resolves into a dilemma - and
both branches are costed:

**Either** the matter sourcing `gamma` is not ordinary baryonic matter - in which case `gamma`
is not sourced by the baryonic mass that Tully-Fisher correlates against.

**Or** the conformal symmetry is **broken** in the matter sector. This is the standard move: a
conformally coupled scalar acquiring a vacuum expectation value. But breaking it introduces
exactly the mass scale that conformal invariance was invoked to forbid - so the universality of
`gamma` stops being a *consequence* and becomes an *assumption*.

**Neither branch is fatal and neither is free.** Naming which one a rotation-curve fit is
standing on is the contribution.

## 4. The reverse-physics form of a twenty-year dispute

Flanagan (2006) argues conformal gravity's Newtonian limit does not come out right when matter
is coupled conformally. Mannheim disputes it. The disagreement has stood for about two decades.

**This does not adjudicate it.** What it does is *locate* it: both sides are choosing branches
of the dilemma above, and on either side the choice is an assumption rather than a derivation.
That is what a reverse-physics treatment is for - the assumption-isolation, not the verdict.

## 5. How the checks are built

- **Mixed components keep it ansatz-independent.** `T^mu_nu` is used rather than `T^{mu nu}`,
  so the trace is a plain diagonal sum and no metric enters. This result does not inherit the
  static spherical ansatz everything else in the line assumes.
- **Non-vacuity.** The trace is required *not* identically zero - otherwise "traceless"
  constrains nothing and every fluid qualifies.
- **The dilemma is kept two-sided.** Radiation is required to *still source* the fourth-order
  equation (`T^0_0 - T^r_r = -rho - p`, nonzero). Without that control the finding would
  collapse to "nothing can source gamma" rather than the sharper and true "ordinary matter
  cannot".
- **The equation of state is forced, not chosen.** `3p - rho = 0` is exhibited as having
  exactly the solution `rho = 3p` by computing the residual, not by quoting the standard result.

## 6. What this does not establish

- **That conformal invariance implies `T^mu_mu = 0`.** Imported from the Noether result. What
  is new is the cost of it.
- **That a galaxy is pressureless baryons.** An observational input, not this repository's. It
  is what makes the dilemma bite, and a reader who rejects it rejects the conclusion.
- **That conformal gravity is wrong, or that MOND is wrong.** Neither branch is fatal. The
  symmetry-breaking branch is the standard construction and is not refuted here - what is
  established is that it carries a cost the vacuum-side results do not advertise.
- **Anything about a conformally coupled scalar specifically.** Only the perfect-fluid case is
  computed.
- **Any rotation-curve fit, galaxy, or numerical comparison.**
- **The resolution of the Flanagan-Mannheim dispute.** This locates it.

## 7. Next

Cost the second branch explicitly. If the symmetry is broken by a scalar acquiring a vacuum
expectation value, the scale it introduces is what sets `gamma` - so *"is gamma universal?"*
becomes *"is that vacuum expectation value universal?"*, which is a question about the scalar
sector rather than about gravity.

Making that translation precise would turn `BH0C`'s conditional into a statement about the
symmetry-breaking sector, and would say exactly what a rotation-curve fit is assuming about it.

---

## Verification

```bash
cd tango/forge && export FORGE_LIB=$PWD/lib
forge -run examples/weyl_matter_trace_gate.forge    # 8/8
```
