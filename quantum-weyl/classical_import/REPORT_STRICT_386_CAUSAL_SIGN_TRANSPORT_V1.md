# Strict 386-row causal sign transport

**Result:** `STRICT_386_CAUSAL_SIGN_TRANSPORT_V1`

**State:** `STRICT_386_CAUSAL_ARCHITECTURE_STABLE_UNDER_MINIMAL_SIGN_TRANSPORT_COMMON_HASH_OPEN`

**Dependencies:** `LOCAL-ALGEBRAIC`, `LORENTZIAN-CAUSAL`

## Outcome

The Gate-V5 ghost-antifield sign repair does **not** invalidate the existing
strict 386-row causal architecture. Its thirty-component minimal carrier has
exactly the endpoint profile of the causal complex:

| endpoint block | role | dimension | sign |
|---|---|---:|---:|
| `G` | Diff plus Weyl ghosts | 5 | +1 |
| `M` | metric field | 10 | +1 |
| `E` | metric antifield | 10 | +1 |
| `I` | Diff plus Weyl ghost antifields | 5 | -1 |

Extending the endpoint involution by the identity on the 356 algebraically
contracted rows gives

```text
T_386 = I_356 direct-sum diag(I_5,I_10,I_10,-I_5).
```

It has 381 positive and five negative diagonal entries. Conjugating the unary
differential and both Green homotopies transports the exact chain-homotopy
identity. Because the map is pointwise and order zero, support and causal
orientation are unchanged. Transporting the pairing at the same time preserves
the graded-adjoint relation.

## What this decides

The strict target-theory causal route survives the newly discovered convention
repair. We therefore do not need to rebuild its hyperbolic architecture merely
because `c_star` and `omega_star` change sign.

This is not yet the missing import bridge. The match is exact at the level of
types, dimensions and complex roles, but Gate V5 accepts zero common hashes.
The certificate does not identify the local q1 bytes with the endpoint bytes,
serialize the pairing on all 386 rows, or prove nonlinear q2/D compatibility.

## Exact checks

| check | status | meaning |
|---|---|---|
| `endpoint_type_dimension_bridge` | `VERIFIED` | the Gate-V5 generator groups match the causal endpoint G/M/E/I ranks |
| `full_transport_involution` | `VERIFIED` | 381 positive and five negative diagonal entries over the integers |
| `transported_unary_nilpotency` | `VERIFIED_BY_EXACT_CONJUGATION` | T_386 is involutive and the source causal complex is a chain complex |
| `transported_green_homotopy` | `VERIFIED_BY_EXACT_CONJUGATION` | conjugation transports the certified two-sided Green-homotopy identity |
| `causal_support_and_orientation` | `VERIFIED` | T_386 is a pointwise order-zero signed bundle automorphism, so it neither enlarges support nor swaps advanced and retarded orientation |
| `transported_adjoint_relation` | `VERIFIED_ON_TRANSPORTED_PAIRING` | the source graded-adjoint theorem is invariant under simultaneous transport of operator and pairing |
| `common_byte_identification` | `NOT_ESTABLISHED` | matching dimensions and formula roles do not identify the Gate-V5 q1 bytes with the 386-row endpoint bytes |
| `nonlinear_causal_compatibility` | `NOT_ESTABLISHED` | the four changed ordered q2 rows are local-algebraic data, while the 386 certificate is unary causal data |

## Foundational strength

For the fixed carrier, the transport wrapper is primitive-recursive finite
algebra: signed permutations, integer counts and equational substitution. It
adds neither a choice operation nor an infinite selection. The weakest base of
the imported analytic causal theorem itself has not been established, so the
PRA classification must not be widened to the whole Green theorem.

## Next gate

Serialize the endpoint inclusion/permutation and pairing on the exact 386-row bytes, prove coefficientwise equality with translated Gate-V5 q1, extend the canonical sign/pairing convention over the 356-row complement, and only then test q2/D compatibility with the causal contraction.

## Reproduction

```bash
python3 quantum-weyl/classical_import/build_strict_386_causal_sign_transport.py --check
python3 quantum-weyl/classical_import/check_strict_386_causal_sign_transport.py
python3 quantum-weyl/classical_import/verify_strict_386_causal_sign_transport.py
python3 -m unittest quantum-weyl/classical_import/tests/test_strict_386_causal_sign_transport.py
```
