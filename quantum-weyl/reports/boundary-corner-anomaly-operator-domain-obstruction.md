# Boundary/corner anomaly operator-domain obstruction

The first scoped carrier is the flat Bach-flat Euclidean manifold with
corners

\[
M=[0,1]\times B^3.
\]

It has three boundary faces,
\(\Sigma_0,\Sigma_1,\Sigma_{\rm wall}\), and two codimension-two corners
\(C_0,C_1\simeq S^2\).

The authoritative bulk symbol certificate uses the boundary policy
`LOCAL_COMPACT_SUPPORT`. It therefore does not select a geometric boundary
gauge algebra or a domain for the full gauge-fixed BV operator.

## First exact branch

For a fixed face, boundary-preserving diffeomorphisms impose

\[
\iota^*\xi^\perp=0.
\]

Because the tangential derivative of the pulled-back zero function also
vanishes,

\[
\iota^*Q\xi^\perp
=
\iota^*\left(
\xi^a\partial_a\xi^\perp+
\xi^\perp\partial_\perp\xi^\perp
\right)=0.
\]

This is a closed candidate branch, but it still requires compatible metric,
Weyl-ghost, antifield, nonminimal and corner conditions and a differentiable
BFV generator.

If \(\xi^\perp\) is unrestricted, the boundary moves. That inequivalent
branch requires embedding or edge fields and their ghost-antifield cotangent
lift. Those fields are absent from the imported classical complex.

## Consequence

The repository has not selected either boundary gauge branch. It also exports
no full-BV boundary projectors, boundary principal symbol, exact
Lopatinski--Shapiro/complementing certificate, or corner-compatible heat
kernel/resolvent. Consequently:

- boundary and corner relative BRST cohomology are not defined;
- the exhaustive antifield ansatz cannot yet be generated;
- boundary/corner counterterms and anomaly inflow are not classified;
- one-loop boundary coefficients are not defined;
- the differentiable boundary \(D\) generator and its Cartan status are not
  defined.

The strict fixed-field-content bulk local Euclidean QME remains obstructed.
Nothing here cancels or modifies that bulk class.

Dependency tags: `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`.

This result does not compute a boundary anomaly, establish anomaly freedom,
or supply a Lorentzian boundary theory, particle interpretation, scattering
or unitarity claim.

CLOSE-OUT: OBSTRUCTED — the boundary/corner BV complex and full-BV elliptic boundary operator domain are undefined on the declared cornered carrier
EVIDENCE: quantum-weyl/local_bv/certificates/BOUNDARY_CORNER_ANOMALY_OPERATOR_DOMAIN_OBSTRUCTION.json
