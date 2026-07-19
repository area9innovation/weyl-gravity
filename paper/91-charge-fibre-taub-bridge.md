# Pure-extra Taub obstruction and a balanced second-order extension in compact Weyl--Maxwell gravity

## Pure extra modes versus Einstein--extra mixtures

GPT-5.6.sol (OpenAI model)

The research programme was commissioned and directed by Asger Alstrup Palm
(`asger@area9.dk`), who initiated the questions, served as the non-technical
orchestrator and corresponding human contact, but claims no technical
contribution.

Working manuscript, 19 July 2026. The theorem-frozen scope is
`LOCAL-ALGEBRAIC` and `REDUCED-MODE`. Circulation remains conditional on the
documented final human review described below.

## Abstract

Linearized Weyl--Maxwell gravity on the compactified magnetically supported
Plebański--Hacyan universe contains the ordinary Einstein--Maxwell modes and
additional Weyl modes. We determine whether the additional generic modes are
tangent to nonlinear solutions on the fixed compact magnetic bundle. On the
closed Cauchy surface $S^1\times S^2$, the quadratic Taub pairing with a
background stabilizer equals the corresponding covariant Lee--Wald moment
map. The time-translation pairing is negative definite on the complete real
pure-extra generic sector, axial and polar, for every
$\ell\geq2$ and every allowed compact momentum. Consequently no nonzero
pure-extra generic tangent admits a fixed-bundle second-order extension.

This obstruction is not stable under mixing with the Einstein sector. The
Einstein primary has an indefinite time-translation form. At
$\ell=2,m=0,k=0$, an Einstein-minus mode and one extra mode have a unique
positive balancing ratio within their declared two-mode span, for which all
five background-stabilizer moment maps vanish. We compute its complete
quadratic Weyl--Maxwell source. The
homogeneous zero-frequency Einstein and extra sources cancel exactly; every
remaining homogeneous channel has an explicit correction; and every
$\ell=2,4$ output is removed by an exact off-shell polar inverse. The four
solved action equations and four target Noether identities span all eight
ungauged polar equations with determinant (-4), including at zero
frequency. Hence this balanced real tangent has an explicit spatially
periodic, finite quasiperiodic second-order correction on the same magnetic
bundle component.

The result exhibits a sharp nonlinear distinction:

\[
\boxed{
\text{pure extra generic mode: obstructed},\qquad
\text{balanced Einstein--extra mode: extendible to second order}.}
\]

The theorem concerns a formal second-order jet, not an exact family or an
all-orders solution. Post-freeze successor certificates now classify the
complete finite-harmonic generic $k=0$ zero cone, one fixed-$|k|$
opposite-momentum cone, and the full exceptional $\ell=1,k=0$ all-$m$ pure
cone. A further tuned nonzero-$k$, axisymmetric $\ell=2$ certificate
classifies the complete all-primary bounded cone on that declared fibre, and
the standard-branch resonance theorem now extends to every $\ell\geq2$ at
the corresponding tuning. A two-absolute-momentum workload has closed all
164 declared basis coefficients, but its arbitrary-amplitude zero variety
remains open. These results sharpen the frontier without changing Theorems A
and B below.

## 1. Introduction

Linearization stability asks whether a solution of the linearized field
equations is the first derivative of a family of exact solutions. On a
compact Cauchy surface, background symmetries can produce quadratic Taub
constraints which are invisible in the linear equations. This phenomenon is
classical in Einstein gravity and is naturally expressed through the
constraint-adjoint kernel or, equivalently on a closed slice, through the
moment map for the background symmetry group [2,10,11]. Higher-derivative
gravity has analogous linearization-instability questions [3].

The present problem is unusually clean because the linear phase space is
already known exactly. The background

\[
M=\mathbb R_t\times S^1_L\times S^2
\]

is a compactification of the magnetically supported Plebański--Hacyan direct
product [4]. With the normalization specified below, it solves both
Einstein--Maxwell and Weyl--Maxwell theory. The complete standard
Einstein--Maxwell harmonic tangent injects into the Weyl--Maxwell tangent,
while the latter contains two extra generic cyclic summands in each parity.
Those extra modes are genuine nonradical linear solutions; they are neither
Weyl-gauge representatives nor null directions of the Lee--Wald form. The
linear phase-space theorem and its conventions are established in the
companion paper [5].

The next question is nonlinear:

> Which of the certified extra linear modes satisfy the quadratic
> integrability constraints, and can an Einstein component cancel their
> obstruction?

We answer both parts at a sharp, publishable scope.

To our knowledge, no previous Weyl--Maxwell calculation combines a definite
all-harmonic obstruction on the new fourth-order primary with an exact
Einstein--extra cancellation and a complete second-order correction.

1. **General pure-extra no-go.** Every nonzero real pure-extra generic
   tangent is obstructed at second order on the fixed magnetic bundle. This
   holds for both parities, every physical $\ell\geq2$, every allowed
   compact momentum, and the completion of finite harmonic sums in the
   time-translation charge norm defined below.

2. **Explicit balanced extension.** One nonzero real Einstein--extra tangent
   at $\ell=2,m=0,k=0$ annihilates all five stabilizer moment maps and has a
   complete explicit second-order correction.

The contrast is the scientific point. The extra sector is not deleted from
the linear theory, nor is it generically promoted to a nonlinear branch.
Rather, the nonlinear solution locus has a singular tangent cone: a pure
extra direction fails the quadratic constraint, while an appropriately
balanced mixed direction passes and extends through second order.

This paper does **not** delay that conclusion until the entire indefinite
mixed cone is classified. The full common zero locus of
$\left(\mu_H,\mu_{P_x},\mu_{J_1},\mu_{J_2},\mu_{J_3}\right)$, including
opposite-momentum standing waves and exceptional/global blocks, is a
post-freeze successor programme summarized in Section 10.

### Main theorems

Let $\mathcal T_X^{\mathrm{gen}}$ be the real, locally gauge-reduced,
generic extra Weyl--Maxwell tangent on the fixed magnetic bundle, and let
$u_-$ and $u_e$ be the axisymmetric axial modes defined in Section 7.

> **Theorem A (definite pure-extra obstruction).** For every nonzero
> $u\in\mathcal T_X^{\mathrm{gen}}$,
> \[
> \mu_H(u)=-\frac L4\lVert u\rVert_H^2<0.
> \]
> Therefore the second-order Weyl--Maxwell equation has no solution on the
> fixed magnetic-bundle component $P_N$.

> **Theorem B (one balanced second-order jet).** Let
> \[
> a_e=\sqrt{\frac{27}{52}(5\sqrt3-6)}>0.
> \]
> The explicitly defined real $\ell=2,m=0,k=0$ Einstein--extra tangent
> annihilates all five background-stabilizer moment maps and admits a smooth,
> real, $S^1_L$-periodic in space and finite quasiperiodic in time
> second-order correction on the same bundle component.

Theorem A concerns the complete axial and polar pure-extra generic sector.
Theorem B is an existence theorem for one declared mixed tangent. It is not a
claim that every common-zero tangent extends.

## 2. The common background and the fixed magnetic-bundle component

We use signature $(-+++)$ and the actions

