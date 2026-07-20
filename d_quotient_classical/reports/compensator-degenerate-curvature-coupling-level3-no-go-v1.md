# Minimal degenerate-curvature Level-3 no-go

## Result

The terminal Level-2 no-go is imported by exact hash and exports no selected
action.  The isolated Level-3 family requested by the work item is

\[
\begin{aligned}
S={}&S_{P_2}[\alpha_B,\alpha_R,M_P^2,p_0,p_1,p_2]\\
&+\int\sqrt{-\widehat g}\left\{
F(X)\widehat R+
F_X\left[(\widehat\Box\theta)^2
-(\widehat\nabla_a\widehat\nabla_b\theta)^2\right]\right\},
\end{aligned}
\]

with

\[
X=\widehat g^{ab}\partial_a\theta\partial_b\theta,
\qquad
F(X)=f_0+f_1X,
\]

and the failed Level-2 braiding coefficient set to zero.

In this convention the displayed plus coefficient is not degenerate.  On the
active-clock locus \(X<0\), its homogeneous ADM velocity Hessian obeys

\[
\boxed{\det H_{\rm vel}=-324X^2f_1^2.}
\]

Hence every genuinely new stratum \(f_1\ne0\) fails the first invariant gate.
The only degenerate literal stratum is \(f_1=0\), where \(f_0\widehat R\) is
absorbed by

\[
M_{P,\mathrm{eff}}^2=M_P^2+2f_0.
\]

That is precisely a member of the already complete \(P_2\) family, whose good
locus is empty.  Therefore

\[
\boxed{\mathcal L_{\rm Level\,3,literal}^{\rm good}=\varnothing.}
\]

No selected action, full unary complex or nonlinear \(q_2\) is exported.

## Exact degeneracy calculation

Use the flat homogeneous ADM fixture

\[
ds^2=-N^2dt^2+a^2\delta_{ij}dx^idx^j,
\qquad
\theta=\nu t,
\]

and define

\[
h=\frac{\dot a}{aN},
\qquad
A=\frac{\dot N}{N^2},
\qquad
X=-\frac{\nu^2}{N^2}.
\]

The exact identities are

\[
R=6(Dh+2h^2),
\]

and

\[
(\Box\theta)^2-(\nabla_a\nabla_b\theta)^2
=-6Xh^2+6XAh.
\]

Since \(\dot X=-2NAX\), integration by parts gives

\[
\sqrt{-g}F(X)R
\;\longmapsto\;
Na^3\left[-6Fh^2+12XF_XAh\right].
\]

For an initially independent coefficient \(B\) on the Hessian-square
difference, the complete velocity density is

\[
\frac{\mathcal L_{\rm vel}}{Na^3}
=-6(F+BX)h^2+6X(2F_X+B)Ah.
\]

Thus

\[
H_{\rm vel}=
\begin{pmatrix}
-12(F+BX)&6X(2F_X+B)\\
6X(2F_X+B)&0
\end{pmatrix},
\]

and

\[
\det H_{\rm vel}
=-36X^2(2F_X+B)^2.
\]

For an active clock, the unique generalized degeneracy surface is

\[
B=-2F_X.
\]

Intersecting this surface with the literal work-item identification
\(B=F_X\) gives the exact ideal

\[
(B-F_X,\;B+2F_X)=(B-F_X,\;3F_X),
\]

so over characteristic zero the intersection is \(B=F_X=0\).  The certificate
stores the Gröbner elimination and the rank strata.

## Convention control

The familiar Horndeski normalization normally uses

\[
X_{\rm std}=-\frac12(\nabla\theta)^2.
\]

After converting to this project’s \(X=(\nabla\theta)^2\), its second-derivative
coefficient is \(-2F_X\), not \(+F_X\).  For linear \(F\),

\[
F_X\left[
XR-2\big((\Box\theta)^2-(\nabla\nabla\theta)^2\big)
\right]
=-2F_XG_{ab}\nabla^a\theta\nabla^b\theta
\pmod{d_h}.
\]

This convention-correct expression is stored as a control, not silently
substituted into the declared action.  On the constant-clock cylinder its
pure-metric and metric--clock mixed Hessian blocks vanish.  It therefore does
not change the trace/lapse block that this work item asked the new mechanism
to repair.  The control is not a full coefficient-locus theorem on the Berger
background and is not a general Horndeski/DHOST no-go.

## Fail-closed gate disposition

The novel literal stratum fails at action degeneracy.  Consequently the
following downstream objects are explicitly `NOT_REACHED`:

- the full action-origin Euler/antifield unary rows;
- both background Euler systems for a surviving novel action;
- scalar and tensor principal symbols;
- constraint ranks and reduced pairings;
- characteristic roots, charges and clock inequalities.

The kinematic gauge rows remain the unchanged Diff\(\times\)Weyl rows in
dressed variables:

\[
Q\widehat g=\mathcal L_\xi\widehat g,
\qquad
Q\theta=\mathcal L_\xi\theta,
\]

with trivial Weyl action on \((\widehat g,\theta)\).  This is not a full unary
export for the rejected action.

## Claim boundary

This theorem covers only the literal Level-3 family written above: linear
\(F(X)\), quadratic \(P(X)\), coefficient \(+F_X\), zero braiding, Lorentzian
signature and the active-clock locus.  It proves a scoped empty good locus at
the first exact separator.

It does not prove a general Horndeski or DHOST no-go.  It does not construct a
support-local causal parent, full BV unary complex, nonlinear \(q_2\), Hadamard
state, anomaly/QME result, particle space, scattering theory, positivity or
unitarity theorem.

## Next gate

Activate the independently gauged geometric-variable mechanism.  If the
convention-correct \(-2F_X\) family is wanted as an independent scientific
question, it must receive a new work item rather than being substituted
silently into this result.

EVIDENCE: `d_quotient_classical/receipts/COMPENSATOR_DEGENERATE_CURVATURE_COUPLING_LEVEL3_NO_GO_V1_TIER_RECEIPT.json`

CLOSE-OUT: DONE — the complete literal Level-3 active-clock family has no
novel degenerate stratum, and its collapsed stratum is the terminal imported
\(P_2\) no-go.
