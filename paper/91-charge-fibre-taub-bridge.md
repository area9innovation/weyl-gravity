# Taub obstruction and balanced extension in compact Weyl--Maxwell gravity

## Pure extra modes versus Einstein--extra mixtures

GPT-5.6.sol (OpenAI model)

The research programme was commissioned and directed by Asger Alstrup Palm
(`asger@area9.dk`), who initiated the questions, served as the non-technical
orchestrator and corresponding human contact, but claims no technical
contribution.

Working manuscript, 17 July 2026. The theorem-frozen scope is
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
frequency. Hence this balanced real tangent has an explicit second-order
correction on the same charge fibre.

The result exhibits a sharp nonlinear distinction:

\[
\boxed{
\text{pure extra generic mode: obstructed},\qquad
\text{balanced Einstein--extra mode: extendible to second order}.}
\]

The theorem concerns a formal second-order jet, not an exact family or an
all-orders solution. Classification of the full mixed moment-map zero cone is
left as the next theorem rather than imposed as a prerequisite for the
present result.

## 1. Introduction

Linearization stability asks whether a solution of the linearized field
equations is the first derivative of a family of exact solutions. On a
compact Cauchy surface, background symmetries can produce quadratic Taub
constraints which are invisible in the linear equations. This phenomenon is
classical in Einstein gravity and is naturally expressed through the
constraint-adjoint kernel or, equivalently on a closed slice, through the
moment map for the background symmetry group [1,2]. Higher-derivative gravity
has analogous linearization-instability questions [3].

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

1. **General pure-extra no-go.** Every nonzero real pure-extra generic
   tangent is obstructed at second order on the fixed magnetic bundle. This
   holds for both parities, every physical $\ell\geq2$, every allowed
   compact momentum, and finite or rapidly decreasing finite-energy
   superpositions.

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
opposite-momentum standing waves and exceptional/global blocks, is the next
theorem.

### Main theorem

Let $\mathcal T_X^{\mathrm{gen}}$ be the real, locally gauge-reduced,
generic extra Weyl--Maxwell tangent on the fixed magnetic bundle, and let
$u_-$ and $u_e$ be the axisymmetric axial modes defined in Section 7.

> **Theorem A (obstruction versus balanced extension).**
>
> 1. For every nonzero $u\in\mathcal T_X^{\mathrm{gen}}$, the
>    constant-lapse Taub pairing is nonzero. Therefore the equation
>    \[
>    L_{\mathrm{WM}}\Phi^{(2)}
>    =-\frac12D^2E_{\mathrm{WM}}[u,u]
>    \]
>    has no fixed-bundle periodic solution.
> 2. The real tangent
>    \[
>    \Phi^{(1)}=\operatorname{Re}(u_-)+a_e\operatorname{Re}(u_e),
>    \qquad
>    |a_e|^2=\frac{27}{52}(5\sqrt3-6),
>    \]
>    annihilates all five background-stabilizer moment maps and admits an
>    explicit real second-order correction $\Phi^{(2)}$ on the same fixed
>    bundle.

Part 1 is a theorem on the complete pure-extra generic sector. Part 2 is an
existence theorem for one declared mixed tangent. It is not a claim that
every common-zero tangent extends.

## 2. The common background and the fixed charge fibre

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
$p$-primary summands. The extra shell is

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
$\omega_+$. The Einstein and extra primary modules are orthogonal under the
direct four-dimensional Lee--Wald current. Each axial and polar extra Gram
matrix $G_X^{\mathrm{par}}$ is positive definite. Thus the extra modes are
genuine nonnull linear solutions, even though Section 5 proves that they are
not fixed-bundle nonlinear tangent directions.

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
$L=DE|_{\bar\Phi}$. A first-order tangent $u$ extends through second order
only if there is a $\Phi^{(2)}$ satisfying

\[
L\Phi^{(2)}
=-\frac12D^2E|_{\bar\Phi}[u,u].
\tag{4.1}
\]

Every adjoint zero mode $\zeta_X$ therefore gives the necessary Taub
condition

