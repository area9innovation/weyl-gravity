# Generic-background physical Hessian through linear curvature

## Result

The same-gauge Euclidean traceless-tensor Hessian is now imported through its
complete first-background-curvature layer.  In the monic source convention,

```text
H_source = 1hat Box^2
         + V^(rho,sigma) nabla_rho nabla_sigma
         + N^rho nabla_rho
         + U
         + O(curvature^2).
```

The exact source ledger contains `9` terms in `V`, `8` in `N`, and `5` in
`U`.  Every term has total engineering order four.  The source is Barvinsky,
Camargo, Kalugin, Ohta and Shapiro, [*On the local term in the anomaly-induced
action of Weyl quantum gravity*](https://arxiv.org/abs/2308.05251),
arXiv:2308.05251v2,
equations `gf-gen`, `gauge-min`, `Hmingen`, `traceless`, `Vrhosi`, `Nrho` and
`U`.  The decompressed TeX source is pinned by SHA-256
`7d8f044fbbc166ff67f4ff4258d6db5ff56d078a3c58884b9201e29d5b0ad118`.

This is a `LOCAL-ALGEBRAIC` plus `EUCLIDEAN-SPECTRAL` coefficient input.  It
is not a full generic Hessian theorem.

## Gauge and normalization crosswalk

The source parameters are

```text
gamma1 = 1/2
gamma2 = -1/6
tau    = -1/4
```

with trace gauge `h=0`.  Hence its vector gauge is exactly the repository
`beta=1/4` gauge

```text
F_mu = nabla^nu h_mu_nu - (1/4) nabla_mu h,
F_W  = h,
```

whose coupled Diff–Weyl ghost has already been certified independently.

The source writes the quadratic form as

```text
S^(2) = (1/4) integral sqrt(g) h H_source h.
```

The repository functional Hessian is therefore

```text
H_repository = (1/2) H_source,
```

matching the exact flat-TT leading coefficient and the round-`S4` dictionary.
The normalized insertion used in the trace logarithm is unchanged:

```text
((H0/2)^-1)(H1/2) = H0^-1 H1.
```

## Exact internal checks

- The four-dimensional traceless projector is idempotent and has rank `9`
  inside the rank-`10` symmetric-tensor bundle.
- On the scalar-flat restriction, `7`, `6`, and `3` terms survive in `V`,
  `N`, and `U`, respectively.
- On constant curvature and TT fields, modulo terms quadratic in curvature,
  the direct `K Box` coefficients are `-8`, `-4`, and `+6`.  Their sum is
  `-6`, so with `A=-Box` the imported source layer is `A^2+6 K A`.
- The full repository round-`S4` Hessian is
  `(1/2)(A+2K)(A+4K)`, with `K=1` on the unit fixture.  The exact difference is the repository
  curvature-squared fixture `+4 K^2` (source monic `+8 K^2`).  This nonzero
  remainder is the fail-closed proof that the import is not the complete
  Hessian.

## What this activates

The first-curvature insertion

```text
H1 = V nabla nabla + N nabla + U
```

is complete.  Therefore the pure three-linear-insertion physical row

```text
Tr[(H0^-1 H1)^3]
```

can now be computed at generic nonexceptional momentum and projected to the
five parity-even third-curvature carriers.

The following remain open:

- the curvature-squared algebraic Hessian layer `H2`;
- mixed third-curvature rows containing both `H1` and `H2`;
- the integrated physical `n=3` triangle;
- assembly of the five repository form-factor functions and coefficients;
- generic primed Green/spectral data, complete `Gamma1/Q1`, residual transfer,
  and every Lorentzian or state claim.

## Replay

Tier 0 and Tier 1 commands are:

```bash
PYTHONPATH=quantum-weyl python3 -m \
  spectral.euclidean.generic_background_physical_hessian_linear_curvature --check
PYTHONPATH=quantum-weyl python3 -m \
  spectral.euclidean.verify_generic_background_physical_hessian_linear_curvature
PYTHONPATH=quantum-weyl python3 -m unittest \
  spectral.euclidean.tests.test_generic_background_physical_hessian_linear_curvature
```

The affected frontier and Paper 12 claim-map verifiers are run after this
certificate is bound to their dependency ledgers.  The full repository suite
is not a per-commit requirement because this import does not alter shared
classical algebra or promote a lifecycle state.

## Verification receipt

The final scoped run on 2026-07-19 recorded:

```text
producer --emit                                      PASS  0.12 s
producer --check                                     PASS  0.13 s
independent certificate verifier                     PASS  0.12 s
8 physical-Hessian unit/mutation tests               PASS  0.27 s
active-frontier generation                           PASS  0.17 s
active-frontier independent verifier                 PASS  0.22 s
8 active-frontier unit/mutation tests                PASS  0.40 s
Paper 12 claim-map reproducibility check              PASS  0.05 s
Paper 12 independent claim-map verifier               PASS  0.04 s
Python compile and JSON parse checks                  PASS
main Paper 12 two-pass LaTeX build                    PASS
computational supplement two-pass LaTeX build         PASS
LaTeX warnings/errors/overfull/underfull audit         PASS (none)
```

One initial supplement invocation from `paper/` failed because its generated
table path is repository-root-relative; it emitted no PDF and was not counted
as a pass. Re-running from the declared repository-root build context passed.
The first active-frontier unit run also rejected the deliberately retired
simplex/IBP next-gate expectation; the stale regression was updated, the
content-addressed frontier was regenerated after the claim map, and the full
scoped frontier module then passed.

Tier 2 was limited to the directly affected generated frontier and Paper 12
claim chain. Tier 3 was not run: this change imports a new content-addressed
coefficient input but changes no shared classical operator or core algebra,
does not freeze a theorem, and does not promote a lifecycle state.