\[
S_{\mathrm{EM}}[g,A]
=\int_M\!\sqrt{-g}\left[
\frac{R-2\Lambda}{2\kappa}-\frac14F_{ab}F^{ab}\right]d^4x,
\]

\[
S_{\mathrm{WM}}[g,A]
=\int_M\!\sqrt{-g}\left[
\frac{\alpha_B}{8}C_{abcd}C^{abcd}-\frac14F_{ab}F^{ab}\right]d^4x.
\]

The Bach convention is

\[
\delta\!\int\sqrt{-g}\,C^2
=4\int\sqrt{-g}\,B_{ab}\,\delta g^{ab}+\text{boundary},
\]

so the Weyl--Maxwell metric equation is

\[
\alpha_BB_{ab}=T_{ab},
\qquad \nabla_aF^{ab}=0,
\qquad dF=0.
\]

The fixture is

\[
M=\mathbb R_t\times S^1_L\times S^2,
\qquad
d\bar s^2=-dt^2+dx^2+d\Omega_2^2,
\qquad
\bar F=\operatorname{vol}(S^2),
\]

with

\[
(\kappa,\Lambda,\alpha_B)=(1,\tfrac12,3).
\]

It lies on the intersection of the Einstein--Maxwell and Weyl--Maxwell
solution loci. This is an incidence relation between two theories, not a
Weyl gauge equivalence. The local geometry belongs to the direct-product
electrovacua studied by Plebański and Hacyan [4]. Exact wave families on
related direct-product universes are known [6,7]; their existence neither
implies nor is implied by the complete harmonic integrability statement
proved here.

The magnetic field is a connection curvature on a nontrivial compact
$U(1)$ bundle $P_N\to S^1\times S^2$. With the chosen normalization the
Chern number is $N=2$. A connection tangent $a=A-\bar A$ is a global
one-form on the fixed bundle, but a uniform continuous change of magnetic
flux changes the bundle family. We therefore define the nonlinear extension
problem on the fixed component $P_N$.

This distinction is load-bearing. If a formal second-order magnetic
coefficient is introduced,

\[
N(\epsilon)=2+2\epsilon^2p,
\]

then a smooth family on the same $N=2$ bundle has $p=0$. A calculation
which removes a Taub source by choosing $p\neq0$ solves a different,
charge-enlarged problem. Electric variation is allowed on fixed $P_N$, but
at the purely magnetic background its linear energy pairing vanishes and it
cannot absorb the pure-extra constant-lapse obstruction.

### Domain of the theorem

The theorem is made after local

\[
\mathrm{Diff}\ltimes\mathcal G_{\mathrm{Weyl}}
\ltimes\mathcal G_{U(1)}
\]

reduction, but before quotienting by the five background stabilizers

\[
H=\partial_t,\qquad P_x=\partial_x,\qquad J_1,J_2,J_3\in\mathfrak{so}(3).
\]

These stabilizers are retained because their Hamiltonians are the quadratic
constraints. Quotienting them before evaluating the moment map would erase
the very obstruction under study.

## 3. Linear input: Einstein and extra primary sectors

Write

\[
\lambda=\ell(\ell+1),\qquad
k=\frac{2\pi n}{L},\quad n\in\mathbb Z.
\]

For every $\ell\geq2$, the generic axial and polar Weyl--Maxwell solution
modules split into the Einstein $q$-primary image and two additional
$p$-primary summands. The axial statement is imported from the companion
linear paper [5]. Because the polar statement is load-bearing for Theorem A,
we record its complete algebraic and current certificate here rather than
importing it by name alone.

The extra shell is

\[
p(\omega,k,\lambda)
=\omega^2-k^2-\lambda+\frac23=0,
\]

so

\[
\omega_e^2=k^2+\lambda-\frac23>0.
\]

The Einstein shell polynomial is

\[
q(\omega,k,\lambda)
=(\omega^2-k^2)^2
-2\lambda(\omega^2-k^2)+\lambda(\lambda-2).
\]

Its two positive-frequency branches will be denoted $\omega_-$ and
$\omega_+$.

### 3.1 Polar module and current theorem

In the polar gauge slice and coefficient order $(A_t,B,C_t,U)$, the
action-normalized reduced Hessian is

\[
H_P=
\begin{pmatrix}
\frac{2k^4+4k^2\lambda+2\lambda^2-3\lambda}{4}
&k\omega(k^2+\lambda)
&\frac{k^2\lambda+2k^2\omega^2+\lambda^2-\lambda\omega^2+\lambda}{4}
&\lambda\\
k\omega(k^2+\lambda)
&-\frac{3k^2\lambda-4k^2\omega^2+3\lambda^2-3\lambda\omega^2-2\lambda}{2}
&-k\omega(\lambda-\omega^2)&0\\
\frac{k^2\lambda+2k^2\omega^2+\lambda^2-\lambda\omega^2+\lambda}{4}
&-k\omega(\lambda-\omega^2)
&\frac{2\lambda^2-4\lambda\omega^2-3\lambda+2\omega^4}{4}
&-\lambda\\
\lambda&0&-\lambda&-2\lambda(k^2+\lambda-\omega^2)
\end{pmatrix}.
\tag{3.1}
\]

The normalization follows from the four-dimensional first variation, with
row weights $(-1,2,-1,2\lambda)$ for the metric $00$, metric $01$, metric
$11$, and polar Maxwell-density equations. It is therefore not inferred from
formal self-adjointness alone.

Let $I_j(H_P)$ denote the ideal generated by the $j\times j$ minors. Over

\[
R_{\mathrm{phys}}^P=
\mathbb Q[\lambda,k,\lambda^{-1},(\lambda-2)^{-1},
(3\lambda-2)^{-1},(3\lambda-4)^{-1},(5\lambda+6)^{-1},
(9\lambda+2)^{-1},(9\lambda-2)^{-1}],
\]

where neither $k$, $\omega$, $p$, nor $q$ is inverted, exact Bézout
witnesses give

\[
I_1=(1),\qquad I_2=(1),\qquad I_3=(p),\qquad I_4=(p^2q).
\tag{3.2}
\]

The resultant

\[
\operatorname{Res}_{\omega}(p,q)=\frac4{81}(9\lambda-2)^2
\tag{3.3}
\]

is a unit on every physical fibre. After specialization to a physical
$(\ell,n)$ fibre, $K_{\ell,n}[\omega]$ is a PID and the specialized Fitting
ideals (3.2) give the Smith factors $1,1,p,pq$, including at $k=0$. No global
Smith normal form over the multivariate ring $R_{\mathrm{phys}}^P[\omega]$
is asserted. Fibrewise primary decomposition gives

\[
\mathcal T_{\mathrm{WM}}^{\mathrm{pol}}
\cong K_{\ell,n}[\omega]/(q)
\oplus\bigl(K_{\ell,n}[\omega]/(p)\bigr)^2.
\tag{3.4}
\]

Here $K_{\ell,n}$ is any characteristic-zero field containing the
specialized coefficients $\lambda=\ell(\ell+1)$ and $k=2\pi n/L$. The
Einstein solution map is injective, is annihilated by $q$, and has
$K_{\ell,n}$-dimension four. Since $q$ is a unit on the two $p$-primary
summands, its image equals the complete $q$-primary summand.

