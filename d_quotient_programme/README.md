# Cross-programme \(D\)-quotient validation dossier

This directory consolidates the four investigations of whether cylinder time
translation/dilatation may be quotiented as gauge.  It is a validation dossier,
not yet Paper IX.

The dossier never assigns one universal Boolean to \(D\).  Every claim is
keyed by

```text
(generator, phase space, boundary conditions, lifecycle layer)
```

because the existing results concern different objects:

- the classical compact-cylinder charge and Taub-zero reduction;
- the real asymptotic generator dictionary and boundary-preservation gate;
- nonlinear homological transfer and interacting Cartan stability;
- the renormalized quantum Ward/QME obstruction.

## Authoritative artifacts

- [`certificates/D_QUOTIENT_PROGRAMME_STATUS.json`](certificates/D_QUOTIENT_PROGRAMME_STATUS.json)
- [`reports/consolidated-status.md`](reports/consolidated-status.md)
- [`registry/generators.json`](registry/generators.json)
- [`registry/phase_spaces.json`](registry/phase_spaces.json)
- [`schema/programme-status-v1.schema.json`](schema/programme-status-v1.schema.json)
- [`schema/team-contribution-v1.schema.json`](schema/team-contribution-v1.schema.json)
- [`contributions/`](contributions/)
- [`reports/classical-scalar-clock-registration-receipt.md`](reports/classical-scalar-clock-registration-receipt.md)
- [`reports/classical-neutral-clock-registration-receipt.md`](reports/classical-neutral-clock-registration-receipt.md)
- [`reports/einstein-ed1a-registration-receipt.md`](reports/einstein-ed1a-registration-receipt.md)
- [`reports/nonlinear-nd1-registration-receipt.md`](reports/nonlinear-nd1-registration-receipt.md)
- [`verify_programme_status.py`](verify_programme_status.py)

## Verification

From `physics/symplectic-reconstruction/`:

```bash
python3 d_quotient_programme/verify_programme_status.py --check --guards
```

The verifier checks the exact Git commit and SHA-256 digest of every imported
team certificate.  A team updates its own certificate first; the programme
certificate is regenerated only after the new claim has passed its team-level
verification.

## Publication policy

Papers VII--VIII retain their completed theorem, now with an explicit compact
phase-space split. The certified one-real-scalar no-go and the scoped neutral
two-field replacement supply the scalar-clock scope half of the Paper-IX gate;
Paper IX remains reserved until at least one complete boundary or interaction
theorem also lands.
A possible Paper X is reserved for interaction and quantum stability after the
applicable classical export and QME gates pass.

The immediate gate is `FULL_NEUTRAL_CLOCK_PAIR_BV_COMPLETION`: construct the
support-local inhomogeneous clock-pair complex and determine whether the
opposite-sign reference direction is entirely gauge or contractible.
Downstream teams must import both the single-scalar obstruction and the scoped
neutral replacement by content hash.
