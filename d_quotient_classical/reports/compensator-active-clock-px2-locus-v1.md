# Quadratic active-clock compensator locus

## Verdict

For the complete declared quadratic shift-symmetric clock enlargement,

\[
P(X)=p_0+p_1X+p_2X^2,\qquad
X=\widehat g^{ab}\partial_a\theta\,\partial_b\theta,
\]

the exact common stationary locus of the unit cylinder and frozen Berger
clock is one-dimensional, but its seven-gate good locus is empty:

\[
\boxed{
\mathcal L_{\mathrm{stationary}}
=\mathbb R\,v,\qquad
\mathcal L_{\mathrm{good}}^{P_2}=\varnothing .
}
\]

No `Candidate C_active` action or action hash is exported.

This is a scoped `LOCAL-ALGEBRAIC`/`LORENTZIAN-CAUSAL` result for one declared
action truncation on two frozen backgrounds. It is not a universal
k-essence, scalar-tensor or compensator no-go.

## Imported gate

The calculation imports
`COMPENSATOR_MINIMAL_ACTION_CLASSIFICATION_AFTER_NEITHER_V1` by the exact
content hash

```text
41ce6db6ab8fc58f4cc1ecedb205f732fd3dcee645f9408506d3535545f7026a
```

from scientific commit
`a5924e707352bab92db2caa4c19cf4223c60f0e3`. The preceding theorem excluded
active-clock retunings; it is used as the boundary of the enlarged ansatz,
not as a substitute for recomputing its Berger equations.

## Complete declared action

Modulo integration by parts, four-dimensional curvature identities, the
Euler density and the invertible algebraic \(R^2\) auxiliary presentation,
the action is

\[
S=\int\operatorname{vol}_{\widehat g}\left[
\frac{\alpha_B}{8}C^2+\alpha_RR^2+\frac{M_P^2}{2}R
+p_0+p_1X+p_2X^2+\alpha_EE_4
\right].
\]

The coefficient order is

\[
x=(\alpha_B,\alpha_R,M_P^2,p_0,p_1,p_2)^T.
\]

There is no HT sector, multiplier, new field, fixed-charge quotient or
enlarged gauge group. Shift symmetry and the declared polynomial degree bound
make \(1,X,X^2\) the complete phase basis. Higher powers of \(X\), higher
derivatives of \(\theta\), \(\theta\)-dependent coefficients and independent
conformal connections are outside the theorem.

## Background Euler equations

For

\[
T_{ab}=-2P_X\partial_a\theta\partial_b\theta+Pg_{ab},
\]

the metric and clock equations are

\[
\alpha_BB_{ab}
+\alpha_R(4R\,\mathrm{Ric}_{ab}-R^2g_{ab})
+M_P^2G_{ab}-T_{ab}=0,
\]

\[
\nabla_a(P_X\nabla^a\theta)=0.
\]

On the unit cylinder, \(\theta\) is constant and \(X=0\). The two independent
metric rows are

\[
\begin{pmatrix}
0&36&3&1&0&0\\
0&12&-1&-1&0&0
\end{pmatrix}x=0.
\]

Thus

\[
M_P^2=-24\alpha_R,\qquad
p_0=36\alpha_R=-\frac32M_P^2.
\]

On the frozen Berger clock,

\[
q=c^2=\frac9{40},\qquad
\omega=\frac34,\qquad
X=-\frac9{16},\qquad
R=\frac{151}{80},
\]

the \(00\), horizontal and vertical rows are

\[
\begin{pmatrix}
\frac{961}{9600}&\frac{22801}{6400}&\frac{151}{160}
 &1&\frac9{16}&-\frac{243}{256}\\
\frac{403}{9600}&\frac{20083}{6400}&-\frac9{160}
 &-1&\frac9{16}&-\frac{81}{256}\\
\frac{31}{1920}&-\frac{3473}{1280}&-\frac{133}{160}
 &-1&\frac9{16}&-\frac{81}{256}
\end{pmatrix}x=0.
\]

