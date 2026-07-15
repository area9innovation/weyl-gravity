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
- [`reports/classical-neutral-clock-health-registration-receipt.md`](reports/classical-neutral-clock-health-registration-receipt.md)
- [`reports/classical-homogeneous-stealth-registration-receipt.md`](reports/classical-homogeneous-stealth-registration-receipt.md)
- [`reports/classical-standard-stealth-no-go-registration-receipt.md`](reports/classical-standard-stealth-no-go-registration-receipt.md)
- [`contributions/classical-positive-berger-clock-background.json`](contributions/classical-positive-berger-clock-background.json)
- [`contributions/classical-berger-clock-charge-seed.json`](contributions/classical-berger-clock-charge-seed.json)
- [`contributions/classical-berger-fixed-coupling-delta-charge.json`](contributions/classical-berger-fixed-coupling-delta-charge.json)
- [`contributions/classical-berger-minimal-bv-clock-sdr.json`](contributions/classical-berger-minimal-bv-clock-sdr.json)
- [`reports/classical-positive-berger-clock-registration-receipt.md`](reports/classical-positive-berger-clock-registration-receipt.md)
- [`reports/classical-berger-clock-charge-seed-registration-receipt.md`](reports/classical-berger-clock-charge-seed-registration-receipt.md)
- [`reports/classical-berger-fixed-coupling-registration-receipt.md`](reports/classical-berger-fixed-coupling-registration-receipt.md)
- [`reports/classical-berger-minimal-bv-sdr-registration-receipt.md`](reports/classical-berger-minimal-bv-sdr-registration-receipt.md)
- [`reports/einstein-ed1a-registration-receipt.md`](reports/einstein-ed1a-registration-receipt.md)
- [`reports/nonlinear-nd1-registration-receipt.md`](reports/nonlinear-nd1-registration-receipt.md)
- [`reports/quantum-cartan-registration-receipt.md`](reports/quantum-cartan-registration-receipt.md)
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

The neutral pair remains a valid homogeneous reference clock, but its local
positive-health promotion is obstructed. The complete standard one-field
stealth family is exhausted as well. The replacement is now concrete: an exact
Berger-cylinder family carries two standard-sign rotating conformal scalars
with positive quartic potential, dominant-energy stress, timelike phase, and
full raw clock incidence. This is a healthy background theorem, not yet a
complete all-row clock theorem. Downstream teams must import all scoped clock
results by content hash.
The first sub-gate is now exact: the phase carries nonzero conserved global
\(O(2)\) momentum and the full helical contraction satisfies
\(\Omega_{\rm total}(\delta,\mathcal L_D)=\omega\delta Q_R\). The fixed-coupling
audit closes the tangent question exactly:

\[
\delta E_N=-\frac{\alpha_Bq^{3/2}}2\frac{\delta Q_R}{Q_R}.
\]

Compact spatial averaging excludes an inhomogeneous escape, so `D_GAUGE`
holds on the declared smooth fixed-coupling linearized Berger phase space.
The temporal/Weyl clock doublets and all minimal dual rows now also admit an
exact first-order support-local cyclic SDR, contracting 8 of the 34 minimal
rows. The immediate gate is now
`BERGER_RETAINED_Q1_AND_NONMINIMAL_COMPLETION`; causal Green homotopies and
stability follow after it. This does not replace the nonlinear team's separate
`CLASSICAL_SUPPORT_LOCAL_Q1_Q2_EXPORT` gate.
