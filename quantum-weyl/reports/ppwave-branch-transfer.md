# Restricted support-local Einstein/extra-Weyl transfer

The pinned Brinkmann pp-wave theorem supplies the first arbitrary-profile,
branch-labelled support-local interaction block.  Its exact Bach equation is

\[
B_{uu}=-\frac14\Delta_\perp^2H,
\]

with no nonlinear dependence on $H$.  The block contains harmonic
Ricci-flat Einstein profiles and biharmonic, non-harmonic extra-Weyl profiles.

Because the restricted classical $q_2$ vanishes before projection, the
transferred bracket is independent of the contraction homotopy:

\[
\ell_2=\pi_{\rm cl}q_2(\iota_{\rm cl}\otimes\iota_{\rm cl})=0.
\]

The complete branch table on this aligned sector is therefore

| Inputs | Einstein output | Extra-Weyl output |
|---|---:|---:|
| Einstein, Einstein | 0 | 0 |
| Einstein, extra Weyl | 0 | 0 |
| extra Weyl, extra Weyl | 0 | 0 |

Thus the two actual metric branches close together on this sector, and
$\ell_2$ does not regenerate a negative direction.  The sign of the
already-present extra-Weyl branch is not classified.

This is a restricted `LOCAL-ALGEBRAIC` support-local theorem, not the complete
BV $q_2$ or 54-row transfer.  It does not classify nonaligned interactions,
the centered $W_+^2/W_-^2$ deformation classes, one-particle cohomology,
causal propagation, scattering, or quantum corrections.

Reproduce with:

```bash
python3 quantum-weyl/transfer/ppwave_branch_transfer_import_certificate.py --check
python3 -m unittest quantum-weyl/transfer/tests/test_ppwave_branch_transfer_import.py
```

## Verification receipt

On 2026-07-16, the pinned bridge producer and guard rail passed in 0.91 s,
and its independent curvature verifier passed in 0.79 s.  The quantum
certificate check passed in 0.43 s; the pp-wave import and nonlinear-ledger
test modules ran eight tests in 0.73 s; the affected nonlinear bootstrap
certificate passed in 0.05 s; and AJV's strict Draft 2020-12 validation passed
in 1.40 s.  Python compile, JSON parse, and scoped diff checks are the Tier 0
rail.  Tier 3 was not run because this imports a content-addressed restricted
block and does not change shared core algebra, promote a lifecycle state, or
claim a freeze/release theorem.
