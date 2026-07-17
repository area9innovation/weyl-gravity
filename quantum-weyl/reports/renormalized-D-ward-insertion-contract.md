# Renormalized D-Ward insertion contract

Dependency tag: `LOCAL-ALGEBRAIC`.

The existing exact Cartan engine already computes

\[
\mathcal A_D^{(1)}=[Q_0,\iota_{D,1}]+[Q_1,\iota_{D,0}]-\mathcal L_{D,1}
\]

and verifies the sourced consistency identity.  The new portable contract
specifies the missing physical data: the observable complex and admissibility
policy; all six order-zero/one Ward operators; regulator, scheme, boundary,
and zero-mode provenance; the regulated Slavnov breaking; and proof artifacts
for every consistency equation.

Two lifecycle branches are accepted.  A nonzero QME source remains
`REGULATED_BREAKING_COMPUTED_QME_OPEN`, forces the Cartan status to
`UNDEFINED_ANALYTICALLY`, and forbids a local-to-Cartan map.  Only the
`QME_RESTORED_CARTAN_CLASSIFIED` branch may emit `ZERO`, `EXACT_REMOVABLE`, or
`NONTRIVIAL_ANOMALY`, with the appropriate primitive or normalized dual
witness.

The checked-in receipt is `INTERFACE_READY_PHYSICAL_INPUT_BLOCKED`.  Its exact
finite fixtures do not supply a physical `Q1`, restored QME, coefficient, or
quantum D verdict.

The upstream density quotient is now complete and the separate regulated
Slavnov-breaking receiver can accept a content-addressed analytic result.
The imported classical 26/54-row causal Green homotopy does not fill this
Ward contract: a BRST-compatible global Hadamard state, renormalized product,
regulated breaking, restored `Q1`, and the order-one D operators are still
required.
