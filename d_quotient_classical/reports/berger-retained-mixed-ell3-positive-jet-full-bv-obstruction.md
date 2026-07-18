# Berger retained mixed ell3: positive-jet full-BV obstruction

## Verdict

The mixed retained ternary representative cannot be removed through summed
pre-reduction PBW order two by the declared derivative-aware cyclic
super-cotangent redefinitions.  The obstruction occurs already on the first
associated-graded page.

The exact normalized dual witness has 22 supported coefficient rows over
`Q(sqrt(10))`.  It evaluates to `1` on the first-page residual and to `0` on
all 5,984 zero-page base-label columns and all 14,998 first-jet columns on
each of four derivative axes.  The zero-page freedom is coupled into the
solve; in particular, the earlier provisional single-coordinate witness is
not used.

## Meaning

This is the first invariant strengthening of the representative-level mixed
interaction within a declared transformation class: no admissible filtered
cyclic `F2/F3` transformation in that class removes it.  Higher positive-jet
profiles cannot repair a first associated-graded obstruction, so extending
the calculation to `q4` would not answer this gate.

The result remains `LOCAL-ALGEBRAIC`, `G0`, and full-BV retained-carrier
specific.  It does not yet identify an operation on residual cohomology,
select an Einstein-like or extra-Weyl branch, define a photon/graviton
amplitude, or establish an SDR-independent deformation class without the
declared filtered cyclic equivalence relation.

## Reproduction

```text
PYTHONPATH=. python3 d_quotient_classical/backreacted_clock/verify_berger_retained_mixed_ell3_positive_jet_full_bv_obstruction.py
PYTHONPATH=. python3 d_quotient_classical/backreacted_clock/verify_berger_retained_mixed_ell3_positive_jet_full_bv_obstruction_exhaustive.py --workers 8
PYTHONPATH=. python3 -m unittest d_quotient_classical.backreacted_clock.tests.test_berger_retained_mixed_ell3_positive_jet_full_bv_obstruction -v
npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true -s d_quotient_classical/schema/berger-retained-mixed-ell3-positive-jet-full-bv-obstruction-v1.schema.json -d d_quotient_classical/certificates/BERGER_RETAINED_MIXED_ELL3_POSITIVE_JET_FULL_BV_OBSTRUCTION_V1.json
```
