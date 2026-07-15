# Flat compensated quadratic minimal BV complex

## Theorem

On four-dimensional Minkowski space, take the constant-compensator phase

\[
g_{\mu\nu}=\eta_{\mu\nu},
\qquad
\phi=v\ne0,
\qquad
\lambda=0.
\]

Write

\[
\rho=\frac{\varphi}{v},
\qquad
\widehat h_{\mu\nu}
=h_{\mu\nu}+2\rho\eta_{\mu\nu}.
\]

The local field map

\[
F:(h,\varphi)\longmapsto(\widehat h,\rho)
\]

has determinant \(1/v\).  It is invertible precisely on the declared
\(v\ne0\) chart.  The linearized gauge transformations become

\[
\delta_\xi\widehat h_{\mu\nu}
=2\partial_{(\mu}\xi_{\nu)},
\qquad
\delta_\sigma\widehat h_{\mu\nu}=0,
\qquad
\delta_\sigma\rho=-\sigma.
\]

Thus the compensator coordinate is an algebraic Weyl Stueckelberg doublet,
while the invariant metric retains only the diffeomorphism gauge action.

The quadratic metric Euler operator is

\[
K_{EW}h=c_1G^{(1)}(h)+2\alpha B^{(1)}(h).
\]

The exact quadratic action factors as

\[
S^{(2)}
=\frac12\langle\widehat h,K_{EW}\widehat h\rangle.
\]

No independent \(\rho\) Hessian remains.

## Pairing and formal adjoint

The symmetric-tensor pairing is

\[
\langle h,k\rangle=h_{\mu\nu}k^{\mu\nu}.
\]

In the ten independent-component basis, off-diagonal entries therefore have
multiplicity two and carry the Lorentzian signs induced by
\(\eta=\operatorname{diag}(1,-1,-1,-1)\).  The certificate constructs this
Gram matrix explicitly rather than using a naive Euclidean transpose.

On compactly supported test sections, the Fourier-symbol formal adjoint uses

\[
p_\mu\longmapsto-p_\mu.
\]

With this convention, the exact operator identities are

\[
K_{EW}R_{\rm diff}=0,
\qquad
R_{\rm diff}^{\dagger}K_{EW}=0,
\qquad
K_{EW}^{\dagger}=K_{EW}.
\]

## Minimal BV complex

The chain degrees follow the repository convention:

| Degree | Coordinates |
|---:|---|
| `-1` | four diffeomorphism ghosts and one Weyl ghost |
| `0` | ten components of \(\widehat h\) and \(\rho\) |
| `1` | their eleven antifields |
| `2` | four diffeomorphism-ghost antifields and one Weyl-ghost antifield |

The total symbol complex has dimension 32.  Its three nonzero blocks are the
gauge map \(R\), Hessian \(H\), and the signed formal-adjoint Noether map.
Exact rational polynomial computation proves

\[
HR=0,
\qquad
R^TG_{\rm field}H=0,
\qquad
q^2=0.
\]

Let \(\Omega\) be the explicit full-rank BV pairing.  The differential is
formally cyclic:

\[
q(-p)^T\Omega+\Omega q(p)=0.
\]

The rational off-shell fixture

\[
p=(2,1,0,0),
\qquad
c_1=-1,
\qquad
\alpha=-1
\]

has gauge rank five, Hessian rank six, and BV rank sixteen.  This checks the
generic algebraic block structure only; it is not an on-shell or residual
cohomology calculation.

## Weyl-doublet contraction

In invariant variables the Weyl coordinates are

\[
(c_W,\rho,\rho^*,c_W^*).
\]

Their differential and homotopy are

\[
q c_W=-\rho,
\qquad
q\rho^*=c_W^*,
\qquad
s\rho=-c_W,
\qquad
s c_W^*=\rho^*.
\]

Deleting these four coordinates gives the 28-dimensional minimal
Einstein--Weyl metric--diffeomorphism complex.  With inclusion \(i\),
projection \(\pi_{cl}\), and homotopy \(s\), the certificate proves

