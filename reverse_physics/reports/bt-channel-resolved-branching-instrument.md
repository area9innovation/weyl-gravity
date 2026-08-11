# BT channel-resolved branching instrument

**Dependency tags:** `LOCAL-ALGEBRAIC`, `REDUCED-MODE`

**Lifecycle:** `CLASSIFIED`

**Certificate:**
`REVERSE_PHYSICS_BT_CHANNEL_RESOLVED_BRANCHING_INSTRUMENT_V1`

## Result

The certified one-, two-, and three-emission Bateman--Turok coefficients have
a positive channel-resolved lift on the actual growing family of labeled
strongly ordered histories.  The lift is a finite completely positive,
trace-preserving branching instrument.  Its first jump is exactly affiliated
with the certified physical pair operator:

\[
 G_{\mathrm{first},i}=\frac1{48}I_2,
 \qquad i=1,2,3.
\]

Here \(I_2\) retains both physical parent-jet species.  The higher jump norms
are fixed by the six- and seven-point trees.  They give a normalized inclusive
state through the three-emission truncation without imposing the scalar Cox
architecture.

This is stronger physical affiliation than the preceding total-count state,
but it is not yet the BT asymptotic Hamiltonian or a spacetime S-matrix.  In
this certificate alone, the six- and seven-point inputs determine scalar
squared norms but not the higher species matrices or amplitude phases.  The
subsequent six- and seven-point pre-trace quotient certificates affiliate the
second and third rates on a grading-faithful four-component carrier.  They do
not make the finite level-three absorbing closure dynamical or supply a
four-emission prediction.

## Labeled histories are rooted combs

A strongly ordered \(k\)-emission history has \(k+2\) labeled outgoing leaves.
It is a rooted comb

\[
 (((\{a,b\},c_3),c_4),\ldots,c_{k+2}),
\]

where the first cherry \(\{a,b\}\) is unordered and the remaining leaves are
ordered along the comb.  Equivalently, it is a permutation modulo exchange of
the first two entries.  Therefore

\[
 |\mathcal H_k|=\frac{(k+2)!}{2}.
\]

For the certified sectors,

\[
 |\mathcal H_0|=1,\qquad
 |\mathcal H_1|=3,\qquad
 |\mathcal H_2|=12,\qquad
 |\mathcal H_3|=60.
\]

There is a canonical insertion rule.  For a comb \((\{a,b\},T)\), insert a
new distinguished leaf \(x\) by replacing the cherry with \(\{a,x\}\) or
\(\{b,x\}\), or by inserting \(x\) in any gap of the ordered tail \(T\).
At level \(k\), this gives exactly

\[
 d_k=k+3
\]

children.  Deleting \(x\) is the inverse.  The insertion fibres are disjoint
and exhaust the next comb level.  Thus the history counts factor as

\[
 3=3,\qquad 12=3\cdot4,\qquad 60=3\cdot4\cdot5.
\]

The producer constructs the children by insertion.  The independent verifier
instead chooses the cherry and orders its complement, then reconstructs every
parent by deleting the distinguished new leaf.  Both exact enumerations give
the same history and edge hashes.

## Exact channel Grams

Let \(P_k(a)=c_k a^k+o(a^k)\) be the certified leading count probability.
The three coefficients are

\[
 c_1=\frac1{16},\qquad
 c_2=\frac5{512},\qquad
 c_3=\frac9{8192}.
\]

The ordered resolution simplex contributes \(1/k!\).  Permutation symmetry
assigns the selected-history coefficient uniformly to every rooted comb, so
the factorial Gram per history is

\[
 w_k=\frac{k!c_k}{|\mathcal H_k|}.
\]

This gives

\[
 w_1=\frac1{48},\qquad
 w_2=\frac5{3072},\qquad
 w_3=\frac9{81920}.
\]

These are exactly the selected-history coefficients recorded by the
five-, six-, and seven-point certificates.  The minimal diagonal
channel/species lift is

\[
 \mathcal G_k=w_k I_{\mathcal H_k}\otimes I_2.
\]

It is strictly positive and has rank \(2|\mathcal H_k|\).  With normalized
species trace \(\operatorname{tr}_{\rm sp}=\operatorname{Tr}_2/2\), summing
over histories gives

\[
 \operatorname{Tr}_{\mathcal H_k}\operatorname{tr}_{\rm sp}\mathcal G_k
 =|\mathcal H_k|w_k
 =\frac{k!P_k(a)}{a^k},
\]

namely \(1/16\), \(5/256\), and \(27/4096\).

## Branching factorization

Every comb has a unique path from the hard state.  Consequently the positive
per-extension rate squares are fixed recursively by

\[
 q_{k-1}=\frac{w_k}{w_{k-1}},\qquad w_0=1.
\]

The exact values are

\[
 q_0=\frac1{48},\qquad
 q_1=\frac5{64},\qquad
 q_2=\frac{27}{400}.
\]

