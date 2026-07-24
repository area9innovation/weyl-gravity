# Axial QNM projective cocycle

This package scalarizes the certified rank-one extension between the two
axial spin-two Regge--Wheeler factors.  In the Schrödinger gauge

\[
D=\partial_{r_*}=\frac{r-2}{r}\partial_r,\qquad
L=D^2+U,
\]

the source has the form \(s_1D+s_0\), and

\[
\mathcal I=s_0-\frac12Ds_1
\]

defines a rational projective cocycle modulo
\(\mathcal K_U=D^3+4UD+2DU\).

The exact generic rational audit proves:

- \(\mathcal I\) is not in \(\operatorname{im}\mathcal K_U\);
- it has the declared reduced representative;
- its class is not proportional to the analytically continued angular
  derivative \(-f/r^2\).

The explicit left-null witness for generic rational nonexactness is

\[
\frac{40i(\omega^2-3)}{3\omega}.
\]

Consequently the finite-specialization corollary excludes splitting only
where this witness and the reduction are defined and nonzero.  No conclusion
is drawn at \(\omega=0\), at the frame-divisor collision \(\omega=i\), or at
the witness zeros \(\omega^2=3\).  The angular comparison has its own declared
witness-zero locus \(\omega^2=-4\).

The angular comparison is algebraic and is not a physical background
deformation.  The result does not evaluate a QNM period \(\beta_n\), choose a
QNM Smith case, or establish a double pole.

Run:

```bash
PYTHONPATH=. python3 -m \
  black_hole_programme.phase3.axial_qnm_projective_cocycle_v1.produce
PYTHONPATH=. python3 -m \
  black_hole_programme.phase3.axial_qnm_projective_cocycle_v1.verify
PYTHONPATH=. python3 -m unittest -v \
  black_hole_programme.phase3.axial_qnm_projective_cocycle_v1.test_projective_cocycle
```
