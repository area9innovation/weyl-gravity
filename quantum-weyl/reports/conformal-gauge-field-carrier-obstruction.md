# First new conformal gauge-field carrier obstruction

## Result

The first genuinely new conformal gauge-field anomaly column remains absent,
not zero.

A finite twelve-gate completeness contract was fixed before comparing the two
smallest candidates beyond Maxwell and the strict Weyl graviton. Neither
candidate reaches a complete coefficient-bearing carrier:

| candidate | first failed gate | exact disposition |
| --- | --- | --- |
| complex minimal-depth conformal spin \(3/2\) | generic-background Noether identity | the Weyl-corrected action varies by an explicit Bach-tensor insertion and closes only on Bach-flat backgrounds |
| real minimal-depth bosonic conformal spin \(3\) | no omitted mixed-spin carrier | the pure sixth-order block fails beyond first curvature order; at minimum the all-curvature spin \(1\)-spin \(3\) carrier is missing, while a separate superconformal argument indicates an additional shifted spin \(2\) sector |

The complete maximal-depth spin-3 model with scalar gauge parameter is a
different theory and does not fill the minimal-depth slot.

## Fail-closed consequences

- no determinant ledger is assembled;
- no literature anomaly coefficient is copied;
- no raw \((c,-a,p,b_{\Box R})\) vector is emitted;
- no column is appended to the Paneitz-extended exact lattice;
- no finite-candidate obstruction is promoted to a no-go theorem for all
  conformal higher spins.

The strict receiver schema
`conformal-gauge-field-carrier-receiver-v1.schema.json` requires a complete
field/ghost/antifield and reducibility dictionary, minimal nilpotency,
off-shell Noether identity, nonminimal pairs, gauge fermion, generic
Riemannian ellipticity, domains, real/chiral structure, zero modes,
determinant powers, contours, two agreeing independent coefficient routes,
kinetic-sign audit and an explicit lattice append. It rejects the decisive
missing-ghost, wrong-chirality and omitted-nonminimal mutations.

## Evidence boundary

Dependency tags:

```text
LOCAL-ALGEBRAIC
```

The source audit uses the explicit Bach variation for the conformal
gravitino, the curvature-squared failure of the pure minimal-depth spin-3
operator, and the lower-spin closure requirements in the primary conformal
higher-spin literature. The preceding Paneitz certificate is imported from
commit `4b72eb33c7ade3d87f72707d56c86418c46e6765` with exact SHA-256
`cb6d708fb081d6a93fc64ab988f267cdd4a0c92651d872aaed5b59e3ecc3cb3c`.

This result is not a determinant or anomaly-coefficient computation, not QME
restoration, and not a Lorentzian, positivity, particle, scattering or
unitarity theorem.

## Verification

```bash
PYTHONPATH=quantum-weyl python3 -m anomalies.conformal_gauge_field_carrier_obstruction_certificate --check
PYTHONPATH=quantum-weyl python3 quantum-weyl/anomalies/verify_conformal_gauge_field_carrier_obstruction.py
PYTHONPATH=quantum-weyl python3 -m unittest anomalies.tests.test_conformal_gauge_field_carrier_obstruction
```

CLOSE-OUT: OBSTRUCTED — both smallest declared candidates fail the finite
complete-carrier contract before determinant or coefficient production.

EVIDENCE:
`quantum-weyl/anomalies/certificates/FIRST_NEW_CONFORMAL_GAUGE_FIELD_CARRIER_OBSTRUCTION.json`
