# Axial outgoing population at \(\omega=1/2\)

This package combines two validated scalar reflection bounds with the exact
RW/RW/spin-one boundary filtration.  Boundary dévissage proves

\[
\ker T_+(1/2)=0,\qquad T_+(1/2)\in GL(3,\mathbb C).
\]

The transport-free Stokes identity then proves that the pulled-back outgoing
form

\[
\mathcal O=T_-^\dagger G_-T_- - H_{\mathcal H^+}
\]

is nondegenerate and has inertia \((1,2,0)\) for \(\alpha_{\rm W}>0\).

The result is pointwise.  It does not provide the entries of \(T_+\), the
extension mixing amplitudes, or interval-wide reflection nonvanishing.

Reproduce and verify with:

```bash
python3 -m black_hole_programme.phase3.axial_outgoing_population_point_half_v1.produce --check
python3 -m black_hole_programme.phase3.axial_outgoing_population_point_half_v1.verify
python3 -m unittest -v black_hole_programme.phase3.axial_outgoing_population_point_half_v1.test_point_half
```
