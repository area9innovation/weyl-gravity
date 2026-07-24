# Outgoing S common-generator remainder

This package repairs the precise serialization gap left by the outgoing
frame-completion preflight. It imports the already validated all-order XI3
column at `r=32`, applies the exact old-to-factor map and

```text
S = i XI3 / (2 omega),
```

and reissues the result in generator `7315` as
`IvTaylor4_omega tensor partial dual_tau`.

The exact degree-four factor head is retained. One common interval remainder
contains the difference between that head and the validated all-order XI3
hull. The dual base is `(Y,Z)` and its tangent is `(X,0)`, so the spin-one
tangent component is exactly zero.

This is an endpoint export only. It does not transport `S` inward, certify a
joint `(E,R,S)` frame, validate `K_plus`, or construct `T_plus`.

Run:

```bash
python3 -m black_hole_programme.phase3.axial_partial_jet_outgoing_splus_common_remainder_v1.produce
python3 -m black_hole_programme.phase3.axial_partial_jet_outgoing_splus_common_remainder_v1.produce --check
python3 -m black_hole_programme.phase3.axial_partial_jet_outgoing_splus_common_remainder_v1.verify
python3 -m unittest -v black_hole_programme.phase3.axial_partial_jet_outgoing_splus_common_remainder_v1.test_remainder
```