\[
\left\langle\zeta_X,
\frac12D^2E[u,u]\right\rangle=0.
\tag{4.2}
\]

For an infinitesimal bundle-covariant automorphism $X$ of the background,
the closed-slice covariant Hamiltonian identity gives

\[
\boxed{
\left\langle\zeta_X,
\frac12D^2E_{\mathrm{WM}}[u,u]\right\rangle
=\mu_X(u)
=\frac12\Omega_{\mathrm{WM}}
(u,\mathcal L_Xu).}
\tag{4.3}
\]

To prove (4.3), differentiate the action Noether-current identity twice,
use $E(\bar\Phi)=0$, $Lu=0$, and
$\mathcal L_X\bar\Phi=0$, then integrate over the closed Cauchy surface.
Every exact Lee--Wald improvement and bundle-patching corner term integrates
to zero. This is the boundaryless specialization of the covariant phase-space
construction [8,9].

The exact real-mode moment maps are

\[
\mu_H
=-\frac{L}{4}\sum
\omega^2 c^\dagger(G_{\mathrm{branch}}\otimes W_\ell)c,
\tag{4.4}
\]

\[
\mu_{P_x}
=\frac{L}{4}\sum
k\omega c^\dagger(G_{\mathrm{branch}}\otimes W_\ell)c,
\tag{4.5}
\]

\[
\mu_{J_a}
=\frac{L}{4}\sum
\omega c^\dagger(G_{\mathrm{branch}}\otimes W_\ell T_a)c.
\tag{4.6}
\]

The sums are block diagonal in $k,\ell$, parity, and frequency shell.
Rotations preserve $\ell$; $J_3$ is diagonal in $m$, while
$J_1,J_2$ connect only $m$ to $m\pm1$. Axial--polar and
Einstein--extra cross terms vanish. The sign and the factor $1/4$ in (4.4)
are fixed by exact agreement with three independent direct tensor
calculations: one axial extra block and the axial and polar Einstein-minus
fixtures at $\ell=2,k=0$.

## 5. The complete pure-extra obstruction

> **Theorem 5.1 (pure-extra fixed-bundle no-go).** Let $u$ be a real
> pure-extra generic Weyl--Maxwell tangent, axial or polar, with finite or
> rapidly decreasing finite-energy harmonic coefficients. If $u\neq0$,
> then $u$ admits no periodic second-order correction on the fixed magnetic
> bundle $P_N$.

### Proof

On the extra shell, $\omega_e^2>0$ for every physical
$\lambda\geq6$. Both extra Gram matrices and the angular form $W_\ell$
are positive definite. Hence every nonzero block contributes strictly
negatively to (4.4):

\[
\mu_H(u)
=-\frac{L}{4}\sum_{\mathrm{extra\ blocks}}
\omega_e^2 c^\dagger(G_X^{\mathrm{par}}\otimes W_\ell)c<0.
\]

Orthogonality makes the same conclusion valid for finite and convergent
rapidly decreasing superpositions. Equation (4.2) is therefore violated for
the constant-lapse adjoint class.

The obstruction cannot be absorbed inside the declared domain. Continuous
magnetic variation changes $c_1(P_N)$, while electric variation has zero
linear pairing with $H$ at the purely magnetic background. Thus (4.1) has
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

Set

\[
|a_e|^2
=\frac{\tau_-}{-\tau_e}
=\frac{27}{52}(5\sqrt3-6).
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

Vanishing Taub charges is necessary but not sufficient for extension. A
nonzero quadratic source can still have a component in another adjoint
cokernel or lie on a resonant output shell. We therefore solve the complete
second-order equation directly.

## 8. Complete second-order extension of the balanced tangent

> **Theorem 8.1 (balanced Einstein--extra second-order extension).** The real
> tangent (7.5) admits a real, periodic, fixed-bundle correction
> $\Phi^{(2)}$ satisfying
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

and every stored four-row remainder is identically zero. The certificate
retains the exact radical expressions for all corrections; writing the
largest cross-channel radicals in the main text would obscure rather than
strengthen the argument.

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
\tag{8.8}
\]

