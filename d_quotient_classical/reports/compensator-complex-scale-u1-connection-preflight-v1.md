# Separated real-scale and compact-\(U(1)\) compensator preflight

## Result

The smallest representation escape named by the minimal-ladder synthesis does
not pass its preflight:

\[
\boxed{
\mathcal L_{\rm separated\ scale/U(1)}^{\rm healthy}
=\varnothing
}
\]

inside the complete declared minimal action, gauge and background ansatz.

There are two independent exact separators.

First, the compact connection makes

\[
B=d\theta+A
\]

derivative-gauge invariant, but it does not change the constant scale weight
of

\[
\sqrt{-g}\,\rho^2 g^{ab}B_aB_b .
\]

Writing \(\Delta=a-b\) for the difference between the candidate metric and
radial scale weights, exact Ward invariance still gives

\[
\boxed{\Delta\kappa_\theta=0.}
\]

Second, the internal \(U(1)\) Euler equation is a Gauss law. On closed
\(S^3\), its integrated temporal component gives

\[
\boxed{
Q_{\rm int}
=\int_{S^3}n_a\,\kappa_\theta\rho^2B^a
=0.
}
\]

For a homogeneous clock with \(\rho=f\ne0\) and \(B_t\ne0\), this forces
\(\kappa_\theta=0\). Thus gauging the phase converts the former global clock
charge into a constraint; it does not preserve a physical relational phase
clock.

## Imported activation boundary

Five artifacts are imported by content hash:

1. the convention-correct Level-3b no-go;
2. the terminal minimal-ladder synthesis;
3. the one-real-connection Level-4 separator;
4. the exact positive Berger clock geometry;
5. the fixed-coupling Berger charge convention.

Neither Level 3b nor the minimal ladder exports a selected action. The
synthesis activates this construction only as a preflight.

## Complete minimal action

The real fields are

\[
(g_{ab},\Phi=\rho e^{i\theta},W_a,A_a),
\qquad \rho>0,
\]

with \(W\) a noncompact real scale connection and \(A\) a compact internal
\(U(1)\) connection. Let

\[
F_W=dW,\qquad H_A=dA,\qquad B=d\theta+A.
\]

Modulo Euler and total derivatives, the declared parity-even density is

\[
\begin{aligned}
\mathcal L=\sqrt{-g}\bigg\{&
\frac{\alpha_C}{8}C^2+\alpha_0\mathcal R_W^2
+\alpha_2(\operatorname{Ric}^{\rm TF}_W)^2\\
&-\frac{\zeta_W}{4}F_W^2
-\frac{\zeta_A}{4}H_A^2
-\frac{\chi}{2}F_W\!\cdot H_A\\
&-\frac{\kappa_r}{2}(D_W\rho)^2
-\frac{\kappa_R}{12}\rho^2\mathcal R_W
-\frac{\kappa_\theta}{2}\rho^2B^2
-\frac{\lambda}{4}\rho^4
\bigg\}.
\end{aligned}
\]

The mixed Abelian curvature term is included. The scalar cross term
\(\rho D_W\rho\cdot B\) is excluded by complex conjugation
\((\theta,A)\mapsto(-\theta,-A)\). Charged sources, extra compensators,
higher derivatives and dimensionful spurions are not in the ansatz.

On \(W=0\), the four-dimensional identity

\[
(\operatorname{Ric}^{\rm TF})^2
=\frac12\left(C^2+\frac16R^2-E_4\right)
\]

gives the effective coefficients

\[
\alpha_B^{\rm eff}=\alpha_C+4\alpha_2,
\qquad
\alpha_R^{\rm eff}=\alpha_0+\frac{\alpha_2}{12}.
\]

## Gauge rank and reducibility

The three gauge parameters are the original Weyl parameter \(\omega\), the
candidate real scale parameter \(\eta\), and the compact internal parameter
\(\gamma\):

\[
\begin{aligned}
\delta g&=2(\omega+a\eta)g,\\
\delta\rho&=-(\omega+b\eta)\rho,\\
\delta W&=-d(\omega+a\eta),\\
\delta\theta&=s\eta+\gamma,\\
\delta A&=-d(s\eta+\gamma).
\end{aligned}
\]

Thus \(B\) is invariant. In the row basis

\[
(\log g,\log\rho,W_L,\theta,A_L)
\]

and ghost basis \((\omega,\eta,\gamma)\), the normalized symbol is

\[
G=
\begin{pmatrix}
1&a&0\\
-1&-b&0\\
-1&-a&0\\
0&s&1\\
0&-s&-1
\end{pmatrix}.
\]

The \((\log g,\log\rho,\theta)\) minor is

