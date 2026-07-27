# Complete massive axial first-jet crosswalk

Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`.

The complete Schwarzschild axial massive-spin-two equations form a coupled
two-channel system for \(Q\) and \(Z\).  At zero squared mass, the exact
Berndtson transformation splits this system into the axial spin-two
Regge--Wheeler factor and the spin-one Maxwell factor.  The transformation
has determinant \(\omega^{-4}\), and its full first-order intertwining
identity is checked symbolically.

Transforming the complete \(m=\mu^2\) tangent into that factor basis gives
four nonzero \(2\times2\) blocks.  The apparent reverse
spin-two-to-spin-one term is rationally exact: in scalar form it is removed
by the constant multiplier
\[
P=-\frac{16}{27\omega^2}.
\]
The tensor-led diagonal tangent has projective density
\[
\mathcal I_{\rm phys}
=
\frac{(r-2)(3r^4\omega^2-20r+30)}
{3r^5\omega^2}.
\]
It obeys the exact normal form
\[
\mathcal I_{\rm phys}
=
\mathcal K_{U_2}\!\left(\frac{r}{6\omega^2}\right)
+\frac13 f.
\]
Consequently,
\[
[\mathcal I_{\rm phys}]=\frac13[f].
\]

The factor \(1/3\) is not a convention that can be discarded.  An exhaustive
rational equality test for \([\mathcal I_{\rm phys}]=[f]\) has coefficient
rank \(3\), augmented rank \(4\), and obstruction
\[
\frac{80(\omega^2-3)}{3\omega^2}.
\]
By contrast, allowing proportionality gives the unique normal form above.

Combining this complete-system result with the certified Bach identity gives
\[
[\mathcal I_{\rm Bach}]
=
\frac{3i\omega}{2}[\mathcal I_{\rm phys}].
\]
The fixed-frequency tangent normalization is therefore
\[
m=\frac{3i\omega}{2}\tau,
\]
not \(m=(i\omega/2)\tau\).

The linearly growing gauge has the correct differentiated phase.  The raw
physical mass tangent has relative \(r\)-coefficient
\(-\sigma i/(2\omega)\); the complete-system reduction gauge adds
\(\sigma i/(3\omega)\), leaving \(-\sigma i/(6\omega)\).  Multiplication by
\(3i\omega/2\) gives \(\sigma/4\), exactly the Bach endpoint coefficient.
The Coulomb-power derivative remains zero.

This closes the exact local coupled-system part of the referee's crosswalk
request and corrects its normalization.  It does not yet supply a convergent
all-order differentiated massive Jost construction, exclude an
opposite-Jost admixture analytically, identify the certified Bach selector
with a physical massive-QNM velocity, or establish a global causal
resolvent.

CLOSE-OUT: DONE — exact complete coupled massive first jet and factor-three
Bach crosswalk certified; analytic differentiated-Jost and physical
mass-velocity promotion remain open.

EVIDENCE:
`black_hole_programme/phase4/axial_complete_massive_jet_crosswalk_v1/certificate.json`
