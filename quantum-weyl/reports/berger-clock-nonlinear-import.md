# Berger-clock nonlinear import and total-D routing

Date: 2026-07-15

Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`

Lifecycle state: `CLASSICAL_CHARGE`

Setting verdict: `INPUT_GATE_BLOCKED`

## Result

The nonlinear-transfer programme now imports the certified positive Berger
clock background and its reduced O(2) charge seed without treating the clock
as a gauge direction.  The imported exact facts include the open interval

```text
(5-sqrt(21))/2 < q < 1/4,
```

positive standard-sign scalar kinetic energy, a bounded-below quartic,
dominant-energy stress, an everywhere-timelike phase, and

```text
Q_R = 16 pi^2 alpha_B q sqrt(1-4q) != 0.
```

The source certificates, classical status ledger, and programme status ledger
are all hashed.  Their setting, phase space, dependency tags, claim states,
and open-gate flags are rechecked before the quantum-side import certificate
can reproduce.

The fixed-coupling tangent audit is now certified.  The lapse constraint gives

```text
delta E_N = -(alpha_B q^(3/2)/2)(delta Q_R/Q_R),
```

and compact `SU(2)_L x U(1)_R` averaging excludes a smooth charged tangent in
every spatial mode.  Hence `Omega_total(delta,L_D)=0` on the declared smooth
fixed-coupling linearized phase space and the scoped verdict is `D_GAUGE`.
The next classical gate is `FULL_BERGER_CLOCK_BV_AND_STABILITY_AUDIT`.

## Physical-run routing

The ND2 manifest pins a fourth artifact, `D_disposition_certificate`, and
validates it against the strict total-`D` schema.  The setting, phase space,
generator, boundary-condition hash, classical commit, dependency-tag union,
and source hashes must all agree.  Execution accepts only the opaque token
returned by complete manifest verification.

| Certified disposition | Nonlinear route |
|---|---|
| `OPEN` | `BLOCKED_PENDING_TOTAL_D_DISPOSITION` |
| `D_GAUGE` | `CARTAN_CONTRACTION_EXECUTED` |
| `D_CHARGED` | `EQUIVARIANCE_ONLY_D_CHARGED_NO_QUOTIENT` |
| `SECTOR_DEPENDENT` | `SCOPED_DISPOSITION_REQUIRED` |
| `NOT_HAMILTONIAN` | `CARTAN_CONTRACTION_NOT_APPLICABLE` |

Only `D_GAUGE` invokes the contraction assembly adapter.  Every other route
returns a receipt with `cartan_execution: null`, so a charged or unresolved
clock cannot be silently removed from the physical complex.

## Claim boundary

This establishes a healthy exact background, nonzero reduced internal clock
momentum, and scoped fixed-coupling linearized `D_GAUGE`.  It does not
establish a support-local matter-coupled BV retract, a physical arity-two
Cartan correction, nonlinear stability, causal Green theory, quantum
admissibility, or any `LORENTZIAN-CAUSAL` or quantum-master-equation theorem.

## Machine receipts

- `quantum-weyl/transfer/certificates/BERGER_CLOCK_NONLINEAR_IMPORT.json`
- `quantum-weyl/transfer/certificates/BERGER_TOTAL_D_DISPOSITION.json`
- `quantum-weyl/transfer/certificates/ND2_PHYSICAL_RUN.json`
- `quantum-weyl/transfer/certificates/NONLINEAR_HOMOLOGICAL_TRANSFER_BOOTSTRAP.json`

## Verification receipt

| Command | Elapsed seconds | Status | Tier |
|---|---:|---|---:|
| Berger import certificate check | 0.03 | PASS | 1 |
| ND2 physical-run certificate regeneration | 0.38 | PASS | 1 |
| Nonlinear aggregate regeneration | 0.03 | PASS | 2 |
| Focused Berger, ND2 physical-run, and aggregate tests | 1.58 | PASS (14 tests) | 2 |
| Positive Berger background check and mutation guards | 1.45 | PASS (8/8 guards) | 1 |
| Berger reduced-charge check and mutation guards | 0.55 | PASS (11/11 guards) | 1 |
| Classical and programme status mutation guards | 0.26 | PASS (25/25 guards) | 2 |
| Affected nonlinear certificate chain | 5.80 | PASS | 2 |
| Complete transfer test suite | 66.03 | PASS (90 tests) | 2 |
| Python compile, JSON/YAML parsing, and scoped diff check | 0.10 | PASS | 0 |
| Scoped fixed-coupling producer and independent reconstruction | 1.62 | PASS | 2 |
| Updated classical and programme guards | 0.17 | PASS (27/27 guards) | 2 |
| Hardened total-`D` affected certificate chain | 5.24 | PASS | 2 |
| Hardened complete transfer suite | 66.69 | PASS (98 tests) | 2 |

The first complete-suite run failed because the classical team had changed
the content-addressed status ledger, making the dependent ND1 certificate
stale.  ND1 and its nonlinear aggregate consumer were regenerated; the failed
70.78-second run is not counted as a pass.  The final 90-test suite above
passed.

Draft-2020-12 instance validation was not run because `jsonschema` is not
installed; this is not counted as a pass.  Deterministic JSON and workflow
YAML parsing did pass.  Tier 3 is not required because the change imports
already-certified, content-addressed classical evidence, promotes no
lifecycle state, and makes no paper or Lorentzian theorem claim.
