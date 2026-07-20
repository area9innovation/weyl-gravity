# Closed-\(S^3\) compact Gauss and relative-clock structure theorem

## Result

For \(n\) smooth homogeneous complex scalars and \(r\) compact Abelian gauge
generators, let

\[
Q\in {\rm Mat}_{n\times r}(\mathbb Z),
\qquad
k={\rm rank}_{\mathbb Q}Q .
\]

On a closed source-free \(S^3\), the integrated Gauss law is

\[
\boxed{Q^Tp=0.}
\]

It sets the total compact gauge charge to zero. It does **not** set all phase
momenta or phase velocities to zero. For positive phase inertia \(M\),

\[
\boxed{
\text{a nonzero healthy gauge-invariant relative clock exists}
\iff n-k>0 .
}
\]

Thus positivity permits neutral relative clocks. An indefinite cancellation,
boundary flux, or external source is not needed for that purpose. A boundary
or external source is needed only to support nonzero total scalar gauge charge
instead of a neutral relative motion.

This corrects the invalid extrapolation

```text
one charged field is killed by Gauss
  => every many-field phase clock is killed by Gauss.
```

## Declared two-derivative class

Write

\[
\Phi_i=\rho_i e^{i\theta_i},
\qquad
v=\dot\theta+QA_0.
\]

The most general homogeneous phase block of a gauge-invariant two-derivative
sigma model has the form

\[
L_{\rm phase}
=\operatorname{Vol}(S^3)
\left[
\frac12v^TMv+\dot\rho^TCv
-V(\rho,\psi)
\right],
\]

where \(M=M^T\), the coefficients may depend smoothly on gauge invariants, and
the omitted radial and Abelian field-strength terms do not change the
integrated constraint. The phase momentum is

\[
p=Mv+C^T\dot\rho.
\]

Varying \(A_0\) gives the local Abelian Gauss equation. Its divergence term
integrates to zero because \(\partial S^3=\varnothing\), hence \(Q^Tp=0\).
Also,

\[
H^2(S^3,\mathbb Z)=0,
\]

so a smooth Abelian bundle supplies no hidden magnetic topological term that
would change this integrated source-free statement.

For the fixed-modulus clock sector, \(\dot\rho=0\), and \(p=Mv\).

Moving moduli do not change the relative-direction count. In general,

\[
v_0=-M^{-1}C^T\dot\rho
\]

gives \(p=0\), and every Gauss solution is

\[
v=v_0+h,
\qquad
h\in\ker(Q^TM).
\]

The radial motion shifts the affine origin of the phase velocities while the
homogeneous relative-clock directions still have dimension \(n-k\). The full
positive sigma-model quotient below treats their kinetic mixing.

## Exact charge-lattice quotient

Smith normal form gives

\[
UQV=
\operatorname{diag}(d_1,\ldots,d_k,0),
\qquad
0<d_1\mid\cdots\mid d_k ,
\]

with integral unimodular \(U,V\). Therefore:

- the continuous gauge rank is \(k\);
- the continuous gauge reducibility is \(r-k\);
- when \(k=r\), the finite kernel has order \(\prod_i d_i\);
- the effective torus action is faithful exactly when \(k=r\) and every
  \(d_i=1\);
- the relative-character lattice is
  \[
  L=\ker_{\mathbb Z}(Q^T),
  \qquad
  {\rm rank}_{\mathbb Z}L=n-k.
  \]

The continuous gauge-invariant relative-phase space consequently has
dimension \(n-k\). Nonprimitive Smith factors change finite isotropy, not this
dimension.

SNF classifies the compact gauge homomorphism. It does not by itself identify
kinetic matrices or potentials unless those tensors are carried through the
same integral field-basis transformation.

## Necessary and sufficient clock conditions

Let \(N\) be a primitive integer basis matrix for

\[
\ker_{\mathbb Z}(Q^T),
\]

and define relative characters

\[
\psi=N^T\theta.
\]

For a proposed fixed-modulus velocity \(v\), the exact conditions are

\[
Q^TMv=0
\]

for zero total gauge charge, and

\[
N^Tv\ne0
\]

for nontrivial relative motion. The second condition is equivalent to

