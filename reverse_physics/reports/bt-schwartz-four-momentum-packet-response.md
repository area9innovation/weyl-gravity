# BT Schwartz four-momentum packet response

Certificate:
`REVERSE_PHYSICS_BT_SCHWARTZ_FOUR_MOMENTUM_PACKET_RESPONSE_V1`.

Dependencies: `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`, `REDUCED-MODE`.

Lifecycle: `COEFFICIENT_COMPUTED`.

## Result

The invariant fixed-total-momentum BT packet detector has a normalizable
successor with genuine four-momentum thickness.  One complex
Gaussian-switched spacetime-local degree-38 density gives a nonzero
square-integrable pair-annihilation response on an open set of total momenta.
The exact combined complement of its two solid-angle packets and a
four-momentum core obeys

\[
 \boxed{\eta_{\rm complete}<{883\over10^6}<10^{-3}.}
\]

The same Fourier envelope separates pair absorption sharply from the other
quadratic frequency sectors.  In the target centre-of-momentum apparatus
frame, every number-scattering transfer is spacelike or null and lies a
strict distance from the future-timelike pair-sum centre.  Every wrong-sign
future-pair argument lies farther away in the past causal cone.

This is a leading switched-local-vertex result.  The Gaussian is Schwartz but
not compactly supported in spacetime.  The calculation does not exponentiate
the complete time-dependent Dyson series and does not turn pointwise spectral
suppression into a number-scattering operator-norm theorem.

## One thick local response

Use the apparatus frame in which the target total momentum is

\[
 {P_0\over\kappa}=\left({8\over5},0,0,0\right),
 \qquad M_0={8\kappa\over5}.
\]

Let \(F\) be the certified antipodally even degree-38 polynomial in the
spatial relative momentum.  Smear its pointwise local quadratic density with
a complex Gaussian modulation whose squared Fourier envelope is

\[
 |\widehat h(P)|^2
 =\exp\left[-{\|P-P_0\|_E^2\over\sigma^2}\right],
\]

where the norm is the positive Euclidean norm selected by the apparatus frame
and

\[
 \epsilon={1\over10000},\qquad
 {\sigma\over M_0}={1\over50000},\qquad
 {\sigma\over\kappa}={1\over31250}.
\]

Two real Hermitian detector quadratures synthesize the complex transition
switching and its adjoint, as in the local two-angle predecessor.  The
spacetime integrand remains local.  Its Gaussian switching has infinite
spacetime tails, so it is not a compactly supported local observable in the
causal-AQFT sense.

For a massless pair write

\[
 P=k_1+k_2,\qquad r={k_1-k_2\over2}.
\]

On the future-timelike direct integral, let \(n\in S^2\) be the direction in
the rotationless centre-of-momentum frame of \(P\).  The response vector is

\[
 w(P,n)=\widehat h(P)
 F\left({2\mathbf r\over M_0}\right).
\]

The massless two-body measure factors into \(d^4P\) times the fixed-
\(P\) angular measure, up to common convention constants.  The Gaussian
controls the four total-momentum directions, while the degree-38 polynomial
contributes only finite polynomial growth.  The resulting vector is nonzero
and square integrable.

## Uniform angular control in the five-sigma core

Put

\[
 \|P-P_0\|_E\leq\epsilon M_0=5\sigma.
\]

If \(M^2=P^2\), the spatial part of the rotationless boost maps the unit
direction by a matrix \(L_v\) with singular values \(1,1,\gamma\).  Throughout
the core,

\[
 \gamma-1\leq
 g_\epsilon={\epsilon^2\over2(1-2\epsilon)}.
\]

The common scale \((M/M_0)^{38}\) cancels from each angular leakage ratio.
Only the deformation \(F(L_vn)-F(n)\) must be controlled.

For the normalized Fejer difference, the Fourier coefficient bounds are

\[
 A_0={2\over1-\rho},
\]

and

\[
 A_1={2\over1-\rho}
 \sum_{m=-19}^{19}{2|m|(20-|m|)\over20^2},
 \qquad
 \sum_{m=-19}^{19}{2|m|(20-|m|)\over20^2}={133\over10}.
\]

In cylindrical coordinates the homogeneous polynomial satisfies

\[
 |F|\leq A_0 R^{38},\qquad
 |\nabla F|\leq(38A_0+A_1)R^{37}.
\]

The mean-value theorem therefore gives

\[
 |F(L_vn)-F(n)|\leq
 (38A_0+A_1)(1+g_\epsilon)^{37}g_\epsilon.
\]

Integrating the induced square-norm error over the projective sphere and
combining it with the exact fixed-\(P\) leakage produces the rigorous core
bound

