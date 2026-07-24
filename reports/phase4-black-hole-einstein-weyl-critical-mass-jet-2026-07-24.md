# Critical Einstein--Weyl mass-jet report

## Disposition

The covariant critical-mass parent algebra is exact.  With the regular
carrier \(\phi=q\) and the signed squared-mass coefficient \(m\), the parent
equations are

\[
\mathcal E h=\mathcal A\phi,\qquad
\mathcal E\phi+m\mathcal E h=0,
\]

so \((\mathcal E+m\mathcal A)\phi=0\).  Differentiating the tensor branch at
\(m=0\) gives

\[
[h]=-[\partial_m\phi]=[\partial_\tau\phi],
\qquad \tau=-m,
\]

modulo the Einstein kernel.  On the transverse-traceless spin-two sector the
critical propagator is the exact difference quotient

\[
[\mathcal E(\mathcal E+m)]^{-1}
=m^{-1}\bigl[\mathcal E^{-1}-(\mathcal E+m)^{-1}\bigr]
\longrightarrow\mathcal E^{-2}.
\]

The finite-mass branch-sign involution diverges in the confluent basis, while
\(-m(C_m+I)/2\) tends to the square-zero extension map.

The massive endpoint audit gives

\[
\partial_m\sqrt{\omega^2-m}\big|_0=-\frac1{2\omega}.
\]

For the Schwarzschild Coulomb exponent

\[
x=M\frac{m-2\omega^2}{i\sqrt{\omega^2-m}},
\]

the first mass derivative vanishes exactly.  Thus the first critical mass jet
contains the linear-\(r_*\) generalized phase, but no first-order Coulomb
\(\log r\) term.  The independently certified intrinsic horizon jet likewise
has \(\dot\lambda_H=0\).

## Fail-closed boundary

The existing axial family

\[
\mathcal B(\tau)=\mathcal B_0+\tau\mathcal B_1
\]

was constructed intrinsically from the pure-Weyl six-state generator.  It has
not yet been derived by reducing the finite-mass Fierz--Pauli system.
Therefore this result does not yet prove

\[
\tau=-m,\qquad b=-\partial_m a,\qquad
\frac{\beta_n}{\alpha_n}=\frac{d\omega_n}{dm}\bigg|_0
\]

for the certified radial/Jost normalization.

The decisive successor is the exact projective-cocycle comparison

\[
[\mathcal I_{\rm mass}]=[\mathcal I_{\rm Bach}]
\quad\text{in}\quad
\mathbb C(r)/\mathcal K_U\mathbb C(r).
\]

The proposed \(O(\omega)\) inverse-shear scaling for \(\ell=2\), the eikonal
QNM slope, and the Maxwell Stückelberg interpretation remain predictions.

## Literature audit

The finite-mass normalization and endpoint phases were checked against
Antoniou--Gualtieri--Pani, arXiv:2412.15037v3 / Phys. Rev. D 111, 064059
(2025).  That source uses \(R-\alpha C^2\),
\(\alpha=1/(2\mu_{\rm lit}^2)\), the asymptotic momentum
\(k=\sqrt{\omega^2-\mu_{\rm lit}^2}\), and the Coulomb exponent used above.
The critical coalescence context was checked against
Lu--Pang--Pope, arXiv:1106.4657v3 / Phys. Rev. D 84, 064001 (2011).
Neither citation substitutes for the locally rederived algebra.

## Verification

- Tier 0: Python source parsed by execution; JSON artifacts materialized;
  scoped `git diff --check` is part of the commit gate.
- Tier 1:
  `python3 -m black_hole_programme.phase4.einstein_weyl_critical_mass_jet_v1.produce`;
  `python3 -m black_hole_programme.phase4.einstein_weyl_critical_mass_jet_v1.verify`;
  `python3 -m unittest -v black_hole_programme.phase4.einstein_weyl_critical_mass_jet_v1.test_mass_jet`.
  Producer, verifier and five mutation tests passed in 2.87 seconds.
- Tier 2 was not required: no imported mathematical object or shared schema
  was modified; all imports are content-hash pinned and checked.
- Tier 3 was not required: this is not a programme freeze or shared-core
  release.

CLOSE-OUT: DONE — exact parent critical-mass jet certified; the physical axial radial/Jost crosswalk is explicitly left open.

EVIDENCE: black_hole_programme/phase4/einstein_weyl_critical_mass_jet_v1/certificate.json