On the positive extra shell, define

\[
D=3k^2+3\lambda-2,\qquad \widetilde D=6k^2+3\lambda-2.
\]

Two explicit extra representatives are

\[
e_1=
\begin{pmatrix}4(3k^2-2)\\0\\-12(k^2+\lambda)\\3\widetilde D\end{pmatrix},
\qquad
e_2=
\begin{pmatrix}-2kD\\\omega_e\widetilde D\\-2kD\\0\end{pmatrix}.
\tag{3.5}
\]

Their direct four-dimensional Lee--Wald Hermitian current Gram matrix is

\[
G_X^{\mathrm{pol}}=
\begin{pmatrix}
18\lambda(4k^2+\lambda-2)(12k^2+9\lambda-2)
&-6k\lambda(3\lambda+2)D\\
-6k\lambda(3\lambda+2)D
&\frac12\lambda(3\lambda-2)^2D
\end{pmatrix}.
\tag{3.6}
\]

Its first principal minor is positive and

\[
\det G_X^{\mathrm{pol}}
=9\lambda^2(\lambda-2)(9\lambda-2)D\widetilde D^2>0
\tag{3.7}
\]

for every physical $\lambda\geq6$ and allowed $k$. Direct reduction of the
mixed current gives zero modulo $(p,q)$, so this block is orthogonal to the
Einstein primary.

> **Theorem 3.1 (generic polar linear input).** On every physical
> $\ell\geq2$ compact-momentum fibre, including $k=0$, the locally
> gauge-reduced polar target has the decomposition (3.4). Its two extra
> positive-frequency directions are nonradical, orthogonal to the Einstein
> primary, and have current inertia $(2,0)$.

Equations (3.1)--(3.7), together with the exact Bézout witnesses in the
machine-readable supplement, constitute the polar theorem used below. This
is an off-shell module and classical current result before the final
background-stabilizer quotient; it is not a causal, particle, or quantum
claim.

The Einstein and extra primary modules are therefore orthogonal under the
direct four-dimensional Lee--Wald current in both parities. Each axial and
polar extra Gram matrix $G_X^{\mathrm{par}}$ is positive definite. Thus the
extra modes are genuine nonnull linear solutions, even though Section 5
proves that they are not fixed-bundle nonlinear tangent directions.

For a positive-frequency coefficient vector $c$ in one branch, parity and
spin-$\ell$ multiplicity block, let $W_\ell$ be the positive invariant
angular Gram form. Reality fixes the negative-frequency and
negative-momentum coefficients by conjugation. We use

\[
\Phi=\operatorname{Re}(c e^{-i\omega t+ikx})
\]

as the real-mode convention.

## 4. Taub pairings as covariant moment maps

Let $E(\Phi)=0$ denote the Weyl--Maxwell Euler--Lagrange equations and
$L=DE|_{\bar\Phi}$. We fix the perturbative convention

\[
\Phi(\epsilon)=\bar\Phi+\epsilon u+\epsilon^2\Phi^{(2)}+O(\epsilon^3).
\tag{4.1}
\]

Thus a first-order tangent $Lu=0$ extends through second order only if

\[
L\Phi^{(2)}
=-\frac12D^2E|_{\bar\Phi}[u,u].
\tag{4.2}
\]

Let $\mathcal C_\Sigma(\Phi)=0$ be the complete nonlinear Weyl--Maxwell
constraint map obtained by the normal and tangential decomposition of the
Euler--Lagrange equations on the closed slice
$\Sigma=S^1_L\times S^2$. Write its source components as $S_A$. For a
background stabilizer $\widehat X$, let $\zeta_{\widehat X}^A$ be its element
of the constraint-adjoint kernel and define

\[
\langle\zeta_{\widehat X},S\rangle_\Sigma
:=\int_\Sigma \zeta_{\widehat X}^A S_A\,d\Sigma_{\bar h},
\tag{4.3}
\]

where $d\Sigma_{\bar h}$ is the background spatial volume measure and the
index contraction includes the metric and Maxwell constraint components in
the four-dimensional action convention of Section 2. Every adjoint zero mode
therefore gives the necessary Taub condition

\[
\left\langle\zeta_{\widehat X},
\frac12D^2\mathcal C_\Sigma|_{\bar\Phi}[u,u]
\right\rangle_\Sigma=0.
\tag{4.4}
\]

The stabilizers are automorphisms of the magnetic bundle, not merely vector
fields on the base. Time and circle translations lift with zero vertical
part. A sphere rotation is lifted as

\[
\widehat J_a=(J_a,\chi_a),
\qquad
\iota_{J_a}\bar F+d\chi_a=0.
\tag{4.5}
\]

Such a global lift exists because $\mathcal L_{J_a}\bar F=0$ and
$H^1(S^2)=0$. It preserves the background connection even though a chosen
local monopole potential need not be invariant. Write
$\widehat{\mathcal L}_{\widehat X}$ for the resulting combined
diffeomorphism--$U(1)$ action.

Let $\mathcal T_{\mathrm{WM}}$ be the smooth harmonic solution space after
local $\mathrm{Diff}\ltimes\mathcal G_{\mathrm{Weyl}}\ltimes
\mathcal G_{U(1)}$ reduction and before the five stabilizers are quotiented.
On every declared generic primary block, the Lee--Wald form
$\Omega_{\mathrm{WM}}$ is nondegenerate. The closed-slice Hamiltonian
identity is the following proposition.

> **Proposition 4.1 (Taub pairing equals the stabilizer moment map).** For
> every smooth finite-harmonic Jacobi field $u$ and every lifted background
> stabilizer $\widehat X$,

\[
\boxed{
\left\langle\zeta_{\widehat X},
\frac12D^2\mathcal C_\Sigma|_{\bar\Phi}[u,u]
\right\rangle_\Sigma
=\mu_{\widehat X}(u)
=\frac12\Omega_{\mathrm{WM}}
(u,\widehat{\mathcal L}_{\widehat X}u).}
\tag{4.6}
\]

To prove (4.6), differentiate the action Noether-current identity twice, use
$E(\bar\Phi)=0$, $Lu=0$, and
$\widehat{\mathcal L}_{\widehat X}\bar\Phi=0$, and then integrate over
$\Sigma$. The second variation of the constraint Hamiltonian gives the left
side of (4.6), while the variation of the Hamiltonian generator gives the
right side. The chosen expansion (4.1) supplies the factor $1/2$. Every exact
Lee--Wald improvement and bundle-patching corner term integrates to zero on
the closed slice. This proves the identity first for smooth finite harmonic
sums. Section 5 extends it by continuity in the charge norm. It is the
boundaryless specialization of the covariant phase-space construction
[8,9].

The exact real-mode moment maps are

\[
\mu_H
=-\frac{L}{4}\sum
\omega^2 c^\dagger(G_{\mathrm{branch}}\otimes W_\ell)c,
\tag{4.7}
\]

\[
\mu_{P_x}
=\frac{L}{4}\sum
k\omega c^\dagger(G_{\mathrm{branch}}\otimes W_\ell)c,
\tag{4.8}
\]

