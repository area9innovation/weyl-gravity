# Round-S4 TT Hessian dictionary receiver readiness

Dependency tags: `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`.

The missing physical handoff now has an executable input contract. A producer
must emit `REPOSITORY_ROUND_S4_TT_HESSIAN_DICTIONARY_V1` and prove

\[
H_{\rm TT}^{\rm repository}
=\frac12\Delta_2^\perp(2)\Delta_2^\perp(4)
\]

on real TT tensors on the round unit \(S^4\). The coefficient \(1/2\) is not
a fit: the flat TT leading symbol of
\(S_{\rm red}=\int(R_{\mu\nu}^2-R^2/3)\) gives

\[
S_{\rm red}^{(2)}=\frac14\langle h,p^4h\rangle,
\]

so the Hessian leading coefficient relative to the monic standard product is
\(\kappa=1/2\).

The receiver additionally requires the exact constant-curvature derivation,
formal self-adjointness, TT ellipticity, zero physical kernel, the fixed Euler
and integration-by-parts policy, and content-addressed producer and independent
verifier artifacts. Mutations of \(\kappa\), the upper shift, a nested hash,
and the classical commit are rejected.

The accepted fixture tests receiver mechanics only. No physical dictionary has
been supplied, and the repository Hessian remains unnormalized until a real
producer artifact passes this contract.
