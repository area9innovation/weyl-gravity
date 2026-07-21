# BH-3 complex-frequency analytic-continuation gate

**Work item:** `black-hole-complex-frequency-analytic-continuation-gate`
**Certificate:** `black_hole_programme/certificates/BH3_ANALYTIC_CONTINUATION_GATE.json`
**Verdict token:** `BH3_AXIAL_ANALYTIC_CONTINUATION_MEROMORPHIC_POLAR_NOT_ACTIVATED`
**Dependency tags:** `LOCAL-ALGEBRAIC`, `REDUCED-MODE` · **Lifecycle:** `CLASSIFIED`

This gate certifies analytic continuation of the Schwarzschild exterior **axial**
mode families and the Lee–Wald symplectic **cross current** from the real
frequency axis into the complex-`omega` plane, with an **exact singular set**,
and records the **polar** sector as **NOT_ACTIVATED**. Everything is
symbolic/exact — no finite set of complex sample frequencies is used (which
cannot establish continuation). It is the analytic-continuation entry gate of the
BH-3 proof-obligation DAG; it admits no BH-3 vocabulary beyond the meromorphic
continuation itself.

## Axial theorem (m = 1, l = 2, `omega` in ℂ)

### 1. Cross scalar / symplectic current — meromorphic, exact poles {i, i/2}

The certified cross invariant `a(omega) = i F^r(E,X)/(pi alpha)`
(`BH2_SYMBOLIC_CROSS_INVARIANT`) is an **exact rational function**
`a(omega) = -96 i omega (omega-2i)(4omega-i)^2 / [5 (omega-i)(2omega-i)]`
with `gcd(num, den) = 1`. A rational function is meromorphic on all of ℂ with
**no branch points**, so it continues from the real axis to a meromorphic
function whose singular set is **exactly its pole set `{i, i/2}`** (both simple).
The Lee–Wald cross current `F^r = -i pi alpha a(omega)` continues with the same
poles. (The verifier recovers the poles independently by partial fractions.)

### 2. Mode Frobenius families — poles, no branch points

From the parity-unified master ODE (`BH2C_METRIC_ALL_ORDERS`,
`c2 F'' + c1 F' + c0 F = 0`, all coefficients polynomial in `omega`):

- the boundary **exponents are entire** in `omega` — infinity `{-3, -4 i omega
  + 1}`, horizon indicial `{0, -4 i omega - 2}`, and the certified RW ingoing
  `+-2 i m omega` — so no branch points arise from the exponents;
- the **infinity** Frobenius series coefficients (both branches) are rational in
  `omega` with **poles only at `omega = 0`**;
- the **horizon** Frobenius series coefficients (both branches) are rational in
  `omega` with poles on the **exact discrete imaginary resonance sets**
  - `s = 0` branch: `{ i j / 4 : j = 3, 4, 5, ... }` (nearest to the real axis
    at `3i/4`);
  - `s = -4 i omega - 2` branch: `{ i j / 4 : j = 1, 0, -1, -2, ... }` (nearest
    at `i/4`);

  these are the integer-difference Frobenius resonances (where a log basis
  appears) — **poles of the normalized representation, not branch points**; the
  invariant current `a(omega)` has poles only `{i, i/2}`.

### 3. Declared domain

`a(omega)` and `F^r` continue meromorphically to `ℂ \ {i, i/2}`. The joint
mode+current representation is analytic on the largest symmetric strip about the
real axis free of every coefficient pole, **`|Im omega| < 1/4`, `omega != 0`**
(the nearest imaginary poles are `±i/4`; `omega = 0` is the excluded exceptional
carrier and the infinity-series pole). The real axis lies in the domain;
**continuation never passes through a pole**. There is no branch point and no
divergent-flux boundary — every axial singularity is an isolated pole at an
exactly known location.

## Polar sector — NOT_ACTIVATED

`BH2_POLAR_QUANTIFIER_REPAIR` closed the polar cross covector **fixture-only**
(`generic_real_frequency_certified: false`); its route-B structural identity
(`Z = E - (K^{-1} a^H).X` symplectically null for all real `omega`) is an
**explicit missing object**, and the repair does not claim complex-`omega`
continuation. No polar continuation is extrapolated from the real-`omega`
fixtures (forbidden). The polar continuation is therefore recorded as
NOT_ACTIVATED, exactly as the stop condition permits.

## What is NOT established (fail-closed)

- any polar-sector continuation or polar singular set;
- Borel/analytic summability of the (asymptotic) infinity Frobenius series —
  coefficient-wise analyticity is proven; sum convergence off the real axis is a
  separate open object;
- general `l` (this gate is `l = 2`; the cross current is certified at `l = 2`);
- no stability, quasinormal-mode, ringdown, scattering, positivity, particle, or
  quantum claim — a meromorphic continuation of a `REDUCED-MODE` current is not a
  spectrum; continuation through a pole is excluded by the declared domain.

## Verification

- `python3 black_hole_programme/verify_bh3_analytic_continuation_gate.py`
  — exact, no sampling: schema + anchor content hashes; **independent**
  recovery of the cross poles by partial fractions; **independent**
  re-derivation of the horizon indicial and the infinity/horizon Frobenius
  coefficients with their `omega`-pole sets, the closed-form resonance formula
  `omega = i j / 4`, the purely-imaginary pole check, and the strip half-width
  `1/4`; polar NOT_ACTIVATED consistency with `BH2_POLAR_QUANTIFIER_REPAIR`;
  claim-boundary + vocabulary.
- `pytest black_hole_programme/tests/test_bh3_analytic_continuation_gate.py` —
  structural Tier-1 rail.

## Receipts

- Generator: `black_hole_programme/bh3_analytic_continuation_gate.py` — imports
  the four anchors by hash (`BH2_SYMBOLIC_CROSS_INVARIANT`,
  `BH2_GENERAL_L_STRUCTURAL`, `BH2C_METRIC_ALL_ORDERS`,
  `BH2_POLAR_QUANTIFIER_REPAIR`), proves the rational meromorphy of `a(omega)`,
  and builds the mode Frobenius series to audit the exact `omega`-pole sets.

EVIDENCE: `black_hole_programme/certificates/BH3_ANALYTIC_CONTINUATION_GATE.json`

CLOSE-OUT: DONE — axial complex-`omega` analytic continuation of modes and cross
current certified with an exact singular set; polar continuation NOT_ACTIVATED,
as permitted by the stop condition.
