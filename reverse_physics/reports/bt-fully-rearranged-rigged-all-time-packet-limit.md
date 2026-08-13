# Fully rearranged BT rigged all-time packet limit

**Certificate:**
`REVERSE_PHYSICS_BT_FULLY_REARRANGED_RIGGED_ALL_TIME_PACKET_LIMIT_V1`

**Dependencies:** `LOCAL-ALGEBRAIC`, `REDUCED-MODE`.
**Lifecycle:** `COEFFICIENT_COMPUTED` for the complete leading selected
smooth-packet all-time coefficient.

## Result

The complete leading fully rearranged BT physical packet probability has a
finite, strictly positive \(T\to\infty\) limit on a nonempty class of smooth
compact source and detector packets:

\[
 \boxed{
 q_{8,\infty}[F]
 =16\left\|\sum_{i,a=0}^2K_{ia,\infty}F\right\|_{L^2(Y)}^2>0.}
\]

This is an all-time wave-packet coefficient, not a whole-carrier scattering
operator.  The distinction is essential.  The finite-window function

\[
 F_T(s)=\int_0^T e^{is\tau}\,d\tau
\]

has no pointwise limit at a fixed generic \(s\ne0\), and the earlier
Hilbert--Schmidt bound grows with \(T\).  Nevertheless it has the tempered
boundary

\[
 \boxed{
 F_T(s)\longrightarrow \pi\delta(s)+i\,\operatorname{PV}{1\over s}.}
\]

Once \(F_T\) acts on the smooth packet before the norm is taken, this boundary
gives strong \(L^2(Y)\) convergence of each packet vector.  It does not imply
operator-norm or Hilbert--Schmidt convergence on all of \(L^2(X)\).

The result closes the leading all-time gate for the already certified
fully rearranged detector.  It does not construct the all-time
\(q_{10}\), an all-order probability, a Møller/LSZ/\(S\) operator, or
Eq. (19).  The order of statements is coefficientwise: first isolate
\(q_8\), then take \(T\to\infty\).  No interchange with a finite-coupling
perturbation sum is claimed.

## Exact nine-channel chart audit

Put

\[
 P=(16/5,\mathbf0),\qquad
 q_{ia}=P-p_i-k_a,
\]

\[
 \delta_{ia}=q_{ia}^0-|\mathbf p_i+\mathbf k_a|,
 \qquad
 D_{ia}=q_{ia}^0+|\mathbf p_i+\mathbf k_a|.
\]

The finite-time exchange kernels are

\[
 \beta_{ia,T}(y,x)
 ={F_T(\delta_{ia}(y,x))\over D_{ia}(y,x)}.
\]

At the certified incoming and outgoing chart centers, exact rational
forward-mode differentiation gives

\[
 \partial_t\delta_{ia}
 =-{N_{ia}\over r_{ia}},
 \qquad
 N_{ia}=(\mathbf p_i+\mathbf k_a)
 \mathbin{\cdot}\partial_t\mathbf p_i,
 \qquad
 r_{ia}^2=|\mathbf p_i+\mathbf k_a|^2.
\]

The complete exact audit is

| \((i,a)\) | \(q^0\) | \(r^2\) | \(N\) | \(q^2\) |
|---:|---:|---:|---:|---:|
| (0,0) | \(4/5\) | \(1296/425\) | \(864/425\) | \(-1024/425\) |
| (0,1) | \(1\) | \(7169/10625\) | \(-16992/10625\) | \(3456/10625\) |
| (0,2) | \(1\) | \(42881/10625\) | \(-4608/10625\) | \(-32256/10625\) |
| (1,0) | \(1\) | \(1577/425\) | \(-96/85\) | \(-1152/425\) |
| (1,1) | \(6/5\) | \(772/425\) | \(168/85\) | \(-32/85\) |
| (1,2) | \(6/5\) | \(388/425\) | \(-72/85\) | \(224/425\) |
| (2,0) | \(1\) | \(1\) | \(-384/425\) | \(0\) |
| (2,1) | \(6/5\) | \(2468/625\) | \(-4008/10625\) | \(-1568/625\) |
| (2,2) | \(6/5\) | \(932/625\) | \(13608/10625\) | \(-32/625\) |

