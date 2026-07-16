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

The authoritative classical lower-by-two theorem is now pinned and replayed:
`A10=Box_2^2+V_2`, with `ord(V_2)<=2`. Its 92 nonzero quadratic-symbol
entries are all nondivisible by the scalar wave, so a factorization fixing
one canonical rough-wave factor is impossible. The downstream exact
lower-order factor screen is also complete. After removing
the exact scalar biwave and the uniquely determined shared first-order
connection, the quadratic remainder has the normalized witness
`-u^-2 [p0 p3] R2[h00,h03]=1`. Consequently two scalar-principal factors with
the same invariant connection and arbitrary order-zero potentials cannot
produce the endpoint. This does not obstruct unequal subprincipal factors or
an auxiliary/first-order realization; a causal Volterra/Levi construction is
also live.

The complete analytic endpoint nevertheless cannot be the metric-causal
Green theorem. Its exact Douglis determinant contains the extra factor
`p0^2-2|p_spatial|^2`, with rank twelve on that cone and rank thirteen off it.
Its exact polarization is mixed: it has nonzero retained metric and clock
components, and selector projection does not kill it. What is contractible is
the clock/graph subcomplex of the BV differential, not this polarization of
the chosen witness. The physical next gate is therefore a hybrid chain
construction: apply the certified BV SDR and construct a new retained witness;
do not project solutions of `L13`.

That projection has now been executed exactly. The retained endpoint is
block diagonal with degree ranks `3|10|10|3`, and its ten-row metric block is
precisely `A10`. The exact local companion
`C20=[[Box_2,-I10],[V_2,Box_2]]` has graph identity
`C20(h,Box_2 h)=(0,A10 h)` and principal determinant `q^20`; it introduces no
extra characteristic cone. An exact two-sided graph SDR now handles arbitrary
companion sources and verifies both retract identities with side conditions.
The remaining analytic gate is the causal Volterra resolvent, global support,
and cyclic adjointness, not identification of the retained PDE.

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
PYTHONPATH=quantum-weyl python3 -m lorentzian.metric_equal_connection_factor_screen_certificate --check
PYTHONPATH=quantum-weyl python3 -m unittest quantum-weyl/lorentzian/tests/test_metric_equal_connection_factor_screen.py -v
PYTHONPATH=quantum-weyl python3 -m lorentzian.retained_biwave_companion_preflight_certificate --check
PYTHONPATH=quantum-weyl python3 -m unittest quantum-weyl/lorentzian/tests/test_retained_biwave_companion_preflight.py -v
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
