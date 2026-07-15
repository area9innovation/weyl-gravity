# Quantum Cartan-defect rail

Dependency tag: `LOCAL-ALGEBRAIC`.

This package begins Q-D1 from the quantum-team challenge.  It treats

\[
\mathcal A_D^{(1)}
=[Q,\iota_1]+[Q_1,\iota_D]-\mathcal L_D^{(1)}
\]

as a degree-zero cocycle in the declared admissible operator complex with
differential

\[
\delta_{\rm End}(T)=[Q,T]_{\rm graded}.
\]

The exact finite engine verifies the classical Cartan identity, the
linearized QME condition `[Q,Q_1]=0`, first-order Ward compatibility, and the
resulting consistency equation `[Q,A_D^(1)]=0`.  It computes the degree-zero
endomorphism cohomology and distinguishes:

```text
ZERO
EXACT_REMOVABLE
NONTRIVIAL_ANOMALY
```

An exact result carries an explicit degree-minus-one primitive.  A
nontrivial result carries a normalized dual witness annihilating every
generated boundary.  The checked fixtures prove these classification
mechanics only; they are not models of the pure-Weyl local BV complex.

## Claim boundary

The physical candidate ledgers currently read `UNDEFINED_ANALYTICALLY`.
There is no renormalized `Q_1`, `iota_1`, or `L_D^(1)`, the classical import
is unfrozen, the AFN0 lower-form and Euler bases are incomplete, and the local
QME has not been restored.  Boundary/corner, scalar-clock, measure, and
Lorentzian observable algebras are also absent.  Consequently this package
does not establish anomaly freedom, an anomaly coefficient, residual quantum
transfer, or a quantum pairing correction.

The universal ambient obstruction group is recorded as

\[
H^0(\operatorname{Der}_{\rm adm}(\mathcal C),[Q,-]).
\]

Its realization as a support-local relative BV group remains gated on a
declared renormalized observable algebra and complete local BV basis.  In
particular, this degree-zero operator obstruction must not be silently
identified with the ordinary ghost-number-one anomaly-density catalogue.

## Verification

From the repository root:

```bash
PYTHONPATH=quantum-weyl python3 -m unittest discover -s quantum-weyl/cartan/tests -v
PYTHONPATH=quantum-weyl python3 -m cartan.certificate --check
python3 -m py_compile quantum-weyl/cartan/*.py quantum-weyl/cartan/tests/*.py
```

The deterministic receipt is
[`certificates/CARTAN_DEFECT_COMPLEX_PRECERTIFICATE.json`](certificates/CARTAN_DEFECT_COMPLEX_PRECERTIFICATE.json).
