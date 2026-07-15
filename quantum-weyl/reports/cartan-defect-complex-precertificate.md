# First-order Cartan-defect precertificate

Dependency tag: `LOCAL-ALGEBRAIC`.

## Result

The Q-D1 rail now has an exact degree-zero operator complex.  At first order,

\[
\mathcal A_D^{(1)}
=[Q,\iota_1]+[Q_1,\iota_D]-\mathcal L_D^{(1)}.
\]

Given `Q^2=0`, `[Q,Q_1]=0`, the classical Cartan identity, and the
first-order Ward condition

\[
[Q,\mathcal L_D^{(1)}]+[Q_1,\mathcal L_D]=0,
\]

the implementation independently verifies

\[
[Q,\mathcal A_D^{(1)}]=0.
\]

Before either source is set to zero, the engine now verifies the stronger
identity

\[
[Q,\mathcal A_D^{(1)}]
=
[[Q,Q_1],\iota_D]
-\left([Q,\mathcal L_D^{(1)}]+[Q_1,\mathcal L_D]\right).
\]

A finite fixture retains a nonzero QME source and verifies the equality term
by term.  Thus failure of defect closure is no longer reported without its
QME and Ward provenance.

Thus the universal algebraic obstruction belongs to

\[
H^0(\operatorname{Der}_{\rm adm}(\mathcal C),[Q,-]).
\]

The exact solver separates zero defects, removable boundaries with explicit
degree-minus-one primitives, and nonzero quotient classes with normalized
dual witnesses.  Three finite fixtures exercise all three outcomes.  They
certify implementation mechanics, not a physical Weyl-gravity anomaly.

Exactness can now be restricted by named rational linear constraints.  The
admissible kernel must be closed under `[Q,-]`.  A regression fixture is exact
in the full endomorphism complex but nontrivial in the admissible subcomplex
because its sole degree-minus-one primitive is forbidden.  This prevents an
illegal finite counterterm from producing a false `EXACT_REMOVABLE` result.

The certificate also verifies first-order scheme covariance.  An
uncompensated homotopy shift changes the defect by the stored exact term
`[Q,X]`; the baseline `ZERO` representative and shifted `EXACT_REMOVABLE`
representative therefore define the same trivial quotient class.  The
compensated homotopy shift and simultaneous similarity transformation leave
the representative unchanged exactly.  A scheme shift excluded by the
admissibility constraints is rejected.

## Fail-closed physical status

The sector ledger now distinguishes algebraic, analytic, and coefficient
status.  Bulk algebraic classification is `IN_PROGRESS`; residual and clock
classification are `BLOCKED`; boundary and measure classification are
`NOT_COMPUTED`.  Every analytic operator remains `UNDEFINED_ANALYTICALLY`,
every coefficient remains `NOT_COMPUTED`, and every requested physical
setting has verdict `ANALYTIC_FRAMEWORK_MISSING`.  In particular:

- the classical compact-cylinder handoff is parsed with mutation guards and
  imported by hash; it says that
  `D` is charged on `P_lin` but gauge on the declared `P_Taub0` derived zero
  fibre; this phase-space split is not promoted to a quantum verdict;
- the classical import remains unfrozen;
- AFN0 lower-form exhaustiveness and the intrinsic Euler tower remain open;
- the minimal antifield/Koszul--Tate rows have not been imported;
- no renormalized operator algebra or actual `Q_1` exists;
- the pure-Weyl QME has not been restored;
- residual transfer is explicitly blocked on `QME_RESTORED`;
- scalar-clock and boundary/BFV complexes are absent.

The package does not identify the degree-zero operator obstruction with the
ordinary ghost-number-one local anomaly-density catalogue.  The map between
them is a later computation after both admissible complexes are declared.

## Receipt

```text
command:
  PYTHONPATH=quantum-weyl python3 -m unittest discover -s quantum-weyl/cartan/tests -q
elapsed_seconds: 0.23
status: PASS (32 tests, including dossier contribution guards)
test_tier: 1

command:
  PYTHONPATH=quantum-weyl python3 -m cartan.certificate --check
elapsed_seconds: 0.07
status: PASS
test_tier: 1

command:
  python3 d_quotient_classical/verify_classical_status.py --guards
elapsed_seconds: 0.05
status: PASS (6/6 mutation guards and artifact validation)
test_tier: 2 targeted imported-certificate audit

command:
  python3 symbolic/verify_conformal_cartan_contraction.py
elapsed_seconds: 12.25
status: PASS
test_tier: 2 targeted dependency audit

command:
  python3 -m py_compile quantum-weyl/cartan/*.py quantum-weyl/cartan/tests/*.py
  python3 -m json.tool <schema and certificate>
status: PASS
test_tier: 0

command:
  PYTHONHASHSEED={1,7,123} PYTHONPATH=quantum-weyl python3 -m cartan.certificate | sha256sum
status: PASS
certificate_sha256: aa7edc21c7250349531559657d4ec69eee2dd9100de3eedf242a8e29829e874c
test_tier: 0
```

Tier 3 was not run: this is an isolated infrastructure precertificate, changes
no shared algebraic dependency, and promotes no physical candidate, QME,
residual-transfer, paper-theorem, or Lorentzian lifecycle state.

## Cross-programme handoff

The quantum team contribution is emitted at
`quantum-weyl/cartan/contributions/QUANTUM_CARTAN_BLOCKED.json`.  It uses
`generator_id = D_compact`, `phase_space_id = compact_quantum`, and lifecycle
`QUANTUM`.  Its claim status is `BLOCKED` and its verdict is null.  The
evidence certificate is pinned to commit
`04e9d20c2c5dd7b2d3fa62492fdc7e12e2fe1f61` and SHA-256
`aa7edc21c7250349531559657d4ec69eee2dd9100de3eedf242a8e29829e874c`.

```text
command:
  PYTHONPATH=quantum-weyl python3 -m cartan.contribution --check
elapsed_seconds: 0.08
status: PASS
test_tier: 1

command:
  python3 d_quotient_programme/verify_programme_status.py --check --guards
status: PASS (5/5 mutation guards)
test_tier: 2 targeted dossier-contract audit
```
