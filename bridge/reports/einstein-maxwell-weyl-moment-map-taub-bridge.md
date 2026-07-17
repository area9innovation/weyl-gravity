# Weyl–Maxwell moment-map/Taub bridge

Result:
`COVARIANT_MOMENT_MAP_TAUB_BRIDGE_AND_GENERIC_EXTRA_FIXED_BUNDLE_NO_GO_CERTIFIED`.

For an infinitesimal automorphism `X` of the compactified Plebański–Hacyan
background, the closed-slice covariant Hamiltonian identity gives

```text
<zeta_X,(1/2)D^2 E_WM[u,u]>
  = mu_X(u)
  = (1/2) Omega_WM(u,L_X u).
```

The proof differentiates the action Noether current twice, uses the linear
equations and background stabilizer condition, and integrates over the closed
slice `S1 x S2`.  Exact Lee–Wald improvements and bundle-patching corner terms
therefore integrate to zero.

The repository sign and real-mode normalization are fixed independently by
three direct tensor calculations at `ell=2,k=0`:

- the two-dimensional axial extra block;
- the Einstein-minus axial mode;
- the Einstein-minus polar mode.

All three equal the prediction from the directly normalized Lee–Wald current.
For `Phi=Re(c exp(-i omega t))`, the time-translation formula is

```text
mu_H=-(L N_ell_m/4) omega^2 c^dagger G c.
```

The corresponding generic formulas are

```text
mu_Px=(L/4) k omega c^dagger(G tensor W_ell)c,
mu_Ja=(L/4) omega c^dagger(G tensor W_ell T_a)c.
```

The complete covariant sum sharpens the raw Clebsch–Gordan preflight:
rotations preserve `ell` because they commute with the sphere Laplacian.
`J_1,J_2` connect only `m` to `m+/-1` within the same `ell`; `J_3` is
diagonal.  The Einstein `q`-primary and extra `p`-primary blocks remain
orthogonal.

Both generic axial and polar extra `p`-primary Gram matrices are positive
definite, while

```text
omega_e^2=k^2+lambda-2/3>0.
```

Consequently `mu_H` is negative definite on every nonzero real pure-extra
generic tangent.  On the fixed compact magnetic bundle, the harmonic magnetic
correction is forbidden topologically and electric variation cannot remove
this component at the purely magnetic background.  Therefore

```text
no nonzero real pure-extra generic tangent extends to second order
within the declared fixed-bundle Weyl–Maxwell phase space.
```

This is a linearization-stability theorem, not removal of the certified linear
solutions.  Mixed Einstein–extra configurations can potentially cancel the
indefinite Einstein contribution and remain open.  Exceptional/Jordan,
charge-varying, residual-quotient, causal, particle, and quantum questions are
also open.

Verification:

```text
python3 -m bridge.einstein_sector.einstein_maxwell_weyl_moment_map_taub_bridge --verify bridge/certificates/einstein_maxwell_weyl_moment_map_taub_bridge.json
python3 -m bridge.einstein_sector.verify_einstein_maxwell_weyl_moment_map_taub_bridge
python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_moment_map_taub_bridge
```

Tier 0 completed in `0.09` seconds and the scoped Tier-1 rail in `2.90`
seconds, both `PASS`.  No content-addressed upstream action, current, tensor,
stabilizer, or charge-fibre input changed, so Tier 2 was not required.  Tier 3
was not run because the mixed and exceptional/global gates remain open and no
release, causal, or quantum lifecycle state is promoted.
