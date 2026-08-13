# Certified BT finite-corner state-to-probability interface

**Result:** `FOUNDATIONAL_BT_CORNER_BORN_INTERFACE_V1`

**Lifecycle:** `SUFFICIENCY_PROVED`

**Dependency tags:** `LOCAL-ALGEBRAIC`, `REDUCED-MODE`

## Result

Yes, conditionally and exactly on the finite detector ideal. The state-representation source and the Born theorem use the identical normalized corner functional omega_P(T)=Tau(PTP)/Tau(P). For a finite J-even incoming projection P_in, a cross-Krein isometry S, an exhaustive finite output partition P_i, and the certified weak-ghost decomposition, the event map sends P_i to E_i=(P_i S P_in)^sharp(P_i S P_in). The same omega_P_in evaluates p_i=Tau(E_i)/Tau(P_in); the imported theorem proves p_i>=0 and sum_i p_i=1. An independent rational witness gives (9/25,16/25,0). The relation is a CONDITIONAL_BRIDGE between the algebraic state-representation and Krein probability-rule cells, not an identification of their full carriers or an unconditional rule for arbitrary processes.

This closes one precise cross-cell interface:

```text
CLASSICAL_STANDARD × ALGEBRAIC_CSTAR × STATE_REPRESENTATION
             -- CONDITIONAL_BRIDGE -->
CLASSICAL_STANDARD × KREIN_INDEFINITE × PROBABILITY_RULE
```

## Why it is genuinely the same state

The shared-object ledger pins the carrier, semifinite trace, incoming
projection, and normalized corner functional on both sides. The target does
not introduce a second expectation functional: it evaluates every event effect
with the source state `omega_P_in`.

For `A_i=P_i S P_in`, the bridge is

```text
E_i=A_i^sharp A_i=P_in S^sharp P_i S P_in
p_i=omega_P_in(S^sharp P_i S)=Tau(E_i)/Tau(P_in).
```

The weak-ghost argument is re-derived under five explicit hypotheses. The
independent exact witness gives probabilities
`(9/25, 16/25, 0/1)`, summing to one.
A second exact fixture retains a nonzero weak null remainder while all null and
cross traces vanish and the public weight remains `18/25`.

## Why the relation is conditional

The state exists for every finite nonzero corner, but arbitrary Krein process
effects need not be positive. Cross-Krein isometry, an exhaustive finite output
partition, paired-domain preservation, and weak ghost orthogonality are real
extra hypotheses. The certified relation is therefore `CONDITIONAL_BRIDGE`,
not `IDENTICAL_OBJECT` or an unconditional generalized Born theorem.

## Predecessor provenance audit

The legacy semifinite certificate's verifier currently fails its input-hash rail
because the narrative embedding note evolved after the certificate was issued.
Its three mathematical/work-item inputs still match. This result records that
failure rather than calling it a pass, and independently re-derives the algebraic
interface and both exact fixtures. It does not repair or relock the predecessor.

## Verification

```text
python3 foundations/build_bt_corner_born_interface.py --check
python3 foundations/check_bt_corner_born_interface.py
python3 foundations/verify_bt_corner_born_interface.py
python3 -m unittest foundations.tests.test_bt_corner_born_interface
```

## Boundaries

- This does not establish a probability rule for arbitrary Krein operators without the five displayed hypotheses.
- This does not establish identity of the full algebraic C* and Krein carriers.
- This does not establish a canonical choice of the finite incoming projection.
- This does not establish a thermodynamic normal state or finite trace of the identity.
- This does not establish the nonlinear Bateman-Turok Eq. (19), a complete NLO probability, or an all-order process.
- This does not establish a gravitational, BV-BRST, QME, residual-transfer, or LORENTZIAN-CAUSAL result.
- This does not establish empirical agreement or a complete physical theory.
- This does not establish repair or successful replay of the predecessor certificate's stale narrative-note provenance pin.
