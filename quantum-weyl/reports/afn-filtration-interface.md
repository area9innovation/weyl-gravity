# Antifield-filtration interface receipt

Date: 2026-07-15

Dependency tag: `LOCAL-ALGEBRAIC`

Result state: `INTERFACE_READY_EXPORT_PENDING`

The local quotient API now accepts a complex decomposed by antifield number.
Blocks are keyed by their antifield-number shift:

```text
-1   delta
 0   gamma
>0   Q_gt0[k]
```

The AFN0 diagonal view is converted back to the existing exact bicomplex, so
the classical export can populate higher blocks without changing the
relative-cohomology API.  Shapes, forbidden shifts, and the AFN0 projection
fail closed.

The comparison ledger is frozen to:

```text
LIFTS_UNCHANGED
REQUIRES_ANTIFIELD_COMPLETION
BECOMES_EXACT
IS_OBSTRUCTED
```

This receipt certifies the interface and block ordering only.  No classical
Koszul--Tate row has been imported, and no minimal-BV quotient or AFN0 lift
comparison has been computed.

Machine receipt:
`quantum-weyl/local_bv/certificates/AFN_FILTRATION_INTERFACE_CERTIFICATE.json`.
