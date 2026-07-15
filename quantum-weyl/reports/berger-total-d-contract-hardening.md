# Berger total-D contract hardening

Date: 2026-07-15

Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`

Lifecycle layer: `CLASSICAL_CHARGE`

## Result

The nonlinear programme now has a strict machine contract for a setting-
scoped total-`D` presymplectic disposition.  It imports the classical Berger
fixed-coupling theorem as `D_GAUGE` on
`positive_berger_fixed_coupling_linearized_solutions`.

The distinction between background charge and charge variation is explicit.
The clock has nonzero background momentum `Q_R`, while the exact lapse row and
compact averaging prove

```text
delta Q_R = 0,
Omega_total(delta,L_D) = 0
```

for every tangent in the declared phase space.  The certificate therefore
records `total_D_charge_variation: ZERO`; it does not falsely assert that the
background matter charge itself vanishes.

## Canonical dispositions

The authoritative classical vocabulary is retained exactly:

| Verdict | Required audit signature | Nonlinear route |
|---|---|---|
| `D_GAUGE` | integrable, `D_IN_KERNEL`, zero charge variation | Cartan route eligible |
| `D_CHARGED` | integrable, `D_NOT_IN_KERNEL`, nonzero charge variation | equivariance only; no quotient |
| `SECTOR_DEPENDENT` | sector-dependent charge and kernel, nonempty sector ledger | scoped certificate required |
| `NOT_HAMILTONIAN` | nonintegrable, kernel and charge undefined | Cartan contraction not applicable |

`D_CHARGED_NO_QUOTIENT` is not a scientific verdict.  The phrase survives
only inside the route label `EQUIVARIANCE_ONLY_D_CHARGED_NO_QUOTIENT`.

## Verification boundary

A terminal certificate must contain:

- the combined gravitational-plus-matter presymplectic contraction;
- fixed normalization and integrability status;
- the allowed fixed-coupling `delta Q` tangent result;
- the presymplectic kernel and total-charge-variation classification;
- exact checks, source hashes, source commit, and test receipts;
- a sector ledger when and only when the verdict is `SECTOR_DEPENDENT`.

The theorem, classical-ledger registration, and programme-ledger registration
are now read from their immutable Git commits.  Each source-artifact row carries
its own `git_commit` and SHA-256 digest; later unrelated additions to the
aggregate ledgers neither invalidate the theorem nor get silently absorbed.
The physical verifier reconstructs those historical blobs before accepting a
run.

The ND2 manifest additionally binds the certificate to its setting, phase
space, boundary-condition hash, classical commit, dependency-tag union, and
all provenance files.  Directly constructed manifests cannot execute the
Cartan engine: only a `VerifiedPhysicalRun` returned after complete validation
is accepted.

## Remaining gate

The scoped `D_GAUGE` result authorizes the quotient classification, not the
physical nonlinear calculation.  ND2 still requires independently pinned
support-local `q1/q2/D`, all-row contraction, and admissibility artifacts plus
their exact evaluator and assembly adapter.  Those belong to
`FULL_BERGER_CLOCK_BV_AND_STABILITY_AUDIT` and the parked
`CLASSICAL_SUPPORT_LOCAL_Q1_Q2_EXPORT`.

## Machine receipts

- `quantum-weyl/transfer/certificates/BERGER_TOTAL_D_DISPOSITION.json`
- `quantum-weyl/transfer/certificates/BERGER_CLOCK_NONLINEAR_IMPORT.json`
- `quantum-weyl/transfer/certificates/ND2_PHYSICAL_RUN.json`
- `quantum-weyl/transfer/schema/total-d-disposition-v1.schema.json`

## Verification receipt

| Command | Elapsed seconds | Status | Tier |
|---|---:|---|---:|
| Classical fixed-coupling producer with guards | 0.85 | PASS | 1 |
| Independent non-holonomic frame reconstruction | 0.77 | PASS | 2 |
| Classical fixed-coupling unit tests | 0.85 | PASS (4 tests) | 1 |
| Classical and programme status guards | 0.17 | PASS (27/27 guards) | 2 |
| Total-`D`, Berger, ND2, and aggregate focused tests | 5.10 | PASS (22 tests) | 2 |
| Affected nonlinear certificate chain | 5.24 | PASS | 2 |
| Complete transfer test suite | 66.69 | PASS (98 tests) | 2 |
| Python compile, JSON/YAML parsing, and scoped diff check | 0.09 | PASS | 0 |

Tier 3 was not run.  This imports an already-certified classical
`CLASSICAL_CHARGE` theorem and hardens the physical-run contract; it does not
freeze a classical or quantum release, change shared algebra, promote a paper
theorem, or establish a `LORENTZIAN-CAUSAL` or quantum lifecycle state.
Draft-2020-12 instance validation was not run because `jsonschema` is not
installed; this is not counted as a pass.
