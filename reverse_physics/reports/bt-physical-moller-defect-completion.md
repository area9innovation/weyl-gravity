# BT physical Møller defect completion

**Certificate:**
`REVERSE_PHYSICS_BT_PHYSICAL_MOLLER_DEFECT_COMPLETION_V1`

**Lifecycle:** `CLASSIFIED`

**Dependencies:** `LOCAL-ALGEBRAIC`, `REDUCED-MODE`

## Result

The certified finite-hierarchy physical vacuum column always admits a
two-sided unitary completion.  The completion is not unique: it requires an
arbitrary unitary map on an infinite-dimensional incoming defect continuum,
and the published vacuum amplitudes contain no information about that map.

This cleanly separates two questions that were previously bundled together.
There is no remaining abstract Hilbert-space unitarity obstruction once the
isometric column exists.  The remaining problem is physical affiliation:
constructing the incoming continuum and its action from the BT asymptotic
Hamiltonian, with the required trace, crossing, resolution and locality
properties.

## Universal completion theorem

Let

\[
 I:H_{\rm hard}\longrightarrow K_{\rm phys}
\]

be the incoming hard inclusion and let

\[
 M_a:H_{\rm hard}\longrightarrow K_{\rm phys},\qquad
 M_a^*M_a=1,
\]

be the certified physical vacuum Møller column.  Define

\[
 P_{\rm in}=II^*,\qquad P_{\rm out}=M_aM_a^*,
\]

\[
 D_{\rm in}=1-P_{\rm in},\qquad
 D_{\rm out}=1-P_{\rm out}.
\]

If \(W\) is a partial unitary between the two defects,

\[
 W^*W=D_{\rm in},\qquad WW^*=D_{\rm out},
\]

then

\[
 \boxed{S_W=M_aI^*+WD_{\rm in}}
\]

obeys

\[
 S_W^*S_W=S_WS_W^*=1,
 \qquad S_WI=M_a.
\]

Conversely, every same-space unitary \(S\) with \(SI=M_a\) has this form,
with

\[
 W=D_{\rm out}SD_{\rm in}.
\]

Thus the column determines the action on the two-dimensional hard input and
nothing on its orthogonal complement.  The minimum additional incoming space
is unitarily isomorphic to \({\rm Ran}\,D_{\rm out}\); a smaller space cannot
make the column surjective.

There is also a basis-free Julia completion,

\[
 \mathcal J(M_a)=
 \begin{pmatrix}
 M_a&D_{\rm out}\\
 0&-M_a^*
 \end{pmatrix},
\]

which is unitary from \(H_{\rm hard}\oplus K_{\rm phys}\) to
\(K_{\rm phys}\oplus H_{\rm hard}\).  It proves existence without selecting
a physical identification of the defect sectors.

## Exact finite witness and nonuniqueness

Compress the four orthogonal outcome levels to probabilities

\[
 (p_0,p_1,p_2,p_3)=\left(\frac12,\frac14,\frac18,\frac18\right)
\]

and retain both physical species.  The reference inclusion and output column
are

\[
 I=e_0\otimes I_2,\qquad
 M=(\sqrt{p_0},\sqrt{p_1},\sqrt{p_2},\sqrt{p_3})^T\otimes I_2.
\]

Both have rank two in an eight-dimensional output, so both defects have rank
six.  The exact Householder matrix sending \(e_0\) to the outcome-amplitude
vector, tensored with \(I_2\), gives one unitary \(S_0\) satisfying
\(S_0I=M\).

A nontrivial rational rotation

\[
 \begin{pmatrix}3/5&-4/5\\4/5&3/5\end{pmatrix}
\]

inside two incoming defect directions fixes \(I\).  Precomposing \(S_0\) by
that rotation gives a different exact unitary \(S_1\), while

\[
 S_1I=S_0I=M.
\]

The producer and independent verifier check both unitaries, both defect
partial-isometry identities, their distinct hashes, and the ten-dimensional
Julia identity exactly.  The witness is not being substituted for the
continuum calculation; it tests the universal algebra and demonstrates live
nonuniqueness.

## The actual physical defect is infinite

The physical output is not eight-dimensional.  It is the direct sum of the
hard range and the nested five-, six-, and seven-point continuum ranges for
all 75 currently available edge marks.  Already the one-emission sector
contains compactly supported \(L^2\) sections on a nonempty resolution
interval.  Its Hilbert dimension is countably infinite, whereas
\({\rm Ran}\,M_a\) has dimension two.

Therefore

\[
 \dim {\rm Ran}(1-M_aM_a^*)=\aleph_0
 \qquad(a>0).
\]

