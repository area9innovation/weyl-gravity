# Symbolic cross invariant a(omega): exact axial rational function

**Certificate:** `certificates/BH2_SYMBOLIC_CROSS_INVARIANT.json`
**Result token:** `BH2_AXIAL_CROSS_INVARIANT_EXACT_RATIONAL_A_OF_OMEGA`
**Dependency tags:** `LOCAL-ALGEBRAIC` + `REDUCED-MODE`. **Lifecycle:** `CLASSIFIED`.
**Producer:** `bh2_symbolic_cross_invariant.py` ·
**Modes:** `bh2_cross_invariant_axial_modes.py` ·
**Verifier:** `verify_bh2_symbolic_cross_invariant.py` (independent VbGeo rail) ·
**Fast rail:** `tests/test_bh2_symbolic_cross_invariant.py`

## What the work item asked

The normal-form theorem `BH2_SYMPLECTIC_NORMAL_FORM` reduced the pure-Weyl
Einstein/additional symplectic extension to a **single** invariant: the cross
scalar `a = K(E, X) = i F^r(E, X)/(pi alpha)`. It proved the block is the
hyperbolic plane with inertia `(1,1)` and determinant `-|a|^2` **iff `a != 0`**,
and left the exact symbolic frequency dependence `a(omega)` as "the only
invariant left to compute". This item computes it (both parities requested).

## What is established (axial l=2)

### The exact cross invariant

With `cross(omega) = F^r(E, conj X)/(pi alpha)` the conserved Eddington-
Finkelstein horizon constant (rho^0 Laurent coefficient of the sphere-integrated
Lee-Wald radial flux), the exact answer is a **rational function of omega**:

```
cross(omega) = -96 * omega * (omega - 2i) * (4*omega - i)^2
               ---------------------------------------------
                        5 * (omega - i) * (2*omega - i)

a(omega) = i * cross(omega)            [ = K(E, X) of the normal form ]
```

### Classification (the item's core deliverable)

- **Zeros of `a`:** `omega in {0, 2i, i/4 (double)}`. The only real zero is
  `omega = 0`, the certified exceptional carrier (`BH2C_SYMBOLIC_INDICIAL`),
  which the claim excludes. **Hence `a(omega) != 0` for every real
  `omega != 0`** — the normal form's nondegenerate hyperbolic-plane branch is
  the physically realized one at *all* nonzero real frequencies, not just at the
  two fixtures. This settles the conditional in the normal-form theorem.
- **Poles of `a` (candidate exceptional frequencies):** `omega in {i, i/2}`.
  Both are off the real axis, so **there is no real exceptional frequency**
  (other than the separately-excluded `omega = 0`): `a` is finite and nonzero
  on all of `R \ {0}`.
- **Conjugate-frequency law:** `cross(-omega) = conj(cross(omega))`, hence
  `a(-omega) = -conj(a(omega))`, verified as an exact identity on every sampled
  real frequency. This is the conjugate-frequency stationarity the item asked
  for; combined with `|a(omega)|^2 = -det`, the normal-form determinant is the
  real-analytic function `-|a(omega)|^2` on `R \ {0}`.

### Method — structural, not interpolation-only

`cross(omega)` is a **conserved** horizon Wronskian: the rho^1..rho^KWIN window
coefficients vanish identically, so the rho^0 constant is exact at finite series
order. It is computed by the corrected composed lift of `BH2A_COMPOSED_REPAIR`
(level-1 Bianchi cascade algebraic in H1, level-2 rank-1 reduction, RW gauge,
n=0 Frobenius balance) reusing the certified ingoing carrier. A single
minimal-degree rational function (numerator degree 4, denominator degree 2) is
reconstructed from a fit set and then confirmed as a **genuine prediction** on a
disjoint held-out set of exact frequencies never used in the fit (over-
determination), and against the two independently certified fixtures. The
denominator is fixed structurally by the horizon indicial data, not by curve
fitting; the fit only fills in the numerator, and the held-out predictions rule
out any higher-degree alternative.

## Verification

- **Independent rail.** `verify_bh2_symbolic_cross_invariant.py` recomputes the
  horizon cross constants on the **VbGeo** Schouten/Kulkarni-Nomizu curvature
  engine (structurally distinct from `weyl_geometry.Geometry` +
  `linearized_bach`, which the producer uses) at several exact frequencies and
  confirms the certificate's closed form predicts every one; it re-derives the
  pole/zero classification, the conjugate law, the two-fixture recovery, and the
  provenance hashes.
- **Fast rail (Tier 1).** `tests/test_bh2_symbolic_cross_invariant.py` checks
  the closed form against the recorded exact samples, the two certified
  fixtures, the no-real-zero/no-real-pole classification, the conjugate law, and
  **decisive mutations** (a shifted pole `(omega-i) -> (omega-2i)`, the wrong
  conjugation sign, and a rescaled normalization are each rejected), plus the
  BH-3 vocabulary lock. Sub-second.

## What is NOT claimed

- **Polar l=2 cross covector `(E|X0, E|X1, E|X2)(omega)`** is *not* solved here.
  The polar horizon families are built by the composition tower of
  `bh2b_polar_cross_flux` (`compose` + per-order nullspace), which requires
  series order `NORD >= ~12` for the Einstein-mode row consistency and costs
  ~20 min per frequency (`windows_3/5 = 1283 s` in `BH2B_COMPOSED_REPAIR`);
  multi-sampled reconstruction at that cost is out of scope for this item's
  compute budget. The two certified polar fixtures (omega in {3/5, 2/7}) are
  recovered by that certificate. **Scoped successor:** a low-order / structural
  polar cross reconstruction, or a documented tower obstruction, is the
  remaining piece for full "both parities" coverage.
- No general `l`; `omega = 0` is excluded (certified exceptional carrier); no
  complex-`omega` analytic continuation; no spectral, dynamical, scattering,
  ringdown, stability, positivity, or particle statement. The cross scalar is a
  local-algebraic symplectic-pairing datum (`LOCAL-ALGEBRAIC` + `REDUCED-MODE`),
  not a Lorentzian-causal object.

## Successors this unlocks

- generic-`l` structural extension (the axial rational structure is the seed);
- BH-3 readiness inputs (the exact nondegeneracy `a != 0` on `R \ {0}`).