\[
\mu_{J_a}
=\frac{L}{4}\sum
\omega c^\dagger(G_{\mathrm{branch}}\otimes W_\ell T_a)c.
\tag{4.9}
\]

The sums are block diagonal in $k,\ell$, parity, and frequency shell.
Here

\[
T_a=-i\mathcal L_{J_a}\big|_{\mathcal H_\ell}
\tag{4.10}
\]

is the Hermitian angular-momentum matrix on the spin-$\ell$ harmonic space,
with Hermiticity taken relative to $W_\ell$. Thus
$T_3Y_{\ell m}=mY_{\ell m}$ and (4.9) is manifestly real. Rotations preserve
$\ell$; $T_3$ is diagonal in $m$, while $T_1,T_2$ connect only $m$ to
$m\pm1$. Axial--polar and
Einstein--extra cross terms vanish. The sign and the factor $1/4$ in (4.7)
are fixed by exact agreement with three independent direct tensor
calculations: one axial extra block and the axial and polar Einstein-minus
fixtures at $\ell=2,k=0$.

## 5. The complete pure-extra obstruction

For a finite real pure-extra harmonic sum, define the time-translation charge
norm

\[
\lVert u\rVert_H^2
:=\sum_{\ell,m,n,\mathrm{par}}
\omega_e^2\,
c_{\ell mn}^{\dagger}
(G_X^{\mathrm{par}}\otimes W_\ell)c_{\ell mn}.
\tag{5.1}
\]

Let $\mathscr H_X$ be the Hilbert completion of finite harmonic sums in this
norm. This is the precise infinite-superposition domain used here; no claim
about a larger PDE energy space is made.

> **Theorem 5.1 (pure-extra fixed-bundle no-go).** Every nonzero real
> pure-extra generic tangent $u\in\mathscr H_X$, axial or polar, satisfies
> $\mu_H(u)=-(L/4)\lVert u\rVert_H^2<0$. If, in addition, $u$ is represented
> in a regularity class in which the quadratic extension equation (4.2) is
> defined and the Taub pairing (4.3) is continuous, then $u$ admits no
> second-order correction on the fixed magnetic bundle $P_N$.

### Proof

On the extra shell, $\omega_e^2>0$ for every physical
$\lambda\geq6$. Both extra Gram matrices and the angular form $W_\ell$
are positive definite. Hence every nonzero block contributes strictly
negatively to (4.7):

\[
\mu_H(u)
=-\frac{L}{4}\sum_{\mathrm{extra\ blocks}}
\omega_e^2 c^\dagger(G_X^{\mathrm{par}}\otimes W_\ell)c<0.
\]

Thus $\mu_H(u)=-(L/4)\lVert u\rVert_H^2$. Proposition 4.1 and the moment map
extend continuously from finite sums to $\mathscr H_X$, and strict
negativity holds for every nonzero vector in the completion. Equation (4.4)
is therefore violated for the constant-lapse adjoint class.

The obstruction cannot be absorbed inside the declared domain. Continuous
magnetic variation changes $c_1(P_N)$, while electric variation has zero
linear pairing with $H$ at the purely magnetic background. Thus (4.2) has
no fixed-bundle solution. $\square$

### What the theorem does not say

The theorem does not remove the extra linear modes. Their Lee--Wald Gram
matrices are nondegenerate, so they remain genuine classical linear
solutions. The conclusion is instead that the exact fixed-bundle solution
locus is singular at the background: its formal tangent space is larger than
its second-order tangent cone.

Nor is this a quantum ghost statement. No positive-frequency Hilbert space,
BRST-compatible Hadamard state, or Lorentzian causal quantum construction is
used.

## 6. Why an Einstein component can cancel the obstruction

The Einstein $q$-primary contribution to $\mu_H$ is indefinite. In each
parity its two master branches contribute opposite signs in the target
current convention. Consequently a negative extra contribution can be
cancelled by an Einstein-minus component without invoking a mixed
Einstein--extra current entry. The cancellation is additive between two
orthogonal diagonal primary blocks.

There is nevertheless a useful same-momentum restriction.

> **Proposition 6.1 (one travelling block at nonzero momentum).** In a
> single fixed $k\neq0$ travelling block, simultaneous vanishing of
> $\mu_H$ and $\mu_{P_x}$ forces all Einstein-plus, Einstein-minus, and
> extra occupations to vanish.

Indeed, the three shell frequencies obey

\[
\omega_-<\omega_e<\omega_+.
\]

After eliminating the Einstein-minus occupation from the two scalar moment
maps, one obtains

\[
\omega_+(\omega_+-\omega_-)A_+
+\omega_e(\omega_e-\omega_-)A_e=0,
\]

where $A_+,A_e\geq0$ are Gram-normalized occupations. Both coefficients are
strictly positive, so $A_+=A_e=0$, and the remaining occupation then
vanishes as well. This proposition does not cover cancellations between
distinct momenta, such as standing-wave combinations.

At $k=0$, the momentum constraint vanishes automatically and a nontrivial
balance becomes possible.

## 7. The minimal balanced tangent

Fix the axial $\ell=2,m=0,k=0$ sector. In the coefficient order
$(H_t,H_x,Q_t,Q_x)$, choose the Einstein-minus representative

\[
u_-=(0,-2,0,2\sqrt3),
\qquad
\omega_-^2=6-2\sqrt3,
\tag{7.1}
\]

and the second extra representative

\[
u_e=(0,-\tfrac23,0,6),
\qquad
\omega_e^2=\frac{16}{3}.
\tag{7.2}
\]

For unit real cosine amplitude, their constant-lapse Taub coefficients are

\[
\tau_-=\frac{48}{5}(-6+5\sqrt3)>0,
\qquad
\tau_e=-\frac{832}{45}<0.
\tag{7.3}
\]

Fix the positive real balancing amplitude

\[
a_e
:=\sqrt{\frac{\tau_-}{-\tau_e}}
=\sqrt{\frac{27}{52}(5\sqrt3-6)}>0.
\tag{7.4}
\]

Then

\[
\Phi^{(1)}
=\operatorname{Re}(u_-e^{-i\omega_-t})
+a_e\operatorname{Re}(u_ee^{-i\omega_et})
\tag{7.5}
\]

is nonzero and satisfies

\[
\mu_H=\mu_{P_x}=\mu_{J_1}=\mu_{J_2}=\mu_{J_3}=0.
\tag{7.6}
\]

Here $\mu_H=0$ follows from (7.3)--(7.4), $\mu_{P_x}=0$ from $k=0$,
and the rotational expectations vanish for the separate axisymmetric
$m=0$ states. Because the Einstein and extra primaries are symplectically
orthogonal, (7.6) is not produced by an interference term.

The declared theorem concerns this positive-real relative phase. Moreover,

\[
\left(\frac{\omega_e}{\omega_-}\right)^2
=\frac43+\frac{4\sqrt3}{9}\notin\mathbb Q,
\tag{7.7}
\]

so the mixed tangent is not periodic in time. It is smooth and periodic in
$x\in S^1_L$, and its time dependence is a finite quasiperiodic sum.

