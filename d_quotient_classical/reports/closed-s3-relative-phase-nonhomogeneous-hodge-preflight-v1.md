# Closed-(S^3) nonhomogeneous relative-phase Hodge/Gauss preflight

## Result

The homogeneous compact-Gauss mechanism extends to every scalar harmonic on
the round closed (S^3). For (n) fixed-modulus phases, (r) Abelian
connections and an integer charge matrix (Q) of rank (k), the positive
two-derivative branch has

\[
\boxed{n-k}
\]

healthy gauge-invariant relative-phase wave families at every scalar harmonic.
For positive phase and gauge kinetic matrices (M) and (K), the exact
relative metric is

\[
G_{\rm rel}
=
\left(N^T M^{-1}N\right)^{-1},
\qquad
Q^TN=0,
\]

and the relative principal polynomial at
\(λ_\ell=\ell(\ell+2)/a^2\) is

\[
\det(G_{\rm rel})
(\omega^2-\lambda_\ell)^{n-k}.
\]

Thus the neutral counterflow clock is not a peculiarity of the homogeneous
truncation. It propagates as a genuine reduced field mode in the declared
quadratic phase--connection class.

This is a `LOCAL-ALGEBRAIC` and `REDUCED-MODE` theorem. It is not yet a
support-local BV causal parent or Green-homotopy result.

## Hodge decomposition

On the round radius-(a) sphere,

\[
\lambda_\ell=\frac{\ell(\ell+2)}{a^2},
\qquad
\deg Y_\ell=(\ell+1)^2.
\]

For \(\ell\ge1\), the normalized exact one-forms
\(dY_\ell/\sqrt{\lambda_\ell}\) have the same Hodge eigenvalue and
degeneracy. The coexact one-forms have

\[
\mu_\ell
=\frac{(\ell+1)^2}{a^2}
=\lambda_\ell+\frac1{a^2},
\]

curl eigenvalues \(\pm(\ell+1)/a\), and total degeneracy
\(2\ell(\ell+2)\). There are no harmonic one-forms because
\(H^1(S^3)=0\).

## Scalar gauge and Gauss reduction

For one nonzero scalar harmonic, write the exact connection coefficient as
\(a_L\), the temporal multiplier as \(A_0\), and the gauge parameter as
\(\alpha\). With the frozen sign convention,

\[
\delta\theta=Q\alpha,
\qquad
\delta a_L=\sqrt\lambda\,\alpha,
\qquad
\delta A_0=\dot\alpha.
\]

The gauge-invariant combinations are

\[
v=\dot\theta-QA_0,
\quad
w=\sqrt\lambda\,\theta-Qa_L,
\quad
e_L=\dot a_L-\sqrt\lambda\,A_0.
\]

The quadratic scalar block is

\[
L_\ell
=\frac12v^TMv
-\frac12w^TMw
+\frac12e_L^TKe_L,
\]

and variation of (A_0) gives the exact local constraint

\[
Q^TMv+\sqrt\lambda\,Ke_L=0.
\]

Choose (N) as above and the normalized horizontal lift

\[
H=M^{-1}NG_{\rm rel}.
\]

It satisfies

\[
N^TH=1,
\qquad
Q^TMH=0.
\]

Consequently the relative variable \(\psi=N^T\theta\) splits exactly from
the vertical phase and longitudinal connection block. Its Lagrangian is

\[
L_{\rm rel,\ell}
=\frac12\dot\psi^TG_{\rm rel}\dot\psi
-\frac12\lambda_\ell\psi^TG_{\rm rel}\psi,
\]

up to a gauge-invariant lower-order potential Hessian.

## Active and matter-kernel gauge directions

There is an important distinction at nonzero harmonics. If
\(\ker Q\ne0\), those gauge directions act trivially on the phases, but they
do not act trivially on the connection. Hence (r-k) is the kernel of the
matter representation, not reducibility of the full connection gauge
complex.

Let (T) span \(\ker Q\). Orthogonalize a complement (S) with respect to
the positive gauge kinetic form:

\[
S_\perp
=S-T(T^TKT)^{-1}T^TKS.
\]

Then

