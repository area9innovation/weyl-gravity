# Classical ordinary-derivative auxiliary cubic export v1

**Result:** `CLASSICAL_ORDINARY_DERIVATIVE_AUXILIARY_CUBIC_EXPORT_V1`

## Outcome

The authoritative ordinary-derivative Weyl action has a nonzero cubic
auxiliary channel after the certified linear generalized-auxiliary split:

`L_fvv=-(1/2) f^mu nu v_mu v_nu-(1/4) tr(f) v^2`.

For the exact traceless spatial direction `f_hat^11=1`, `f_hat^22=-1` and
`v_1=1`, the density is `-1/2*t*s^2` and its mixed
polarization is **-1**.

Therefore literal zero-extension, even followed only by the recorded linear
shear, is not the authoritative nonlinear ordinary-derivative action.  This is
not a no-go for equivalence: a nonlinear auxiliary elimination or higher cyclic
L-infinity map may supply exactly the missing channel.

## Reproduction

```text
python3 d_quotient_classical/nonminimal_identity/classical_ordinary_derivative_auxiliary_cubic_export_v1.py --check
python3 d_quotient_classical/nonminimal_identity/check_classical_ordinary_derivative_auxiliary_cubic_export_v1.py
python3 d_quotient_classical/nonminimal_identity/verify_classical_ordinary_derivative_auxiliary_cubic_export_v1.py
python3 -m unittest d_quotient_classical.nonminimal_identity.tests.test_classical_ordinary_derivative_auxiliary_cubic_export_v1
```

## Boundary

This exports one decisive source interaction, not the complete nonminimal q2/q3
ledger, a causal nonlinear response, Gate A, Hadamard data, or QME restoration.
