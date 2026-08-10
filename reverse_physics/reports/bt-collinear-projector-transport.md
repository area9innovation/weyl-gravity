# Bateman--Turok coherent collinear projector transport

> **SUPERSEDED NORMALIZATION (2026-08-10).**  This historical report inserted
> the absolute real-rate coefficient `1/512` directly into a dimensionless
> projector.  The corrected target is `1/48` per pair after division by the
> Born rate, with amplitude `sqrt(3)/12`, hard block `-1/16`, and total
> collinear block `+1/16`.  The projector architecture and idempotence argument
> survive.  The correction and the ordinary-Fock-generator obstruction are
> certified in
> [`REVERSE_PHYSICS_BT_ASYMPTOTIC_GENERATOR_PREFLIGHT_V1`](../certificates/REVERSE_PHYSICS_BT_ASYMPTOTIC_GENERATOR_PREFLIGHT_V1.json).

**Result:** `CLASSIFIED`

**Dependencies:** `LOCAL-ALGEBRAIC`, `REDUCED-MODE`

**Certificate:**
[`REVERSE_PHYSICS_BT_COLLINEAR_PROJECTOR_TRANSPORT_V1`](../certificates/REVERSE_PHYSICS_BT_COLLINEAR_PROJECTOR_TRANSPORT_V1.json)

## Result

The ordinary mass-regulator obstruction appeared to be bypassed at the finite exact
carrier level by changing the measured object.  Instead of the bare
block-diagonal sum of a hard two-particle projector and unresolved
three-particle projectors, use one projector whose image is coherently rotated
between the hard channel and the three unordered final-pair collinear channels.

Let the common factor `lambda^6*log(c)/(pi^4*s)` be suppressed.  The preceding
real-emission calculation supplies `+1/512` in each of the three pair channels,
hence `+3/512` in total.  An exact charge-neutral projector transport with
mixing amplitude

\[
 a=\sqrt{\frac1{512}}=\frac{\sqrt2}{32}
\]

then forces

\[
 \Delta P_{\rm hard}=-3a^2=-\frac3{512},\qquad
 \sum_{r=1}^3\Delta P_{rr}=+3a^2=+\frac3{512}.
\]

The response cancels.  The negative term is not a freely chosen finite
counterterm: it is the unique hard-block normalization required by
`P^2=P` once the first-order hard--collinear mixing is fixed.

This breaks the **finite algebraic normalization barrier**.  It does not yet
break the dynamical or continuum barrier.  The mixing norm was matched to the
certified real coefficient; it has not been derived from the BT/PS asymptotic
Hamiltonian.

## Exact construction

Use the four-dimensional carrier

\[
 (h,r_{12},r_{13},r_{23})
\]

over `Q(sqrt(2))`.  Here `h` is the hard channel and the three `r` entries are
the unordered collinear pair channels.  Start from

\[
 P_0=\operatorname{diag}(1,0,0,0)
\]

and the skew generator

\[
 K=
 \begin{pmatrix}
 0&-a&-a&-a\\
 a&0&0&0\\
 a&0&0&0\\
 a&0&0&0
 \end{pmatrix},\qquad K^T=-K.
\]

For a formal positive logarithmic resolution shell, write

\[
 U(\epsilon)=e^{\epsilon K},\qquad
 P(\epsilon)=U(\epsilon)P_0U(\epsilon)^{-1}
 =P_0+\epsilon P_1+\epsilon^2P_2+O(\epsilon^3).
\]

The exact calculation gives

\[
 P_1=[K,P_0],
\]

and

\[
 P_2=
 \begin{pmatrix}
 -3a^2&0&0&0\\
 0&a^2&a^2&a^2\\
 0&a^2&a^2&a^2\\
 0&a^2&a^2&a^2
 \end{pmatrix}.
\]

The off-diagonal entries in the collinear block are essential: this is a
coherent cross-multiplicity projector, not an incoherent weighted event sum.
The producer checks exactly that

\[
 U^TU=I+O(\epsilon^3),\qquad
 P^2=P+O(\epsilon^3),\qquad
 \operatorname{tr}P=1+O(\epsilon^3).
\]

