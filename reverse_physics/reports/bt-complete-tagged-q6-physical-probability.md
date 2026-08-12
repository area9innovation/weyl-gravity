# Complete tagged BT physical probability through q6

Certificate: `REVERSE_PHYSICS_BT_COMPLETE_TAGGED_Q6_PHYSICAL_PROBABILITY_V1`.

Dependencies: `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`, `REDUCED-MODE`.
Lifecycle: `COEFFICIENT_COMPUTED`.

## Result

The selected hard tagged BT experiment now has a complete physical
probability through order `lambda^6`, not just a leading click or an isolated
loop coefficient.

For a normalized compact positive spectator packet `f`, define

\[
 C_{ff}(T)=\langle f,{\cal W}_{\kappa,T}f\rangle
\]

using the certified connected six-point finite-time kernel. Put

\[
 {\cal C}(z)={\sin z\over z}-\operatorname{Ci}(z)
\]

and

\[
 \begin{split}
 B_*(T,\mu)={}&L_*+6-{\cal C}(4\kappa T/5)
 -{\cal C}(16\kappa T/5)\\
 &-4{\cal C}(4\sqrt2\kappa T/5).
 \end{split}
\]

Then

\[
 \boxed{
 q_{\rm tag}[f;T]=q_4\left[1+\lambda^2R_6[f;T,\mu]\right]
 +O(\lambda^8),}
\]

where

\[
 q_4={75\lambda^4\Delta\Omega\over
 2048\pi^2\kappa^2\operatorname{Area}},
\]

\[
 \boxed{
 R_6[f;T,\mu]
 ={2\sqrt2\over3}\operatorname{Re}C_{ff}(T)
 +{5\over24\pi^2}B_*(T,\mu).}
\]

Equivalently, the two nonzero absolute order-`lambda^6` terms are

\[
 {25\sqrt2\lambda^6\Delta\Omega\over
 1024\pi^2\kappa^2\operatorname{Area}}
 \operatorname{Re}C_{ff}(T)
\]

and

\[
 {125\lambda^6\Delta\Omega\over
 16384\pi^4\kappa^2\operatorname{Area}}B_*(T,\mu).
\]

## Why the coefficient is complete

The certified object ledger contains exactly three order-`lambda^6`
interferences:

1. the tagged active tree crossed with the connected six-point tree;
2. the tagged active tree crossed with the finite-time active loop; and
3. the tagged active tree crossed with the spectator order-`lambda^2`
   two-point block.

The first is `C_ff(T)`. The second is `B_*(T,mu)`. The third vanishes in the
declared normal-ordered, massless, unit-residue auxiliary scheme. Source and
detector corrections are not additional terms because both sides of the
selected scalar experiment are transported by the same two-sided similarity.
A pure survival term misses the nonforward active output support.

The complete covariantly named probability satisfies `q(lambda)=q(-lambda)`.
Thus every odd coefficient vanishes, including orders `lambda^5` and
`lambda^7`, and the next remainder is `O(lambda^8)`.

## Exact sign boundary

The order-`lambda^6` coefficient has the sign of `R6`. It is not universally
positive or negative: it depends on the packet, duration, scale, and declared
finite renormalization convention. Its zero wall is

\[
 \begin{split}
 L_*={}&-6+{\cal C}(4\kappa T/5)+{\cal C}(16\kappa T/5)
 +4{\cal C}(4\sqrt2\kappa T/5)\\
 &-{16\sqrt2\pi^2\over5}\operatorname{Re}C_{ff}(T).
 \end{split}
\]

Since

\[
 L_*=\log\left[{15625\over65536}
 \left({\mu\over\kappa}\right)^6\right],
\]

the corresponding fixed-`lambda(mu)` scale is

\[
 {\mu_{\rm crit}\over\kappa}=
 \left\{{65536\over15625}\exp\left[
 -6+\sum{\cal C}-{16\sqrt2\pi^2\over5}
 \operatorname{Re}C_{ff}(T)\right]\right\}^{1/6},
\]

where `sum C` is the three displayed transient contributions with
multiplicities `1,1,4`. Running of the leading term cancels the explicit scale
dependence at this order. A finite coupling-scheme change moves this wall, so
it is not an invariant sign theorem.

The packet and transient bounds are

\[
 |C_{ff}(T)|\le {54T\sqrt{\mu_{\rm in}\mu_{\rm out}}\over d_0},
\]

\[
 \left|\sum{\cal C}\right|
 \le {25/16+5/\sqrt2\over\kappa T}.
\]

Hence `R6` is finite for every declared `T>0`. Because `q4>0`, the displayed
truncation is positive at sufficiently small coupling. This is perturbative
positivity of one selected experiment, not an all-order theorem.

## Meaning

This is the direct-physics outcome sought by the Bateman line: a normalized,
positive-carrier, finite-time scalar detector probability beyond leading
order, obtained without assuming Eq. (19). It is deliberately selected and
finite order. It does not construct general Eq. (19), an all-time scattering
operator, all-order positivity, gravity or metric BV--BRST transfer, a
gravitational QME, residual quantum transfer, or anything
`LORENTZIAN-CAUSAL`.

## Verification receipt

All scientific processes ran sequentially under `ulimit -v 500000`. The q6
producer passes `25/25` checks in `0.80 s` at `69,860 KB` peak RSS; the
independent verifier passes `25/25` in `0.35 s` at `71,548 KB`; and 15 tests,
including 14 adversarial mutations, pass in `0.42 s` at `72,604 KB`. The
finite-time-loop predecessor independently passes `30/30`, `32/32`, and 15
tests, with every peak below `80 MB`.

Tier 0 compiles six Python files and parses eight JSON files in `0.02 s` at
`14,776 KB`. An earlier invocation from `paper/` used repository-relative
paths and failed immediately; it is not counted. Papers 05 and 06 each
compile twice; their final passes take `0.49 s` at `50,600 KB` and `0.50 s`
at `50,788 KB`, producing respectively 58 pages (`652,036` bytes) and 54 pages
(`637,505` bytes), with no new overfull boxes. Git's diff check is run outside
the scientific address-space cap because its threaded lstat helper cannot
start inside that inherited shell.

Tier 2 checks the exact hash and passing state of the finite-time loop and all
five other direct predecessors. Tier 3 was run because this coefficient is a
paper theorem. It is **not a pass**: 2,180 tests ran in `775.562 s` (`777.23
s` wall, `391,360 KB` peak RSS), with 32 failures and 9 skips in older BT
provenance/hash or executable-certificate rails plus the capped
`chain_imports` Git scan. Neither new package failed. The failure blocks a
repository freeze or release claim and is not evidence for this scoped
coefficient. The Science Forge fold accepts 1,515 nodes, zero invalid items
and zero malformed events in `1.48 s` at `13,864 KB`.

Commands:

```text
ulimit -v 500000; python3 reverse_physics/bt_finite_time_active_loop_affiliation.py --write --check
ulimit -v 500000; python3 reverse_physics/verify_bt_finite_time_active_loop_affiliation.py
ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_finite_time_active_loop_affiliation
ulimit -v 500000; python3 reverse_physics/bt_complete_tagged_q6_physical_probability.py --write --check
ulimit -v 500000; python3 reverse_physics/verify_bt_complete_tagged_q6_physical_probability.py
ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_complete_tagged_q6_physical_probability
ulimit -v 500000; python3 -m unittest discover -v
```
