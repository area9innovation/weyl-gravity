# Common Einstein--Maxwell/Weyl--Maxwell product background

## Status and claim boundary

This note records an exact `LOCAL-ALGEBRAIC` common-background theorem. Its
machine certificate is
`bridge/certificates/einstein_maxwell_product_incidence.json`.

The result supplies the base point that the Berger Einstein-incidence audit
showed was missing. It does not yet construct either linearized BV complex, a
tangent chain map, a relational clock, a causal Green complex, an
asymptotically flat sector, or an observable equivalence.

## Frozen theories

Use signature `(-,+,+,+)` and the repository Bach convention. The two actions
are

\[
S_{WM}=\int\!\sqrt{-g}\left(\frac{\alpha_B}{8}C_{abcd}C^{abcd}
-\frac14F_{ab}F^{ab}\right),
\]

\[
S_{EM}=\int\!\sqrt{-g}\left(\frac{R-2\Lambda}{2\kappa}
-\frac14F_{ab}F^{ab}\right).
\]

Their metric equations are respectively

\[
\alpha_B B_{ab}=T_{ab},\qquad
G_{ab}+\Lambda g_{ab}=\kappa T_{ab}.
\]

The same Maxwell action and the same field strength occur in both theories.

## Theorem

Let

\[
(M,g)=M_2(k_1)\times\Sigma_2(k_2)
\]

be the direct product of an oriented Lorentzian constant-curvature surface
and an oriented Riemannian constant-curvature surface. Take the aligned
Maxwell field

\[
F=E\,\mathrm{vol}_{M_2}+P\,\mathrm{vol}_{\Sigma_2},
\qquad \rho=\frac{E^2+P^2}{2}.
\]

The factor volume forms are parallel, so `dF=0` and `d*F=0`. In an adapted
orthonormal frame,

\[
R_{ab}=k_1g_{ab},\qquad R_{ij}=k_2g_{ij},\qquad
R=2(k_1+k_2),
\]

and, with

\[
A=\frac{(k_1-k_2)(k_1+k_2)}6,
\]

the remaining tensors reduce to

\[
B_{ab}=A g_{ab},\qquad B_{ij}=-A g_{ij},
\]

\[
T_{ab}=-\rho g_{ab},\qquad T_{ij}=+\rho g_{ij}.
\]

For `alpha_B>0`, `kappa>0`, `k_2>k_1`, and `k_1+k_2>0`, the same metric and
Maxwell field solve both theories exactly if

\[
\boxed{
\Lambda=\frac{k_1+k_2}{2},\qquad
\rho=\frac{k_2-k_1}{2\kappa},\qquad
\alpha_B\kappa(k_1+k_2)=3.}
\]

The generator derives the Riemann, Ricci, Schouten, Weyl, Bach, and Maxwell
stress tensors symbolically rather than installing these block formulas as
the answer. An independent consumer rechecks both metric equations.

## Flat critical specialization

Set `k_1=0` and choose the second factor to be a round sphere. Then

\[
k_2=\frac{3}{\alpha_B\kappa},\qquad
\Lambda=\frac{3}{2\alpha_B\kappa},\qquad
\rho=\frac{3}{2\alpha_B\kappa^2}.
\]

For a pure magnetic field,

\[
P^2=\frac{3}{\alpha_B\kappa^2},\qquad
r_{S^2}^2=\frac{\alpha_B\kappa}{3}.
\]

Thus `R^(1,1) x S^2` is a positive-energy common background. Quotienting the
flat spatial translation by a nonzero period gives the smooth spacetime

\[
\mathbb R_t\times S^1_L\times S^2_r
\]

with compact Cauchy topology `S^1 x S^2` and global timelike Killing field
`partial_t`. The quotient changes no local field equation.

For the optional global normalization

\[
\frac{q_{\min}}{2\pi}\int_{S^2}F=N\in\mathbb Z,
\]

the flat branch additionally requires

\[
\alpha_B=\frac{3N^2}{4q_{\min}^2}.
\]

This discrete formula depends on the declared Maxwell normalization; the
local common-background theorem does not.

## Endpoint audit

- If `k_1=k_2`, Einstein--Maxwell incidence forces `rho=0`. This is a
  flux-free common vacuum product, not the desired matter-coupled branch.
- If `k_1+k_2=0` with unequal curvatures, the Bach tensor vanishes. Pure
  Weyl--Maxwell then forces `T=0`, whereas Einstein--Maxwell requires nonzero
  flux. The Bertotti--Robinson-type endpoint is therefore not a same-field
  common solution of the two frozen theories.

The product family and flat critical branch are independently discussed in
the cosmological Einstein--Maxwell literature; see
[`arXiv:2604.19168`](https://arxiv.org/abs/2604.19168). That reference is
context, not a computational input to the certificate.

## Interpretation

This is stronger than the vacuum statement that every Einstein metric is
Bach-flat. It exhibits a nonzero positive stress tensor for which one metric
and one matter field solve both complete sets of background equations. It
therefore licenses a same-base-point tangent comparison.

It does not show that Einstein gravity is a Weyl gauge slice or that the
linearized observables agree. The common solution is also static rather than
a relational matter clock, and it is not asymptotically flat.

## Next gate

Construct the minimal Einstein--Maxwell and Diff x Weyl--Maxwell BV complexes
at this identical base point. The comparison must include the Maxwell ghost
and antifield rows and must certify:

1. both Hessians, gauge maps, Noether identities, nilpotency, and cyclicity;
2. an explicit tangent chain map or an exact obstruction;
3. helicity-two and photon cohomology before the residual quotient;
4. the two covariant presymplectic currents and their normalizations;
5. which additional fourth-order Weyl modes remain at this base point.

Only after those checks may this common solution be promoted to an Einstein
tangent sector.
