# Axial partial-jet endpoint frames v1

This endpoint-only certificate imports the exact six-state factor gauge and
the existing horizon, incoming-infinity, and outgoing-infinity recurrences.
It certifies exact factor lines, scalar rescalings, the common permutation,
frozen spin-one normalization, and the dual-number inverse/frame laws.

It fails closed on the remaining step: the imported artifacts do not provide
the differentiated endpoint recurrence and analytic normalizer lifts needed
to compute \(K_H,K_-,K_+\).  Consequently it does not construct endpoint
partial-jet frames and makes no \(T_+\) or scattering claim.

Run:

```bash
python3 -m black_hole_programme.phase3.axial_partial_jet_endpoint_frames_v1.produce
python3 -m black_hole_programme.phase3.axial_partial_jet_endpoint_frames_v1.produce --check
python3 -m black_hole_programme.phase3.axial_partial_jet_endpoint_frames_v1.verify
python3 -m unittest black_hole_programme.phase3.axial_partial_jet_endpoint_frames_v1.test_endpoint_frames
```