\[
K_a=S_\perp^TKS_\perp,
\qquad
Q_a=QS_\perp,
\qquad
V=Q_a^TMQ_a
\]

are positive on the (k) matter-active directions. Eliminating (A_0) by
Gauss gives the longitudinal kinetic form

\[
\boxed{
K_L(\lambda)
=
\left(K_a^{-1}+\lambda V^{-1}\right)^{-1}
}
\]

and the frequency-squared operator

\[
\boxed{
\Omega_L^2
=\lambda I+K_a^{-1}V.
}
\]

Thus there are (k) massive vector-longitudinal scalar families. The
(r-k) matter-kernel exact-connection directions are pure gauge plus Gauss
constraint and contribute no physical scalar mode.

For coexact one-forms, all (r) transverse connection families survive, with

\[
\Omega_T^2
=\mu_\ell I+K^{-1}Q^TMQ.
\]

There are (k) massive and (r-k) massless Maxwell families, each in both
curl chiralities.

## Exceptional strata and zero modes

- At \(\ell=0\), no exact spatial one-form exists. (A_0) is a Gauss
  multiplier and the quotient is exactly the homogeneous (n-k)-dimensional
  relative-phase system.
- If (k=0), all phases are relative and all connections are massless.
  There are no physical scalar connection modes.
- If (k=n\), there is no relative phase, although the (k) massive
  vector-longitudinal families remain.
- Nonprimitive Smith factors change finite isotropy, not the continuous mode
  counts.
- For nonsingular indefinite (M), the formula remains meaningful only when
  both (A=N^TM^{-1}N) and the active vertical Gram matrix are nonsingular.
  The relative sector is called healthy exactly when (A^{-1}>0). Singular
  cases require a new Dirac reduction and receive no verdict here.

A reduced potential Hessian (U_{\rm rel}) is lower order and does not alter
hyperbolicity. Stability of a particular harmonic additionally requires

\[
\lambda_\ell G_{\rm rel}+U_{\rm rel}\ge0.
\]

## Independent homogeneous check

The producer pins the homogeneous theorem by SHA-256 but consumes none of its
terminal-verdict fields. The independent verifier reconstructs the equal-charge
two-field quotient from

\[
Q=(1,1)^T,
\quad
M=\operatorname{diag}(2,3),
\quad
N=(1,-1)^T
\]

and obtains

\[
G_{\rm rel}=\frac65,
\]

then checks that value against the imported homogeneous fixture. This closes
the \(\ell=0\) crosscheck without using the earlier verdict as an oracle.

## Exact fixtures and payload

The oracle-free payload contains five rational fixtures:

1. the equal-charge two-phase counterflow at \(\ell=1\);
2. a rank-deficient two-gauge system with one neutral phase at \(\ell=2\);
3. a rank-zero uncharged system;
4. the exceptional zero-gauge system;
5. a full-phase-rank system with no relative phase.

The rank-deficient fixture has one massless transverse connection family, one
massive family, two relative phases, and exactly one massive longitudinal
family. Its coexact frequency operator has eigenvalues (9) and (12), while
its longitudinal frequency is (11). These values independently test the
matter-kernel split rather than merely the full-rank formula.

The payload status is

```text
ORACLE_FREE_EXACT_MATRIX_PAYLOAD_NO_CONFLUX_VERDICT
```

It is suitable for a later typed consumer, but it is not itself a Conflux
result and does not weaken the separately blocked atlas gate.

## Claim boundary and next gate

This preflight does not select a model-specific gravity-coupled action, build
the unreduced local BV complex, solve Gauss through a support-local
construction, construct retarded/advanced Green operators, prove nonlinear
closure, or establish Hadamard, particle, scale-generation, or quantum claims.

The next physical gate is to select one positive two-derivative scalar--(U(1))
action and construct its unreduced local BV causal parent without inserting a
nonlocal Coulomb inverse.

CLOSE-OUT: DONE — exact all-ell Hodge/Gauss reduction and oracle-free payload complete.
EVIDENCE: d_quotient_classical/compensator/CLOSED_S3_RELATIVE_PHASE_NONHOMOGENEOUS_HODGE_PREFLIGHT_V1.json
