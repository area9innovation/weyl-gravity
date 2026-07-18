# Clock-weighted Berger polarization stream through `two_j=138`

Dependency tags: `LOCAL-ALGEBRAIC`, `LORENTZIAN-CAUSAL`.

The exact Clebsch--Gordan recurrence is applied to the six corrected
external-clock scalar rails for `p=0,2,4,6,8,10`, including the declared
detector coframe prefactors.  Through form `two_j=138` this gives 86,736
detector-component entries, 231,018 scalar-term applications and 520,416
clock-power intervals.  The lower/upper neighboring scalar modes never exceed
`two_j=139`.

The artifact stores per-mode counts, maximum widths and canonical hashes of
the complete reconstructible interval stream instead of serializing a large
dense image.  The producer plus content-addressed scalar dependencies are the
machine-readable reconstruction path.  All 1,980 comparisons with the direct
`two_j<=4` form calculation have overlapping intervals.

The exhaustive generator/verifier replays all 520,416 intervals.  The normal
focused test rail instead checks the stored coverage, the exact signed-square-
root converter against the generic algebraic implementation, and a
reconstructed top-mode entry, keeping the per-commit smoke loop below the
repository's one-minute target.

This closes polarization coefficient construction.  The temporal Green
polynomial still has to be applied in exact charge blocks of dimension at
most three.  The spatial tail, full Maxwell and massive images, recoil,
second-order-cone restriction and inactive Bridge 3 remain open.
