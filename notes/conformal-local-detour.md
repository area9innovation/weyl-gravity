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
the Euler-density boundary term vanish.  A separate global flat-BGG theorem,
recorded below, now proves exactness at the metric and curvature slots for
smooth complexified global sections.  It does not by itself prove exactness
on the finite-energy algebraic cylinder module, construct the local BV/BFV
zero-mode split, or identify the globally reduced physical state space.

The relevant primary source is Branson and Gover,
[The conformal deformation detour complex for the obstruction tensor](https://arxiv.org/abs/math/0605192).
Their theorem states that the obstruction-flat sequence is a formally
self-adjoint complex in all signatures; ellipticity is asserted only in
Riemannian signature.  The related general construction is Gover, Somberg,
and Soucek,
[Yang--Mills detour complexes and conformal geometry](https://arxiv.org/abs/math/0606401).
The global bridge uses Gover and Peterson,
[The ambient obstruction tensor and the conformal deformation complex](https://arxiv.org/abs/math/0408229),
and Čap,
[Overdetermined systems, conformal geometry, and the BGG complex](https://arxiv.org/abs/math/0610225).

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
from importing an elliptic-Hodge decomposition on a completed function
space, but it does not obstruct the following sheaf-theoretic argument.

## Global flat-BGG theorem on the cylinder

On an oriented conformally flat four-manifold, the adjoint BGG deformation
complex is

\[
\Gamma(T)\xrightarrow{K_0}\Gamma(S^2_0T^*[2])
\xrightarrow{C_1}\Gamma(\mathcal C[2])
\xrightarrow{C_1^\sharp\star}\Gamma(S^2_0T^*[-2])
\xrightarrow{K_0^\sharp}\Gamma(T^*[-2]).
\]

In particular,

\[
\boxed{C_1^\sharp\star C_1=0.}
\]

For a locally conformally flat pseudo-Riemannian geometry this is a fine
resolution of the flat adjoint-tractor local system.  Since

\[
M=\mathbb R\times S^3\simeq S^3
\]

is simply connected, the local system is constant with fibre
\(\mathfrak{so}(4,2)_\mathbb C\).  Therefore

\[
H^q_{\rm def}(M)
\cong H^q(S^3;\mathbb C)\otimes\mathfrak{so}(4,2)_\mathbb C
=
\begin{cases}
\mathfrak{so}(4,2)_\mathbb C,&q=0,3,\\
0,&q=1,2,4.
\end{cases}
\]

The two middle vanishing statements are precisely

\[
\boxed{\ker C_1=\operatorname{im}K_0},
\qquad
\boxed{\ker(C_1^\sharp\star)=\operatorname{im}C_1}
\]

for unrestricted smooth complexified global sections.  This conclusion is
global and all-level, but it is not a bounded-inverse statement on a Hilbert
or Krein completion.

## Exact Bach-to-curvature isomorphism

The map \([h]\mapsto C_1h\) now gives

\[
\boxed{
\frac{\ker B_{\rm lin}}{\operatorname{im}K_0}
\cong
\ker C_1^\sharp\cap\ker(C_1^\sharp\star).}
\]

The proof is algebraic once global exactness is known.  A Bach solution maps
to both kernels because \(B_{\rm lin}=C_1^\sharp C_1\) and
\(C_1^\sharp\star C_1=0\).  The first global exactness statement makes the
map injective.  The second produces a global metric potential for every
curvature in the target intersection, and \(C_1^\sharp U=0\) then makes that
potential Bach-flat.

In Lorentz signature, write \(U=U_++U_-\) with
\(\star U_\pm=\pm iU_\pm\).  The two target equations independently imply
\(C_1^\sharp U_+=C_1^\sharp U_-=0\).  Thus

\[
\frac{\ker B_{\rm lin}}{\operatorname{im}K_0}
\cong \mathscr W_+^{\rm sm}\oplus\mathscr W_-^{\rm sm}.
\]

The smooth result is equivariant, but by itself it controls the weight of
the quotient class rather than the mode content of a chosen metric
potential.  The repository now closes the algebraic positive-energy step
independently: `bridge/metric_preimages/all_energy.py` gives symbolic
same-energy metric representatives for every allowed `E/A/L` tower,
computes their full Weyl image, and proves the Bach equation identically in
the energy.  Thus secular terms such as `t exp(-iEt)` and infinite harmonic
preimages are unnecessary in the `D`-finite, `SO(4)`-finite module.  This
does not prove continuity, closed range, or bounded inverses on an analytic
completion.

## The controlled global zero-mode pair

The same theorem leaves exactly

\[
H^0_{\rm def}(M)\oplus H^3_{\rm def}(M)
\cong
\mathfrak{so}(4,2)_\mathbb C[0]
\oplus\mathfrak{so}(4,2)_\mathbb C[3].
\]

The first copy is the fifteen conformal Killing fields.  The second lies on
the dual equation side.  Its dimension, representation, and position make
it the canonical candidate for the dual BFV/Taub constraint sector, but the
equal-time map and normalization have not yet been proved.  This replaces an
unspecified collection of possible global rows with one finite pair.

## What the repository certifies

The following rails are complementary rather than interchangeable:

1. `verify_conformal_bgg_bridge.py` checks the signature-aware Hodge
   identities, the exact flat-symbol relation `C1^sharp star C1=0`, the
   cylinder cohomology dimensions, the chiral split, and the uniqueness and
   degree of the bottom four-ghost scalar.  The fine-resolution theorem
   remains a cited mathematical input.
2. `verify_conformal_detour_polynomial.py` constructs exact Euclidean
   homogeneous-polynomial matrices through degree six and reproduces the
   quotient dimensions `10,40,82,136,202`.  It is an independent convention
   and low-level regression audit, not the all-level proof.
3. `verify_conformal_cylinder_preimages.py` proves the symbolic all-energy
   physical `E/A/L` metric preimages in cylinder coordinates.
4. `verify_conformal_raw_bv_transfer.py` constructs the polynomial
   ghost/metric/equation/identity rows, an exact raw SDR, and the measured
   noncompact homotopies.  It closes the centered vector-space transfer but
   not the cross-energy cyclic BV/BFV normalization.
3. `verify_conformal_detour_action.py` checks the action normalization,
   formal adjoints, and finite scalar Ward kernels.
4. `verify_conformal_c2a_reducibilities.py` constructs all fifteen cylinder
   conformal-Killing reducibilities directly.
5. `verify_conformal_weyl_module.py` constructs the abstract algebraic
   `E/A/L` coefficient module and its complete character.  It does not by
   itself give the geometric curvature intertwiner or a finite-mode metric
   potential.

Run the bridge audits with

```bash
python3 symbolic/verify_conformal_bgg_bridge.py
python3 symbolic/verify_conformal_detour_polynomial.py
python3 symbolic/verify_conformal_detour_action.py
```

## Remaining algebraic and BV/BFV tasks

The main missing theorem is no longer smooth metric-to-curvature exactness.
Three sharper bridges remain:

1. **Algebraic cylinder realization:** construct the all-level `E/A/L`
   curvature intertwiner and finite-mode Bach-flat metric potentials.
2. **BV transfer:** split the canonical
   \(\mathfrak g[0]\oplus\mathfrak g[3]\) pair without double counting,
   inventory every relevant ghost and antifield row, and construct a full
   `SO(4,2)`-equivariant cyclic retract whose transferred differential is
   strictly Chevalley--Eilenberg.
3. **Residual BFV choice:** derive the centered four-ghost polarization and
   complementary-degree norm from the chosen closed-universe BFV pairing.

Identifying the degree-three BGG copy with the dual BFV/Taub sector and
fixing its normalization from one equivariant component remains a valuable
part of the second bridge, but the direct second-order Taub argument does not
depend on that bundle-level identification.

No conclusion about the full local-plus-residual BV cohomology, physical
pairing, or energy-six interaction block follows until that zero-mode task is
closed.
