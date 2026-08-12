# BT finite-time active-loop affiliation

Certificate: `REVERSE_PHYSICS_BT_FINITE_TIME_ACTIVE_LOOP_AFFILIATION_V1`.

Dependencies: `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`, `REDUCED-MODE`.
Lifecycle: `COEFFICIENT_COMPUTED` for the selected finite-duration loop.

## Result

The covariant MSbar active loop is now affiliated with the same sharp
finite-duration interaction-picture convention used by the tagged BT tree.
The answer is not simply the asymptotic bubble: it has a finite transient.

Define

\[
 C(z)={\sin z\over z}-\operatorname{Ci}(z)
     =\int_z^\infty {\sin u\over u^2}\,du,
 \qquad z>0.
\]

For channel momentum `P=(P0,p_vector)`, the renormalized finite-time bubble is

\[
 \boxed{
 B_{T,\overline{\rm MS}}(P)
 =\log{\mu^2\over|(P^0)^2-|\mathbf P|^2|}+2
 -C\!\left(T|P^0-|\mathbf P||\right)
 -C\!\left(T|P^0+|\mathbf P||\right).}
\]

The transient tends to zero for hard channels. Thus the large-time boundary
is exactly the independently certified covariant bubble `L_X+2`.

## Ordered Dyson derivation

At two vertices, put `tau=t1-t2`. The ordered integral is

\[
 D_T(\delta)=\int_0^Tdt_1\int_0^{t_1}dt_2\,
 e^{i\delta(t_1-t_2)}
 =\int_0^T(T-\tau)e^{i\delta\tau}d\tau.
\]

The one-vertex tree has time factor `F_T(0)=T` on the energy diagonal. The
real tree-loop cross selects the dispersive part

\[
 {\operatorname{Im}D_T(\delta)\over T}
 =\int_0^T\left(1-{\tau\over T}\right)\sin(\delta\tau)d\tau
 ={1\over\delta}-{\sin(\delta T)\over T\delta^2}.
\]

Its continuous value at `delta=0` is zero. The on-shell absorptive cut is a
different component and is not inserted into the real tree-loop virtual
interference.

The same kernel is the Hilbert transform of

\[
 K_T(\nu)={|F_T(\nu)|^2\over2\pi T}
 ={1-\cos(\nu T)\over\pi T\nu^2},
 \qquad \int_{\mathbb R}K_T(\nu)d\nu=1.
\]

Consequently the second-Dyson dispersive coefficient is the unit-mass Fejer
energy average of the renormalized covariant bubble. Renormalizing the local
two-vertex product first is essential: it fixes the MSbar local term before
the finite spectral average is taken. The average preserves every local
constant because its mass is one.

For `x>0`, convolution of `log|x|` with `K_T` gives

\[
 \log x+C(Tx).
\]

One independent check differentiates this expression: its derivative is
exactly `1/x-sin(Tx)/(T x^2)`, the ordered-Dyson kernel above. The large-`x`
boundary fixes the additive constant. Factoring the two light-cone roots of
`(P0)^2-p^2` then gives the boxed result, with a minus sign because the bubble
contains the negative logarithm.

## Exact tagged coefficient

Finite sharp time is frame dependent. The tagged experiment is evaluated in
the total three-particle center frame used by its connected-tree certificate.
There the active `s`-channel subsystem is boosted. Direct reconstruction from
the exact rational momenta gives light-cone gaps

\[
 s:\quad {4\kappa\over5},\ {16\kappa\over5},
 \qquad
 t,u:\quad {4\sqrt2\kappa\over5},\ {4\sqrt2\kappa\over5}.
\]

Therefore

\[
 \begin{split}
 B_{s,T}+B_{t,T}+B_{u,T}
 ={}&L_*+6-C(4\kappa T/5)-C(16\kappa T/5)\\
 &-4C(4\sqrt2\kappa T/5),
 \end{split}
\]

and the active-loop contribution to the local tagged click is

\[
 \boxed{
 q_{\rm loop,T}^{(6)}={125\lambda^6\Delta\Omega
 \over16384\pi^4\kappa^2\operatorname{Area}}
 \left[L_*+6-C(4\kappa T/5)-C(16\kappa T/5)
 -4C(4\sqrt2\kappa T/5)\right].}
\]

