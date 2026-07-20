# BH2C metric reconstruction — all orders, both parities

**Certificate:** `certificates/BH2C_METRIC_ALL_ORDERS.json`
**Result token:** `BH2C_METRIC_ALL_ORDERS_ONE_POWER_POLYNOMIAL_LOG_FREE`
**Dependency tags:** `LOCAL-ALGEBRAIC` + `REDUCED-MODE`. **Lifecycle:** `CLASSIFIED`.
**Producer:** `bh2c_metric_all_orders.py` · **Verifier:** `verify_bh2c_metric_all_orders.py`
**Fast rail:** `tests/test_bh2c_metric_all_orders.py` (11 tests, ~0.7 s)

## What the work item asked

Lift the certified symbolic-frequency Schwarzschild curvature indicial sectors
(`BH2C_SYMBOLIC_INDICIAL`, commit `eb766b49e`) to **complete formal metric
perturbations**, both parities, real `omega != 0`, and decide **exactly**
whether the repeated fourth-order characteristics generate logarithmic or
tortoise-polynomial metric partners — either an all-orders reconstruction or
the first exact obstruction in a complete declared class.

## What is established

### 1. Unification: one master ODE governs both parities

The homogeneous polar `l=2` h-system (state `[Ah, Ch, Ch', Kh]`) collapses to a
single **autonomous second-order ODE for `Ch`**: the exact rational system
matrix has vanishing `Kh` and `Ah` columns except `Mh[0,3] = I*omega`, so `Kh`
and `Ah` are pure downstream quadratures. The axial `l=2` h-system (state
`[H0, H1, H1']`) collapses, after eliminating the quadrature `H0`, to a
third-order ODE for `H1` with **no undifferentiated `H1` term**, so `U = H1'`
obeys the *same* operator. Built from independent curvature rows, the two
parities produce the identical master operator

```
(r^2 - 2r) F'' + (2 I omega r^2 + 2 r + 2) F' + (6 I omega r - 6) F = 0,
        F = Ch (polar) = H1' (axial).
```

This retires the apparent length-3 (polar) / length-2 (axial) Jordan block of
`BH2C_POLAR_METRIC_INDICIAL`: the non-semisimple leading matrix was an artifact
of packaging one second-order ODE plus quadratures into a first-order frame.

### 2. Exact exponents

`r = infinity` is an irregular singular point of Poincaré rank 1. The two
formal solutions are

```
F ~ r^{-3} (1 + O(1/r))                                  [lam = 0]
F ~ exp(-2 I omega r) r^{-4 I omega + 1} (1 + O(1/r))    [lam = -2 I omega]
```

The oscillatory power exponent `-4 I omega + 1` reproduces the certified
`sigma0` of `BH2C_METRIC_LEADING` / `BH2C_POLAR_FLUX_CLASS` (**positive
control**).

### 3. Recurrence theorem (this is why it is *all orders*)

For the `lam = 0` branch the diagonal recursion coefficient at order `k` is
exactly `-2 I omega (k - 3)`: nonzero for every integer `k >= 4` whenever
`omega != 0`. Hence every `1/r` coefficient is uniquely determined and the
series is a genuine all-orders object, not a truncation. `k = 3` is the
indicial root (the free leading coefficient). The first coefficients are
`c3 = 1, c4 = 0, c5 = 15 I / (2 omega), c6 = 35 / (2 omega^2)`.

### 4. The mu = 0 resonance is a polynomial — not a log, not a ramification

The resonant `mu = 0` sector produces a single generalized-eigenmode whose only
non-decaying content is **one extra power of r**:

```
polar:  Ch = 0, Kh = kappa   =>   Ah = I*omega*kappa*r        (degree 1)
axial:  H1 = const           =>   H0 = (-I*omega) r + O(1)    (degree 1)
```

with **no logarithm and no fractional (ramified) power anywhere**. This is the
exact all-orders form of `BH2C_METRIC_LEADING`'s leading-order "at most one
power of r over the carrier" bound: the bound is *saturated* by a degree-1
polynomial and never exceeded. The a-priori admissibility of ramified
exponents flagged by `BH2C_POLAR_METRIC_INDICIAL` is thereby decided
**negatively**.

### 5. omega = 0 exception

At `omega = 0` the recurrence coefficient `-2 I omega (k-3)` vanishes
identically, the two exponential rates collide (`0 = -2 I omega`), and the
master indicial degenerates to `(s - 2)(s + 3)`: integer-separated exponents
with `r^{+2}` growth, so the one-power bound **breaks** and a logarithmic
resonance is admissible. `omega = 0` is the certified exceptional carrier
(`BH2C_SYMBOLIC_INDICIAL` exceptional set `{0}`); the physical reconstruction
claim here **excludes** it.

## Verification

- **Independent rail.** `verify_bh2c_metric_all_orders.py` re-derives every
  object on the VbGeo Schouten/Kulkarni–Nomizu curvature engine (structurally
  distinct from `weyl_geometry.Geometry` + `linearized_bach`) and reproduces
  the identical master ODE, both exponents, the recurrence coefficient, the
  positive control, the degree-1 log-free unramified mode, the `omega = 0`
  classification and the leading matrices. It also re-affirms that both leading
  matrices equal `BH2C_METRIC_LEADING`'s `B0h`, and checks schema + content
  hashes. (~16 s)
- **Fast rail (Tier 1).** `tests/test_bh2c_metric_all_orders.py` re-derives the
  exponents, the recurrence coefficient and the `omega = 0` indicial directly
  from the recorded master-ODE strings (no geometry rebuild), and includes
  **decisive mutations**: a wrong `lam = 0` exponent (`-2`, `-4`) fails the
  leading balance; the recurrence resonance occurs at exactly `k = 3` and
  nowhere else; and omitting the `omega = 0` exception is caught by the
  integer-separated exponents (log admissible). ~0.7 s.

## What is NOT claimed

No convergence or Borel summability of the formal series; no finite-flux,
radiative, spectral, dynamical-selection or physical statement; no general `l`;
no on-shell or sourced-composition reconstruction (this is the homogeneous
h-system). The sourced-composition log tails of `BH2C_FLUX_CLASS` are a
distinct object and are not addressed here.

## Successors this unlocks

- the symbolic-frequency finite-flux boundary class
  (`black-hole-symbolic-frequency-finite-flux-radiation-class`);
- the metric-level input required by Paper 14 endpoint disposition.
