# BT eight-point hard-profile obstruction

**Certificate:** `REVERSE_PHYSICS_BT_EIGHT_POINT_HARD_PROFILE_OBSTRUCTION_V1`

**Lifecycle:** `CLASSIFIED`

**Dependencies:** `LOCAL-ALGEBRAIC`, `REDUCED-MODE`

## Result

The complete eight-point tree does **not** continue the bare hard-independent
scalar hierarchy that fixed the second and third ordered moments at six and
seven points.  The obstruction appears before a physical fourth moment can be
read off.

For eight labeled external legs the complete cubic/quartic topology count is

\[
 \begin{array}{c|c}
 (V_3,V_4)&\text{trees}\\ \hline
 (6,0)&10395\\
 (4,1)&17325\\
 (2,2)&6300\\
 (0,3)&280
 \end{array}
\]

for a total of (34300) trees.  The exact subset-current recursion sums all
of them.  On both declared hard fixtures the amplitude begins at common
external-mass order (delta^2), and all eight square-free spectator masks
are present.

The two fixtures have exactly the same soft data

\[
 (a_0,a_1,a_2,a_3,a_4,\tau_1,\tau_2,\tau_3,\tau_4)
 =(1,4,3,2,1,10,7,5,3).
\]

They also have the same triple and quartet hard invariants.  They differ only
in the last adjacent hard invariant, which is changed from (33) to (34).

## Why the complementary products must be summed first

The leading amplitude is a three-bit square-free spectator jet.  Its
individual components, and even its four complementary products, need not
possess separate ordered hierarchy limits.  The physical projector is the
coefficient of the full spectator product in the square.  It is therefore
formed first as

\[
 [\eta_5\eta_6\eta_7]A_8^2
 =2\sum_{m=0}^{3} A_{8,m}A_{8,7-m}.
\]

Only this summed rational function is subjected to the ordered hierarchy.
This ordering avoids assigning separate infinities to terms that can cancel
only in the complete projector.

The two complete projected squares have the same ordered valuation

\[
 (\nu_{\epsilon_1},\nu_{\epsilon_2},\nu_{\epsilon_3})=(0,0,-1).
\]

Thus the bare fourth hierarchy retains an outer (1/\epsilon_3) pole.  More
importantly, the exact leading residues are

\[
 R_{33}=\frac{628651753}{1317120000},\qquad
 R_{34}=\frac{412771753}{1317120000},
\]

and hence

\[
 \boxed{R_{33}-R_{34}=\frac{257}{1568}\ne0.}
\]

The hard-independent scalar kernel used at six and seven points therefore
does not exist on this bare eight-point hierarchy carrier.

## Independent finite-point rail

The producer works over the rational-function field in the three hierarchy
parameters and uses dot-product cubic vertices.  The independent verifier
instead:

1. substitutes the exact finite hierarchy point
   ((\epsilon_1,\epsilon_2,\epsilon_3)=(1/5,2/7,3/11)) before the recursion;
2. uses its own rational Laurent and square-free algebras; and
3. evaluates the cubic vertex through the invariant triangle polynomial.

It reproduces the two complete projected values

\[
 \frac{520471052635202957}{31004982162000000},
 \qquad
 \frac{511691474216301555234829}
 {31171230876352644000000}.
\]

Their difference is

\[
 \frac{204441102626227759}{550777115935200000}\ne0.
\]

This method-distinct check confirms that the hard dependence is in the
complete tree, rather than an artifact of the symbolic hierarchy extractor.

## Consequence for the fourth moment

The provisional compact recurrence and its candidate inner coefficient
(629) are withdrawn.  In particular, this result does not rule out the
two-atom Cox completion selected by the first three moments.  Its fourth
prediction remains a target, not a failed theorem:

\[
 m_4^{(2\text{-atom})}=\frac{73}{32768},\qquad
 P_4^{(2\text{-atom})}=\frac{73}{786432}.
\]

