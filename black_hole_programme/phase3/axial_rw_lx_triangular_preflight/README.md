# Axial \(L_{\rm RW}\)–\(L_x\) triangular preflight

This package tests the dimensionally viable replacement for the excluded
claim that the complete six-dimensional axial Bach module is a single scalar
Regge--Wheeler square.

The exact four-state Ricci carrier is cyclic in \(P\).  Its scalar order-four
operator factors on the right as

\[
L_4=L_x\circ L_{\rm RW}.
\]

The second factor is not opaque.  Under
\(Z=y/[r^2(r-2)]\), its equation becomes the ingoing-EF form of the
\(\ell=2\) spin-one Regge--Wheeler equation, with Maxwell potential
\(6(1-2/r)/r^2\).  This is a differential-factor classification, not a
claim that a physical Maxwell field or spin-one particle is present.

The package also gives exact rational embedding and quotient maps and an
invertible rational gauge in which the carrier connection is block
triangular with diagonal factors \(L_{\rm RW}\) and \(L_x\).  The
two-dimensional Einstein metric kernel is independently conjugate to the
same \(L_{\rm RW}\) first-order companion system.  Consequently the complete
six-state module has an exact three-step filtration with diagonal factors

\[
L_{\rm RW},\qquad L_{\rm RW},\qquad L_x.
\]

This proves the requested **triangular equivalent**, but not the stronger
direct decomposition
\(\ker(L_{\rm RW}^2)\oplus\ker(L_x)\).  The natural transformed six-state
connection retains nonzero extension terms.  Whether a further rational
gauge splits those extensions or identifies the two RW factors with the
canonical scalar square remains open.

Run:

```bash
python3 -m black_hole_programme.phase3.axial_rw_lx_triangular_preflight.verify
python3 -m unittest -v \
  black_hole_programme.phase3.axial_rw_lx_triangular_preflight.tests.test_preflight
```
