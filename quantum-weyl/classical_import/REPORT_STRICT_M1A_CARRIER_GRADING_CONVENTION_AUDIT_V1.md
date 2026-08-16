# M1A carrier-grading convention audit

**Result:** `STRICT_M1A_CARRIER_GRADING_CONVENTION_AUDIT_V1`

**Dependencies:** `LOCAL-ALGEBRAIC`, `REDUCED-MODE`, `LORENTZIAN-CAUSAL`

**Lifecycle:** `CLASSIFIED`; M1A remains `OPEN` and Gate A remains `FAIL_CLOSED`.

## Result

M1A cannot safely flatten the current grading labels.  The local BV source uses
standard BV ghost number, while the D-finite comparison uses a field named
`ghost_number` as its q-chain degree.  On the thirty common endpoint rows,
`chain_degree = -bv_ghost_number`; the two conventions have opposite sign on
20 rows.  Every D-finite q0 arrow raises its legacy value by
one, with 0 defects, confirming its chain
meaning.  Separately, conformal compact weight in the zero-mode and centered CE
payload is not the local q-chain degree.

The audit reconstructs all thirty endpoint rows from the authoritative action
dictionary and atom manifest.  Their BV ghost number, chain degree, antifield
number, form degree, parity, mass dimension, Weyl weight and intrinsic jet order
are now source-linked explicitly.  The remaining 356 local rows still need an
action/mapping-cone semantic extension; this audit does not guess those values.

## Carrier coverage

| Carrier | Rows | Fully namespaced | Partial | Remaining work |
|---|---:|---:|---:|---|
| `LOCAL_GRAPH_BV_386` | 386 | 30 | 356 | Declare action-derived auxiliary weights and the mapping-cone grading functor, including typed not-applicable values where no conformal or CE grading exists. |
| `REPRESENTED_ENDPOINT_DFINITE_4080` | 4,080 | 0 | 4,080 | Replace the misleading legacy ghost_number key by chain_degree and bind every represented endpoint species to one local typed species. |
| `DFINITE_COMPARISON_4490` | 4,490 | 0 | 4,490 | Separate the 4,080 represented endpoint coordinates from the 410-coordinate scalar test nonminimal doublet and give the latter an explicit source dictionary or exclude it from the authoritative source. |
| `FORMAL_COTANGENT_COMPARISON_8980` | 8,980 | 0 | 8,980 | Retain as a formal comparison carrier; do not use it as the authoritative full local BV source. |
| `ACTION_RESIDUAL_940` | 940 | 0 | 940 | Bind the 470 primal and 470 action-dual rows to namespaced chain/BV degrees without identifying the finite represented dual with the full continuous dual. |
| `ZERO_MODE_15_PLUS_15` | 30 | 30 | 0 | None for its declared zero-mode namespace; local BV and CE gradings must be explicit not-applicable values rather than zeros. |
| `CENTERED_C3_C4_C5` | 12,343 | 12,343 | 0 | None for its declared CE namespace; it is a cochain carrier and not a local field/antifield dictionary. |

The 4,490-coordinate D-finite comparison contains
4,080 minimal coordinates
with an exact sign bridge and
410
scalar test-nonminimal coordinates without a local source dictionary.  The
formal 8,980-coordinate cotangent source remains a comparison object, not the
authoritative original BV source.

## Required schema repair

M1A must use distinct tagged fields: `bv_ghost_number`, `chain_degree`,
`antifield_number`, `form_degree`, `Grassmann_parity`, `mass_dimension`,
`Weyl_weight`, `conformal_compact_weight`, `ce_ghost_number`, and
`intrinsic_jet_order_bound`.  Per-arrow `operator_order_bounds` is a separate
object.  A grading that does not apply must be marked `NOT_APPLICABLE` with a
reason, never silently zeroed.

## Boundary

This is a convention and source-authority audit.  It completes none of M1A,
M1B or M1C, replays no final Gate-A check, and establishes no Hadamard,
renormalized-product, QME or residual-transfer result.

## Next construction

Adopt M1A1, then derive M1A2 from the action and mapping-cone functor and M1A3 from the represented endpoint/action-dual crosswalk; only their union may be frozen as M1A4.
