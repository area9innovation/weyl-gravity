# Berger detector-profile Haar normalization repair

Status: `CERTIFIED`.  The old `2.809e8` energy constant and “necessary `two_j>=138`” label are superseded; the cutoff obstruction and the computed `two_j=138` working rail survive.

The rod-coordinate Jacobian and the apparatus Jacobian are different objects:

- `d^3R/d^3y = 8 c a^3`;
- `dSigma = (8c/y0)d^3y`;
- `J=sqrt(det G)=a^3 y0`.

Therefore `J dSigma=d^3R`, and at a detector clock center `J=1`, not `8c`.  Repeating the Parseval argument with `chi=rho J` gives a rigorous total Fourier-energy lower bound above `7.02e7`.  The retained `two_j<=4` energy is still at most `675`, so more than `0.99999` is omitted.

The corrected unit-entry capacity lower bound first closes at dimension `98`, or `two_j=97`.  The already computed rail through `two_j=138` remains a valid larger working rail; it is simply no longer labelled mathematically necessary.  No streamed coefficient or temporal result changes, and no infinite-tail upper bound is inferred.