\[
v\notin{\rm im}_{\mathbb R}Q.
\]

If \(M>0\), then

\[
\ker(Q^TM)=({\rm im}\,Q)^{\perp_M}
\]

and its intersection with \({\rm im}\,Q\) is zero. Its dimension is \(n-k\).
This proves the boxed criterion.

There are also exact componentwise criteria. For a selected set of field
indices \(S\):

\[
\exists v\in\ker(Q^TM),\quad v_i\ne0\ \forall i\in S
\]

if and only if

\[
e_i\notin{\rm im}_{\mathbb R}(MQ)
\quad\forall i\in S.
\]

Likewise,

\[
\exists p\in\ker(Q^T),\quad p_i\ne0\ \forall i\in S
\]

if and only if

\[
e_i\notin{\rm im}_{\mathbb R}Q
\quad\forall i\in S.
\]

The proof is finite-dimensional: each forbidden zero component is a proper
hyperplane precisely when the corresponding coordinate functional is
nonzero on the constraint kernel, and a finite union of proper real
hyperplanes cannot cover that kernel.

## Reduced positive kinetic form

Gauss implies

\[
p=N\Pi.
\]

At fixed moduli,

\[
v=M^{-1}N\Pi
\]

and therefore

\[
\dot\psi
=N^TM^{-1}N\Pi
=A\Pi,
\qquad
A=N^TM^{-1}N .
\]

The exact reduced metric is

\[
\boxed{
G_{\rm rel}
=
\left(N^TM^{-1}N\right)^{-1}.
}
\]

Indeed, for \(z\ne0\),

\[
z^TAz=(Nz)^TM^{-1}(Nz)>0,
\]

so \(A\) and \(G_{\rm rel}\) are positive definite whenever \(M\) is.

For nonsingular declared-indefinite \(M\), the same formula applies when
\(A\) is nonsingular. The relative sector is healthy only when \(A>0\).
An indefinite cancellation that merely solves Gauss is not called healthy.
If \(A\) is singular, an additional Dirac reduction is required and this
certificate emits no health claim.

The full sigma-model statement is the familiar quotient metric. If \(G\) is
the field-space kinetic form and the gauge Killing matrix is \(K=(0,Q)\),
then, when the vertical Gram matrix is invertible,

\[
P_G
=
1-K(K^TGK)^{-1}K^TG
\]

is the horizontal projector. A positive \(G\) induces a positive quotient
metric.

The machine checks this beyond a block-diagonal phase model with the exact
mixed fixture

\[
G=
\begin{pmatrix}
2&\frac12&0\\
\frac12&3&\frac13\\
0&\frac13&4
\end{pmatrix},
\qquad
K=
\begin{pmatrix}0\\1\\1\end{pmatrix},
\qquad
K^TGK=\frac{23}{3}.
\]

For the generated rational projector it verifies independently

\[
P_G^2=P_G,\qquad
P_GK=0,\qquad
K^TGP_G=0,\qquad
GP_G=P_G^TG,
\]

and exact positive definiteness of both \(G\) and the two-dimensional
horizontal pullback.

## Exact witnesses

### Two charged fields: genuine counterflow

Take

\[
Q=
\begin{pmatrix}1\\1\end{pmatrix},
\qquad
M=
\begin{pmatrix}2&0\\0&3\end{pmatrix},
\qquad
N=
\begin{pmatrix}1\\-1\end{pmatrix}.
\]

With \(\Pi=1\),

\[
p=
\begin{pmatrix}1\\-1\end{pmatrix},
\qquad
v=
\begin{pmatrix}\frac12\\-\frac13\end{pmatrix}.
\]

Then

\[
Q^Tp=0,
\qquad
\dot\psi=\frac56,
\qquad
G_{\rm rel}=\frac65,
\]

and both phase momenta and velocities are nonzero. The exact kinetic energy
agrees before and after reduction:

\[
\frac12p^TM^{-1}p
=
\frac12G_{\rm rel}\dot\psi^2
=
\frac5{12}.
\]

This is a healthy positive counterflow, not an indefinite cancellation.

### One charged plus one neutral field

For

