# BT pair-block fourth-order response: certified positive (L=6) interval

**Dependency boundary:** `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`,
`REDUCED-MODE`

**Lifecycle:** `COEFFICIENT_COMPUTED` as a certified numeric interval, not as
an exact rational

**Certificate:**
`REVERSE_PHYSICS_BT_EUCLIDEAN_PAIR_BLOCK_RESPONSE_G4_L6_INTERVAL_V1`

## Result

The complete six-topology order-\(\lambda^4\) nearest-neighbour pair
response on the periodic \(6^4\) lattice lies in the real interval

\[
 \boxed{
  0.000821636134836984048978
  \le T_{4,6}\le
  0.000821636147436984048978
 }.
\]

The lower endpoint is strictly positive. This promotes the finite-volume
coefficient from a binary64 observation to a certified-interval result.
It does not compute the exact rational value.

The six enlarged complex disks are

\[
\begin{array}{c|r|r}
\text{term}&\text{midpoint}&\text{recorded radius} \\ \hline
F_{4,0}&+0.000503375490622672053164&2.40\times10^{-16}\\
F_{4,2}&+0.00216496945607622996544&6.08\times10^{-12}\\
F_{4,4}&-0.00105646796008433114247&1.50\times10^{-13}\\
-F_{3,3}\Gamma_3&+0.0000111719445283249415006&3.84\times10^{-15}\\
-F_{2,2}\Gamma_4&-0.00166025264114145040832&1.52\times10^{-16}\\
+F_{2,2}\Gamma_3^2&+0.000858839851135538639699&7.39\times10^{-17}
\end{array}
\]

Their midpoint sum agrees with the recorded total to
\(3.56\times10^{-23}\). The total radius \(6.30\times10^{-12}\)
contains the sum of all six individually enlarged disks and the decimal
printing error. The sign margin is more than \(1.3\times10^8\) radii.

## Why this is a certificate rather than another floating-point observation

Every complex scalar is stored as a midpoint \(m\) and a nonnegative radius
\(r\), denoting the disk \(|z-m|\le r\). Addition and multiplication
propagate the input disks and add explicit forward-error allowances to the
new radius. The final radius expressions receive an additional multiplicative
inflation.

The recorded platform has radix-2, 64-mantissa-bit extended precision,
round-to-nearest evaluation and standard excess precision. The per-operation
allowance \(10^{-17}\) exceeds 128 unit roundoffs. GCC 15.2 emits direct x87
long-double operations for the complex kernel; contraction is disabled. The
sixth-root seed uses the midpoint
`0xd.db3d742c265539dp-4` and radius \(2\times10^{-19}\); the verifier
checks by exact rational squaring that this disk contains \(\sqrt3/2\).

The displayed C output prints only four significant digits for each radius.
The data receipt therefore enlarges every printed radius by at least one
percent. The certified intervals are the enlarged data radii, never the
shorter terminal strings.

This is a platform-conditioned forward-error proof. It is distinct from exact
rational arithmetic, and the certificate labels it
`CERTIFIED_COMPLEX_DISK_INTERVAL`.

## Independent checks

The interval rail encloses all three previously certified exact values:

\[
 F_{2,0}=-\frac{15643}{1517824},\qquad
 F_{4,0}=\frac{41416831}{82278203392},\qquad
 b^{\mathrm{pair}}_{2,6}
 =\frac{956585197}{10069092633600}.
\]

The nonimporting verifier separately:

- validates the strict schema and all content hashes;
- recomputes term and total endpoints with exact decimal arithmetic;
- checks all rational fixtures by exact `Fraction` conversion;
- requires every earlier binary64 term and total to lie in its new disk;
- proves the sixth-root seed containment with rational squared bounds;
- probes the compiler macros, long-double storage and rounding mode;
- rejects false exact, large-volume and Lorentzian promotions.

Thus the earlier binary64 evaluator is an independent midpoint cross-check,
not the source of the interval proof.

## Resource result

The exhaustive run streamed all \(1296^2\) momentum pairs with eight OpenMP
workers. It took 9126 seconds (2:32:06), used 72523.27 user seconds and 4.61
system seconds, exited zero, and peaked at only 5200 KiB resident memory under
the 500000 KiB virtual-memory ceiling.

The previous OOM was therefore conclusively a dense-representation problem.
Replacing dense coordinate response tensors by six streamed Fourier
topologies remains effective even after conservative interval propagation.

## Meaning and next gate

At \(L=6\), both the order-\(\lambda^2\) and order-\(\lambda^4\)
pair-response coefficients are rigorously positive. This is a real
finite-volume result, but it is not a fixed-coupling response theorem.

The next gate is the large-volume hard-hard, hard-soft and soft-soft split.
The exact axial identity

\[
\Gamma_4(-k,k,l,-l)=\omega(k)\bigl[
4\omega(l)(2-\cos l_1)+8\sin^2l_1
+4\omega(k)(1-\cos l_1)^2\bigr]
\]

identifies a potentially negative logarithmic tadpole. It is a research
direction here, not part of this certificate: the other five topologies still
need uniform shell bounds before any large-volume conclusion is promoted.

Nothing here proves a uniform perturbative remainder, response at
\(\lambda=2/5\), a heat-bath or Witten gap, the actual interacting
\(H^{-1}\) moment, tightness, continuum identification, a Born rule, Krein
reconstruction, a new physical dimension, or anything `LORENTZIAN-CAUSAL`.
Paper 21 is unchanged because no reconstruction or continuum lifecycle state
is promoted.

## Verification

Run sequentially under the memory ceiling:

```text
ulimit -v 500000; python3 reverse_physics/bt_euclidean_pair_block_response_g4_l6_interval.py --check
ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_pair_block_response_g4_l6_interval.py
ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_pair_block_response_g4_l6_interval
cc -std=c11 -O2 -fopenmp -D_DEFAULT_SOURCE -ffp-contract=off -fexcess-precision=standard -Wall -Wextra -Werror reverse_physics/bt_euclidean_pair_block_response_g4_l6_interval.c -lm -o /tmp/bt-pair-g4-l6-interval
ulimit -v 500000; OMP_NUM_THREADS=8 /tmp/bt-pair-g4-l6-interval
```

The final exhaustive command is the recorded Tier-2 production run and is
not normalized as a per-commit test. Tier 3 is not triggered: this is a
finite-volume coefficient enclosure, with no paper theorem, \(H^{-1}\),
continuum, freeze, release, shared-core or Lorentzian promotion.

The append-only planning event was written on its second invocation in 5.54
seconds at 238236 KiB peak RSS. Its first invocation failed before creating
an event because the Go runtime could not reserve its page-summary virtual
address space under `ulimit -v 500000`; that failure is not a pass. The
prescribed `GOMEMLIMIT=300MiB` retry succeeded. The independent planning
import then folded 1703 nodes with zero invalid items and zero malformed
events in 6.53 seconds at 242528 KiB peak RSS.

The read-only Science Forge shadow rail exited zero in advisory mode after
2.86 seconds at 339448 KiB peak RSS. It reported, rather than certified,
the existing unpinned-toolchain/stdlib drift, a missing-SymPy failure in the
bp2 bridge audit, and corpus growth relative to the 2026-07-19 baseline.
Those advisory findings are not scientific passes and do not touch this
interval certificate's focused rails.
