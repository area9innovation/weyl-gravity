# Axial local commutant and spectral \(C\), v1

This package separates two statements that must not be conflated.

1. The nonsplit axial spin-two differential module has local commutant
   \(\mathbb C[\varepsilon]/(\varepsilon^2)\).  It has no nontrivial local
   semisimple branch observable and no local positive involution.
2. Every positive-real-frequency incoming solution fiber nevertheless has a
   nonlocal spectral fundamental symmetry obtained from the matrix sign of
   its invertible Hermitian flux Gram.

The second construction is global and frame-dependent.  It does not establish
canonicity, covariance, causality, complex-frequency holomorphy, BRST
compatibility, or an endpoint-block-diagonal scattering symmetry.

At threshold the exact incoming Witt basis gives positive-majorant weights
\(\omega,\omega,\omega^3\).  The natural all-frequency completion is therefore
weighted and is not uniformly equivalent to unweighted \(L^2\).

The scattering section also proves a useful correction: once both the
conserved Krein identity and the fundamental-symmetry axioms hold, equality of
the pulled-back positive forms is equivalent to \(C\)-intertwining.  Neither
hypothesis may be dropped.

Run:

```bash
python3 -m black_hole_programme.phase4.axial_local_commutant_spectral_c_v1.produce
python3 -m black_hole_programme.phase4.axial_local_commutant_spectral_c_v1.verify
python3 -m unittest -v black_hole_programme.phase4.axial_local_commutant_spectral_c_v1.test_commutant_spectral_c
```