These are newly derived \(P(X)\) rows; the old five-by-five determinant was
not reused. The clock equation passes because \(X\), \(P_X\) and the
stationary gradient are constant.

The stacked five-by-six matrix has

\[
\operatorname{rank}M=5,\qquad
\det M_{[:,0:5]}=\frac{91791}{40960}\ne0.
\]

Its exact kernel is

\[
x=t\left(
\frac{81}{20},
\frac{27}{3290},
-\frac{324}{1645},
\frac{486}{1645},
\frac{18}{25},
1
\right),\qquad t\in\mathbb R.
\]

Equivalently, an integer generator is

\[
(133245,270,-6480,9720,23688,32900).
\]

There are only two real strata: \(t=0\), the zero action, and \(t\ne0\), on
which the \(R^2\) auxiliary presentation and clock coefficients are nonzero.

## Complete homogeneous Hessian

For \(t\ne0\), set

\[
\chi=2\alpha_RR,\qquad
\psi=\chi+\frac{M_P^2}{2},\qquad
M_P^2=-\frac{324}{1645}t.
\]

Writing the clock fluctuation as \(v\), the complete homogeneous quadratic
density is

\[
L_{\rm hom}
=-3\dot\psi\dot u-6\psi u+\frac6{M_P^2}\psi^2
-p_1\dot v^2,\qquad p_1=\frac{18}{25}t.
\]

The velocity Hessian in the basis \((u,\psi,v)\) is

\[
V=
\begin{pmatrix}
0&-3&0\\
-3&0&0\\
0&0&-\frac{36}{25}t
\end{pmatrix}.
\]

Therefore

\[
\operatorname{inertia}V=
\begin{cases}
(1,2,0),&t>0,\\
(2,1,0),&t<0.
\end{cases}
\]

The exact eigenpair \(+3,-3\) remains for every nonzero \(t\). The physical
sign failure is therefore not repaired by the clock.

The integrated Euler Hessian is

\[
H(D)=
\begin{pmatrix}
0&3(D^2-2)&0\\
3(D^2-2)&12/M_P^2&0\\
0&0&\frac{36}{25}tD^2
\end{pmatrix},
\]

with

\[
\det H(D)=-\frac{324}{25}tD^2(D^2-2)^2.
\]

On the state basis
\((u,\dot u,\psi,\dot\psi,v,\dot v)\), the characteristic and minimal
polynomials are both

\[
\lambda^2(\lambda^2-2)^2.
\]

There is a size-two clock block at \(0\) and size-two scalar blocks at
\(\pm\sqrt2\).

In the project convention, the Lee--Wald current and raw-\(D\) Hamiltonian are

\[
\omega^0=-3\left[
\delta u\wedge\delta\dot\psi+
\delta\psi\wedge\delta\dot u
\right]-2p_1\delta v\wedge\delta\dot v,
\]

\[
H_D=-3\dot u\dot\psi+6\psi u-\frac6{M_P^2}\psi^2
-p_1\dot v^2.
\]

Already at \(v=\dot v=u=\psi=0\),

\[
(\dot u,\dot\psi)=(1,-1)\Rightarrow H_D=3,\qquad
(\dot u,\dot\psi)=(1,1)\Rightarrow H_D=-3.
\]

This independently fails the physical-sign and raw-\(D\) gates.

## Exact clock cone

The principal clock tensor is

\[
K^{ab}=P_Xg^{ab}
+2P_{XX}\nabla^a\theta\nabla^b\theta .
\]

On the stationary locus at the Berger fixture,

\[
P_X=-\frac{81}{200}t,\qquad
P_X+2XP_{XX}=-\frac{531}{200}t.
\]

Standard-sign clock propagation requires both quantities to be negative, so

\[
t>0.
\]

The sound speed is exact and subluminal:

