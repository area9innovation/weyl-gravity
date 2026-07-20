# Complex compensator vacuum-cylinder causal BV parent

## Result

The smallest changed-action repair of the strict tau-adic dressed-trace
obstruction exists on the unit conformal cylinder.

Use the certified formal-polar fixture

\[
\kappa_r=-1,\qquad \kappa_\theta=1,\qquad f=1,
\qquad M_P^2=\frac16.
\]

The cylinder is not Einstein, so the conformal \(\rho^2R\) term and a
constant potential cannot solve both the temporal and spatial metric
equations by themselves.  The independent dressed-curvature coupling is
essential.  The unique solution inside the declared action is

\[
\alpha_R=-\frac1{144},\qquad
V_0=\frac14,\qquad \lambda=1.
\]

The dressed metric density

\[
F(R)=\frac1{12}R-\frac1{144}R^2-\frac14
\]

obeys

\[
F(6)=F'(6)=0,\qquad F''(6)=-\frac1{72}.
\]

Thus the unit cylinder with constant phase is an exact solution even though
it is not Einstein.

## Exact trace repair

For the dressed conformal trace
\(\delta\widehat g=u\widehat g\),

\[
\delta R=-3(\Box+2)u.
\]

Because the background is a double root of \(F\), the added Hessian has no
tracefree or gauge-complement row.  Its complete quadratic contribution is

\[
S_u^{(2)}=-\frac1{16}\int u(\Box+2)^2u,
\qquad
H_u=-\frac18(\Box+2)^2.
\]

Writing \(G_2^\pm\) for the advanced/retarded Green operators of
\(P_2=\Box+2\),

\[
G_u^\pm=-8G_2^\pm G_2^\pm
\]

is a two-sided Green inverse for \(H_u\), preserves the causal support cone,
and satisfies \((G_u^+)^\sharp=G_u^-\).  The phase block is
\(H_\theta=\Box\) with its ordinary scalar advanced/retarded Green
operators.

The old arbitrary compact-support witness is disposed explicitly:

\[
q_{\rm changed}(fu)
=-\frac18(\Box+2)^2f\,u^*.
\]

A compactly supported solution of the iterated normally-hyperbolic equation
vanishes, so the previous infinite-dimensional trace homology family is no
longer closed.  This is a kinetic repair, not a finite zero-mode deletion.

## Complete carrier

The carrier has 390 rows:

```text
356  imported algebraically contractible strict rows
 26  imported strict causal endpoint-complement rows
  8  dressed Weyl/trace/phase endpoint rows
---
390
```

Its endpoint degree profile is `(5,12,12,5)`.  The strict 386-row inventory
is retained and the exact new rows are
`tau,tau_hat_star,theta,theta_star`.  Global U(1) adds no local ghost.

In the ordered scalar basis

```text
(sigma,u,v,theta,u_star,v_star,theta_star,sigma_star)
```

the exact sparse differential, odd pairing and both Green homotopies satisfy

\[
q^2=0,\qquad
q\Lambda^\pm+\Lambda^\pm q=1,\qquad
(\Lambda^+)^\sharp=\Lambda^-.
\]

The full lift is

\[
\Lambda_{390}^\pm
=S_{356}+\iota_{34}
\bigl(\Lambda_{\rm strict\ comp}^\pm
\oplus\Lambda_{\rm scalar/phase}^\pm\bigr)\pi_{34}.
\]

The perturbation factors through the endpoint scalar-curvature row and the
imported side conditions annihilate it against `S_356`, so no infinite HPL
series is required.

## Boundary

This is the changed formal `rho!=0` unequal-kinetic polar theory.  It is not
the sign-obstructed Cartesian-analytic complex scalar and not strict pure
Weyl gravity.  The negative `alpha_R` and scalar sector are not claimed stable
or positive.  Raw-D Cartan, Berger specialization, changed residual
cohomology, Hadamard/Feynman states, anomaly/QME, particles, scattering and
unitarity remain open.

## Reproduction

```bash
python3 d_quotient_classical/compensator/complex_compensator_vacuum_cylinder_causal_parent.py --check
python3 d_quotient_classical/compensator/verify_complex_compensator_vacuum_cylinder_causal_parent.py
python3 -m unittest d_quotient_classical.compensator.tests.test_complex_compensator_vacuum_cylinder_causal_parent
```

Core hash: `5f13a1c69fdc29894bca1b694e761a53e9e646c12b53479f37025d84105d30f0`

CLOSE-OUT: DONE — the changed-action 390-row causal BV parent is certified
EVIDENCE: d_quotient_classical/certificates/COMPLEX_COMPENSATOR_VACUUM_CYLINDER_CAUSAL_PARENT_V1.json
