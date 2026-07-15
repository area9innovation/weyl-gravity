# Local Schouten-zero Weyl-image receipt

Date: 2026-07-15

Dependency tag: `LOCAL-ALGEBRAIC`

Result state: `SCHOUTEN_ZERO_IMAGE_VERIFIED`

Classical snapshot: `UNFROZEN`

## Outcome

The certified eight-dimensional four-dimensional integrated order-six
Riemann quotient now has an exact derivative-safe Weyl restriction.  Every
Riemann factor is first interpreted through

```text
Riemann = Weyl + metric wedge Schouten
```

with derivative labels placed on Weyl or Schouten and never on the metric.
The projection then sets Schouten and every covariant derivative of Schouten
to zero.  A factorized evaluator keeps only the unique all-Weyl branch; direct
single-factor algebraic and differentiated witnesses verify that it equals
the full five-term expansion followed by projection.

## Exact image

The 39-column source presentation has an eight-dimensional quotient after
the universal and four-dimensional relations.  Its Schouten-zero images
produce 17 nonzero target monomials.  The mapped relation ledger is

```text
family                         mapped rows  cumulative rank  quotient dim
R3 Bianchi                               6                3            14
(nabla R)^2 Bianchi                     14                8             9
R nabla^2 R Bianchi                     14               13             4
integration by parts                    12               14             3
covariant commutators                    4               15             2
four-dimensional Schouten              56               16             1
```

There are 106 unique nonzero mapped relations in total.  The induced map on
the stored source quotient basis is

```text
[0, 0, 1/3, 1/6, 0, 0, 0, 1],
```

so it has rank one and a seven-dimensional exact kernel.  All seven kernel
vectors and their ambient tensor expressions are stored in the certificate.

Each source sector reaches the same surviving target class:

```text
Riemann^3                  rank 1
(nabla Riemann)^2          rank 1
Riemann nabla^2 Riemann    rank 1
```

This is the expected structural role of the mapped integration-by-parts and
commutator rows: derivative and cubic representatives become coordinates of
one restricted class rather than independent directions.

## Odd companion

The unique target representative is dualized on one Weyl factor with the
explicit epsilon-over-two primitive.  The resulting expression is nonzero
and parity odd.  It is stored as
`CONSTRUCTED_NOT_A_COMPLETE_BASIS`: this proves an explicit odd companion,
not exhaustion of all single-epsilon contractions or their relations.

## Claim boundary

This theorem sets the full Schouten jet to zero.  Through the differential
Bianchi identity that also imposes `Cotton = 0`.  It is therefore a
Schouten-flat leading-Weyl restriction, not the unrestricted local Weyl-jet
algebra needed for the complete counterterm and anomaly calculation.

Still `NOT_COMPUTED` are:

- the unrestricted Weyl--Cotton jet quotient;
- exhaustive parity-odd single-epsilon enumeration;
- Weyl-BRST closure and exactness;
- antifield/Koszul--Tate completion and descent;
- anomaly coefficients, QME restoration, or residual transfer.

Gate A remains fail-closed pending the portable classical contraction export.

## Verification receipt

| Tier | Command/rail | Elapsed | Result |
|---|---|---:|---|
| 0 | compile local package, parse all quantum JSON, validate common result schemas, scoped diff check | 1.45 s | pass |
| 1 | complete local-BV unit rail, quiet mode | 22.56 s wall | 112 pass in 22.11 s |
| 2 | nine local certificate reproduction checks, parallel | 18.76 s wall | pass |
| 2 | new certificate under hash seeds `1,7,123`, parallel | 14.58 s wall | pass |
| 2 | two-pass `conformal-residual-cohomology.tex` build | 1.23 s | pass; no unresolved references on final pass |

The complete local rail remains below the agreed 60-second escalation
threshold.  Independent certificate checks and hash-seed checks run in
parallel without sharing output files.  Tier 3 was not triggered: this is a
local restriction theorem, not the classical freeze, a BRST-cohomology or
QME theorem, a lifecycle promotion, or a release.  The full repository suite
was not run and is not represented as passing.

Commands:

```bash
PYTHONPATH=quantum-weyl python3 -m unittest discover \
  -s quantum-weyl/local_bv/tests -q
PYTHONPATH=quantum-weyl python3 \
  -m local_bv.weyl_image_certificate --check
python3 quantum-weyl/schema/validate_result.py \
  quantum-weyl/certificates/LOCAL_SCHOUTEN_ZERO_WEYL_IMAGE.json
```

## Machine receipts

- `quantum-weyl/local_bv/certificates/LOCAL_SCHOUTEN_ZERO_WEYL_IMAGE_CERTIFICATE.json`;
- `quantum-weyl/certificates/LOCAL_SCHOUTEN_ZERO_WEYL_IMAGE.json`.

## Next local gate

Retain Schouten/Cotton rather than setting them to zero, construct the
unrestricted Weyl--Cotton jet quotient, and build a compressed dual-Weyl
carrier for exhaustive odd enumeration without expanding millions of raw
epsilon pairings.
