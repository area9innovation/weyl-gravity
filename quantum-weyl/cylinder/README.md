# Quantum cylinder restriction bootstrap

The cylinder branch is initialized, but it is deliberately blocked at the
classical-import gate.  Its machine-readable state is
[`bootstrap.json`](bootstrap.json), tagged `LOCAL-ALGEBRAIC`.

The existing classical repository supplies content-addressed evidence for a
15-generator conformal ledger, the selected positive-frequency state ledger,
and centered

\[
H^4_{\rm res}=\operatorname{span}\{[W_+^2],[W_-^2]\},\qquad G_{\rm res}=I_2.
\]

Those two classes are deformation/vertex classes, not one-particle states.
The bootstrap does not copy or reconstruct the classical computations.

No `LOCAL_TO_CYLINDER_MAP` is claimed.  The full projection pipeline remains
blocked because the classical team has not yet exported a complete
`pi_cl`, portable residual representation matrices, normalized representative
vectors, or centered bases in both adjacent degrees 3 and 5.  The displayed
even/odd basis formula is only a convention ledger; an explicit parity
operator and its Ward identity remain `NOT_AVAILABLE`/`NOT_COMPUTED`.

Run the import verifier before using this directory:

```bash
python3 quantum-weyl/classical_import/verify_snapshot.py --check
```

It is a successful integrity check when the command exits zero while the
certificate still reports `gate_a_status: FAIL_CLOSED`.  Exit zero means the
fail-closed ledger is current, not that Gate A has passed.
