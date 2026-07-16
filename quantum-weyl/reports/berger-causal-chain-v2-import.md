# Berger causal chain v2 import

The quantum consumer pins classical commit `74318359` and independently
imports the full repaired causal chain:

- retained 26-row advanced and retarded chain homotopies;
- support-local lift to all 54 gauge-fixed rows;
- cyclic (D)-Cartan contraction through arities one and two.

The 26-row export is bound to the accepted Volterra v2 hash and now records
the correct frozen input commit. Its row inventory, proof-artifact hashes,
causal support, cyclic adjointness, (D)-equivariance and zero-mode policy are
checked independently. The 54-row lift replays the `54=28+26` decomposition
and rejects inverse spatial operators or projectors.

At arity two, the import retains the concrete audit of all 25,543 admissible
degree-zero row triples. The frozen odd Darboux pairing has 27 negative dual
slots and the resulting (C_3) group-law defect count is zero. The cyclic
primitive has two-sided causal-hull support; it is not mislabeled as separately
advanced or retarded.

This is still a classical BV causal import. Arity three, Hadamard data,
renormalized Lorentzian products, Lorentzian QME restoration and quantum
claims remain open.

```text
PYTHONPATH=quantum-weyl python -m lorentzian.berger_causal_chain_v2_import_certificate --check
PYTHONPATH=quantum-weyl python -m unittest quantum-weyl/lorentzian/tests/test_berger_causal_chain_v2_import.py -v
```

Verification receipt (2026-07-16): the complete affected chain—Volterra v2,
26-row v2, 54-row v2, causal (D)-Cartan v2, both quantum certificate checks,
and eleven quantum mutation/schema tests—passed in 2.02 seconds. Tier 3 was
not run because no Hadamard, QME, quantum lifecycle, freeze or paper theorem
was promoted.