\[
\pi_{cl}i=1,
\qquad
i\pi_{cl}=1-qs-sq,
\]

together with

\[
s^2=0,
\qquad
si=0,
\qquad
\pi_{cl}s=0,
\qquad
qi=iq_{red},
\qquad
\pi_{cl}q=q_{red}\pi_{cl}.
\]

The BV pairing restricts nondegenerately to the reduced complex.  Therefore

\[
\boxed{
\text{compensated minimal BV}
\simeq
\text{Einstein--Weyl Diff minimal BV}
\oplus
\text{contractible Weyl doublet}
}
\]

on the flat \(v\ne0\) chart.

## Boundary ledger

The action representative is

\[
S_W+\int\sqrt{-g}\,\zeta
(\phi^2R-6\phi\Box\phi).
\]

Its integrated bulk form uses

\[
\zeta(\phi^2R+6\partial_\mu\phi\partial^\mu\phi)
\]

and differs by

\[
-6\zeta\nabla_\mu(\phi\nabla^\mu\phi).
\]

Compact support permits this divergence to be dropped in the formal-adjoint
calculation.  It remains in the ledger because a later BFV or boundary-current
theorem must restore it.

## Lifecycle boundary

This result is deliberately named a local minimal BV certificate, not the
complete classical import freeze.  The following remain open:

- physical residual or on-shell cohomology and its pairing;
- global \(p=0\) Killing and cylinder residual modes;
- a gauge-fixed nonminimal complex;
- Green-hyperbolic and Hadamard data;
- a dynamical matter BV lift of the universal sourced-defect Ward chain map;
- null-infinity, scattering, and quantum constructions.

The canonical operator export and the first scoped characteristic result are
now complete in
`notes/conformal-compensated-nonzero-characteristic-snapshot.md`.  A separate
consumer verifies the actual sparse matrices without importing this
constructor.  Exact representative-frame contractions give cohomology
dimensions `(0,2,2,0)` on the nonzero null branch and `(0,5,5,0)` on the
second root, with nondegenerate momentum-reversing odd BV pairings.

That is a scoped symbol snapshot, not the global
`COMPENSATED_CLASSICAL_IMPORT_FREEZE`.  Covariant characteristic bundles,
global zero modes, the physical Cauchy/radiative pairing, the dynamical matter
BV lift of the defect map, and nonminimal causal data remain open.  The
universal external-source Ward/defect chain map is now certified separately;
what remains here is its model-dependent dynamical matter realization.

## Berger-clock coordination

The two Berger inputs pinned by this certificate establish:

- an exact positive-energy rotating scalar clock on a compact squashed Berger
  background;
- a nonzero conserved internal \(O(2)\) clock momentum.

They were fail-closed before a total-(D) verdict.  Since this certificate was
issued, the classical programme has additionally certified `D_GAUGE` on the
specific smooth fixed-coupling linearized Berger phase space, the
support-local cyclic clock SDR, and the complete coefficientwise cyclic
26-row retained minimal `q1`.  Nonminimal rows, the causal Green complex, and
nonlinear stability remain open.

The Einstein-side incidence theorem also proves that this particular Berger
background is neither Einstein, conformally Einstein, nor Einstein with the
same clock stress for any constant `kappa,Lambda`.  It is therefore a genuine
non-Einstein Weyl--matter branch rather than a background on which to embed an
Einstein tangent complex.

The Berger phase is a dynamical relational matter clock on a non-flat compact
background and uses the opposite metric-signature convention.  The coordinate
\(\rho\) in this theorem is a flat-phase Stueckelberg variable.  It is
contractible and supplies no relational time.  No Berger operator or sign
formula is inserted into the flat differential, and the newer scoped
`D_GAUGE` verdict does not alter this theorem's characteristic cohomology.

Machine certificate:
`bridge/certificates/compensated_quadratic_minimal_bv.json`.
