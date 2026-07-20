# Minimal compensator-action classification after NEITHER

## Verdict

The seven-gate good locus is empty in the declared minimal action class:

\[
\boxed{\mathcal L_{\mathrm{good}}^{\mathrm{minimal}}=\varnothing.}
\]

No Candidate C action or action hash is exported.

This is a scoped `LOCAL-ALGEBRAIC`/`LORENTZIAN-CAUSAL` theorem. It covers the
formal \(\rho\ne0\) polar complex compensator with four metric derivatives,
at most two compensator derivatives, one algebraic presentation of \(R^2\),
and an optional minimal Henneaux--Teitelboim sector under the small reducible
three-form gauge group.

## Complete declared action

Modulo integration by parts, four-dimensional curvature identities, the
Euler density and invertible algebraic auxiliary-field presentations, the
parity-even dressed action is

\[
\begin{aligned}
S_{\rm bulk}
=\int\operatorname{vol}_{\widehat g}\biggl[
&\frac{\alpha_B}{8}C^2+\alpha_RR^2
+\frac{M_P^2}{2}R
-\frac{Z_\theta}{2}(\nabla\theta)^2-V_0
+\alpha_E E_4\biggr],\\
S_{\rm HT}
=\epsilon_{\rm HT}\int
&\lambda_{\rm HT}
\left(\operatorname{vol}_{\widehat g}-dA_3\right),
\qquad \epsilon_{\rm HT}\in\{0,1\}.
\end{aligned}
\]

Every nonzero HT coefficient is normalized to one by rescaling the
multiplier. The coefficient vector relevant to local Euler equations is

\[
x=(\alpha_B,\alpha_R,M_P^2,Z_\theta,V_0)^T.
\]

\(E_4\) is topological, \(\Box R\) is horizontally exact, and Pontryagin is
parity odd. The action class is exactly the minimal family frozen by
`COMPLEX_COMPENSATOR_ACTION_QUARTET_PREFLIGHT_V1`. Higher-than-two-derivative
phase operators, multiplier kinetic/potential extensions, global
three-form quotients, fixed-flux sectors and independent conformal
connections are explicitly outside this theorem.

## Exact stationary separator without the HT sector

For constant \(R\) and covariantly constant clock gradient, the orthonormal
Euler equation is

\[
\alpha_B B_{ab}
+\alpha_R(4R\,\operatorname{Ric}_{ab}-R^2g_{ab})
+M_P^2G_{ab}
-T_{ab}[Z_\theta,V_0]=0.
\]

On the unit cylinder with constant \(\theta\), the two independent rows are

\[
\begin{pmatrix}
0&36&3&0&-1\\
0&12&-1&0&1
\end{pmatrix}x=0.
\]

Equivalently,

\[
M_P^2=-24\alpha_R,\qquad
V_0=\frac32M_P^2=-36\alpha_R.
\]

On the frozen Berger clock

\[
a=1,\quad q=c^2=\frac9{40},\quad
\omega=\frac34,\quad R=\frac{151}{80},
\]

the \(00\), horizontal and vertical rows are

\[
\begin{pmatrix}
\frac{961}{9600}&\frac{22801}{6400}&\frac{151}{160}&-\frac9{32}&-1\\
\frac{403}{9600}&\frac{20083}{6400}&-\frac9{160}&-\frac9{32}&1\\
\frac{31}{1920}&-\frac{3473}{1280}&-\frac{133}{160}&-\frac9{32}&1
\end{pmatrix}x=0.
\]

Stacking the cylinder and Berger rows gives a square rational matrix with

\[
\det M_{\rm cyl+Berger}=-\frac{91791}{81920}\ne0,
\qquad
\operatorname{rank}M_{\rm cyl+Berger}=5.
\]

Its exact RREF is \(I_5\). Therefore

\[
x=0
\]

is the only common stationary vector in the no-HT family. That vector has no
phase pairing and leaves the conformal trace without a causal parent; it
cannot pass the seven gates.

Two independent regression controls prevent a convention accident:

* the original positive Berger vector
  \[
  (5,0,-1/6,1,119/1920)
  \]
  annihilates the Berger rows but not the cylinder rows;
* Candidate A
  \[
  (5,-1/144,1/6,1,1/4)
  \]
  annihilates the cylinder rows but not the Berger rows.

## Cylinder scalar Hessian

The cylinder equations also give an independent physical separator. For
\(\alpha_R\ne0\), introduce

