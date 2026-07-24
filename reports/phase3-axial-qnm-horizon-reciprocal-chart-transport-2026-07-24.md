# Phase 3 axial QNM horizon reciprocal-chart transport

Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`.

This bounded repair tests the complete panel enclosure at the predecessor's
first `REFERENCE_Q_MAJORANT_DISCRIMINANT`. When the enclosure excludes zero,
it applies the certified chart change

\[
p=\frac1q,\qquad p_\tau=-\frac{q_\tau}{q^2},\qquad
p_\omega=-\frac{q_\omega}{q^2},
\]

and attempts validated continuation only to \(r=4\). The generated package
records the exact first obstruction and stops fail-closed if no reciprocal
chart is available or if the successor majorant fails.

The result is positive on this bounded gate. All 16 full-panel \(q\)
enclosures exclude zero at the first obstruction, whose radii are
\(r=2.6728683216200833\ldots\) for panels 0--7 and
\(r=2.7149225917213387\ldots\) for panels 8--15. After the reciprocal switch,
all 16 panels reach \(r=4\), with 129 or 133 accepted successor steps and no
rejected trial.

The decisive repair is to retain the scalar logarithmic norm of
\(2i\omega c-2bp\). A preliminary absolute-value estimate discarded this
dissipative real part and inflated the reciprocal remainder; it was not used
for the certified result.

This does not establish a QNM, an EP2, an Evans boundary theorem, an outgoing
Bach frame, or a Lorentzian-causal result.
