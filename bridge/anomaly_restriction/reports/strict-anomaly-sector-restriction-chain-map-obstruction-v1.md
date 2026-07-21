# Strict-anomaly sector restriction: split chain-map obstruction

## Result

The requested strict pure-Weyl full-BV restriction maps do not exist on the
two pinned targets for two different reasons.

For the fixed-coupling positive Berger sector there is a hard antifield-row
obstruction.  At the exact rational fixture \(q=9/40\), \(\alpha_B=5\),

\[
B_{00}=\frac{(1-q)^2}{6}=\frac{961}{9600},
\qquad
\alpha_B B_{00}=\frac{961}{1920}\ne0.
\]

The Berger clock background is on shell for the matter-coupled action, so the
corresponding coupled metric-antifield constant is zero.  Consequently the
identity-jet full-BV chain equation already fails at zero fluctuation:

\[
j\,s_{\rm PW}(g^*_{00})-Q_{\rm Berger}j(g^*_{00})
=\frac{961}{1920}.
\]

An antifield-number-zero evaluation of gravitational densities is not a
repair.  The source theory must instead be changed to the actual
gravity-clock(-Maxwell) BV theory, whose anomaly cohomology has not been
computed.

For the conformal cylinder, the pure-Weyl background itself creates no such
obstruction.  The missing object is instead the target carrier.  The selected
sector is the derived common zero fibre of fifteen homogeneous quadratic
moment maps.  Its unary tangent complex is therefore the full linear complex;
deleting charged unary modes is categorically wrong.  A faithful receiver
needs fifteen Koszul/BFV generators

\[
d\eta_A=\mu_A,\qquad A=1,\ldots,15,
\]

together with a bulk-to-time-slice transgression carrying the local currents
to the endpoint moment maps.  The pinned minimal BV theorem explicitly lists
that transgression as unproved.  Thus the cylinder disposition is
`NO_CERTIFIED_MAP`, not a universal no-go against an enlarged derived
construction.

## Consequences

All six anomaly-class images remain undefined.  None is called zero, exact or
nontrivial, and neither the cylinder raw-\(D\) nor Berger
\(K_{\rm Berger}=D-\omega R\) Cartan defect is computed.  Raw \(D\) is not
substituted for \(K_{\rm Berger}\).

The old receiver should not be rerun.  The next honest gates are:

1. construct the cylinder 15-generator derived BFV/Koszul time-slice carrier
   and residual projection;
2. compute the local anomaly complex of the actual matter-coupled Berger
   theory, or provide a genuine BV action morphism cancelling the displayed
   antifield defect.

Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`.

This result does not establish restricted anomaly freedom, a compensator
verdict, a QME, Hadamard state, positivity, particles, scattering or
unitarity.

EVIDENCE:
`bridge/certificates/STRICT_ANOMALY_SECTOR_RESTRICTION_CHAIN_MAP_OBSTRUCTION_V1.json`
