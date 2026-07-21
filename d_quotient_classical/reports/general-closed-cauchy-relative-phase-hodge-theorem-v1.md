# General closed-Cauchy relative-phase Hodge/Gauss theorem

## Result

The round-
\(S^3\) nonhomogeneous relative-phase theorem extends to every connected,
closed, oriented smooth Riemannian Cauchy three-manifold once the spectrum is
left as background data and the harmonic/integral sectors are retained.

For \(n\) fixed-modulus phases, \(r\) compact Abelian connections and integral
charge matrix

\[
Q:\mathbb Z^r\longrightarrow\mathbb Z^n,
\qquad k=\operatorname{rank}Q,
\]

each positive scalar Laplace eigenfunction carries exactly \(n-k\)
gauge-invariant relative-phase wave families.  If \(N\) spans
\(\ker Q^T\), their exact reduced kinetic form is

\[
G_{\rm rel}=(N^TM^{-1}N)^{-1}.
\]

For positive \(M\) and \(K\), this form is positive and healthy relative waves
exist on every positive scalar eigenspace if and only if

\[
n-\operatorname{rank}Q>0.
\]

This is a `LOCAL-ALGEBRAIC` and `REDUCED-MODE` structural theorem.  It is not a
support-local causal-parent theorem.

## Analytic hypotheses

The only infinite-dimensional analytic input is the standard smooth Hodge
theorem for a connected closed oriented Riemannian three-manifold \(X\):

\[
\Omega^1(X)
=d\Omega^0_\perp(X)\oplus\delta\Omega^2(X)\oplus\mathcal H^1(X).
\]

The scalar Laplacian has a simple constant eigenspace and discrete positive
eigenspaces \(E_\lambda\) of finite multiplicity \(m_\lambda\).  For
\(\lambda>0\),

\[
Y\longmapsto \frac{dY}{\sqrt\lambda}
\]

identifies \(E_\lambda\) with the exact one-form eigenspace.  Positive coexact
eigenspaces \(F_\nu\), with multiplicities \(t_\nu\), are independent
metric/topological data.  No round-sphere relation between \(\lambda\) and
\(\nu\) is assumed.

The harmonic sector has dimension

\[
\dim\mathcal H^1(X)=b_1(X)
\]

and contains the harmonic representatives of the integral large-gauge
lattice.

## Gauss reduction

The linearized constraint is

\[
Q^TM(\dot\theta-QA_0)+\delta K(\dot A-dA_0)=0.
\]

Integrating over a closed slice removes the codifferential term:

\[
Q^T\int_XM(\dot\theta-QA_0)\,\mathrm{vol}=0.
\]

For a normalized positive scalar eigenmode it becomes

\[
Q^TMv_\lambda+\sqrt\lambda\,K e_{L,\lambda}=0.
\]

Let \(T\) span \(\ker Q\), and choose an active complement \(S\).  The
\(K\)-orthogonal active lift is

\[
S_\perp
=S-T(T^TKT)^{-1}T^TKS.
\]

With

\[
K_a=S_\perp^TKS_\perp,
\qquad
V=(QS_\perp)^TM(QS_\perp),
\]

eliminating \(A_0\) gives

\[
K_L(\lambda)
=\left(K_a^{-1}+\lambda V^{-1}\right)^{-1},
\]

and longitudinal frequency operator

\[
\lambda I+K_a^{-1}V.
\]

The positive coexact one-form eigenspace has frequency operator

\[
\nu I+K^{-1}Q^TMQ.
\]

Thus each scalar eigenspace has \(m_\lambda(n-k)\) relative families and
\(m_\lambda k\) massive longitudinal families.  Each coexact eigenspace has
\(t_\nu k\) massive and \(t_\nu(r-k)\) massless Maxwell families.

The matter kernel \(\ker Q\) is not reducibility for nonconstant gauge
parameters: its exact connection modes are gauge/constraint directions, while
its coexact and harmonic connection modes remain physical Maxwell/Wilson
carriers.  Only constant parameters in \(\ker Q\) act trivially on the full
linearized carrier.

## Integral winding/Wilson quotient

Let the nonzero Smith invariants of \(Q\) be

\[
d_1\mid d_2\mid\cdots\mid d_k.
\]

For each free integral \(H^1\) generator, phase winding
\(w\in\mathbb Z^n\), harmonic connection coordinate
\(a\in\mathbb R^r\), and large gauge winding \(z\in\mathbb Z^r\) obey

\[
(w,a)\sim(w+Qz,a+2\pi z).
\]

Smith reduction gives the presentation-independent quotient

\[
\boxed{
\mathbb R^k\times\mathbb T^{r-k}
\times\mathbb Z^{n-k}
\times\prod_{i=1}^k\mathbb Z/d_i
}.
\]

Taking the \(b_1(X)\)-fold product gives:

- \(b_1k\) local active harmonic families;
- \(b_1(r-k)\) compact kernel-Wilson families;
- free relative winding rank \(b_1(n-k)\);
- the \(b_1\)-fold product of the finite Smith sectors.

