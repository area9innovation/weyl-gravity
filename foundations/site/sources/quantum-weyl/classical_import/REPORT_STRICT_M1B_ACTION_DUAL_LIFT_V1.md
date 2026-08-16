# Strict M1B action-derived dual lift

**Result:** `STRICT_M1B_ACTION_DUAL_LIFT_V1`
**Lifecycle:** `CLASSIFIED`
**Dependency tags:** `LOCAL-ALGEBRAIC`, `REDUCED-MODE`, `LORENTZIAN-CAUSAL`

## Result

The primal M1B composite has a unique action-derived dual lift on represented
energies two through six.  The rank-386 local
BV density pairing and rank-940 residual
action pairing force

```text
q_dual_comp    = -q_comp^sharp
iota_dual_comp =  pi_comp^sharp
pi_dual_comp   =  iota_comp^sharp
s_dual_comp    = -s_comp^sharp
```

All 470 residual dual coordinates match the
frozen M1A rows and their explicit compact-source representatives with zero
support, crosswalk, pairing, or adjoint-uniqueness defects.  The independent
finite verification core contains 4,080
dual test coordinates and replays all normalized dual contraction identities
with zero defects.

## Boundary

The 4,080-coordinate algebraic-dual core is a verification device, not a new
authoritative source carrier.  This result identifies the 470 residual dual
inclusion classes with compact sources; it does not claim that every functional
on the verification core has such a representative, nor does it construct an
all-energy continuous dual.  The rank-940 typed cyclic replay remains the final
M1B subpackage.  M1C, Gate A, nonlinear Green compatibility, Hadamard data,
renormalized products, QME restoration, and residual transfer remain open.

## Reproduction

```text
python3 quantum-weyl/classical_import/build_strict_m1b_action_dual_lift.py --check
python3 quantum-weyl/classical_import/check_strict_m1b_action_dual_lift.py
python3 -m pytest -q quantum-weyl/classical_import/tests/test_strict_m1b_action_dual_lift.py
```
