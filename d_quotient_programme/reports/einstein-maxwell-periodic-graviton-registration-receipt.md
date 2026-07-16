# Periodic Einstein--Maxwell gravitational-mode registration receipt

Date: 2026-07-16

The programme imports commit
`04bc143ce297f49548dabac98af59e9f9c63f248` and certificate
`bridge/certificates/einstein_maxwell_periodic_graviton_second_order.json` with
SHA-256
`9376a4d4d2d1a0b9e77ee78ece90cd74e82b574b02a84030ed93e1f5946caef4`.

It registers a separate compact fixed-charge phase-space row for the plus
normal branch of one smooth odd-parity `l=2` gravitational harmonic with its
magnetic-flux-forced Maxwell dressing. The verdict is
`PERIODIC_L2_GRAVITATIONAL_MODE_FIXED_CHARGE_OBSTRUCTION`.

The imported theorem proves a nonzero constant-lapse pairing at `t=0` and
therefore a second-order obstruction for this declared branch. It does not
classify the minus branch or promote a universal helicity, causal, scattering,
or nonlinear-closure claim.

Verification:

```text
python3 d_quotient_programme/verify_programme_status.py --check --guards
```

The command passed in `0.22 s`, including exact regeneration, imported
evidence hashes, and mutation guards. This is the affected Tier-2 programme
chain. Tier 3 was not run because no full-stack freeze, release, or lifecycle
promotion is made.
