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

Thus the universal algebraic obstruction belongs to

\[
H^0(\operatorname{Der}_{\rm adm}(\mathcal C),[Q,-]).
\]

The exact solver separates zero defects, removable boundaries with explicit
degree-minus-one primitives, and nonzero quotient classes with normalized
dual witnesses.  Three finite fixtures exercise all three outcomes.  They
certify implementation mechanics, not a physical Weyl-gravity anomaly.

## Fail-closed physical status

Every bulk, residual, boundary/corner, measure, and scalar-clock candidate
sector is `UNDEFINED_ANALYTICALLY`.  Every requested physical setting has
verdict `ANALYTIC_FRAMEWORK_MISSING`.  In particular:

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
elapsed_seconds: 0.09
status: PASS (11 tests)
test_tier: 1

command:
  PYTHONPATH=quantum-weyl python3 -m cartan.certificate --check
elapsed_seconds: 0.06
status: PASS
test_tier: 1

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
certificate_sha256: c1cd80a9e6040c542c50dc559374ae31bd86e0239bcc235a323f1b3ca4d1ef2a
test_tier: 0
```

Tier 3 was not run: this is an isolated infrastructure precertificate, changes
no shared algebraic dependency, and promotes no physical candidate, QME,
residual-transfer, paper-theorem, or Lorentzian lifecycle state.
