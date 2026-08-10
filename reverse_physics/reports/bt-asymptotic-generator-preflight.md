# Bateman--Turok asymptotic-generator preflight

**Result:** `CLASSIFIED`

**Dependencies:** `LOCAL-ALGEBRAIC`, `REDUCED-MODE`

**Certificate:**
[`REVERSE_PHYSICS_BT_ASYMPTOTIC_GENERATOR_PREFLIGHT_V1`](../certificates/REVERSE_PHYSICS_BT_ASYMPTOTIC_GENERATOR_PREFLIGHT_V1.json)

## Result

The finite coherent-projector architecture survives, but its first certificate
used the wrong normalization.  The real-emission number `1/512` is an
**absolute rate coefficient** after the common factor
`lambda^6*log(c)/(pi^4*s)` is removed.  A projector correction is
dimensionless and multiplies the Born rate.  Bateman--Turok's Born rate is

\[
 B=\frac{3\lambda^4}{32\pi^2s}.
\]

Consequently the dimensionless Gram coefficient required for each unordered
final pair is

\[
 \frac{\lambda^6\log c/(512\pi^4s)}
      {3\lambda^4/(32\pi^2s)}
 =\frac{\lambda^2\log c}{\pi^2}\frac1{48}.
\]

With
\(\eta=\lambda^2\log c/\pi^2\), the exact target is therefore `1/48`
per pair and `1/16` for all three pairs.  The normalized finite projector has

\[
 a=\sqrt{\frac1{48}}=\frac{\sqrt3}{12},\qquad
 (P_2)_{hh}=-\frac1{16},\qquad
 \sum_r(P_2)_{rr}=+\frac1{16}.
\]

Multiplying the hard block by the Born rate gives

\[
 B\,\eta\left(-\frac1{16}\right)
 =-\frac{3\lambda^6\log c}{512\pi^4s},
\]

which cancels the certified three-pair real response exactly.  This corrects,
rather than removes, the finite algebraic construction.

The same preflight finds the first exact dynamical obstruction.  For two
massless daughters with parent virtuality `t`, the published cubic vertex has

\[
 \mathcal M_3=-i\lambda\,\lambda_K(t,0,0)
              =-i\lambda t^2,
\]

while their energy deficit is

\[
 \Delta E=\frac{t}{2E}+O(t^2).
\]

An ordinary first-order Dyson/Fock asymptotic kernel therefore scales as

\[
 \frac{\mathcal M_3}{\Delta E}=O(t)\longrightarrow0.
\]

Its Gram operator is zero and cannot equal the nonzero target `1/48`.  A
double/Jordan denominator instead has a finite power-counting limit,
`M3/(Delta E)^2 -> -4 i lambda E^2`.  This is only a necessity result: the
corresponding distributional generator, its domain, normalization, incoming
sectors, and pseudo-unitarity have not been constructed.

## Correction ledger

The predecessor
[`REVERSE_PHYSICS_BT_COLLINEAR_PROJECTOR_TRANSPORT_V1`](../certificates/REVERSE_PHYSICS_BT_COLLINEAR_PROJECTOR_TRANSPORT_V1.json)
is retained as an immutable historical artifact and marked
`SUPERSEDED_NORMALIZATION`.  It inserted `1/512` directly into a dimensionless
projector.  In the corrected shell units its hard contribution would have
absolute coefficient `9/16384`, leaving nonzero residual `87/16384`; the
independent verifier checks that this error is numerically live.

Nothing in the predecessor's projector algebra is invalid.  Replacing
`a^2=1/512` by `a^2=1/48` preserves skew transport, order-two idempotence, and
trace preservation exactly, now over `Q(sqrt(3))`.

## Why the public asymptotic formula is not yet enough

Bateman and Turok write their free asymptotic map `R_t` only through leading
order, with corrections denoted `O(lambda)`.  The cross-multiplicity kernel
needed here is precisely an order-`lambda` object.  The cubic vertex determines
its numerator, but the ordinary single secular denominator gives zero.  The
missing object is therefore not an arbitrary fit: it must be the order-`lambda`
Jordan/double-secular part of `R_t`, or an equivalent distributional
asymptotic generator, and its exact Gram must be `1/48` per pair.

This calculation does not infer that such a term exists.  It says what any
successful construction must contain and gives a sharp zero-versus-`1/48`
test.

