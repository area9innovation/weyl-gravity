# Generic ghost n=1/n=2 Hodge-resolvent reduction

Dependency tags: `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`.

## Result

The curved Endo one- and two-insertion rows no longer require a nonminimal
heat-kernel ansatz.  On primed nonzero modes, the exact finite-proper-time
identity integrates to

\[
G_{H_0}=G_F-\frac13\,d\Delta_0^{-2}\delta,
\qquad
F=-\Box\mathbf 1+\operatorname{Ric}.
\]

Indeed, after reversing the order of integration,

\[
\int_0^\infty dt\int_t^{3t/2}ds\,K_{\Delta_0}(s)
=\frac13\int_0^\infty ds\,sK_{\Delta_0}(s)
=\frac13\Delta_0^{-2}.
\]

Writing \(L=d\Delta_0^{-2}\delta\) and \(W=-2\operatorname{Ric}\), the
one-insertion term is exactly

\[
\operatorname{Tr}(G_{H_0}W)
=\operatorname{Tr}_1(G_FW)
-\frac13\operatorname{Tr}_0(\Delta_0^{-2}\delta Wd).
\]

The two-insertion term is

\[
-\frac12\operatorname{Tr}(G_{H_0}WG_{H_0}W)
=-\frac12\operatorname{Tr}_1(G_FW G_FW)
+\frac13\operatorname{Tr}_0(\Delta_0^{-2}\delta W G_FW d)
-\frac1{18}\operatorname{Tr}_0(
\Delta_0^{-2}\delta Wd\Delta_0^{-2}\delta Wd).
\]

Cyclicity merges the two mixed orderings.  Thus the unresolved nonminimal
problem is reduced to exactly five covariant minimal vector/scalar resolvent
carriers.  The \(n=1\) carriers require the second-curvature-order minimal
kernels; the \(n=2\) carriers require the first-curvature-order kernels.
Measure, parallel transport and derivative commutators remain inside those
covariant kernels and may not be replaced by an isolated flat metric vertex.

## Independent check

An independent replay uses a symmetric rational endomorphism that mixes the
transverse and longitudinal subspaces.  It checks

\[
H_0G_{H_0}=1
\]

and compares the direct and five-carrier expressions at \(n=1,n=2\).  It
also recovers the cyclic longitudinal coefficients

\[
\frac13,quad-\frac13,quad\frac19,quad-\frac1{81}
\]

of the already completed \(n=3\) sector.  All equalities hold over exact
rationals; coefficient and lifecycle mutations are rejected.

## Claim boundary

This closes the nonminimal architecture of the curved Endo \(n=1,n=2\)
rows.  It does **not** evaluate the five remaining minimal carriers, project
them to the five repository functions, complete the ghost determinant, or
supply the physical fourth-order Hessian.  No complete `Gamma1/Q1`, residual
transfer, Lorentzian QME, Hadamard, particle, positivity, scattering or
unitarity result follows.

## Replay

```bash
PYTHONPATH=quantum-weyl python3 -m \
  spectral.euclidean.generic_background_ghost_n1_n2_hodge_resolvent_reduction --check
PYTHONPATH=quantum-weyl python3 -m \
  spectral.euclidean.verify_generic_background_ghost_n1_n2_hodge_resolvent_reduction
PYTHONPATH=quantum-weyl python3 -m unittest \
  spectral.euclidean.tests.test_generic_background_ghost_n1_n2_hodge_resolvent_reduction
```
