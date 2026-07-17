# Retained mixed ell3 constant-field redefinition screen

Dependency tag: `LOCAL-ALGEBRAIC`. Generality: `G0`.

After setting every PBW derivative word to zero and lowering with the typed
retained odd pairing, the mixed physical action lies in

```text
Sym^2(G*) tensor Sym^2(A*)
dimension = 550
```

The complete matter-parity-preserving zero-jet cotangent-lift ansatz has 810
`F2` and 1,880 `F3` coefficients. Its exact coboundary matrix has shape
`550 x 2690`, 5105 nonzero entries,
rank 550, and zero-dimensional cokernel. The landed constant-field mixed
quartic has 63 nonzero coordinates and the exported
51-coefficient primitive reconstructs all
of them exactly.

## Meaning

The two zero-derivative representative evaluations printed in Paper 11 prove
that the frozen retained tensor is nonzero, but they cannot be used as
nonremovability witnesses: the *entire* constant-field mixed quartic sector is
an exact redefinition image.

This does **not** settle N-G4. The 288 ghost/antifield completion coefficients
have not been independently matched by this primitive. Positive-jet terms,
integration-by-parts relations, the complete jet-bounded cyclic redefinition
complex, descent to `ell1` cohomology, and branch-resolved mixing remain open. The next gate is
`BERGER_RETAINED_MIXED_ELL3_POSITIVE_JET_CYCLIC_REDEFINITION`.
