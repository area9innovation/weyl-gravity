# Strict 386-row operator portability audit v1

## Outcome

The operator gate must split by mathematical type. The endpoint q1 is already a portable finite jet table. The full q1, H_alg, projectors, inclusion and projection are exact and executable in current producers, but only their formulas, summaries and hashes cross the certificate boundary; they need finite sparse component or jet tables. Advanced and retarded Green homotopies are nonlocal analytic maps. The current causal theorem and its support/adjoint transfer remain valid, but no receiver-executable kernel, convergent name or represented action is serialized. Asking for a finite Green coefficient table is therefore the wrong contract. The next route is: serialize full local q1 first, serialize H_alg/i/p second, then import an analytic endpoint Green action on declared represented spaces and assemble the full action. Gate A, local D, q2, Hadamard and QME remain fail closed.

## Why there are two serialization problems

A local differential operator is determined by finitely many component jet coefficients on the fixed background. A Green operator is nonlocal: portability requires a represented action, convergent name, or distribution kernel together with its topology and causal-support theorem. A finite jet table is not an honest representation of that object.

## Operator inventory

| object | mathematical type | current state | decisive missing artifact |
|---|---|---|---|
| `ENDPOINT_Q1_30` | `FINITE_COMPONENT_JET_TABLE` | `PORTABLE_COMPONENT_BYTES` | none |
| `FULL_Q1_386` | `FINITE_COMPONENT_JET_TABLE` | `PRODUCER_COEFFICIENTWISE_COMPLETE_RECEIVER_TABLE_ABSENT` | one receiver-readable 386-row sparse jet table |
| `H_ALG_AND_PROJECTORS_386` | `FINITE_SPARSE_COMPONENT_MAP` | `EXACT_EXECUTABLE_AND_HASHED_RECEIVER_TABLE_ABSENT` | 386-row H_alg, P_alg and P_end entry tables |
| `ENDPOINT_INCLUSION_PROJECTION_386_30` | `FINITE_SPARSE_COMPONENT_MAP` | `EXACT_EXECUTABLE_AND_HASHED_RECEIVER_TABLE_ABSENT` | 386-by-30 inclusion and 30-by-386 projection entry tables |
| `ENDPOINT_GREEN_PLUS_MINUS_30` | `ANALYTIC_GREEN_ACTION` | `THEOREM_CHARACTERIZED_PORTABLE_ACTION_ABSENT` | represented endpoint source and target spaces |
| `FULL_GREEN_PLUS_MINUS_386` | `ANALYTIC_GREEN_ACTION` | `THEOREM_CHARACTERIZED_PORTABLE_ACTION_ABSENT` | portable endpoint Green action |

## What is already portable

The endpoint q1 has **80** exact arrow tables, **619** nonzero coefficients and all **700** Bach four-jet columns checked. The 386-row basis and pairing are separately portable.

## What is exact but trapped behind producer hashes

The full q1 and local SDR maps are executable and exact in the existing classical producers. Their certificates expose formulas and content hashes, not row/column coefficient entries. Re-running those producers is reproduction; it does not give the quantum receiver a stable input object.

## What remains analytic

The endpoint and full Green homotopies have theorem-level causal, support and adjoint transfer. The causal transfer theorem remains valid; this audit does not revoke it. It records the narrower fact that an independent receiver cannot apply or inspect the advanced/retarded maps from the current JSON artifacts alone.

## Ranked route

1. `STRICT_386_FULL_Q1_JET_TABLE` — Every source calculation exists; the receiver table and common digest are the missing objects.
2. `STRICT_386_LOCAL_SDR_COMPONENT_MAPS` — H_alg, P_alg, P_end, i_end and p_end are exact executable local maps and can be emitted without solving a new PDE.
3. `STRICT_ENDPOINT_ANALYTIC_GREEN_ACTION` — The theorem exists, but portability requires represented spaces and an action/kernel object rather than another finite matrix.
4. `STRICT_FULL_GREEN_COMPONENT_ACTION_REPLAY` — Assemble only after the local maps and endpoint action share the fixed 386-row convention.

## Reproduction

```text
python3 quantum-weyl/classical_import/build_strict_386_operator_portability_audit.py --check
python3 quantum-weyl/classical_import/check_strict_386_operator_portability_audit.py
python3 quantum-weyl/classical_import/verify_strict_386_operator_portability_audit.py
python3 -m unittest quantum-weyl/classical_import/tests/test_strict_386_operator_portability_audit.py
```

## Boundaries

- This does not establish portable full q1, H_alg, projector, inclusion or projection component tables.
- This does not establish a receiver-executable endpoint or full advanced/retarded Green action or distribution kernel.
- This does not establish that the existing causal Green-homotopy theorem is false or incomplete as an existence theorem.
- This does not establish componentwise replay of every homotopy, projector and suspended-adjoint identity.
- This does not establish the weakest foundational base for the imported analytic Green theorem.
- This does not establish a passed Gate A, local D, q2 compatibility, Hadamard state, Ward theorem, QME restoration or Lorentzian quantum theory.

## Next gate

Emit one canonical full-q1 finite component jet table on the fixed 386-row basis from the existing generalized-auxiliary, curvature-cylinder and endpoint producers. Independently reconstruct q1 and replay q1 squared and pairing adjointness before serializing the local SDR maps. Treat Lambda_plus/minus under the separate ANALYTIC_GREEN_ACTION contract.
