# Strict 386-row stabilized q2 lift preflight v1

## Outcome

A precise lift exists: extend the minimal q2 by zero over the 356 split contractible rows and transport it through the exact BV-canonical shear. Its graph-coordinate support envelope contains 140 ordered-component channels and 68 distinct block triples, with 110 possible input rows and 110 possible output rows; all generalized auxiliaries and Y-cone rows remain interaction-inert. The q1/q2 identity, Koszul symmetry, cyclicity and D/q2 derivation follow exactly for this candidate by direct-sum reasoning, stationary tensor naturality and canonical conjugation. This does not close Gate A: no authoritative classical export or certified cyclic L-infinity equivalence identifies the candidate with the intended full nonlinear nonminimal/auxiliary Weyl BV theory.

## The construction

In split coordinates, use

`q2_split(x,y)=i_end q2_min(pi_end x,pi_end y)`.

Thus the certified minimal six-species bracket acts on the 30 endpoint rows,
while every bracket involving a split contractible input is zero.  In graph
coordinates the exact action is retained as the compositional DAG

`q2_graph(x,y)=S q2_split(S^-1 x,S^-1 y)`.

This is not a mode truncation or an approximate tensor.  It is an exact cyclic
trivial stabilization followed by the already certified BV-canonical shear.

## Derived support envelope

- Minimal primary / ordered components: **12 / 22**.
- Expanded transported component channels: **140**.
- Distinct potentially nonzero block triples: **68** of **10648** ordered carrier triples.
- Input / output row envelopes: **110 / 110**.
- Rows interaction-inert in both slots and output: **196**.
- Entirely inert blocks: `AUX_ETA, AUX_ETA_STAR, AUX_F_HAT, AUX_F_HAT_STAR, AUX_V, AUX_V_STAR, CONE_Y_EQ, CONE_Y_EQ_SHARP, CONE_Y_ID, CONE_Y_ID_SHARP, CONE_Y_U, CONE_Y_U_SHARP`.

The block ledger is a support envelope.  It does not assert that every
component coefficient allowed by a listed triple is nonzero.

## Identities established for the candidate

- `q1/q2`: **VERIFIED_BY_DIRECT_SUM_AND_EXACT_CONJUGATION**, defects **0**.
- Koszul symmetry: **VERIFIED_BY_EXACT_CONJUGATION**, defects **0**.
- BV cyclicity: **VERIFIED_BY_ORTHOGONAL_DIRECT_SUM_AND_BV_CANONICAL_TRANSPORT**, defects **0**.
- `D/q2`: **VERIFIED_FOR_STABILIZED_CANDIDATE_BY_STATIONARY_NATURALITY_AND_CONJUGATION**, defects **0**.

The D statement is structural but exact: the cylinder flow is a derivation of
all twelve tensor-natural minimal operators and commutes with both rational
shear circuits on the stationary ultrastatic background.

## Why Gate A still fails closed

This receiver has constructed a valid cyclic stabilization.  It has not
imported an authoritative nonlinear extension from the classical programme.
In particular, it cannot decide whether the intended nonminimal or
generalized-auxiliary sector is interaction-free before the canonical shear.
Calling the candidate “the full classical q2” would violate the classical
import gate even though the algebra is internally consistent.

## Next gate

Obtain authoritative classical theory identity: either import a source-certified full 386-row q2 interaction ledger and compare it with this candidate, or import a source-certified cyclic L-infinity equivalence to the trivial stabilization. Only then may the receiver bind q2 and D/q2 into the Gate-A common snapshot and proceed to q2/Green compatibility.
