# Strict minimal-BV q3 cyclicity v1

**Result:** `STRICT_MINIMAL_BV_Q3_CYCLICITY_V1`

**State:** `MINIMAL_Q3_ARITY_AND_CYCLICITY_CERTIFIED_386_CYCLIC_STABILIZATION_OPEN`
**Dependency:** `LOCAL-ALGEBRAIC`

## Outcome

The imported minimal q3 is cyclic under the repository's canonical odd BV
pairing.  Its only nonzero sector is

```text
V4(h1,h2,h3,h4) = Omega(h4, q3(h1,h2,h3))
                   = D^4 S_W(h1,h2,h3,h4) mod d.
```

The fourth variation of one local action is symmetric in all four metric
directions.  All metric directions are even, so the cyclic Koszul sign is
`+1`.  The receiver sign translation is also `+1` on `h` and `h_star`; its
minus signs occur only on the two ghost-antifield rows, whose q3 components
are identically zero.

This is an integrated-local-functional statement modulo horizontal boundary
terms.  It deliberately does not claim pointwise equality of unintegrated
density representatives.  Compact support is the boundary condition that
makes the integrated cyclic identity exact.

The minimal carrier now has both the complete arity-three identity and q3
cyclicity.  The next unresolved object is the explicit 386-row cyclic
stabilization; no full-carrier promotion is made here.

## Reproduction

```text
python3 quantum-weyl/classical_import/build_strict_minimal_bv_q3_cyclicity.py --check
python3 quantum-weyl/classical_import/check_strict_minimal_bv_q3_cyclicity.py
python3 quantum-weyl/classical_import/verify_strict_minimal_bv_q3_cyclicity.py
python3 -m unittest quantum-weyl/classical_import/tests/test_strict_minimal_bv_q3_cyclicity.py -v
```

## Does not establish

- pointwise equality of cyclic density representatives before integration by parts.
- a cyclic stabilization or L-infinity morphism to all 386 graph rows.
- the 386-row arity-three identity or general lambda-squared source closure.
- q3 compatibility with a causal Green homotopy or an analytic Moller map.
- renormalized Lorentzian time-ordered products or a Hadamard state.
- QME restoration, residual transfer, or a Lorentzian quantum theory.
