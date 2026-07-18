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
Einstein row layout and the certified invariant chain-map formula.  A separate
consumer validates the strict Draft 2020-12 schema, every dependency hash,
row/dual typing, stable identifiers, degree preservation, PBW ordering,
coefficient-jet ordering, operator-order bounds, the common identity blocks
and the two zero Weyl images.  Mutation testing rejects a forged row
identifier.  The original invariant chain-map verifier is rerun as a source
theorem regression.

## Claim boundary

The authoritative status is
`EXACT_PBW_REPRESENTATIVE_TARGET_Q1_REPLAY_PENDING`.  The payload is an exact
executable representative of the already certified linear map, but it does
not yet replay the serialized target-side chain equation because the frozen
40-row Weyl--Maxwell `q1` payload does not yet exist.  It therefore does not
claim cyclicity, a nonlinear relative morphism, causal Green data, Berger
branch transport or a quantum result.  Promotion to a complete serialized
chain morphism requires coefficientwise target-`q1` composition after that
payload lands.
