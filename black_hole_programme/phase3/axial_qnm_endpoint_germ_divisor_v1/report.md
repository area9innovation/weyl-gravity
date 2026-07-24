# Exact endpoint-germ divisor audit

Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`.

Lifecycle: `CLASSIFIED`.

## Established

For the exact axial \(\ell=2\), \(M=1\) spin-two Regge--Wheeler factor, the
future-horizon ansatz

\[
y=q^{2i\omega}P_H(q),\qquad q=1-\frac2r,
\]

has a reduced polynomial-coefficient recurrence whose \(h_{m+1}\) divisor is

\[
(m+1)(m+1+4i\omega).
\]

The outgoing-infinity ansatz

\[
y=e^{-i\omega/q}q^{2i\omega}P_I(q),\qquad q=\frac1r,
\]

has a formal inverse-\(r\) recurrence whose \(g_{m+1}\) divisor is

\[
2i\omega(m+1).
\]

On the closed radius-\(0.025\) disk imported from the noncertifying contour
seed, exact rational interval geometry gives

\[
\operatorname{Re}\omega
\le -0.348671684418041835793492,
\]

\[
\operatorname{Im}\omega
\ge 0.06396231568893569828046093.
\]

Consequently all horizon recurrence collisions
\(\omega=i(m+1)/4\), the infinity divisor \(\omega=0\), the named frame
events \(i/4,i/2,i\), and the moving exterior divisor \(r\omega-2i\) for
real \(r\ge2\) are excluded on the whole disk.  The horizon branch is a
nonresonant local Frobenius germ after fixing its leading coefficient.

## Open gates

The infinity recurrence is formal.  Neither endpoint has a quantitative
uniform remainder enclosure.  The following therefore remain open:

1. a ball-valued outgoing infinity initializer or compactified regular germ;
2. correlated complex-ball transport to a common match radius;
3. a nonzero boundary lower bound for the Evans determinant;
4. a ball-valued frequency derivative and argument-principle integer;
5. the intrinsic tangent \(b\), the moment \(b/a\), and every Smith/EP2
   selection.

The imported numerical seed supplies contour geometry only.  Its approximate
root and sampled winding remain explicitly noncertifying.

## Verification

```bash
python3 produce.py
python3 verify.py
python3 -m unittest -v test_endpoint_germs.py
python3 -m py_compile produce.py verify.py test_endpoint_germs.py
```

Observed scoped runtimes on 2026-07-24 were \(0.83\) s for production,
\(0.39\) s for independent verification, and \(0.41\) s for the six-test
unit suite.  The JSON Schema validation passed.  Tier 2 was not required
because no shared mathematical input changed; Tier 3 was not required
because this is not a freeze, theorem promotion, or release.

## Disposition

This is a successful exact prerequisite, not a QNM certificate.  It removes
endpoint recurrence collisions from the proposed disk and leaves analytic
tail/remainder control as the next typed dependency.
