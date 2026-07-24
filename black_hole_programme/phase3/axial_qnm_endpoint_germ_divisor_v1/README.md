# Axial scalar QNM endpoint-germ divisor audit

Status: `EXACT — CLASSIFIED — NO ROOT COUNT`.

Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`.

This package derives the exact horizon and infinity reduced equations for
the axial \(\ell=2\), \(M=1\) spin-two Regge--Wheeler factor in the
repository's \(e^{+i\omega t}\) convention.  It extracts their formal
coefficient recurrences and proves that every recurrence and named frame
divisor is nonzero on the closed radius-\(0.025\) disk proposed by the
noncertifying QNM seed.

The disk geometry is imported only as an exact decimal/rational input.  The
seed's sampled winding and approximate root are not promoted.

The horizon factor is

\[
y=q^{2i\omega}P_H(q),\qquad q=1-\frac2r,
\]

and the coefficient of \(h_{m+1}\) in the reduced recurrence is

\[
(m+1)(m+1+4i\omega).
\]

The exact noncollision bound gives the unique nonresonant local Frobenius
germ after fixing \(h_0\).  It does not give a quantitative tail enclosure.

The outgoing infinity factor is

\[
y=e^{-i\omega/q}q^{2i\omega}P_I(q),\qquad q=\frac1r,
\]

and the coefficient of \(g_{m+1}\) in its formal inverse-\(r\) recurrence is

\[
2i\omega(m+1).
\]

The complete seed disk lies strictly in the upper-left quadrant.  This
excludes \(\omega=0\), all horizon collision points
\(\omega=i(m+1)/4\), the named frame events \(i/4,i/2,i\), and the exterior
moving divisor \(r\omega-2i\) for every real \(r\ge2\).

## Reproduction

```bash
python3 -m black_hole_programme.phase3.axial_qnm_endpoint_germ_divisor_v1.produce
python3 -m black_hole_programme.phase3.axial_qnm_endpoint_germ_divisor_v1.verify
python3 -m unittest -v black_hole_programme.phase3.axial_qnm_endpoint_germ_divisor_v1.test_endpoint_germs
```

## Boundary

The infinity series is only a formal asymptotic recurrence.  This package
does not enclose either endpoint remainder, propagate complex balls, prove
the Evans determinant nonzero on the contour, count roots, enclose a QNM, or
select a Bach Smith/EP2 branch.
