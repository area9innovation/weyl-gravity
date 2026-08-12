# BT continuous hard-angle probability through lambda six

Certificate:
`REVERSE_PHYSICS_BT_CONTINUOUS_ANGLE_Q6_FAMILY_V1`.

Dependencies: `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`, `REDUCED-MODE`.

Lifecycle: `COEFFICIENT_COMPUTED`.

## Result

The complete selected tagged Bateman--Turok probability through
\(\lambda^6\) extends from the ninety-degree fixture to every hard angle in
one exact fixed-energy scattering family.  Put \(c=\cos\theta\), with
\(-1<c<1\), and in units \(\kappa=1\) choose

\[
 p_0=k_0=(6/5,6/5,0,0),
\]

\[
 p_{1,2}=(1,-3/5,\mathord\pm4/5,0),
\]

\[
 k_{1,2}=
 (1,-3/5,\mathord\pm4c/5,
             \mathord\pm4\sqrt{1-c^2}/5).
\]

All six momenta are future null and total momentum is conserved.  The active
Mandelstam invariants are

\[
 s={64\over25},\qquad
 t=-{32(1-c)\over25},\qquad
 u=-{32(1+c)\over25},\qquad s+t+u=0.
\]

The endpoints are not hard: \(c=1\) is forward identity and \(c=-1\) is the
exchanged-forward permutation.  They are deliberately excluded.

For every interior angle, four of the ten connected channels remain exactly
resonant.  Summing all six weight-five and four weight-six channels gives the
exact tree bracket

\[
 \begin{split}
 W(c,T)={}&12T+{125\over256}\sin{16T\over5}
 +{125\over128}\sin{8T\over5}\\
 &+{10\sin(a_tT)\over-t}
 +{10\sin(a_uT)\over-u},
 \end{split}
\]

where

\[
 a_t={2\over5}\left(\sqrt{17-8c}-3\right),\qquad
 a_u={2\over5}\left(\sqrt{17+8c}-3\right).
\]

The key sign result is

\[
 \boxed{W(c,T)\geq {13\over24}T>0}
 \qquad(-1<c<1,\ T>0).
\]

Thus the positive tree interference and its secular resonant part are not
artifacts of the ninety-degree rational fixture.

The active finite-time loop is also explicit throughout the family.  With
\(C(z)=\sin z/z-\operatorname{Ci}(z)\),

\[
 \begin{split}
 B_*(c,T,\mu)={}&
 \log {15625(\mu/\kappa)^6\over65536(1-c^2)}+6
 -C(4\kappa T/5)-C(16\kappa T/5)\\
 &-2C\!\left({4\kappa T\sqrt{2(1-c)}\over5}\right)
 -2C\!\left({4\kappa T\sqrt{2(1+c)}\over5}\right).
 \end{split}
\]

Consequently the selected coefficient on each angle fibre is

\[
 q_{\rm tag}(c;f,T)
 =q_4\left[1+\lambda^2R_6(c;f,T,\mu)\right]+O(\lambda^8),
\]

\[
 q_4={75\lambda^4\Delta\Omega
 \over2048\pi^2\kappa^2\operatorname{Area}},
 \qquad
 R_6={2\sqrt2\over3}\operatorname{Re}C_{ff}(c,T)
 +{5\over24\pi^2}B_*(c,T,\mu).
\]

This is fibrewise: the scattering angle is retained as a classical record.
It is not an off-diagonal coherent detector in two angle variables.

## Ten channels

The ten representative masks, in the predecessor's source order, are

\[
 7,11,19,13,21,25,14,22,26,28.
\]

Their exact families are:

- masks \(11,13,22,25\): null, \(\delta=0\), \(D=2\);
- mask \(7\): \(q^2=256/25\), \(\delta=D=16/5\);
- mask \(14\): \(q^2=-128/25\), \(\delta=-8/5\), \(D=16/5\);
- masks \(19,26\): \(q^2=t\), \(\delta=-a_t\),
  \(D=D_t\);
- masks \(21,28\): \(q^2=u\), \(\delta=-a_u\),
  \(D=D_u\).

Here

\[
 D_t={2\over5}(3+\sqrt{17-8c}),\qquad
 D_u={2\over5}(3+\sqrt{17+8c}),
\]

and the two exact factorizations are

\[
 -t=a_tD_t,\qquad -u=a_uD_u.
\]

The four null channels account for the angle-independent \(12T\) term.

## Strict tree bound

For every interior angle, \(a_t,a_u>0\) and
\(D_t,D_u>12/5\).  Applying \(\sin x\geq-x\) only to positive arguments
gives

\[
 {125\over256}\sin{16T\over5}\geq-{25T\over16},
 \qquad
 {125\over128}\sin{8T\over5}\geq-{25T\over16},
\]

and

\[
 {10\sin(a_tT)\over-t}\geq-{10T\over D_t}
 \geq-{25T\over6},
\]

with the same estimate for the \(u\) term.  Therefore

\[
 12-{25\over16}-{25\over16}-{25\over6}-{25\over6}
 ={13\over24}.
\]

At \(c=0\), the two exchange terms coincide and reproduce the independently
certified selected-fixture bracket.  At every fixed interior angle the sine
terms are bounded, so \(W(c,T)/T\to12\).

## Compact-angle control

On \(|c|\leq c_\star<1\), the smallest active light-cone gap is bounded by

\[
 d_{\rm gap}={4\kappa\over5}
 \min\{1,\sqrt{2(1-c_\star)}\}>0.
\]

