# Fully rearranged BT $V_4^3$ triangle block

**Certificate:** `REVERSE_PHYSICS_BT_FULLY_REARRANGED_V4_CUBED_TRIANGLE_BLOCK_V1`

**Tags:** `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`, `REDUCED-MODE`.
**Lifecycle:** `COEFFICIENT_COMPUTED` for the isolated covariant block.

## Result

The first loop block selected by the fully rearranged $q_{10}$ ledger is
now computed.  In the public auxiliary theory,

\[
 S_{\mathrm{int}}={g\over2}\int \Omega^2\Upsilon^2,
 \qquad g=\lambda^2,
\]

the $V_4^3$ six-leg graph has three momentum-independent quartic vertices
joined by three cross-only propagators.  With $\lambda^6$ outside the
coefficient, its covariant value is

\[
 \boxed{
 T_{6,V_4^3}^{\mathrm{cov}}
 ={8\over16\pi^2}\sum_{P\in\operatorname{Pair}(6)}
 C_0(Q_{P,1}^2,Q_{P,2}^2,Q_{P,3}^2)S_P .}
\]

Here $P$ runs over the fifteen perfect pairings of the six labeled external
legs, $Q_{P,j}$ is the momentum entering the corresponding vertex, and

\[
 C_0(s_1,s_2,s_3)=
 \int_{x,y,z\geq0}\!dx\,dy\,dz\,
 {\delta(1-x-y-z)\over
  -xy s_1-yz s_2-zx s_3-i0}
\]

is the declared massless scalar triangle master.  The factor eight is the
product of the three auxiliary vertex tensors divided by $g^3$.  The
remaining multiplicity is carried exactly by $S_P$.

This is one term in $y_6$, hence one term in

\[
 q_{10}=\langle y_5,y_5\rangle
 +2\operatorname{Re}\langle y_4,y_6\rangle.
\]

It is not the complete $q_{10}$ coefficient.

## Exact species routing

Represent an external assignment by a six-bit mask, with $\Omega=1$ and
exactly three bits set.  There are twenty such assignments.  At each vertex
the two external legs and two internal half-edges must contain two
$\Omega$'s and two $\Upsilon$'s; the two ends of every internal edge must
have opposite species.

Direct enumeration gives, for every one of the fifteen pairings:

- twelve external assignments with one internal routing;
- eight external assignments with two internal routings; and
- squared Hilbert--Schmidt tensor norm $12+4(8)=44$.

For any fixed neutral external assignment, summing its routing weight over
all fifteen pairings gives exactly $21$.  On the dressed positive source
$u_0=(|000\rangle+|111\rangle)/\sqrt2$,

\[
 S_Pu_0=w_Pu_0,
 \qquad
 w_P=\begin{cases}
 2,&P\text{ pairs every input leg with an output leg},\\
 1,&\text{otherwise}.
 \end{cases}
\]

There are six pairings of the first kind and nine of the second.

The independent verifier does not reuse the producer's edge-orientation
enumeration.  It forms the fifteen matchings as a quotient of all $6!$
permutations and enumerates all $2^6$ internal half-edge species strings,
then imposes the three edge and three vertex constraints.

## Tree--triangle incidence

Let $\mathcal R_B$, $B=0,\ldots,9$, be the full eight-dimensional Choi lifts
of the ten certified positive-frame tree residue matrices.  The exact
$10$-by-$15$ full-carrier species cross Gram is

\[
 G_{BP}=\operatorname{Tr}(\mathcal R_B^*S_P)
 \in\left\{6,{13\over2}\right\}.
\]

It contains sixty entries equal to $6$ and ninety equal to $13/2$.
Every row sums to $189/2$, and every column sums to $63$.  These numbers
are combinatorial; no triangle integral or kinematic fixture is fitted to
them.  Restriction to the positive four-frame divides every entry by two, so
the corresponding values are $3$ and $13/4$.  Keeping these carriers distinct
avoids importing a full-Choi trace as a positive-frame probability.

## No UV counterterm

The graph has

\[
 (V_4,I,E,L,d_\lambda)=(3,3,6,1,6).
\]

Its superficial ultraviolet degree in four dimensions is

\[
 \omega=4L-2I=4-6=-2.
\]

It has no proper loop subgraph.  Therefore this isolated block is ultraviolet
finite, has no subtraction-scale dependence, and requires no local
counterterm.  This is simpler than the two-quartic four-point bubble, whose
$\omega=0$ local divergence requires coupling renormalization.

## Nonempty hard packet domain

At the exact rational fully rearranged detector center, put the three outgoing
momenta into all-incoming convention.  For all fifteen pairings, every
triangle leg is off shell.  Exact rational evaluation gives

\[
 \min_{P,j}|Q_{P,j}^2|={32\over625},
 \qquad
 \min_P|\lambda_K(Q_{P,1}^2,Q_{P,2}^2,Q_{P,3}^2)|
 ={80896\over903125},
\]

