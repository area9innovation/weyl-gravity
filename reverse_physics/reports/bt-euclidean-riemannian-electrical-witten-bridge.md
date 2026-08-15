# BT Riemannian electrical Witten bridge

Certificate:
`REVERSE_PHYSICS_BT_EUCLIDEAN_RIEMANNIAN_ELECTRICAL_WITTEN_BRIDGE_V1`

Dependency tags: `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`, `REDUCED-MODE`

## Result

The positive bosonic lift and the physical BT Witten problem use the same
random-conductance operator, but a metric term is essential. The reciprocal
determinant in the flat Schrödinger-potential density is the Riemannian volume
element produced by changing coordinates from the physical log field. It is
not an additional Euclidean potential whose Poincare inequality could be
imported unchanged.

Let

\[
 u(\psi)=r(\psi)-\overline r(\psi){\bf1},
 \qquad L_\psi=D_\psi u.
\]

The physical log-field carrier has its ordinary Euclidean metric. In the
flat $u$ coordinates this becomes

\[
 \boxed{g_u=L_\psi^{-T}L_\psi^{-1}},
 \qquad
 g_u^{-1}=L_\psi L_\psi^T.
\]

The already certified identity

\[
 |\det_HL_\psi|=\det{}'K(u)
\]

therefore says

