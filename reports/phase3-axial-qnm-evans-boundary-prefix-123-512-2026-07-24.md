# Phase 3 axial QNM Evans boundary prefix: 123/512

Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`.

## Result

The validated projective Evans boundary continuation now covers the exact
contiguous parameter prefix

\[
[0,123/512].
\]

The append-only continuation used three packages:

- v7 repaired parent panel `105/512` by accepting children `210/1024` and
  `211/1024`;
- v7b repaired parent panel `106/512` by accepting children `212/1024` and
  `213/1024`;
- v8 accepted every fixed-grid child panel from `214/1024` through
  `245/1024`.

The next honest gap starts at `246/1024`. Every accepted panel certifies that
the common affine enclosure of the projective Evans mismatch excludes zero.
The v8 producer retained the unchanged transport core and accepted only the
ordered contiguous prefix.

## Performance disposition

The 32-panel v8 affected-chain producer completed in 108.81 seconds. Its first
performance-contract check therefore failed closed rather than being reported
as a fast Tier-1 pass. The mathematical rows, hashes and schema were retained,
and the replayless independent verifier, schema check and three focused tests
subsequently passed. Future continuation chunks must be smaller.

## What this establishes

- certified boundary nonvanishing on the exact prefix `[0,123/512]`;
- reproducible continuation of the same projective Evans section and stable
  root convention used by the predecessor packages;
- an exact next gap at `246/1024`.

## What this does not establish

This prefix is not a closed contour. It establishes no argument-principle
count, no QNM, no local Smith branch, no nonzero Fredholm overlap, and no EP2
or Green-resolvent pole. Those flags remain false in every certificate.

## Verification

The scoped verification consisted of Python compilation, JSON-schema
validation, the independent replayless verifiers, and three tests for each of
v7, v7b and v8. Paper 14's generated claim map, append-only coverage overlay,
source-map verifier and ten adversarial claim-map tests also passed. Two direct
`pdflatex` passes rebuilt the 45-page manuscript.
