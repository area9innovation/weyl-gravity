# BT six-point strongly ordered tree dynamics

**Dependency tags:** `LOCAL-ALGEBRAIC`, `REDUCED-MODE`

**Lifecycle:** `COEFFICIENT_COMPUTED`

**Certificate:** `REVERSE_PHYSICS_BT_SIX_POINT_STRONGLY_ORDERED_TREE_V1`

## Result

The complete Bateman--Turok six-point tree does not select the coherent
stationary-independent-increment completion constructed from the one-emission
rate.  In the nested strongly ordered double-collinear sector, its leading
two-count coefficient is

\[
 P_2(a)=\frac{5a^2}{512}+o(a^2),
\]

where the coherent Poisson completion predicts \(a^2/512\).  The ordered
tree coefficient is five times larger.  Equivalently, with mean
\(\mu(a)=a/16\),

\[
 M_2(a)=\frac{5a^2}{256},\qquad
 \kappa_2(a)=M_2(a)-\mu(a)^2=\frac{a^2}{64}.
\]

Thus the leading ordered double logarithm is positively correlated, or
super-Poisson.  The relative \(1/48\) one-pair weight and its rank-two GNS
factor remain correct one-emission data, but their Gaussian/coherent
independent-increment completion is not dynamically selected by the
six-point tree.

This is not a complete \(2\to4\) probability, a proof of universal hard-angle
independence beyond the three exact fixtures, an all-order non-Poisson law, or
a proof of Eq. (19).

## Complete tree recursion

For six labeled external legs, cubic and quartic vertex counts satisfy
\(V_3+2V_4=4\).  The exact topology counts are

\[
 \begin{array}{c|c|c}
 (V_3,V_4)&\hbox{trees}&\hbox{relative sign}\\ \hline
 (0,2)&10&+\\
 (2,1)&105&-\\
 (4,0)&105&+
 \end{array}
\]

for 220 trees in total.  The signs follow from the BT vertex and double-pole
propagator phases.  A subset-current recursion evaluates them without ever
forming one expanded 220-term symbolic expression.  It reproduces the
certified five-point 25-tree jet before being used at six points.

The six-point cyclic chart uses the six adjacent pair squares \(s_i\) and
three complementary adjacent triple squares \(t_i=t_{i+3}\).  The opposite
pair dot products are then fixed by momentum conservation.  For the nested
history

\[
 (k_0,k_1)\longrightarrow K_{01},\qquad
 (K_{01},k_2)\longrightarrow K_{012},
\]

retain the hierarchy parameter \(\epsilon\) until after the common mass
boundary:

\[
 \begin{split}
 x_0&=\delta\epsilon a_0,&x_1&=\delta\epsilon a_1,
 &s_{01}&=\delta\epsilon\tau_1,\\
 x_2&=\delta a_2,&x_j&=\delta a_j\quad(j=3,4,5),
 &s_{012}&=\delta\tau_2.
 \end{split}
\]

The full amplitude begins at order \(\delta^2\).  Squaring it and taking the
three hard-spectator coefficient \([a_3a_4a_5]\) gives the same rational
function at three unrelated hard fixtures.  Only then is
\(\epsilon\to0\) taken.  The compact strong-order kernel is

\[
 \frac{3a_2^3 A\,B}{32\tau_1^4\tau_2^3},
\]

where

\[
 A=(a_0-a_1)^2-2\tau_1(a_0+a_1)+2\tau_1^2,
\]

\[
 B=a_2A+2\tau_2\{-A+3\tau_1^2\}.
\]

The other 216 trees contribute at the same external-mass order as the four
naively iterated pole graphs.  A pole-residue-only factorization would
therefore give the wrong kernel.

## Coupled threshold reduction

The hierarchy limit is nonuniform if taken before phase-space integration.
At finite \(\epsilon\), the outer threshold bounds the inner invariant by

\[
 \tau_1\le
 \frac{(\sqrt{\tau_2}-\sqrt{a_2})^2}{\epsilon}.
\]

The calculation consequently retains \(\epsilon\), integrates the outer
Källén root first, and only then extracts its nonanalytic divided germ.  The
two required universal moments, with \(r\) the outer daughter-mass ratio,
are

\[
 J_3(r)=\frac{r^2-2r\log r-1}{2(r-1)^3},
\]

\[
 J_4(r)=
 \frac{r^3-6r^2\log r+9r^2-6r\log r-9r-1}
 {6(r-1)^5}.
\]

Both have unit \(r\log r\) coefficient.  The remaining inner kernel is
rationalized by

\[
 u=1+m^2+m(z+z^{-1}),\qquad r_{\mathrm{inner}}=m^2.
\]

Its antiderivative is verified by exact differentiation.  Substitution of the
small root of \(u=\Lambda\) into that antiderivative independently reproduces
the finite expression below.  The subtraction is
made at fixed physical invariant \(u=\Lambda\), not at fixed \(z\); since
\(z=m/\Lambda+O(\Lambda^{-2})\), confusing these cutoffs changes a
mass-dependent finite term.  The invariant-cutoff finite part is

