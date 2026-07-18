# Generic-background Diff–Weyl ghost CPT obstruction

Status:
`GENERIC_GHOST_OPERATOR_NONMINIMAL_AND_HODGE_MIXED_MINIMAL_CPT_SUBSTITUTION_OBSTRUCTED`.

Dependency tags: `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`.

For

\[
 F_\mu=\nabla^\nu h_{\mu\nu}-\beta\nabla_\mu h,
 \qquad F_W=h,
\]

the exact coupled Diff×Weyl Faddeev–Popov rows are

\[
 \delta F_\mu=
 \Box\xi_\mu+R_{\mu\nu}\xi^\nu
 +(1-2\beta)\nabla_\mu\nabla\!\cdot\!\xi
 +2(1-4\beta)\nabla_\mu\omega,
\]

\[
 \delta F_W=2\nabla\!\cdot\!\xi+8\omega.
\]

The Weyl row is algebraically invertible. Its exact Schur complement gives

\[
 M_{\rm eff}\xi_\mu=
 \Box\xi_\mu+R_{\mu\nu}\xi^\nu
 +\frac12\nabla_\mu\nabla\!\cdot\!\xi,
\]

independently of \(\beta\). Thus no choice of the trace coefficient in this
gauge removes the nonminimal derivative term.

At a unit covector its normalized principal symbol has eigenvalues

\[
 \left(\frac32,1,1,1\right).
\]

It is elliptic but not Laplace type. A two-covector exact check also rules out
arbitrary fixed invertible two-sided bundle redefinitions. If
\(A P(e_i)B\) were scalar for both \(i=0,1\), then
\(P(e_0)^{-1}P(e_1)\) would have to be scalar up to similarity, whereas its
exact diagonal is \(\operatorname{diag}(2/3,3/2,1,1)\).

The Einstein Hodge reduction is not generic. On a gradient,

\[
 M_{\rm eff}(\nabla c)
 =-\frac32\nabla\Delta_0c+2R_{\mu\nu}\nabla^\nu c.
\]

Writing \(R_{\mu\nu}=Rg_{\mu\nu}/4+S_{\mu\nu}\), a tracefree Ricci jet with
\(S_{01}=S_{10}=1\) sends the gradient covector \(e_0\) to the transverse
component \(2e_1\). Hence the longitudinal sector is not invariant on a
generic background. When \(S=0\), the accepted Einstein factor returns:

\[
 M_{\rm eff}(\nabla c)
 =-\frac32\nabla(\Delta_0-R/3)c.
\]

## Consequence

The four-factor repository determinant ledger is an Einstein/round-sphere
Hodge reduction. The five imported CPT kernels apply to minimal second-order
Laplace-type operators. The generic ghost determinant satisfies neither
condition, so direct substitution of the Einstein ranks into those kernels is
mathematically invalid.

The next coefficient-bearing calculation must provide either:

- covariant perturbation theory for the nonminimal vector operator
  \(M_{\rm eff}\), in the matched gauge and measure; or
- a different generic-background gauge or local field extension, together
  with an exact determinant-and-Jacobian equivalence to minimal Laplace
  blocks.

The generic physical fourth-order metric kernel remains an independent
missing input. No repository cubic function or coefficient, complete
\(\Gamma_1\) or \(Q_1\), residual transfer, or Lorentzian theorem follows.

## Replay

```bash
PYTHONPATH=quantum-weyl python3 -m spectral.euclidean.generic_background_ghost_cpt_obstruction --check
PYTHONPATH=quantum-weyl python3 -m spectral.euclidean.verify_generic_background_ghost_cpt_obstruction
PYTHONPATH=quantum-weyl python3 -m unittest spectral.euclidean.tests.test_generic_background_ghost_cpt_obstruction
```
