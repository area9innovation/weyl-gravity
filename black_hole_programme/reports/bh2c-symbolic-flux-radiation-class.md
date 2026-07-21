# BH-2C symbolic-frequency finite-Lee–Wald-flux radiation class

**Work item:** `black-hole-symbolic-frequency-finite-flux-radiation-class`
**Certificate:** `black_hole_programme/certificates/BH2C_SYMBOLIC_FLUX_RADIATION_CLASS.json`
**Verdict token:** `BH2C_SYMBOLIC_FREQUENCY_FINITE_FLUX_RADIATION_CLASS_EINSTEIN_SELECTED`
**Dependency tags:** `LOCAL-ALGEBRAIC`, `REDUCED-MODE`
**Lifecycle:** `CLASSIFIED`

This certificate lifts the decisive content of the two certified `omega = 3/5`
flux-class fixtures — `BH2C_FLUX_CLASS` (axial) and `BH2C_POLAR_FLUX_CLASS`
(polar), each of which selects the Einstein sector at infinity by
symplectic-norm finiteness — to **symbolic real frequency `omega`**, and
establishes that the selection is **`omega`-independent** with **no real
exceptional frequency**. It closes the earlier checkpoint
(`reports/bh2c-symbolic-flux-einstein-extra-checkpoint.md`, Sessions 1–2) whose
Session-2 slice resolved the gauge obstruction and extracted the carrier
exponents but issued no certificate.

## What is established (symbolic `omega`, recomputed by the generator)

### 1. Literal Lee–Wald finite side (axial)

Driving the **certified** EF sphere-integrated axial Lee–Wald slice density
`F^v` (the same `LinearizedTheta` object certified in `BH2A_FLUX_MATRIX` and
specialised at `omega = 3/5` in `BH2C_FLUX_CLASS`) with the certified Einstein
(Regge–Wheeler) mode profiles `E0` (rate `mu = 0`) and `E2` (rate
`mu = -2 omega`), **retaining all terms — no leading-exponent shortcut** — the
conjugate-pair slice density falls as

```
F^v[E0 x E0] ~ r^-2 ,   F^v[E2 x E2] ~ r^-2 ,
```

with an **`omega`-independent** integer leading power `-2 < -1`: the Einstein
slice norm is **finite at infinity for every real `omega`**. The leading
coefficients (rational functions of `omega`) are recorded on the certificate;
they are nonzero and never change the power for real `omega != 0`.

This is the object the work item required "the literal Lee–Wald current
evaluation, not the leading exponent alone" — the full `F^v` bilinear, all
boundary/derivative-of-curvature terms retained, at symbolic frequency.

### 2. Extra-branch carrier exponents (axial)

On the Ricci-flat background `delta Ric` is gauge-invariant
(`L_xi Ric = L_xi 0 = 0`), so the extra (non-Einstein) branch is carried by the
trace-free, divergence-free axial **Ricci carrier** `psi` (the certified BH-2A
extra object), sidestepping the rank-1 axial-gauge degeneracy that blocked the
raw `(h0,h1)` metric in Session 1. Its operator `(1/2) Box psi + C psi = 0` at
infinity has, at symbolic `omega`,

```
rate condition:  lambda^2 + omega^2 = 0   =>   lambda = +- i omega
power:           rate -i omega -> s = -2 i omega ,   rate +i omega -> s = +2 i omega
```

i.e. `psi_carrier ~ exp(+- i omega r) r^{+- 2 i omega} = exp(+- i omega r_*)`
(tortoise phase): the carrier **amplitude real part is 0**, `omega`-independent.

### 3. Frequency dependence / no real exceptional frequency (derived)

`omega` enters every exponent **only** through an imaginary tortoise phase
(`|r^{2 i omega}| = 1` for real `omega`). Hence the amplitude real parts are
`omega`-independent: the Einstein metric master `F` decays (`Re <= -3`, giving
`F^v ~ r^-2`) while the extra carrier does not (`Re = 0`). The
finite-vs-divergent split is therefore **`omega`-independent as a derived fact**,
holding for every real `omega != 0`, with the exponents `+- i omega`,
`+- 2 i omega` never real and never colliding. `omega = 0` is the certified
exceptional carrier (`BH2C_SYMBOLIC_INDICIAL` exceptional set `{0}`) and is
excluded.

