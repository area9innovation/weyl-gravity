# Strict 386-row full-q1 split sign gate v1

## Outcome

No. The executable generalized-auxiliary matrix whose SHA-256 is already certified contains v_star -> +eta_star on four rows. The factorized actual-curved-Q source and both generalized/curved human ledgers instead declare v_star -> -eta_star. Nilpotency and the 36-row contraction hold for either sign, so the existing algebraic checks cannot detect the mismatch. The serialized exact odd pairing does: the executable plus sign has zero component cyclicity defects, while the declared minus sign has eight exact defects, two orientations for each of four components. The published 386-row carrier is the split mapping-cylinder presentation, so T, A and B belong to the separate canonical shear and endpoint inclusion/projection, not to the primitive split q1 arrows. Full q1 serialization must therefore pause at this sign gate. The minimal repair is to change the factorized dual arrow and textual ledgers to plus, matching both the executable matrix and the current pairing, and then rerun the affected classical chain. No causal theorem is revoked and no Hadamard or QME claim is promoted.

## Exact sign comparison

| candidate | q1 squared | contraction | pairing cyclicity |
|---|---:|---:|---:|
| executable `+I_4` | 0 defects | 0 defects | 0 defects |
| declared `-I_4` | 0 defects | 0 defects | **8 defects** |

The eight failures are not numerical noise: all coefficients are exact rationals. Nilpotency and contractibility are blind to this isolated cotangent sign; the odd pairing is the decisive independent rail.

## Coordinate consequence

The first full-q1 table should serialize the split differential and serialize the canonical shear separately.

## Preferred repair

Change the factorized curved q dual arrow and textual certificate ledgers to v_star -> +eta_star, matching the executable matrix and current odd pairing.

The repair is **not applied by this result**. The classical affected chain must be regenerated before full q1 bytes can be accepted.

## Reproduction

```text
PYTHONPATH=<sympy-site> python3 quantum-weyl/classical_import/produce_strict_386_auxiliary_q_sign_witness.py --check
python3 quantum-weyl/classical_import/build_strict_386_full_q1_split_sign_gate.py --check
python3 quantum-weyl/classical_import/check_strict_386_full_q1_split_sign_gate.py
python3 quantum-weyl/classical_import/verify_strict_386_full_q1_split_sign_gate.py
python3 -m unittest quantum-weyl/classical_import/tests/test_strict_386_full_q1_split_sign_gate.py
```

## Boundaries

- This does not establish that the preferred sign repair has been applied to the authoritative classical source and affected certificate chain.
- This does not establish a receiver-readable full 386-row q1 component jet table or accepted common operator snapshot hash.
- This does not establish componentwise nilpotency and cyclicity of the endpoint and curvature-cone blocks in one combined artifact.
- This does not establish portable local SDR maps, endpoint/full Green actions, local D or q2 compatibility.
- This does not establish a Hadamard state, Ward theorem, QME restoration, residual transfer or Lorentzian quantum theory.

## Next gate

Repair the factorized curved auxiliary dual-arrow sign to +I_4 or explicitly replace the auxiliary pairing convention, then regenerate and verify the affected classical certificate chain. Only after the repaired source and serialized pairing agree should the full split-basis q1 table be emitted.
