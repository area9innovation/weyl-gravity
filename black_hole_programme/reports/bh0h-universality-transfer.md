# gamma is not a conformal invariant, and what that costs the scalar

**Certificate** `BH0H_UNIVERSALITY_TRANSFER`
**Verifier** `black_hole_programme/bh0h_universality_transfer.py` - 18 checks, all PASS
**Dependency tag** `LOCAL-ALGEBRAIC`
**Builds on** `BH0B` (the forced family), `BH0C` (universality), `BH0E` (the dilemma),
`BH0F` (the constant-vev branch), `BH0G` (conformal weight -2)

> `BH0F` asked for the universality requirement to be transferred from `gamma` to the scalar
> profile. It transfers, and the answer is an equation. It also relocates the
> Flanagan-Mannheim dispute onto a single premise, without settling it.

---

## 1. Two results already here force a third

`BH0G` computed that the Bach tensor has conformal weight `-2`, so **Bach flatness is a
property of a conformal class, not of a metric.** `BH0B` computed that in the gauge `b = 1/B`
the general Bach-vacuum solution is

```
B = w - u/r + gamma r - k r^2        subject to    w^2 + 3 u gamma = 1
```

Put those together and something follows immediately: the conformal group must **act** on that
four-parameter family. Nobody had computed the action.

## 2. The action, and it has one parameter

Under `g -> Omega^-2 ghat` the angular part fixes `Omega = hat_r / r`. Demanding the image stay
in the gauge `b = 1/B` is then not a choice but an ODE,

```
d hat_r / dr = (hat_r / r)^2
```

whose general solution is a Moebius map, `hat_r = r / (1 - C r)` - one constant, no further
freedom. Solving it rather than guessing a map is what makes the one-parameter family complete.
The induced action on the parameters is

```
u      ->  u
w      ->  w + 3 u C
gamma  ->  gamma - 2 w C - 3 u C^2
k      ->  k + C gamma - C^2 w - C^3 u
```

It is a genuine one-parameter group - `C` then `C2` composes to `C + C2`, computed on every
parameter - and it preserves `w^2 + 3 u gamma` as a polynomial identity, so it stays inside
`BH0B`'s solution set rather than landing on it by luck.

**And `gamma` moves.** From a member with `gamma = 0` (where the constraint forces `w = 1`),

```
gamma  =  -2C - 3 u C^2
```

nonzero for every nonzero `C`. So `gamma` is not an invariant of the Bach vacuum. It is a
coordinate on the conformal class.

## 3. The scalar is the conformal factor

A conformally coupled scalar has weight `-1`, so the frame in which it is **constant** is
reached by exactly this map with `Omega = S / S_0`. That is the frame `BH0F` analysed, and
there `gamma = 0`.

So for a non-constant scalar the linear potential in the physical frame is generated entirely
by the profile, and the profile that does it is explicit:

```
S(r) = S_0 / (1 - C r)        C = (S'/S) at the origin
```

which gives the transfer `BH0F` asked for, in closed form:

```
gamma  =  -2 (S'/S)  -  3 u (S'/S)^2        and to leading order   gamma = -2 (S'/S)
```

`gamma` is fixed by the scalar's **fractional radial gradient** and by nothing else about the
profile; the second term is a mass correction through `u`.

## 4. What universality now means

`BH0C` requires `gamma` to be the same constant for every galaxy - that is what makes the
baryonic Tully-Fisher relation come out, and what identifies `gamma` with `a0 / 2c^2`. Section
3 turns that into

> **`S'/S` is the same constant for every galaxy.**

That is a much more specific demand than it looks. The scalar is what breaks the conformal
symmetry, and it is sourced by the configuration; the requirement is that its fractional
gradient be identical across galaxies whose masses differ by orders of magnitude. Nothing here
says it cannot be met. What is now available is the equation it has to meet, which is what
`BH0F` meant by "making that transfer precise".

## 5. Where the two-decade dispute actually lives

`BH0E` recorded that Flanagan (2006) argues conformal gravity's Newtonian limit fails when
matter is coupled conformally, that Mannheim disputes it, and that `BH0E` locates rather than
adjudicates.

This sharpens the location to a single premise. The two frames are **conformally related** and
only one of them carries a linear potential. So the disagreement is not about the vacuum
solution, which both sides agree on, and not about the algebra, which is section 2. It is
entirely about **which frame matter follows** - equivalently, how a particle's mass scale
tracks `S`. That is a premise about the coupling.

Both frames are exhibited here and neither is preferred.

## 6. What this does not establish

- That `S(r) = S_0/(1 - C r)` **solves** the coupled scalar-plus-Bach system with matter
  present. It is the profile that realises the conformal map, from the weight `-1`
  transformation law, and the map is exact. The dynamical problem is not solved here, and that
  is the remaining half of "forced versus sourced".
- The scalar's conformal weight. Weight `-1` in `D = 4` is standard and is a premise, exactly
  as `BH0F` enters the field equation as one.
- Which frame matter follows. Deliberately open.
- That `S'/S` cannot be universal. The transfer says what universality **requires**, not that
  the requirement fails.
- Anything about rotation curves, galaxies, MOND, `a0`, or any number.
- Anything outside the gauge `b = 1/B`, whose reachability `BH0G` reduced to an ODE rather than
  proved in general.

## 7. Controls

Four, and one of them failed first.

- **The identity element is pinned.** `C = 0` must give `gamma = 0` and a constant scalar,
  reproducing `BH0F` exactly. A transfer that did not degenerate to the known answer would not
  be looking at the same problem.
- **Non-vacuity.** Some `C` must give `gamma != 0`, or "gamma is not invariant" would be
  consistent with the group acting trivially.
- **An independent rail on the image.** The Bach tensor of a numeric image member is computed
  through the curvature engine and vanishes identically - a different code path from the
  `(r B)'''' = 0` test used for the general statement - and that member is required to have
  `gamma != 0` so the rail is not run on a trivial case.
- **The group law.** `C` then `C2` must equal `C + C2` on every parameter. This **failed on the
  first run**, and for a substitution-order reason rather than a mathematical one: a sequential
  dictionary substitution rewrites `w` inside the image of `gamma` a second time. Recorded
  because a composition law that fails for a tooling reason looks exactly like one that fails.

## 8. Next

Two directions, independent of each other, neither attempted here.

**(a) The dynamical half.** Solve the conformally coupled scalar's own field equation on the
image metric with an ordinary-matter source, and ask whether `S(r) = S_0/(1 - C r)` is
admissible. That would turn a kinematic transfer into a sourced one, which is what "forced
versus sourced" is still missing.

**(b) The frame half.** Compute the geodesics of both frames for a particle whose mass tracks
`S`. That would make the Flanagan-Mannheim premise a computed object rather than a stated one.

**Further prior art**, found on a second search: Keith Horne, *Conformal Gravity rotation curves
with a conformal Higgs halo*, Mon. Not. Roy. Astron. Soc. **458** (2016) 4122, states it five
years before Hobson & Lasenby and to the level of the exact formula:

> Since particle rest masses scale with `S(r)/S_0`, their world lines do not follow time-like
> geodesics of the MK metric `g_mu_nu`, as previously assumed, but rather those of the
> Higgs-frame MK metric `Omega^2 g_mu_nu`, with the conformal factor `Omega(r) = S(r)/S_0`.

That is `BH0H`'s conformal factor and `BH0I`'s geodesic statement together. The first correction
named only Hobson & Lasenby; naming one prior source when there are two is the same failure at a
smaller scale.
