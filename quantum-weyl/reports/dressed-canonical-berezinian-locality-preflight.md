# Dressed canonical BV Berezinian locality preflight

The common dressed-variable change is canonically valid on the formal
\(\rho=f e^{-\tau}\), \(f>0\), \(\rho\ne0\) chart, but its finite-carrier BV
Berezinian is not one.

For the four-dimensional metric, the symmetric-tensor fibre has rank ten.  In
the \(\tau\) coordinate the base transformation is

\[
\widehat g=e^{-2\tau}g,\qquad \widehat\tau=\tau ,
\]

and its base log Jacobian is therefore \(-20\tau\) per common carrier cell.
The parity-reversed cotangent block is the inverse transpose.  In the
Berezinian it contributes a second copy of the base determinant, so

\[
\log\operatorname{Ber}_{\rm BV}=-40\tau,\qquad
\operatorname{Ber}_{\rm BV}^{(N)}
=\exp\!\left(-40\sum_{i=1}^{N}\tau_i\right).
\]

Including the preceding polar change \(\rho=f e^{-\tau}\) gives

\[
\left|\operatorname{Ber}_{\rm BV}^{(N)}\right|
=f^{-2N}\exp\!\left(-38\sum_{i=1}^{N}\tau_i\right).
\]

The independent replay verifies the forward/inverse composition and the
canonical one-form identity

\[
g^*\delta g+\tau^*\delta\tau
=\widehat g^*\delta\widehat g+\widehat\tau^*\delta\tau,
\qquad
\widehat\tau^*=\tau^*+2g_{\mu\nu}g^{*\mu\nu}.
\]

It also rejects omission of the cotangent factor, reversal of the antifield
shift, promotion to a unit Jacobian, and promotion to an action-independent
continuum-local result.  The unchanged ghost and nonminimal coordinate blocks
have unit Berezinian.  Contractible quartet and nonminimal torsions are one
only on a common dual-compatible regulated carrier; their reduction is not an
additional invertible coordinate transformation.

Formally, a continuum regulator would produce

\[
\log\operatorname{Ber}_{R}=-40\,\operatorname{Tr}_{R}(\tau).
\]

A declared covariant Laplace-type regulator has local bulk heat-kernel
asymptotics, but the regulator connection, dual projectors, finite
subtraction, boundary coefficients, zero-mode projector, priming convention
and real contour depend on the selected action and Hessian.  In particular,
\(-40\operatorname{Tr}(\Pi_0\tau)\) is finite-rank and generally global, while
multiplication by \(e^{-2\tau}\) need not preserve a spectral cutoff.
Consequently there is no unique action-independent local counterterm module
at this gate.

The strict receiver records the exact common payload and requires Candidate A
or B to recompute every regulator-, domain-, zero-mode-, contour- and
renormalization-dependent field.  Its included acceptance fixture is
synthetic and is not physical input.

Dependency tag: `LOCAL-ALGEBRAIC`.

This result does not compute a determinant, QAP, anomaly coefficient, QME,
global anomaly, Hadamard state, particle, scattering, positivity or unitarity
statement.

CLOSE-OUT: OBSTRUCTED — the raw finite BV Berezinian is exact and nonunit, but selected-Hessian regulator data are indispensable for continuum locality and no unique action-independent counterterm module exists.

EVIDENCE: `quantum-weyl/anomalies/certificates/DRESSED_CANONICAL_BEREZINIAN_LOCALITY_PREFLIGHT.json`