Thus the same incoming rotation coordinate \(t\) is noncritical for all nine
channels.  Exactly channel \((2,0)\) crosses shell at the center.  By
continuity, the packet neighborhoods can be shrunk so that:

1. every \(|\partial_t\delta_{ia}|\) has a positive uniform lower bound;
2. channel \((2,0)\) has one regular shell crossing; and
3. the other eight phase supports remain separated from zero.

No channel-dependent coordinate assumption is needed.

## The half-line Fourier theorem

For a Schwartz test \(g\), define

\[
 I_T(g)=\int_{\mathbb R}F_T(s)g(s)\,ds
       =\int_0^T\widehat g(\tau)\,d\tau,
\qquad
 \widehat g(\tau)=\int_{\mathbb R}e^{i\tau s}g(s)\,ds.
\]

Integration by parts \(N>1\) times gives

\[
 |\widehat g(\tau)|
 \le {\|g^{(N)}\|_1\over|\tau|^N},
\]

and hence the explicit tail estimate

\[
 \boxed{
 |I_\infty(g)-I_T(g)|
 \le {\|g^{(N)}\|_1\over
 (N-1)T^{N-1}}.}
\]

The limiting action is

\[
 I_\infty(g)
 =\pi g(0)
 +i\,\operatorname{PV}\int_{\mathbb R}{g(s)\over s}\,ds.
\]

Two exact fixtures determine both signs independently.  For the even
Gaussian,

\[
 g_e(s)=e^{-s^2},
\qquad
 I_T(g_e)=\pi\operatorname{erf}(T/2)
 \longrightarrow\pi.
\]

For the odd Gaussian,

\[
 g_o(s)=s e^{-s^2},
\qquad
 I_T(g_o)=i\sqrt\pi(1-e^{-T^2/4})
 \longrightarrow i\sqrt\pi.
\]

The first sees the \(+\pi\delta\) term, while the second sees the
\(+i\,\mathrm{PV}\) term.  Their exact rational Taylor coefficients are
recorded in the certificate and recomputed by the independent verifier.

## Packet-space limit

Write the source coordinate locally as \(x=(t,z)\).  For fixed output
\(y\), use \(s=\delta_{ia}(t,z,y)\).  The implicit function theorem gives
\(t=t_{ia}(s,z,y)\), and the channel action becomes

\[
 (K_{ia,T}F)(y)
 =\int_{\mathbb R}F_T(s)g_{ia,y}(s)\,ds,
\]

\[
 g_{ia,y}(s)
 =\int dz\,
 { \chi F\rho_X
 \over D_{ia}|\partial_t\delta_{ia}|}
 \bigg|_{t=t_{ia}(s,z,y)} .
\]

Here \(\chi\) is the same real source/output cutoff for every unit-weight
channel; no channel is reweighted.  For smooth cutoffs supported strictly
inside the shrunken compact neighborhood, the family \(g_{ia,y}\) is uniformly bounded in every
compactly supported smooth seminorm.  The Fourier-tail estimate is therefore
uniform in \(y\).  Since \(Y\) has finite measure,

\[
 K_{ia,T}F\longrightarrow K_{ia,\infty}F
 \quad\hbox{in }L^2(Y),
\]

\[
 (K_{ia,\infty}F)(y)
 =\pi g_{ia,y}(0)
 +i\,\operatorname{PV}\int {g_{ia,y}(s)\over s}\,ds.
\]

There are only nine channels, so their coherent unit-weight sum also
converges in \(L^2(Y)\).  Continuity of the norm then proves

\[
 \lim_{T\to\infty}
 16\left\|\sum_{i,a}K_{ia,T}F\right\|^2
 =
 16\left\|\sum_{i,a}K_{ia,\infty}F\right\|^2.
\]

## Why the limit is not merely zero

