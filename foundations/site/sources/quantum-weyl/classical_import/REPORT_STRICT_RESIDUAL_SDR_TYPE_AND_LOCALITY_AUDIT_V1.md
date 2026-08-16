# Strict residual-SDR type and locality audit

**Result:** `STRICT_RESIDUAL_SDR_TYPE_AND_LOCALITY_AUDIT_V1`
**Dependencies:** `LOCAL-ALGEBRAIC`, `REDUCED-MODE`, `LORENTZIAN-CAUSAL`
**Gate A:** `FAIL_CLOSED`

## Decision

The former `M3_RESIDUAL_SDR` request combined objects from different
categories.  It must not be satisfied by identifying equal-looking dimensions
or by relabeling a harmonic projection as support-local.

| Carrier | Coordinates | What they count | Locality |
|---|---:|---|---|
| `GRAPH_ENDPOINT_FIELDS` | 30 | `SECTION_SHEAF_COMPONENT_CARRIER` | `FINITE_ORDER_SUPPORT_LOCAL` |
| `DFINITE_WEYL_RESIDUAL` | 470 | `FINITE_HARMONIC_COEFFICIENT_CARRIER` | `REDUCED_MODE_NOT_ARBITRARY_SUPPORT` |
| `CONFORMAL_KILLING_COTANGENT` | 30 | `FINITE_LIE_COTANGENT_CARRIER` | `GLOBAL_ZERO_MODE_COEFFICIENTS` |
| `CENTERED_CE_COCHAINS` | 12,343 | `FINITE_CENTERED_CE_COCHAIN_CARRIER` | `LOCAL_ALGEBRAIC_AND_REDUCED_MODE_ONLY` |

The graph `30` counts local BV component species.  The M5 `30` counts fifteen
global conformal-Killing generators and fifteen dual coefficients.  Their
labels are disjoint.  The finite W+/W- residual carrier has 470 coordinates at
energies two through six.

## Locality obstruction

A nonzero constant or harmonic projector expands support.  The certificate
includes two exact rational three-site projectors: each sends a vector
supported only at site zero to a vector supported at all three sites.  The
continuum witness is the same: project a compactly supported cutoff times a
global mode back onto that mode.  Therefore the specified reduced-mode
projection cannot be a support-nonincreasing differential map in a Green
homotopy transfer.

This is a scoped obstruction to the direct promotion of the existing mode
receiver.  It does not rule out a new infinite-dimensional local curvature or
equation-level carrier.

## Repaired gate

- `M3L_COMMON_ENDPOINT_SDR_BINDING`: bind the already exact support-local
  386-to-30 graph SDR to the common strict manifest.
- `M3R_TYPED_RESIDUAL_COMPARISON`: construct the harmonic restriction and
  W+/W- residual comparison separately, label its nonlocal maps
  `REDUCED-MODE`, and state the analytic domains.

No common hash is accepted by this classification.  Hadamard, QME and quantum
residual-transfer stages remain open.

## Reproduction

```text
python3 quantum-weyl/classical_import/build_strict_residual_sdr_type_audit.py --check
python3 quantum-weyl/classical_import/check_strict_residual_sdr_type_audit.py
python3 -m unittest quantum-weyl/classical_import/tests/test_strict_residual_sdr_type_audit.py
```
