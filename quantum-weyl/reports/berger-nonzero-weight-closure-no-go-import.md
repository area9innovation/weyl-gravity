# Berger finite nonzero-weight closure no-go import

The pinned classical result at commit `74125e01` decides the proposed finite
nonzero-$D$-weight extension before the Cartan equation can be posed.  On
the rational Berger action block, the cubic square map

\[
Q(x)=q_2(x,x):\mathbb C^3\longrightarrow\mathbb C^3
\]

is anisotropic over both \(\mathbb R\) and \(\mathbb C\).  Thus every
nonzero field mode of weight \(w\) has a nonzero equation output at weight
\(2w\).  Cyclic nondegeneracy then forces a field at weight \(-2w\), and
iteration produces the unbounded sequence

\[
w,-2w,4w,-8w,\ldots.
\]

Hence no finite, pairing-nondegenerate, nonzero-weight mode block can be
closed under the action-derived $q_2$.  The first candidate with weights
$(-1,0,+1)$ leaks at weight $+2$:

\[
q_2(u_{+1},u_{+1})=
\frac{27}{80}E_{u,+2}-\frac{27}{20}E_{N,+2}
+\frac9{80}E_{\rho,+2}.
\]

The exact normalized dual leakage witness is
\((80/27,0,0)\).  This is a closure witness in the missing output space,
not a Cartan-cohomology obstruction witness.  In particular, it would be
incorrect to feed a projected subset of these channels into the Cartan
solver and call the resulting primitive an admissible finite-block verdict.

The result is `LOCAL-ALGEBRAIC` and `REDUCED-MODE` only.  It neither rules
out nor constructs the infinite all-weight completion, and it supplies no
full support-local $q_2$, local $D$-equivariance, Lorentzian causal
structure, residual transfer, or quantum correction.  This no-go identified
the two honest continuations.  The subsequent
[all-weight Cartan verdict](berger-all-weight-arity-two-cartan-import.md)
completes the homogeneous integer-weight route.  The remaining gate is the
full support-local `classical_binary_q2` and `D_action_cl` on the 54-row
complex.

Reproduce the pinned quantum import with:

```bash
python3 quantum-weyl/transfer/berger_nonzero_weight_no_go_import_certificate.py --check
python3 -m unittest quantum-weyl/transfer/tests/test_berger_nonzero_weight_no_go_import.py
```

## Verification receipt

The exact no-go, pinned import, prior reduced-mode Cartan verdict, nonlinear
programme ledger, arity-two solver, and block-sparse rail passed 30 tests in
5.59 seconds.  The direct 54-row unary consumer passed its five tests
separately in 29.11 seconds:

```bash
python3 -m unittest \
  d_quotient_classical.backreacted_clock.tests.test_berger_nonzero_weight_finite_block_no_go \
  quantum-weyl/transfer/tests/test_berger_rational_fixture_q2_d_import.py \
  quantum-weyl/transfer/tests/test_berger_reduced_mode_cartan.py \
  quantum-weyl/transfer/tests/test_berger_nonzero_weight_no_go_import.py \
  quantum-weyl/transfer/tests/test_nonlinear_transfer_certificate.py \
  quantum-weyl/transfer/tests/test_arity_two_cartan.py \
  quantum-weyl/transfer/tests/test_block_sparse_arity_two.py
python3 -m unittest \
  quantum-weyl/transfer/tests/test_berger_gauge_fixed_nonminimal_import.py
```

AJV Draft 2020-12 strict validation of the new quantum certificate passed.
Tier 0 Python and JSON parse checks and `git diff --check` passed.  The
affected certificate chain was run; the repository-wide Tier 3 suite was not
run because this change neither freezes a classical/quantum release nor
changes shared core algebra.