A same-space two-sided completion needs a complete incoming continuum of this
size and a unitary map from it onto the outgoing defect.  Rotating that
incoming defect by any unitary leaves every vacuum-column amplitude and every
probability already certified in \(M_a\) unchanged.  Even a one-parameter
phase family is invisible.

The public amplitudes therefore cannot select the two-sided operator.  This
is not a defect of the calculations: a single column never contains the
scattering of arbitrary incoming states.

## Consequence for the physical route

The result advances the physical route in two ways:

1. A two-sided unitary completion is proved to exist at the abstract
   reduced-mode level.  Positivity and normalization of the known vacuum
   column are compatible with a full unitary.
2. The missing object is now exact.  It is not one more scalar coefficient;
   it is an infinite-dimensional defect partial unitary \(W\), together with
   a physical identification of its incoming states.

The next calculation must derive \(W\) from the regulated BT asymptotic
Hamiltonian or obstruct it after imposing resolution translation, the nested
Källén intertwiners, crossing and the generalized-Born trace.  Choosing a
mathematical \(W\) is not evidence that BT dynamics chooses it.

## Claim boundary

Established exactly:

- existence and complete parameterization of same-space unitary extensions;
- the converse theorem and minimal defect dimension;
- a basis-free Julia completion;
- two distinct exact finite unitaries with the same physical column;
- rank-six finite compressed defects; and
- countably infinite defect multiplicity on the actual continuum carrier.

Not established:

- a preferred defect action;
- derivation from the BT Hamiltonian;
- incoming/outgoing LSZ identification or crossing;
- spacetime locality, causality, cluster decomposition or a spectral
  condition;
- a fourth jump or complete \(2\to n\) probability;
- the finite NLO constant or positivity beyond the finite hierarchy;
- all-order Eq. (19), a gravity/BRST lift, or anything
  `LORENTZIAN-CAUSAL`; or
- literature priority.

## Literature boundary

The public source remains Bateman and Turok,
[arXiv:2607.00096v1](https://arxiv.org/abs/2607.00096), submitted
2026-06-30.  A search on 2026-08-12 found no public companion containing the
deferred Eq. (19) proof or a dressed two-sided Møller construction.  The
certificate therefore makes no literature-priority claim.

## Verification receipt

All scientific Python, SymPy and TeX processes ran sequentially on
2026-08-12 under `ulimit -v 500000`, using Python 3.12.13 at
`/home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3`.

- Tier 0 Python compilation passed in 0.03 s with 14,980 KiB peak RSS.
- Tier 0 parsing passed for the work item, append-only event, schema and
  certificate; the timed parse took 0.03 s with 13,852 KiB peak RSS.
- The exact producer reproduced the certificate and passed 28/28 checks in
  1.67 s with 70,212 KiB peak RSS.
- The independent reconstruction passed 23/23 checks, including schema and
  input hashes, in 1.47 s with 73,944 KiB peak RSS.
- The falsification suite passed 20/20 tests in 16.57 s (16.61 s including
  timing overhead), with 74,176 KiB peak RSS.  Mutations covered the outcome
  probabilities and amplitudes, Householder and defect rotations, defect
  ranks, unitary hashes, universal formula, continuum dimension and dense
  core, missing input, source audit, claim promotions, scope and provenance.
- Papers V and VI compiled twice.  Their final passes took 0.49 s and 0.50 s
  with at most 50,868 KiB peak RSS.  Paper V retains its four pre-existing
  overfull boxes and introduces no new one; Paper VI has no overfull box or
  undefined reference.  PDF text extraction found the theorem, infinite
  defect and non-promotion boundary in both rendered papers.
- The narrow Science Forge import-program check accepted all 1,433 nodes
  with zero invalid items and zero malformed events in 15.32 s, using
  280,308 KiB peak RSS.  It ran with GOMEMLIMIT=256MiB, GOMAXPROCS=1 and a
  60 s timeout.
- The broader advisory Science Forge shadow rail did not complete under the
  500,000 KiB virtual-address cap: its Go/cbp tooling aborted during
  preflight.  This is recorded as a resource-limited non-pass, not as audit
  evidence; the narrower program validation above covers the changed planning
  records.

The producer imports both mathematical predecessors by content hash.  Its
universal completion proof, the exact finite nonuniqueness witness and the
method-independent verifier form the affected Tier 2 chain for this new leaf.
Tier 3 was not run because no shared core, freeze, release, lifecycle
promotion beyond `CLASSIFIED`, complete BT probability, Eq. (19), spacetime
S operator, gravitational transfer or Lorentzian claim changed.  No skipped
tier is reported as a pass.