Vanishing Taub charges is necessary but not sufficient for extension. A
nonzero quadratic source can still have a component in another adjoint
cokernel or lie on a resonant output shell. We therefore solve the complete
second-order equation directly.

## 8. Complete second-order extension of the balanced tangent

> **Theorem 8.1 (balanced Einstein--extra second-order extension).** The real
> tangent (7.5), with the positive real amplitude (7.4), admits a smooth,
> real correction $\Phi^{(2)}$ which is $S^1_L$-periodic in space and a
> finite quasiperiodic sum in time on the same fixed magnetic-bundle
> component. It satisfies
> \[
> L_{\mathrm{WM}}\Phi^{(2)}
> =-\frac12D^2E_{\mathrm{WM}}
> [\Phi^{(1)},\Phi^{(1)}].
> \tag{8.1}
> \]

### 8.1 Selection rules and real-mode factors

The product of two axial $\ell=2,m=0$ harmonics is polar and contains only

\[
\ell_{\mathrm{out}}=0,2,4.
\]

The time dependence produces the five channel types

| Channel | Output frequency |
|---|---:|
| Einstein self-sum | $2\omega_-$ |
| extra self-sum | $2\omega_e$ |
| cross-sum | $\omega_e+\omega_-$ |
| cross-difference | $\omega_e-\omega_-$ |
| conjugate self-products | (0) |

For $\Phi=\operatorname{Re}z=(z+\bar z)/2$ and symmetric Hessian $B$,

\[
\frac12B(\Phi,\Phi)
=\frac18B(z,z)+\frac14B(z,\bar z)
+\frac18B(\bar z,\bar z).
\]

Thus self-sums carry factor $1/8$, while self-zero, cross-sum, and
cross-difference terms carry factor $1/4$. These factors are replayed
symbolically in the certificate rather than inserted as conventions after
the calculation.

### 8.2 The exceptional homogeneous channel

In homogeneous coefficient order $(C,K,U)$, the directly computed linear
operator on rows $(E_{00},E_{11},E_{22},M_1)$ is

\[
L_0(\Omega)=
\begin{pmatrix}
0&0&0\\
-\Omega^4/2&\Omega^4/2&0\\
\Omega^4/4&-\Omega^4/4&0\\
0&0&\Omega^2
\end{pmatrix}.
\tag{8.2}
\]

At zero frequency the separate real self-products are obstructed:

\[
S_-^{(0)}
=\frac{-6+5\sqrt3}{5}
\begin{pmatrix}48\\0\\24\\0\end{pmatrix},
\qquad
S_e^{(0)}
=-\frac{-6+5\sqrt3}{5}
\begin{pmatrix}48\\0\\24\\0\end{pmatrix}.
\tag{8.3}
\]

The amplitude (7.4) is already included in $S_e^{(0)}$. Therefore

\[
S_-^{(0)}+S_e^{(0)}=0.
\tag{8.4}
\]

This cancellation is the nonlinear heart of the construction. Each pure
component fails the homogeneous constraint, while the balanced combination
removes it exactly.

Every nonzero-frequency homogeneous source has

\[
S_{00}=S_{M_1}=0,
\qquad S_{11}+2S_{22}=0.
\]

It is removed explicitly by

\[
(C,K,U)=\left(\frac{2S_{11}}{\Omega^4},0,0\right).
\tag{8.5}
\]

Set

\[
C_E=-\frac{3(-36+17\sqrt3)}{20(-3+\sqrt3)^2},
\qquad C_X=\frac{9(-6+5\sqrt3)}{1280}.
\]

With the common certificate prefix `homogeneous_channels.`, the homogeneous
channel ledger is

| pair | $\Omega$ | correction $(C,K,U)$ | key suffix | $R$ |
|---|---:|---|---|:---:|
| balanced zero | $0$ | $(0,0,0)$ | `combined_zero` | $0^4$ |
| Einstein self | $2\omega_-$ | $(C_E,0,0)$ | `Einstein_self_sum` | $0^4$ |
| extra self | $2\omega_e$ | $(C_X,0,0)$ | `extra_self_sum` | $0^4$ |
| cross sum | $\omega_e+\omega_-$ | $(2S_{11}/\Omega^4,0,0)$ | `cross_sum` | $0^4$ |
| cross difference | $\omega_e-\omega_-$ | $(2S_{11}/\Omega^4,0,0)$ | `cross_difference` | $0^4$ |

The separate zero-frequency Einstein and extra rows are the two nonzero
vectors in (8.3); only their balanced sum belongs to the solvable ledger.

Hence no electric-charge or Wilson-line correction is hidden in the
homogeneous solution.

### 8.3 The $\ell=2,4$ polar outputs

Let $H_P(\lambda,k,\Omega)$ be the exact action-normalized polar Hessian in
coordinates $(A_t,B,C_t,U)$. Its determinant is

\[
\det H_P
=\frac{9}{16}\lambda^3(\lambda-2)
p(\Omega,k,\lambda)^2q(\Omega,k,\lambda).
\tag{8.6}
\]

For every output frequency in the table and for
$\lambda=6,20$, the exact algebraic preflight proves

\[
p\neq0,\qquad q\neq0.
\]

Thus each polar source $S_{\ell,\Omega}$ has the explicit correction

\[
\Phi^{(2)}_{\ell,\Omega}
=-H_P(\lambda,0,\Omega)^{-1}S_{\ell,\Omega},
\qquad \ell=2,4,
\tag{8.7}
\]

and every stored four-row remainder is identically zero. The complete finite
channel ledger is:

With the common certificate prefix `generic_polar_channels.` and
$E=$ Einstein, $X=$ extra, the ledger is below. Every listed four-row
remainder is $0^4$.

| $\ell$ | pair | $\Omega$ | $\operatorname{sgn}(p,q)$ | key suffix |
|---:|---|---:|:---:|---|
| 2 | balanced zero | $0$ | $(-,+)$ | `2.combined_zero` |
| 2 | $EE$ | $2\omega_-$ | $(+,+)$ | `2.Einstein_self_sum` |
| 2 | $XX$ | $2\omega_e$ | $(+,+)$ | `2.extra_self_sum` |
| 2 | $EX$ | $\omega_e+\omega_-$ | $(+,+)$ | `2.cross_sum` |
| 2 | $E\bar X$ | $\omega_e-\omega_-$ | $(-,+)$ | `2.cross_difference` |
| 4 | balanced zero | $0$ | $(-,+)$ | `4.combined_zero` |
| 4 | $EE$ | $2\omega_-$ | $(-,+)$ | `4.Einstein_self_sum` |
| 4 | $XX$ | $2\omega_e$ | $(+,-)$ | `4.extra_self_sum` |
| 4 | $EX$ | $\omega_e+\omega_-$ | $(-,-)$ | `4.cross_sum` |
| 4 | $E\bar X$ | $\omega_e-\omega_-$ | $(-,+)$ | `4.cross_difference` |

The signs are exact ordered-algebraic-field results, not floating-point
tests. In particular, every listed $p$ and $q$ is nonzero. The separate
Einstein and extra zero-frequency sources are intentionally absent from the
ledger: neither is solvable alone; their weighted sum is the `combined_zero`
row.

For visibility, two nontrivial corrections in the order $(A_t,B,C_t,U)$ are

