# Classical \(D\)-quotient challenge: handoff report

## Executive status

The compact vacuum-cylinder result is **sector-dependent** on two precisely
declared phase spaces:

- On the unrestricted locally reduced linearized solution space
  \(\mathcal P_{\rm lin}\), \(D\) has a nonzero, integrable quadratic Noether
  Hamiltonian. The lowest \(E\), \(A\), and \(L\) branches provide exact
  charged examples.
- Those charged vectors do not lie in the full Taub/moment-map zero fibre and
  are obstructed as isolated tangent vectors to the selected nonlinear
  closed-universe solution space.
- On the derived full moment-map zero fibre \(\mathcal P_{\rm Taub0}\), the
  pullback of \(\mu_D\) and \(d\mu_D\) vanishes. Quotienting the corresponding
  null orbit is the Paper-VII closed-universe choice.

Thus compactness alone does not make \(D\) gauge. The zero-charge/Taub
restriction does. This conclusion is not exported to matter-coupled,
deformed, dS/AdS, or asymptotically flat phase spaces.

The first matter-clock candidate has now been resolved negatively but
constructively. For one real conformally coupled scalar, the invariant
homogeneous variable \(\chi=aT\) is an exact local oscillator clock with
positive improved charge. It is not a consistent nonzero background on the
exact vacuum cylinder: its stress tensor is nonzero while the cylinder Bach
tensor vanishes. Around the only compatible background, \(\bar T=0\), its
linearized Diff \(\times\) Weyl incidence vanishes. This obstructs that
candidate without assigning a verdict to a backreacted or composite clock.

The present charge audit composes the exact reduced-mode moment map with the
already-certified Lorentzian current comparison, so it is tagged
`REDUCED-MODE` and `LORENTZIAN-CAUSAL`. This does not classify any new
boundary phase space.

## Scope and conventions

### Unrestricted linearized sector

- Field space: the \(D\)-finite \(E/A/L\) linearized solution module after
  local Diff \(\times\) Weyl reduction.
- Boundary: the closed cylinder \(\mathbb R\times S^3\); no spatial boundary
  or corner term.
- Hamiltonian normalization: the action-normalized kernel
  \(M_D=-\tfrac12 JD\).
- Interpretation: a valid charge computation on \(\mathcal P_{\rm lin}\),
  not proof of nonlinear linearizability.

### Derived Taub-zero sector

- Field space: the formal common zero fibre of all fifteen quadratic
  Taub/moment-map components, with its derived residual quotient.
- Charge: \(\iota^*\mu_D=0\) and
  \(\iota^*\iota_{X_D}\Omega=d(\iota^*\mu_D)=0\).
- Interpretation: proper gauge only after the explicit zero-charge
  restriction and quotient.

## Compact-cylinder charge receipt

The exact all-energy branch formula and lowest charged representatives are
recorded in the producer certificate referenced by
`CLASSICAL_D_QUOTIENT_STATUS.json`. The decisive examples are:

| branch | energy | \(H_D\) at unit real amplitude | radial \(\delta H_D\) |
|---|---:|---:|---:|
| \(E\) | 2 | \(-1\) | \(-2\) |
| \(A\) | 3 | \(3/2\) | \(3\) |
| \(L\) | 4 | \(2\) | \(4\) |

They establish `D_CHARGED` on \(\mathcal P_{\rm lin}\). The same certificate
records why they do not establish `D_CHARGED` on
\(\mathcal P_{\rm Taub0}\).

## Residual-complex comparison

| Complex | Mathematical status | Computation status | Current result |
|---|---|---|---|
| Absolute \(SO(4,2)\) CE complex | selected Paper-VII complex | certified baseline | centered \(H^4=\mathbb C^2\), one-particle \(H^4=0\), Gram \(I_2\) |
| \(D\) global, lowering subalgebra gauged | legal closed-subalgebra comparison | partial | exact through total \(D\)-weight four; not a physical selection theorem |
| Zero-charge transformations \(\mathfrak g_{H=0}\) | closure not established | open | no complex promoted |
| Local gauge only; residual \(SO(4,2)\) global | zero residual differential | certified | full \(E/A/L\) one-particle module survives with branch Krein signs |

Deleting only the \(D\) ghost is rejected: the remaining fourteen conformal
generators are not a Lie subalgebra. The exact obstruction is

\[
\frac14\sum_a[K^-_a,K^+_a]=2D.
\]

## Background matrix

| Setting | \(D\) charge | Cartan contraction | Causal homotopy | One-particle sector | Pairing | Einstein sector |
|---|---|---|---|---|---|---|
| Vacuum cylinder | `SECTOR_DEPENDENT` on the declared sectors | certified baseline | certified baseline | zero only in selected absolute residual \(H^4\) | \(I_2\) on centered degree-four classes | open in this challenge record |
| Cylinder + scalar clock | one-real-scalar exact-cylinder candidate `OBSTRUCTED`; replacement phase space `OPEN` | `OPEN` | `OPEN` | `OPEN` | `OPEN` | `OPEN` |
| Cylinder + Yang--Mills | `NOT_TESTED` | `NOT_TESTED` | `NOT_TESTED` | `NOT_TESTED` | `NOT_TESTED` | `NOT_TESTED` |
| Weakly deformed background | `NOT_TESTED` | `NOT_TESTED` | `NOT_TESTED` | `NOT_TESTED` | `NOT_TESTED` | `NOT_TESTED` |
| Lorentzian dS/AdS | `NOT_TESTED` | `NOT_TESTED` | `NOT_TESTED` | `NOT_TESTED` | `NOT_TESTED` | `NOT_TESTED` |
| Asymptotically flat | `NOT_TESTED` | `NOT_TESTED` | `NOT_TESTED` | `NOT_TESTED` | `NOT_TESTED` | `NOT_TESTED` |

The JSON certificate, rather than this prose table, is authoritative for
status promotion.

## Next gates

1. Replace the obstructed one-scalar exact-cylinder candidate by a genuinely
   backreacted solution, a Weyl-invariant composite/two-field clock, or a
   separately declared reference-matter model; then compute its total charge.
2. Decide closure of the zero-charge transformations on the chosen sector,
   allowing a field-dependent algebroid if necessary.
3. Compute the first background-deformation obstruction and a quantitative
   stability radius.
4. Treat dS/AdS and asymptotically flat boundaries as new Lorentzian phase
   spaces, not as consequences of the compact-cylinder verdict.
5. Optionally reproduce the compact current-to-moment-map equivalence in an
   independent implementation; this is a cross-check, not a missing premise.

## Verification receipts

The exact commands, elapsed times, tiers, and skipped higher-tier reasons are
stored in the machine certificate. The scoped handoff commands are:

```bash
python3 d_quotient_classical/verify_classical_status.py --guards
python3 symbolic/verify_compact_cylinder_d_charge_audit.py --check
python3 -m unittest bridge.taub_moment_map.tests.test_compact_d_charge
python3 symbolic/verify_conformal_d_global_alternatives.py --check-result
python3 d_quotient_classical/scalar_clock/conformal_scalar_clock.py --check --guards
python3 -m unittest d_quotient_classical.scalar_clock.tests.test_conformal_scalar_clock
```

No full-suite result is implied by the scoped checks.
