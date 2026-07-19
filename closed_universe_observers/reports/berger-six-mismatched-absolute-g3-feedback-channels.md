# Six mismatched Berger absolute-g3 feedback channels

Dependency tags: `LOCAL-ALGEBRAIC`, `LORENTZIAN-CAUSAL`.

All six mismatched `two_j=0,k=0` blocks are now evaluated on source and
feedback mass-squared intervals `[1,2]`.  Exact support ordering is

```text
h0 < D0 < h1 < D1.
```

It forces four coefficient blocks to vanish without numerical cancellation:

```text
I_001 = I_010 = I_011 = I_110 = 0.
```

The two allowed paths require different cross-window inputs.  `I_100` uses
the newly certified D1 advanced detector remainder on `h0`.  `I_101`
propagates the `h0` source retardedly across the gap to `h1`.  Their real and
imaginary interval widths contract strictly on the 2/4/8-cell rail, but both
8-cell complex rectangles still contain zero.

Together with the two matched-channel certificate, all eight `I_abc[0,0]`
blocks are evaluated on this validation domain.  This is not an all-shell
recoil scalar, a sign/nonzero theorem, a physical mass choice, a quotient or
tangent-cone result, a Bridge-3 activation, or a quantum claim.
