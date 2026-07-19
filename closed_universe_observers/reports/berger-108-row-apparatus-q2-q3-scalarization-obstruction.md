# Berger 108-row apparatus q2/q3 scalarization obstruction

The activated scalar interaction lift is fail-closed at its first unavailable map. The completed 108-row unary differential is certified on the pinned Berger background quotient, and the old apparatus and emitter certificates retain their action-level interaction identities. They do not, however, supply the nonlinear Weyl/temporal clock coordinate map used by the newly repaired scalar unary.

This matters before any component expansion. If a formal coordinate map has identity linear part and a quadratic coefficient `F2`, then it leaves `q1` unchanged while changing `q2` by `[q1,F2]`. On the exact two-term fixture `q1(e)=f`, `F2(e,e)=e` changes `q2(e,e)` by `f`. Holding `F2` fixed but changing `F3(e,e,e)` similarly changes `q3(e,e,e)` by `f`. Thus unary agreement cannot select the missing scalar interactions.

The result is `NO_CERTIFIED_MAP`, not a no-go theorem. The next gate is to derive and serialize the action-normalized same-background nonlinear clock canonical map through `F3`, including the signed-pairing cotangent lift. Only then may the generated scalar `q2/q3` payloads be tested against the arity identities, `K_Berger` equivariance, observer-morphism stability, and the detector restriction to the second-order cone.

Verification:

```text
python3 -m closed_universe_observers.generate_berger_108_row_apparatus_q2_q3_scalarization_obstruction --check
python3 -m closed_universe_observers.verify_berger_108_row_apparatus_q2_q3_scalarization_obstruction
pytest -q closed_universe_observers/tests/test_berger_108_row_apparatus_q2_q3_scalarization_obstruction.py
```
