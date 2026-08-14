# Strict support-local q2/D readiness audit v1

**Result:** `STRICT_SUPPORT_LOCAL_Q2_D_READINESS_V1`

**Lifecycle:** `CLASSIFIED`

## Outcome

No existing artifact closes M2, but the deficit is substantially narrower than an unknown interaction. The strict minimal master action is fixed, and an earlier all-energy audit declares a complete six-role action-defined q2 ansatz with maximum metric derivative order four and the correct support-intersection rule. What is absent is the portable component payload: no receiver-evaluable tensor-natural AST, complete component hashes, or independent q1q2, D-derivation and cyclicity replay exists. Five rows are gauge-algebra or cotangent-lift serialization tasks. The unique hard coefficient kernel is the metric-antifield row, which contains the polarized second variation of the Bach equation together with cotangent Diff/Weyl terms. The full local D action is also absent; a raw-D result on a selected finite intrinsic carrier is only a control. Separately, the known rank-64 E_5 obstruction rules out an SO(4,2)-equivariant SDR from the all-energy causal source to the old weights-2,3,4 receiver. It does not obstruct support-local q2 on the all-energy carrier. The correct route is therefore to export q2 and D on an all-energy rapid-decay or support-local carrier first, and only then build a compatible completed time-slice receiver.

## Six output rows

| Symbol | Role | Portable status | Remaining work |
|---|---|---|---|
| `c_mu` | Diff ghost | `NOT_COMPONENT_SERIALIZED` | Serialize the displayed gauge-algebra or cotangent-lift term with exact factorial and sign conventions in the receiver AST. |
| `omega` | Weyl ghost | `NOT_COMPONENT_SERIALIZED` | Serialize the displayed gauge-algebra or cotangent-lift term with exact factorial and sign conventions in the receiver AST. |
| `h_mu_nu` | metric | `NOT_COMPONENT_SERIALIZED` | Serialize the displayed gauge-algebra or cotangent-lift term with exact factorial and sign conventions in the receiver AST. |
| `hstar_mu_nu` | metric antifield/equation | `HARD_COEFFICIENT_KERNEL_OPEN` | Serialize the polarized second Bach variation together with the metric-antifield cotangent Diff/Weyl action in a receiver-evaluable tensor-natural AST. |
| `cstar_mu` | Diff-ghost antifield/identity | `NOT_COMPONENT_SERIALIZED` | Serialize the displayed gauge-algebra or cotangent-lift term with exact factorial and sign conventions in the receiver AST. |
| `omegastar` | Weyl-ghost antifield/identity | `NOT_COMPONENT_SERIALIZED` | Serialize the displayed gauge-algebra or cotangent-lift term with exact factorial and sign conventions in the receiver AST. |

Five rows are primarily exact serialization of gauge-algebra or cotangent-lift
terms already named by the master action.  The metric-antifield row is the
coefficient-heavy kernel because it contains the polarized second Bach
variation through fourth metric-jet order.

## Seven receiver gates

| Check | Current status | Why |
|---|---|---|
| `q1_squared_zero` | `SCOPED_VERIFIED_INPUT` | The exact finite minimal chain and all-energy causal unary complex are existing controls; the future common payload must still replay its own q1 bytes. |
| `q1_q2_arity_two_nilpotency` | `NOT_COMPUTED_FOR_PORTABLE_STRICT_PAYLOAD` | No strict component payload exists on which the receiver can evaluate the arity-two master identity. |
| `q2_koszul_symmetry` | `TAYLOR_CONVENTION_DECLARED_NOT_REPLAYED` | The action source declares q2=(1/2)D^2Q, but no receiver checks the serialized polarized components. |
| `q2_row_completeness` | `SOURCE_ANSATZ_DECLARED_PAYLOAD_ABSENT` | All six minimal output roles are named, but complete component ledgers and hashes are absent. |
| `D_q1_commutator_zero` | `NOT_COMPUTED_ON_FULL_LOCAL_CARRIER` | Raw D is controlled on a selected intrinsic finite carrier, not on every local field, ghost and antifield row. |
| `D_q2_derivation` | `NOT_COMPUTED` | Neither a complete strict q2 payload nor the matching full local D action is available. |
| `BV_cyclicity_q2` | `ACTION_DERIVED_EXPECTED_NOT_REPLAYED` | The BV master action fixes a canonical cyclic origin, but the receiver has no component payload and pairing on which to replay cyclicity. |

## The obstruction belongs to the receiver, not q2

At energy five the all-energy source has a two-chirality `E` cohomology block
of dimension **64**, while the old selected receiver has dimension
**0** there.  Any equivariant SDR into that receiver has defect rank at
least **64**.  This failure occurs at unary order and does not obstruct a
support-local `q2` on the all-energy carrier.

## Next executable cut

1. **`STRICT_Q2_KINEMATIC_AND_COTANGENT_COMPONENT_AST`** — Serialize the five non-Bach output rows with exact local tensor operations, signs, factorial convention, complete row ledgers and hashes.
2. **`STRICT_POLARIZED_SECOND_BACH_VARIATION`** — Derive and serialize the metric-antifield D^2 Bach kernel through fourth metric-jet order, separately from the gauge-cotangent terms.
3. **`STRICT_FULL_LOCAL_D_ACTION`** — Serialize raw D on the same all-energy field/ghost/antifield carrier and distinguish it from compact weights and Berger K.
4. **`STRICT_Q2_D_INDEPENDENT_RECEIVER`** — Replay q1q2=0, Koszul symmetry, row completeness, [D,q1]=0, D derivation and BV cyclicity on the exact exported bytes.
5. **`ALL_ENERGY_COMPLETED_TIME_SLICE_RECEIVER`** — Only after the local export, construct a rapid-decay/Sobolev all-energy receiver retaining E_n for every n>=2 and the corresponding A/L towers.

## Reproduction

```text
python3 quantum-weyl/classical_import/build_strict_support_local_q2_d_readiness.py --check
python3 quantum-weyl/classical_import/check_strict_support_local_q2_d_readiness.py
python3 quantum-weyl/classical_import/verify_strict_support_local_q2_d_readiness.py
python3 -m unittest quantum-weyl/classical_import/tests/test_strict_support_local_q2_d_readiness.py
```

## What this does not establish

- a portable strict support-local q2 component payload.
- the polarized second variation of the Bach equation.
- a full local D action or D-Cartan homotopy.
- any of the six interaction-side receiver identities.
- an obstruction to strict support-local q2 on the all-energy carrier.
- an all-energy completed time-slice receiver or residual SDR.
- a passed classical import gate, Hadamard state, QME restoration or Lorentzian quantum theory.
