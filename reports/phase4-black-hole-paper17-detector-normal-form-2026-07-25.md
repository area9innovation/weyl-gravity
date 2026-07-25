# Paper 17 detector normal form

## Result

Paper 17 now carries the certified rank-one double pole through arbitrary
analytic source, reconstruction, and observation maps.  If

\[
G(\omega)=\frac{G_{-2}}{z^2}+\frac{G_{-1}}z+O(1),
\qquad z=\omega-\omega_n,
\]

and

\[
\mathcal H(\omega)=\mathcal O(\omega)G(\omega)S(\omega),
\]

then exact Laurent multiplication gives

\[
\mathcal H_{-2}=\mathcal O_0G_{-2}S_0,
\]

\[
\mathcal H_{-1}
=\mathcal O_0G_{-1}S_0
+\mathcal O_1G_{-2}S_0
+\mathcal O_0G_{-2}S_1.
\]

For the parent pure-Weyl metric response,

\[
\mathcal H_{-2}
=-\frac{\nu_n}{4\alpha_{\rm W}\alpha_n}
(\mathcal O_0u_n)\otimes(\widetilde u_nS_0).
\]

At the certified QNM, \(\nu_n\ne0\).  Therefore the measured local channel
retains the double pole precisely when both resonant overlaps are nonzero:

\[
\mathcal O(\omega_n)u_n\ne0,
\qquad
\widetilde u_nS(\omega_n)\ne0.
\]

Analytic frequency dependence in source insertion or reconstruction can
change the accompanying simple pole, but it affects the principal
coefficient only through the values of the maps at the resonance.

## Real isolated-resonance template

Combining the certified mode with its reflected partner gives the real
critical template

\[
h(t)=e^{-\gamma t}
\left[
(a_0+a_1t)\cos(\Omega t)
+(b_0+b_1t)\sin(\Omega t)
\right].
\]

With

\[
Q=\partial_t^2+2\gamma\partial_t+(\gamma^2+\Omega^2),
\]

the ordinary QNM quadratures obey \(Qh_{\rm GR}=0\), while the critical
template obeys

\[
Q^2h=0.
\]

Generically \(Qh\ne0\): applying \(Q\) once removes the ordinary part and
leaves another ordinary damped sinusoid.  This is the real-time
characterization of a repeated spectral root.

## Uniform near-critical template

For two resonances separated by \(\delta=\omega_m-\omega_0\), define

\[
\Phi_0=e^{i\omega_0t},
\qquad
\Phi_1=e^{i\omega_0t}\frac{e^{i\delta t}-1}{\delta}.
\]

The exact identity

\[
r_0e^{i\omega_0t}+r_1e^{i(\omega_0+\delta)t}
=A\Phi_0+B\Phi_1,
\qquad
A=r_0+r_1,\quad B=\delta r_1,
\]

replaces the diverging separated residues by finite confluent amplitudes.
Since

\[
\Phi_1(t;0)=it\,e^{i\omega_0t},
\]

the template is analytic at the Weyl point and becomes

\[
e^{i\omega_0t}[A(0)+iB(0)t].
\]

The crossover is controlled by

\[
\eta=\frac{|\delta|}{\gamma}
\simeq\frac{|\nu_nm|}{\gamma}.
\]

The regimes \(\eta\ll1\), \(\eta=O(1)\), and \(\eta\gg1\) are respectively
Jordan-like, crossover, and resolved two-mode regimes.  This is a local
linewidth classification, not a detector-sensitivity result.

## Finite isolated-mode norms

For

\[
g(t)=Ct\,e^{(-\gamma-i\Omega)t},
\qquad\gamma>0,
\]

Paper 17 proves

\[
\int_0^\infty|g(t)|^2\,dt
=\frac{|C|^2}{4\gamma^3},
\]

\[
\int_0^\infty|\dot g(t)|^2\,dt
=\frac{|C|^2(\gamma^2+\Omega^2)}{4\gamma^3}.
\]

The polynomial factor therefore has finite integrated amplitude and finite
derivative norm.  Together with the already proved bounded envelope, this
shows transient enhancement of the isolated mode, not a time-domain
instability.

## Independent verification

The exact verifier independently checks:

- both observable-transfer Laurent coefficients;
- the parent rank-one source-observer coefficient and its sign;
- \(Q^2h=0\), \(Qh\ne0\) for a generalized quadrature, and
  \(Qh_{\rm GR}=0\);
- the exact divided-difference identity and its removable critical limit;
- both integrated norms by symbolic Laplace integration;
- the fail-closed declaration schema.

Nine new mutation tests reject a missing simple-pole term, a parent-pole
sign change, an incorrect oscillator power, a reversed divided difference,
an incorrect linewidth ratio, an incorrect derivative norm, and three
forbidden physical promotions.  The scoped suite passed 67 tests in
66.190 seconds.  The full repository suite passed 149 tests in 1.26
seconds.

## Claim boundary

Established:

- exact propagation of the double and simple Laurent coefficients through
  analytic source/reconstruction chains;
- exact rank-one source-observer nonannihilation criterion;
- exact real repeated-root damped-sinusoid normal form;
- exact \(Q^2\) ordinary-differential characterization;
- exact divided-difference continuation to two separated resonances;
- exact linewidth crossover variable;
- exact finite integrated amplitude and derivative norms.

Not established:

- nonzero overlap for a specified asymptotic strain or Newman--Penrose
  observable;
- nonzero adjoint overlap for a specified astrophysical source;
- a global retarded inverse-Laplace deformation;
- a complete detector waveform;
- detectability or parameter-estimation sensitivity;
- a time-domain instability or quantum statement.

CLOSE-OUT: DONE — Paper 17 now gives the exact local waveform family and a
uniform near-critical parameterization that every observable Weyl EP2
channel must have when the two resonant overlaps are nonzero.

EVIDENCE: `reports/PAPER17_DETECTOR_NORMAL_FORM_TIER_RECEIPT.json`
