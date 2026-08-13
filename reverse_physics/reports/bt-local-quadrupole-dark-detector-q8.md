# Local quadrupole BT dark detector at order lambda eight

**Certificate:**
`REVERSE_PHYSICS_BT_LOCAL_QUADRUPOLE_DARK_DETECTOR_Q8_V1`

**Dependency tags:** `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`,
`REDUCED-MODE`

**Lifecycle:** `COEFFICIENT_COMPUTED`

## Result

The finite-bandwidth BT dark-port coefficient can be selected by an explicit
finite-derivative local scalar density.  The construction does not require an
ideal angular projector or a rotating-wave deletion.  It is a theorem about
the leading nonzero coefficient in an externally coupled detector, not an
all-order detector probability and not a derivation of the apparatus from the
public closed BT Hamiltonian.

For equal-mass pair momenta, define

\[
 P=k_1+k_2,\qquad r={k_1-k_2\over2},\qquad P\mathbin{\cdot}r=0.
\]

Let \(a\) be a calibrated real spacelike apparatus axis and \(M_0\) the
target pair mass.  The pair symbol

\[
 F_2(P,r)={6\over M_0^4}
 \left[P^2(a\mathbin{\cdot}r)^2
 -{P^2a^2-(a\mathbin{\cdot}P)^2\over3}r^2\right]
\]

is real, exchange-even under \(r\mapsto-r\), and polynomial of total momentum
degree four.  It therefore defines a Hermitian normal-ordered local quadratic
density with four derivatives,

\[
 D_2(x)=:
 \phi(x_1)F_2\!\left(-i(\partial_1+\partial_2),
 {-i(\partial_1-\partial_2)\over2}\right)
 \phi(x_2):\bigg|_{x_1=x_2=x}.
\]

## Exact fibrewise darkness

On every timelike fixed-\(P\) two-body fibre, invariant angular averaging
gives

\[
 \left\langle r_\mu r_\nu\right\rangle
 =-{P^2\over12}\left(g_{\mu\nu}-{P_\mu P_\nu\over P^2}\right).
\]

Substitution into \(F_2\) makes its angular mean identically zero.  The
leading BT four-point amplitude is angle-independent on each such fibre, so
the local quadrupole annihilates it exactly throughout the finite-bandwidth
packet.  This is an algebraic trace-free identity, rather than a small-leakage
estimate.

At the central centre-of-mass point \(P=(M_0,0,0,0)\), with \(a\) along the
incoming spatial axis,

\[
 F_2=P_2(c)={3c^2-1\over2}.
\]

The rational fixtures give value \(1\) along the axis and \(-1/2\)
transversely.  For the boosted timelike fixture
\(P=(5/4,3/4,0,0)\), the three orthonormal transverse directions give
\(25/16,-25/32,-25/32\), whose sum is exactly zero.

## The surviving higher-order moment

For the complete relative order-six correction \(R_6(c)\), define the
quadrupole moment

\[
 J_R=\int_{-1}^{1}P_2(c)R_6(c)\,dc.
\]

The connected-tree part is enclosed by exact rational interval arithmetic on
512 cells.  Its certified interval is positive and, in particular,

\[
 J_{\rm tree}>{1\over100}.
\]

The loop's angle-dependent part is

\[
 B(c)=\text{common}-2\{H(A(1-c))+H(A(1+c))\},\qquad A={32\over25}.
\]

With

\[
 h_n={(-1)^{n+1}\over2n(2n+1)(2n)!},\qquad
 I_n=\int_{-1}^{1}P_2(c)(1-c)^n dc
 ={2^{n+1}n(n-1)\over(n+1)(n+2)(n+3)},
\]

the loop moment becomes

\[
 J_{\rm loop}=-4\sum_{n\geq2}h_nA^nI_n.
\]

It is alternating, and for \(n\geq2\)

\[
 \left|{t_{n+1}\over t_n}\right|
 ={A n\over(n-1)(2n+3)(n+4)}
 \leq {32\over525}<{2\over25}.
\]

The first positive term plus the next negative term therefore gives the exact
lower bound

\[
 J_{\rm loop}>{252416\over73828125}>{1\over400}.
\]

Tree and loop moments have the same positive sign.  Dropping the positive
tree contribution and using \(\pi^2<10\) gives

\[
 J_R>{5\over24\pi^2}\,{1\over400}>{1\over19200}.
\]

The verifier does not replay the producer's angular enclosure.  It changes
variables to the intermediate energy defect

\[
 0\leq z\leq{4\over5},\qquad
 c(z)=1-{15z\over8}-{25z^2\over32},
\]

and proves the tree lower bound using a separate 1024-cell exact rational
interval calculation.  It also obtains the loop power moments by direct
binomial integration.

## Positive local detector probability

Because

\[
 \int_{-1}^{1}P_2(c)dc=0,\qquad
 \int_{-1}^{1}P_2(c)^2dc={2\over5},
\]

normalizing the quadrupole mode on either the sphere or the unordered-pair
quotient gives the exact Cauchy factor

\[
 {Q_{8,\mathrm{local}}\over\bar q_4}\geq {5J_R^2\over16}.
\]

The fibre mean remains exactly zero as \(P\) varies.  Joint continuity of the
hard tree and renormalized off-diagonal loop moments therefore supplies a
nonempty finite-bandwidth neighborhood retaining half the central moment,

\[
 J_R^{\rm band}>{1\over38400}.
\]

