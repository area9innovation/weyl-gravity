# Lorentzian analytic contracts

This package contains fail-closed interfaces for causal Green operators,
Hadamard data, and later causal products.  Interface readiness is not an
analytic existence theorem.

The first contract is the retained 26-row Berger endpoint.  It requires both
advanced and retarded chain-homotopy identities, causal support, cyclic
adjointness, `D`-equivariance, row completeness, and an explicit zero-mode
policy.  Hadamard certification is a separate conditional stage.

The first physical input has also landed: the ghost and dual identity
endpoint blocks are Green hyperbolic by exact normally-hyperbolic
factorization.  The import independently replays all four `QW+WQ` blocks and
the generic rank-eight-plus-two metric principal boundary. Characteristic-rank
stratification remains open, so rank eight is not asserted on every
characteristic covector. The metric Green realization—and therefore the full
26-row endpoint—remains open.

The clock-reattached principal theorem has now been independently imported.
It resolves the retained rank-eight presentation upstairs as scalar biwaves
on the 34-row minimal complex. The preferred route is to complete the curved
lower-order `QW+WQ` witness there and transport Green operators back through
the support-local clock SDR. Direct retained routes remain allowed, but only
with characteristic-rank stratification.

The authoritative curved 34-row package has now landed and passed the exact
adapter.  The imported pairing is nondegenerate; `q34` and `W34` are cyclic;
and `q34 W34 + W34 q34 = P34` holds coefficientwise in the invariant-frame
PBW algebra.  This closes the curved-witness algebraic gate.  It does not
construct advanced or retarded inverses of `P34`, causal support, Hadamard
data, or a Lorentzian quantum theory.

The subsequent coordinate audit found that the first submitted witness mixed
raw and dressed clock coordinates.  Classical commit `3147774e` repairs the
package coherently.  The quantum consumer now pins and independently replays
`F12`, `C12`, `q34_raw`, `W34_raw`, `P34_raw`, and `pairing34_raw`.  The four
raw principal blocks are exactly `I5,I10,I10,I5`, and the transport is
BV-canonical.  The exact `10+2` preflight identifies a nonzero rank-one,
wave-divisible order-six Schur term under naive clock elimination.  This is a
filtered-extension target, not a Green theorem; all causal and Hadamard flags
remain false.

Classical commit `db099319` is now the authoritative lower-by-two input:
`A10=Box_2^2+V_2` with `ord(V_2)<=2`. The quantum replay verifies its exact
operator identity, rank ledger, and canonical rough-wave factor no-go. The
downstream lower-order factor screen rules out the smallest remaining ansatz:
two scalar-principal second-order factors sharing the same invariant
first-order connection.  Its normalized quadratic-symbol witness is one.
Unequal subprincipal factors, auxiliary/first-order realizations, and a causal
Volterra/Levi resolvent remain open; no Green or quantum flag is promoted.

The full 13-row route is now more sharply classified. Its exact Douglis
determinant contains a genuine `p0^2=2|p_spatial|^2` factor. Consequently no
inverse on arbitrary 13-row sources can have support confined to the
background metric cone. The extra cone belongs to the acyclic clock/graph
incidence, so this is not a physical superluminality claim. The active route
is hybrid: contract that incidence support-locally, then construct the causal
chain homotopy on the retained complex.

The first hybrid step is now exact. Projection by the certified classical
contraction gives `P26_metric=A10=Box_2^2+V_2`. The associated local 20-row
companion has principal determinant `q^20` and no extra characteristic cone.
This identifies the correct retained PDE and reduces the live analytic gate
to a causal Volterra resolvent with global support control. No advanced or
retarded operator has yet been constructed.

Reproduce the current contract receipt with:

```bash
PYTHONPATH=quantum-weyl python3 -m lorentzian.green_endpoint_contract_certificate --check
PYTHONPATH=quantum-weyl python3 -m unittest quantum-weyl/lorentzian/tests/test_green_endpoint_contract.py -v
PYTHONPATH=quantum-weyl python3 -m lorentzian.berger_endpoint_factor_import_certificate --check
PYTHONPATH=quantum-weyl python3 -m unittest quantum-weyl/lorentzian/tests/test_berger_endpoint_factor_import.py -v
PYTHONPATH=quantum-weyl python3 -m lorentzian.clock_reattached_principal_import_certificate --check
PYTHONPATH=quantum-weyl python3 -m unittest quantum-weyl/lorentzian/tests/test_clock_reattached_principal_import.py -v
PYTHONPATH=quantum-weyl python3 -m lorentzian.curved_witness_adapter_certificate --check
PYTHONPATH=quantum-weyl python3 -m unittest quantum-weyl/lorentzian/tests/test_curved_witness_adapter.py -v
PYTHONPATH=quantum-weyl python3 -m lorentzian.curved_witness_import_certificate --check
PYTHONPATH=quantum-weyl python3 -m unittest quantum-weyl/lorentzian/tests/test_curved_witness_import.py -v
PYTHONPATH=quantum-weyl python3 -m lorentzian.metric_mixed_order_green_contract_certificate --check
PYTHONPATH=quantum-weyl python3 -m unittest quantum-weyl/lorentzian/tests/test_metric_mixed_order_green_contract.py -v
PYTHONPATH=quantum-weyl python3 -m lorentzian.metric_equal_connection_factor_screen_certificate --check
PYTHONPATH=quantum-weyl python3 -m unittest quantum-weyl/lorentzian/tests/test_metric_equal_connection_factor_screen.py -v
PYTHONPATH=quantum-weyl python3 -m lorentzian.retained_biwave_companion_preflight_certificate --check
PYTHONPATH=quantum-weyl python3 -m unittest quantum-weyl/lorentzian/tests/test_retained_biwave_companion_preflight.py -v
PYTHONPATH=quantum-weyl python3 -m lorentzian.raw_endpoint_import_certificate --check
PYTHONPATH=quantum-weyl python3 -m lorentzian.raw_endpoint_import_certificate --replay-check
PYTHONPATH=quantum-weyl python3 -m unittest lorentzian.tests.test_raw_endpoint_import -v
```