\[
c_s^2=\frac{P_X}{P_X+2XP_{XX}}=\frac9{59}.
\]

The clock gradient is timelike and monotone,

\[
X=-\frac9{16}<0,\qquad \dot\theta=\frac34.
\]

On the unit cylinder, however, the constant-clock quadratic density is

\[
L_{\rm clock}^{\rm cyl}=-p_1\dot v^2,
\]

whose standard-sign condition is \(p_1<0\), hence \(t<0\). Thus the two
backgrounds give the exact independent separator

\[
\{t<0\}\cap\{t>0\}=\varnothing.
\]

This separator is additional to the immutable split gravity--auxiliary pair.

## Raw-\(D\) and \(K_{\rm Berger}\) charges

With the declared shift-current convention,

\[
j^a=2P_X\nabla^a\theta,
\qquad
Q_R=-2P_X\omega=\frac{243}{400}t
\]

per unit Berger volume. The matter densities are

\[
\rho_{\rm clock}
=-2P_X\omega^2-P
=\frac{523827}{2105600}t,
\]

\[
\rho_{\rm clock}-\omega Q_R
=-P
=-\frac{435537}{2105600}t.
\]

For the total closed-background covariant phase space,

\[
K_{\rm Berger}=D-\omega R,\qquad
\iota_{\mathcal L_K}\Omega_{\rm total}=0,\qquad
\iota_{\mathcal L_D}\Omega_{\rm total}
=\omega\,\delta Q_R.
\]

The earlier fixed-coupling proof that \(\delta Q_R=0\) used the different
linear-clock action and is deliberately not imported as a conclusion for
this \(P(X)\) theory. No spatial surface charge is present on closed \(S^3\);
the internal current is conserved by the displayed clock equation. The
raw-\(D\) gate is already decided by the exact both-sign unit-cylinder
Hamiltonian.

## Seven-gate result

The exact dispositions are:

1. the complete invariant action is explicit; no selected-action all-row
   \(q_2\) is exported after the terminal failure;
2. for \(t\ne0\), the \(R^2\) auxiliary scalar replaces the compact-support
   trace, but is physical and unhealthy;
3. the complete support-local mixed causal parent is not promoted after gate
   5 fails;
4. the reduced action-derived Lee--Wald form is nondegenerate but split;
5. every real stationary point fails: \(t=0\) has no dynamics, and \(t\ne0\)
   retains the \((+3,-3)\) pair; the two clock-health half-lines are also
   disjoint;
6. raw \(D\) is charged on the declared unit-cylinder ambient sector;
7. all stationary Euler rows pass, while a healthy monotone Berger clock
   exists only on \(t>0\).

Consequently no point passes all seven gates simultaneously. No numerical
scan or fitted sample enters the proof.

## Reproduction

```bash
python3 d_quotient_classical/compensator/active_clock_px2_locus.py --check
python3 d_quotient_classical/compensator/verify_active_clock_px2_locus.py
python3 -m unittest \
  d_quotient_classical.compensator.tests.test_active_clock_px2_locus -v
npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true \
  -s d_quotient_classical/schema/compensator-active-clock-px2-locus-v1.schema.json \
  -d d_quotient_classical/certificates/COMPENSATOR_ACTIVE_CLOCK_PX2_LOCUS_V1.json
python3 d_quotient_classical/atlas/generate_classical_atlas_fragment.py --check
python3 d_quotient_classical/atlas/verify_classical_atlas_fragment.py
python3 -m unittest \
  d_quotient_classical.atlas.tests.test_classical_atlas_fragment -v
```

CLOSE-OUT: DONE — the complete declared quadratic active-clock stationary
locus is exact and its seven-gate good locus is empty.

EVIDENCE:
`d_quotient_classical/receipts/COMPENSATOR_ACTIVE_CLOCK_PX2_LOCUS_V1_TIER_RECEIPT.json`