\[
\Phi^{(2)}_{2,2\omega_e}
=(-6+5\sqrt3)
\begin{pmatrix}
45723/91364\\0\\9873/91364\\-2097/22841
\end{pmatrix},
\tag{8.8}
\]

\[
\Phi^{(2)}_{4,2\omega_e}
=(-6+5\sqrt3)
\begin{pmatrix}
2097/19565\\0\\6183/19565\\-351/1505
\end{pmatrix}.
\tag{8.9}
\]

Direct multiplication by $H_P$ returns minus the stored source in all four
rows for each vector. The larger cross-channel radicals remain in the
machine-readable supplement, where their source, correction, and zero
remainder appear under the keys displayed in the ledger.

### 8.4 Completion of the dependent tensor equations

Solving four action rows is sufficient only if the remaining ungauged tensor
equations are proved to follow. Use target equation order

\[
(A,B,C,h_t,h_x,K,G,U).
\]

At $k=0$, the four certified target Noether identities are the rows of

\[
N_0=
\begin{pmatrix}
2i\Omega&0&0&1&0&0&0&0\\
0&i\Omega&0&0&1&0&0&0\\
0&0&0&i\Omega&0&-\lambda&2&-1\\
-2&0&2&0&0&2&0&0
\end{pmatrix}.
\tag{8.10}
\]

Let $S_{A,B,C,U}$ select equations $A,B,C,U$. Exact calculation gives

\[
\det\begin{pmatrix}S_{A,B,C,U}\\N_0\end{pmatrix}=-4.
\tag{8.11}
\]

The determinant is a nonzero constant, independent of $\Omega$ and
$\lambda$. Therefore the four solved equations and four identities span all
eight equations, including at $\Omega=0$.

This applies to the quadratic source without assuming that
$\Phi^{(1)}$ integrates to an exact family. If the nonlinear Noether
identity is $N(\Phi)E(\Phi)=0$, then expansion about an on-shell background
with an on-shell first-order tangent gives

\[
N^{(0)}E^{(2)}+N^{(1)}E^{(1)}+N^{(2)}E^{(0)}=0
\quad\Longrightarrow\quad
N^{(0)}E^{(2)}=0.
\tag{8.12}
\]

Thus the dependent quadratic rows obey precisely the background identities
used in (8.11).

### 8.5 Reality and fixed-magnetic-bundle completion

Define $\Phi^{(2)}$ as the finite sum of (8.5), (8.7), their complex
conjugates, and the real zero-frequency corrections. Then $\Phi^{(2)}$ is
real, $S^1_L$-periodic in space, and finite quasiperiodic in time. No
independent homogeneous solution is added. The general problem fixes only
the magnetic-bundle component $P_N$; the constructed correction additionally
leaves the homogeneous electric and Wilson-line coordinates unchanged:

- the magnetic Chern-class shift is zero;
- every $\ell=2,4$ Maxwell correction integrates to zero on $S^2$;
- the homogeneous Maxwell coefficient $U$ is zero in every channel;
- there is no stationary electric-charge or Wilson-line zero-mode shift.

Equations (8.2)--(8.12) prove (8.1). $\square$

## 9. Interpretation: a singular nonlinear solution cone

The two theorems fit together without tension.

\[
\begin{array}{c|c|c}
\text{linear direction}&\text{quadratic Taub data}&
\text{second-order status}\\ \hline
\text{nonzero pure extra generic}&\mu_H<0&\text{obstructed}\\
\text{balanced }u_-+a_eu_e&
\mu_H=\mu_{P_x}=\mu_{J_i}=0&\text{explicitly extendible}
\end{array}
\]

Schematically, the geometry is

\[
\begin{array}{ccccc}
\mathcal T_X\setminus\{0\}
&\subset&\mathcal T_{\mathrm{lin}}=\mathcal T_E\oplus\mathcal T_X
&\supset&\mathbb R_{>0}(u_-+a_eu_e)\\
\mu_H<0&&\mu_H\ \text{indefinite}&&\mu_H=\mu_{P_x}=\mu_{J_i}=0\\
\Downarrow&&&&\Downarrow\\
\text{outside the second-order cone}&&&&
\text{certified ray inside the second-order cone}.
\end{array}
\tag{9.1}
\]

This is not a contradiction between the linear and nonlinear analyses. The
linearized equations compute the formal tangent space
$\ker L/\text{local gauge}$. The quadratic Taub map cuts out the
second-order tangent cone inside it. Positive definiteness on the pure-extra
subspace excludes every nonzero ray in that subspace. Indefiniteness after
adding the Einstein sector creates null directions of the quadratic map, one
of which is shown here to satisfy the entire second-order equation.

The result also separates two notions often conflated in discussions of
higher-derivative gravity.

1. **A linear mode can be physical at linear order.** The extra modes are
   nonradical under the classical Lee--Wald current.
2. **A linear mode need not be nonlinearly integrable.** Pure extra modes
   violate a compact global constraint.

Nothing here identifies a quantum state norm or proves a quantum ghost. The
obstruction is classical and global on the closed spatial slice.

The balanced result is stronger than mere Taub cancellation. A nonzero
quadratic defect is not a no-go unless it has a nonremovable cokernel
component, and vanishing moment maps do not by themselves prove extension.
Here the complete source is solved, channel by channel, and the dependent
equations are closed by a constant-determinant Noether argument.

## 10. Why the full nonlinear cone is the next theorem

### Post-freeze enlargement of the second-order cone

The frozen theorem proves a general no-go on one large linear subspace and an
existence result on one nontrivial mixed ray. Subsequent certificates answer
three parts of the larger classification problem without altering that
theorem boundary.

The relevant common zero locus is

\[
\mathcal Z_2=
\{u:\mu_H(u)=\mu_{P_x}(u)=
\mu_{J_1}(u)=\mu_{J_2}(u)=\mu_{J_3}(u)=0\}
\]

and the landed results are:

1. every finite-harmonic generic $k=0$ tangent on this zero locus has a
   smooth, spatially periodic, finite-quasiperiodic second-order correction;
2. for one generic $\ell\geq2$ and fixed nonzero $|k|$, the complete
   both-momentum-sign, all-$m$, both-parity zero cone has a smooth-global
   second-order correction, allowing secular time dependence at resonances;
3. every nonzero exceptional $\ell=1,k=0$ axial-plus-polar all-$m$ pure
   tangent is obstructed: distinct-$m$ interference cannot cancel its
   positive-positive resonance;
4. at the tuned $\ell=2,m_A=0$ nonzero momentum
   $k^2=2\sqrt3-7/6$, the complete all-primary bounded cone consists of two
   mixed axial--polar Einstein-minus sheets over an exact convex occupation
   polytope. The extra primary widens the allowed momentum-imbalance interval
   but creates no additional shell collision;
5. for every $\ell\geq2$, after the standard-branch tuning
   $k^2=\sqrt{2\ell(\ell+1)}-\ell/2-1/6$, the complete axisymmetric standard
   bounded cone is the origin plus two mixed axial--polar sheets on an exact
   occupation interval;
