# First Berger arity-two Cartan verdict

The action-derived stationary Berger block gives the first scientific
`REDUCED-MODE` arity-two verdict.  It is not a synthetic solver fixture.  The
input is the classical six-row Koszul--Tate block at

\[
q=\frac9{40},\qquad \alpha_B=5,\qquad
\lambda=\frac{119}{480},\qquad \omega=\frac34,
\]

with fields \((\delta u,\delta N,\delta\rho)\), where
\(c=c_0(1+u)\), their three equation rows,
and a nonzero action-derived \(q_2\) with 18 independent sparse coefficients.

## Exact verdict

Every declared row has \(D\)-weight zero.  Consequently the imported linear
action is \(L_D=0\), the compatible linear contraction is \(\iota_D=0\), and
the centered block has no nonlinear action coefficient \(L_D^{(2)}\).  The
existing exact Cartan engine therefore computes

\[
A_D^{(2)}=[q_2,\iota_D]-L_D^{(2)}=0,
\qquad
[q_1,\iota_D^{(2)}]=-A_D^{(2)}=0.
\]

The admissible exact primitive is

\[
\boxed{\iota_D^{(2)}=0}.
\]

This is a binary exact-primitive verdict, not an obstruction verdict.  The
zero primitive is automatically contained in every homogeneous linear
cyclicity, reality, field-support, and boundary constraint subspace on this
finite block.  No Lorentzian or causal admissibility is inferred.

The classical producer already performs the scoped rational coordinate change
\(c=c_0(1+u)\) and normalizes the action density by \(c_0\).  Both \(q_1\)
and this particular \(q_2\) consequently reach the quantum adapter over
\(\mathbb Q\).  The calculation uses the existing `Fraction` solver; it does
not widen the general PBW engine.

## Physical interpretation

The exact unary map has rank three from three degree-zero fields to three
degree-one equations, so the six-row Koszul--Tate block is acyclic.  Its
unreduced stationary Hessian has inertia \((n_+,n_-,n_0)=(1,2,0)\), but those
two negative algebraic Hessian directions do not survive as cohomology.
Thus this correction introduces **no negative physical direction**.

This block does not answer whether an interaction couples an Einstein-like
radiative branch to the extra fourth-order/Weyl branch.  The certified Berger
background is itself a non-Einstein Weyl--matter background, and the six
homogeneous rows carry no Einstein/extra-Weyl branch labels.  The applicable
answer is `NOT_APPLICABLE_AT_THIS_BASE_POINT`, not a claim of nonlinear branch
decoupling.

## Precise limitation

This result is `LOCAL-ALGEBRAIC` and `REDUCED-MODE` only.  It covers one
stationary, homogeneous, \(D\)-weight-zero, six-row action-derived block.  It
does not cover the remaining 48 gauge-fixed rows, nonzero \(D\)-weights, the
support-local polydifferential \(q_2\), radiative Einstein/Weyl branch states,
a causal or Hadamard complex, a transferred residual vertex, or a quantum
master-equation correction.  In particular, the zero source here cannot rule
out a Cartan obstruction in any omitted nonzero-weight or support-local block.

The machine-readable verdict and exact provenance are recorded in
`quantum-weyl/transfer/certificates/BERGER_FIRST_ARITY_TWO_CARTAN_VERDICT.json`.

## Verification receipt

The affected classical source chain passed in 2.84 seconds:

```bash
python3 d_quotient_classical/backreacted_clock/berger_rational_fixture_q2_d_block.py --check --guards
python3 d_quotient_classical/backreacted_clock/verify_berger_rational_fixture_q2_d_block.py
python3 -m unittest d_quotient_classical.backreacted_clock.tests.test_berger_rational_fixture_q2_d_block
```

The scoped quantum import, mutation, exact-solver, programme-ledger, and unary
regressions passed 25 tests in 33.25 seconds:

```bash
python3 -m unittest \
  quantum-weyl/transfer/tests/test_berger_rational_fixture_q2_d_import.py \
  quantum-weyl/transfer/tests/test_berger_reduced_mode_cartan.py \
  quantum-weyl/transfer/tests/test_nonlinear_transfer_certificate.py \
  quantum-weyl/transfer/tests/test_arity_two_cartan.py \
  quantum-weyl/transfer/tests/test_berger_gauge_fixed_nonminimal_import.py
```

AJV Draft 2020-12 strict validation of the unary import, reduced-mode import,
and Cartan-verdict certificates passed in 5.08 seconds.  Tier 0 Python/JSON
parse checks and `git diff --check` passed.  The affected certificate chain was
run; the repository-wide Tier 3 suite was not run because this is neither a
freeze/tag nor a change to shared core algebra.