There is no negative rate and no moment-cone obstruction.  Since a level-\(k\)
history has \(d_k=k+3\) children, the total exit rates are

\[
 \Lambda_0=3q_0=\frac1{16},\qquad
 \Lambda_1=4q_1=\frac5{16},\qquad
 \Lambda_2=5q_2=\frac{27}{80}.
\]

The leading pure-birth probabilities are therefore

\[
 \Lambda_0a=\frac a{16},
\]

\[
 \frac{\Lambda_0\Lambda_1}{2}a^2
 =\frac{5a^2}{512},
\]

and

\[
 \frac{\Lambda_0\Lambda_1\Lambda_2}{6}a^3
 =\frac{9a^3}{8192}.
\]

Thus the growing channel carrier explains the certified history factorials
without treating the 12 and 60 histories as words over a fixed three-letter
alphabet.

## Completely positive normalized instrument

Use the reduced positive carrier

\[
 \mathcal K_{\le3}
 =\bigoplus_{k=0}^3\ell^2(\mathcal H_k)\otimes\mathbb C^2_{\rm species},
\]

of dimension \(2(1+3+12+60)=152\).  For every insertion edge
\(e:h\to c\) from level \(k\), define

\[
 L_e=\sqrt{q_k}\,|c\rangle\langle h|\otimes I_2.
\]

Then, for every parent history,

\[
 \sum_{c:h\to c}L_{h\to c}^{\dagger}L_{h\to c}
 =\Lambda_k|h\rangle\langle h|\otimes I_2.
\]

The finite generator

\[
 \mathcal L(\rho)=\sum_e
 \left(L_e\rho L_e^\dagger
 -\frac12\{L_e^\dagger L_e,\rho\}\right)
\]

is in exact GKSL form.  It generates a completely positive trace-preserving
semigroup.  The corresponding classical history generator is Metzler and has
zero column sums.  Level three is declared absorbing.

Starting from the hard state, the exact level probabilities are

\[
 p_0(a)=e^{-a/16},
\]

\[
 p_1(a)=\frac14\left(e^{-a/16}-e^{-5a/16}\right),
\]

\[
 p_2(a)=\frac{25}{88}e^{-a/16}
 -\frac{25}{8}e^{-5a/16}
 +\frac{125}{44}e^{-27a/80},
\]

\[
 p_3(a)=1-p_0(a)-p_1(a)-p_2(a).
\]

They solve the exact forward equations

\[
 \dot p_0=-\Lambda_0p_0,
\]

\[
 \dot p_1=\Lambda_0p_0-\Lambda_1p_1,
 \qquad
 \dot p_2=\Lambda_1p_1-\Lambda_2p_2,
 \qquad
 \dot p_3=\Lambda_2p_2,
\]

and obey \(\sum_{k=0}^3p_k(a)=1\) for every \(a\ge0\).  Positivity follows
from the conservative finite-state Markov generator, not from cancellation
between signed truncations.  The GKSL channel has a Stinespring dilation on
every bounded resolution interval.

## What this says about the Cox state

The two-atom Cox state and the branching instrument have the same unmarked
leading count moments through degree three.  Total counts alone therefore do
not choose between them.

They are not the same channel lift.  The previous local coherent carrier used
three one-emission pair marks.  Fixed three-letter words have dimensions

\[
 3,\quad 3^2=9,\quad 3^3=27,
\]

whereas the physical labeled comb sectors have dimensions

\[
 3,\quad12,\quad60.
\]

Thus a fixed three-mark Cox lift is not channel-faithful without enlarging its
mark space as particle multiplicity grows.  The rooted-comb branching carrier
does make that enlargement.  Within the balanced comb-Markov architecture,
the first three extension rates are uniquely fixed by the tree coefficients.
No all-order uniqueness follows.

## Physical boundary and next gate

The first jump has an exact physical affiliation: its three children are the
three unordered pair channels and each jump Gram is the certified
\((1/48)I_2\).  The construction therefore retains both physical jet species
and the correct per-pair normalization.

The scalar six- and seven-point tree calculations certify only a square-free
trace for each history.  Taking
\(w_kI_{\mathcal H_k}\otimes I_2\) is the minimal positive symmetry-compatible
lift.  It does not derive the off-diagonal species matrix or amplitude phase.
Likewise, making level three absorbing creates an exactly normalized finite
instrument but is not a statement that BT dynamics forbids a fourth emission.