Choose real nonnegative smooth source and detector cutoffs that are positive
near the unique \((2,0)\) shell crossing.  For the eight shell-separated
channels \(g_{ia,y}(0)=0\), so their limiting contribution is purely
imaginary.  The shell channel contributes

\[
 \operatorname{Re}(K_{20,\infty}F)(y)
 =\pi g_{20,y}(0)>0
\]

on an open output subset.  No sum of the eight imaginary off-shell boundary
terms can cancel it.  Consequently

\[
 \sum_{i,a}K_{ia,\infty}F\ne0,
\qquad
 q_{8,\infty}[F]>0.
\]

This is a nonempty packet class, not a claim that every packet has a positive
transition coefficient.

## Completeness and common Born rule

The predecessor's exact support theorem annihilates every disconnected
order-\(\lambda^4\) partition on these fully rearranged detector supports.
That support statement is independent of \(T\) and survives distributional
passage to the limit.  Hence the limiting nine-channel sum is still the
complete leading transition amplitude for this detector.

Total ghost complement acts only on the finite species carrier, while the
half-line boundary acts only on momentum.  They commute.  The certified
total-\(\kappa\) fixedness therefore survives, and

\[
 q_{8,\infty}^{\rm public}[F]
 =q_{8,\infty}^{\rm Hilbert}[F].
\]

This is the same common-Born statement as at finite time, now for the
selected all-time leading packet coefficient.

## What “all-time physical” means here

Established:

- an exact common noncritical coordinate for all nine exchange channels;
- the tempered \(T\to\infty\) limit of every channel on smooth packets;
- coherent \(L^2(Y)\) convergence of the complete nine-channel leading
  packet vector;
- a finite, strictly positive coefficient \(q_{8,\infty}\) for a nonempty
  real packet class;
- persistence of disconnected-support annihilation; and
- persistence of public/Hilbert common-Born equality.

Not established:

- pointwise convergence of \(F_T\);
- Hilbert--Schmidt or operator-norm convergence;
- a bounded extension to the entire \(L^2\) carrier;
- a strong Møller, LSZ or \(S\) operator;
- an exact finite-coupling or all-order probability;
- uniformity in \(\lambda\) or exchange of the all-time and perturbative
  limits;
- the all-time limit of \(q_{10}\);
- an inclusive cross section or KLN theorem;
- the ordinary logarithmic-shell endpoint excluded by its own certificate;
- the standard scalar projector or general Eq. (19);
- gravity, metric BV--BRST, QME or `LORENTZIAN-CAUSAL` physics; or
- literature priority.

The earlier logarithmic-shell no-go is not contradicted.  It rules out a
strong limit of moving normalized endpoint-shell vectors on an ordinary
fixed \(L^2\) carrier.  The present result first smears the regular hard
channel against a fixed smooth compact packet and takes the limit in the
test-function topology.  These are different domains and different claims.

## Next gate

The completed finite-time correction is

\[
 q_{10,T}[F]
 =2\operatorname{Re}
 \langle T_{4,T}F,T_{6,T}F\rangle,
\]

where \(T_{6,T}\) is the triangle plus bubble-with-bridge.  Promoting it
requires uniform distributional control of the triangle's two intermediate
defects and of the renormalized three-window bubble/bridge distribution on
the same smooth packet domain.  The leading result does not supply that
theorem automatically.

A separate analytic question is whether \(K_\infty\) extends boundedly to
the full \(L^2\) packet carrier.  That operator theorem would be valuable,
but it is not needed for the selected smooth-packet coefficient proved here.

## Verification receipt

Every scientific Python and TeX command ran sequentially under
`ulimit -v 500000`.  Tier 3 additionally used
`PATH=/usr/local/bin:/usr/bin:/bin`.