The distinction between the two `s` gaps is important. Replacing both by
`sqrt(s)=8 kappa/5` would silently boost to the active two-body center frame
and would not describe the same finite-time tagged experiment.

## Finite hard window

There is also a closed formula in the active two-body center frame. Let

\[
 a={1-\cos\theta_0\over2},\qquad c=1-2a,
 \qquad b=T\sqrt s,
\]

and set

\[
 A(z)=z\sin z-\cos z-z^2\operatorname{Ci}(z),
 \qquad A'(z)=2zC(z),
\]

\[
 J_T(a)={A(b\sqrt{1-a})-A(b\sqrt a)\over b^2}.
\]

Then

\[
 \boxed{
 \sigma_{\rm loop,T}^{(6)}={5\lambda^6\over64\pi^3s}
 \left\{c\left[3\log{\mu^2\over s}+6\right]+I(a)
 -2cC(b)-4J_T(a)\right\},}
\]

where

\[
 I(a)=2c-2(1-a)\log(1-a)+2a\log a.
\]

This formula is explicitly tied to active-CM sharp-time switching; it is not
substituted into the differently framed tagged fixture.

## Compact-packet affiliation

On compact hard support suppose both light-cone factors are at least
`d_gap>0`. Since `|C(z)|<=1/z`,

\[
 |B_T|\leq 2+\max|\log(\mu^2/|P^2|)|+{2\over T d_{\rm gap}}.
\]

The six-dimensional species tensor is finite. After the common momentum
delta is reduced, the active loop is therefore a bounded Hilbert--Schmidt
kernel on every declared compact finite-measure product. Tensoring the
normalized spectator identity places it on the same finite-time packet
carrier as the tagged tree.

## Meaning and remaining gate

This closes the missing finite-duration active-loop affiliation. Together
with the normal-ordered spectator zero, all individual order-`lambda^6`
objects are now computed. One deliberately separate task remains: assemble
this loop functional with the already certified packet-dependent connected
tree cross, verify their common normalization, and state the final selected
`q6` formula and sign boundary.

The result does not prove general Eq. (19), all-time scattering, all-order
positivity, gravity or metric BV--BRST transfer, a restored gravitational QME,
or anything `LORENTZIAN-CAUSAL`. No literature-priority claim is made.

## Verification receipt

All scientific processes ran sequentially under `ulimit -v 500000`. The
producer passes `30/30` checks in `0.55 s` at `70,612 KB` peak RSS; the
method-distinct verifier passes `32/32` in `0.76 s` at `75,448 KB`; and 15
tests, including 14 adversarial mutations, pass in `2.84 s` at `79,380 KB`.
The paired q6 consumer passes `25/25`, `25/25`, and 15 tests in `0.80 s`,
`0.35 s`, and `0.42 s`, with peaks below `73 MB`.

Tier 0 compiles six Python files and parses eight JSON files in `0.02 s` at
`14,776 KB`. An earlier invocation from `paper/` used repository-relative
paths and failed immediately; it is a path error and is not counted. Paper 05
compiles twice, with final time `0.49 s`, peak RSS `50,600 KB`, 58 pages and
`652,036` bytes. Paper 06 compiles twice, with final time `0.50 s`, peak RSS
`50,788 KB`, 54 pages and `637,505` bytes. No new overfull boxes occur. Git's
threaded lstat cannot start inside the inherited scientific virtual-memory
shell, so the diff check is run outside that shell.

Tier 2 is the content-addressed direct consumer chain: the q6 package checks
this certificate and all five other direct predecessors. Tier 3 was run
because the result is inserted as a paper theorem. It is **not a pass**:
unittest discovery ran 2,180 tests in `775.562 s` (`777.23 s` wall,
`391,360 KB` peak RSS), with 32 failures and 9 skips in older BT
provenance/hash or executable-certificate rails plus the capped
`chain_imports` Git scan. Neither new package failed. This full-suite result
does not support a freeze or release claim. The Science Forge fold accepts
1,515 nodes, zero invalid items and zero malformed events in `1.48 s` at
`13,864 KB`.

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
