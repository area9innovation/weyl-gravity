# Compact-cylinder \(D\)-charge audit

## Result

The compact vacuum-cylinder verdict is **`SECTOR_DEPENDENT`**.
Compactness removes the spatial boundary and its flux; it does not by itself
make cylinder time translation a presymplectic degeneracy.

On the unrestricted algebraic linearized solution space after the local
Diff x Weyl quotient,

```text
P_lin verdict = D_CHARGED
H_D = mu_D = zbar M_D z
M_D = -(1/2) J D
```

The charge is integrable, conserved, and nonzero on smooth global modes:

| branch | energy | unit-amplitude \(H_D\) | radial \(\delta H_D\) |
|---|---:|---:|---:|
| E | 2 | -1 | -2 |
| A | 3 | 3/2 | 3 |
| L | 4 | 2 | 4 |

The unit \(E_2\) mode is the strongest compact counterexample: \(H_D=-1\)
and its unit radial variation is \(-2\).  It is **not** claimed to be tangent
to a second-order Bach-flat family.  In fact its nonzero \(D\) moment map
excludes it from the Taub zero fibre.

On the explicitly restricted formal phase space

```text
P_Taub0 = mu^{-1}(0)
```

the answer changes.  If \(i:P_{\rm Taub0}\to P_{\rm lin}\), then

\[
 i^*\iota_{X_D}\Omega_\Sigma
 =i^*d\mu_D=d(i^*\mu_D)=0.
\]

With \(H_D[0]=0\), the pulled-back charge vanishes.  Thus `D_GAUGE` holds on
the selected common fifteen-component Taub/Kuranishi zero fibre and its
derived residual quotient, not on `P_lin`.

## Declared covariant data

- Spacetime: \(\mathbb R\times S^3\), with closed oriented Cauchy surface.
- Action: \(S_{\rm red}=\int\sqrt{-g}(R_{\mu\nu}R^{\mu\nu}-R^2/3)\).
- Presymplectic convention: the action-derived metric current transported to
  \(+I_E\oplus(-I_A)\oplus(-I_L)\).
- Boundary and corners: \(\partial S^3=\varnothing\); no corner variables or
  timelike-boundary flux occur.
- Counterterms: the Euler/total-derivative convention is fixed, no boundary
  counterterm is added, and the additive normalization is \(H_D[0]=0\).

## Exact scope

This audit composes the certified covariant current comparison with the exact
all-energy E/A/L moment-map normalization.  It carries both
`REDUCED-MODE` and `LORENTZIAN-CAUSAL` dependency tags.  The reduced-mode
calculation is not used alone to infer a new Lorentzian current theorem.

It proves neither sufficiency of the quadratic Taub conditions for an exact
nonlinear solution nor a universal decision about clocks, deparametrized
sectors, or boundaries.  Those settings remain open:

- cylinder plus conformally coupled scalar clock
- cylinder plus Yang-Mills
- weakly perturbed conformally flat backgrounds
- Lorentzian dS and AdS with declared boundary conditions
- asymptotically flat spacetimes at null infinity

## Reproduction and provenance

```bash
python3 symbolic/verify_compact_cylinder_d_charge_audit.py
python3 -m unittest bridge.taub_moment_map.tests.test_compact_d_charge
```

Tier 0 and Tier 1 are the applicable test tiers.  Higher tiers are not
required because this audit changes no shared operator or previously
certified theorem input.  The recorded scoped runs took 0.57 s for the
certificate audit and 0.48 s for the unit-test command on 2026-07-15.

Imported base commit: `394743bbf36dbd4df670db4a8451d9fea66ccac8`

- `bridge/certificates/closed_universe_bfv.json`: `37eda8319d7fbe69e6b0838677b3d7fd4aecddd8b6274c281fefc2cf3f612ceb`
- `bridge/certificates/taub_moment_map.json`: `84fb8d94043f89fcd70e8fdd2940b266ea6f9006c3ff94cb55884b1b4ceb46e1`
- `bridge/taub_moment_map/all_energy.py`: `29d3549c4bdba06dc65a971e4e29f6f983554cbb7b98883c9c0882099d50c67f`
- `bridge/taub_moment_map/compact_d_charge.py`: `ea10ef431861f6b6df8cbc913b1a3ffea5c0cc5e279161dda4a9198a6b459098`
- `covariant_completion/certificates/curved_EAL_pairing_regression.json`: `ae9f0cc61bfa38e0a4b202d822ad23bcdb0d4771dbcc1914805fc53141b895b8`
- `covariant_completion/certificates/curved_current_comparison.json`: `c98211f74ae81b5b2d8acaadbd61d20e3cfa58bf0b24ef4077e29677457812bc`
- `d_quotient_classical/schema/compact-cylinder-d-charge-audit-v1.schema.json`: `ffbf472ea119480e65892d134d1dcbcf9864443e49a7b123dc19e87d059b6f75`
- `field_bv_identification/zero_modes/certificates/taub_obstruction_map.json`: `72ac747c0b15c85c75f7a86d983960f305e486c96ab594c056f9b3377cfbf540`
- `symbolic/verify_compact_cylinder_d_charge_audit.py`: `bbed90ee7fad1424dd9510418597bea5f10e903f4cb1c9d4609e5e0656347918`