The imported exact estimate \(|C(z)|\leq1/z\) yields

\[
 \left|B_*-(L+6)\right|
 \leq {1\over\kappa T}
 \left({25\over16}+{5\over\sqrt{2(1-c_\star)}}\right).
\]

The logarithm lies between its values at \(c=0\) and
\(|c|=c_\star\), so its absolute value is bounded by the larger absolute
endpoint value.

For a genuine compact spectator-packet tube, retain the predecessor's
hypothesis \(D_A\geq d_0>0\).  Then

\[
 |{\cal W}_{\kappa,T}|\leq {54T\over d_0},\qquad
 |C_{ff}|\leq {54T\over d_0}
 \sqrt{\operatorname{vol}_{\rm in}\operatorname{vol}_{\rm out}}.
\]

On the exact normalized angle fibre, \(d_0=2\), giving \(27T\).  The latter
number is not asserted for an arbitrary neighborhood without the stronger
support bound.  Combining the packet and loop estimates gives an explicit
finite \(M_R\) with \(|R_6|\leq M_R\).  Hence
\(\lambda^2M_R<1\) is a sufficient uniform positivity condition for the
truncated bracket on any declared compact hard-angle interval.

## Independent rail

The producer works directly in \(c=\cos\theta\) and radical energy gaps.  The
independent verifier instead uses the stereographic coordinate \(r>0\),

\[
 c={1-r^2\over1+r^2},\qquad
 \sin\theta={2r\over1+r^2},
\]

so that

\[
 t=-{64r^2\over25(1+r^2)},\qquad
 u=-{64\over25(1+r^2)}.
\]

It reconstructs all ten subset momenta, fixes every energy-gap square-root
branch, rebuilds the complete tree sum, proves the denominator inequalities,
recomputes the six loop gaps and invariant product, and checks the compact
bounds.  It does not import the producer module.

## Exact boundary

Established:

- one exact continuous hard nonforward fixed-energy angle family;
- all ten channel momenta, invariants, gaps and denominators;
- four persistent resonant channels;
- strict positive tree interference for every interior angle and \(T>0\);
- the complete finite-time active loop throughout the family;
- uniform packet and loop bounds on compact hard-angle intervals;
- a sufficient uniform small-coupling positivity condition; and
- transport to all nine spectator labels by the independently certified
  permutation action.

Not established:

- an off-diagonal two-angle detector or coherent erasure of the angle record;
- either forward endpoint;
- real--virtual, survival, collinear or KLN completion;
- an all-order probability or all-time Møller/LSZ/S operator;
- the standard scalar projector or general Bateman--Turok Eq. (19);
- gravity, metric BV--BRST, QME or residual transfer;
- anything `LORENTZIAN-CAUSAL`; or
- literature priority.

## Next physical gate

The next calculation is the off-diagonal kernel
\(K(\theta,\theta')\) for a finite-resolution detector that does not retain
the exact angle record.  It must be derived from the BT packet dynamics and
shown bounded with a positive detector complement.  Pointwise positivity of
\(W(c,T)\) does not decide that problem.  The separate endpoint route needs a
common real--virtual/survival regulator controlling the logarithms at
\(t=0\) or \(u=0\).

## Verification receipt

All scientific computations ran sequentially under `ulimit -v 500000`.
JSON parsing passed in 0.03 s at 14,032 kB peak RSS, and Python byte
compilation passed in 0.02 s at 15,280 kB.  The producer passed 46 internal
checks in 0.49 s at 69,752 kB.  The independent stereographic rail passed 61
checks in 0.74 s at 74,228 kB.  Twenty-nine tests, including twenty-eight
adversarial certificate mutations, passed in 7.60 s at 77,712 kB.

This is also the affected Tier 2 chain.  All six direct predecessor
certificates are unchanged and content addressed; both new rails recompute
their hashes and passing flags.  The producer reconstructs all ten channels
directly, while the verifier uses the independent stereographic chart and
does not import the producer module.

Papers 05 and 06 compile twice under the same cap.  Their final passes take
0.48 s at 50,944 kB and 0.51 s at 50,708 kB, producing respectively 60
pages (663,268 bytes) and 56 pages (645,367 bytes).  The new Paper 06
dependency paragraph introduced no overfull box; the remaining logged
overfull boxes predate this theorem.

Tier 3 was required because the result is stated as a paper theorem.  It is
**not a pass**.  The run completed 2,265 tests in 788.193 s
(789.21 s wall time) at 391,472 kB peak RSS, with 32 failures and 9 skips.
All 29 new tests passed inside that run.  The preceding baseline had 2,236
tests with the same 32 failures and 9 skips, so the count increased by exactly
the new passing package.  The failures remain in older BT provenance/hash
rails and the existing `chain_imports` scan.  This blocks a repository freeze
or release promotion but does not turn the scoped exact rails into failures.

The advisory Science Forge shadow wrapper exited zero by design in 3.83 s at
59,912 kB, but its internal audit is **not a pass**.  Under the 500 MB cap,
the Go toolchain could not reserve its page-summary address space and the
bridge audit failed closed with exit 2.  The read-only coverage census still
ran and reported 1,601 certificates against the older 976-certificate
baseline.  No graph acceptance is claimed.  A failed internal rail or a
skipped test is never counted as a pass.

Commands:

```text
ulimit -v 500000; python3 reverse_physics/bt_continuous_angle_q6_family.py --check
ulimit -v 500000; python3 reverse_physics/verify_bt_continuous_angle_q6_family.py
ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_continuous_angle_q6_family
```