| Tier | Command or rail | Result | Elapsed | Peak RSS |
|---|---|---:|---:|---:|
| 0 | Python compile and JSON parse | PASS | below 0.1 s each | below 25 MiB |
| 0/1 | exact Fraction producer `--write --check` | PASS, 36/36 | 0.03 s | 18,304 KiB |
| 1 | analytic-rotation and Gaussian-series independent verifier | PASS, 37/37 | 0.08 s | 24,044 KiB |
| 1 | focused adversarial suite | PASS, 22 tests including 20 mutations | 1.78 s | 24,572 KiB |
| 2 | six live scientific predecessor/new verifiers | PASS, 26/26, 28/28, 55/55, 54/54, 41/41 and 37/37 | 0.39 s total | 24,672 KiB |
| 2 | combined live affected tests | PASS, 164 tests | 3.67 s | 66,528 KiB |
| 0 | Paper V, two `pdflatex` passes | PASS | 0.58 s, 0.60 s | 50,976 KiB maximum |
| 0 | Paper VI, two `pdflatex` passes | PASS | 0.60 s, 0.59 s | 50,964 KiB maximum |
| 2 | Science Forge planning import/fold | PASS, 1,589 nodes; 0 invalid items; 0 malformed events | 7.74 s | 293,160 KiB |
| 3 | full `unittest discover` | **FAIL-CLOSED**, 3,500 tests: 31 failures, 9 skips | 715.718 s (716.79 s rail) | 391,436 KiB |

The Tier-3 total increased by exactly the twenty-two new tests relative to
the preceding 3,478-test run.  The failure and skip counts are unchanged.
All failures remain in the older certificate/hash-drift families and the two
existing `chain_imports` assertions; the new producer, verifier and
test module do not occur in the failure list.  This full rail is not called a
pass and promotes no repository freeze.

One contextual predecessor deserves an explicit fail-closed note.  The live
logarithmic-shell verifier rejects the changed hash of
`notes/bateman-turok-embedding.md`, and its focused nine-test family
therefore has one failure.  The present theorem does not import that note or
use the old producer as a mathematical premise.  Its independent verifier
instead reconstructs directly from the content-pinned certificate the six
unit disjoint shell intervals and the exact \(1/8\) non-Cauchy distance used
only to distinguish domains.  The contextual live rail is still recorded as
failed, not silently promoted.

The advisory Science Forge shadow rail completed in 2.08 s at 339,676 KiB.
It inventories 1,634 certificates and 1,419 verifier files while retaining
the known Forge 0.0.2/stdlib mismatch, bridge-audit E9118 and baseline corpus
drift.  Its advisory exit zero is not certified success; its verifier count
also includes concurrent foundations work outside this package.
The mandatory `s-f work check` invocation fails visibly at the known local
`sfc` build gate and is not recorded as a pass.  The method-distinct
planning import above nevertheless folds the new item and event with zero
malformed input.  The non-certifying paper prose advisory retains the two
papers' existing global parenthetical and abstract-density findings and
reports no excess novelty language.  The paper-principles path named by the
current Science Forge guide is absent from the checked-out Forge tree; a
repository-wide filename search found no moved copy.

Paper V has 83 pages, 769,920 bytes and SHA-256
`a8646db94027afc1be2eb623f04b66e2d749102d0864bf960a9affb8c047ea70`.
Paper VI has 72 pages, 732,354 bytes and SHA-256
`93eacfd8ab711e0a660cbbf7deb5fb80c7071835ee1db2932f5dc7bcee1c445c`.
There are no undefined references; all six Paper-V and two Paper-VI overfull
boxes predate and lie outside the new passages.  The certificate SHA-256 is
`d8e6529cfc8c1fbc8cf31a7486eede56d868809d0ab12e70ece4a80d7ad04015`.

CLOSE-OUT: DONE -- the complete leading fully rearranged BT packet
probability has a finite, nonzero all-time limit on a nonempty smooth compact
rigged packet class, without promotion to a whole-carrier scattering
operator or to the finite-time \(q_{10}\).

EVIDENCE:
`reverse_physics/certificates/REVERSE_PHYSICS_BT_FULLY_REARRANGED_RIGGED_ALL_TIME_PACKET_LIMIT_V1.json`
