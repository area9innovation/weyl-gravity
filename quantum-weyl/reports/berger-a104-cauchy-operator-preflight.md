# Berger A104 Cauchy-operator preflight

The stationary spectral receipt fixed the hybrid rank-52 second-order target
and the convention (H_{104}=iA_{104}), but it did not contain the
coefficientwise spatial differential matrix (A_{104}). This preflight
closes the part of that gap supported by portable classical inputs.

For each exact rank-20 graph companion, write

\[
C_{20}=K_2\partial_t^2+K_1\partial_t+K_0.
\]

The machine extracts the three stationary spatial matrices, proves
(\operatorname{rank}K_2=20), constructs the exact algebraic inverse of
(K_2), and emits

\[
A_{40}=
\begin{pmatrix}
0&I_{20}\\
-K_2^{-1}K_0&-K_2^{-1}K_1
\end{pmatrix}.
\]

Substitution independently reconstructs the original second-order equation.
This succeeds for

\[
A_{10}=\Box_2^2+V_2
\]

and for the separately constructed lower graph companion of

\[
A_{10}^{\sharp}=(\Box_2^{\sharp})^2+V_2^{\sharp}.
\]

The latter is deliberately the graph companion of the formal-adjoint
endpoint, not the literal matrix adjoint of the first companion. This keeps
the same high/low Sobolev ordering on both endpoints. Ten exact sparse
operator artifacts record (K_0,K_1,K_2,K_2^{-1},A_{40}) in both sectors.
Together these cover 80 of the 104 Cauchy components.

The remaining 24 components are exactly the ghost and identity sectors. The
classical theorem proves their two-factor normally-hyperbolic
factorizations, but the current portable import supplies only the theorem
statement and principal symbols. The existing endpoint contract explicitly
records these four coefficient matrices as requested but not exported:

```text
F_spatial_K_spatial
Box_1_spatial_covector
F_spatial_K_spatial_formal_adjoint
Box_1_spatial_covector_formal_adjoint
```

Reconstructing them independently in `quantum-weyl` would violate the
classical-import boundary. They are therefore the minimal missing endpoint
carrier for `ghost_A12` and `identity_A12`.

The 104 Cauchy row IDs, degrees, parity and Sobolev exponents are now frozen.
Pairing partners are not asserted: the spacetime BV pairing has not yet been
converted into the Cauchy Lagrange boundary form. Likewise, `q26` exists,
but its rank-52 companion prolongation and the induced `q_Cauchy_104` have
not been exported. Consequently neither `[A104,q_Cauchy]=0` nor Krein
skew-adjointness can yet be tested.

The closed-generator theorem is therefore not authorized yet. Once the four
endpoint factor records, companion BRST prolongation, and Cauchy boundary
form land, the full (A_{104}) can be assembled and identified on a smooth
core with the stationary evolution. Only then should domain equality,
compact resolvent, zero isolation, frequency splitting or Hadamard state
selection be attempted.

```bash
PYTHONPATH=quantum-weyl python3 -m lorentzian.berger_a104_cauchy_operator_preflight_certificate --check
PYTHONPATH=quantum-weyl python3 -m lorentzian.verify_berger_a104_cauchy_operator_preflight
PYTHONPATH=quantum-weyl python3 -m unittest quantum-weyl/lorentzian/tests/test_berger_a104_cauchy_operator_preflight.py -v
```

## Verification receipt

Recorded 2026-07-17:

- Tier 0 Python compilation, strict JSON parsing, and `git diff --check`
  passed.
- Tier 1 independently replayed the temporal split, both exact inverses, both
  rank-40 generators, all ten generated artifacts, the 104-row ledger, and
  the fail-closed mutations.
- Tier 2 regenerated the nine affected certificates in 9.9 seconds; nine
  freshness checks passed in 11.559 seconds; nine independent verifiers
  passed in 11.844 seconds; and 68 direct-consumer tests passed in 21.247
  seconds.
- Tier 3 was not run because no freeze, release, shared core-algebra change,
  or paper theorem was promoted. Full `A104`, BRST compatibility, pairing,
  closedness, spectral and Hadamard claims remain false.
