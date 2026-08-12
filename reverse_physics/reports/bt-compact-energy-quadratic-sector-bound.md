# BT compact-energy quadratic-sector bound

Certificate:
`REVERSE_PHYSICS_BT_COMPACT_ENERGY_QUADRATIC_SECTOR_BOUND_V1`.

Dependencies: `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`, `REDUCED-MODE`.

Lifecycle: `COEFFICIENT_COMPUTED`.

## Result

The four-momentum-thick BT packet detector has an explicit finite-jet
off-shell realization whose unwanted quadratic field sectors are controlled
in operator norm at first Dyson order on a declared compact energy window.
With

\[
 K=\{\mathbf k:M_0/4\leq |\mathbf k|\leq3M_0/4\},
\]

the number-scattering compression $P_KNP_K$ is Hilbert--Schmidt.  Relative
to an exact nonzero lower bound for the desired pair vector, its squared norm
is less than $10^{-1,000,000}$.  The complete wrong-sign pair vector has the
same million-decimal squared suppression.  Including both Hermitian
adjoints, the entire undesired first-Dyson quadratic block on the declared
domain obeys

\[
 \boxed{{\|E_{\rm undesired}\|\over\|A_{\rm pair}\|}
 <10^{-400,000}.}
\]

Consequently the relative change in the leading click effect is less than
$10^{-399,999}$.

This is not an unrestricted-energy theorem.  The number operator statement
is explicitly the $K\to K$ compression selected by the apparatus energy
window.  It is also a first-Dyson coefficient theorem, not a bound on the
complete time-ordered evolution.

## Explicit off-shell local density

Let $F$ be the certified antipodally even homogeneous polynomial of degree
38 that realizes the fixed-total-momentum angular packet filter.  Its
off-shell extension is the bidifferential density

\[
 {\cal D}_F(x)=:
 F\!\left({i\partial_1-i\partial_2\over M_0}\right)
 \phi(x_1)\phi(x_2):\bigg|_{x_1=x_2=x}.
\]

This is a finite jet-local density through order 38.  Evenness of $F$
makes it symmetric under exchange of the two scalar factors.  In the
quadratic frequency decomposition its symbols and Fourier transfers are