Consequently

\[
 \boxed{
 {Q_{8,\mathrm{local}}\over\bar q_4}
 >{1\over4718592000}>{1\over5000000000}.}
\]

This is an absolute positive coefficient, not merely a coherent-minus-recorded
difference.

## Detector outcome and perturbative order

Couple the density to a pointer by

\[
 H_{\rm det}(t)=g_{\rm det}\,\sigma_x\otimes
 \int d^3x\,h(t,\mathbf x)D_2(t,\mathbf x),
\]

with the Hermitian switching quadratures understood.  Choose smooth compact
Fourier support for \(h\) inside the certified finite-bandwidth neighborhood.
Its inverse Fourier transform is Schwartz, but it is not compactly supported
in spacetime.

The selected outcome is: pointer excited, active field in the vacuum, and
the tagged spectator unchanged.  At first order in \(g_{\rm det}\), only the
pair-annihilation part of the local quadratic density can reach this outcome.
Number scattering and pair creation terminate in orthogonal nonvacuum field
sectors.  Thus no rotating-wave term is discarded, and

\[
 p_{\rm selected}
 =g_{\rm det}^2\lambda^8Q_{8,\mathrm{local}}
 +O(g_{\rm det}^2\lambda^{10})+O(g_{\rm det}^4).
\]

## Claim boundary

The certificate does not establish:

- a numerical support radius for the continuity neighborhood;
- compact spacetime support or a causal-AQFT observable;
- the sign of the \(g_{\rm det}^4\) or \(\lambda^{10}\) remainders;
- selection of the apparatus axis, switching, coupling, or outcome by BT
  dynamics;
- the recorded or bright-port absolute order-eight coefficient;
- forward, collinear, real--virtual, or KLN completion;
- an all-time Moller, LSZ, or S operator;
- the standard scalar projector or general BT Eq. (19);
- a positive full BT Hilbert/Fock construction;
- gravity, metric BV--BRST, QME restoration, residual transfer, or anything
  `LORENTZIAN-CAUSAL`;
- literature priority.

The result closes the finite-derivative-local-apparatus objection at the
displayed coefficient.  The next physical gates are the
\(g_{\rm det}^4\) correction and a compact-spacetime switching with a certified
tail bound; the BT-internal gate remains the missing all-order Eq. (19) or an
independently controlled dark \(O(\lambda^{10})\) remainder.

## Verification receipts

The producer, independent verifier, and adversarial tests are deterministic
and memory capped:

```text
ulimit -v 500000; python3 reverse_physics/bt_local_quadrupole_dark_detector_q8.py --check
ulimit -v 500000; python3 reverse_physics/verify_bt_local_quadrupole_dark_detector_q8.py
ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_local_quadrupole_dark_detector_q8
```

Verification results:

```text
producer: 29/29 PASS, wall 1.25 s, peak RSS 270404 KiB
independent verifier: 41/41 PASS, wall 1.26 s, peak RSS 263240 KiB
adversarial tests: 37/37 PASS, wall 5.96 s, peak RSS 263260 KiB
```

Papers V and VI each passed two sequential
`pdflatex -interaction=nonstopmode -halt-on-error` builds under the same
500000 KiB virtual-memory cap.  Their final PDFs have respectively 70 pages
and 701490 bytes, and 61 pages and 669252 bytes.  Their SHA-256 hashes are
`8b23efabe5ca801b44d6bfd4c7aa0b2faf6a33950358da6a9a5b26baf3a102dc`
and
`09e1ddd93a7d396dc43dd8005bfa5f4b7a7b44f51e076a94008feacba87a9b0c`.
The four builds took 1.57 s, 1.57 s, 1.58 s, and 1.58 s, with peak RSS below
280000 KiB.  There are no undefined references or TeX errors and no overfull
box at either inserted theorem.

Tier 3 ran sequentially under the cap.  It is fail-closed rather than a
repository-wide pass: 2710 tests ran in 701.677 s (702.77 s enclosing wall)
at 391336 KiB peak RSS, with 31 failures and 9 skips.  All 37 tests introduced
by this theorem passed.  The 31 failure names are exactly the pre-existing
baseline set: their canonically sorted lists have the common SHA-256
`83a116976bf2fb697b95070337c41d79df0ffc80697a508f29d1240ff0f1bbc0`.
Thus the theorem introduces no Tier-3 regression, but the older failures and
skips remain findings and support no freeze.

The append-only Science Forge planning fold accepted 1547 nodes with zero
invalid items and zero malformed events in 5.93 s at 237316 KiB peak RSS.  It
ran outside the virtual-address cap because the Go runtime reserves a larger
virtual arena before execution.  The advisory shadow rail exited zero by
design in 2.06 s at 349624 KiB peak RSS, while honestly retaining its two
existing findings: the Forge 0.0.2 binary's standard-library hash mismatch
causes bridge-audit error `E9118`, and the coverage census now contains 1613
certificates against the 976-certificate 2026-07-19 baseline.  Neither
advisory finding verifies or falsifies this theorem.

Tier 3 was required because a new `COEFFICIENT_COMPUTED` theorem was inserted
in Papers V and VI.  The producer and method-distinct verifier rechecked the
four content-addressed predecessor certificates as the affected Tier-2 chain.
No classical input, shared core operator, quantum schema, QME lifecycle state,
or Lorentzian claim changed, so unrelated classical and quantum freeze chains
were not rebuilt separately.
