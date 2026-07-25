# Paper 17 null-infinity reconstruction

Date: 2026-07-25  
Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`

## Result

The axial \(\ell=2\) reconstruction question is analytically closed at the
level of the exact outgoing radial/Jost module and its Bondi shear.

In the normalized outgoing factor frame,

\[
E=2\,\mathrm{EI2},\qquad
R=\mathrm{XI2}
-\frac{i(16\omega^2-4i\omega-5)}{\omega}\,\mathrm{XI3}.
\]

After the common physical phase is converted from ingoing
Eddington--Finkelstein time \(v\) to retarded time \(u=v-2r_*\), exact
substitution into the complete metric reconstruction gives

\[
(H_0,H_1)_E=(-r,2r)+O(1),
\]

\[
(H_0,H_1)_R=
\left(\frac34r^2-\frac32r,-\frac32r^2\right)+O(1).
\]

Thus

\[
(H_0,H_1)_R=-\frac34r\,(H_0,H_1)_E+O(E).
\]

The coefficient \(-3/4\) agrees independently with the certified outgoing
moving-phase rate derivative.

For the odd gauge law

\[
h_u\mapsto h_u-i\omega\xi,\qquad h_2\mapsto h_2-2\xi,
\]

the radiation-gauge choice \(\xi=h_u/(i\omega)\) yields
\(h_2=2ih_u/\omega\). Consequently,

\[
\mathcal O_{\mathscr I^+}E
=\lim_{r\to\infty}\frac{h^E_{AB}}r
=-\frac{2i}{\omega}X_{AB}\ne0.
\]

The Einstein QNM therefore has a nonzero asymptotic radiative overlap. Its
strain has the standard falloff

\[
\frac{h^E_{AB}}{r^2}
=-\frac{2i}{\omega r}e^{i\omega u}X_{AB}+O(r^{-2}).
\]

The generalized carrier does not share that falloff:

\[
\frac{h^R_{AB}}{r^2}
=\frac{3i}{2\omega}e^{i\omega u}X_{AB}+O(r^{-1}).
\]

The previously open cancellation does not occur. Since the generalized
root has nonzero carrier quotient, adding an Einstein representative cannot
cancel its leading \(r^2\) angular metric coefficient.

## Double-pole observation coefficient

In the \(E\)-normalization, the parent principal coefficient

\[
G_{-2}
=-\frac{\nu_n}{4\alpha_{\rm W}\alpha_n}
E\otimes\widetilde u_n
\]

has exact Bondi-shear coefficient

\[
\mathcal O_{\mathscr I^+}G_{-2}
=\frac{i\nu_n}
{2\alpha_{\rm W}\alpha_n\omega_n}
X_{AB}\otimes\widetilde u_n.
\]

The isolated local-contour strain therefore contains

\[
-\frac{\nu_n}
{2\alpha_{\rm W}\alpha_n\omega_n}
\frac{u}{r}e^{i\omega_nu}X_{AB}
\langle\widetilde u_n,S(\omega_n)F\rangle.
\]

Equivalently, using \(\nu_n=2i\kappa_n/\omega_n\), the scalar coefficient is
\(-i\kappa_n/(\alpha_{\rm W}\alpha_n\omega_n^2)\).

This proves the observation-side overlap. It does not prove nonzero
excitation by a specified physical source.

## Derivative correction

The paper previously combined a fixed-frequency Jost derivative with a
moving QNM frequency. These must be distinguished.

At fixed \(\omega\),

\[
\partial_m\log y_\sigma
=-\frac{\sigma i}{2\omega}r+O(1),\qquad
\partial_m\rho_\sigma=0.
\]

Along \(\omega_n(m)\),

\[
\frac{d}{dm}\log y_\sigma
=\sigma i\left(\nu_n-\frac1{2\omega_n}\right)r
+2\sigma i\nu_n\log r+O(1).
\]

The frequency-dependent radial and logarithmic pieces combine with the
temporal derivative into the phase-adapted null coordinate
\(u_\sigma=t+\sigma r_*\):

\[
\frac{d_m\Psi_m|_0}{\Psi_0}
=i\nu_nu_\sigma-\frac{\sigma i}{2\omega_n}r+O(1).
\]

For the outgoing branch \(\sigma=-1\), \(u_\sigma=u=t-r_*\), and the Bach
normalization gives

\[
\frac{i\omega_n}{2}\frac{d_m\Psi_m|_0}{\Psi_0}
=-i\kappa_nu-\frac14r+O(1).
\]

## Claim boundary

Established:

- exact outgoing Einstein and carrier metric heads;
- exact odd radiation-gauge reconstruction;
- nonzero Einstein Bondi shear;
- failure of standard falloff for the constant generalized component;
- nonzero observation-side coefficient of the double pole;
- standard \(u/r\) falloff of the enhanced local-contour term;
- corrected fixed-frequency versus total QNM mass derivative.

Not established:

- a nonzero overlap for a specified astrophysical source;
- a global retarded inverse-Laplace deformation;
- finite Bondi flux or an admissible large-gauge completion for the full
  generalized component;
- a detector or parameter-estimation theorem;
- polar parity or other multipoles.

The exact certificate is
`black_hole_programme/phase4/axial_qnm_null_infinity_reconstruction_v1/certificate.json`.

EVIDENCE: `black_hole_programme/phase4/axial_qnm_null_infinity_reconstruction_v1/receipt.json`

CLOSE-OUT: DONE — exact null-infinity reconstruction, corrected QNM tangent,
Paper 17 revision, certificate, claim map, mutation tests, PDF, and receipts
are complete; physical-source overlap and global causal promotion remain
explicit successor gates.