\[
Q=
\begin{pmatrix}1\\0\end{pmatrix},
\qquad
M=\operatorname{diag}(2,3),
\]

Gauss sets \(p_1=0\) but leaves \(p_2\). With \(p=(0,1)^T\),

\[
\dot\theta_2=\frac13,
\qquad
G_{\rm rel}=3.
\]

This is the exact compact-charge mechanism seen in the terminal two-field
preflight.

### Three fields and two gauges

For

\[
Q=
\begin{pmatrix}
1&0\\
0&1\\
1&1
\end{pmatrix},
\qquad
N=
\begin{pmatrix}-1\\-1\\1\end{pmatrix},
\qquad
M=\operatorname{diag}(2,3,5),
\]

the relative dimension is one and

\[
G_{\rm rel}=\frac{30}{31}>0.
\]

The result is not peculiar to a single \(U(1)\).

## Potential and dynamical realization

Gauge invariance permits phase Fourier characters only from
\(\ker_{\mathbb Z}(Q^T)\). Arbitrary nonzero reduced initial velocity defines
a local evolving solution of the reduced regular mechanical system.

A uniform helical background

\[
\psi(t)=\psi_0+wt
\]

requires more: \(w\) must generate a continuous symmetry of the reduced
potential, with the transverse coordinates at a critical point. A
phase-independent potential supplies this condition. The structure theorem
does not claim that every gauge-invariant potential admits uniform rotation
or that a compact phase is a globally monotone clock for all time.

## Raw \(D\) and \(K_{\rm Berger}\) phase moment maps

On the Gauss surface,

\[
\Theta_{\rm phase}
=
\operatorname{Vol}(S^3)p^T\delta\theta
=
\operatorname{Vol}(S^3)\Pi^T\delta\psi.
\]

For a stationary background with phase velocity \(\bar v\),

\[
\delta H_D^{\rm phase}
=
\operatorname{Vol}(S^3)\bar v^T\delta p
=
\operatorname{Vol}(S^3)\dot{\bar\psi}^{\,T}\delta\Pi.
\]

The expression is gauge invariant because

\[
(\bar v+Q\lambda)^Tp-\bar v^Tp
=
\lambda^TQ^Tp
=0.
\]

If \(w=\dot{\bar\psi}\) generates a continuous relative rotation \(R_w\) of
the potential, the stabilizer

\[
K_{\rm Berger}=D-R_w
\]

has zero phase-sector moment-map variation:

\[
\delta H_{K_{\rm Berger}}^{\rm phase}=0.
\]

This is only the phase-sector contribution. No full gravitational
\(K_{\rm Berger}\) moment map, pairing or causal carrier follows.

## Sources and boundaries

With the sign convention frozen in the certificate, the integrated equation
is

\[
Q^TP_{\rm phase}+q_{\rm external}
=
\Phi_{\partial\Sigma}.
\]

On closed \(S^3\), \(\Phi_{\partial\Sigma}=0\). External charge may therefore
permit nonzero scalar gauge charge only by exact total cancellation. On a
manifold with boundary, electric boundary flux can carry the mismatch.

Neither modification is necessary for a neutral relative clock. They matter
only if the desired sector has nonzero total gauge charge or if
\(n-\operatorname{rank}Q=0\).

## Programme consequence

The compact-Gauss question is now structurally closed for the declared
finite homogeneous two-derivative class:

\[
\boxed{
\text{reject a many-field clock only after reducing the charge lattice and
the positive quotient metric.}
}
\]

The one-field obstruction remains correct. The two-field preflight remains
terminal because its independent scale/trace and kinetic requirements fail,
not because compact Gauss forbids its neutral relative phase.

No model-specific full-BV or causal successor is activated by this theorem.
A successor still needs a selected action that independently passes the
scale/trace gate.

EVIDENCE: `d_quotient_classical/receipts/CLOSED_S3_GAUGED_CLOCK_GAUSS_STRUCTURE_THEOREM_V1_TIER_RECEIPT.json`

CLOSE-OUT: DONE — zero total compact charge is classified exactly and healthy
positive relative clocks survive precisely when
\(n-\operatorname{rank}Q>0\).
