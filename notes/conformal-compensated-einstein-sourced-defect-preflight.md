# Sourced Einstein-defect preflight in the compensated phase

## Result

The next Einstein-sector problem is not automatically a construction problem.
For ordinary same-source matter coupling, the existence of a sourced Einstein
sector is already constrained by a local tensor obstruction.

On four-dimensional Minkowski space in the constant-compensator phase, define

\[
\widehat h_{\mu\nu}
=h_{\mu\nu}+2\frac{\varphi}{v}\eta_{\mu\nu}.
\]

Under

\[
\delta_\sigma h_{\mu\nu}=2\sigma\eta_{\mu\nu},
\qquad
\delta_\sigma\varphi=-v\sigma,
\]

the field \(\widehat h\) is Weyl invariant.  It retains the ordinary
linearized diffeomorphism transformation.

Let \(G^{(1)}\) and \(B^{(1)}\) be the linearized Einstein and geometric Bach
tensors.  Exact tensor algebra gives

\[
B^{(1)}_{\mu\nu}=Q(G^{(1)})_{\mu\nu},
\]

where

\[
Q(S)_{\mu\nu}
=\frac12\Box S_{\mu\nu}
-\frac16(\eta_{\mu\nu}\Box-\partial_\mu\partial_\nu)S^\rho{}_\rho.
\]

The identities

\[
\partial^\mu G^{(1)}_{\mu\nu}=0,
\qquad
\partial^\mu B^{(1)}_{\mu\nu}=0,
\qquad
B^{(1)\mu}{}_{\mu}=0
\]

hold exactly.  In TT gauge this reduces to

\[
G^{(1)}(h^{TT})=-\frac12\Box h^{TT},
\qquad
B^{(1)}(h^{TT})=-\frac14\Box^2h^{TT},
\]

matching the earlier reduced certificates.

## Same-source obstruction

Use the linearized Einstein--Weyl equation

\[
c_1G^{(1)}(\widehat h)+2\alpha B^{(1)}(\widehat h)=T.
\]

The conventional same-source Einstein equation is

\[
c_1G^{(1)}(\widehat h)=T.
\]

An Einstein solution solves the Einstein--Weyl equation with the same source
if and only if

\[
\boxed{Q(T)=0.}
\]

Indeed, substituting \(G^{(1)}=T/c_1\) gives

\[
B^{(1)}=\frac1{c_1}Q(T).
\]

This condition is not implied by stress-tensor conservation or by the Weyl
trace Ward identity.  For the exact Fourier-symbol witness

\[
p_\mu=(1,0,0,0),
\qquad
T_{\mu\nu}=\operatorname{diag}(0,1,-1,0),
\]

one has

\[
p^\mu T_{\mu\nu}=0,
\qquad
T^\mu{}_{\mu}=0,
\qquad
Q(T)=\frac12T\ne0.
\]

Therefore arbitrary same-source Einstein truncation is refuted already at
linearized flat level.  This does not refute compatible restricted sources.
It identifies their exact local admissibility equation.

## Gauge-covariant defect

Define

\[
\Delta_{\mu\nu}
=G^{(1)}_{\mu\nu}(\widehat h)-\frac1{c_1}T_{\mu\nu}.
\]

The Einstein--Weyl equation implies

\[
(c_1I+2\alpha Q)\Delta
=-\frac{2\alpha}{c_1}Q(T).
\]

Thus zero defect propagates homogeneously only for compatible sources.  In the
reduced TT normalization

\[
D(D+M^2)h=J,
\qquad
M^2=\frac{c_1}{\alpha},
\]

the source-relative defect

\[
\delta=Dh-\frac{J}{M^2}
\]

obeys

\[
(D+M^2)\delta=-\frac{DJ}{M^2}.
\]

This recovers the tensor condition as \(DJ=0\) in the TT channel.

## Source Ward identities

With convention

\[
\delta S_{\rm source}
=\int\left(\frac12T^{\mu\nu}\delta g_{\mu\nu}
+J_\phi\delta\phi\right),
\]

Diff x Weyl covariance requires

\[
\nabla_\mu T^\mu{}_{\nu}=J_\phi\partial_\nu\phi,
\qquad
T^\mu{}_{\mu}-\phi J_\phi=0.
\]

On the constant frame these become conservation and
\(T^\mu{}_{\mu}=vJ_\phi\).  A traceful metric source with no compensator source
is not a valid Weyl-covariant source multiplet.

These Ward identities are necessary, but the explicit counterexample proves
that they do not replace \(Q(T)=0\).

## Affine sector versus BV subcomplex

For fixed nonzero external \(T\), the solution set of \(Lh=T\) is an affine
translate of \(\ker L\).  It is not closed under addition and is therefore not
a linear BV subcomplex.

The correct terminology is:

> affine same-source Einstein sector.

A genuine sourced BV subcomplex requires dynamical matter fields, any matter
gauge ghosts, antifields, equations, and the full Diff x Weyl Ward identities.
It must be built on a separately certified compensated quadratic BV complex.
The existing pure-Weyl free BV certificate is not that object.

## Dressed-source alternative

For an Einstein source \(T_E\), the local higher-derivative source

\[
T_{EW}=T_E+\frac{2\alpha}{c_1}Q(T_E)
\]

makes the same Einstein solution satisfy the Einstein--Weyl equation.  This is
an exact construction, but it changes the source coupling.  It must not be
reported as conventional same-source Einstein equivalence.

## Revised E-D2 sequence

1. Certify the local quadratic minimal BV complex: Hessian, gauge maps, ghosts,
   antifields, Noether rows, nilpotency, cyclicity, and the Weyl Stueckelberg
   contraction.  This is now complete in
   `notes/conformal-compensated-quadratic-minimal-bv.md`.
2. Export the actual minimal BV operators and certify a declared exact
   cohomology result kind.  The nonzero representative fibers are now complete
   in `notes/conformal-compensated-nonzero-characteristic-snapshot.md`, with
   inclusions, projections, homotopies, and momentum-reversing odd BV
   pairings.  The global freeze remains open at the covariant-bundle and zero
   mode gates.
3. Lift \(\Delta\) to the universal external-source Ward complex and classify
   its compatible kernel.  This is now complete in
   `notes/conformal-compensated-sourced-defect-chain-map.md`: both Ward squares,
   the sourced residual identity, and exact representative source kernels are
   certified.
4. Select a dynamical matter action and prove that its full BV complex maps to
   the universal source Ward complex.  External spurions are not themselves a
   matter BV theory.
5. Construct retarded and advanced defect propagation on declared spaces.
6. Compute the first nonlinear obstruction and only then pass to null infinity
   and scattering.

The target is explicitly disjunctive: construct a same-source sector on a
precise admissible class, or issue a scoped no-go.  Do not assume generic
matter closure.

Machine certificate:
`bridge/certificates/compensated_einstein_sourced_defect_preflight.json`.
