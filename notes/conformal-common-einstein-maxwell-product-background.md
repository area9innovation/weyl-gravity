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

### Principal tangent preflight completed

The certificate
`bridge/certificates/einstein_maxwell_product_tangent_preflight.json` now
freezes the two minimal layouts

```text
Einstein--Maxwell: 5 -> 14 -> 14 -> 5
Weyl--Maxwell:     6 -> 14 -> 14 -> 6
```

and constructs their exact principal chain map. In the normalization inherited
from the two frozen actions, the field map is the identity, the metric equation
map is `alpha_B kappa Q_p`, and the Maxwell equation map is the identity. The
final identity map multiplies the four Diff identities by
`alpha_B kappa p^2/2`, preserves the Maxwell identity, and has zero component
in the additional Weyl trace identity. All chain squares pass.

At a nonzero null covector the Einstein symbol cohomology splits into two
metric and two photon classes. It injects into the Weyl--Maxwell simple-symbol
cohomology, which has four metric and two photon classes. Thus the ordinary
Einstein graviton-plus-photon symbol sector is present, with a two-dimensional
additional Weyl metric cokernel at this level.

This is not yet a complete spectrum statement: generalized solutions of the
fourth-order operator require a prolonged characteristic complex.

### Complete on-shell linear tangent inclusion completed

The certificate
`bridge/certificates/einstein_maxwell_chevreton_tangent.json` now closes the
curvature/flux question **on shell**. On any four-dimensional source-free
Einstein--Maxwell solution, the repository-convention Bach identity reads

```text
B_mn-(2*kappa*Lambda/3)T_mn=C_Ch_mn,
```

where the convention-adjusted Chevreton trace `C_Ch` is quadratic in
`nabla F`. The aligned product flux is parallel, so `C_Ch` and its first
variation vanish. Together with the certified product tuning
`alpha_B*(2*kappa*Lambda/3)=1`, this proves that every solution of the
complete linearized Einstein--Maxwell equations solves the complete
linearized Weyl--Maxwell equations with the same `(h,a)`. An exact coordinate
radion fixture checks the result directly, including all lower-order terms.

The ordinary graviton-plus-photon tangents therefore survive before the
residual quotient. This remains an on-shell solution-tangent inclusion, not a
curved off-shell BV chain map or an observable embedding. Since the
Chevreton defect is quadratic, the first possible nonlinear obstruction is
at second order.

### Second-order tangent test completed

`EINSTEIN_MAXWELL_SECOND_ORDER_INCLUSION_TEST` now separates three outcomes.
On the compact `S1 x S2` quotient at fixed magnetic flux, the certified
constant radion and the Maxwell duality tangent have nonzero constant-lapse
pairings (`-2L` and `-L/2`), proving that no smooth periodic second-order
correction exists. Both extend if the required second-order magnetic-flux
shift is allowed, so these are charge-sector obstructions.

On the universal cover, a null radiative tangent has the nonzero pure-null
coefficient `C_Ch^(2)=4(dt-dx) tensor (dt-dx)`, but the explicit correction
`h2=D(-dt^2+dx^2)`, `D=u^3 v(5uv-24)/24`, cancels the complete quadratic
source. Nonzero Chevreton defect is therefore not by itself an obstruction.
Neither fixture settles periodic nonzero-frequency graviton/photon harmonics
or general nonlinear closure.

### Curved completion

Construct the minimal Einstein--Maxwell and Diff x Weyl--Maxwell BV complexes
at this identical base point. The comparison must include the Maxwell ghost
and antifield rows and must certify:

1. both Hessians, gauge maps, Noether identities, nilpotency, and cyclicity;
2. the off-shell equation/identity row maps extending the certified on-shell
   tangent inclusion, or an exact obstruction;
3. helicity-two and photon cohomology before the residual quotient;
4. the two covariant presymplectic currents and their normalizations;
5. which additional fourth-order Weyl modes remain at this base point.

Only after those checks may this common solution be promoted to an Einstein
tangent sector.
