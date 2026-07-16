# Periodic Einstein--Maxwell photon registration receipt

Date: 2026-07-16

The programme imports commit
`bf6efe476336c23520dd70f0ffccbae4dfae975d` and certificate
`bridge/certificates/einstein_maxwell_periodic_photon_second_order.json` with
SHA-256
`3f3ac8f10c9fadc36180f98c48404e4e733fc420f97bb529c5b1316f550def93`.

It registers a separate compact fixed-charge phase-space row for the smooth
`l=1`, `omega=2` photon--metric tangent. The verdict is
`PERIODIC_PHOTON_SECOND_ORDER_FIXED_CHARGE_OBSTRUCTION`. It is not merged with
the zero-mode fixed-flux fixtures or the universal-cover null extension.

The imported theorem proves a nonzero constant-lapse pairing of `-16/3` and
therefore a second-order obstruction for this one mode. It does not promote a
general photon, helicity-two, causal, scattering, or nonlinear-closure claim.

Verification:

```text
python3 d_quotient_programme/verify_programme_status.py --check --guards
```

The command passed in `0.28 s`, including exact regeneration, evidence-hash
checks, and mutation guards. Tier 2 is satisfied by this affected programme
certificate chain. Tier 3 was not run because the registration does not freeze
or release the full classical/quantum stack and promotes no lifecycle state.
