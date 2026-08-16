# Residual cyclic-carrier obstruction and cotangent preflight

**Result:** `STRICT_RESIDUAL_CYCLIC_CARRIER_OBSTRUCTION_V1`
**Dependencies:** `LOCAL-ALGEBRAIC`, `REDUCED-MODE`
**M4R:** `BLOCKED_BY_M3RC`
**Gate A:** `FAIL_CLOSED`

## Decisive obstruction

The current M3R target contains 470 positive-energy
W+/W- coordinates, all in degree zero.  Every synthesis column lands in a
trace-free metric slot.  The authoritative degree-minus-one BV pairing pairs
metric rows with metric-antifield rows and has no metric--metric entries.
Consequently the literal induced form `iota_M3R^T Omega iota_M3R` has
0 entries, rank
0, and nullity
470.  Nondegeneracy requires rank
470.

The equation `q_res^T Omega + Omega q_res=0` is not a rescue: `q_res=0`, so it
is vacuous even for the zero form.

## Why the older cross-energy form does not close M4R

The committed cross-energy certificate is a valid symmetric even form on 268
raw physical coordinates at energies two through five.  It explicitly does
not identify that form with a gauge-fixed field-theoretic BV antibracket, and
it omits energy six.  It remains useful representation-theoretic evidence but
is not evidence for the degree-minus-one M4R pairing.

## Smallest explicit repair class

Adjoining one degree-one dual for each primal coordinate produces the
940-coordinate finite shifted-cotangent carrier.
Its canonical signed-permutation odd pairing has
940 nonzero ordered entries and
exact rank 940.  This is minimal only
within the declared full cotangent-completion class.

The dual inclusion, projection, and homotopy into the authoritative endpoint
complex are not constructed.  Therefore this is an exact carrier preflight,
not M4R.  The next gate is M3RC: construct and identify those dual comparison
maps, then replay cyclicity and only afterward attempt the M1 common freeze.

## Reproduction

```text
python3 quantum-weyl/classical_import/build_strict_residual_cyclic_carrier_obstruction.py --check
python3 quantum-weyl/classical_import/check_strict_residual_cyclic_carrier_obstruction.py
python3 -m unittest quantum-weyl/classical_import/tests/test_strict_residual_cyclic_carrier_obstruction.py
```