\[
\det G_{\{g,\rho,\theta\}}=a-b=\Delta.
\]

For \(\Delta\ne0\), the rank is three and the candidate scale column acts on
the dressed metric

\[
\widehat g=(\rho/f)^2g,
\qquad
\delta_\eta\widehat g=2\Delta\eta\,\widehat g.
\]

For \(\Delta=0\), the rank is two and

\[
G
\begin{pmatrix}
-a\\1\\-s
\end{pmatrix}
=0.
\]

The candidate column is exactly \(a\) times the old Weyl column plus \(s\)
times the compact column. It adds no dressed-trace gauge direction.

The generic minimal BRST rows are the Diff semidirect completion of

\[
\begin{aligned}
Qg&=2(\omega+a\eta)g,&
Q\rho&=-(\omega+b\eta)\rho,\\
Q\theta&=s\eta+\gamma,&
QW&=-d(\omega+a\eta),\\
QA&=-d(s\eta+\gamma).
\end{aligned}
\]

On \(\Delta=0\), retaining all three ghosts requires an even ghost-for-ghost
\(z\) with

\[
Q\omega=-az,\qquad
Q\eta=z,\qquad
Q\gamma=-sz.
\]

The induced contribution to every field row is
\(G(-a,1,-s)^T=0\). Equivalently, one may quotient to the irreducible
\((\omega,\gamma)\) presentation. Both descriptions show explicitly that the
candidate column adds no dressed-trace contraction.

At linear order, if \(\delta g=2u\,g\), the dressed conformal variable is

\[
\widehat u=u+\frac{\delta\rho}{f},
\qquad
Q_\eta\widehat u=\Delta\eta.
\]

Thus \(\Delta\ne0\) gauges \(\widehat u\) but, as the next section proves,
removes its entire declared scalar action; \(\Delta=0\) preserves
\(\widehat u\) and is reducible.

## Exact constant-Ward ideal

Even though \(B\) is derivative-gauge invariant, the four scalar densities
have candidate-scale weights

\[
\begin{array}{c|c}
\text{density}&\text{weight}\\ \hline
(D_W\rho)^2&2\Delta\\
\rho^2\mathcal R_W&2\Delta\\
\rho^2B^2&2\Delta\\
\rho^4&4\Delta .
\end{array}
\]

The exact Ward ideal therefore contains

\[
(\Delta\kappa_r,\Delta\kappa_R,
\Delta\kappa_\theta,\Delta\lambda).
\]

A constant \(\eta\) already proves this statement, so derivative
improvements cannot reopen the \(\Delta\ne0\) branch. On that branch the new
trace gauge direction exists, but the complete minimal scalar action,
including the phase residue, vanishes. On \(\Delta=0\), the scalar action may
survive, but the proposed scale direction is reducible.

## Exact cylinder system

Set

\[
K_R=\kappa_Rf^2,\qquad
Z_\theta=\kappa_\theta f^2,\qquad
V=\lambda f^4.
\]

For

\[
g=-dt^2+d\Omega_3^2,\quad
W=A=0,\quad \rho=f,\quad B_t=0,
\]

the independent rows \((E_{00},E_{\rm horizontal},E_\rho)\), in coefficient
order

\[
(\alpha_B^{\rm eff},\alpha_R^{\rm eff},K_R,Z_\theta,V),
\]

are

\[
\begin{pmatrix}
0&36&-\frac12&0&-\frac14\\
0&12&\frac16&0&\frac14\\
0&0&1&0&1
\end{pmatrix}.
\]

The exact rank is two, and the complete relations are

\[
K_R=144\alpha_R^{\rm eff},
\qquad
V=-144\alpha_R^{\rm eff},
\]

with \(\alpha_B^{\rm eff}\) and \(Z_\theta\) free. This is a constant-phase
cylinder, not a clock background.

On the independent \(\Delta\ne0\) branch, the Ward ideal further sets
\(K_R=Z_\theta=V=0\), hence \(\alpha_R^{\rm eff}=0\). Only the Bach-flat
spectator and flat gauge-curvature terms remain; the scalar/trace block has
vanished.

## Exact Berger stationary/Gauss system

Lift the certified fixture

\[
a=1,\qquad q=c^2=\frac9{40},\qquad
R=\frac{151}{80},\qquad B_t=\frac34
\]

with \(W=A=0\) and \(\rho=f\). The rows

\[
(E_{00},E_{\rm horizontal},E_{\rm vertical},E_\rho,E_A^0)
\]

form

