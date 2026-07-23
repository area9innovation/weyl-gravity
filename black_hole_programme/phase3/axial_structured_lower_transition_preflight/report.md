# Phase-3 structured lower-transition preflight

## Withdrawal

The former `PREFLIGHT_PASS` is withdrawn. The multi-panel `sl_compose`
routine received matrices produced by `ivam_block_lower`, whose layout is
contiguous \(8+4\), but extracted their blocks with
`gc_affine_submatrix`, which assumes the original interleaved standard-state
ordering. Its upper-right-zero check reconstructed a zero block after the
incorrect extraction and therefore could not expose the defect.

The source, certificate, and historical measurements are retained for
provenance. They establish no composed transition, rank, width, or global
connection. See `withdrawal.json`.

## Disposition

`WITHDRAWN_LAYOUT_DEFECT`, without paper promotion.

The full 12-by-12 raw interval transition is not needed to prove local
factor rank.  The axial system is exactly block lower after the certified
state permutation.  Its carrier and Einstein-kernel diagonal transitions
can be propagated and certified separately, while the lower lift is
computed by a one-\(G\) Peano--Baker convolution.  The determinant identity
then supplies the full-rank proof.

The first actual eight-panel microfactor passes in under one second after a
16-second compile.  This is a large improvement over the slow raw recurrence
and removes the first microfactor's rank refusal.

## Important limitation

The lower block's maximum interval width is about 621.884 on the first
microfactor.  That is acceptable for the structural rank theorem because
the lower block does not enter the determinant, but it may be too broad for
the eventual connection coefficients.  The next integration experiment
should therefore:

1. retain this diagonal-only rank proof;
2. express the lower block in the shared moving frames;
3. compute the reset correction
   \[
   C_{k,1}^{-1}
   (L C_{c,0}+K D_0-D_1W_c);
   \]
4. rebase that rectangular correction after each short reset;
5. compare width growth against the raw 32-by-1 pilot.

No global connection, channel, flux, CPT, or stability conclusion follows
from this preflight.
