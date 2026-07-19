# Compact-product Einstein--Weyl chain map: executable PBW handoff

## Result

`EINSTEIN_WEYL_COMPACT_PRODUCT_CHAIN_MAP_PBW_V1` exports the previously
certified support-local compact-product Einstein--Maxwell to Weyl--Maxwell
linear inclusion as an exact coordinate-PBW operator.  It maps the complete
38-row minimal source layout into the expected 40-row minimal target layout
using stable row identifiers rather than relying on coincident numeric row
positions.

The map has 100 nonzero source/target row pairs and 221 PBW terms.  Its
maximum differential order is two, its coefficient jets are exported through
order four at the declared product base point, and it contains no inverse
Laplacian, inverse curl, frequency division or momentum division.  The extra
Weyl ghost and Weyl identity rows have zero image.

## Verification

The producer deterministically regenerates the payload from the committed
Einstein and Weyl row layouts and the certified invariant chain-map formula.
The legacy covariant equation convention and the action-derived BV cotangent
rows differ by a sign on the Maxwell Euler input; the serializer applies that
typed adapter to the four derivative-Maxwell coefficients and the associated
identity term.  A separate
consumer validates the strict Draft 2020-12 schema, every dependency hash,
row/dual typing, stable identifiers, degree preservation, PBW ordering,
coefficient-jet ordering, operator-order bounds, the common identity blocks
and the two zero Weyl images. It then composes the frozen 40-row target q1 with
the inclusion and compares it coefficientwise with the inclusion composed
with the frozen 38-row source q1. All 40 defect rows vanish. Mutation testing
rejects both a forged row identifier and a reversed Maxwell cotangent sign.
The original invariant chain-map verifier is rerun as a source theorem
regression.

## Claim boundary

The authoritative status is `EXACT_PBW_CHAIN_MAP_TARGET_Q1_REPLAYED`.  This is
an exact executable linear chain map on the frozen source and target carriers.
It does not claim cyclicity, a nonlinear relative morphism, causal Green data,
Berger branch transport or a quantum result.
