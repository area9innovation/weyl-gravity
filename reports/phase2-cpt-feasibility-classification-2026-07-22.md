# Phase-2 structured-CPT feasibility classification

Result: `FINITE_STRUCTURED_ETA_POSITIVE_C0_PARTIAL_GENUINE_C_AND_BRST_OPEN_OR_OBSTRUCTED_QUARTET_NO_GO`.

Independent exact replay separates six questions that must not be conflated:

| Question | Compact Weyl-Maxwell blocks | Cylinder | Counterflow quartet |
| --- | --- | --- | --- |
| Positive structured `eta` | Complete nonempty cone classified | `eta0=I` on the stationary reduced carrier | Impossible |
| Positive fundamental symmetry | Unique `C0=-I2 direct-sum I2 direct-sum I4` | Reduced `C0` exists | Gate not reached |
| Genuine Mannheim `C` | Not established: independent `P/T` absent | Not established | Spectrally excluded |
| Residual/BRST descent | Invariant-state/orbit quotient absent | Obstructed in the declared invariant commutant | Not applicable |
| Broken-PT no-go | Not applicable | Not applicable | Complex spectrum is unrescuable |
| Nontrivial ghost normalizer | Unclassified | Open outside the declared commutant | Cannot repair complex spectrum |

## Replayed evidence

For compact blocks the positive-frequency generator is the positive spectral
square root of `H^2`; the three positive squared frequencies are distinct for
`lambda>=6`.  Because the square root is injective, `Comm(H)=Comm(H^2)`.
The full orientation-preserving commutant, allowing axial/polar mixing, is

```text
M2(C) direct-sum M2(C) direct-sum M4(C), dimension 24.
```

Exact `q`-block matrices replay `C0^2=1` and `eta0=G C0>0`.  The imported
relative action operator is neither `H` nor `H^2`.  `C0` is a fundamental
symmetry, not a genuine Mannheim operator: no independent fixed-sector `P/T`
datum exists.

For the cylinder, direct energy-five reconstruction gives zero commutator rank
for `D` and all six compact generators, rank 32 for every one of eight proper
conformal generators, and stacked BRST defect rank 102 per chirality.  Thus
the reduced sign flip is positive but not a residual chain map.  The
all-energy invariant-commutant obstruction is retained; nontrivial ghost
normalizers outside it are not classified.

For the counterflow negative control, the exact factor

```text
40 z^4 + 773 z^2 + 3748
```

has `z^2` discriminant `-2151`.  The Schrödinger generator therefore has
nonreal spectrum.  A positive pseudo-Hermitian metric would make it similar
to a Hermitian operator, so none exists.  This is broken-PT exponential
growth, not a wrong-norm problem.

## Scoped Jordan analogy

The secular logarithms and characteristic-shell Jordan structure may be
compared algebraically with the equal-frequency Pais-Uhlenbeck Jordan limit.
This does not prove equivalence, zero-norm decoupling, or a `C` operator.

## Paper-15 disposition

No paper was edited.  The typed correction request asks Paper 15 to report
the compact positive result, the missing-`P/T` genuine-C boundary, the
cylinder chain obstruction and open ghost-normalizer route, the quartet
spectral no-go, and the strictly scoped Jordan analogy.  None supports a
full-BV state, anomaly cancellation, particles, scattering or unitarity.

## Verification

The producer and independent verifier separately reconstruct the compact
commutant, cylinder ranks and quartet discriminant.  Eight decisive mutations
prevent dimension-12 parity shrinkage, `H/H^2` confusion, eta-as-C promotion,
chain-map promotion, quartet rescue, ghost-route closure, analogy promotion
and unitarity promotion.

Tier 0 and scoped Tier 1 pass.  Tier 2 is unnecessary because all three joined
inputs are unchanged and content-addressed.  Tier 3 is not run because this is
a downstream classification, not a freeze or quantum lifecycle promotion.

CLOSE-OUT: DONE — the three exact inputs are independently joined into a six-row typed classification that separates positive eta, fundamental symmetry, genuine C, BRST descent, spectral no-go and the open ghost-normalizer route.
EVIDENCE: quantum-weyl/pt_cpt/synthesis/receipts/PHASE2_CPT_FEASIBILITY_CLASSIFICATION_V1_TIER_RECEIPT.json
