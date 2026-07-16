# Berger base-wave Hadamard parametrix

The repaired causal chain fixes the commutator but does not by itself select a
two-point function.  This stage constructs the universal local singular part
for the three normally hyperbolic operator types appearing in the retained
endpoint:

- the rank-ten symmetric-tensor rough wave `Box_2`;
- the rank-three covector rough wave `Box_1`;
- the rank-three Faddeev--Popov factor `F_spatial K_spatial`.

For any such operator \(P\), on a geodesically convex neighborhood, use

\[
H_P^+(x,x')={1\over8\pi^2}
\left({U_P(x,x')\over\sigma_\epsilon(x,x')}
+V_P(x,x')\log{\sigma_\epsilon(x,x')\over\ell^2}\right).
\]

Here \(U_P=\Delta^{1/2}\tau_P\). To avoid half-squared-distance convention
ambiguities, the certificate records the invariant Riesz--Hadamard recursion
using \(\Gamma=2\sigma\), exactly in the form of equation (48) of the cited
vector-bundle construction; in four dimensions those coefficients reorganize
into the displayed \(U/\sigma+V\log\sigma\) form. The result satisfies the
left and formal-adjoint right equations modulo smooth kernels. Its wavefront
set is exactly the positive-frequency null relation:
the usual scalar boundary-value argument gives inclusion, while the
invertible coincidence value \([U_P]=I\) rules out cancellation of the
leading fibre polarization.

The complementary-degree kernel is attached to \(P^\sharp\):

\[
(H_P^+)^{\sharp,\mathrm{swap}}=H_{P^\sharp}^-\pmod{C^\infty}.
\]

No equality \(P=P^\sharp\) is assumed. The singular parametrix is jointly
stationary under the helical generator \(D=e_0\), because the background,
connections, world function, transport recursion and \(i0\) prescription are
all invariant under simultaneous time translation.

The sign and time-orientation dictionary is fixed by a separate flat
normalization witness. It uses signature `(-,+,+,+)`, future vector
`partial_t`, operator `P=-partial_t^2+Delta_spatial`, future null covector
`k=(-|p|,p)`, and `E=G_ret-G_adv`. The positive-frequency Fourier kernel
then has the chosen `+i0 Delta_t` boundary orientation and satisfies

\[
W_0^+(x,x')-W_0^+(x',x)=iE(x,x').
\]

Exact integer sign checks reproduce nullness, future orientation, Fourier
damping, the operator/causal-propagator sign reversal, and the graded-CCR
sign. This witness fixes conventions; it does not replace the curved
vector-bundle microlocal theorem.

The generated analytic JSON objects are therefore identified as
theorem-instantiation ledgers rather than independent proofs. They bind the
standard theorem hypotheses, formulas, references, and repository operator
inventory. The flat convention artifact is separately typed as a
normalization witness.

This is not yet a global Hadamard state.  The smooth bisolution completing the
parametrix remains undetermined, and that smooth part is exactly where the
zero-frequency choice, positivity/Krein policy and global BRST Ward identities
live.  No inverse spatial Laplacian, mode projector or deletion of zero modes
is used.  The next gate is the typed Møller/Volterra transport of this local
singular structure to the twenty-component companion system.

At this stage the antisymmetric part agrees with the causal propagator only
modulo a smooth local kernel.  That remainder is not called a bisolution:
until the smooth left and right equation defects are removed, doing so would
silently promote a parametrix into an exact state.  The later global-completion
gate must separately construct the exact smooth correction, impose the graded
CCR, choose the zero-frequency covariance, state the off-shell Krein policy,
and test positivity on BRST observables.

## Verification receipt

| Tier | Command | Elapsed | Result |
|---:|---|---:|---|
| 0 | Python compilation, JSON parsing, and scoped `git diff --check` | 0.1 s | PASS |
| 0 | Strict AJV Draft 2020-12 validation of the base-parametrix certificate | 1.52 s | PASS |
| 2 | Causal-v2, Hadamard-gate, base-parametrix, ND3, and nonlinear aggregate checks plus 19 focused tests | 2.34 s | PASS |

Tier 3 was not run: this hardens convention normalization and certificate
routing without changing a classical operator, shared core algebra, theorem
lifecycle, freeze tag, or release boundary.
