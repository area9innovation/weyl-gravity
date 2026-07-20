# Polar composed-lift audit and exact constant horizon fluxes

## Verdict

`BH2B_POLAR_COMPOSED_LIFT_AUDITED_EXACT_CONSTANT_FLUX`
(certificate `black_hole_programme/certificates/BH2B_COMPOSED_REPAIR.json`,
tags `LOCAL-ALGEBRAIC` + `REDUCED-MODE`, lifecycle `CLASSIFIED`).

Polar counterpart of `BH2A_COMPOSED_REPAIR`, closing the work item
`black-hole-polar-composed-repair`. Unlike the axial case, **no pipeline
defect was found at the horizon**: the certified polar composition
already imposed all seven δRic rows, and the repair is a strengthening
(exact constants replacing radius-sampled numerics) plus one genuine
correction at infinity.

## 1. Horizon: exact constant fluxes (supersedes the sampled values)

The sphere-integrated EF Lee–Wald `F^r` of every conjugate family pair is
expanded as an exact Laurent window in ρ = r − 2. The structure is sharp:

| block | result |
|---|---|
| all 9 conformal-gauge pairs (`G|*`, `*|G`) | identically zero at every window key |
| `E|E` | identically zero at every window key |
| 15 physical pairs (`E|Xj`, `Xi|Xj`) | exactly one nonzero key, ρ⁰ |

Keys ρ¹…ρ⁷ vanish identically for every pair — **true on-shell
constancy**, not a tolerance. (Key ρ⁸ is the truncation edge of the
NORD = 16 mode series and lies outside the certified window.) This
supersedes `BH2B_POLAR_CROSS_FLUX`'s radius-sampled numerical matrix and
its 5 × 10⁻² r-independence tolerance with exact rational constants; that
certificate's *theorems* (composition existence, Hermiticity, null
control separation) are **confirmed, not repaired**.

Representative exact values at ω = 3/5, as `F^r/(πα)`:

| pair | exact constant |
|---|---|
| `X0|X0` | −2871808 i/35525 |
| `X1|X1` | −1172815072 i/22203125 |
| `X0|X1` | −63530880/888125 − 20282624 i/888125 |
| `X1|X2` | 1177699920/22203125 − 601270848 i/22203125 |

Exact Hermiticity (`K = i F^r/(πα)`, `K_ij = conj(K_ji)`) and exact real
positivity of the extra-block diagonal now hold as *exact rational
identities*, replacing the earlier truncation-bounded numeric checks.

## 2. Lift statement

All analytic carrier modes lift, at both fixtures and in both sectors:
the composition recursion (n = 0 Frobenius balance imposed, log resonance
fail-closed) plus the Einstein-family correction solve succeeds for every
mode. The lift ambiguity is exactly span(Einstein mode, conformal gauge
mode) per slot.

## 3. Invariance classification

- **Conformal shifts change nothing** — every `G` pair is identically
  zero, so adding any multiple of the gauge mode to either slot leaves
  every entry fixed.
- **Einstein shifts** leave the controls and the `E` row/column invariant
  (because `E|E` = 0 exactly) and shift the extra block by exact
  multiples of the cross constants:
  `ΔF(Xi|Xj) = conj(β_j)·F(Xi|E) + β_i·F(E|Xj)`.
- Therefore the **cross constants are invariant** and the **extra-block
  constants are representative-dependent**; the certified values are at
  the pipeline's canonical representatives (correction parameters
  zeroed). A representative-invariant sign theory remains the open
  successor item.

## 4. Infinity: the vv/vr audit — a genuine correction to BH2C

The `BH2C_POLAR_FLUX_CLASS` homogeneous h-jets solve a four-row reduction
(vx, rx, rr, angW); the `vv` and `vr` rows were never imposed. Auditing
them exactly:

- `vr` is **clean** on every jet, and the −2ω sector jet is clean on both
  rows.
- **All three μ0 power jets (σ₀ = 1, 0, −1) fail `vv`** with exact
  nonzero residuals. The shipped `E0` representative — the terminating
  jet `(A, C, K) = (r, 0, −5i/3)` — fails with the closed-form residual
  **(2r + 3)/r²**, so it is *not* a linearized Einstein solution.
- The μ0 space contains **exactly one** Einstein direction: the unique
  vv-clean combination of the three jets (exact rational coefficients,
  nullspace dimension 1, all three jets participating). It passes vv, vr
  and both imposed rows.

Recomputed table row with the true representative:

| pair | shipped BH2C | corrected |
|---|---|---|
| `E0|E0` | identically 0 ("extra μ0 degeneracy") | **(−2, 0)** |
| `E0|X0j*` | (1, 0) | (1, 0) — unchanged |

The corrected `E0|E0` class equals the certified `E2|E2` class, so the
two parities' Einstein pairs now behave identically. **The
norm-selection verdict survives and is strengthened**: Einstein pairs
are slice-integrable, all extra pairs divergent, Einstein selected in
both sectors. Only the μ0 Einstein *row* of the BH2C table is
superseded; the E|X and X|X classes and the selection theorem stand.

## Decisive mutations

- **M1 (row audit).** The superseded `E0` representative fails `vv` with
  the exact closed-form residual (2r + 3)/r² — a positive-control check
  confirms the four imposed rows are simultaneously clean on it, so the
  failure is specific to the never-imposed row.
- **M2 (window).** A deliberately off-shell pseudo-mode (the a-slot `X0`
  series truncated to its leading three orders) drifts at nonzero window
  keys, proving the constancy assert is decisive rather than vacuous.

## Verification discipline

Bilinear coefficients are extracted by differentiation of the multilinear
structure (never `.coeff` on expanded giant trees); all arithmetic is
exact Laurent-dict with intermediate caps above the output window (towers
first, coefficient last); `nsimplify` is used nowhere; and the imposed
rows are re-audited as positive controls before any vv/vr verdict is
trusted. These are the five tool-traps banked in the axial repair,
applied prospectively.

## What was NOT established

- symbolic-frequency values; general ℓ;
- a representative-invariant extra-block sign theory (null-quotient
  pairing — the named successor);
- outer-boundary / scattering-domain counterparts;
- any dynamical-behaviour statement (vocabulary coordinator-gated).

## Receipts

```bash
python3 black_hole_programme/bh2b_composed_repair.py          # producer
python3 black_hole_programme/verify_bh2b_composed_repair.py   # independent verifier (VbGeo)
python3 -m pytest black_hole_programme/tests/test_bh2b_composed_repair.py -q
```

## Close-out

```text
CLOSE-OUT: DONE — the complete stop condition is met: a polar composed-repair certificate with an independent verifier, decisive mutations for each repaired source/row term, and this human report; it states that all analytic carrier modes lift, prints the exact mixed and extra pairings at both declared fixtures, classifies which entries are invariant under Einstein/conformal lift shifts, and supersedes the affected older fixture values (BH2B_POLAR_CROSS_FLUX values; BH2C mu0 Einstein row) append-only with content hashes and explicit scope statements.
EVIDENCE: black_hole_programme/certificates/BH2B_COMPOSED_REPAIR.json (commit d7c637fa; producer 3002.7 s, fast rail 5/5, independent VbGeo verifier 2522.8 s all checks passed)
```