\[
 d\operatorname{vol}_g(u)={du\over\det{}'K(u)}.
\]

Consequently the exact flat-potential BT law is most naturally written

\[
 d\mu(u)=Z^{-1}e^{-G(u)}d\operatorname{vol}_g(u),
 \qquad
 G(u)={\|u\|^2+N\ell_0(u)^2\over2\lambda^2}.
\]

Its physical scalar Dirichlet form is

\[
 \mathbb E_\mu\!\left[
  \nabla_uf\mathbin\cdot L_\psi L_\psi^T\nabla_uf
 \right],
\]

not the identity-metric expression. This distinction is decisive for the
Witten problem.

## One conductance operator, three roles

Let $\Omega=e^\psi$, let $K\Omega=0$ be the ground-shifted
Schrödinger operator, and define

\[
 B=\operatorname{diag}(\Omega)K\operatorname{diag}(\Omega).
\]

Then $B$ is the graph Laplacian with edge conductances

\[
 c_{xy}=w_{xy}\Omega_x\Omega_y.
\]

The same $B$ has three exact interpretations.

First, it is the precision operator of the pinned Gaussian free fields in the
positive bosonic lift.

Second, for a physical Fourier observable

\[
 F_h(\psi)=\langle h,\psi\rangle,
 \qquad \sum_xh_x=0,
\]

solve

\[
 B\phi=h,
 \qquad \sum_x\Omega_x^2\phi_x=0.
\]

Then its differential in flat coordinates is

\[
 \boxed{
 d_uF_h=-\operatorname{diag}(\Omega^2)\phi=L_\psi^{-T}h.}
\]

In a root-$o$ gauge, the solution is a pinned-GFF covariance:

\[
 \phi_x^{(o)}
 =\mathbb E_o\!\left[
   \zeta_x\sum_yh_y\zeta_y
  \right],
 \qquad \operatorname{Cov}(\zeta)=(B^{(o)})^{-1}.
\]

The constant shift needed to impose the $\Omega^2$-weighted gauge does not
change $B\phi=h$. Despite the possibly large electrical potential, the
physical norm remains exactly coordinate invariant:

\[
 |dF_h|_{g^{-1}}^2=\|h\|_2^2.
\]

There is a stronger connection cancellation. Although
$d_uF_h=L_\psi^{-T}h$ varies with $u$, it is the coordinate transform of
the constant one-form $h\mathbin\cdot d\psi$. It is therefore parallel for
the pullback metric:

\[
 \boxed{\nabla^g(dF_h)=0.}
\]

The derivatives of the killed Green kernel are exactly cancelled by the
Levi--Civita connection. Using the finite-volume Witten commutator and Gibbs
integration by parts gives

\[
 \mathcal L_1(dF_h)=d(\mathcal L_0F_h)=d(D_hS),
\]

\[
 \boxed{
 \mathcal Q_1(dF_h)
 =\mathbb E_\mu[(D_hS)^2]
 =\mathbb E_\mu[D_h^2S].}
\]

Thus the parallel-source Witten numerator is exactly the nonlinear current
susceptibility. The bosonic Green field supplies its coordinate expression;
it does not create an additional derivative penalty.

Third, the same operator factorizes the complete nonlinear action score. For

\[
 A(\psi)={1\over2}\sum_xr_x^2,
 \qquad w_x={r_x\over\Omega_x^2},
\]

the certified weighted current is

\[
 J_{xy}=c_{xy}(w_x-w_y),
\]

and direct differentiation gives

\[
 \boxed{
 \nabla_\psi A=-Bw,
 \qquad D_hA=-h^TBw.}
\]

Thus the bosonic covariance, the physical-source resolvent, and the nonlinear
score current are not merely analogous constructions. They are three uses of
one exact conductance Laplacian.

## Vacuum scaling

At the vacuum, $\Omega=1$ and $B=-\Delta$. If $h$ is a Fourier
eigenmode with eigenvalue $\omega(p)$, then

\[
 \phi={h\over\omega(p)},
 \qquad h^TB^+h={\|h\|^2\over\omega(p)}.
\]

Meanwhile $L_\psi=-\Delta$, the cometric is $(-\Delta)^2$, and the
source norm remains $\|h\|^2$. This reproduces the free bilaplacian
geometry without losing or inventing a momentum factor. For the parallel
source, the Witten numerator is exactly

\[
 \mathcal Q_1(dF_h)
 ={\omega(p)^2\over\lambda^2}\|h\|^2.
\]

For a fluctuating field, electrical Cauchy--Schwarz gives

\[
 |D_hA|^2\leq(h^TBh)(w^TBw).
\]

This is exact but not yet volume-uniform. Both factors fluctuate and the
previous slab obstruction shows that pointwise weighted-energy comparison is
too weak. The expectation must retain the Gibbs law and the Witten
connection.

## Exact four-cycle fixture

On the unweighted four-cycle, take

\[
 \Omega=(1,2,1,1/2),\qquad h=(1,-1,0,0).
\]

The conductance Laplacian is

\[
 B=\begin{pmatrix}
 5/2&-2&0&-1/2\\
 -2&4&-2&0\\
 0&-2&5/2&-1/2\\
 -1/2&0&-1/2&1
 \end{pmatrix}.
\]

The root-three pinned solution and the $\Omega^2$-mean-zero solution are

\[
 \phi^{(3)}=(1/5,-1/4,-1/5,0),
\]

\[
 \phi=(9/25,-9/100,-1/25,4/25).
\]

Both solve $B\phi=h$. The resulting flat source covector is

\[
 -\Omega^2\phi=(-9/25,9/25,1/25,-1/25),
\]

agreeing with the independently certified inverse-transpose flat Jacobian.
The electrical energy is

\[
 h^T\phi={9\over20}.
\]

For the weighted residual potential

\[
 w=(1/2,-1/4,1/2,8),
\]

the exact action score is

\[
 -Bw=(9/4,3,9/4,-15/2),
 \qquad D_hA=-3/4.
\]

Also

\[
 w^TBw={117\over2},
 \qquad h^TBh={21\over2}.
\]

In the standard three-coordinate mean-zero basis, the independently rebuilt
metric has relative volume factor

\[
 {\det g\over\det g_H}={16\over15625}
 =\left({4\over125}\right)^2.
\]

Thus its positive square root is exactly $1/\det'K=4/125$. Contracting the
transformed source with the cometric gives $2=\|h\|^2$, as required.

## Consequence for the research gate

The positive lift remains useful, but its role is now precise. It supplies a
pinned-GFF representation of the same Green operator that differentiates the
physical source. It does not authorize treating the flat potential as a
Euclidean field with identity Dirichlet metric.

The next calculation must put $B$, its pinned Green kernel, and the random
cometric into the connection-corrected Witten Schur form. At the vacuum it
must reproduce the $\omega(p)^2$ scale. The two admissible outcomes remain:

1. a volume-uniform lower form bound on the $dT$ cyclic sector; or
2. a normalized full-Witten low-Rayleigh sequence with nonzero $dT$
   overlap.

An effective-resistance blow-up, a pointwise weighted-energy failure, or a
Euclidean flat-coordinate Poincare theorem alone decides neither outcome.
No interacting $H^{-1}$ moment, continuum limit, Born probability, Krein
reconstruction, or Lorentzian statement is established here.
