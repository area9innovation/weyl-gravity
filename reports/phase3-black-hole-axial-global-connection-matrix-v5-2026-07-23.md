# Phase 3 axial global connection matrix v5

## Scope and disposition

This item attempted the first validated horizon-to-infinity connection matrix
for the repaired axial Bach system on Schwarzschild with `M=1`, `ell=2`, and
real `M omega` in `[1/2,3/4]`. The required first cell was
`[1/2,129/256]`.

The result is **SHORTFALL**, not a black-hole theorem. The affine substrate
gap reported by the earlier attempt is closed. The remaining issue is a
bounded-runtime decomposition of the validated radial flow; no mathematical
refusal was reached.

## What landed

The generated rail now:

* imports the exact repaired six-state flow and exact radial current;
* imports the certified horizon and infinity endpoint initializers;
* preserves one affine frequency generator (`7315`) through coefficients,
  frames, the forced lower lift, endpoint bases and the current;
* uses the raw horizon order
  `XH0a,XH0b,EH0,XHplus,EHout,XHminus` and selects raw columns `0,1,2`;
* propagates the horizon data from `rho=2^-22` in the sheared
  `(P,P',Q,Q',H1,rho F)` chart;
* materializes all 1,792 infinity coefficient entries once and reuses them
  through the table-backed affine-flow API;
* keeps the carrier, Einstein kernel and forced lower block separate.

Forge commit
`f2ab419230f03003580d885735e029ce2deed71e` supplies the table-backed
`IvLinParamAffineFlow` API. Its affected C/native and ASan gates pass.

## Measured execution gate

The compact generated rail is approximately 3.9 MB rather than the earlier
38 MB monolith. Forge compilation remains below 1 GiB peak RSS. In the
table-backed run:

1. the complete coefficient table materialized successfully;
2. the first 8-by-8 carrier flow began;
3. it did not return or refuse within the declared 20-minute execution
   budget;
4. the run was stopped before kernel, raw lower-lift, horizon, rank or current
   gates.

The complete command consumed 505 CPU seconds and 25:29 wall time including
compilation, with peak RSS 999,384 KiB. This is a runtime-budget shortfall,
not evidence of singularity or nonexistence.

## Exact successor

The first reset-level pilot on `t in [0,1]` (64 panels) also remained inside
the carrier flow at the ten-minute cutoff. Its compiled runner used 867,480
KiB peak RSS; execution itself used only 22,100 KiB. No mathematical refusal
was reached.

The next bounded unit is therefore an eight-panel microfactor of width `1/8`.
The 224 microfactors must use byte-identical shared micro-boundary frames and
the same affine cell. Each must emit a content-addressed `IvAffineMat` handoff
containing exact rational centre and linear data plus an outward interval
remainder. The final join composes those handoffs by certified affine
apply/solve and then performs:

* the full `T` column-rank test;
* the `I-` and `I+` projection-rank tests;
* the radial-current coordinate identity.

The request is recorded at
`planning/forge-requests/phase3-black-hole-axial-global-connection-matrix-v5.json`.

## Claim boundary

This work does not establish a global connection matrix, endpoint flux,
scattering channel, stability, CPT metric, positivity or unitarity. It also
does not establish a mathematical obstruction in the Bach system.

CLOSE-OUT: SHORTFALL — the shared-generator table rail is compiler-safe, but both the full carrier and one-reset carrier exceeded their execution budgets before any mathematical verdict
MISSING-DEP: content-addressed eight-panel microfactor flow and composition rail