| sector | polynomial symbol | switching argument |
|---|---|---|
| desired pair annihilation | $F((k_1-k_2)/M_0)$ | $k_1+k_2$ |
| number scattering | $F((k+k')/M_0)$ | $k-k'$ |
| wrong-sign pair | $F((k_1-k_2)/M_0)$ | $-(k_1+k_2)$ |

The complex Gaussian modulation is realized by two real Hermitian detector
quadratures together with their adjoints, as in the predecessor.  Its squared
Fourier envelope is

\[
 |\widehat h(Q)|^2
 =\exp[-\|Q-P_0\|_E^2/\sigma^2],
 \qquad {\sigma\over M_0}={1\over50000}.
\]

The density is spacetime local.  The Gaussian switching is Schwartz and is
not compactly supported.

## Desired pair lower bound

On the unit Gaussian four-ball

\[
 \|P-P_0\|_E\leq\sigma,
\]

the same boost-distortion estimate used by the thick-packet predecessor gives
an angular response at least $t\pi$.  The exact rational $t$ and its
canonical hash are stored in the certificate, and independent reconstruction
gives

\[
 t>{1\over64}.
\]

The four-dimensional Gaussian ball integral is

\[
 \int_{\|z\|\leq1}e^{-\|z\|^2}\,d^4z
 =\pi^2(1-2/e).
\]

In the declared symmetric bosonic and projective-angular convention this
gives

\[
 \|w\|^2\geq
 {t\pi^3\sigma^4\over8}(1-2/e)>0.
\]

The verifier reconstructs the order-20 filter from its $20\times20$
amplitude sum, evaluates the full latitude integral both by a closed factorial
form and by recurrence, rebuilds the degree-38 gradient estimate, and checks
the exact rational receipt.  The elementary partial sum
$1+1+1/2+1/6+1/24=65/24>8/3$ independently makes the Gaussian-ball lower
bound strict.

## Compact-energy number operator

Use the invariant massless one-particle measure

\[
 d\mu(k)={d^3\mathbf k\over2|\mathbf k|},
\]

with common $2\pi$ conventions omitted consistently.  The full angular
energy band has finite measure

\[
 \mu(K)=\pi M_0^2\left[\left({3\over4}\right)^2
 -\left({1\over4}\right)^2\right]
 ={\pi M_0^2\over2}.
\]

On $K\times K$, the compressed number kernel is

\[
 N_K(k',k)=
 \widehat h(k-k')F((k+k')/M_0).
\]

For future-null $k,k'$, the transfer $k-k'$ is non-timelike.  Its squared
Euclidean apparatus-frame distance from $P_0$ is at least $M_0^2/2$, so

\[
 |\widehat h(k-k')|^2\leq e^{-1,250,000,000}.
\]

The compact band also gives

\[
 |F((k+k')/M_0)|\leq A_0(3/2)^{38}.
\]

It follows directly that

\[
 \|N_K\|_{\rm HS}^2\leq
 A_0^2(3/2)^{76}e^{-1,250,000,000}
 \left({\pi M_0^2\over2}\right)^2.
\]

Dividing by the desired-pair lower bound leaves a prefactor bounded by
$2^{153}$.  The verifier reconstructs that exponent from the independent
ledger

\[
 153=5+76+64+6+2,
\]

where the entries control $2A_0^2$, $(3/2)^{76}$, $s^{-4}$, $t^{-1}$,
and $(1-2/e)^{-1}$, respectively.  Thus

\[
 {\|N_K\|^2\over\|w\|^2}
 \leq{\|N_K\|_{\rm HS}^2\over\|w\|^2}
 <2^{153-1,250,000,000}<10^{-1,000,000}.
\]

No large exponential or floating-point rank calculation is used.

## Global wrong-sign pair vector

For a future pair with total momentum $P$, the counter-rotating switching
argument is $-P$.  In Gaussian units

\[
 R={\|-P-P_0\|_E\over\sigma}\geq{1\over s},
 \qquad s={1\over50000}.
\]

The degree-76 squared polynomial growth is absorbed into the Gaussian using

\[
 (1+sR)^{76}e^{-R^2}
 \leq e^{-cR^2},
 \qquad c=1-76s^2={624999981\over625000000}>{1\over2}.
\]

The exact four-dimensional radial tail is proportional to
$c^{-2}e^{-c/s^2}(1+c/s^2)$, with

\[
 {c\over s^2}=2,499,999,924.
\]

After division by the desired lower bound, the prefactor is below $2^{47}$.
The independent ledger is

\[
 47=5+32+6+2+2,
\]

for $2A_0^2$, the radial factor, $t^{-1}$, the unit-ball inverse, and
$c^{-2}$.  Therefore

\[
 {\|w_-\|^2\over\|w\|^2}
 <2^{47-2,499,999,924}<10^{-1,000,000}.
\]

Unlike the number statement, this pair-vector tail is integrated over the
complete relevant future-pair direct integral.

## Complete first-Dyson comparison

The desired vacuum-to-pair block has the rank-one form

\[
 A_{\rm pair}=-ig\,|e,0\rangle\langle g,w|,
\]

together with its physical reverse adjoint.  The undesired quadratic block
contains the number compression, its adjoint, the wrong-sign pair map, and
its adjoint.  Adjoint blocks have the same norm.  Taking square roots of the
two million-decimal squared bounds and summing four blocks gives

\[
 {\|E_{\rm undesired}\|\over\|A_{\rm pair}\|}
 <4\times10^{-500,000}<10^{-400,000}.
\]

For $\delta=\|E\|/\|A\|$,

\[
 {\|(A+E)^\dagger(A+E)-A^\dagger A\|\over\|A\|^2}
 \leq2\delta+\delta^2<10^{-399,999}.
\]

This establishes that the selected leading pair click is not an artefact of
silently deleting the other quadratic frequency sectors on the declared
energy-windowed first-Dyson domain.

## Claim boundary

This result does not establish:

- a number-operator bound outside $M_0/4\leq|k|\leq3M_0/4$;
- an invariant core or convergence theorem for second and higher Dyson terms;
- exact all-time Rabi evolution for the thick packet;
- compact spacetime support of the switching;
- selection of the band, switching, or coupling by public BT dynamics;
- either absolute order-$\lambda^8$ packet probability coefficient;
- forward, real--virtual, or KLN completion;
- an all-time Moller, LSZ, or scattering operator;
- the standard scalar projector or general Bateman--Turok Eq. (19);
- a positive physical Hilbert/Fock completion;
- gravity, metric BV--BRST, QME restoration, or residual transfer;
- anything tagged `LORENTZIAN-CAUSAL`;
- literature priority.

The next calculational gate is the unequal-packet absolute $q_8$ Gram and
$X_2$--$X_6$ interference.  The distinct functional-analytic gate is
control of higher time-ordered Dyson terms on a common invariant core.

## Verification

Producer:

```text
ulimit -v 500000; python3 reverse_physics/bt_compact_energy_quadratic_sector_bound.py --check
```

Independent verifier:

```text
ulimit -v 500000; python3 reverse_physics/verify_bt_compact_energy_quadratic_sector_bound.py
```

Mutation suite:

```text
ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_compact_energy_quadratic_sector_bound
```

The independent rail uses a direct (20\times20) filter reconstruction,
closed-form-versus-recurrence latitude comparison, exact rational receipt
hashing, and separately reconstructed prefactor ledgers.  It does not call
the compact-energy producer.

## Verification receipt

All scientific processes ran sequentially under `ulimit -v 500000`.

- Tier 0 Python compile and JSON parse: PASS in 0.14 s at 14,796 KB peak
  RSS.  `git diff --check` also passed.
- Exact producer and byte-drift check: PASS 29/29 in 0.10 s at 16,520 KB
  peak RSS.
- Independent direct-Fejer, recurrence, density-symbol and dyadic-ledger
  verifier: PASS 68/68 in 0.09 s at 24,372 KB peak RSS.
- Mutation suite: PASS 47/47 in 0.65 s at 25,080 KB peak RSS.
- Tier 2 dependency handling: both predecessor certificates were unchanged
  and content-addressed.  Their hashes and passing summaries were rechecked,
  while the independent verifier reconstructed the consumed fixed-sphere
  filter rather than rerunning the compact-energy producer.
- Papers V and VI: PASS after two sequential
  `pdflatex -interaction=nonstopmode -halt-on-error` passes each.  The final
  passes took 0.50 s at 50,828 KB and 0.52 s at 51,024 KB peak RSS.  The
  PDFs have 66 pages (687,579 bytes) and 59 pages (660,634 bytes), with
  SHA-256 hashes
  `1da3a2e2b651924890d0f8eb7710cd6dc27df997b7512a0e69733dd753f73c5e`
  and
  `8dd5da4a6a1b366c9ab926ec75e84d495163b1cc51591a06683f7544edfbe912`.
  There are no undefined citations or references and no box warning at the
  inserted theorem locations.  The initial `latexmk` attempt was not a pass:
  that executable is unavailable, so the explicit two-pass `pdflatex` rail
  was used.
- Tier 3: FAIL-CLOSED, 2,546 tests in 697.071 s, with 31 failures and 9
  skips; the enclosing timed process took 698.14 s and peaked at 391,500 KB.
  All 47 new compact-energy tests passed.  Relative to the immediately prior
  2,499-test baseline, the new tests add no failure or skip and the historical
  failure total decreased from 32 to 31.  The remaining older
  content-addressed producer/verifier and chain-import failures are not
  passes.
- Science Forge advisory shadow rail: ABORTED, not a pass.  Its external
  caller helpers aborted under the cap and the remaining read-only process
  made no further progress; this invocation alone was terminated after 127 s.
  Older detached shadow processes in the shared workspace were not touched.

Exact scoped commands used the repository Python explicitly:

```bash
ulimit -v 500000
/home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/bt_compact_energy_quadratic_sector_bound.py --check
/home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/verify_bt_compact_energy_quadratic_sector_bound.py
/home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 -m unittest -v reverse_physics.tests.test_bt_compact_energy_quadratic_sector_bound
/home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 -m unittest discover -v
```

The Tier-3 and advisory failures remain fail-closed.  Neither is used as
evidence for the compact-energy theorem; its positive evidence is the exact
producer, independent reconstruction, mutation suite, and paper build above.
