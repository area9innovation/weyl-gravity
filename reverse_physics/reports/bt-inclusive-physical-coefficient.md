# BT \(R_t\) pushforward coefficient

**Correction:** the physical object identification in this predecessor is
superseded by `REVERSE_PHYSICS_BT_INCLUSIVE_NLO_OBJECT_LEDGER_V1`.  The exact
block lemma and the zero \(R_t P R_t^\dagger\) trace below remain valid.  The
kernel used here is not \(P_{\rm out}(S-1)P_{\rm in}\), so it does not erase
the independently certified \(+1/512\) real response per pair.

**Result:** `COEFFICIENT_COMPUTED`

**Dependencies:** `LOCAL-ALGEBRAIC`, `REDUCED-MODE`

For an orthogonal incoming/outgoing detector pair,

\[
 A(\lambda)=P_{\rm out}(1+\lambda K+\lambda^2L+\cdots)P_{\rm in}
\]

has no order-zero term.  Consequently

\[
 [A^\dagger A]_{\lambda^2}
 =(P_{\rm out}KP_{\rm in})^\dagger(P_{\rm out}KP_{\rm in}),
\]

independently of every unknown higher composite amplitude.  Four exact block
fixtures verify the identity with unrelated rational second-order maps.

The complete signed public BT kernel has zero parent-raised trace pointwise in
all sign sectors.  The covariant squeeze preserves it by similarity and the
neutral orbit factor cancels from normalized conditional weights.  Summing
the complete species kernel at every finite regulator therefore gives zero
before the endpoint is removed.  Sixty-four exact detector-cell masks all give
zero, and the simple-function limit gives zero for arbitrary declared
measurable detector support.

Hence, for the declared public \(R_t\) pushforward,

\[
 \boxed{\Delta_{R_t P R_t^\dagger}=0}.
\]

The public map does not reproduce \(1/48\) because it is a different object.
The physical five-point response remains \(+1/512\) per pair and \(+3/512\)
over three pairs, equivalently \(1/48\) and \(1/16\) after Born
normalization.  The physical virtual response does not cancel it; the
\(R_t\) zero is a distinct Eq. (19) result, not a physical summand.  The
complete NLO probability and all-order Eq. (19) are not established.

Verification uses exact rational producer and independent block/kernel rails,
plus seven tests with five decisive mutations.  All commands ran sequentially
under `ulimit -v 500000`.  Tier 0 passed in 0.17 s (15,600 KB peak RSS).
Certificate generation and the 20/20 producer each took 0.05 s (20,716 KB),
the independent verifier passed 7/7 in 0.13 s (30,140 KB), and the mutation
suite passed 7/7 in 0.83 s (30,472 KB).  Papers V and VI compiled twice; final
passes took 0.87 s and 0.98 s with at most 51,020 KB peak RSS.  Tier 3 was not
run because this promotes one physical coefficient, not the complete NLO
probability, all-order Eq. (19), a freeze, or a release.  The append-only event
uses the documented manual fallback; no coordinator pass is claimed.
