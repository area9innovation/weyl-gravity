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

The engine also retains the sourced identity before imposing anomaly freedom:

\[
[Q,\mathcal A_D^{(1)}]
=
[[Q,Q_1],\iota_D]
-\left([Q,\mathcal L_D^{(1)}]+[Q_1,\mathcal L_D]\right).
\]

This keeps a QME source separate from a Ward-algebra source.  Exactness may
be computed in a declared linear-constraint subcomplex of admissible
operators.  The implementation verifies that the constraints are preserved
by `[Q,-]`; a primitive in the full endomorphism space is not accepted when
it violates those constraints.  The certificate includes a regression where
an ambient `EXACT_REMOVABLE` defect becomes `NONTRIVIAL_ANOMALY` after its
only primitive is excluded.

First-order scheme changes are explicit.  An uncompensated admissible shift
`iota_1 -> iota_1 + X` changes the representative by `[Q,X]` and therefore
preserves its quotient class.  Adding the matching Ward correction preserves
the representative itself.  Simultaneous similarity redefinitions of
`Q_1`, `iota_1`, and `L_D^(1)` also leave the first-order defect unchanged.
The engine rejects a scheme generator that is outside the declared
admissible subcomplex.

The physical Ward-operator socket is specified separately by
[`ward_insertion_contract.py`](ward_insertion_contract.py). It requires a
content-addressed observable complex, admissibility policy, all six
order-zero/one operators, regulator and boundary provenance, the regulated
Slavnov breaking, and proof artifacts for the sourced consistency identity.
A sourced QME-open payload cannot emit a Cartan class or local-to-Cartan map.

## Claim boundary

The physical sector ledger separates algebraic classification, analytic
operator construction, and coefficient computation. The full minimal,
nonminimal, pure-Diff, mixed Diff--Weyl, and canonically gauge-fixed local BV
anomaly quotient is complete on the regular Bach locus, with even/odd
dimensions `2/1`. The exact Slavnov assembly preflight binds the standard
background vector `(199/30,-87/20,0)` to that quotient and exposes a strict analytic input
schema, but does not identify it with the repository breaking. The classical
26/54-row causal Green homotopy is imported; global BRST Hadamard covariance,
renormalized products, and all order-one Ward operators remain absent.
There is no renormalized `Q_1`, `iota_1`, or `L_D^(1)`, and the local QME has
not been restored or declared obstructed. Boundary/corner, scalar-clock,
measure, and Lorentzian observable algebras are also absent. Consequently
this package does not establish anomaly freedom, a repository anomaly
coefficient, residual quantum transfer, or a quantum pairing correction.

The required classical D-quotient handoff settings are parsed, semantically
verified, and imported by content hash.  Additive settings, including the
Berger clock, are enumerated but not consumed by this compact quantum rail.
The consumed handoff records a
sector-dependent compact-cylinder result: `D_CHARGED` on the unrestricted
locally reduced linearized space `P_lin`, and `D_GAUGE` only on the declared
full Taub/moment-map zero fibre `P_Taub0`.  This restricts the quantum question
to a declared phase space; it does not supply a quantum Ward identity.

The universal ambient obstruction group is recorded as

\[
H^0(\operatorname{Der}_{\rm adm}(\mathcal C),[Q,-]).
\]

Its realization as a support-local relative BV group remains gated on a
declared renormalized observable algebra; the local BV anomaly-density basis
is now complete. In
particular, this degree-zero operator obstruction must not be silently
identified with the ordinary ghost-number-one anomaly-density catalogue.

## Verification

From the repository root:

```bash
PYTHONPATH=quantum-weyl python3 -m unittest discover -s quantum-weyl/cartan/tests -v
PYTHONPATH=quantum-weyl python3 -m cartan.certificate --check
PYTHONPATH=quantum-weyl python3 -m cartan.ward_insertion_contract_certificate --check
python3 -m py_compile quantum-weyl/cartan/*.py quantum-weyl/cartan/tests/*.py
```

The deterministic receipt is
[`certificates/CARTAN_DEFECT_COMPLEX_PRECERTIFICATE.json`](certificates/CARTAN_DEFECT_COMPLEX_PRECERTIFICATE.json).
