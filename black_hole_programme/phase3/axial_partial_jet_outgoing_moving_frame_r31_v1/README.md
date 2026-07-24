# Outgoing common moving-frame checkpoint at r=31

This package reissues the certified outgoing `R/E/S` reduced checkpoint in
one analytic moving spin-two gauge.  It applies the exact first-jet
corrections

```text
Rdot_moving = Rdot_fixed + diag(0,93/4) Rbase
Sbase_common = h0 Sbase_core
Sdot_common = h0 (Sdot_fixed_core + diag(0,93/4) Sbase_Y_core)
```

with

```text
h0 = (32/31) exp(i omega (64 + 4 log 32)).
```

`h0` is retained as a typed entire zero-free analytic unit.  It is not
expanded into the rational degree-four Taylor core.  Exact coefficient
addition and outward-rounded binary64 remainder addition preserve the common
frequency generator `7315`.

The independent verifier reparses both original `R` transports and the
original `S` checkpoint, reconstructs the corrected models without using the
producer's model-operation code, verifies the triangular rank-three minor and
restart hashes, and checks the residual endpoint-normalization conditions.

Run:

```bash
python3 -m black_hole_programme.phase3.axial_partial_jet_outgoing_moving_frame_r31_v1.produce --check
python3 -m black_hole_programme.phase3.axial_partial_jet_outgoing_moving_frame_r31_v1.verify
python3 -m unittest black_hole_programme.phase3.axial_partial_jet_outgoing_moving_frame_r31_v1.test_moving_frame
python3 -m black_hole_programme.phase3.axial_partial_jet_outgoing_moving_frame_r31_v1.audit
```

The result certifies analytic first-jet `K_plus=0` in the complete moving
factor gauge on the pilot child.  It does not construct `T_plus`, a Stokes
identity, or a scattering/flux theorem.
