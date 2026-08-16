# BT pair-block response: negative fourth-order large-volume logarithm

Dependency tags: `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`, `REDUCED-MODE`

Lifecycle: `COEFFICIENT_COMPUTED`

Certificate:
`REVERSE_PHYSICS_BT_EUCLIDEAN_PAIR_BLOCK_RESPONSE_G4_LARGE_VOLUME_LOG_V1`

## Result

The nearest-neighbour pair block repairs the BT single-site response at one
loop, and its fourth-order coefficient is positive on the certified
\(6^4\) fixture. That repair is not uniform in volume. For the complete
six-topology order-\(\lambda^4\) coefficient,

\[
 \boxed{
 \lim_{L\to\infty}\frac{T_{4,L}}{\log L}
 =-\frac{3W_4}{112\pi^2}<0
 },
 \qquad
 W_4=\int_{[-\pi,\pi]^4}
 \frac{d^4l}{(2\pi)^4}\frac1{\omega(l)}>0.
\]

Thus \(T_{4,L}\to-\infty\) logarithmically and is eventually negative.
Exactly one topology carries the logarithm. The other five are uniformly
\(O(1)\).

This decides the coefficientwise perturbative pair-response strategy: it
cannot furnish a volume-uniform positivity proof. It does not decide the
resummed response at \(\lambda=2/5\), because no volume-uniform perturbative
remainder or convergence theorem exists.

## 1. Exact action vertices

Put

\[
 a=\omega(k),\qquad b=\omega(l),\qquad
 c=\omega(k-l).
\]

The translation-stripped cubic action vertex satisfies the exact dispersion
identity

\[
 \Gamma_3(-k,l,k-l)
 =a^2+b^2+c^2-2ab-2ac-2bc
 =(c-a-b)^2-4ab.
\]

For an axial \(k=(k_1,0,0,0)\), write
\(u=1-\cos l_1\). Direct reduction of the four \(1|3\) and three
\(2|2\) partitions gives

\[
 \boxed{
 \Gamma_4(-k,k,l,-l)=a\bigl[
 4b(2-\cos l_1)+8\sin^2l_1+4a(1-\cos l_1)^2
 \bigr].
 }
\]

Every term in the bracket is nonnegative. Away from the removed zero mode,
the leading bracket is strictly positive. The producer verifies both
identities by exact multivariate polynomial arithmetic. The independent rail
uses an exact interpolation grid at one more point than each variable degree.

## 2. Pair-response soft coefficient

A fixed-range local response vertex is a trigonometric polynomial. Constant
shift invariance makes it vanish when any background momentum is zero. A
finite-difference division or compact mean-value bound therefore gives

\[
 |F_{i,r}(k_1,\ldots,k_r)|\le
 C_{i,r}\prod_{j=1}^r\sqrt{\omega(k_j)},
\]

with a constant independent of \(L\).

For the quadratic pair vertex, hypercubic symmetry and evenness improve this
to

\[
 F_{2,2}(k,-k)=\frac3{28}\omega(k)+O(\omega(k)^2).
\]

The coefficient is exact. The certified one-loop numerator begins with
\((3/56)e_1\); the six-topology normalization carries \(1/(2N)\), so
\(F_{2,2}\) has twice that coefficient.

## 3. Tadpole reduction

Define

\[
 A_L(k)=\frac1N\sum_l
 \Gamma_4(-k,k,l,-l)\omega(l)^{-2}.
\]

The exact axial identity and hypercubic symmetry imply the uniform expansion

\[
 A_L(k)=C_L\omega(k)+O(\omega(k)^2),
\]

where

\[
 C_L=\frac1N\sum_{l\ne0}\left[
 \frac{4(2-\cos l_1)}{\omega(l)}
 +\frac{8\sin^2l_1}{\omega(l)^2}
 \right]>0.
\]

The remainder is uniform because every fourth-order \(k\) derivative
retains the two \(l\) soft factors, leaving only the integrable normalized
sum \(N^{-1}\sum\omega(l)^{-1}\).

The exact \(L=6\) diagnostic is

\[
 C_6=\frac{15611139211}{12843230400}>0,
\]

and the exact averaged quartic remainder coefficient is
\(701304949/29355955200>0\).

Dominated Brillouin-zone convergence gives a limit for \(C_L\). By
hypercubic symmetry,

\[
 \int\frac{\cos l_1}{\omega(l)}
 =W_4-\frac18,
\]

because \(\sum_\mu x_\mu/\omega=1\). Periodic integration by parts
then gives

\[
 \int\frac{\sin^2l_1}{\omega(l)^2}
 =\frac12\int\frac{\cos l_1}{\omega(l)}.
\]

Substitution yields the exact positive limit

\[
 \boxed{C_L\longrightarrow8W_4.}
\]

## 4. Four-dimensional lattice sums

Three normalized sums control every topology:

\[
\begin{aligned}
 W_{1,L}&=\frac1N\sum_{k\ne0}\omega(k)^{-1}=O(1),\\
 G_{2,L}&=\frac1N\sum_{k\ne0}\omega(k)^{-2}
 =\frac1{8\pi^2}\log L+O(1),\\
 S_L&=\frac1{N^2}\sum_{k,l}
 \frac1{\omega(k)\omega(l)\omega(k+l)}=O(1).
\end{aligned}
\]

The first two follow by the standard four-dimensional shell count and the
local expansion \(\omega(k)=|k|^2+O(|k|^4)\). The logarithmic coefficient is
the radial factor
\(2\pi^2/(2\pi)^4=1/(8\pi^2)\).

For the sunset sum, order the geodesic radii of \(k,l,-k-l\). Momentum
conservation makes the two largest comparable. In a dyadic sector with
smallest radius \(s\) and largest radius \(R\), the normalized contribution
is \(O(s^2/L^2)\). Summing \(s\le R\le L\) is uniformly bounded.
This is the multivariable estimate that avoids the spurious \(O(\log L)\)
obtained by separating the three propagators before using conservation.

## 5. Six-topology audit

The topology bounds are:

| topology | majorant after propagators | disposition |
|---|---|---|
| \(F_{4,0}\) | constant | \(O(1)\) |
| \(F_{4,2}\) | \(C/\omega(k)\) | \(W_{1,L}=O(1)\) |
| \(F_{4,4}\) | \(C/[\omega(k)\omega(l)]\) | \(W_{1,L}^2=O(1)\) |
| \(-F_{3,3}\Gamma_3\) | \(C/[\omega(k)\omega(l)\omega(k+l)]\) | \(S_L=O(1)\) |
| \(-F_{2,2}\Gamma_4\) | \(-\frac14\frac3{28}C_L/\omega(k)^2\) plus integrable terms | unique negative logarithm |
| \(+F_{2,2}\Gamma_3^2\) | \(C/[\omega(k)\omega(l)\omega(k-l)]\) | \(S_L=O(1)\) |

For the last row, the selectable cubic estimates give

\[
 |\Gamma_3|^2\le
 C\omega(k)^2\omega(l)\omega(k-l),
\]

which is exactly the extra pair of soft factors needed to reduce the term to
the sunset sum. For the \(F_{3,3}\Gamma_3\) row, the local response
soft factors and three selectable cubic bounds give the same sunset
majorant.

No other logarithm remains to cancel the tadpole.

## 6. Leading coefficient and meaning

The only logarithmic prefactor is

\[
 -\frac14\times\frac3{28}\times8W_4
 \times\frac1{8\pi^2}
 =-\frac{3W_4}{112\pi^2}.
\]

In ordinary language: updating a pair fixes the wrong-way one-loop effect,
and on a small lattice even fourth order points the right way. On larger and
larger lattices, however, the quartic interaction accumulates contributions
from every momentum scale. Those equal-scale contributions add a negative
amount per logarithmic shell. Eventually their sum wins.

This breaks the coefficientwise perturbative barrier, but it does not decide
the physical fixed-coupling measure. A negative growing coefficient in a
nonuniform series is a reason to stop using that series as a positivity
proof, not permission to call the true response negative.

The next viable gate is a nonperturbative normalized pair-response or centered
conditional-score inequality. Only after such a volume-uniform inequality
exists can a response-to-Witten transfer and the actual interacting
\(H^{-1}\) shell sum be attempted.

The finite-volume ordinary Osterwalder--Schrader obstruction remains the
authoritative reconstruction disposition. This coefficient theorem neither
strengthens it to a continuum OS theorem nor says anything about an
indefinite/Krein reconstruction. It establishes no continuum measure, Born
rule, new physical dimension, or `LORENTZIAN-CAUSAL` result. Paper 21 remains
unchanged because no actual \(H^{-1}\), tightness, or reconstruction lifecycle
state is promoted.

## Verification

```text
ulimit -v 500000; python3 reverse_physics/bt_euclidean_pair_block_response_g4_large_volume_log.py --check
ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_pair_block_response_g4_large_volume_log.py
ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_pair_block_response_g4_large_volume_log
```

The exact producer passed in 0.05 seconds at 21056 KiB peak RSS. The
method-distinct interpolation verifier passed in 0.10 seconds at 30048 KiB.
All thirteen focused and adversarial-mutation tests passed in 0.18 seconds at
30652 KiB. Higher-tier receipts are recorded in the certificate. Tier 3 is
not triggered because this is a fixed-order method obstruction, not a
fixed-coupling, \(H^{-1}\), continuum, paper theorem, freeze, release,
shared-core, or Lorentzian promotion.

The append-only sequence-85 planning event passed in 5.59 seconds at 212048
KiB peak RSS. The independent import folded 1704 nodes with zero invalid
items and zero malformed events in 6.18 seconds at 249556 KiB peak RSS. The
read-only Science Forge shadow rail exited zero in advisory mode after 2.99
seconds at 331016 KiB peak. It reported the existing unpinned-toolchain and
stdlib drift, missing SymPy in the bp2 bridge audit, and the stale July corpus
baseline; those findings are reported, not scientific passes, and are
unrelated to the focused theorem rails.