\[
\chi=2\alpha_RR,\qquad
\psi=\chi+\frac{M_P^2}{2}.
\]

The complete homogeneous trace/auxiliary quadratic density is

\[
L_{\rm hom}
=-3\dot\psi\dot u-6\psi u+\frac6{M_P^2}\psi^2.
\]

Its velocity Hessian is

\[
\begin{pmatrix}0&-3\\-3&0\end{pmatrix},
\qquad \operatorname{inertia}=(1,1),
\]

and the exact \(D\)-evolution has characteristic and minimal polynomial

\[
(\lambda^2-2)^2.
\]

Thus the roots are real \(\pm\sqrt2\), each with a size-two Jordan block.
The raw-\(D\) Hamiltonian

\[
H_D=-3\dot u\dot\psi+6\psi u-\frac6{M_P^2}\psi^2
\]

takes both signs already at
\((u,\dot u,\psi,\dot\psi)=(0,1,0,\mp1)\).

If \(\alpha_R=0\), cylinder stationarity instead forces
\(M_P^2=V_0=0\). The metric action is then conformal in the trace sector, so
the imported compact-support dressed-trace obstruction remains. These two
branches independently fail gates 5 or 2/3.

## Why the HT branch cannot evade the separator

When \(\epsilon_{\rm HT}=1\), the background multiplier can shift the
effective potential separately on the two backgrounds, so it would be
incorrect to reuse the preceding determinant as if \(\lambda_{\rm HT}\)
were fixed.

The obstruction is instead global. In the ordered basis
\((u,a,\lambda_{\rm HT})\),

\[
H_{\rm HT}(D)=
\begin{pmatrix}
0&0&2\\
0&0&D\\
2&-D&0
\end{pmatrix},
\qquad
H_{\rm HT}(D)(D/2,1,0)^T=0.
\]

Its characteristic and generic minimal polynomial is

\[
\lambda(\lambda^2+D^2-4).
\]

Adding the \(R^2\) auxiliary scalar gives a combined determinant

\[
\det H_{\rm combined}=-9D^2P^2,
\]

so the harmonic \(D=0\) three-form direction survives every such mixing.
Globally,

\[
H^3(\mathbb R\times S^3)=\mathbb R,\qquad
H_c^4(\mathbb R\times S^3)=\mathbb R.
\]

The ambient Lee--Wald pair and raw-\(D\) Hamiltonian are

\[
\Omega_{\rm top}=\delta a\wedge\delta\lambda_{\rm HT},
\qquad
H_D=V_{S^3}\lambda_{\rm HT}.
\]

On Berger, the volume constraint requires
\(\bar A_3=t\,\operatorname{vol}_{\rm Berger}\), hence

\[
\mathcal L_D\bar A_3=\operatorname{vol}_{\rm Berger},
\]

which is not exact under the declared small gauge group. The HT branch
therefore fails gates 3, 5, 6 and 7 unless one changes the theory by imposing
a superselection condition or a global quotient.

## Complete branch classification

\[
\begin{array}{c|c|c}
\text{branch}&\text{exact separator}&\text{verdict}\\ \hline
\epsilon_{\rm HT}=0&
\det M_{\rm cyl+Berger}\ne0&
\text{only the dynamically empty vector}\\
\epsilon_{\rm HT}=1&
H^3/H_c^4,\ H_D,\ [\operatorname{vol}_{\rm Berger}]\ne0&
\text{global gates fail}
\end{array}
\]

Consequently no coefficient point passes all seven gates. No score,
numerical scan or preferred sample enters the proof.

## Reproduction

```bash
python3 d_quotient_classical/compensator/minimal_action_classification_after_neither.py --check
python3 d_quotient_classical/compensator/verify_minimal_action_classification_after_neither.py
python3 -m unittest d_quotient_classical.compensator.tests.test_minimal_action_classification_after_neither -v
npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true \
  -s d_quotient_classical/schema/compensator-minimal-action-classification-after-neither-v1.schema.json \
  -d d_quotient_classical/certificates/COMPENSATOR_MINIMAL_ACTION_CLASSIFICATION_AFTER_NEITHER_V1.json
```

CLOSE-OUT: DONE — the declared minimal family has an exact empty seven-gate
coefficient locus; no Candidate C or selected-action consumer is exported.

EVIDENCE: `d_quotient_classical/receipts/COMPENSATOR_MINIMAL_ACTION_CLASSIFICATION_AFTER_NEITHER_V1_TIER_RECEIPT.json`
