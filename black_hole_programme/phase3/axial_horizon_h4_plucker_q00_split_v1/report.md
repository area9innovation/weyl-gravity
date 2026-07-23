# q00 split-remedy report

## Question

Does exact dyadic frequency subdivision preserve enough parameter
correlation to remove the unsplit q00 projective-pivot refusal at shell 4,
segment 3?

## Declared cover

The two closed child cells meet exactly at \(4097/8192\), have equal width
\(1/8192\), and cover the original q00 cell without a gap or an interior
overlap.

Each child restarts from its own exact frequency generator. No enclosure is
reinterpreted or sampled from the parent run.

## Outcome

Both children pass through shell 4, segment 2 and then independently return
typed refusal code 32 at shell 4, segment 3.

The final certified margins are:

- lower child: \(8.883383071043247\times10^{-8}\);
- upper child: \(8.808679226360098\times10^{-8}\).

All 45 Plücker relation checks pass at every reached boundary. The exact
two-child cover therefore shows that simply halving q00 does not recover a
componentwise projective pivot.

The similarity of the two child margins to the unsplit margin indicates
that the loss is not primarily driven by frequency-cell width. The next
remedy should change the projective functional or correlation
representation rather than recursively subdividing frequency by default.

## Boundary

This experiment stops at the former refusal boundary. It does not establish
later shells, endpoint amplitudes, scattering, a physical ghost, or
time-domain stability. It does not change papers or lifecycle records.