There are three possible ways the physical fourth coefficient could still
emerge:

- the outer fixed-invariant Källén reduction could cancel the bare
  (1/\epsilon_3) pole and its hard dependence;
- the correct pre-trace quotient could retain a hard-profile component that
  becomes scalar only after recombination; or
- the physical count process may require a channel- and hard-profile-valued
  fourth jump rather than one universal scalar rate.

The next calculation must therefore retain (epsilon_3) through the outer
threshold integral and reduce the complete projected square before taking
the massless hierarchy limit.  A fourth Cox comparison is authorized only if
that reduced coefficient becomes hard independent after normalization.

## Claim boundary

Established exactly:

- the complete (34300)-tree topology and recursion on two exact fixtures;
- common leading order (delta^2) and all eight spectator masks;
- the common ordered valuation ((0,0,-1));
- nonzero finite-point hard dependence on an independent rail;
- the exact residue difference (257/1568).

Not established:

- nonexistence of a threshold-integrated fourth factorial moment;
- failure of every hard-profile or channel-resolved quotient;
- exclusion of the two-atom Cox completion;
- a complete (2\to6) probability;
- an all-order physical Møller or LSZ operator;
- all-order Eq. (19), a gravity/BRST lift, or anything
  `LORENTZIAN-CAUSAL`.

## Resource disposition

Early full-symbolic and componentwise-limit prototypes reached the declared
memory cap or produced unresolved separate infinities.  No uncapped symbolic
job was run.  The successful construction fixes the nine soft variables at
exact rational data, retains only the three hierarchy variables symbolically,
and sums complementary products before any limit.  The two final producer
fixtures remained below (103\) MB RSS.  The independent verifier used about
(20\) MB RSS.

The exhaustive producer is an affected-certificate rail.  Routine edit
checks use `--fast-check` on the content-addressed certificate and the
method-distinct finite-point verifier, whose complete two-fixture run takes
about six seconds.

## Verification receipt (2026-08-11)

All scientific Python, SymPy, and TeX commands ran sequentially under
`ulimit -v 500000`.

| tier | command or check | result | elapsed | peak RSS |
|---|---|---:|---:|---:|
| 0 | Python compile of producer, verifier, and tests; JSON parse of work item, certificate, and schema | PASS | 0.13 s | below 20 MB |
| 1 fast | certificate content/hash check | PASS | 0.04 s | below 20 MB |
| 1 | method-distinct two-fixture rational-series verifier | PASS, 12/12 | 4.04 s | 31,056 KB |
| 1 | fast producer/verifier plus eleven falsifying mutations | PASS, 13/13 | 47.77 s | 31,468 KB |
| 2 affected certificate | exhaustive two-fixture rational-function producer drift check | PASS, 12/12 | 89.46 s | 103,168 KB |
| paper | Paper V two-pass PDF build | PASS; no new overfull box | 0.45 / 0.46 s | 50,996 / 50,716 KB |
| paper | Paper VI two-pass PDF build | PASS; no warning or overfull box | 0.47 / 0.48 s | 50,768 / 50,888 KB |
| advisory | `ci/science-forge-shadow.sh` | INCONCLUSIVE; two capped `cbp` helpers aborted and the silent census was terminated after 3:37, exit 130 | 217.06 s | 59,956 KB parent RSS |

Paper V retains four pre-existing overfull boxes and its pre-existing
PDF-string warnings.  The inserted passage creates no new warning.  The
successful symbolic rails remained below (104) MB; earlier failed
componentwise prototypes were not counted as passes and promoted no claim.
The advisory Science Forge run is likewise not a pass and is not used by the
certificate.

Tier 2 stops at this new certificate and its direct paper consumers: all
predecessor certificates are imported by unchanged content hashes, and no
downstream mathematical certificate consumes the new result yet.  Tier 3 is
unnecessary because this is a fail-closed `CLASSIFIED` preflight, not a freeze,
release, shared-core-algebra change, or theorem/lifecycle promotion.
