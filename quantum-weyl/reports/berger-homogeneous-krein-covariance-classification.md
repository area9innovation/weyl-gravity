# Homogeneous Berger Krein covariance classification

This theorem closes the finite homogeneous covariance question left by the
stationary complex-structure obstruction.  Its carrier is the exact
left-invariant \(80\)-row metric plus metric-antifield Cauchy graph at

\[
(\alpha_B,u,v)=(1,1,5),\qquad \rho^2=2.
\]

It is a `LOCAL-ALGEBRAIC`/`REDUCED-MODE` result.  In particular, ordinary
matrix positivity after forgetting the metric/antifield parity is only a
diagnostic; it is not a probability inner product on the graded BV carrier.

## Action pairing

Let the metric graph operator be

\[
P=K_2\partial_t^2+K_1\partial_t+K_0,
\]

and let \(S\) exchange its two ten-row graph summands.  The separately
exported metric-antifield graph obeys

\[
K_2^\star=SK_2^TS,\qquad
K_1^\star=-SK_1^TS,\qquad
K_0^\star=SK_0^TS.
\]

The action Lagrange current therefore has the exact Cauchy matrix

\[
B=
\begin{pmatrix}
SK_1&SK_2\\
-SK_2&0
\end{pmatrix},
\qquad
A_\star^TB+BA=0.
\]

The machine finds \(\operatorname{rank}B=40\).  On the doubled carrier this
gives the nondegenerate invariant forms

\[
\Omega=
\begin{pmatrix}
0&-B^T\\
B&0
\end{pmatrix},
\qquad
G=
\begin{pmatrix}
0&B^T\\
B&0
\end{pmatrix}.
\]

Here \(\Omega\) is antisymmetric, while \(G\) is symmetric with inertia
\((40,40)\).

## Complete stationary matrix class

Every real stationary symmetric form solves

\[
A_{80}^T\mu+\mu A_{80}=0.
\]

The independently assembled exact \(3240\times3240\) Lyapunov matrix has
rank \(3112\), hence the solution space has dimension \(128\).  Every
Hermitian stationary normalized CCR matrix is consequently

\[
W(\mu)=\mu+\frac{i}{2}\Omega
\]

for one of those \(128\) parameters.

The exact primary/Jordan decomposition gives the positive-semidefinite
subcone as

\[
\operatorname{Sym}^+_2(\mathbb R)
\times\bigl(\operatorname{Herm}^+_2(\mathbb C)\bigr)^3
\times\bigl(\operatorname{Herm}^+_4(\mathbb C)\bigr)^5.
\]

Its linear span has dimension \(95\), its maximum real rank is \(54\), and
every member has a radical of dimension at least \(26\).  The lost
directions are precisely the non-imaginary primaries and the nilpotent images
of the zero and frequency-\(4\) Jordan primaries.

This forces a sharp result.  If \(W(\mu)\) were positive, any nonzero vector
in the forced radical of \(\mu\) would have zero \(W\)-norm.  Positivity
would then imply \(Wv=0\), hence \(\Omega v=0\), contradicting
\(\operatorname{rank}\Omega=80\).  Thus the stationary positive normalized
CCR class is empty.

There is nevertheless a canonical stationary normalized Krein functional,

\[
W_K=\frac12(G+i\Omega),
\]

which is nondegenerate and has inertia \((40,40)\).  The entire indefinite
class is the \(128\)-parameter affine family above; its inertia is
determinantally stratified rather than constant.

## Nonstationary alternative

With

\[
T=\operatorname{diag}(B,I_{40}),\qquad
\Omega=T^TJ_0T,
\]

the Cauchy-time choice

\[
W_0=\frac12(T^TT+i\Omega)
\]

is a positive, rank-\(40\), pure finite-dimensional covariance.  Its exact
evolution

\[
W_t=e^{tA_{80}^T}W_0e^{tA_{80}}
\]

preserves positivity, purity and the CCR, but is not stationary.  This
separates the available time-dependent option from the obstructed stationary
one.

No wavefront set or Hadamard condition exists on this finite homogeneous
block.  The corrected \(q_{\rm Cauchy}\), full \(104\)-row Cauchy pairing,
BRST Ward identity and physical quotient remain absent.  Accordingly this
result is not a full BV Hadamard state, physical positivity, a QME theorem,
or a particle/scattering/unitarity statement.

Machine-readable evidence:

- `quantum-weyl/lorentzian/certificates/BERGER_HOMOGENEOUS_KREIN_COVARIANCE_CLASSIFICATION.json`
- `quantum-weyl/lorentzian/generated/berger_homogeneous_krein_covariance_classification/classification_summary.json`

CLOSE-OUT: CERTIFIED — the complete parity-forgotten homogeneous stationary
CCR affine class has 128 parameters and no positive member; the canonical
Krein representative has inertia \((40,40)\), while positive pure
finite-dimensional covariances require explicit time dependence.

EVIDENCE:
`quantum-weyl/lorentzian/certificates/BERGER_HOMOGENEOUS_KREIN_COVARIANCE_CLASSIFICATION.json`
