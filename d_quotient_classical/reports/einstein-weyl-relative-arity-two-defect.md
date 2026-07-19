# Compact-product relative arity-two defect

## Result

`EINSTEIN_WEYL_RELATIVE_ARITY_TWO_DEFECT_V1` computes the strict defect

\[
\Delta_2=q_{2,W}(f_1,f_1)-f_1q_{2,E}
\]

for the frozen action-derived Einstein--Maxwell and Weyl--Maxwell Taylor
packages and the independently replayed support-local unary inclusion.  The
complete homogeneous-base-point PBW operator contains 50,854 nonzero rational
coefficients in 15 of the 40 target rows.  Its maximum total input-derivative
order is four.

The ten metric-equation rows contain 45,434 terms, the four diffeomorphism
identity rows contain 5,152 terms, and the Weyl-trace identity contains 268
terms.  The four Maxwell equation rows and the U(1) identity row remain strict.
The degree profile is

```text
output 1, inputs (-1,1):  6468
output 1, inputs (0,0):  38966
output 2, inputs (-1,2):   784
output 2, inputs (0,1):   4636
```

## Verification

The producer evaluates one output row at a time and never loads q3.  A separate
consumer validates both strict Draft 2020-12 schemas and every dependency
hash, independently decodes the two q2 payloads and unary inclusion, recomputes
all 50,854 coefficients, and compares the serialized operator row by row.

## Claim boundary

This is the exact source for the next homotopy equation.  A nonzero strict
defect proves only that the unary map is not by itself an arity-two morphism.
It neither proves nor disproves the existence of a support-local `f2`.
Arity three remains unauthorized until `f2` is constructed or a normalized
obstruction is certified.
