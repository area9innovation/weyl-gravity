# C2i-D: the local pure-Weyl detour complex

## Result and scope

There are two related statements which must not be conflated.

1. On a four-dimensional **Bach-flat** background, the linearized Bach
   operator sits in a formally self-adjoint conformal detour complex.  This is
   the Branson--Gover obstruction-flat theorem.
2. On the stronger **conformally flat** background used here, the
   action-normalized linearized Bach operator factors exactly through the
   linearized Weyl curvature.  This second statement follows from the
   quadratic pure-Weyl action, not from the leading-symbol argument alone.

The unit Einstein cylinder is conformally flat, so both statements apply on
the formal domain of smooth variations for which integrations by parts and
the Euler-density boundary term vanish.  Neither statement by itself proves
global exactness on `R x S3`, computes the local BV cohomology, or identifies
the globally reduced physical state space.

The relevant primary source is Branson and Gover,
[The conformal deformation detour complex for the obstruction tensor](https://arxiv.org/abs/math/0605192).
Their theorem states that the obstruction-flat sequence is a formally
self-adjoint complex in all signatures; ellipticity is asserted only in
Riemannian signature.  The related general construction is Gover, Somberg,
and Soucek,
[Yang--Mills detour complexes and conformal geometry](https://arxiv.org/abs/math/0606401).

## Operators and pairings

For a metric variation and a Diff\(\times\)Weyl parameter, set

\[
K(\xi,\sigma)_{\mu\nu}
=\mathcal L_\xi\bar g_{\mu\nu}+2\sigma\bar g_{\mu\nu}
=2\bar\nabla_{(\mu}\xi_{\nu)}+2\sigma\bar g_{\mu\nu}.
\]

After quotienting the trace, this becomes the conformal Killing operator

\[
(K_0\xi)_{\mu\nu}
=2\bar\nabla_{(\mu}\xi_{\nu)}
-\frac12\bar g_{\mu\nu}\bar\nabla\!\cdot\!\xi.
\]

Let

\[
C_1h=\left.\frac{d}{d\varepsilon}
C[\bar g+\varepsilon h]\right|_{\varepsilon=0}
\]

be the linearized Weyl-curvature map.  Formal adjoints below use the
spacetime action pairing, with compact temporal support, periodic Euclidean
time, or another boundary condition that removes the time-boundary term.
For the full gauge operator,

\[
K^\sharp t=
\left(-2\bar\nabla_\mu t^{\mu\nu},\;2t^\mu{}_{\mu}\right).
\]

On trace-free tensors the second component disappears and this reduces to
\(K_0^\sharp\).

## Exact local identities

### Gauge invariance of linearized Weyl curvature

Naturality and conformal covariance give

\[
C_1(\mathcal L_\xi\bar g)=\mathcal L_\xi C[\bar g],
\qquad
C_1(2\sigma\bar g)\propto\sigma C[\bar g].
\]

Since the cylinder background is conformally flat,

\[
\boxed{C_1K=0.}
\]

This is stronger than checking only the fifteen reducibility parameters:
it holds for arbitrary local Diff\(\times\)Weyl parameters.

### Exact factorization and its normalization

In four dimensions,

\[
C^2=R_{\mu\nu\rho\sigma}^2-2R_{\mu\nu}^2+\frac13R^2,
\qquad
E_4=R_{\mu\nu\rho\sigma}^2-4R_{\mu\nu}^2+R^2,
\]

so the repository action is

\[
S_{\rm red}
=\int\sqrt{-g}\left(R_{\mu\nu}^2-\frac13R^2\right)
=\frac12\int\sqrt{-g}\,(C^2-E_4).
\]

On a fixed topology and the formal domain just stated, \(E_4\) contributes
only a boundary/topological term.  Because \(C[\bar g]=0\), its mixed second
variation is

\[
\delta_h\delta_kS_{\rm red}
=\langle C_1h,C_1k\rangle_{\mathcal W}.
\]

Define the lower-metric action-normalized Euler derivative by

\[
\delta S_{\rm red}=\langle h,\mathcal E(g)\rangle,
\qquad
B_{\rm lin}=D\mathcal E|_{\bar g}.
\]

Then

\[
\langle h,B_{\rm lin}k\rangle
=\langle C_1h,C_1k\rangle_{\mathcal W},
\]

and therefore

\[
\boxed{B_{\rm lin}=C_1^\sharp C_1}
\]

with

\[
\boxed{\lambda=1}
\]

in the repository's action-normalized convention.  A Bach tensor defined
with a different overall sign, an upper-metric variation, or an action
containing an additional coupling has the corresponding rescaled
\(\lambda\).  On a Bach-flat but non-conformally-flat background, the
Branson--Gover theorem still gives the detour complex, but the simple exact
factorization need not hold: curvature-dependent lower-order terms remain.

The Weyl-fibre pairing is Lorentzian/indefinite.  Thus the notation
\(C_1^\sharp C_1\) is a formal-adjoint factorization, not a positivity
factorization.

### Detour and Noether identities

The factorization and \(C_1K=0\) give

\[
\boxed{B_{\rm lin}K=0.}
\]

Since a Hessian is formally self-adjoint,

\[
\boxed{B_{\rm lin}^\sharp=B_{\rm lin}},
\]

and hence

\[
\boxed{K^\sharp B_{\rm lin}=0.}
\]

Equivalently, the latter identity is the linearization of the exact Bach
Noether identities

\[
\nabla_\mu B^{\mu\nu}=0,
\qquad
B^\mu{}_{\mu}=0.
\]

In trace-free conformal geometry the local detour sequence is therefore

\[
\Gamma(T)
\xrightarrow{K_0}
\Gamma(S^2_0T^*)
\xrightarrow{B_{\rm lin}}
\Gamma(S^2_0T^*)
\xrightarrow{K_0^\sharp}
\Gamma(T^*).
\]

It is a formally self-adjoint complex.  Lorentzian signature prevents one
from importing the Riemannian elliptic-Hodge conclusion without a separate
hyperbolic/domain analysis.

## What the repository certifies now

The current machinery covers complementary portions of this theorem.

1. `verify_conformal_c2a_reducibilities.py` constructs all fifteen cylinder
   conformal-Killing Diff\(\times\)Weyl reducibilities exactly.  This checks
   the finite kernel of \(K\), not the arbitrary local gauge map.
2. `verify_conformal_quartic_exchange.py` constructs the full local scalar
   gauge matrices \(K_\pm\) and two independent slices for the `s`, `t`, and
   `u` harmonic blocks.
3. `verify_conformal_quartic_hessian.py` derives the corresponding quadratic
   action Hessians from the curved-cylinder reduced-Weyl action and verifies

   \[
   B_{\rm lin}K_+=0,
   \qquad
   K_-^T B_{\rm lin}=0
   \]

   exactly in those blocks.  The `t` block is genuinely Hessian-null and is
   not inverted.
4. `verify_conformal_detour_polynomial.py` constructs actual Euclidean
   homogeneous-polynomial jet matrices for \(K,C_1,B_1\) at degrees two
   through six.  It checks \(C_1K=0\), \(B_1K=0\), finite-level exactness
   at the potential--Weyl slot, separation of all fifteen conformal-Killing
   zero modes, and quotient dimensions `10,40,82,136,202`.  This is genuine local
   operator data, but it does not construct the Lorentzian cylinder-harmonic
   intertwiner or the formal-adjoint pairing.
5. `verify_conformal_detour_action.py` supplies the complementary
   action-derived audit.  It checks the exact frequency-adjoint
   self-adjointness of the scalar `s,t,u` Hessians, verifies the
   reduced-action normalization, and makes both finite scalar Ward kernels
   explicit.
6. `verify_gravity_spectral.py` contains an independent flat-momentum
   linearized Weyl map and verifies its diffeomorphism kernel and
   tracelessness.  It is not yet a curved-cylinder harmonic operator.
7. `verify_conformal_weyl_module.py` matches the on-shell Weyl-curvature
   character resolution to the complete `E/A/L` tower.  Character equality
   is not a proof of exactness of the local metric detour complex.

Run the fast bridge audit with

```bash
python3 symbolic/verify_conformal_detour_polynomial.py
python3 symbolic/verify_conformal_detour_action.py
```

Their fail-closed switches reject requests for an all-level Lorentzian
cylinder intertwiner, all harmonic sectors, or global cohomology.

## Missing executable certificate

The finite Euclidean homogeneous-polynomial jet certificate is exact at
degrees two through six.  An all-level **Lorentzian cylinder-harmonic** certificate
still requires new code.

### 1. Construct the geometric middle map

Extend the curved-cylinder perturbiner from Ricci curvature to the full
linearized Riemann tensor and form its trace-free Weyl projection.  For every
scalar, transverse-vector and TT harmonic block, construct

\[
C_{1,\Delta}:\mathcal H^{\rm metric}_\Delta
\longrightarrow\mathcal H^{\rm Weyl}_\Delta.
\]

The target can be organized by the electric and magnetic spatial Weyl
tensors, but its normalization must come from the full spacetime contraction
in the action.

### 2. Construct the exact adjoint pairing

Integrate the Weyl-fibre and metric pairings over `S3`, pairing frequency
\(+\omega\) with \(-\omega\).  This supplies the actual matrices defining
\(C_{1,\Delta}^\sharp\); ordinary Euclidean transpose is not sufficient in
Lorentzian component bases.

### 3. Verify the block identities independently

For every complete harmonic block, check

\[
C_{1,\Delta}K_\Delta=0,
\]

\[
B_{{\rm lin},\Delta}
=C_{1,\Delta}^\sharp C_{1,\Delta},
\]

where \(B_{{\rm lin},\Delta}\) is generated independently as the two-wave
action Hessian.  Then verify its adjointness and both Ward kernels.  Agreement
must include the trace/Weyl gauge direction and the generalized
conformal-Killing `ell=|omega|=1` block.

### 4. Only then compute local cohomology

The operator identities establish a complex, not its global exactness.
One must still determine

\[
\ker B_{{\rm lin},\Delta}/\operatorname{im}K_\Delta
\]

in every scalar, vector and TT block; split the fifteen reducibility zero
modes; include local ghosts, antifields and nonminimal pairs; and build the
compact-degree-equivariant cyclic retract required by C2h/C2i.

No conclusion about the global cylinder BRST cohomology, physical pairing,
or energy-six interaction block follows before that work is complete.
