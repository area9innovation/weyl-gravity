# Extended rod–memory–Maxwell unary gate

## Verdict

The existing 64-row gravity–clock–Maxwell complex already has an exact
nilpotent \(q_1\), nondegenerate odd cyclic pairing, and causal advanced and
retarded homotopies. The requested 78-row extension is nevertheless
`INPUT_BLOCKED` on the unchanged Berger background.

This is not caused by the memory readout. For a Maxwell kinetic operator
\(M\), memory transport \(T\), and local readout \(B\), the cyclic Hessian on
the ordered fields \((A,m,p)\) is

\[
K=\begin{pmatrix}
M&0&-B^*\\
0&0&T^*\\
-B&T&0
\end{pmatrix}.
\]

Writing \(G=M^{-1}_{\rm ret}\), \(H=T^{-1}_{\rm ret}\), and
\(J=(T^*)^{-1}_{\rm ret}\), its exact retarded inverse is the finite matrix

\[
G_{\rm ext}=\begin{pmatrix}
G&GB^*J&0\\
HBG&HBGB^*J&H\\
0&J&0
\end{pmatrix}.
\]

The certificate proves both \(KG_{\rm ext}=1\) and
\(G_{\rm ext}K=1\) in the universal noncommutative operator algebra. Thus no
Neumann series or small-coupling assumption is required. If the factors are
retarded and \(B,B^*\) are local compactly supported coefficient operators,
every displayed composition has retarded support.

## Exact fixed-background obstruction

The declared detector rods have standard-sign action

\[
S_R=-\frac12\sum_{I=1}^3\int\sqrt{-\widehat g}\,
\widehat g^{ab}\partial_aR^I\partial_bR^I
\]

and unit relational Jacobian in an orthonormal detector chart. Their three
gradients are

\[
dR^1=(0,1,0,0),\qquad dR^2=(0,0,1,0),\qquad dR^3=(0,0,0,1).
\]

Direct substitution gives

\[
T^R_{\hat a\hat b}
=\operatorname{diag}\left(\frac32,-\frac12,-\frac12,-\frac12\right).
\]

The detector preflight explicitly excludes this order-
\(\epsilon_R^2\) stress from the fixed background. Consequently that
background is off shell for every nonzero rod coupling. The BV Taylor
expansion there is curved, with a nonzero metric \(q_0\); it cannot be
promoted as an uncurved nilpotent extended \(q_1\).

Treating the rods as external probes would avoid the tadpole but would not
satisfy the requested dynamical rod–memory BV extension. Likewise, simply
dropping the stress would destroy action-derived cyclicity.

## Required handoff

The next admissible input is:

1. a backreacted gravity–clock–rod background satisfying every Euler row;
2. its rod Hessian, diffeomorphism action, and BV-adjoint blocks;
3. explicit content-addressed detector operators \(B_a,B_a^*\);
4. explicit memory transport \(T,T^*\) and retarded inverses \(H,J\);
5. exact 78-row checks of \(q_1^2=0\), pairing nondegeneracy, unary
   cyclicity, Green homotopy, Maxwell-gauge compatibility, and
   \(K_{\mathrm{Berger}}\) equivariance.

This result is `LOCAL-ALGEBRAIC` and `LORENTZIAN-CAUSAL`. It is an exact
readiness/obstruction certificate, not an extended apparatus complex, a
backreacted observer model, or a quantum result.

Tier-2 replay on 2026-07-17: certificate reproduction passed in 0.32 seconds,
independent verification in 0.33 seconds, and five mutation/unit tests in
0.37 seconds. Strict Draft 2020-12 validation passed in 2.44 seconds. Tier 3
was not run because no freeze, shared algebra engine, lifecycle promotion,
QME result, release boundary, or paper theorem changed.

Verification:

```bash
python3 -m d_quotient_classical.backreacted_clock.berger_extended_rod_memory_maxwell_unary_gate --check
python3 -m d_quotient_classical.backreacted_clock.verify_berger_extended_rod_memory_maxwell_unary_gate
python3 -m unittest d_quotient_classical.backreacted_clock.tests.test_berger_extended_rod_memory_maxwell_unary_gate -v
```
