# Berger Hadamard lift and zero-mode preflight

The complete 54-row gauge-fixed complex does not require an independent
Hadamard construction on all rows. The certified causal contraction has

\[
\Lambda_{54}^{\pm}
=S_{\rm cl}+\iota_{\rm cl}\Lambda_{26}^{\pm}\pi_{\rm cl}.
\]

The same algebraic homotopy occurs for both support choices, hence

\[
\Delta_{54}
=\iota_{\rm cl}\Delta_{26}\pi_{\rm cl}.
\]

Consequently a retained covariance lifts canonically as

\[
\omega^+_{2,54}
=\iota_{\rm cl}\omega^+_{2,26}\pi_{\rm cl}.
\]

Cyclicity of the contraction transfers its graded antisymmetric part, and
the two chain-map identities transfer both BRST Ward equations. Since the
inclusion and projection are finite-order support-local differential maps,
they introduce no new wavefront directions. The 28 algebraically
contractible rows therefore add no independent singular covariance.

The actual gauge-fixed pairing is replayed rather than inferred from row
counts. It has rank 54 and exactly 27 Darboux pairs. All 2,916 ordered
exchange signs are generated from the 27 even and 27 odd rows. This fixes
commutators on even rows and anticommutators on odd rows without leaving a
prose-only Koszul convention.

The latest classical result is also pinned: the support-local \(q_2\), its
local \(D\)-derivation identity, and the cyclic two-sided-causal
\(D\)-Cartan contraction through arity two are certified on all 54 rows.
These are classical compatibility data, not anomaly cancellation or a QME.

The remaining zero-frequency problem is now localized exactly. The causal
construction retains spatial zero modes but supplies neither the generalized
zero eigenspace of the stationary generator on the global 26-row solution
complex nor its Jordan structure. The local Hadamard parametrix cannot
determine this smooth global freedom. The next certificate must therefore
export that finite-dimensional carrier (or prove it absent), restrict
\(q_{26}\), \(\Delta_{26}\), the pairing and real involution to it, and solve
the finite-dimensional CCR, Ward, reality, \(D\)-invariance and physical
positivity/Krein conditions.

No two-point function, Hadamard state, positivity theorem, renormalized
product, QME restoration, or quantum result is claimed here.

```text
PYTHONPATH=quantum-weyl python3 -m lorentzian.berger_hadamard_lift_zero_mode_preflight_certificate --check
PYTHONPATH=quantum-weyl python3 -m lorentzian.verify_berger_hadamard_lift_zero_mode_preflight
PYTHONPATH=quantum-weyl python3 -m unittest quantum-weyl/lorentzian/tests/test_berger_hadamard_lift_zero_mode_preflight.py -v
```