The source equations are Bateman--Turok's Born rate, cubic vertex, and
leading asymptotic map in
[arXiv:2607.00096v1](https://arxiv.org/abs/2607.00096).  The calculation above
uses those formulas but does not import the paper's tree-level positivity
claim into the loop problem.

## Charge gate

Around the chosen broken vacuum the cubic monomial is one Omega fluctuation
times two Upsilon fields.  With the BT charges used by the finite radical
calculation its bare charge is

\[
 q(\Omega)+2q(\Upsilon)=+1-2=-1.
\]

Thus the earlier declaration of a neutral finite generator cannot be inferred
from the bare cubic vertex.  The background transforms under the broken
boost, so background/spurion factors and the full `R_t` action must be included
before charge neutrality can be tested.  The charge gate is
`NOT_CLEARED_BY_BARE_CUBIC_VERTEX`, not failed for every possible dressed
construction.

## What moved

| Object | State |
|---|---|
| absolute real response per final pair | `1/512`, unchanged |
| dimensionless projector Gram target per pair | `CORRECTED_TO_1/48` |
| finite normalized four-channel projector | `CONSTRUCTED` |
| ordinary single-denominator Fock generator | `OBSTRUCTED` |
| order-`lambda` Jordan/`R_t` generator | `NOT_CONSTRUCTED` |
| bare-cubic charge-neutrality inference | `NOT_CLEARED` |
| incoming degenerate sectors | `NOT_CONSTRUCTED` |
| continuum dressed projector | `NOT_CONSTRUCTED` |
| physical NLO quotient probability | `NOT_ESTABLISHED` |

The next calculation is now unambiguous:

> Derive the order-`lambda` distributional part of the BT asymptotic map on a
> regulated incoming-plus-outgoing carrier, including broken-vacuum charge
> bookkeeping, and test whether its Gram is exactly `1/48` per unordered pair.

## Claim boundary

This certificate is a reduced scalar preflight.  It does not establish a
dressed-state or KLN theorem, a full asymptotic map, a continuum domain, a
renormalized NLO quotient trace, beyond-tree positivity, a tensor or BRST
gravity lift, or anything `LORENTZIAN-CAUSAL`.  In particular, a finite
double-denominator power-counting limit is not an existence theorem for the
required distribution.

## Verification

```text
ulimit -v 500000; python3 reverse_physics/bt_asymptotic_generator_preflight.py --check
ulimit -v 500000; python3 reverse_physics/verify_bt_asymptotic_generator_preflight.py
ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_asymptotic_generator_preflight
```

The producer uses exact rational arithmetic over `Q(sqrt(3))`.  The verifier
does not import it: it independently reconstructs the Born/real ratio,
projector equations, Kallen and energy-deficit limits, charge boundary, pinned
hashes, and two decisive mutations.

Final scoped receipt, 2026-08-10:

| Tier | Command | Time | Peak RSS | Result |
|---|---|---:|---:|---|
| 0 | `py_compile` on producer, verifier, test | 0.04 s | 16,064 KB | PASS |
| 0 | `json.tool` on certificate, schema, event, work item | 0.14 s | 14,668 KB | PASS |
| 1 producer | producer `--check` | 0.04 s | 20,788 KB | PASS, 21/21 |
| 1 independent | verifier | 0.10 s | 30,012 KB | PASS, 12/12 |
| 1 focused | new unit tests | 0.46 s | 30,556 KB | PASS, 10/10 |
| 1 consumers | predecessor projector tests | 0.42 s | 30,408 KB | PASS, 9/9 |
| 1 consumers | axis-gluing tests | 22.50 s | 74,492 KB | PASS, 10/10 |
| 1 consumers | charge-stability tests | 0.28 s | 57,108 KB | PASS, 14/14 |
| papers | Paper 05 final pass | 0.40 s | 50,780 KB | PASS |
| papers | Paper 06 final pass | 0.43 s | 50,644 KB | PASS |

All commands ran sequentially with `ulimit -v 500000`.  PDF text extraction
confirms the corrected `1/48`, single-denominator obstruction, Jordan gate,
and non-transfer language.  Paper 06 has no overfull boxes; Paper 05 retains
only three small pre-existing boxes, at most 4.21 pt.  Tier 2 regeneration is
unnecessary because the two mathematical inputs are unchanged and
content-addressed; Tier 3 is not required because this is not a freeze,
release, theorem promotion, or shared-core change.  These skipped tiers are
not passes.

The immutable predecessor planning item was closed by an append-only
`OBSTRUCTED` event and a corrected Jordan successor was opened.  The `sfc`
writer was attempted under the same cap but the Go runtime could not reserve
its page-summary virtual address space before executing.  The cap was not
relaxed.  A manually emitted event of the documented `event-v0` byte shape is
explicitly labelled as that fallback; the failed coordinator launch is not a
pass.

## Parallel physical baseline (2026-08-10)

While the Jordan endpoint gate remains open,
[`REVERSE_PHYSICS_BT_UV_HARD_SCATTERING_LAW_V1`](../certificates/REVERSE_PHYSICS_BT_UV_HARD_SCATTERING_LAW_V1.json)
establishes the positive leading-log hard rate in every fixed nonforward
angular window.  The new result uses this preflight's corrected Born
normalization but neither constructs nor bypasses the missing `R_t` dressing.
It is the UV baseline against which an eventual inclusive completion must be
tested.