No floating-point arithmetic occurs.

## Why the normalization is forced

The key fact does not depend on the exponential parameterization.  Write a
general formal projector

\[
 P=P_0+\epsilon P_1+\epsilon^2P_2
\]

and require `P^2=P` through order two.  The order-one equation says that `P1`
is purely hard--collinear.  The order-two equation is

\[
 P_0P_2+P_2P_0+P_1^2=P_2.
\]

If the hard--collinear block of `P1` is `A`, the diagonal blocks are uniquely
fixed:

\[
 (P_2)_{hh}=-AA^T,\qquad (P_2)_{cc}=A^TA.
\]

For `A=(a,a,a)` this is precisely `-3/512` versus `+3/512`.  Only an
order-two hard--collinear basis-gauge block remains free, and exponential
transport sets it to zero.  Omitting the negative hard term leaves an exact
hard idempotency defect `+3/512`; the independent verifier rejects that
mutation.

This locates the previous obstruction.  The bare real-plus-virtual
calculation compared separate particle-number blocks.  Such a block-diagonal
projector contains the positive Gram term but no normalization term tying it
back to the hard state.  An axis-compatible parent-mass map cannot manufacture
that term because its boundary response is zero.  Coherent projector transport
can, because the term follows from normalization rather than from the parent
mass logarithm.

## BT/Krein charge gate

The construction is placed only on the positive neutral quotient carrier; it
does not import a global positive Hilbert metric into the Krein theory.  Its
generator is declared charge-neutral.  The new producer and verifier recompute
the finite Laurent-charge fact needed here: a sandwich of total shift zero maps
every tested charge `q<0` back to `q<0`, while the decisive positive-shift
mutation sends `q=-2` to charge zero.  The charge-null preflight therefore
passes without importing the older inclusive-radical certificate.

That statement remains finite and algebraic.  It does not prove that a
continuum asymptotic generator exists, has the stated charge, is trace class,
or is produced by BT dynamics.  A positive-charge mutation is decisive: it
can send a negative-charge input to charge zero and make it trace-visible.

## Relation to known infrared architectures

