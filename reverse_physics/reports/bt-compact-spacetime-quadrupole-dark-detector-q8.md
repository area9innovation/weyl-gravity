# Compact-spacetime local BT quadrupole detector at order lambda eight

**Certificate:**
`REVERSE_PHYSICS_BT_COMPACT_SPACETIME_QUADRUPOLE_DARK_DETECTOR_Q8_V1`

**Dependency tags:** `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`,
`REDUCED-MODE`

**Lifecycle:** `COEFFICIENT_COMPUTED`

## Result

The certified degree-four local quadrupole detector admits a smooth
compactly supported spacetime switching with an exactly dark leading channel
and a strictly positive absolute order-\(\lambda^8\) coefficient.  The exact
bound is

\[
 \boxed{
 {Q_{8,\mathrm{compact}}\over\bar q_4}
 >{1\over18874368000}>{1\over20000000000}.}
\]

The support radius exists but is not numerically bounded.  The result is the
leading \(g_{\rm det}^2\) coefficient of a local detector insertion.  It is not
an all-order detector probability or a renormalized causal perturbative AQFT
construction.

## Compact cutoff sequence

Let \(h_0\in\mathcal S(\mathbb R^4)\) be the switching of the local-quadrupole
predecessor.  Its Fourier transform is smooth and compactly supported inside
the certified hard finite-bandwidth neighborhood.  Choose a real function
\(\chi\in C_c^\infty(\mathbb R^4)\) such that

\[
 \chi(x)=1\quad (|x|_E\leq1),\qquad
 \chi(x)=0\quad (|x|_E\geq2),
\]

and put

\[
 h_R(x)=\chi(x/R)h_0(x),\qquad R\geq1.
\]

Then

\[
 \operatorname{supp}h_R\subset\{|x|_E<2R\}.
\]

The real and imaginary parts of \(h_R\) give two real compactly supported
Hermitian detector quadratures.

For multiindices \(\alpha,\beta\), Leibniz' rule gives terms in which
\(\gamma\leq\beta\) derivatives land on the cutoff.  Such a term carries
\(R^{-|\gamma|}\), is supported outside the radius-\(R\) ball when
\(\gamma=0\), or on the annulus \(R\leq|x|_E\leq2R\) when
\(\gamma\ne0\).  Arbitrary Schwartz tail gain therefore yields, for every
seminorm order \(N,m\) and every \(L\),

\[
 p_{N,m}(h_R-h_0)
 \leq C_{N,m,L}R^{-L}p_{N+L,m}(h_0).
\]

Thus \(h_R\to h_0\) in Schwartz topology.  Fourier transformation is a
continuous automorphism of Schwartz space, so
\(\widehat h_R\to\widehat h_0\) in the same topology.

No compact-Fourier-support statement is made for \(h_R\).  Indeed, the
Fourier tails required by compact spacetime support are retained explicitly.

## Why the finite-order response is continuous

The relevant order-\(\lambda^4\) pair amplitude, after the declared compact
incoming and unchanged-spectator smearing, is a tempered distribution in the
detector switching.

For the connected tree, the imported global finite-time theorem proves that
the complete ten-channel column is Hilbert--Schmidt and obeys

\[
 \|A_{\rm full}\|^2
 \leq {1539\over400\pi^6}\lambda^8T^2.
\]

At every apparent soft zero the worst squared behavior is \(r^{-2}\) against
four transverse variables, hence \(r\,dr\), and is locally integrable.

For the active renormalized loop, the only hard-angle endpoint singularity is
the invariant logarithm

\[
 \log{1\over1-c^2}
 =-\log(1-c)-\log(1+c)+\text{constant}.
\]

Both endpoints are locally integrable because

\[
 \int_0^1|\log u|du=1.
\]

The finite-time transient is locally bounded after the same endpoint
combination, and the renormalized bubble has at most logarithmic growth.
Multiplication by the degree-four quadrupole symbol preserves polynomial
growth.  These bounds make the complete selected finite-order functional

\[
 A_4:\mathcal S(\mathbb R^4)\longrightarrow\mathbb C
\]

tempered and therefore continuous.

Since the predecessor proves \(A_4(h_0)\ne0\), Schwartz convergence supplies
some finite \(R_0\) such that, for every \(R\geq R_0\),

\[
 |A_4(h_R)-A_4(h_0)|<{1\over2}|A_4(h_0)|,
 \qquad |A_4(h_R)|>{1\over2}|A_4(h_0)|.
\]

This is an existence theorem.  It does not turn qualitative distributional
continuity into a fabricated numerical detector size.

## Why Fourier tails do not restore the lower order

For every switching—not only one with narrow momentum support—the leading
pair amplitude factors fibrewise as

\[
 A_2(h_R)=\int dP\,\widehat h_R(P)C_2(P)
 \int_{S_P^2}F_2(P,r)d\Omega_P.
\]

The covariant trace-free identity proved in the predecessor is

\[
 \int_{S_P^2}F_2(P,r)d\Omega_P=0
\]

for every timelike \(P\).  Therefore

\[
 \boxed{A_2(h_R)=0}
\]

