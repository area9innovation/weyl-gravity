# Two-field compact-charge and scale-health preflight

## Result

The second complex field genuinely repairs the one-field compact-Gauss
problem, but it does not repair the independent dressed-trace scale gate:

\[
\boxed{
\mathcal L_{\rm two\ field,\ minimal}^{\rm healthy}
=\varnothing .
}
\]

The exact new information is important:

\[
\boxed{
\text{primitive compact rank one leaves a physical relative phase clock.}
}
\]

Thus the terminal obstruction is not compact charge or Berger stationarity.
It is the trichotomy

\[
\boxed{
\begin{array}{ll}
\text{independent scale weights}
&\Rightarrow\text{null or indefinite scalar kinetic},\\
\text{independence through the relative phase}
&\Rightarrow\text{the clock is gauge},\\
\text{positive scalar kinetic plus physical clock}
&\Rightarrow\text{the candidate scale column is reducible}.
\end{array}}
\]

No full BV or causal successor is activated.

## Imported boundary

The result hash-imports:

1. the empty one-field separated scale/\(U(1)\) preflight;
2. its `NOT_ACTIVATED` conditional full-gate closure;
3. the exact positive Berger clock fixture.

The two-field alternative is therefore active, while the one-field causal
path remains closed.

## Integral compact-charge classification

Let

\[
Q\in{\rm Mat}_{2\times r}(\mathbb Z),
\qquad r=0,1,2,
\]

be the compact charge matrix of two phase circles. Equivalent descriptions
are quotiented by

\[
Q\sim UQV,
\qquad
U\in GL(2,\mathbb Z),\quad V\in GL(r,\mathbb Z),
\]

together with field permutations and signs.

The exact Smith classification is:

| rank | Smith form | faithful case | physical phase dimension |
|---:|---|---|---:|
| 0 | zero | no compact gauge change | 2 |
| 1 | \(\operatorname{diag}(d,0)\) | \(d=1\) | 1 |
| 2 | \(\operatorname{diag}(d_1,d_2)\) | \(d_1=d_2=1\) | 0 |

For rank one,

\[
d=\gcd(Q_{11},Q_{21}).
\]

For a \(2\times2\) rank-two matrix,

\[
d_1=\gcd(\text{entries}),
\qquad
d_1d_2=|\det Q|,
\qquad
d_1\mid d_2.
\]

The only minimal faithful case that leaves a continuous phase is therefore

\[
\boxed{
Q=
\begin{pmatrix}
1\\0
\end{pmatrix}.
}
\]

It gauges \(\theta_1\) and leaves

\[
\psi=\theta_2
\]

as the physical relative phase.

The integer classification is checked twice: SymPy's exact
`smith_normal_form` and the GMP-backed Forge `math/snf` kernel. The Forge
fixture covers primitive rank one, nonprimitive rank one, unimodular rank two
and a finite-kernel rank-two example.

For a real-plus-complex representation, the phase lattice has rank one.
Faithful compact rank one gauges its only phase, while rank zero is the
unchanged global-phase theory. It therefore cannot provide a compact-gauged
relative phase. Its two radial modes obey the same scale/positivity lemma
below.

## Complete declared minimal action

For two complex polar fields

\[
\Phi_i=\rho_i e^{i\theta_i},\qquad i=1,2,
\]

the declared parity-even formal-polar action contains

\[
\begin{aligned}
\mathcal L=\sqrt{-g}\bigg\{&
\frac{\alpha_C}{8}C^2+\alpha_R\mathcal R_W^2
-\frac12K^r_{ij}D\rho_i\cdot D\rho_j\\
&-\frac1{12}K^R_{ij}\rho_i\rho_j\mathcal R_W
-\frac12K^\theta_{ij}\rho_i\rho_jB_i\cdot B_j
-V_4(\rho_1,\rho_2)\\
&-\frac14Z_{\alpha\beta}H^\alpha\cdot H^\beta
-\frac12\chi_\alpha F_W\cdot H^\alpha
-\frac{\zeta_W}{4}F_W^2
\bigg\},
\end{aligned}
\]

where

\[
B_i=d\theta_i+Q_{i\alpha}A^\alpha
\]

and

\[
V_4=
\frac{\lambda_{40}}4\rho_1^4
+\frac{\lambda_{22}}2\rho_1^2\rho_2^2
+\frac{\lambda_{04}}4\rho_2^4.
\]

This is the complete declared formal-polar scalar bilinear and regular
\(U(1)\)-invariant quartic ansatz at the stated derivative order. No
nonpolynomial potential or higher derivative is fitted to the background.

## Exact scale Ward matrix

Let the metric candidate-scale weight be \(a\), and the radial weights be
\(b_1,b_2\). Every scalar bilinear matrix has constant-\(\eta\) weight matrix

\[
W=
\begin{pmatrix}
2(a-b_1)&2a-b_1-b_2\\
2a-b_1-b_2&2(a-b_2)
\end{pmatrix}.
\]

For each \(K=K^r,K^R,K^\theta\), the Ward equations include

\[
(a-b_1)K_{11}=0,
\]

\[
(2a-b_1-b_2)K_{12}=0,
\]

\[
(a-b_2)K_{22}=0.
\]

Quartic entries obey

\[
(4a-b_i-b_j-b_k-b_l)\lambda_{ijkl}=0.
\]

A constant gauge parameter already proves these relations; derivative
improvements cannot cancel them.

## Positivity lemma

For a real symmetric scalar kinetic matrix

\[
K=
\begin{pmatrix}
k_{11}&k_{12}\\
k_{12}&k_{22}
\end{pmatrix},
\]

