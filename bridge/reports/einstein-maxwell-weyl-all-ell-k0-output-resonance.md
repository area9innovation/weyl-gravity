# All-generic-ell k=0 quadratic output resonance theorem

Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`.

For every integer input `ell>=2`, the nine nonzero quadratic frequencies
built from the Einstein-plus, Einstein-minus, and extra shell at `k=0` miss
every angularly allowed Weyl--Maxwell target shell.

The proof is exact.  Shell ordering reduces the infinite audit to four
candidate families: `L=2ell`, `L=2ell-1`, and, for one mixed sum only,
`L=2ell-1` with `2<=ell<=7`.  Exact resultants with

```text
p_L(z)=z-(L(L+1)-2/3),
q_L(z)=(z-L(L+1))^2-2L(L+1)
```

are nonzero on every candidate.  The three difference frequencies lie below
the first generic shell, while the two largest sum frequencies lie above the
largest angularly allowed shell.  Exceptional `L=1` roots are contained in
the same root set `{0,4/3,4}`.  At `L=0`, every actual nonzero-frequency
source is in the homogeneous operator image by the exact Noether identity.

Thus a failure of the general-`ell`, `k=0` second-order cone theorem cannot
come from a nonzero sum/difference resonance.  The remaining gate is the
zero-frequency source map and its adjoint-cokernel projection.  This report
does not promote the complete all-`ell` cone.

## Verification receipt

Date: 2026-07-17.

* Tier 0: scoped compilation and structured-data checks, `0.05 s`, passed.
* Tier 1: deterministic replay, independent symbolic verifier, and three
  regression tests, `2.10 s`, passed.
* Tier 2 was not run because every imported target-operator, physical-ring,
  exceptional-shell, and homogeneous-Noether input is unchanged and
  content-addressed.
* Tier 3 was not run because this closes the output-resonance gate without
  promoting the complete all-`ell` second-order cone or a programme freeze.