for every finite \(R\), irrespective of the Paley--Wiener Fourier tails.
The compact cutoff changes the total-momentum weight but cannot mix angular
trace into the quadrupole.

The retained half-amplitude bound squares to one quarter in probability.
Applying it to the imported theorem gives

\[
 {Q_{8,\mathrm{compact}}\over\bar q_4}
 >{1\over4}{1\over4718592000}
 ={1\over18874368000}
 >{1\over20000000000}.
\]

For the pointer-excited, active-field-vacuum, unchanged-spectator outcome,

\[
 p_{\rm selected}
 =g_{\rm det}^2\lambda^8Q_{8,\mathrm{compact}}
 +O(g_{\rm det}^2\lambda^{10})+O(g_{\rm det}^4).
\]

## Claim boundary

Established:

- a degree-four local quadratic detector density;
- two real \(C_c^\infty\) spacetime switching quadratures;
- exact order-\(\lambda^2\) darkness for every cutoff radius;
- continuity of the selected finite-order response in Schwartz topology;
- existence of a finite cutoff radius retaining half the amplitude; and
- a strictly positive absolute compact-spacetime order-eight coefficient.

Not established:

- a numerical radius, duration, or spatial size;
- compact Fourier support or deletion of Fourier tails;
- renormalized Lorentzian time-ordered products or causal perturbative AQFT;
- the \(g_{\rm det}^4\) or \(\lambda^{10}\) remainder sign;
- selection of the apparatus by public BT dynamics;
- recorded/bright order-eight coefficients or real--virtual/KLN completion;
- an all-time Moller, LSZ, or S operator;
- the standard scalar projector or general Eq. (19);
- a complete positive BT Hilbert/Fock construction;
- gravity, metric BV--BRST, QME restoration, residual transfer, or anything
  `LORENTZIAN-CAUSAL`;
- literature priority.

The physical branch has therefore crossed the finite-spacetime-locality gate
at the displayed coefficient.  Its next quantitative gate is an explicit
Schwartz-seminorm continuity constant and numerical \(R_0\); its next
perturbative gate is \(g_{\rm det}^4\) or the dark \(\lambda^{10}\) remainder.
The BT-internal Eq. (19) route remains separate and open.

## Verification commands

```text
ulimit -v 500000; python3 reverse_physics/bt_compact_spacetime_quadrupole_dark_detector_q8.py --check
ulimit -v 500000; python3 reverse_physics/verify_bt_compact_spacetime_quadrupole_dark_detector_q8.py
ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_compact_spacetime_quadrupole_dark_detector_q8
```

## Verification receipts

All Python and TeX processes ran sequentially under `ulimit -v 500000`.

- Producer: 27/27 PASS in 1.08 s at 261048 KiB peak RSS.
- Method-distinct verifier: 28/28 PASS in 1.11 s at 272544 KiB peak RSS.
- Adversarial suite: 34/34 PASS in 0.056 s (1.19 s enclosing wall) at
  260984 KiB peak RSS.  It includes 33 mutations of the cutoff, topology,
  tempered-response gate, exact lower bound, and claim boundary.
- Papers V and VI: PASS after at least two
  `pdflatex -interaction=nonstopmode -halt-on-error` passes each.  Their
  settled PDFs have 71 pages (705081 bytes) and 62 pages (671943 bytes), with
  SHA-256
  `9ba1107e66e4d7df3f6cf69f7b1ddac100a28c47f460b5443e4d2908de25e4c6`
  and
  `396d5f0e5d0ed71a280a5f10e3f7038e6c1890c8db33b5111363bfccbe727097`.
  The settled passes took 1.58 s at 260928 KiB and 1.59 s at 251796 KiB.
  There are no undefined references or TeX errors and no overfull box at
  either compact-switching theorem.
- Tier 3: FAIL-CLOSED, 2744 tests in 701.939 s (703.00 s enclosing wall) at
  391472 KiB peak RSS, with 31 failures and 9 skips.  All 34 new tests passed.
  The canonically sorted failure names have SHA-256
  `83a116976bf2fb697b95070337c41d79df0ffc80697a508f29d1240ff0f1bbc0`,
  exactly the preceding baseline hash.  Thus no regression was introduced,
  but the older findings remain and this is not a repository-wide pass or
  freeze.
- Science Forge planning fold: 1549 nodes, zero invalid items and zero
  malformed events in 5.90 s at 242192 KiB peak RSS.  It ran outside the
  virtual-address cap because the Go runtime reserves a larger virtual arena.
- Advisory Science Forge shadow: exit zero by design in 1.96 s at 335892 KiB
  peak RSS, with its existing fail-closed bridge-audit `E9118` finding from a
  Forge 0.0.2 standard-library hash mismatch and a census of 1614 certificates
  versus the 976-certificate 2026-07-19 baseline.  Those findings neither
  verify nor falsify this theorem.

Tier 3 was required because Papers V and VI acquire a new
`COEFFICIENT_COMPUTED` theorem.  The producer and independent verifier
content-check and re-evaluate the four direct predecessor certificates as the
affected Tier-2 chain.  No classical input, shared core algebra, quantum
schema, QME lifecycle state, or Lorentzian claim changed, so unrelated freeze
chains were not rebuilt separately.
