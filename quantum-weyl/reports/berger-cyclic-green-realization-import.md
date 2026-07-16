# Berger cyclic analytic Green realization import

The quantum consumer pins classical commit
`e415ba39c102ede59300cac64c44a2a1a298c88e` and independently reconstructs
the 36-row analytic realization with ranks `[5,13,13,5]`. The added `y,y*`
pair is a support-local analytic graph pair; the authoritative BV complex
remains the 34-row `[5,12,12,5]` complex.

The exact replay verifies both source and solution graph SDRs, their
intertwining with `L13` and `L12`, the formal-adjoint antifield block, the
nondegenerate 36-row pairing, and cyclicity of `P36`. The future Green pair is
required to obey `G13_plus^sharp=G13_minus`. No inverse Laplacian or spatial
zero-mode projector is admitted.

The result is an analytic realization ready for Green analysis, not a Green
theorem. Advanced/retarded inverses, causal support, the 26-row causal
homotopy, causal D-Cartan realization, Hadamard state, QME, and quantum theory
remain open.

```text
PYTHONPATH=quantum-weyl python -m lorentzian.cyclic_green_realization_import_certificate --check
PYTHONPATH=quantum-weyl python -m unittest quantum-weyl/lorentzian/tests/test_cyclic_green_realization_import.py -v
```

The three exact and mutation-sensitive tests complete in 16.61 seconds. Tier
0 and the affected Tier 1/2 certificate chain were run. Tier 3 was not
required because no Green operator, causal homotopy, or quantum lifecycle
state is promoted.
