# Berger metric mixed-order Green realization contract

Dependency tags: `LOCAL-ALGEBRAIC`, `LORENTZIAN-CAUSAL`.

The first dressed cyclic witness has a generic rank-eight metric symbol. An
exact normalized coefficient witness shows that it is not the independently
required scalar-biwave block, so it is algebraically valid but not an
admissible Green endpoint. The BV-canonical raw transport restores the scalar
biwave on all ten metric and five gauge directions.

The preferred fourth architecture is therefore
`RAW_CLOCK_RANK_ONE_WAVE_EXTENSION`, alongside the direct filtered,
differential-algebraic, and auxiliary-field routes. A direct retained solver
must classify its characteristic-rank strata. The raw route pins both the
scalar-biwave principal blocks and the exact cyclic `QW+WQ` identity. Its
exact 10+2 Schur preflight exposes a nonzero rank-one, wave-divisible
order-six term. The imported 13-row scalar-wave prolongation now realizes
that term as an order-four support-local extension with exact triangular
reduction to `L12 direct sum I1`. The remaining analytic work is to construct
advanced/retarded inverses, causal support, cyclic adjointness, and
support-local Green transport.

The extension is now also paired and cyclic on the 36-row analytic
realization `[5,13,13,5]`. Exact source/solution graph SDRs identify its
relation to the authoritative 34-row BV complex, and the required future
adjoint identity is `G13_plus^sharp=G13_minus`. The analytic `y,y*` pair does
not add BV cohomology.

All routes require exact proofs of both left and right inverse identities,
advanced/retarded support, propagation of constraints, formal-adjoint and
cyclic compatibility, `D`-equivariance, row completeness, and a zero-mode
policy. The raw route additionally requires the pinned endpoint and rank-one
wave-extension imports, scalar null-cone control, and SDR transport. Green
realization and transport remain open. A principal-symbol factorization alone
cannot pass.

Even a successful metric export does not implicitly promote the full 26-row
Green homotopy. Assembly with the already certified ghost and identity blocks
must pass the separate endpoint contract. Hadamard data and quantum execution
remain later stages.

Reproduce the interface receipt with:

```bash
PYTHONPATH=quantum-weyl python3 -m lorentzian.metric_mixed_order_green_contract_certificate --check
PYTHONPATH=quantum-weyl python3 -m unittest quantum-weyl/lorentzian/tests/test_metric_mixed_order_green_contract.py -v
```

The certificate records the exact commands and elapsed time of the current
scoped verification run. The full classical chain and Tier 3 are unnecessary
unless the content-addressed classical input or a causal lifecycle theorem is
promoted.

The raw endpoint fast receipt and metric-contract tests are the smoke rails.
The independent endpoint PBW replay completed in 84.59 seconds with
`SCIENTIFIC REPLAY PASS`; it is a separate exhaustive rail, not a per-edit
smoke test. The rank-one extension importer independently replays the exact
13-row triangular reduction and fixed-incidence obstruction; the cyclic
realization importer independently replays the 36-row pairing, cyclicity,
formal adjoint, and graph SDRs.