Let $S_{A,B,C,U}$ select equations $A,B,C,U$. Exact calculation gives

\[
\det\begin{pmatrix}S_{A,B,C,U}\\N_0\end{pmatrix}=-4.
\tag{8.9}
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
\tag{8.10}
\]

Thus the dependent quadratic rows obey precisely the background identities
used in (8.9).

### 8.5 Reality and fixed-charge completion

Define $\Phi^{(2)}$ as the finite sum of (8.5), (8.7), their complex
conjugates, and the real zero-frequency corrections. Then
$\Phi^{(2)}$ is real and periodic. No independent homogeneous solution is
added. The correction preserves the declared charge fibre:

- the magnetic Chern-class shift is zero;
- every $\ell=2,4$ Maxwell correction integrates to zero on $S^2$;
- the homogeneous Maxwell coefficient $U$ is zero in every channel;
- there is no stationary electric-charge or Wilson-line zero-mode shift.

Equations (8.2)--(8.10) prove (8.1). $\square$

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

The current paper proves a general no-go on one large linear subspace and an
existence result on one nontrivial mixed ray. That is already a coherent
nonlinear statement. Completing the full mixed cone would answer a different
classification problem.

The next theorem should determine the common zero locus

\[
\mathcal Z_2=
\{u:\mu_H(u)=\mu_{P_x}(u)=
\mu_{J_1}(u)=\mu_{J_2}(u)=\mu_{J_3}(u)=0\}
\]

and then test the quadratic source on its strata. The natural order is:

1. classify the full $k=0$ cone using Gram-normalized occupation matrices;
2. classify opposite-momentum standing-wave balances;
3. incorporate exceptional, homogeneous, twist, charge, and Wilson-line
   blocks;
4. determine which surviving second-order jets encounter cubic or higher
   obstructions.

None of those steps is needed to validate Theorems 5.1 and 8.1. Conversely,
the single balanced extension must not be extrapolated into a general closure
theorem.

## 11. Scope boundary

The established statements are:

- the covariant moment-map/Taub identity on the declared compact generic
  solution space;
- the complete pure-extra generic fixed-bundle second-order no-go;
- the trivial common $H,P_x$ zero locus in one nonzero-$k$ travelling
  block;
- one all-stabilizer-zero Einstein--extra $k=0$ tangent;
- one complete explicit second-order correction for that tangent.

The following remain open:

- the full mixed moment-map zero cone;
- general mixed second-order closure;
- integration of the certified jet to an exact or all-orders family;
- exceptional and generalized global blocks;
- a final background-stabilizer quotient or relational observable;
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
| direct generic polar extra current | `bridge/certificates/einstein_maxwell_weyl_polar_lee_wald_gate.json` |
| direct axial/polar fixture Taub matrices | `bridge/certificates/einstein_maxwell_weyl_hermitian_axial_polar_ell2_taub.json` |
| generic moment-map bridge and pure-extra no-go | `bridge/certificates/einstein_maxwell_weyl_moment_map_taub_bridge.json` |
| mixed zero-locus fixture and off-shell preflight | `bridge/certificates/einstein_maxwell_weyl_mixed_moment_map_zero_locus.json` |
| complete balanced correction | `bridge/certificates/einstein_maxwell_weyl_balanced_ell0_second_order.json` |

Fast verification:

```bash
python3 bridge/einstein_sector/verify_charge_fibre_paper_claim_map.py
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
real-channel factors, and verifies the fixed-charge/reality flags. The largest
nested-radical cross-channel equations are replayed by the exhaustive rail.

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

---

**Frozen claim flag:**
`PURE_EXTRA_GENERIC_NO_GO_AND_ONE_BALANCED_MIXED_SECOND_ORDER_EXTENSION_CERTIFIED`.

**Next theorem:** full $k=0$ common moment-map zero cone, followed by
opposite-momentum standing-wave and exceptional/global strata.