\[
 \eta_{\rm core}
 <0.000882012816932776710\ldots.
\]

The exact numerator and denominator lie in
\(\mathbb Q\pi+\mathbb Q+\mathbb Q\sqrt2\); strict rational enclosures for
\(\pi\) and \(\sqrt2\) decide the comparison.

## Complete four-momentum tail

Set

\[
 z={P-P_0\over\sigma},\qquad R=\|z\|_E.
\]

Outside the core, \(R\geq5\).  The pair energy gives the global polynomial
bound

\[
 |F(2\mathbf r/M_0)|^2
 \leq A_0^2(1+sR)^{76},
 \qquad s={\sigma\over M_0}={\epsilon\over5}.
\]

For \(R\geq5\),

\[
 (1+sR)^{76}\leq e^{76sR}
 \leq e^{(76\epsilon/25)R^2}.
\]

Thus the exterior is dominated by a four-dimensional radial Gaussian with

\[
 c=1-{76\epsilon\over25}>0.
\]

Its exact radial integral is bounded using

\[
 \int_{R\geq5}e^{-cR^2}d^4z
 ={\pi^2\over c^2}e^{-25c}(1+25c).
\]

A 75-term positive Taylor partial sum gives an exact upper bound on
\(e^{-25c}\).  The denominator is bounded from the unit \(z\)-ball, which is
entirely future timelike, using a 20-term lower bound on \(e\).  All powers of
\(\pi\) cancel.  The resulting rational tail bound is

\[
 \eta_{P,{\rm tail}}
 <0.000000586640212958096882\ldots<10^{-6}.
\]

Consequently

\[
 \eta_{\rm complete}
 \leq\eta_{\rm core}+\eta_{P,{\rm tail}}
 <0.000882599457145734807\ldots
 <{883\over10^6}.
\]

This bound covers the complete future-timelike pair direct integral, not only
the five-sigma core.

## Exact separation from number scattering

For future null one-particle momenta,

\[
 q=k_{\rm in}-k_{\rm out}
\]

obeys

\[
 q^2=-2k_{\rm in}\mathbin\cdot k_{\rm out}\leq0.
\]

Every number-scattering Fourier argument is therefore spacelike or null.  In
units of \(M_0\), write \(q=(q_0,\mathbf q)\).  The non-timelike condition
gives \(|\mathbf q|^2\geq q_0^2\), and hence

\[
 \|q-P_0\|_E^2
 \geq(q_0-1)^2+q_0^2
 =2(q_0-1/2)^2+{1\over2}.
\]

The lower bound is attained on the future null cone.  Thus

\[
 {\operatorname{dist}_E(P_0,\{q:q^2\leq0\})^2\over M_0^2}
 ={1\over2}.
\]

Since \(\sigma/M_0=1/50000\), every number-scattering squared Fourier
envelope obeys

\[
 |\widehat h(q)|^2\leq
 e^{-1,250,000,000}<10^{-1,000,000}.
\]

The wrong-sign pair argument is \(-P\) for future causal \(P\), which lies in
the past causal cone.  Its nearest point to \(P_0\) is the origin, so

\[
 {\operatorname{dist}_E(P_0,\text{past causal cone})^2\over M_0^2}=1
\]

and

\[
 |\widehat h(-P)|^2\leq
 e^{-2,500,000,000}<10^{-1,000,000}.
\]

The final decimal inequalities are exact consequences of \(e>2\) and
\(2^{10}>10^3\); no large floating-point exponential is evaluated.

These are pointwise spectral-envelope bounds.  The unrestricted number
sector also contains an unbounded mean momentum and degree-38 derivative
weights.  An operator-norm statement still requires an input energy domain
and a Schur or Hilbert--Schmidt estimate.

## Leading positive packet effect

Normalize the nonzero response vector:

\[
 v={w\over\|w\|}.
\]

The leading pair-annihilation transition is

\[
 A_1=-ig\|w\||e,0\rangle\langle g,v|.
\]

Writing \(\zeta=g^2\|w\|^2\), define

\[
 E_{\rm click}=\zeta|v\rangle\langle v|,
 \qquad E_{\rm no}=I-E_{\rm click}.
\]

They are positive and complete for \(0\leq\zeta\leq1\).  More than

\[
 {999117\over10^6}
\]

of the normalized response mode lies in the declared four-momentum-thick
two-packet region.

This instrument packages the leading local-vertex coefficient as a normalized
two-outcome experiment.  It is not the exact effect of the complete
time-ordered evolution; higher Dyson terms can modify it.

## Boundary and next calculation

Established:

- one spacetime-local degree-38 density with a Schwartz switching;
- a nonzero square-integrable pair response on an open four-momentum set;
- a combined angular and total-momentum leakage bound below \(883/10^6\);
- an exact timelike-pair versus non-timelike-number cone gap;
- pointwise Gaussian suppression of the number and wrong-sign pair sectors;
  and
- a positive normalized leading packet instrument.

Not established:

- compact spacetime support;
- an exact time-independent local Hamiltonian with Gaussian energy response;
- complete time ordering or all-order Rabi evolution;
- an operator-norm or probability bound for number scattering;
- control of unrestricted number-sector mean momentum;
- practical bandwidth or minimal duration;
- selection of the apparatus by public BT dynamics;
- either absolute order-\(\lambda^8\) probability coefficient;
- forward or real--virtual/KLN completion;
- an all-time Moller, LSZ or \(S\) operator;
- general Eq. (19), gravity, metric BV--BRST, restored QME or residual
  transfer;
- anything `LORENTZIAN-CAUSAL`; or
- literature priority.

The next detector calculation is now sharply posed: impose the already used
compact incoming energy support, retain the Gaussian transfer kernel and
prove a Schur or Hilbert--Schmidt bound on the number-scattering operator.
The counter-rotating time ordering must then be included before the leading
instrument can be promoted to a complete finite-duration detector.

## Independent rail and verification receipt

The producer imports the content-pinned exact fixed-sphere linear forms and
derives the Lipschitz and Gaussian-tail bounds by rational arithmetic.  The
verifier follows the independent predecessor rail: it reconstructs each
Fejer kernel from the direct \(20\times20\) amplitude sum, recomputes the
root-of-unity azimuthal integrals and obtains the two latitude integrals by a
beta closed form and an integration-by-parts recurrence.  It independently
rebuilds the concentration inequalities, uses an 85-term exponential bound
to check that the stored 75-term tail is conservative, and verifies the cone
minima on exact saturating fixtures.

All scientific processes ran sequentially under `ulimit -v 500000`.

- Python parse/compile: PASS, 0.04 s, 15,176 KB peak RSS.
- Exact producer and byte-drift check: PASS 34/34, 0.09 s, 16,736 KB peak
  RSS.
- Independent direct-Fejer, concentration and cone verifier: PASS 48/48,
  0.18 s, 24,676 KB peak RSS.
- Mutation suite: PASS 49/49, 3.02 s, 24,640 KB peak RSS.
- Papers V and VI: PASS after two `pdflatex -halt-on-error` passes each.
  Their final passes took 0.49 s at 50,648 KB and 0.52 s at 50,668 KB peak
  RSS.  The PDFs have 66 pages (684,922 bytes) and 59 pages (659,140 bytes),
  with SHA-256 hashes
  `94e19f431886c76098d6c5ec05b68d935ab7cdd5c5dcfec072e449d15050991d`
  and
  `993bc10859a0b05d4c6b1b7ae6f6b9a4dc00e8e6d94a954fe11c315ecaf7c804`.
  There are no undefined citations or references and no new overfull box at
  either inserted theorem.
- Paper prose advisory: NON-CERTIFYING findings.  Both programme manuscripts
  remain above the parenthetical and abstract-ledger advisory budgets;
  emphasis, em-dash, mean sentence, novelty and vocabulary measurements are
  within their advisory budgets.  These findings are not scientific gates.
- Tier 3: FAIL-CLOSED, 2,499 tests in 797.190 s, with 32 failures and 9
  skips; the enclosing timed process took 13:18.22 and peaked at 391,424 KB.
  All 49 new Schwartz response tests passed.  The failure and skip totals are
  unchanged from the predecessor 2,450-test run: older content-addressed
  producer/verifier rails and the capped chain-import scan remain failing,
  and the scan records that it did not run.  They are not passes.
- Science Forge advisory shadow rail: internally FAIL-CLOSED, advisory exit
  0 in 3.91 s at 59,972 KB.  External caller helpers aborted under the cap
  and the Go bridge audit could not reserve page-summary memory, so that audit
  failed with exit 2.  The coverage census reported 1,608 certificates against
  the 976-certificate 2026-07-19 baseline.  No bridge-audit pass is claimed.

Exact scoped commands:

```bash
ulimit -v 500000
/home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/bt_schwartz_four_momentum_packet_response.py --check
/home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/verify_bt_schwartz_four_momentum_packet_response.py
/home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 -m unittest -v reverse_physics.tests.test_bt_schwartz_four_momentum_packet_response
```

EVIDENCE:
`reverse_physics/certificates/REVERSE_PHYSICS_BT_SCHWARTZ_FOUR_MOMENTUM_PACKET_RESPONSE_V1.json`
