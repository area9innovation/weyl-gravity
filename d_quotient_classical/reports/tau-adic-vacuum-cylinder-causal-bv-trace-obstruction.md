# Tau-adic vacuum-cylinder causal BV trace obstruction

## Result

The formal Wess--Zumino compensator does **not** extend the certified strict
vacuum-cylinder causal complex to a complete classical causal BV carrier in
the declared finite differential class.

The convention bridge is forced:

```text
strict local BV:  delta g = 2 omega g
causal endpoint:  delta g = sigma g
compensator:      delta tau = omega
therefore:        sigma=2 omega,  delta tau=sigma/2.
```

On the normalized scalar endpoint, the extended unary differential is

```text
sigma -> phi_trace + tau/2,
phi_trace_star + tau_hat_star/2 -> -sigma_star.
```

The exact canonical dressed change isolates

```text
u = phi_trace - 2 tau
```

and its cotangent `u_star` in the zeroth-order Weyl/trace subquotient.  The
serialized six-dimensional matrix has rank
`2` and subquotient homology
dimension
`2`.
The cotangent row is not promoted to full-complex cohomology because the
diffeomorphism companion still acts on it.

The field class *does* promote.  Choose compactly supported `f` outside the
finite fifteen-dimensional span of global conformal-Killing factors, with
`integral(4 f vol)=1`, and define
`lambda_u(h,tau)=integral tr(h-2 tau g_bar) vol`.  Conformal invariance gives
`q0(f u)=0`; Stokes gives `lambda_u(L_xi g_bar)=0` for every compactly
supported diffeomorphism ghost; and the convention-correct Weyl arrow gives
`lambda_u(g_bar sigma,sigma/2)=0`.  Thus `lambda_u` kills the complete
compactly supported endpoint boundary space and evaluates to one on `f u`.
Composition with the certified endpoint projection lifts it to the 386-row
carrier.

The advanced/retarded primitive can be one-sided rather than compact, so the
decisive global step is separate.  If any smooth primitive mapped to `f u`,
its metric component would obey the conformal-Killing equation.  The imported
global kernel has exactly fifteen CKV modes, forcing `f` into their finite
conformal-factor span, contrary to its construction.

If an advanced or retarded homotopy satisfied
`q0 Lambda+Lambda q0=1`, that identity on `f u` would produce precisely the
forbidden smooth primitive.  This is algebraic before wavefront questions
arise.

## Complete declared class

The no-go covers the mandated compensator rows followed by finite-order
support-local cyclic changes of variables, contractible nonminimal or
generalized-auxiliary additions, finite differential cyclic SDR lifts, and
gauge-fermion canonical transforms.  These operations preserve homology.
The obstruction is an arbitrary compact-support family, not one of the
finite conformal-Killing zero modes.

There are two smallest structural repairs, and both change the theory:

1. add the missing independent conformal gauge generator and its BV
   cotangent completion; or
2. add an order-zero dressed-trace kinetic term, for example a nonzero
   `R(g_hat)^2` direction.

The one-loop Wess--Zumino term is order `hbar`; it cannot provide an inverse
for a vanishing order-zero trace Hessian over the formal `hbar`-adic ring.

## Scope

The strict 386-row advanced/retarded complex, its complete minimal and
nonminimal inventory, the formal tau-adic cotangent lift, and raw
`D_compact=partial_t` Cartan data are consumed by exact hashes.  Raw-D
compatibility and the nondegenerate odd pairing remain true, but do not
remove the scalar homology.

This result supplies no full tau-adic Hadamard kernel, positivity,
Lorentzian QME, particle, scattering or unitarity claim.

## Reproduction

```bash
python3 d_quotient_classical/compensator/tau_adic_vacuum_cylinder_causal_bv_trace_obstruction.py --check
python3 d_quotient_classical/compensator/verify_tau_adic_vacuum_cylinder_causal_bv_trace_obstruction.py
python3 -m unittest d_quotient_classical.compensator.tests.test_tau_adic_vacuum_cylinder_causal_bv_trace_obstruction
```

CLOSE-OUT: OBSTRUCTED — the exact first obstruction is certified for the complete declared finite differential carrier class
EVIDENCE: d_quotient_classical/certificates/TAU_ADIC_VACUUM_CYLINDER_CAUSAL_BV_TRACE_OBSTRUCTION_V1.json
