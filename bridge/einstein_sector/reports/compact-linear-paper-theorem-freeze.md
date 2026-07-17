# Compact Einstein--Maxwell/Weyl--Maxwell Paper A theorem freeze

## Disposition

The scoped mathematical claims in
`paper/10-compact-einstein-maxwell-weyl-phase-space.tex` are
`THEOREM_FROZEN`. The next scientific gate is external specialist review,
not another major internal calculation.

The freeze covers the complete standard Einstein--Maxwell harmonic phase
space, the formal fixed-bundle tangent inclusion, the relative Lee--Wald
endomorphism, the physical-ring generic axial quotient, and the generic
axial extra current and extractors. It does not promote the polar extra
branch, final residual quotient, nonlinear closure, causal scattering, or a
quantum interpretation.

## Final internal refinements

- connected the connection tangent `a` to the field-strength tangent `f=da`;
- defined `K_{ell,n}=Q(k_n)` and separated the algebraic module from the real
  positive-frequency current space;
- listed the five functorial ingredients of the dual-number Chevreton bridge;
- defined the determinantal ideals at first use;
- corrected the theorem label and completed the 2003 Chevreton-conservation
  journal citation.

## Verification

Tier 0 and the scoped paper checks were run on 2026-07-17:

```text
python3 bridge/einstein_sector/verify_compact_linear_paper_claim_map.py
pdflatex -interaction=nonstopmode -halt-on-error -output-directory paper paper/10-compact-einstein-maxwell-weyl-phase-space.tex  # three passes
```

The claim-map verifier passed. All three TeX passes completed without
undefined references or overfull boxes. Final human verification of the
manuscript, certificates, citations, and authorship disclosure remains a
submission gate.

Tier 3 for the owning Einstein package was then run:

```text
python3 -m unittest discover -s bridge/einstein_sector/tests -p 'test_*.py'
```

Result: `377` tests passed in `263.805 s`. The unrelated classical, nonlinear,
and quantum packages were not rebuilt because this freeze changes only the
paper lifecycle and manuscript prose; their certified inputs are imported by
unchanged content hashes.
