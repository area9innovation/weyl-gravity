# Phase-3 moving-frame lower-transition report

## Disposition

`PREFLIGHT_PASS`

The first axial infinity microfactor now has a layout-correct, rigorously
enclosed moving-frame block-lower transition over four dyadic subdivisions
of the declared frequency cell.

## Corrected provenance boundary

The earlier structured preflight cannot support a multi-panel transition:
its composer used the standard-interleaved extractor after matrices had been
packed into a contiguous `8+4` block layout.  The earlier rank and width
claims are superseded.

This result imports only its coefficient and shared nine-frame table as
content-addressed input data.  It does not import the invalid composer, rank
claim, width claim, or certificate.

## Certified result

For generator `7315`,
\(M\omega\in[1/2,129/256]\), and \(t\in[0,1/8]\):

| Quantity | Result |
|---|---:|
| frequency subcells | 4 |
| radial panels per subcell | 8 |
| local Taylor order | 12 |
| carrier diagonal rank | 8 on every subcell |
| kernel diagonal rank | 4 on every subcell |
| exact upper-right block | zero |
| maximum local lower width | 0.00887141066029161 |
| maximum composed lower width | 0.07027467354990395 |
| superseded unframed benchmark | 621.8840812306481 |
| benchmark contraction factor | 8849.33433079602 |

The proof uses the exact block-lower moving-frame formula, retains the
shared affine generator, preserves outward Taylor remainders when restricting
to subcells, and rebases all composed blocks at 128 dyadic bits.  Full
12-by-12 interval rank is not used: the exact triangular determinant identity
reduces rank to the two certified diagonal blocks.

## Independent checks

The rational oracle verifies:

1. contiguous structured composition equals full matrix multiplication;
2. the displayed lower-block moving formula equals \(B_1^{-1}UB_0\);
3. the superseded interleaved extractor differs on carrier, kernel and lower
   blocks of a tagged 12-state witness.

Mutation rails reject the interleaved extractor, deletion of the
\(D_1W_c\) term, generator drift, loss of the width improvement, and source
hash drift.

## Remaining boundary

This preflight does not establish:

- a single affine enclosure without frequency subdivision;
- the remaining 223 infinity microfactors;
- useful width after joining the infinity chain;
- the horizon chart and horizon-to-infinity connection;
- populated physical channels or their flux signatures.

The next step is a deterministic batch run using one global 1,793-frame
table and ephemeral source hashes, followed by validated joins with dyadic
rebasing.

