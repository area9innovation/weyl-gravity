# Phase 3 axial QNM inward-transport shortfall

The exact ECS scalar initializer sets now have a uniform analytic transport
certificate from \(r=45\) to the concrete matching point \(r=4\).
The certificate uses the reduced phase-factored system and an exact
Gronwall bound
\[
\|\Phi(4,45)\|_\infty<3^{69}.
\]

This establishes existence and analytic frequency dependence on the
proposed closed QNM disk.  It is not yet computationally useful: the
resulting component balls have radius of order \(10^{33}\), so they cannot
prove an Evans boundary is nonzero.

The intrinsic tangent source is nonsingular throughout the finite interval,
with the exact divisor margin
\[
|r\omega-2i|\ge4\,\omega_{\min}.
\]
The missing datum is the correlated ECS \(\tau\)-derivative initializer at
\(r=45\).  The next implementation should combine a tangent Volterra tail
with panelwise centered complex-ball or Lohner transport.  No QNM, root
count, Smith fibre or EP2 is promoted here.
