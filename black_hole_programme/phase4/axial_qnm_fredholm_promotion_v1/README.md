# Axial QNM finite-interval Fredholm promotion A

This package promotes the already certified connection Smith valuations
`(0,0,2)` at one enclosed simple axial spin-two Schwarzschild QNM to a
second-order pole of a precisely declared **finite-interval radial
boundary-value inverse**.

For finite ordinary radii \(r_H<r_I\), the operator is

\[
\mathscr L(\omega)Y=
\left(
Y'-\mathbb A(\omega)Y,\,
B_H(\omega)Y(r_H),\,
B_I(\omega)Y(r_I)
\right):
H^1\longrightarrow L^2\oplus\mathbb C^3\oplus\mathbb C^3 .
\]

The proof uses the analytic initial-value isomorphism

\[
Y\longmapsto (Y'-\mathbb A Y,Y(r_H))
\]

to reduce \(\mathscr L\), by analytic invertible transformations, to
\(I_{L^2}\oplus\mathbb B(\omega)\).  Eliminating the three forbidden horizon
coordinates reduces the \(6\times6\) boundary matrix \(\mathbb B\) to the
effective \(3\times3\) matrix

\[
M(\omega)=B_I(\omega)\Phi(r_I,r_H;\omega)H(\omega).
\]

The selected endpoint frames identify \(M\) with the certified QNM connection
matrix up to analytic units.  Its Smith form `(0,0,2)` therefore gives a
rank-one coefficient at order \((\omega-\omega_n)^{-2}\) in
\(\mathscr L(\omega)^{-1}\).

The principal range is the source-Einstein root line.  The exact complete
reconstruction identifies that line with the nonzero metric kernel state
\((H_1,H_1')\), so the double-pole coefficient survives a physical metric
observation.

This is a `REDUCED-MODE` radial Green-operator theorem.  It is not an
exterior spacetime causal resolvent, does not perform a Laplace contour
deformation, and does not establish a \(t e^{i\omega_n t}\) contribution.
Those belong to a separate Fredholm promotion B.

Run:

```bash
python3 -m black_hole_programme.phase4.axial_qnm_fredholm_promotion_v1.produce
python3 -m black_hole_programme.phase4.axial_qnm_fredholm_promotion_v1.verify
python3 -m unittest -v black_hole_programme.phase4.axial_qnm_fredholm_promotion_v1.test_fredholm
```
