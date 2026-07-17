# Berger retained observer K-descent gate

## Result

The exact two-detector Maxwell transfer remains a valid rank-two probe-limit
baseline, but it is **not yet a typed observable cocycle of the retained
36-row gravity-clock-Maxwell complex**.

The obstruction is structural, not a failed coefficient fit.  The record
functional depends on six detector-indexed rods and four memory/multiplier
fields.  Those ten fields and their ten cyclic partners are absent from the
retained complex.  Moreover, the global rods are neutral under the clock's
internal rotation, so their Berger generator action is

\[
K R_{aI}=(D-\omega R_{\rm internal})R_{aI}=D R_{aI}.
\]

At time offset \(1/96\), inside each detector's physical half-width \(1/48\),
the first rod has the exact nonzero value

\[
-\frac{\sqrt{58}}6\frac{3\sqrt{10}}{10}\cos(\varphi_a)
 \sin\!\left(\frac{\sqrt{58}}{576}\right)<0,
\]

with \(\varphi_0=\sqrt{10}/12\) and
\(\varphi_1=\sqrt{10}/6\).  Freezing the rods therefore drops genuine terms
from the \(K\)-variation of both the detector smearing and the composite
polarization \(d\Theta\wedge dR^a\).

## Scope

This is not a no-go theorem for the observer programme.  It identifies the
next exact gate: construct the action-derived cyclic 84-row unary complex,
pairing, Berger \(K\)-action, and causal homotopy, then replay the observer
evaluation as a chain morphism.  The already-certified rank-two probe
transfer and global rod solutions remain useful inputs to that construction.

## Replay

```bash
python3 closed_universe_observers/generate_berger_retained_observer_k_descent_gate.py
python3 closed_universe_observers/verify_berger_retained_observer_k_descent_gate.py
pytest -q closed_universe_observers/tests/test_berger_retained_observer_k_descent_gate.py
```
