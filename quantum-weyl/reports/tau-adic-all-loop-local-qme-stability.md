# Formal tau-adic all-loop local QME stability

## Result

The compensator-extended theory admits an order-by-order formal local QME
restoration theorem, conditional on a declared quantum action principle.

The imported complete cohomology is

\[
H^{1,4}_{\rm ext}(s\mid d_h)=0
\]

in both parities and at every antifield number. Its stable dimension-four
counterterm module is

\[
H^{0,4}_{\rm ext}(s\mid d_h)=
\operatorname{span}\{
C(\widehat g)^2,E_4(\widehat g),R(\widehat g)^2,
C(\widehat g)\widetilde C(\widehat g)\},
\]

with \(\Box R(\widehat g)\) horizontally exact. The
\(R(\widehat g)^2\) direction is mandatory. Exact ghost-zero terms are
canonical transformations; the four displayed directions account for
coupling redefinitions, including the Euler and parity-odd topological
directions.

Let the counterterm deformation raise the complete formal ideal

\[
\mathfrak m=(\hbar,z_C,z_E,z_{R^2},z_P).
\]

The regular Koszul--Tate contraction persists by the formal inverse

\[
(1+h\delta_{\rm ct})^{-1}
=\sum_{k\geq0}(-h\delta_{\rm ct})^k.
\]

Therefore the zero ghost-one \(E_1\) page stays zero after every formal
coupling deformation. The infinite \(\tau\) expansions of dressed invariants
do not create new independent cohomology generators.

Assume the QME has been restored through order \(n-1\). Under the declared
quantum action principle, the first order-\(n\) breaking is a local
dimension-four ghost-one functional and obeys the Wess--Zumino consistency
condition. Vanishing \(H^{1,4}_{\rm ext}\) gives

\[
\mathcal A_n=s_{\rm ext,n-1}B_n+d_hC_n.
\]

The counterterm \(-B_n\) removes the breaking. Its closed ambiguity is
absorbed by the stable coupling module and canonical transformations, so the
same argument repeats at every finite formal order.

## Essential condition

This is not an unconditional regulator theorem. The repository has not
constructed an all-order regulator/subtraction scheme proving that:

- every first breaking is local in this completed algebra;
- the breaking obeys the consistency equation;
- subtraction stays continuous in the formal filtration;
- the regular coupling chart does not hit a singular Koszul--Tate stratum.

These hypotheses are machine-visible and remain a separate analytic
construction gate. The result follows the standard local-BRST/algebraic-
renormalization induction described by Barnich, Brandt and Henneaux:

- <https://arxiv.org/abs/hep-th/0002245>
- <https://arxiv.org/abs/hep-th/9405109>
- <https://arxiv.org/abs/hep-th/9505173>

## Claim boundary

This is `LOCAL-ALGEBRAIC`. It applies to the changed formal \(\tau\)-adic
compensator theory in a massless homogeneous dimension-four subtraction
algebra near the declared regular chart. It does not repair strict pure-Weyl
gravity, construct the assumed regulator, prove convergence, exclude global
anomalies, or establish Lorentzian renormalized products, a Lorentzian QME,
residual transfer, states, positivity, particles, scattering or unitarity.

CLOSE-OUT: DONE — the formal local all-order induction closes conditionally
on the declared QAP, and the missing regulator/QAP construction is isolated
as the next independent gate.

EVIDENCE: `quantum-weyl/anomalies/certificates/TAU_ADIC_ALL_LOOP_LOCAL_QME_STABILITY.json`
