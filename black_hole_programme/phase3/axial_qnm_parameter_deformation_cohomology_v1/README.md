# Axial QNM parameter-deformation cohomology

This package tests whether the certified rank-one repeated-spin-two
extension can be explained, modulo a rational connection coboundary, by
varying the Schwarzschild mass or the frequency.

The frozen operator uses \(M=1\).  The producer therefore first reconstructs
the dimensionful Schwarzschild \(\ell=2\) ingoing-Eddington--Finkelstein
Regge--Wheeler companion at fixed areal radius \(r\) and physical frequency
\(\omega\):

\[
A_{\rm RW}(M)=
\begin{pmatrix}
0&1\\
\dfrac{6(r-M)}{r^2(r-2M)}
&
-\dfrac{2M}{r(r-2M)}
-\dfrac{2i\omega r}{r-2M}
\end{pmatrix}.
\]

For

\[
E_{\rm RW}
=q_\omega\partial_\omega A_{\rm RW}
+q_M\partial_M A_{\rm RW}
+D_A B,\qquad
D_A B=B'+BA-AB,
\]

the trace residues at the horizon and infinity force

\[
q_\omega+\omega q_M=0.
\]

The surviving combination is not an independent deformation:

\[
\partial_M A_{\rm RW}-\omega\partial_\omega A_{\rm RW}
=D_A\!\left(-rA_{\rm RW}-\operatorname{diag}(0,1)\right)
\quad(M=1).
\]

Thus adjoining the mass derivative does not enlarge the rational
deformation class.  The proposed parameter-derivative explanation is
equivalent to the still-open question whether \(E_{\rm RW}\) itself is a
rational coboundary.

No \(\Lambda\) derivative is defined by the frozen Schwarzschild operator.
The angular label is fixed at discrete \(\ell=2\); an analytic continuation
in \(\ell(\ell+1)\) is not treated as a physical parameter deformation.

Run:

```bash
python3 -m black_hole_programme.phase3.axial_qnm_parameter_deformation_cohomology_v1.produce
python3 -m black_hole_programme.phase3.axial_qnm_parameter_deformation_cohomology_v1.verify
python3 -m unittest -v \
  black_hole_programme.phase3.axial_qnm_parameter_deformation_cohomology_v1.tests.test_cohomology
```
