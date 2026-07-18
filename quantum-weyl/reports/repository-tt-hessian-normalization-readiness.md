# Repository TT Hessian normalization readiness

Dependency tags: `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`.

The repository now has enough evidence to isolate the physical-Hessian gap,
but not to close it. The action convention is exact:

\[
S_{\rm red}=\int\sqrt g\left(R_{\mu\nu}R^{\mu\nu}-\frac13R^2\right)
=\frac12\int\sqrt g\,(C^2-E_4),
\]

and on a conformally flat background its mixed Hessian is

\[
\delta_h\delta_kS_{\rm red}=\langle C_1h,C_1k\rangle,
\qquad B_{\rm lin}=C_1^\sharp C_1.
\]

The unit cylinder also has an exact action-derived TT Bach factorization,
while the standard Euclidean coefficient calculation uses

\[
\Delta_2^\perp(2)\Delta_2^\perp(4)=A(A+2).
\]

These statements do not yet constitute an operator identification. The
classical Nariai endpoint is action-derived, but its nonzero parallel Weyl
curvature makes it ineligible as the missing round-\(S^4\) dictionary.
Likewise, the cylinder factorization fixes a different background and does
not by itself settle the Euclidean transverse-Laplacian convention.

The precise missing carrier is therefore
`REPOSITORY_ROUND_S4_TT_HESSIAN_DICTIONARY_V1`. It must establish

\[
H_{\rm TT}^{\rm repository}
=\kappa\,\Delta_2^\perp(2)\Delta_2^\perp(4)
\]

with the exact sign and scalar \(\kappa\), the TT pairing, the definition of
the Laplacian family, the Euler/integration-by-parts policy, Euclidean
continuation, and the zero-mode domain.

The certificate is deliberately fail-closed: it does not identify the
repository determinant, compute its anomaly coefficients, or decide the
quantum master equation.
