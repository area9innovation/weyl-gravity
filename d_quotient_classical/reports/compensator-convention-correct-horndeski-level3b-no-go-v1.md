# Convention-correct quartic-Horndeski Level-3b no-go

## Result

The physically intended family uses the project convention

\[
X=\widehat g^{ab}\partial_a\theta\partial_b\theta
\]

and the exact action

\[
\begin{aligned}
S={}&S_{P_2}
+\int\sqrt{-\widehat g}\bigg\{
F(X)\widehat R\\
&\qquad
-2F_X\left[(\widehat\Box\theta)^2
-(\widehat\nabla_a\widehat\nabla_b\theta)^2\right]
\bigg\},
\end{aligned}
\]

where

\[
F(X)=f_0+f_1X
\]

and the Level-2 braiding coefficient is zero.

The corrected action is exactly Horndeski-degenerate.  Nevertheless its
complete common cylinder/Berger seven-gate good locus is empty:

\[
\boxed{\mathcal L_{\rm Level\,3b}^{\rm good}=\varnothing.}
\]

The obstruction is already complete on the constant-clock cylinder, so no
Berger coefficient sample or inherited Berger background is used.

## Independent Horndeski degeneracy

On

\[
ds^2=-N^2dt^2+a^2\delta_{ij}dx^idx^j,
\qquad
\theta=\nu t,
\]

define

\[
h=\frac{\dot a}{aN},
\qquad
A=\frac{\dot N}{N^2},
\qquad
X=-\frac{\nu^2}{N^2}.
\]

The two exact ingredients are

\[
\sqrt{-g}F(X)R
\;\longmapsto\;
Na^3[-6Fh^2+12XF_XAh],
\]

and

\[
(\Box\theta)^2-(\nabla\nabla\theta)^2
=-6Xh^2+6XAh.
\]

With coefficient \(-2F_X\), all \(Ah\) terms cancel:

\[
\frac{\mathcal L_{\rm vel}}{Na^3}
=-6(F-2XF_X)h^2.
\]

Thus

\[
H_{\rm vel}=
\begin{pmatrix}
-12(F-2XF_X)&0\\
0&0
\end{pmatrix},
\qquad
\det H_{\rm vel}=0,
\]

with exact lapse-velocity null vector \((0,1)\).  This rederives degeneracy in
the repository convention; it does not import the standard
\(X_{\rm std}=-X/2\) formula as an assumption.

## Complete cylinder stationary locus

Absorb the constant \(f_0\) into

\[
M_{P,\mathrm{eff}}^2=M_P^2+2f_0.
\]

In coefficient order

\[
(\alpha_B,\alpha_R,M_{P,\mathrm{eff}}^2,p_0,p_1,p_2,f_1),
\]

the two cylinder Euler rows are

\[
\begin{pmatrix}
0&36&3&1&0&0&0\\
0&12&-1&-1&0&0&0
\end{pmatrix}.
\]

The \(f_1\) column is exactly zero because
\(d\bar\theta=0\).  The matrix has rank two and the complete solution is

\[
M_{P,\mathrm{eff}}^2=-24\alpha_R,
\qquad
p_0=36\alpha_R,
\]

with

\[
\alpha_B,\alpha_R,p_1,p_2,f_1
\]

free.  Every common cylinder/Berger stationary vector is a subset of this
complete cylinder locus.

## Full cylinder quadratic effect

For linear \(F\), the boundary identity is

\[
f_1\left[
XR-2\big((\Box\theta)^2-(\nabla\nabla\theta)^2\big)
\right]
=-2f_1G_{ab}\nabla^a\theta\nabla^b\theta
\pmod{d_h}.
\]

Since \(d\bar\theta=0\), the \(f_1\) contribution has:

```text
pure metric Hessian       ZERO
metric-clock mixed block  ZERO
clock-clock block         -4 f1 G_bar^{ab} k_a k_b
```

On \(\mathbb R\times S^3\),

\[
\bar G^{00}=3,
\qquad
\bar G^{ij}=-\gamma^{ij}.
\]

Including the \(p_1X\) term, the exact clock symbol is

\[
-2(p_1+6f_1)\omega^2
+2(p_1+2f_1)|k|^2.
\]

The time and spatial rank surfaces are respectively

\[
p_1+6f_1=0,
\qquad
p_1+2f_1=0.
\]

These surfaces cannot affect the metric trace/lapse block.

## Complete two-stratum obstruction

The cylinder stationary locus has exactly two disjoint strata.

### \(\alpha_R\ne0\)

The \(R^2\) auxiliary trace block has velocity matrix

\[
K_{\rm tr}=
\begin{pmatrix}
0&-3\\
-3&0
\end{pmatrix}.
\]

Under the exact rational change

\[
P=
\begin{pmatrix}
1&1\\
1&-1
\end{pmatrix},
\]

\[
P^TK_{\rm tr}P=
\operatorname{diag}(-6,6).
\]

The corrected Horndeski slope appends only a clock diagonal and cannot alter
this split inertia.  The raw-\(D\) witnesses \(+3\) and \(-3\) remain.

### \(\alpha_R=0\)

Cylinder stationarity forces

\[
M_{P,\mathrm{eff}}^2=p_0=0.
\]

The remaining \(C^2\) metric action is trace-free.  The \(p_1,p_2\) and
\(f_1\) terms are clock-only at quadratic order.  Therefore the imported
arbitrary compact-support dressed-trace class

\[
u=\phi_{\rm trace}-2\tau
\]

and its dual nonmembership functional survive by direct-sum extension.  No
complete advanced/retarded chain homotopy exists on this branch.

The two strata exhaust the cylinder locus, so their common good locus is
empty.  Intersecting with any Berger stationary locus cannot reopen it.

## Unary, constraint and charge boundary

The new term introduces no gauge generator:

\[
Q\widehat g=\mathcal L_\xi\widehat g,
\qquad
Q\theta=\mathcal L_\xi\theta.
\]

The homogeneous lapse-velocity null vector is the Horndeski primary
constraint.  On the cylinder the metric and constraint rows remain those of
the \(P_2\) family; only the clock principal entry changes.

The shift current is

\[
j^a
=2P_X\nabla^a\theta
-4f_1G^{ab}\nabla_b\theta.
\]

No Berger current or \(K_{\rm Berger}\) charge is promoted because no
coefficient survives the prior cylinder physical gate.

## Claim boundary

This theorem covers the complete linear-\(F\), convention-correct quartic
Horndeski family with quadratic \(P(X)\), zero braiding, the constant-clock
unit cylinder and the requirement of one action passing both cylinder and
Berger gates.

It does not compute a Berger stationary locus, because the complete cylinder
good locus is already empty.  It is not a no-go for higher \(F\), \(G_5\),
DHOST, independent connections, extra fields or other backgrounds.  It
selects no action and establishes no full causal parent, nonlinear \(q_2\),
Hadamard state, anomaly/QME result, particle space, scattering, positivity or
unitarity theorem.

## Next gate

The convention-correct Level-3b mechanism is terminal at the cylinder gate.
The independently gauged Weyl-connection Level 4 may now be activated under
a fresh authoritative item.

EVIDENCE: `d_quotient_classical/receipts/COMPENSATOR_CONVENTION_CORRECT_HORNDESKI_LEVEL3B_NO_GO_V1_TIER_RECEIPT.json`

CLOSE-OUT: DONE — the corrected family is Horndeski-degenerate, but every
coefficient on its complete cylinder stationary locus has either split
\(R^2\) inertia or surviving compact-support dressed-trace homology.