Resolving the six-point constant/linear parent jets before this trace gives
the first exact obstruction.  The unique amplitude coefficients are
\((2Q_{\rm inner},a_2/2)\), and the pulled-back spectator-profile endomorphism
has a strictly negative characteristic discriminant above outer threshold.
It is therefore not similar to a positive scalar multiple of \(I_2\).
Certificate
`REVERSE_PHYSICS_BT_SIX_POINT_PARENT_JET_INTERFERENCE_V1` retains the scalar
\(5/3072\) history weight and this finite CPTP completion, but refutes its
amplitude affiliation above the first jump on the declared two-species
carrier.  The next physical gate is the minimal four-component parent-jet
times spectator-profile carrier.  On that grading-faithful carrier the exact
pullback has spectrum \(\{0,2uv\}\), a nondegenerate collapse-invisible
kernel, and a Krein-orthogonal two-dimensional image on which the raised Gram
is \(2uvI_2>0\).  Certificate
`REVERSE_PHYSICS_BT_SIX_POINT_PROFILE_QUOTIENT_COMPLETION_V1` proves the
pointwise quotient identity for the complete six-point amplitude, replays the
five-point physical prefix, and thereby affiliates the conditional second
rate \(5/64\) with the quotient species fibre.  The complete seven-point
pre-trace certificate
`REVERSE_PHYSICS_BT_SEVEN_POINT_PROFILE_QUOTIENT_AFFILIATION_V1` now resolves
the singleton/complementary-pair tensor on the same four-component carrier.
After the seven-leg delta-prime sign its quotient eigenvalue is positive, and
the arbitrary-vector identity affiliates the third rate \(27/400\).  Thus all
three available jumps are amplitude-affiliated.  The level-three absorbing
closure remains a construction; the eight-point pre-trace tensor separately
determines a possible \(q_3\) and tests continuation.

The successor certificate
`REVERSE_PHYSICS_BT_QUANTUM_STOCHASTIC_MOLLER_DILATION_V1` dilates this pinned
instrument to a strongly continuous unitary additive-resolution cocycle with
one Boson noise channel per insertion edge.  It reproduces this report's exact
generator hash under vacuum reduction.  Its global reverse annihilation terms
do not promote the reduced level-three closure to a physical terminal sector.

This certificate does not establish a complete physical \(2\to n\)
probability, incoming degenerate sectors, a BT asymptotic Hamiltonian, a
spacetime-local Møller/LSZ or unitary S operator, Eq. (19), anything
`LORENTZIAN-CAUSAL`, or a metric/BRST lift.

## Verification receipt

All symbolic jobs run sequentially under `ulimit -v 500000`.  The producer
uses direct rooted-comb insertion.  The verifier does not import it: it chooses
the cherry and orders the complementary labels, reconstructs parents by an
independent delete-leaf map, rebuilds the sparse generator, derives the rates
from the three predecessor certificates, and checks the exact probability
ODEs and normalization.

The close-out runs were:

| rail | exact command | result | elapsed | peak RSS |
|---|---|---:|---:|---:|
| producer | `ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/bt_channel_resolved_branching_instrument.py --write --check` | 19/19 PASS | 0.06 s | 17,020 kB |
| independent verifier | `ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/verify_bt_channel_resolved_branching_instrument.py` | 21/21 PASS | 0.62 s | 70,388 kB |
| mutation and unit suite | `ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 -m unittest -v reverse_physics.tests.test_bt_channel_resolved_branching_instrument` | 14/14 PASS | 1.84 s | 70,676 kB |
| Paper V, second pass | `ulimit -v 500000; cd paper && pdflatex -interaction=nonstopmode -halt-on-error 05-interaction-obstructions.tex` | PASS | 0.47 s | 51,076 kB |
| Paper VI, second pass | `ulimit -v 500000; cd paper && pdflatex -interaction=nonstopmode -halt-on-error 06-einstein-weyl-interaction-obstructions.tex` | PASS | 0.68 s | 50,600 kB |
| Science Forge import | `FORGE_LIB=/home/alstrup/area9/tango/forge/lib /tmp/forgebin -run /home/alstrup/area9/tango/forge/tools/science-forge/sfc.forge -- import-program planning/work-items /tmp/bt-branching-science-forge-graph.json graph` | 1,390 nodes; 0 invalid items; 0 malformed events | 5.61 s | 481,448 kB |

The advisory `ci/science-forge-shadow.sh` completed in 2.05 s with exit zero,
while reporting the pre-existing Forge toolchain/stdlib hash mismatch,
compiler diagnostic E9118 in the independent bridge audit, and corpus drift
from 976 to 1,531 certificates.  The bridge audit failure is not counted as a
pass.

Tier 0 Python compilation, JSON parsing, whitespace, content-hash, and exact
staged-diff checks and Tier 1 scoped tests were run.  A capped Git invocation
failed with `unable to create threaded lstat` and is not a pass; the uncapped
`git diff --check` then passed in 0.03 s at 10,924 kB.  The memory ceiling is
retained for Python and TeX research jobs rather than used to disable Git's
own status worker.  Tier 2 was unnecessary
because this is a new leaf over unchanged content-addressed predecessor
certificates.  Tier 3 was not run because no freeze, complete physical
probability, all-order theorem, shared core algebra, or Lorentzian claim was
promoted.  No skipped or advisory check is recorded as a pass.
