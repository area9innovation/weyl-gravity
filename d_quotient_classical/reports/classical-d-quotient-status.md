# Classical $D$-quotient challenge: handoff report

## Executive status

The compact-cylinder result is **sector-dependent** in the precise scope
recorded by the machine certificate:

- On the unrestricted locally reduced linearized solution space `P_lin`,
  $D$ has a nonzero, integrable quadratic Noether Hamiltonian. The lowest
  $E$, $A$, and $L$ branches provide exact charged examples.
- Those charged vectors do not lie in the full Taub/moment-map zero fibre and
  are obstructed as isolated tangent vectors to the selected nonlinear
  closed-universe solution space.
- On the derived full moment-map zero fibre `P_Taub0`, the pullbacks of
  $mu_D$ and $d mu_D$ vanish. Quotienting the corresponding null orbit is the
  Paper-VII closed-universe choice.

Thus compactness alone does not make $D$ gauge. The explicit
zero-charge/Taub restriction does. This conclusion is not exported to
matter-coupled, deformed, dS/AdS, or asymptotically flat phase spaces.

The compact audit composes reduced-mode data with the certified Lorentzian
current comparison and therefore carries both `REDUCED-MODE` and
`LORENTZIAN-CAUSAL`. It is not a boundary-charge theorem. The boundary and
clock challenges remain open.

## Scope and conventions

### Unrestricted linearized sector

- Field space: the $D$-finite $E/A/L$ linearized solution module after local
  Diff x Weyl reduction.
- Boundary: the closed cylinder `R x S3`; there is no spatial boundary or
  corner term.
- Hamiltonian normalization: the action-normalized kernel
  `M_D = -(1/2) J D`.
- Interpretation: a valid charge computation on `P_lin`, not proof of
  nonlinear linearizability.

### Derived Taub-zero sector

- Field space: the formal common zero fibre of all fifteen quadratic
  Taub/moment-map components, with its derived residual quotient.
- Charge: the pullback identities are `i* mu_D = 0` and
  `i* i_XD Omega = d(i* mu_D) = 0`.
- Interpretation: proper gauge only after the explicit zero-charge
  restriction and quotient.

## Compact-cylinder charge receipt

The exact all-energy branch formula and charged representatives are recorded
in the producer certificate referenced by
`CLASSICAL_D_QUOTIENT_STATUS.json`. The decisive examples are:

| branch | energy | unit-amplitude $H_D$ | radial $delta H_D$ |
|---|---:|---:|---:|
| $E$ | 2 | $-1$ | $-2$ |
| $A$ | 3 | $3/2$ | $3$ |
| $L$ | 4 | $2$ | $4$ |

They establish `D_CHARGED` on `P_lin`. The same certificate records why they
do not establish `D_CHARGED` on `P_Taub0`.

## Residual-complex comparison

| Complex | Mathematical status | Computation status | Current result |
|---|---|---|---|
| Absolute `SO(4,2)` CE complex | selected Paper-VII complex | certified baseline | centered $H^4=C^2$, one-particle $H^4=0$, Gram $I_2$ |
| $D$ global, lowering subalgebra gauged | legal closed-subalgebra comparison | partial | exact through total $D$-weight four; not a physical selection theorem |
| Zero-charge transformations `g_H=0` | closure not established | open | no complex promoted |
| Local gauge only; residual `SO(4,2)` global | zero residual differential | certified | full $E/A/L$ one-particle module survives with branch Krein signs |

Deleting only the $D$ ghost is rejected: the remaining fourteen conformal
generators are not a Lie subalgebra. The exact obstruction is the invariant
contraction of raising and lowering generators that reproduces $D$.

## Background matrix

| Setting | $D$ charge | Cartan contraction | Causal homotopy | One-particle sector | Pairing | Einstein sector |
|---|---|---|---|---|---|---|
| Vacuum cylinder | `SECTOR_DEPENDENT` on the declared sectors | certified baseline | certified baseline | zero only in selected absolute residual $H^4$ | $I_2$ on centered degree-four classes | open in this challenge record |
| Cylinder + scalar clock | `OPEN` | `OPEN` | `OPEN` | `OPEN` | `OPEN` | `OPEN` |
| Cylinder + Yang--Mills | `NOT_TESTED` | `NOT_TESTED` | `NOT_TESTED` | `NOT_TESTED` | `NOT_TESTED` | `NOT_TESTED` |
| Weakly deformed background | `NOT_TESTED` | `NOT_TESTED` | `NOT_TESTED` | `NOT_TESTED` | `NOT_TESTED` | `NOT_TESTED` |
| Lorentzian dS/AdS | `NOT_TESTED` | `NOT_TESTED` | `NOT_TESTED` | `NOT_TESTED` | `NOT_TESTED` | `NOT_TESTED` |
| Asymptotically flat | `NOT_TESTED` | `NOT_TESTED` | `NOT_TESTED` | `NOT_TESTED` | `NOT_TESTED` | `NOT_TESTED` |

The JSON certificate, rather than this prose table, is authoritative for
status promotion.

## Next gates

1. Add a conformally coupled scalar clock and compute its total improved
   charge before considering Yang--Mills.
2. Decide closure of the zero-charge transformations on the chosen sector,
   allowing a field-dependent algebroid if necessary.
3. Compute the first background-deformation obstruction and a quantitative
   stability radius.
4. Treat dS/AdS and asymptotically flat boundaries as new Lorentzian phase
   spaces, not as consequences of the compact-cylinder verdict.
5. As an optional independent check, rederive the certified compact result
   directly from the covariant presymplectic current without the
   current-to-$E/A/L$ transport.

## Verification receipts

The exact commands, elapsed times, tiers, and skipped higher-tier reasons are
stored in the machine certificate. The scoped handoff commands are:

```bash
python3 d_quotient_classical/verify_classical_status.py --guards
python3 symbolic/verify_compact_cylinder_d_charge_audit.py --check
python3 -m unittest bridge.taub_moment_map.tests.test_compact_d_charge
python3 symbolic/verify_conformal_d_global_alternatives.py --check-result
```

No full-suite result is implied by these scoped checks.
