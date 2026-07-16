# All-weight Berger arity-two Cartan verdict

The finite-mode closure no-go is resolved by retaining every integer
$D$-weight.  On the algebraic direct sum of the spatially homogeneous
Berger block, $q_1$ acts weightwise, $q_2$ acts by weight convolution,
and the integer lattice is closed under addition.

The Cartan source is generically nonzero:

\[
A_D^{(2)}(x_k,y_l)=(k+l)H^{-1}C(x,y)_{k+l}.
\]

The exact binary verdict is
`ADMISSIBLE_EXACT_PRIMITIVE`.  The nonzero primitive is the first-order,
time-local, graded-cyclic operator

\[
\iota_D^{(2)}(E_k,x_l)
=-\frac{2k+l}{3}H^{-1}C(H^{-1}E,x)_{k+l},
\]

\[
\iota_D^{(2)}(E_k,F_l)
=\frac{k-l}{3}C(H^{-1}E,H^{-1}F)_{k+l},
\]

together with graded symmetry.  Its operator $D$-weight is zero: inputs
of weights $k,l$ map to weight $k+l$.  Exact symbolic calculation for
arbitrary $k,l$ proves

\[
[q_1,\iota_D^{(2)}]=-[q_2,\iota_D^{(1)}].
\]

The retained field content at every weight is
$(u_k,N_k,\rho_k;E_{u,k},E_{N,k},E_{\rho,k})$.  The Hessian is invertible,
so the algebraic direct-sum Koszul--Tate complex is acyclic weight by weight.
The primitive therefore introduces no negative physical direction.  The
unreduced Hessian signature is not being promoted to a physical spectrum.

Einstein-like versus extra-Weyl branch coupling is not applicable on this
block: the background is non-Einstein and these homogeneous metric/lapse/
clock rows carry no radiative branch labels.  This verdict neither proves
coupling nor decoupling of those radiative branches.

## Precise limitation

This is `LOCAL-ALGEBRAIC` and `REDUCED-MODE`.  It retains all temporal
integer weights but only three spatially homogeneous field/equation pairs.
It is not the full four-dimensional support-local $q_2$, not the complete
54-row Cartan contraction, and contains no causal/Hadamard data, residual
transfer, quantum correction, or `LORENTZIAN-CAUSAL` theorem.

Reproduce the pinned quantum verdict with:

```bash
python3 quantum-weyl/transfer/berger_all_weight_cartan_import_certificate.py --check
python3 -m unittest quantum-weyl/transfer/tests/test_berger_all_weight_cartan_import.py
```

## Verification receipt

The classical producer, independent verifier, three classical tests, and AJV
Draft 2020-12 strict schema validation passed in the scoped pre-import run.
The affected no-go, all-weight, import, prior Cartan, nonlinear-ledger, and
exact-solver chain then passed 37 tests in 7.47 seconds:

```bash
python3 -m unittest \
  d_quotient_classical.backreacted_clock.tests.test_berger_nonzero_weight_finite_block_no_go \
  d_quotient_classical.backreacted_clock.tests.test_berger_all_weight_arity_two_d_cartan \
  quantum-weyl/transfer/tests/test_berger_rational_fixture_q2_d_import.py \
  quantum-weyl/transfer/tests/test_berger_reduced_mode_cartan.py \
  quantum-weyl/transfer/tests/test_berger_nonzero_weight_no_go_import.py \
  quantum-weyl/transfer/tests/test_berger_all_weight_cartan_import.py \
  quantum-weyl/transfer/tests/test_nonlinear_transfer_certificate.py \
  quantum-weyl/transfer/tests/test_arity_two_cartan.py \
  quantum-weyl/transfer/tests/test_block_sparse_arity_two.py
```

The unchanged direct 54-row unary consumer passed its five tests separately
in 29.11 seconds.  Both new quantum certificates pass AJV Draft 2020-12
strict validation.  Tier 0 Python and JSON parse checks and
`git diff --check` passed.  The affected certificate chain was run; the
repository-wide Tier 3 suite was not run because this is neither a freeze/tag
nor a change to shared core algebra.