positive definiteness requires

\[
k_{11}>0,\qquad
k_{22}>0,\qquad
k_{11}k_{22}-k_{12}^2>0.
\]

The two diagonal Ward equations therefore force

\[
\boxed{b_1=b_2=a.}
\]

The semidefinite boundary does not evade this. If \(k_{ii}=0\) in a
positive-semidefinite \(2\times2\) matrix, its determinant condition forces
\(k_{12}=0\). Hence a weight-mismatched field is an entire null row/column,
not an active healthy mode.

This is the exact sign separator.

## Gauge rank and reducibility

For the canonical primitive charge \(Q=(1,0)^T\), use the row basis

\[
(\log g,\log\rho_1,\log\rho_2,\theta_1,\theta_2,W_L,A_L)
\]

and ghost basis \((\omega,\eta,\gamma)\). The symbol is

\[
G=
\begin{pmatrix}
1&a&0\\
-1&-b_1&0\\
-1&-b_2&0\\
0&s_1&1\\
0&s_2&0\\
-1&-a&0\\
0&-s_1&-1
\end{pmatrix}.
\]

Its decisive minors are

\[
a-b_1,\qquad a-b_2,\qquad -s_2.
\]

After positivity, \(b_1=b_2=a\). There are then two cases.

If \(s_2\ne0\), the third column is independent only because the candidate
scale transformation shifts the surviving relative phase. The clock is
gauge.

If \(s_2=0\), then

\[
G
\begin{pmatrix}
-a\\1\\-s_1
\end{pmatrix}
=0.
\]

The rank is two. Both dressed metrics

\[
\widehat g_i=(\rho_i/f_i)^2g
\]

are \(\eta\)-invariant, and the candidate column adds no dressed-trace gauge
direction.

This exhausts the healthy scale strata. An independent candidate obtained
from \(b_i\ne a\) acts only on a null/indefinite scalar direction.

## Cylinder and Berger equations

Define the aggregate background coefficients

\[
K=f^TK^Rf,\qquad
C=\beta^TZ(f)\beta,\qquad
U=4V_4(f).
\]

The metric Euler equation is

\[
\alpha_BB_{ab}
+\alpha_R(4R\,{\rm Ric}_{ab}-R^2g_{ab})
-\frac K6G_{ab}-T_{ab}=0.
\]

On the constant-phase unit cylinder, the \((00,\mathrm{horizontal})\) rows
in order \((\alpha_B,\alpha_R,K,C,U)\) are

\[
\begin{pmatrix}
0&36&-\frac12&-\frac12&-\frac14\\
0&12&\frac16&-\frac12&\frac14
\end{pmatrix}.
\]

The two exact radial rows are

\[
K^Rf+\nabla_fV_4=0.
\]

On the frozen Berger geometry, the three metric rows are

\[
\begin{pmatrix}
\frac{961}{9600}&\frac{22801}{6400}&-\frac{151}{960}&-\frac12&-\frac14\\
\frac{403}{9600}&\frac{20083}{6400}&\frac3{320}&-\frac12&\frac14\\
\frac{31}{1920}&-\frac{3473}{1280}&\frac{133}{960}&-\frac12&\frac14
\end{pmatrix},
\]

with radial equations

\[
\frac{151}{480}K^Rf
-\nabla_f\!\left(\frac12\beta^TZ(f)\beta\right)
+\nabla_fV_4=0
\]

and compact Gauss equation

\[
Q^TZ(f)\beta=0.
\]

The primitive charge lattice genuinely removes the one-field Gauss
obstruction. With

\[
\beta_1=0,\qquad\beta_2=\frac34,
\]

the exact aggregate vector

\[
\left(5,0,1,\frac9{16},\frac{119}{480}\right)
\]

annihilates all three Berger metric rows, and the compact Gauss row vanishes.
The neutral relative momentum \(p_2\) may be nonzero. Thus a stationary
positive relative clock exists at the compact-charge level.

It does not intersect the independent dressed-trace scale gate because of
the positivity/reducibility trichotomy.

## Charge disposition

With

\[
p=Z(f)\beta,
\]

the compact constraint is

\[
Q^Tp=0.
\]

For \(Q=(1,0)^T\), this sets \(p_1=0\) but leaves

\[
Q_{\rm rel}=p_2
\]

unconstrained and potentially nonzero. The phase contribution to the raw
\(D\)-moment map is \(\beta_2\,\delta p_2\).

The scale charge remains a constraint on closed \(S^3\). Leaving it physical
to obtain a clock or trace mode is forbidden and is not used.

## Claim boundary

This theorem covers two formal-polar complex fields or the real-plus-complex
subcase, at most two compact generators with integral charge lattice up to
\(GL(\mathbb Z)\), the displayed two scale columns, the complete declared
minimal scalar bilinear/regular quartic action, and the certified homogeneous
cylinder/Berger fixtures.

It does not exclude additional fields, non-Riemannian or constrained target
kinetics, higher derivatives, other potentials, boundaries, backgrounds or
representations. It selects no action and establishes no full BV carrier,
causal parent, nonlinear \(q_2\), Hadamard state, anomaly/QME result,
particle space, scattering, positivity or unitarity theorem.

EVIDENCE: `d_quotient_classical/receipts/COMPENSATOR_TWO_FIELD_CHARGE_MATRIX_PREFLIGHT_V1_TIER_RECEIPT.json`

CLOSE-OUT: DONE — primitive rank-one compact charge repairs the Gauss clock
gate, but exact scale Ward identities plus positive scalar inertia force the
candidate scale direction to be reducible or to gauge the relative clock.
