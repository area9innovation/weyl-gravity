# BH-2C stage 4: polar norm-selection table — Einstein selected at infinity

## Verdict

`BH2C_POLAR_NORM_SELECTION_EINSTEIN_SELECTED_AT_INFINITY`
(certificate `black_hole_programme/certificates/BH2C_POLAR_FLUX_CLASS.json`,
tags `LOCAL-ALGEBRAIC` + `REDUCED-MODE`, lifecycle `CLASSIFIED`).

The polar (even-parity) companion of BH2C_FLUX_CLASS, decided at the
fixture level (polar ℓ = 2, ω = 3/5, Schwarzschild m = 1, EF chart).
The carrier foundation is imported live from the certified
BH2B_POLAR_REACH analysis (light mode: its full `_require` chain up to
the gauge-exponent stage re-runs inside this producer and verifier).

## Exact results

1. **Composed-lift classification with power enhancement.** Solving
   δRic[h] = ψ at r → ∞ per leading carrier formal solution (three per
   sector), with depth-12 carrier jets:
   - sector μ = 0: pure-power AND single/double-log ansätze at the naive
     base all fail; the lift requires **one power enhancement plus a
     single log** — class (extra, nlog) = (1, 1) at s_base = 1. This is
     the inhomogeneous realization of the rank-1 resonance certified in
     BH2C_ASYMPTOTIC_JORDAN ("at most one power enhancement"). The
     homogeneous σ₀ = 2 family still dominates the composed lift.
   - sector μ = −2ω: class (0, 0) at s_base = −12i/5 — a pure
     oscillatory power, no enhancement, no log.
   - Parity contrast: the axial composed lifts are single-log in both
     sectors with no enhancement.
   - Gauge control: the exact conformal-gauge carrier jet (harmonic Φ)
     classifies as (0, 0) pure-power through the same machinery.
2. **Flux power table** (leading (r-power, log-power) of the EF slice
   density F^v on conjugate pair classes, all jet combinations):
   E0×E0: identically **zero** in the slice density (an extra μ = 0
   degeneracy); E2×E2: (−2, 0), exactly the axial Einstein behavior —
   the Einstein slice norm is **finite** in both sectors.  (The certified
   BH2B_POLAR_FLUX nullness — the polar Einstein-branch *radial* flux
   F^r vanishes identically for conjugate pairs — is a separate exact
   statement about F^r, not about F^v.)
   E×X: (1, 0) sector 0 and (3, 0) sector −2ω — divergent;
   X×X: (2, 0) sector 0 and (4, 0) sector −2ω — divergent.
3. **Noise-floor discipline.** Every certified-nonzero entry lies
   strictly above the truncation noise floor of its pair.

## The source-depth lesson (methodological)

The derived carrier sources (D, Ec, G rows) carry positive r-weights up
to 4, so source series built from depth-N jets are valid only through
key N − 4. At the axial depth (N = 4) the polar μ0 staircase reads
corrupted keys and produces a *spurious inconsistency at every log
order*. The repair is depth-12 jets via a column-parametric staircase
(kernel parameters as exact rational columns; naive order-by-order
extension of shallow jets fails because kernel components back-react on
higher-order consistency). The exact conformal-gauge lift (which must be
pure-power) is the control that exposed the bug and now guards the
certificate. The axial certificate was re-verified at carrier depth 12:
its table and log-tail dichotomy are unchanged (see the depth-guard note
in `bh2c_flux_class.py`).

## Consequence

At the fixture mode level the polar finite-slice-norm asymptotic phase
space at infinity again contains **exactly the Einstein sector** (whose
μ = 0 self-pair is identically zero in the slice density). Together with
BH2C_FLUX_CLASS this completes the **two-parity norm-selection table**:
at both ends and in both parities, branch selection at infinity is a
phase-space normalization, not a local boundary condition.

## What was NOT established

- symbolic-frequency table; summability of the enhanced/log series;
- an asymptotically flat phase-space/charge-algebra construction;
- general ℓ; the sign or value of any finite norm;
- stability vocabulary stays locked.

## Receipts

```bash
python3 black_hole_programme/bh2c_polar_flux_class.py            # producer (~12 min)
python3 black_hole_programme/verify_bh2c_polar_flux_class.py     # independent verifier (~12 min)
python3 -m pytest black_hole_programme/tests/test_bh2c_polar_flux_class.py -q  # fast rail
```
