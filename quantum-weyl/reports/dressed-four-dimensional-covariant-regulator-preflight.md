# Dressed four-dimensional covariant regulator preflight

A strictly four-dimensional regulator receiver exists conditionally for a
selected fourth-order BV Hessian, but the present action-independent data do
not instantiate it.

The bounded receiver covers two declared routes:

1. matched proper-time/heat-kernel profiles \(F(K/\Lambda^4)\);
2. higher covariant derivatives
   \(K[1+(K/\Lambda^4)^N]\) with finite BV Pauli--Villars doublets.

Both routes require the selected gauge-fixed operator \(K\) to be fourth-order
elliptic and sectorial on declared contours, pairing-self-adjoint on matched
primal/dual domains, and BRST intertwining:

\[
K^\sharp=K,\qquad [Q,K]=0.
\]

The zero-mode and complementary projectors must commute with \(Q\) and be
dual-compatible.  Boundary conditions must define a local elliptic problem
invariant under both \(Q\) and the adjoint, while regulator-field masses,
statistics and contours must satisfy the selected heat-moment equations.

Under those hypotheses, the imported finite-carrier coefficient gives

\[
\log\operatorname{Ber}_R
=-40\,\operatorname{Tr}
\left[\Pi_\perp\,\tau F(K/\Lambda^4)\,\Pi_\perp\right].
\]

The inverse has the opposite sign and composition is exact only when the same
operator, domain and projectors are used.  The zero-mode term
\(-40\operatorname{Tr}(\Pi_0\tau)\) remains finite-rank and generally global.

If \(K\) is Weyl-BRST invariant, the regulated Ward symbol is

\[
Q_W\log\operatorname{Ber}_R
=-40\,\operatorname{Tr}
\left[\Pi_\perp\,\omega F(K/\Lambda^4)\,\Pi_\perp\right].
\]

For a nonintertwining regulator, the certificate retains the Duhamel insertion
containing \(QK\); it vanishes only when \(QK=KQ\) and the zero-mode projector
also intertwines.  Diff covariance turns the bulk variation into a trace of a
commutator, modulo the explicitly selected boundary-domain contribution.

The first missing action-dependent object is therefore the complete
gauge-fixed fourth-order Hessian symbol complex: row ordering, principal and
subprincipal symbols, BRST identities, primal/dual domains, zero modes,
contours and boundary conditions.  The atom and odd-pairing ledger does not
determine these data.  Candidate A’s scalar parent and Candidate B’s reducible
three-form parent consequently remain in separate fail-closed receiver slots.

This route is not identified with dimensional regularization.  A
four-dimensional scheme parameterizes finite counterterms directly in the
four-dimensional \(H^{0,4}\) module; DR/MS first carries an evanescent
continuation torsor.  Both ultimately need an action-specific mixing and
subtraction map, but no equivalence map is presently certified.

Dependency tags: `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`.

This result does not construct an actual regulator, compute determinant or
anomaly coefficients, establish QAP or an all-loop/Lorentzian QME, or make
global-anomaly, Hadamard, positivity, particle, scattering or unitarity
claims.

CLOSE-OUT: OBSTRUCTED — the local receiver theorem is exact under explicit symbol hypotheses, but the selected gauge-fixed Hessian complex, domains, zero modes and contours are the first indispensable action-dependent data.

EVIDENCE: `quantum-weyl/anomalies/certificates/DRESSED_FOUR_DIMENSIONAL_COVARIANT_REGULATOR_PREFLIGHT.json`
