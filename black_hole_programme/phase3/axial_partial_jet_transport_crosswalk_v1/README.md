# Axial partial-jet transport crosswalk v1

This package certifies an exact local algebraic crosswalk for the complete
axial six-state filtration. In factor coordinates ordered as metric
Regge–Wheeler tangent, carrier Regge–Wheeler base, and spin-one quotient, the
connection is

\[
\begin{pmatrix}
A&E&C\\
0&A&D\\
0&0&A_x
\end{pmatrix}.
\]

The previously published \(E=USJ\) block and the newly derived \(C=USN\)
block both have rank one. The full matrix is obtained directly from the
published six-state reconstruction by one exact rational coordinate change,
not by assembling independently transformed blocks.

The same matrix is the spin-two-row partial first jet of

\[
\mathcal B(\tau)=
\begin{pmatrix}
A+\tau E&D+\tau C\\
0&A_x
\end{pmatrix},
\]

with the spin-one state held \(\tau\)-independent. This is deliberately called
a **partial jet**: the full first jet of a four-state system would be
eight-dimensional.

The certificate does not construct compatible endpoint jet frames, recover
\(T_+\), prove a scattering identity, run bounded transport, or repair the H4
exterior-norm rail. In particular, preserving the intrinsic dual-number
correlation is not by itself an H4 cure; the required successor combines the
shared \(\omega\)-Taylor algebra with the dual-number algebra.

Run:

```bash
python3 -m black_hole_programme.phase3.axial_partial_jet_transport_crosswalk_v1.produce
python3 -m black_hole_programme.phase3.axial_partial_jet_transport_crosswalk_v1.verify
python3 -m unittest black_hole_programme.phase3.axial_partial_jet_transport_crosswalk_v1.test_partial_jet_crosswalk
```
