# Strict 386-row nonminimal theory-identity obstruction v1

**Result:** `STRICT_386_NONMINIMAL_THEORY_IDENTITY_OBSTRUCTION_V1`

## Outcome

The exact source/candidate comparison is nonzero in the cyclic channel
`Omega(f_hat,q2(v,v))`:

- authoritative ordinary-derivative action: **-1**;
- trivial-stabilization candidate: **0**;
- source minus candidate: **-1**.

The candidate is therefore not literally the authoritative nonminimal action,
and the recorded linear shear cannot make it so.  Its internal q1/q2/q3,
cyclicity and D-equivariance certificates remain valid.  The missing object is
now sharper: a nonlinear auxiliary-elimination or cyclic L-infinity map whose
first quadratic correction reproduces this channel.

## Reproduction

```text
python3 quantum-weyl/classical_import/build_strict_386_nonminimal_theory_identity_obstruction.py --check
python3 quantum-weyl/classical_import/check_strict_386_nonminimal_theory_identity_obstruction.py
python3 quantum-weyl/classical_import/verify_strict_386_nonminimal_theory_identity_obstruction.py
python3 -m unittest quantum-weyl.classical_import.tests.test_strict_386_nonminimal_theory_identity_obstruction
```

## Boundary

This is an obstruction to literal and linear theory identity, not an obstruction
to nonlinear equivalence and not a causal, Hadamard, or QME result.
