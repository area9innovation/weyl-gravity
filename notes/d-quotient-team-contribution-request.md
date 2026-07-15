# Contribution request for the cross-programme \(D\)-quotient dossier

The following message is intended to be sent unchanged to the classical,
Einstein/boundary, nonlinear, and quantum teams.

---
We now have a shared cross-programme \(D\)-quotient dossier at
`d_quotient_programme/`.  Please contribute to that dossier through your own
team certificate; do not edit the consolidated verdict by hand.

The central rule is that every claim is keyed by

```text
(generator_id, phase_space_id, boundary_conditions, lifecycle_layer)
```

There is no team vote and no universal `D_GAUGE` Boolean.  Results for
different generators, phase spaces, boundary conditions, or lifecycle layers
are different rows, not contradictions.

Before starting new work:

1. Read `d_quotient_programme/registry/generators.json` and
   `d_quotient_programme/registry/phase_spaces.json`.
2. Reuse an existing identifier when it is exact.  If it is not exact, propose
   a new identifier rather than overloading an old one.
3. Preserve the current classical split:
   - `compact_P_lin`: `D_CHARGED`;
   - `compact_P_Taub0` and `compact_P_der`: `D_GAUGE` only after the explicit
     full moment-map zero restriction.
4. Do not identify `H_ESU`, `D_M`, `D_rad`, and `P_0` without an explicit
   phase-space-preserving intertwiner.
5. Do not promote a result beyond its dependency tag.  In particular,
   `REDUCED-MODE` and `LOCAL-ALGEBRAIC` do not prove a new
   `LORENTZIAN-CAUSAL` or quantum statement.

For each new result, send one machine-readable contribution conforming to
`d_quotient_programme/schema/team-contribution-v1.schema.json` with:

- `team_id`, `setting_id`, `generator_id`, and `phase_space_id`;
- exact boundary/corner conditions and lifecycle layer;
- `claim_status` and one scoped verdict, or `null` while open;
- what is established and explicitly not established;
- the certificate path, full Git commit, and SHA-256 hash;
- exact verification commands and the next blocking gate.

Team-specific priorities:

- **Classical:** retain the neutral pair as a scoped homogeneous reference
  theorem, retain the complete standard positive-sign one-field stealth family
  as a scoped no-go, and own the next positive-energy non-conformally-flat
  clock model, its total improved symplectic form, and total \(D\) charge.
- **Einstein/boundary:** import the single-scalar obstruction and use only a
  certified replacement clock where relevant; otherwise
  complete one real boundary-preserving full-Bach phase space and compute the
  selected generator's charge and flux.
- **Nonlinear:** import the classical obstruction and any replacement tensors
  by hash, complete the
  support-local \(q_2\) export, and compute the first interacting
  \(D\)-Cartan defect or correction.
- **Quantum:** import the same classical obstruction/replacement setting by
  hash, construct the
  renormalized observable algebra, and classify the first Ward/QME obstruction
  without promoting the classical verdict.

`SCALAR_CLOCK_VERTICAL_SLICE` is certified as obstructed for one real
conformal scalar on the exact vacuum cylinder. Its replacement
`NEUTRAL_CONFORMAL_CLOCK_PAIR` is certified on the exact homogeneous sector
with internal signature `(+,-)` and scoped verdict `D_GAUGE`. The shared gate
was tested by `NEUTRAL_CLOCK_BV_HEALTH_AUDIT` and is obstructed as a globally
regular positive local clock: the ratio kinetic sign changes on every winding
orbit. Do not broaden the replacement beyond its homogeneous claim. The next
gate is now `POSITIVE_ENERGY_NONCONFORMALLY_FLAT_BACH_SOURCED_CLOCK`; other
teams consume the full standard stealth no-go by hash rather than independently
repeating the scalar classification. Generalized scalar actions count as new
theories with separate health and BV gates.

Paper IX remains reserved until the scalar-clock theorem and at least one
boundary or interaction theorem are certified.  Paper X remains reserved for
interaction/quantum stability after the classical export and QME gates.

After committing your team certificate, report its path, commit, hash, scoped
verdict, dependency tags, and exact next gate.  The central dossier will then
be regenerated and its mutation guards rerun.

---
