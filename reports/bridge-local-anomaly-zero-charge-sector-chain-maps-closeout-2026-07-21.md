# Bridge closeout: strict anomaly restriction chain maps

The receiver requested full strict pure-Weyl local-BV restriction maps to the
conformal-cylinder Taub-zero derived sector and the fixed-coupling positive
Berger fluctuation complex.  Exact input pinning and a method-distinct audit
show that the two targets fail for different reasons.

## Berger: hard full-BV obstruction

At the certified rational fixture \(q=9/40\), \(\alpha_B=5\), the pure-Weyl
metric-antifield constant is

```text
B_00 = 961/9600
alpha_B B_00 = 961/1920
```

The matter-coupled Berger target is on shell, so its corresponding constant is
zero.  The full-BV identity-jet chain equation therefore has exact defect
`961/1920`.  No receiver-valid full-BV map exists in the declared class.
AFN0 background evaluation is not substituted for that map.

## Cylinder: missing derived carrier, not a universal no-go

The all-fifteen-component Taub-zero sector begins quadratically and leaves the
unary tangent complex unchanged.  A faithful target must adjoin fifteen
Koszul/BFV generators with `d eta_A=mu_A` and provide the bulk-to-time-slice
transgression.  The pinned cylinder minimal-BV theorem explicitly records
that transgression as unproved.  Thus the current receiver is not typeable
from the pinned inputs.  Its status is `NO_CERTIFIED_MAP`; no claim is made
that an enlarged derived BV-BFV construction cannot exist.

## Evidence and verification

- certificate:
  `bridge/certificates/STRICT_ANOMALY_SECTOR_RESTRICTION_CHAIN_MAP_OBSTRUCTION_V1.json`;
- exact producer and independent verifier:
  `bridge/anomaly_restriction/`;
- human-readable report:
  `bridge/anomaly_restriction/reports/strict-anomaly-sector-restriction-chain-map-obstruction-v1.md`;
- receipt:
  `bridge/anomaly_restriction/receipts/STRICT_ANOMALY_SECTOR_RESTRICTION_CHAIN_MAP_OBSTRUCTION_V1_TIER_RECEIPT.json`;
- fail-closed atlas:
  `residual_atlas/strict-anomaly-sector-restriction-obstruction-fragment-v1.json`.

Producer, independent witness reconstruction, strict schema validation, four
scientific/mutation tests, three atlas tests and the common atlas validator
pass.  The first independent run failed an overly literal wording assertion
and is recorded as `NOT_A_PASS`; the repaired verifier checks the exact
quadratic formula.  Tier 2 was not required because no shared input changed.
Tier 3 was not run because this is a scoped `CLASSIFIED` obstruction, not a
freeze or release.

All six class images and both Cartan defects remain undefined.  No anomaly
freedom, compensator, QME, causal, state, particle, positivity or unitarity
claim is promoted.

CLOSE-OUT: OBSTRUCTED — Berger has the exact full-BV antifield chain defect 961/1920, while the cylinder requires a not-yet-constructed derived BFV/Koszul time-slice carrier; the old receiver cannot be populated honestly.