\[
\begin{pmatrix}
\frac{961}{9600}&\frac{22801}{6400}&-\frac{151}{960}&-\frac9{32}&-\frac14\\
\frac{403}{9600}&\frac{20083}{6400}&\frac3{320}&-\frac9{32}&\frac14\\
\frac{31}{1920}&-\frac{3473}{1280}&\frac{133}{960}&-\frac9{32}&\frac14\\
0&0&\frac{151}{480}&-\frac9{16}&1\\
0&0&0&1&0
\end{pmatrix}.
\]

It has rank four. The exact rank witness is

\[
\frac{2120493}{40960000}\ne0,
\]

and its complete kernel is

\[
t\left(
0,-\frac{1600}{22801},-\frac{480}{151},0,1
\right).
\]

In particular,

\[
\boxed{Z_\theta=0.}
\]

This failure is isolated cleanly from the inherited geometry. The certified
positive ungauged Berger clock has coefficient vector

\[
\left(5,0,1,1,\frac{119}{480}\right).
\]

It annihilates the first four metric/radial rows exactly. The new normalized
compact-Gauss row evaluates to \(1\). Thus the positive fixture is rejected
precisely because its global phase has been gauged, not because the imported
Berger curvature or sign conventions drifted.

The result is not an artifact of choosing flat spatial connections. The
temporal internal equation is

\[
\nabla_b\left(\zeta_AH_A^{ba}+\chi F_W^{ba}\right)
=Z_\theta B^a.
\]

Its integral over closed \(S^3\) has no boundary flux. Therefore every smooth
stationary homogeneous clock lift with \(B_t\ne0\), including invariant
magnetic sectors, obeys \(Z_\theta=0\).

## Principal forms and charges

The transverse Abelian kinetic matrix is

\[
K_{\rm vec}=
\begin{pmatrix}
\zeta_W&\chi\\
\chi&\zeta_A
\end{pmatrix},
\qquad
\det K_{\rm vec}=\zeta_W\zeta_A-\chi^2.
\]

It can have a healthy Maxwell cone when

\[
\zeta_W>0,\qquad
\zeta_A>0,\qquad
\zeta_W\zeta_A-\chi^2>0.
\]

That does not repair the scalar gate. The scale Stückelberg coefficients are

\[
M_{\rm eff}^2=-\frac{\kappa_Rf^2}{6},
\qquad
M_W^2=(\kappa_R-\kappa_r)f^2,
\]

and the phase Stückelberg residue is

\[
Z_\theta=\kappa_\theta f^2.
\]

The independent scale branch sets all three scalar coefficients to zero.
The Berger Gauss row sets \(Z_\theta=0\) independently.

Before gauging, the phase current would be

\[
J_\theta^a=-Z_\theta B^a.
\]

After gauging,

\[
Q_{\rm int}
=\int_{S^3}n_aJ_\theta^a
=\text{boundary flux}
=0.
\]

Accordingly the phase contribution to the raw \(D\)-moment map is
\(\beta\,\delta Q_{\rm int}=0\). The scale-gauge contribution is likewise a
constraint charge without a boundary term on closed \(S^3\). This is not a
positive physical clock charge.

## Terminal disposition

The two complete scale strata are:

1. \(\Delta\ne0\): three independent gauge columns and a new dressed-trace
   gauge direction, but the Ward ideal sets
   \(\kappa_r=\kappa_R=\kappa_\theta=\lambda=0\).
2. \(\Delta=0\): the candidate scale column is reducible against the original
   Weyl and compact columns and adds no dressed-trace gauge direction.

Independently, the compact Gauss law eliminates the nonzero homogeneous phase
charge on closed \(S^3\). The declared minimal separated scale/\(U(1)\) good
locus is therefore empty. No causal or nonlinear completion is activated.

## Claim boundary

This result covers one formal-polar complex compensator, one real scale
connection, one compact internal connection, the displayed gauge
representation, the complete declared minimal parity-even terms, and the
certified cylinder/Berger homogeneous fixtures on closed \(S^3\).

It does not exclude charged source sectors, a second modulus, extra
compensators, nontrivial boundaries, higher derivatives, nonstationary
electric sectors, other backgrounds or general metric-affine geometry. It
selects no action and establishes no causal parent, nonlinear \(q_2\),
Hadamard state, anomaly/QME result, particle space, scattering, positivity or
unitarity theorem.

EVIDENCE: `d_quotient_classical/receipts/COMPENSATOR_COMPLEX_SCALE_U1_CONNECTION_PREFLIGHT_V1_TIER_RECEIPT.json`

CLOSE-OUT: DONE — exact rank/Ward elimination and an independent compact-Gauss
constraint prove that the separated minimal connection architecture cannot
simultaneously gauge the dressed trace and retain the closed-\(S^3\) phase
clock.