### 4. Numeric anchor (cross-rail)

The `omega = 3/5` specialisation of this same pipeline is the certified axial
table (`E0|E0 = E2|E2 = (-2,0)` finite; every extra-involving class
non-negative/divergent, `X0|X0` with a log) and the certified polar table
(Einstein sector finite, extra divergent). Both fixtures are imported by content
hash; the axial anchor table is stored verbatim and re-checked against the
on-disk fixture by the verifier.

## Headline

At symbolic real `omega`, the finite-slice-norm asymptotic phase space at
infinity contains **exactly the Einstein sector** (axial, literal flux; polar by
the parity-unified master ODE + `BH2B_POLAR_FLUX` nullness + the polar fixture),
for **every real `omega != 0`**. The horizon endpoint diagnostics do not exclude
the extra branch; infinity-side symplectic-norm finiteness does — a phase-space
normalization, not a local boundary condition — and that selection is
`omega`-independent.

## What is NOT established (fail-closed)

- The **exact symbolic-`omega` divergent sub-table** (`E|X`, `X|X`) and the
  **symbolic log tails**: the composed sourced log solve over `Q(omega)` did not
  complete a bounded run (the `omega = 3/5` fixture runs it in ~7 s; symbolic
  `omega` is ~200× per stage and the composed-log Gauss–Jordan over `Q(omega)`
  did not terminate in the time box). The divergent side is anchored at
  `omega = 3/5` by the two fixtures plus the `omega`-independent exponent
  argument — **not** recomputed symbolically.
- The **polar literal symbolic flux** is carried by the parity-unified master
  ODE (`BH2C_METRIC_ALL_ORDERS`, `unified_across_parities`) and the certified
  polar Einstein radial-flux nullness (`BH2B_POLAR_FLUX`) plus the polar fixture;
  it is not recomputed symbolically here.
- A **conjugate-frequency pairing theorem**, lift invariance, and an independent
  current-identity rail at symbolic `omega`.
- An **asymptotically flat phase-space / charge-algebra construction**, series
  summability, and **general `l`**.
- No Lorentzian-causal, spectral (quasinormal), scattering, stability,
  positivity, particle, or quantum statement — none is implied by a
  `REDUCED-MODE` asymptotic slice-norm classification.

## Verification

- `python3 black_hole_programme/verify_bh2c_symbolic_flux_radiation_class.py`
  — fast rails (seconds): schema + content hashes; numeric-anchor fixture
  hashes; an **independent** carrier-exponent rail re-derived on the
  verifier-side geometry engine `VbGeo` (Schouten / Kulkarni–Nomizu, not the
  generator's `Geometry`); the `omega`-independence / no-real-exceptional-
  frequency structural checks; and claim-boundary consistency.
- `... --full` — Tier-3 exhaustive rail (~6 min): additionally re-derives the
  axial Einstein literal `E0|E0`, `E2|E2` flux on `VbGeo` and checks both fall
  as `r^-2` with nonzero leading coefficient.
- `pytest black_hole_programme/tests/test_bh2c_symbolic_flux_radiation_class.py`
  — structural Tier-1 rail.

## Receipts

- Generator: `black_hole_programme/bh2c_symbolic_flux_radiation_class.py`
  (recomputes rails 1–2; imports the two `omega = 3/5` fixtures by hash).
- The finite side reuses the certified `BH2C_FLUX_CLASS` pipeline
  (`LinearizedTheta` `F^v`, sourced `M3` h-system, homogeneous Einstein jets)
  with `omega` symbolic and the profile set restricted to the Einstein branches.
- The carrier rail reuses the BH-2A trace-free Ricci-carrier construction (the
  Session-2 unblock).

EVIDENCE: `black_hole_programme/certificates/BH2C_SYMBOLIC_FLUX_RADIATION_CLASS.json`

CLOSE-OUT: DONE — symbolic real-frequency finite-Lee--Wald-flux classification established for the declared Schwarzschild radiation class; certificate `BH2C_SYMBOLIC_FLUX_RADIATION_CLASS.json`.
