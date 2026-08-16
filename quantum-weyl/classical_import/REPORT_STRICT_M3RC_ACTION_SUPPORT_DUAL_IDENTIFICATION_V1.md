# Strict M3RC action/support dual identification

**Result:** `STRICT_M3RC_ACTION_SUPPORT_DUAL_IDENTIFICATION_V1`
**Dependencies:** `LOCAL-ALGEBRAIC`, `REDUCED-MODE`, `LORENTZIAN-CAUSAL`
**M3RC-B:** `COMPLETE_ON_REPRESENTED_ENERGIES_2_THROUGH_6`
**Gate A:** `FAIL_CLOSED`

## Result

The formal residual cotangent dual now has a classical action/support
realization.  The imported causal theorem supplies

```text
Lambda = Lambda_plus - Lambda_minus : Gamma_c(C)[1] -> Gamma_sc(C)
[u] -> [Q(chi_plus u)]
```

as mutually inverse maps on cohomology.  Because the cylinder Cauchy surface
is the compact S3, `Gamma_sc=Gamma_smooth`.  The action-derived Cauchy form,
the causal Green pairing, and the E/A/L form agree on cohomology.

For every represented positive-frequency mode `u_i`, let `s_i` be +1 in the
E family and -1 in the A or L family.  Then

```text
v_i = (-i*s_i) conjugate(u_i)
j_i = Q(chi_plus v_i)
```

is an explicit compact-source class whose causal image pairs as
`Omega_Sigma(v_i,u_j)=delta_ij`.  All 470
formal duals are identified with zero support, recovery, crosswalk, or pairing
defects.  The positive-frequency Krein inertia is
(230,
240, 0), while the suspended
940-coordinate odd pairing has exact rank
940.

## Boundary

This closes M3RC-B on the finite represented energies two through six.  It is
not a theorem about the full continuous dual of every smooth or all-energy
completion, and it does not turn the formal 8,980-coordinate source into the
unchanged authoritative classical complex.  M4R is now ready, not complete;
M1, Gate A, Hadamard and QME remain fail closed.

## Reproduction

```text
python3 quantum-weyl/classical_import/build_strict_m3rc_action_support_dual_identification.py --check
python3 quantum-weyl/classical_import/check_strict_m3rc_action_support_dual_identification.py
python3 -m unittest quantum-weyl/classical_import/tests/test_strict_m3rc_action_support_dual_identification.py
```
