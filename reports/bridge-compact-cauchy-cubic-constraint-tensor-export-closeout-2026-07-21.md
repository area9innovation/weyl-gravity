# Cubic canonical constraint tensor export closeout

## Outcome

The requested action-normalized cubic export is obstructed before harmonic
projection by a missing representation and normalization bridge. The selected
covariant Weyl-Maxwell action, the canonical constraint ledger, the balanced
first-order fixture, and the complete covariant second-order correction are
all content-addressed. No input fixes the exact action-to-Ostrogradsky
canonical transformation in a declared boundary-term convention.

## First absent row

The first undefined row is `H_perp`. The imported ledger contains

```text
-(P_ij P^ij)/(2 sqrt(h))
```

but also states that its canonical variables use an unspecified nonzero
rescaling relative to `alpha_B=3`, and that the background momentum is merely
proportional to `diag(-2,1,1)` with its action normalization suppressed.

This ambiguity affects cubic coefficients exactly. On the one-slot jet

```text
h = 1+epsilon,
P = scale*(1+epsilon),
```

the epsilon-cubed coefficient of that constraint term is `scale^2/32`.
Choosing the equally nonzero normalized scales one and two gives `1/32` and
`1/8`. Both preserve the rank-only symbol result after normalized-coordinate
rescaling, but they do not give the same action-normalized cubic tensor.

## Missing representation crosswalk

The stored second-order solution is expressed in covariant reduced fields
`(A_t,B,C_t,U)` for `ell>=2` and `(C,K,U)` for `ell=0`. The canonical constraint
map requires `(h,K,pi,P,a,E)`. There is no certified channelwise map supplying
`delta pi`, `delta P`, the exact background `P`, or the boundary-term convention
that defines them. Consequently the following remain unavailable:

- `D3C_barPhi[u,u,u]`;
- every mixed `D2C_barPhi[u,v]` channel;
- the five stabilizer projections;
- the resonant `ell=2` q-minus and p-extra projections;
- the second action jet and arity-three Noether identity.

The verifier rejects mutations that set the suppressed scale to one, set the
missing canonical momenta to zero, replace canonical constraints by covariant
Euler rows, assert the cubic `H_perp` row, or infer arity-three Noether data
from the linear symbol. No absent coefficient is inserted as zero.

## Required next input

Derive from the selected `alpha_B=3` action and certify:

1. the higher-derivative boundary-term convention;
2. the exact Ostrogradsky canonical transformation and background momentum;
3. the channelwise map from every stored covariant correction to
   `(delta h,delta K,delta pi,delta P,delta a,delta E)`;
4. an independent reconstruction of the first `H_perp` jet.

Only then can the cubic tensor and arity-three identity be differentiated
without introducing a competing action.

EVIDENCE: `bridge/certificates/EINSTEIN_WEYL_COMPACT_CAUCHY_CUBIC_CONSTRAINT_TENSOR_EXPORT_OBSTRUCTION_V1.json`; `residual_atlas/einstein-weyl-compact-cauchy-cubic-constraint-tensor-export-obstruction-fragment-v1.json`; `bridge/einstein_sector/receipts/EINSTEIN_WEYL_COMPACT_CAUCHY_CUBIC_CONSTRAINT_TENSOR_EXPORT_OBSTRUCTION_V1_TIER_RECEIPT.json`
CLOSE-OUT: OBSTRUCTED — the first action-normalized H_perp cubic row is undefined until the alpha_B=3 Ostrogradsky normalization, boundary-term convention, background momentum and covariant-to-canonical correction crosswalk are certified.
