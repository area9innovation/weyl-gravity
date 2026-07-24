# Mixed horizon pivot-switch continuation

Dependency tag: `REDUCED-MODE`.

## Bounded continuation

The certified \(e_2-e_3\) fixed-GL switch was replayed with the common
base/tangent action and the exact normalized identities

\[
v_{\mathrm{pivot}}=1,\qquad
\dot v_{\mathrm{pivot}}=0.
\]

Five panels strictly beyond the switch pass.  The last valid checkpoint is at

\[
\rho=\frac{3}{8388608}.
\]

Every nontrivial chart switch is serialized; only the original \(e_2-e_3\)
switch is needed on this bounded continuation.

## Honest next obstruction

On attempted panel 32, ending at
\(\rho=97/268435456\), the rectangular Taylor majorant returns a non-finite
tail.  At the preceding valid panel only the current \(e_2\) chart excludes
zero (modulus lower bound \(0.42120\ldots\)); every other row in the fixed
atlas has lower bound zero.  A further projective switch therefore cannot
pre-empt this particular loss.

The rail stops fail closed at `NONFINITE_TAYLOR_ENCLOSURE`.  It does not reach
the next dyadic shell, \(r=4\), \(H_4\), \(T_+\), or the global Stokes
identity.
