# Strict pure-Weyl q3 witness and source inventory v1

## Outcome

Yes for the pinned pure-Weyl metric witness, but not yet as a full authoritative import. Exact cubic differentiation of the action-normalized Bach Euler density gives 41 rational terms across all ten metric-equation rows and q1 q3=-75760/9, exactly cancelling three times the certified 75760/27 q2 Jacobiator. The full lambda-squared source is therefore q1-closed on this witness. The repository's complete Berger q3 cannot be directly imported: it belongs to Weyl gravity plus a positive clock at a fixed Berger background on a different 54-row carrier, and no same-theory cyclic carrier map is certified. Arbitrary-input full-BV q3 and its 386-row stabilization remain open.

## Exact cancellation

```text
q2(x,q2(x,x))_omega_star = 75760/27
q1(q3(x,x,x))_omega_star = -75760/9
q1 q3 + 3 q2 q2             = 0
q1 S2                        = 0
```

The cubic metric source has 41 exact rational
terms across 10 output rows.  All four
linear Diff-Noether images and the coefficient of the full nonlinear Weyl
trace identity vanish exactly.

## Why the existing complete q3 is not the strict import

| Source | Theory | Carrier | Disposition |
|---|---|---|---|
| `BERGER_SUPPORT_LOCAL_Q3` | Weyl gravity plus a positive rotating conformal clock | 54-row gauge-fixed Berger BV complex | `NO_CERTIFIED_SAME_THEORY_CARRIER_MAP` |
| `STRICT_BACH_NATURAL_OPERATOR_AST_V1` | strict pure Weyl | portable metric Euler row | `SAME_THEORY_PORTABLE_Q2_DOES_NOT_EXPORT_Q3` |
| `STRICT_PURE_WEYL_CUBIC_BACH_RECEIVER_V1` | strict pure Weyl | ten metric-equation rows of the strict 30-row endpoint | `RECEIVER_DERIVED_WITNESS_CANCELLATION_CERTIFIED` |

The Berger result remains a valid complete q3 theorem on its own declared
Weyl-plus-clock carrier.  The incompatibility decision says that no currently
certified same-theory cyclic map authorizes its use as the pure-Weyl strict
q3.  It is not a nonexistence theorem for every possible future relation.

## Reproduction

```text
python3 quantum-weyl/classical_import/build_strict_386_pure_weyl_q3_witness.py --check
python3 quantum-weyl/classical_import/check_strict_386_pure_weyl_q3_witness.py
python3 quantum-weyl/classical_import/verify_strict_386_pure_weyl_q3_witness.py
python3 -m unittest quantum-weyl/classical_import/tests/test_strict_386_pure_weyl_q3_witness.py -v
```

## Boundaries

- This does not establish an authoritative arbitrary-input pure-Weyl q3 export.
- This does not establish the ghost, antifield, nonminimal, auxiliary, residual, or full 386-row q3 components.
- This does not establish the general arity-three L-infinity identity beyond the pinned diagonal metric witness.
- This does not establish general lambda-squared or all-order nonlinear source closure.
- This does not establish nonexistence of a future Berger-to-pure-Weyl relation; only the absence of a currently certified same-theory map is asserted.
- This does not establish q3 compatibility with retarded or advanced Green actions.
- This does not establish a passed classical import gate, analytic Moller map, Hadamard state, renormalized products, QME restoration, residual transfer, or Lorentzian quantum theory.
