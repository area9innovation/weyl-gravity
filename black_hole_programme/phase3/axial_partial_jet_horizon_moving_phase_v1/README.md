# Axial partial-jet horizon moving phase v1

This package replaces the refused all-mode near-horizon exponential
microfactor with the selected regular Frobenius germ.

The exact factor gauge has horizon residue

\[
R_H=\begin{pmatrix}0&0\\3/2&-1-4i\omega\end{pmatrix},
\qquad
E_{-1}=0.
\]

For the regular eigenline \(\lambda_H=0\), the left/right perturbation
formula therefore gives

\[
\dot\lambda_H=
\frac{\ell_H^T E_{-1}r_H}{\ell_H^Tr_H}=0.
\]

No intrinsic \(\tau\log\rho\) term is required.  The producer constructs five
exact orders of the coupled base/tangent Frobenius recurrence and evaluates
the finite seed with `IvTaylor4_omega tensor dual_tau`.

An exact Cauchy/generating-function majorant encloses the all-order coupled
tail at \(\rho_0=2^{-22}\).  The tail-enclosed seed is transported across the
first radial panel, where the direct repeated-spin-two route and the
dual-number route agree.

The result remains deliberately fail closed for the spin-one Levelt
initializer, transport beyond that one panel, \(K_H\), \(T_+\), H4, and
global scattering.

Run:

```bash
python3 -m black_hole_programme.phase3.axial_partial_jet_horizon_moving_phase_v1.produce --check
python3 -m black_hole_programme.phase3.axial_partial_jet_horizon_moving_phase_v1.verify
python3 -m unittest black_hole_programme.phase3.axial_partial_jet_horizon_moving_phase_v1.test_moving_phase
```