\[
 -\frac{
 24m^6\log m-71m^6-204m^4\log m-63m^4
 +60m^2\log m+63m^2+71}
 {6(m^2-1)}.
\]

At small \(m\),

\[
 \frac{71}{6}+m^2\left(10\log m+\frac{67}{3}\right)
 +O(m^4\log m)
 =\frac{71}{6}+r_{\mathrm{inner}}
 \left(5\log r_{\mathrm{inner}}+\frac{67}{3}\right)+\cdots.
\]

The inner nonanalytic coefficient is therefore \(5\).  With the outer
factor \(3/32\), the exact mixed cocycle is

\[
 \bigl[r_1\log r_1\,r_2\log r_2\bigr]\mathcal I_6
 =\frac{15}{32}.
\]

At fixed physical \(u\), every divergent large-\(u\) subtraction coefficient
is polynomial in the external mass ratio.  A mass-independent invariant
local subtraction can alter analytic powers of \(r\), but not the
\(r\log r\) coefficient.  A fixed-\(z\) cutoff is excluded precisely because
it is mass dependent.

## Factorials and the factor five

Before the external-mass kernel, the rational phase factors are

\[
 N_4=16\frac1{2!2!}\frac12\frac1{32}=\frac1{16},
\]

and

\[
 N_6=256\frac1{2!4!}\frac12\frac1{2^2}
 \frac1{32^3}\,4^2=\frac1{3072}.
\]

The hard square-free kernel is \(3/2\).  Hence one selected nested history,
normalized to the Born process, contributes

\[
 \frac{N_6}{N_4}\frac{15/32}{3/2}=\frac5{3072}.
\]

There are

\[
 \binom42\,2=12
\]

labeled nested histories: choose the inner daughter pair and then the third
daughter of the outer split.  The strongly ordered resolution simplex has
volume \(a^2/2\).  Therefore

\[
 12\times\frac12\times\frac5{3072}\,a^2
 =\frac{5a^2}{512}.
\]

The coherent model instead gives

\[
 \frac12\left(\frac a{16}\right)^2=\frac{a^2}{512}.
\]

## What changes and what does not

The six-point result falsifies one assumption of the preceding completion:
resolution increments are not independent at leading ordered double
logarithm.  It does not invalidate:

- the relative semifinite detector weight;
- the rank-two one-emission physical Gram;
- local normality of the coherent state as a mathematical construction;
- the one-emission hard/real cancellation.

It says that the coherent state is not the state selected by the nonlinear
tree dynamics.  A positive non-Gaussian state must match mean \(a/16\) and
second factorial cumulant \(a^2/64\).  Those two moments do not determine a
unique state.  The next discriminator is the seven-point, triple-strongly-
ordered tree jet.

## Verification boundary

The producer uses a cached subset-current recursion and dot-product vertices.
The verifier enumerates all 220 rooted trees explicitly, replaces every
cubic vertex by the invariant triangle polynomial, checks four exact
two-scale points at three hard fixtures, derives the inner rational partial
fractions independently, differentiates a separately assembled
antiderivative, and recomputes every factorial.

All Python commands run sequentially under `ulimit -v 500000`.  The scoped
calculation remains below 100 MB RSS.  The complete non-strongly-ordered
six-body projector, connected single-log and finite terms, loops, a unique
non-Poisson completion, a spacetime Møller/LSZ construction, beyond-tree
positivity, and Eq. (19) remain open.

## Verification receipt

The scoped rail was run from repository commit
`277d24697700fc8e5a97d44cc5bd073167059206` on 2026-08-11:

| Tier | Command or check | Result | Elapsed / peak RSS |
|---|---|---|---|
| 0 | Python byte-compilation; JSON parsing; `git diff --check` | PASS | recorded in the commit handoff |
| 1 | `python3 reverse_physics/bt_six_point_strongly_ordered_tree.py --check` | 20/20 PASS | 7.77 s / 80,136 kB |
| 1 | `python3 reverse_physics/verify_bt_six_point_strongly_ordered_tree.py` | 17/17 PASS | 6.04 s / 81,712 kB |
| 1 | `python3 -m unittest reverse_physics.tests.test_bt_six_point_strongly_ordered_tree -v` | 13/13 PASS | 22.21 s / 82,384 kB |
| 1 | two-pass builds of Papers V and VI | PASS | below the 500 MB cap |
| coordination | `sfc import-program planning/work-items /tmp/weyl-six-point-planning-graph.json` | 1,386 nodes; 0 invalid items; 0 malformed events | 5.9 s |
| advisory | `ci/science-forge-shadow.sh` | existing E9118 bridge failure and corpus-baseline drift reported; **not a pass** | 2.3 s |

Tier 2 was not invoked because this package adds a leaf certificate without
changing a shared operator, schema, generated input, or predecessor
certificate.  Tier 3 was not invoked because no freeze, theorem-lifecycle
promotion, shared core-algebra change, or release is claimed.  Those omitted
tiers are not counted as passes.

The advisory shadow rail itself exited zero by design, but its bridge audit
failed closed on the pre-existing Forge E9118 toolchain incompatibility; this
result does not use that advisory exit as evidence.
