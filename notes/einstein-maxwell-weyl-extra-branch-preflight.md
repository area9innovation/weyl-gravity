# Weyl–Maxwell complementary-branch preflight

Dependency boundary: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`. Lifecycle:
`CLASSIFIED`.

The invariant extra object is

```text
Q_extra = H^0(C_WM^full) / i_* H^0(C_EM^std).
```

It is a quotient, not a chosen complement. A symplectic-orthogonal
representative may be asserted only after constructing the full target reduced
form and controlling its radical. Extra solution classes, adjoint-cokernel
classes, presymplectic radicals, and gauge classes remain distinct result
kinds.

The first solve is the generic axial `ell>=2` block at symbolic `lambda` and
periodic momentum `k`. It must derive the complete target harmonic operator,
quotient its on-shell kernel by target gauge and the certified Einstein image,
retain all characteristic multiplicities and Jordan chains, and compute the
complete Einstein/extra Lee–Wald matrix. Zeros of the existing relative
symplectic weights are not extra dispersions.

The preflight imposes no bounded-in-time or two-ended boundary selection and
certifies no extra particle, causal sector, or quantum claim.

Receipt (2026-07-16): Tier 0 Python/JSON parsing and scoped diff checks passed.
Tier 1 and the affected certificate chain passed as part of the 35-test suite
in 1.31 s; the mixed-current direct replay took 16.92 s and the independent
mixed, assembly, and preflight verifiers passed. Tier 3 was not run because
this is a reduced-mode preflight with unchanged content-addressed current
engine and no lifecycle or release promotion.

The generic axial child preflight has now landed. It contracts the six
ungauged odd-parity coefficients to four invariants over the exact differential
ring using only the constant pivot `2`; it does not invert `D`, `k`, or a
dispersion factor. The target operator remains the next missing object.