where $\lambda_K$ is the Källén discriminant.  Hence the packet neighborhoods
can be shrunk while remaining separated from every massless soft/collinear
triangle locus and every triangle Landau discriminant.  On that compact
neighborhood the fifteen scalar masters are locally bounded.  After reducing
the common momentum-conservation delta, their finite species sum defines a
Hilbert--Schmidt covariant packet kernel.

This regularity statement is local to the certified hard packet domain.  It
does not claim a global triangle bound across threshold or collinear strata.

## Ghost parity and the Born rule

Total three-particle ghost parity complements all six species bits.  Every
routing has a complemented routing, so coefficientwise

\[
 \kappa_3S_P\kappa_3=S_P.
\]

The scalar triangle masters and momentum packet projectors commute with
$\kappa_3$.  The already certified $T_4$ is also fixed.  Therefore the
isolated tree--triangle interference operator obeys

\[
 T_4^\sharp T_{6,V_4^3}+T_{6,V_4^3}^\sharp T_4
 =T_4^*T_{6,V_4^3}+T_{6,V_4^3}^*T_4.
\]

Thus this particular contribution is common to the public Krein and positive
Hilbert prescriptions.  This does **not** determine its sign: the complex
triangle masters and coherent packet overlaps still enter.

## What remains

The covariant coefficient is not yet identified with the third-order
finite-duration auxiliary Dyson kernel.  A sharp finite-time switching
calculation can contain transient energy-denominator terms that are absent
from the covariant boundary.  That affiliation must be derived before this
block is inserted into the finite-time $q_{10}$ experiment.

Three further connected order-six classes remain:

\[
 V_3^2V_4^2,\qquad V_3^4V_4,\qquad V_3^6.
\]

Complete $q_{10}$ additionally needs the full $y_5$ norm, source and
detector dressing through second order, and vacuum/survival normalization.
No sign, finite-coupling positivity, general Eq.~(19), gravitational transfer,
or `LORENTZIAN-CAUSAL` conclusion follows from this block.

## Verification receipt

All scientific Python and TeX processes ran sequentially below the 500 MB
virtual-memory ceiling.

- Tier 0 passes.  The three Python files compile, all changed JSON parses, the
  Draft-2020-12 schema is strict and valid, an injected extra property is
  rejected, and the final scoped diff has no whitespace error.  Strict schema
  validation took `0.10 s` at `21824 KiB` peak RSS.
- The producer passes `32/32` checks in `0.03 s` at `16720 KiB`.  The
  method-distinct verifier passes `36/36` in `0.03 s` at `15444 KiB`.  All
  `23` focused tests, including `22` adversarial mutations, pass in `0.230 s`
  (`0.26 s` enclosing wall time) at `18624 KiB`.
- The ten-command affected Tier-2 chain passes for the q10 ledger, common-Born
  theorem, fully rearranged support theorem, auxiliary active one-loop tensor,
  and ten-channel packet instrument.  It took `2.17 s` at `71976 KiB`.
- Papers V and VI compile twice with no undefined citation or reference and no
  new overfull box.  Their PDFs remain `79` and `68` pages and contain
  `740870` and `699116` bytes, with SHA-256
  `bb7a59e8eb12adb2e1f8146f33f3535f2399c82783e13c8f5e4a31f340f11be0`
  and `c2e14fc31748293c74eeecdf062db57a7110b6b2239bfe4c8ed3994d46ccb3c2`.
  The four-pass build took `2.09 s` at `51036 KiB`; Paper V retains six known
  overfull boxes and Paper VI two.
- Tier 3 is fail-closed, not a repository-wide pass.  With system tools ahead
  of semantic-search shims, `3209` tests ran in `702.712 s` (`703.74 s` wall)
  at `391704 KiB`, with the established `31` failures and `9` skips.  All
  `23` new tests pass.  The failures remain older certificate drift and the
  fifteen-path `chain_imports` policy list; none is counted as a pass.
- The append-only planning fold accepts `1573` nodes with zero invalid items
  and zero malformed events in `1.47 s` at `14260 KiB`.
- The advisory Science Forge shadow wrapper exits zero by design in `1.96 s`
  at `334464 KiB`, but its bridge audit remains fail-closed at the known
  toolchain/standard-library `E9118` mismatch.  Its read-only census finds
  `1626` certificates and `1407` verifier files.  This advisory exit is not
  theorem evidence.

Tier 3 was required because Papers V and VI acquire a
`COEFFICIENT_COMPUTED` loop theorem.  No classical freeze, QME state,
residual transfer or `LORENTZIAN-CAUSAL` state changed.  The final certificate
SHA-256 before staging is
`6dc5d75dc19acfc827b702632192def1cdd02ddf034db2637b52373ad6e1adde`.

CLOSE-OUT: DONE -- the isolated covariant $V_4^3$ triangle coefficient,
species tensor, hard-packet domain and common-Born class are exact;
finite-duration affiliation and complete $q_{10}$ remain open.

EVIDENCE:
`reverse_physics/certificates/REVERSE_PHYSICS_BT_FULLY_REARRANGED_V4_CUBED_TRIANGLE_BLOCK_V1.json`