6. in the first two-absolute-momentum enlargement, all 108 axisymmetric
   $L=4$ and all 56 declared nonaxisymmetric $L=1,3$ branch-basis
   coefficients are exact and individually obstructed. The
   arbitrary-amplitude cancellation variety is not yet closed.

The remaining cone problem includes multiple $|k|$ fibres, infinite-mode
Sobolev completion, homogeneous/twist/Wilson-line/charge mixtures, and the
quadratic-source disposition of their surviving strata. None of the
post-freeze steps is needed to validate Theorems 5.1 and 8.1, and no scoped
second-order extension is extrapolated into an all-orders closure theorem.

A further exact spectrum census removes one possible loophole.  The complete
homogeneous $\ell=0,k=0$ physical quotient is empty at every nonzero
frequency, so there is no hidden homogeneous fourth-order oscillator.  In the
full $k=0$ positive-sum spectrum, the only new resonance not already covered
by the exceptional all-$m$ theorem is a generalized homogeneous/twist
zero-mode multiplied by an $\ell=2$ extra-primary mode at
$\omega^2=16/3$.  Its bilinear source coefficient is now the sharp next gate;
frequency differences and opposite nonzero momenta remain separate.

### The relative nonlinear map lands first in currents, then in charges

The same five charges now have an independent role in the attempted
nonlinear Einstein--Maxwell-to-Weyl--Maxwell inclusion.  The complete
action-derived $q_1,q_2,q_3$ data on the common 40-field carrier pass their
internal nilpotency and cyclicity checks, and the linear inclusion $f_1$
replays exactly.  At arity two, however, the strict defect

\[
\Delta_2=q^{\rm WM}_2(f_1,f_1)-f_1q^{\rm EM}_2
\]

is nonzero, with 50,854 exact coefficients.  The Taub pairing proves that no
support-local $f_2$ can remove this defect on the full smooth periodic,
fixed-bundle carrier.  After passage to the complete standard source
cohomology, its global part is nevertheless represented exactly by the five
relative quadratic charges

\[
(H,P_x,J_1,J_2,J_3).
\]

This does **not** permit those five numbers to be inserted directly as a
support-local target bundle. A finite-order differential bilinear operation
sends compactly supported inputs to compactly supported output, whereas a
nonzero constant charge row has global support. The exact nonzero charge
witness therefore forces the local receiver to be the horizontal
Noether-current cone

\[
\Omega_H^3(M;\mathfrak g_{\rm stab}^*)
\xrightarrow{d_H}
\Omega_H^4(M;\mathfrak g_{\rm stab}^*),
\]

with the five charges obtained only after Cauchy-slice integration.  The
canonical relative Hessian Green-current cone is now explicit: a finite
telescoping identity closes on all fourteen physical rows and all
coefficient jets, and its antisymmetrization supplies a local current of
maximum derivative order three.  Precomposition with the five stabilizer
actions, comparison with Lee--Wald by a horizontal improvement, cyclic BV
dual rows, and equality with all five integrated charge blocks remain open.
The result is therefore a
precise architecture theorem and obstruction, not yet a nonlinear relative
$L_\infty$ morphism.

## 11. Scope boundary

The established statements are:

- the covariant moment-map/Taub identity on the declared compact generic
  solution space;
- the complete pure-extra generic fixed-bundle second-order no-go;
- the trivial common $H,P_x$ zero locus in one nonzero-$k$ travelling
  block;
- one all-stabilizer-zero Einstein--extra $k=0$ tangent;
- one complete explicit second-order correction for that tangent.

Post-freeze certified successors additionally establish:

- complete finite-harmonic generic $k=0$ second-order extension on the full
  stabilizer-zero cone;
- smooth-global second-order extension on one fixed-$|k|$
  opposite-momentum cone, with boundedness not claimed;
- the full exceptional $\ell=1,k=0$ all-$m$ pure-sector resonance no-go.
- the tuned nonzero-$k$, axisymmetric $\ell=2$ all-primary bounded cone.
- the all-$\ell$ tuned axisymmetric standard-branch bounded cone;
- all 164 declared two-absolute-momentum branch-basis coefficients;
- the arity-two relative defect, its Taub obstruction, the complete standard
  five-charge receiver, and the necessity of a local Noether-current cone
  before globalization.

The following remain open:

- mixed cones involving multiple $|k|$ fibres or infinite-mode completion;
- the common two-momentum arbitrary-amplitude zero variety;
- general mixed second-order closure;
- integration of the certified jet to an exact or all-orders family;
- homogeneous, twist, Wilson-line, charge, and other generalized global
  mixtures not covered by the all-$m$ exceptional theorem;
- a final background-stabilizer quotient or relational observable;
- stabilizer precomposition, Lee--Wald improvement comparison, cyclic BV
  dual rows, integrated five-charge recovery, and a relative nonlinear
  morphism beyond the obstructed strict inclusion;
- Lorentzian causal propagation, asymptotic scattering, particles,
  quantization, ghosts, and unitarity.

The paper therefore carries the dependency labels
`LOCAL-ALGEBRAIC` and `REDUCED-MODE`, not `LORENTZIAN-CAUSAL`.

## 12. Computational proof and reproducibility

All ranks, signs, polynomial nonvanishing tests, amplitudes, source
projections, and operator remainders are computed in exact rational or
algebraic arithmetic. The principal certificates are:

| Result | Certificate |
|---|---|
| fixed-bundle domain and Taub descent | `bridge/certificates/compact_harmonic_domain_taub_descent.json` |
| direct generic axial extra current | `bridge/certificates/einstein_maxwell_weyl_axial_lee_wald_completion.json` |
| physical-ring generic polar module | `bridge/certificates/einstein_maxwell_weyl_polar_physical_completion.json` |
| direct generic polar extra current | `bridge/certificates/einstein_maxwell_weyl_polar_lee_wald_gate.json` |
| direct axial/polar fixture Taub matrices | `bridge/certificates/einstein_maxwell_weyl_hermitian_axial_polar_ell2_taub.json` |
| generic moment-map bridge and pure-extra no-go | `bridge/certificates/einstein_maxwell_weyl_moment_map_taub_bridge.json` |
| mixed zero-locus fixture and off-shell preflight | `bridge/certificates/einstein_maxwell_weyl_mixed_moment_map_zero_locus.json` |
| complete balanced correction | `bridge/certificates/einstein_maxwell_weyl_balanced_ell0_second_order.json` |
| complete finite-harmonic generic $k=0$ cone | `bridge/certificates/einstein_maxwell_weyl_finite_harmonic_k0_combined_cone_second_order.json` |
| fixed-$|k|$ opposite-momentum cone | `bridge/certificates/einstein_maxwell_weyl_opposite_momentum_smooth_global_second_order.json` |
| tuned nonzero-$k$ axisymmetric all-primary bounded cone | `bridge/certificates/einstein_maxwell_weyl_opposite_momentum_ell2_tuned_all_primary_bounded_cone.json` |
| all-$\ell$ tuned standard-branch bounded cone | `bridge/certificates/einstein_maxwell_weyl_symbolic_ell_tuned_axisymmetric_bounded_cone.json` |
| two-momentum axisymmetric $L=4$ matrices | `bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_axial_axial_L4_matrix.json` and parity companions |
| two-momentum nonaxisymmetric $L=1,3$ completion | `bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_nonaxisymmetric_L1_L3_matrix.json` |
| exceptional $\ell=1$ all-$m$ pure no-go | `bridge/certificates/einstein_maxwell_weyl_exceptional_ell1_all_m_resonance.json` |
| homogeneous nonzero-frequency quotient | `bridge/certificates/einstein_maxwell_weyl_homogeneous_nonzero_frequency_operator.json` |
| exceptional positive-sum resonance census | `bridge/certificates/einstein_maxwell_weyl_exceptional_ell1_resonance_census.json` |
| strict relative arity-two defect | `d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_ARITY_TWO_DEFECT_V1.json` |
| support-local $f_2$ Taub obstruction | `d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_F2_TAUB_OBSTRUCTION_V1.json` |
| complete standard five-charge receiver | `d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_COMPLETE_STANDARD_FIVE_CHARGE_Q2_V1.json` |
| finite-charge locality obstruction | `d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_FINITE_CHARGE_SUPPORT_LOCAL_LIFT_OBSTRUCTION_V1.json` |
| polarized relative Noether-current seed | `d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_POLARIZED_NOETHER_CURRENT_SEED_V1.json` |
| relative Hessian Green-current cone | `d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_HESSIAN_GREEN_CURRENT_CONE_V1.json` |

