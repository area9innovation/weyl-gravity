# Classical Berger retained-layout registration receipt

Date: 2026-07-15

The cross-programme dossier imports the committed
`BERGER_RETAINED_MINIMAL_LAYOUT` certificate from commit `46d95a1f`.  The
registered verdict is `RETAINED_MINIMAL_LAYOUT_FROZEN` on the existing
`positive_berger_fixed_coupling_linearized_solutions` phase space, with
dependency tag `LOCAL-ALGEBRAIC`.

The registration freezes the 26 retained minimal rows, degrees, bundle types,
pairings, allowed `q1` blocks, support rules, and differential-order ceilings.
It does not promote any retained coefficient, nonminimal row, stability
result, Green homotopy, or nonlinear operation.  The next gate is
`BERGER_RETAINED_MINIMAL_OPERATOR`.

Verification:

```bash
python3 d_quotient_programme/verify_programme_status.py --check --guards
```
