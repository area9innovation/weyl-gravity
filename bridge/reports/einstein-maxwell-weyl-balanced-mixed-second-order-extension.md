# Balanced Einstein--extra second-order extension

Result:
`MINIMAL_BALANCED_MIXED_TANGENT_COMPLETE_SECOND_ORDER_CORRECTION_CERTIFIED`.

The generic moment-map cone first gives two complementary statements.

1. In one fixed nonzero-momentum travelling block, simultaneous vanishing of
   `H` and `P_x` forces every Einstein-plus, Einstein-minus, and extra
   occupation to vanish.  The proof uses the strict shell ordering

   ```text
   omega_minus < omega_extra < omega_plus.
   ```

2. At `k=0`, a nonzero common-zero tangent exists.  The minimal fixture uses
   the axial `ell=2,m=0` Einstein-minus representative with unit amplitude and
   the second axial extra representative with

   ```text
   |a_extra|^2=(27/52)*(5*sqrt(3)-6).
   ```

   Its `H`, `P_x`, and all three rotation moment maps vanish exactly.  This is
   additive cancellation of diagonal `q`- and `p`-primary charges; the mixed
   Lee--Wald block itself is zero.

The quadratic source of this real tangent has frequencies `0`,
`2*omega_minus`, `2*omega_extra`, and
`omega_extra +/- omega_minus`, with polar outputs only at `ell=0,2,4`.
The direct Bach--Maxwell calculation establishes:

- the Einstein and extra homogeneous zero-frequency sources cancel in all
  four independent rows;
- every nonzero-frequency homogeneous channel has an explicit correction in
  the Weyl gauge `K=U=0`;
- every `ell=2,4` channel is off both `p` and `q` shells and the stored exact
  action-Hessian inverse gives a four-component correction;
- every operator remainder is identically zero.

The completeness statement is now hardened in three additional ways.

- The certificate content-addresses the full polar tensor, physical-ring
  completion, ungauged Noether lift, and the imported polar operator engine.
- In ungauged equation order `(A,B,C,h_t,h_x,K,G,U)`, the selector for the
  four solved equations `(A,B,C,U)` stacked with the four target Noether
  identities at `k=0` has determinant `-4`.  It is therefore invertible for
  every frequency and every `lambda`, including the zero-frequency channel.
  Expanding `N(Phi)E(Phi)=0` about an on-shell background with an on-shell
  first-order tangent gives `N^(0)E^(2)=0`, so the dependent quadratic tensor
  rows follow from the four solved action rows without an integrability
  assumption.
- The real-field expansion certifies the `1/8` self-sum and `1/4` self-zero,
  cross-sum, and cross-difference factors.  Complex-conjugate reconstruction
  is explicit, and no magnetic Chern-class, electric-charge-fibre, or
  zero-frequency Wilson-line shift is introduced.

Thus the finite real sum of the stored channel corrections and their complex
conjugates is a complete `Phi^(2)` for the declared tangent.  This proves one
mixed Einstein--extra second-order extension.  It does not prove closure of
the full mixed zero locus or integrability to an exact nonlinear family.

Verification:

```text
python3 -m bridge.einstein_sector.einstein_maxwell_weyl_mixed_moment_map_zero_locus --verify bridge/certificates/einstein_maxwell_weyl_mixed_moment_map_zero_locus.json
python3 -m bridge.einstein_sector.verify_einstein_maxwell_weyl_mixed_moment_map_zero_locus
python3 -m bridge.einstein_sector.einstein_maxwell_weyl_balanced_ell0_second_order --verify bridge/certificates/einstein_maxwell_weyl_balanced_ell0_second_order.json
python3 -m bridge.einstein_sector.verify_einstein_maxwell_weyl_balanced_ell0_second_order
python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_mixed_moment_map_zero_locus bridge.einstein_sector.tests.test_einstein_maxwell_weyl_balanced_ell0_second_order
```

The exhaustive unreduced tensor replay is deliberately separate:

```text
python3 -m bridge.einstein_sector.einstein_maxwell_weyl_balanced_ell0_second_order --verify-exhaustive bridge/certificates/einstein_maxwell_weyl_balanced_ell0_second_order.json
```

It passed during production in `468.66` seconds.  The fast rail checks all
imported hashes, schema, the determinant-`-4` Noether completion, real-channel
factors, the charge/reality audit, exact ranks, the rational and single-radical
channel equations, and every stored zero remainder.  The nested-radical
cross-channel equations are replayed only on the exhaustive rail.

A trial brute-force projection of the additional vector and sphere
trace-free quadratic rows was stopped because SymPy's exact trigonometric
integration did not complete in a maintainable certificate time.  No claim
depends on that trial; dependent-row completeness is instead certified by the
exact unit-determinant Noether completion above.