The constant compact-gauge stabilizer is

\[
\ker(\mathbb T^r\to\mathbb T^n)
\cong
\mathbb T^{r-k}\times\prod_i\mathbb Z/d_i.
\]

The flat-connection group fits into

\[
0\to
H^1(X;\mathbb R)/H^1(X;\mathbb Z)_{\rm free}
\to H^1(X;\mathbb R/\mathbb Z)
\to \operatorname{Tor}H^2(X;\mathbb Z)
\to0.
\]

For nowhere-zero charged phases, admissible disconnected bundle sectors obey

\[
Qc=0\quad\text{in }H^2(X;\mathbb Z)^n.
\]

The certificate records the torsion kernel of this map.  The dynamical theorem
itself is linearized only in the trivial smooth bundle chart.

## Topological obstruction

The local real \(K\)-orthogonal active/kernel decomposition is not generally
an integral lattice decomposition.  It descends to a global product of Wilson
subtori only when \(\ker Q\cap\mathbb Z^r\) admits a primitive
\(K\)-orthogonal integral complement.  Without that extra datum, the local
mass split remains valid but a presentation-free global product

\[
\mathbb T^{kb_1}\times\mathbb T^{(r-k)b_1}
\]

is not certified.

This is the precise topological obstruction returned by the gate.  It does
not obstruct the local tangent-space Hodge/Gauss reduction or its mode counts.

## Zero modes and charge strata

The constant scalar mode independently gives

\[
Q^Tp_0=0,
\qquad
\dim\mathcal P_{\rm rel}=n-k,
\qquad
G_{\rm rel}=(N^TM^{-1}N)^{-1}.
\]

There is no exact connection partner at \(\lambda=0\).  Harmonic one-forms
are separate physical/global carriers and must not be erased as pure gauge.

If some field modulus vanishes, the phase chart changes.  The payload
enumerates every active-row support and recomputes the rank, Smith invariants,
relative dimension and compact stabilizer from \(Q_S\).  Inactive complex
fields require Cartesian variables, so the theorem does not silently continue
the phase description through those singular strata.

For nonsingular indefinite kinetic data, health is decided eigenspace by
eigenspace from

\[
G_{\rm rel},\qquad K,\qquad
K_a^{-1}+\lambda V^{-1}.
\]

Singular relative, vertical or Schur forms define a separate Dirac stratum and
receive no verdict.

## Round-\(S^3\) and homogeneous regressions

Only these inputs of the predecessor were round-\(S^3\)-specific:

- \(\lambda_\ell=\ell(\ell+2)/a^2\) and multiplicity
  \((\ell+1)^2\);
- \(\nu_\ell=(\ell+1)^2/a^2\), curl chirality, and total coexact
  multiplicity \(2\ell(\ell+2)\);
- \(b_1(S^3)=0\) and \(\operatorname{Tor}H^2(S^3;\mathbb Z)=0\).

The Hodge split, integrated Gauss identity, exact-mode normalization,
charge-rank decomposition and all finite matrix identities are general.  The
independent verifier substitutes the sphere spectrum into the general
formulas and reproduces the imported \(\ell=1\) fixture exactly.  It also
reconstructs the \(\lambda=0\) homogeneous quotient without consuming the
predecessor terminal verdict.

## Exact fixtures and independent rail

The payload contains three exact fixtures:

1. \(S^1\times S^2\), \(b_1=1\), two equal-charge phases;
2. flat \(T^3\), \(b_1=3\), rank-deficient two-gauge system with a neutral
   phase;
3. \(L(5,1)\), \(b_1=0\), \(\operatorname{Tor}H^2=\mathbb Z/5\), with
   nonprimitive charge \(2\).

The independent verifier imports no producer code.  It uses SymPy's integer
Smith-normal-form implementation rather than the producer's determinantal-
divisor algorithm, reconstructs the cellular Betti/torsion data, all reduced
matrices, compact stabilizers, winding counts and torsion-bundle kernels, and
checks a separate unimodular-presentation fixture.

The generated atlas fragment keeps causal, observational and quantum columns
at `NO_CERTIFIED_MAP`.  It does not identify these carriers with pure-Weyl
residual modes or particles.

## Claim boundary and next gate

This theorem does not select a model-specific local action, construct an
unreduced BV complex, produce support-local advanced/retarded Green operators,
prove nonlinear closure, couple gravity or the \(D\)-action, or establish
Hadamard, particle, scale-generation or quantum claims.

The next gate is to select one positive two-derivative scalar--\(U(1)\) action
and construct its unreduced support-local BV causal parent while retaining the
integral harmonic sector.

CLOSE-OUT: DONE — general closed-Cauchy Hodge/Gauss theorem, integral quotient, topological obstruction and fail-closed atlas complete.
EVIDENCE: d_quotient_classical/compensator/GENERAL_CLOSED_CAUCHY_RELATIVE_PHASE_HODGE_THEOREM_V1.json