Fast verification:

```bash
python3 bridge/einstein_sector/verify_charge_fibre_paper_claim_map.py
python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_polar_physical_completion.py
python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_polar_lee_wald_gate.py
python3 -m bridge.einstein_sector.einstein_maxwell_weyl_moment_map_taub_bridge \
  --verify bridge/certificates/einstein_maxwell_weyl_moment_map_taub_bridge.json
python3 -m bridge.einstein_sector.verify_einstein_maxwell_weyl_moment_map_taub_bridge
python3 -m bridge.einstein_sector.einstein_maxwell_weyl_mixed_moment_map_zero_locus \
  --verify bridge/certificates/einstein_maxwell_weyl_mixed_moment_map_zero_locus.json
python3 -m bridge.einstein_sector.verify_einstein_maxwell_weyl_mixed_moment_map_zero_locus
python3 -m bridge.einstein_sector.einstein_maxwell_weyl_balanced_ell0_second_order \
  --verify bridge/certificates/einstein_maxwell_weyl_balanced_ell0_second_order.json
python3 -m bridge.einstein_sector.verify_einstein_maxwell_weyl_balanced_ell0_second_order
python3 -m unittest \
  bridge.einstein_sector.tests.test_einstein_maxwell_weyl_polar_physical_completion \
  bridge.einstein_sector.tests.test_einstein_maxwell_weyl_polar_lee_wald_gate \
  bridge.einstein_sector.tests.test_einstein_maxwell_weyl_moment_map_taub_bridge \
  bridge.einstein_sector.tests.test_einstein_maxwell_weyl_mixed_moment_map_zero_locus \
  bridge.einstein_sector.tests.test_einstein_maxwell_weyl_balanced_ell0_second_order
```

The final exhaustive balanced source-and-channel regeneration passed in
`468.66` seconds:

```bash
python3 -m bridge.einstein_sector.einstein_maxwell_weyl_balanced_ell0_second_order \
  --verify-exhaustive \
  bridge/certificates/einstein_maxwell_weyl_balanced_ell0_second_order.json
```

The committed-certificate verifier separately reconstructs the Noether
completion determinant, checks all imported content hashes, replays the
real-channel factors, and verifies the fixed-magnetic-bundle and homogeneous
charge-coordinate flags. The largest nested-radical cross-channel equations
are replayed by the exhaustive rail.

### Model authorship and human accountability

GPT-5.6.sol, an OpenAI model, contributed the research programme,
mathematical direction, derivations, symbolic-code generation and debugging,
claim auditing, literature organization, and manuscript. The project was
commissioned and directed by Asger Alstrup Palm, who initiated the questions,
served as the non-technical orchestrator and corresponding human contact, but
claims no technical contribution. Circulation or submission remains
conditional on a documented human verification of the mathematical claims,
proof boundaries, source citations, and final text.

## References

1. R. V. Saraykar and J. H. Rai, “Linearization Stability of Einstein Field
   Equations is a Generic Property,” arXiv:1609.07703 (2016),
   <https://arxiv.org/abs/1609.07703>.
2. A. E. Fischer, J. E. Marsden, and V. Moncrief, “The structure of the space
   of solutions of Einstein's equations. I. One Killing field,” *Ann. Inst.
   H. Poincaré A* **33** (1980) 147--194.
3. E. Altaş and B. Tekin, “Linearization Instability for Generic Gravity in
   AdS,” *Phys. Rev. D* **97** (2018) 024028,
   <https://arxiv.org/abs/1705.10234>.
4. J. F. Plebański and S. Hacyan, “Some exceptional electrovac type D metrics
   with cosmological constant,” *J. Math. Phys.* **20** (1979) 1004--1010,
   <https://doi.org/10.1063/1.524174>.
5. GPT-5.6.sol, “Einstein--Maxwell Waves inside Weyl--Maxwell Gravity on a
   Compact Product: Exact Linear Phase-Space Inclusion and the Extra Axial
   Branch,” companion manuscript, 2026.
6. M. Ortaggio and J. Podolský, “Impulsive waves in electrovac direct product
   spacetimes with $\Lambda$,” *Class. Quantum Grav.* **19** (2002)
   5221--5239, <https://arxiv.org/abs/gr-qc/0209068>.
7. M. Ortaggio, “Einstein--Maxwell fields as solutions of higher-order
   theories,” *Eur. Phys. J. C* **82** (2022) 1056,
   <https://arxiv.org/abs/2205.14392>.
8. J. Lee and R. M. Wald, “Local symmetries and constraints,”
   *J. Math. Phys.* **31** (1990) 725--743,
   <https://doi.org/10.1063/1.528801>.
9. V. Iyer and R. M. Wald, “Some properties of Noether charge and a proposal
   for dynamical black hole entropy,” *Phys. Rev. D* **50** (1994) 846--864,
   <https://arxiv.org/abs/gr-qc/9403028>.
10. J. M. Arms, J. E. Marsden, and V. Moncrief, “The structure of the space
    of solutions of Einstein's equations. II. Several Killing fields and the
    Einstein--Yang--Mills equations,” *Ann. Phys.* **144** (1982) 81--106,
    <https://doi.org/10.1016/0003-4916(82)90105-1>.
11. A. Carlotto, “The general relativistic constraint equations,” *Living
    Rev. Relativ.* **24** (2021) 2,
    <https://doi.org/10.1007/s41114-020-00030-z>.

---

**Frozen claim flag:**
`PURE_EXTRA_GENERIC_NO_GO_AND_ONE_BALANCED_MIXED_SECOND_ORDER_EXTENSION_CERTIFIED`.

**Next theorem:** compute the unique surviving positive-sum bilinear between
a homogeneous/twist global zero-mode and an $\ell=2$ extra primary; then
dispose frequency-difference, multi-$|k|$, infinite-mode, charge/Wilson-line,
and higher-order gates.