Hannesdottir and Schwartz replace free asymptotic evolution by a universal
soft-collinear asymptotic Hamiltonian and interpret the resulting hard
S-matrix in terms of dressed states or factorization
([arXiv:1906.03271](https://arxiv.org/abs/1906.03271)).  Their later paper
shows explicit divergence cancellation when asymptotic evolution is retained
with hard cutoffs ([arXiv:1911.06821](https://arxiv.org/abs/1911.06821)).
Those gauge-theory results motivate the architecture, but no theorem or
coefficient is imported into this scalar Krein model.

The genuinely new question here is narrower: does the exact BT coefficient
admit a normalized cross-multiplicity projector compatible with the already
certified charge radical?  The finite answer is yes.  Literature priority is
not claimed for coherent/dressed asymptotic states as a general method.

## What moved

| Object | State |
|---|---|
| ordinary axis-compatible independent-mass regulator | `OBSTRUCTED` |
| finite coherent four-channel projector | `CONSTRUCTED` |
| compensating `-3/512` normalization | `FORCED_BY_IDEMPOTENCE` |
| cancellation of the finite carrier response | `EXACT` |
| neutral BT relative-radical preflight | `PASSES` |
| BT asymptotic-Hamiltonian derivation of the generator | `NOT_CONSTRUCTED` |
| continuum dressed projector | `NOT_CONSTRUCTED` |
| incoming degenerate sectors | `NOT_CONSTRUCTED` |
| full NLO quotient trace | `NOT_COMPUTED` |
| physical NLO probability | `NOT_ESTABLISHED` |

Subject to the superseding normalization notice above, the architecture
survives its finite projector test.  The
historical gate was no longer “find an arbitrary `-3/512` term.”  It was:

> Derive the first-order splitting generator from the broken-vacuum BT/PS
> dynamics and prove that its regulated Gram operator is `1/512` per pair.

The superseding preflight shows that this target was dimensionally wrong and
that the ordinary first-order single-denominator generator has zero collinear
Gram.  The live gate is the order-`lambda` Jordan/`R_t` distributional
generator with corrected target `1/48` per pair.

If the dynamical Gram coefficient differs, the finite witness does not
describe BT scattering.  The continuum calculation must also include incoming
degenerate sectors; a final-state jet projector alone cannot settle an
initial-state collinear problem.

## Claim boundary

This certificate does not establish:

- a dressed-state or KLN theorem for BT theory;
- that the displayed generator follows from the BT asymptotic Hamiltonian;
- existence, convergence, or trace-class control in the continuum;
- a complete NLO cross section or regulator-independent probability;
- positivity or unitarity beyond Bateman--Turok's tree theorem;
- a global Hilbert metric for the Krein theory;
- anything about the tensor/BRST gravitational lift; or
- anything `LORENTZIAN-CAUSAL`.

The coefficient input is the reduced-mode certificate
[`BT_REAL_VIRTUAL_AXIS_GLUING`](bt-real-virtual-axis-gluing.md).  The charge
input is the local-algebraic relative-radical certificate.  These dependency
types remain distinct.

## Verification

```text
ulimit -v 500000; python3 reverse_physics/bt_collinear_projector_transport.py --check
ulimit -v 500000; python3 reverse_physics/verify_bt_collinear_projector_transport.py
ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_collinear_projector_transport
```

The independent verifier does not import the producer.  It parses the sparse
`Q(sqrt(2))` matrices, independently solves the order-two projector equation,
checks the three diagonal responses, validates the predecessor hashes, and
rejects removal of the hard normalization.  A second mutation assigns a
positive BT charge shift and must also be rejected.

Final scoped receipt (wall time measured with `/usr/bin/time`, 2026-08-10):

| Tier | Command | Time | Result |
|---|---|---:|---|
| 0 | `python3 -m py_compile` on producer, verifier, and test | 0.04 s, 15,976 KB | PASS |
| 0 | `python3 -m json.tool` on certificate, schema, and work item | 0.10 s, 14,732 KB | PASS |
| 1 | producer `--check` | 0.04 s, 20,680 KB | PASS, 18/18 |
| 1 independent | independent verifier | 0.10 s, 29,984 KB | PASS, 13/13 |
| 1 direct consumers | 33 focused projector, axis-gluing, and charge tests | 22.67 s, 74,616 KB | PASS, 33/33 |

The first direct-consumer run failed closed because the system Python lacks
SymPy, while the axis-gluing rail declares the repository's Python 3.12
environment.  It also exposed pre-existing provenance drift in the older
inclusive-radical certificate: its embedding-note hash predates current
`master`.  This certificate does not import that stale artifact; it recomputes
the finite neutral-shift fact independently.  The older certificate was left
untouched rather than causing an unrelated transitive hash cascade.  The
failed run was not counted as a pass.

The successor work-item JSON parses.  A full `sfc import-program` was attempted
under the same 500,000 KB cap, but the Go runtime failed while reserving its
page-summary address space before evaluating the item.  The memory cap was not
relaxed, and that planning import is recorded as **not run to a result**, not
as a pass.  The item follows the existing `work-v0` structure; programme-level
folding remains an advisory follow-up.

Paper 05 now records the finite transport as Remark 14.4, and Paper 06 records
only the non-transfer boundary.  Both PDFs were rebuilt twice under the
500,000 KB cap.  Final passes were 0.41 s / 50,748 KB for Paper 05 and
0.42 s / 50,428 KB for Paper 06.  Paper 06 has no warnings or overfull boxes;
Paper 05 retains only its three small pre-existing overfull boxes.  PDF text
extraction independently found the coefficient, finite-carrier scope, and
open asymptotic-Hamiltonian boundary in both artifacts.

Tier 2 was not required because no mathematical predecessor, shared operator,
or imported artifact changed; this result imports unchanged content-addressed
inputs.  Tier 3 is
not a freeze, theorem promotion, shared-core change, or release.  Any skipped
higher tier will be recorded as skipped, not passed.

EVIDENCE: `reverse_physics/certificates/REVERSE_PHYSICS_BT_COLLINEAR_PROJECTOR_TRANSPORT_V1.json`
