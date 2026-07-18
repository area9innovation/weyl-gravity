# Round-S4 conformal zero-mode volume locality

Dependency tags: `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`.

The ten Killing and five proper-conformal ghost zero modes reproduce
`dim so(5,1)=15`. The Euclidean conformal group `SO(5,1)` is noncompact, so
its naive Haar volume is divergent rather than a finite normalization factor.
A global partition function therefore needs an explicit collective-coordinate
or group-volume prescription and its Gram/Faddeev--Popov measure.

On a fixed stabilizer stratum, changing a constant group-volume normalization
does not alter the local operator symbol, local `b4` density, or support-local
Slavnov breaking. Stabilizer jumps and the global collective-coordinate
measure remain open. This result does not certify the combined repository
measure ledger or a QME.

## Verification

```bash
PYTHONPATH=quantum-weyl python3 -m spectral.euclidean.round_s4_conformal_volume_locality --check
PYTHONPATH=quantum-weyl python3 -m spectral.euclidean.verify_round_s4_conformal_volume_locality
PYTHONPATH=quantum-weyl python3 -m unittest spectral.euclidean.tests.test_round_s4_conformal_volume_locality
```
