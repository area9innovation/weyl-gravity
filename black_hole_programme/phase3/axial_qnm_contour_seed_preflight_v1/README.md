# Axial QNM contour-seed preflight

Status: `UNVALIDATED-NUMERIC — NONCERTIFYING`

Dependency tag: `REDUCED-MODE`.

This directory contains deterministic floating-point reconnaissance for an
axial \(\ell=2\), \(M=1\) Schwarzschild scalar QNM contour.  It deliberately
contains no `certificate.json`.  The scripts do not use interval or ball
arithmetic, do not enclose endpoint-series remainders, and do not certify a
root, a root count, \(b/a\), \(\beta\), a Smith branch or an EP2.

## Scripts

- `qnm_leaver_preflight.py` evaluates finite backward continued-fraction
  approximants at increasing depths.
- `qnm_mpmath_shooting_preflight.py` independently matches horizon and
  infinity logarithmic derivatives using local series and arbitrary-precision
  Taylor ODE transport.
- `qnm_contour_diagnostic.py` samples a provisional circle using the finite
  continued fraction as a local Evans proxy.

The JSON files capture the stdout of the corresponding scripts.

## Reproduction

From the repository subtree root:

```bash
python3 \
  black_hole_programme/phase3/axial_qnm_contour_seed_preflight_v1/qnm_leaver_preflight.py
python3 \
  black_hole_programme/phase3/axial_qnm_contour_seed_preflight_v1/qnm_mpmath_shooting_preflight.py
python3 \
  black_hole_programme/phase3/axial_qnm_contour_seed_preflight_v1/qnm_contour_diagnostic.py
```

`mpmath` is required.  The shooting script normally takes tens of seconds.

## Fail-closed interpretation

Numerical agreement between these scripts is a seed-quality observation only.
The finite continued fraction may contain truncation poles; the shooting
endpoint expansions lack remainder enclosures; requested ODE tolerances are
not ball bounds; sampled winding is not an argument-principle proof; and the
intrinsic tangent \(b\) is absent.

See
`reports/phase3-axial-qnm-contour-seed-preflight-2026-07-24.md` for the exact
validated-endpoint-ball work ledger.
